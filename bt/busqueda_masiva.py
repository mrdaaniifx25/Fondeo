"""Pre-registro docs/PREREGISTRO_busqueda_masiva.md

BUSQUEDA MASIVA: 20.000 estrategias mecanicas generadas por fuerza bruta.

La clave de arquitectura: el desenlace de cada barra se precalcula UNA vez
(para cada combinacion de stop y objetivo, en largo y en corto). Despues una
"estrategia" es solo una mascara booleana, asi que evaluar 20.000 es gratis.

Contraste principal: correlacion entre el t DENTRO de muestra y el t FUERA.
Mide si buscar sirve de algo.

  python3 bt/busqueda_masiva.py
"""
import numpy as np, pandas as pd
from math import sqrt
rng = np.random.default_rng(20261013)

INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 0.70),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 12.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  0.8)]
TF = [("M5", 5, 120), ("M15", 15, 240), ("H1", 60, 960)]
KS, RRS = (1.0, 2.0, 3.0), (1.0, 2.0)
NEST, MAXB, CORTE = 20000, 60000, pd.Timestamp("2025-01-01")


def barras(ruta, minutos):
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    t = (M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None))
    g = M.assign(k=t.dt.floor(f"{minutos}min")).groupby("k", sort=True)
    b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"))
    b["fin"] = g.apply(lambda x: x.index[-1], include_groups=False).reindex(b.index)
    return M, b[b.index.notna()]


def primitivas(b):
    """~40 condiciones booleanas por barra, TODAS desplazadas (solo pasado)."""
    O, H, L, C = (b[k].to_numpy() for k in "ohlc")
    s = lambda x: pd.Series(x, index=b.index)
    P = {}
    cl = s(C)
    d = cl.diff()
    for n in (7, 14, 21):
        up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
        dn = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
        r = 100 - 100/(1 + up/dn.replace(0, np.nan))
        for u in (30, 50, 70):
            P[f"RSI{n}>{u}"] = (r > u); P[f"RSI{n}<{u}"] = (r < u)
    mm = {n: cl.rolling(n).mean() for n in (10, 20, 50, 100, 200)}
    for a, bb in ((10,20),(10,50),(20,50),(20,100),(50,200)):
        P[f"MM{a}>MM{bb}"] = mm[a] > mm[bb]; P[f"MM{a}<MM{bb}"] = mm[a] < mm[bb]
    ema = lambda n: cl.ewm(span=n, adjust=False).mean()
    mac = ema(12) - ema(26)
    P["MACD>0"] = mac > 0; P["MACD<0"] = mac < 0
    P["MACD>senal"] = mac > mac.ewm(span=9, adjust=False).mean()
    P["MACD<senal"] = mac < mac.ewm(span=9, adjust=False).mean()
    tr = pd.concat([s(H)-s(L), (s(H)-cl.shift(1)).abs(), (s(L)-cl.shift(1)).abs()],
                   axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    P["ATR alto"] = atr > atr.rolling(100).median()
    P["ATR bajo"] = atr < atr.rolling(100).median()
    P["barra ancha"] = (s(H)-s(L)) > 1.5*atr
    P["barra estrecha"] = (s(H)-s(L)) < 0.5*atr
    for n in (10, 20, 55):
        P[f"rompe max{n}"] = cl >= s(H).rolling(n).max().shift(1)
        P[f"rompe min{n}"] = cl <= s(L).rolling(n).min().shift(1)
    ph, pl = s(H).shift(1), s(L).shift(1)
    P["barre min previo"] = (s(L) <= pl) & (cl > pl) & (cl < ph)   # CRT alcista
    P["barre max previo"] = (s(H) >= ph) & (cl < ph) & (cl > pl)   # CRT bajista
    P["cierra sobre max previo"] = cl > ph
    P["cierra bajo min previo"] = cl < pl
    cuerpo = (cl - s(O)).abs()
    P["vela verde"] = cl > s(O); P["vela roja"] = cl < s(O)
    P["cuerpo grande"] = cuerpo > 0.7*(s(H)-s(L))
    P["martillo"] = (s(O)-s(L)).where(cl>s(O), cl-s(L)) > 2*cuerpo
    sub = (cl > cl.shift(1)).astype(int)
    P["3 verdes"] = sub.rolling(3).sum() == 3
    P["3 rojas"] = sub.rolling(3).sum() == 0
    hor = b.index.hour
    for a, z in ((0,4),(4,8),(8,12),(12,16),(16,20),(20,24)):
        P[f"hora {a:02d}-{z:02d}"] = pd.Series((hor >= a) & (hor < z), index=b.index)
    for i, dia in enumerate(("lun","mar","mie","jue","vie")):
        P[dia] = pd.Series(b.index.dayofweek == i, index=b.index)
    # TODO desplazado una barra: la condicion se lee al cierre y se opera despues
    return {k: v.shift(1).fillna(False).to_numpy().astype(bool) for k, v in P.items()}, atr


def desenlaces(M, b, atr, hor, U, coste):
    """R neta de entrar en la apertura de la barra siguiente, por (k, rr, lado)."""
    HH, LL, OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()
    e = b.fin.to_numpy().astype(int) + 1
    a14 = atr.shift(1).to_numpy()
    n = len(b)
    val = np.isfinite(a14) & (a14 > 0) & (e < len(M)-hor-1)
    e = np.clip(e, 0, len(M)-1)
    OUT = {}
    for k in KS:
        for rr in RRS:
            for lado in (1, -1):
                OUT[(k, rr, lado)] = np.full(n, np.nan)
    paso = 8000
    for i0 in range(0, n, paso):
        i1 = min(i0+paso, n)
        m = val[i0:i1]
        if not m.any(): continue
        ee = e[i0:i1][m]
        ix = np.clip(ee[:, None] + np.arange(hor)[None, :], 0, len(HH)-1)
        rmin = np.minimum.accumulate(LL[ix], axis=1)
        rmax = np.maximum.accumulate(HH[ix], axis=1)
        ent = OO[ee]; aa = a14[i0:i1][m]
        for k in KS:
            r = k*aa
            cr = coste/(r/U)
            malo = cr > 1.0
            for rr in RRS:
                for lado in (1, -1):
                    sl = ent - lado*r; tp = ent + lado*rr*r
                    if lado > 0:
                        hs = rmin <= sl[:, None]; ht = rmax >= tp[:, None]
                    else:
                        hs = rmax >= sl[:, None]; ht = rmin <= tp[:, None]
                    fs = np.where(hs.any(1), hs.argmax(1), hor)
                    ft = np.where(ht.any(1), ht.argmax(1), hor)
                    v = np.where(ft < fs, rr, np.where(fs < hor, -1.0, 0.0)) - cr
                    v[malo] = np.nan
                    o = OUT[(k, rr, lado)]
                    o[i0:i1][m] = v
    return OUT


def t_agr(r, dias):
    """t con error estandar agrupado por dia."""
    r = r[np.isfinite(r)]
    if len(r) < 30: return np.nan
    m = r.mean()
    su = pd.Series(r - m).groupby(dias[:len(r)]).sum()
    s2 = float((su**2).sum())
    return m*len(r)/sqrt(s2) if s2 > 0 else np.nan


PANEL = []
for nom, ruta, U, coste in INS:
    for et, mi, hor in TF:
        M, b = barras(ruta, mi)
        if len(b) > MAXB:          # uniforme en el tiempo, no las ultimas
            b = b.iloc[np.linspace(0, len(b)-1, MAXB).astype(int)]
        P, atr = primitivas(b)
        OUT = desenlaces(M, b, atr, hor, U, coste)
        dentro = np.asarray(b.index < CORTE)
        dia = pd.Series(b.index.date).astype(str).to_numpy()
        BASE = {}
        for kk in KS:
            for rr2 in RRS:
                for ld in (1, -1):
                    v = OUT[(kk, rr2, ld)]
                    BASE[(kk, rr2, ld)] = (
                        float(np.nanmean(v[dentro])) if np.isfinite(v[dentro]).any() else np.nan,
                        float(np.nanmean(v[~dentro])) if np.isfinite(v[~dentro]).any() else np.nan)
        PANEL.append((f"{nom}/{et}", P, OUT, dentro, dia, BASE))
        print(f"{nom}/{et}: {len(b):,} barras  ({int(dentro.sum()):,} dentro / "
              f"{int((~dentro).sum()):,} fuera)")

NOM = sorted(PANEL[0][1].keys())
print(f"\nprimitivas: {len(NOM)}   paneles: {len(PANEL)}   "
      f"estrategias a generar: {NEST:,}\n")

res = []
for _ in range(NEST):
    pi = int(rng.integers(len(PANEL)))
    et, P, OUT, dentro, dia, BASE = PANEL[pi]
    nc = int(rng.integers(2, 4))
    cond = list(rng.choice(NOM, size=nc, replace=False))
    k = float(rng.choice(KS)); rr = float(rng.choice(RRS)); lado = int(rng.choice((1,-1)))
    m = P[cond[0]].copy()
    for c in cond[1:]: m &= P[c]
    r = OUT[(k, rr, lado)]
    md = m & dentro & np.isfinite(r)
    mf = m & (~dentro) & np.isfinite(r)
    if md.sum() < 200 or mf.sum() < 50: continue
    rd, rf = r[md], r[mf]
    bd, bf = BASE[(k, rr, lado)]
    res.append((et, " Y ".join(cond), k, rr, lado, int(md.sum()), int(mf.sum()),
                float(rd.mean()), float(t_agr(rd, dia[md])),
                float(rf.mean()), float(t_agr(rf, dia[mf])),
                float(rd.mean()-bd), float(rf.mean()-bf)))

T = pd.DataFrame(res, columns="panel reglas k rr lado nd nf Rd td Rf tf Ed Ef".split()).dropna()
print(f"estrategias validas (n>=200 dentro y >=50 fuera): {len(T):,}\n")

print("="*92); print("1 · DISTRIBUCION DEL t DENTRO DE MUESTRA"); print("="*92)
print(f"  media {T.td.mean():+.2f}   desv {T.td.std():.2f}   "
      f"(el puro ruido daria media 0,00 y desv 1,00)")
for u in (2, 3, 4, 5):
    print(f"  con t dentro > +{u}: {int((T.td>u).sum()):>6}   "
          f"con t dentro < -{u}: {int((T.td<-u).sum()):>6}")
print(f"  R neta media de las {len(T):,}: {T.Rd.mean():+.4f} dentro / {T.Rf.mean():+.4f} fuera")

print("\n" + "="*92); print("2 · LAS MEJORES DENTRO -> QUE HACEN FUERA"); print("="*92)
print(f"  {'seleccion':<26}{'n':>6}{'t dentro':>11}{'R dentro':>11}{'R FUERA':>11}{'t FUERA':>10}")
for q in (10, 50, 100, 200, 500):
    s = T.nlargest(q, "td")
    print(f"  las {q:<4} mejores por t dentro{len(s):>6}{s.td.mean():>+11.2f}"
          f"{s.Rd.mean():>+11.4f}{s.Rf.mean():>+11.4f}{s.tf.mean():>+10.2f}")
s = T.nlargest(200, "td")
print(f"\n  de las 200 mejores dentro, cuantas siguen positivas fuera: "
      f"{int((s.Rf>0).sum())} de 200  ({100*(s.Rf>0).mean():.0f} %)")
print(f"  por azar se esperaria aproximadamente: {100*(T.Rf>0).mean():.0f} %")

print("\n" + "="*92)
print("3 · PRINCIPAL · CORRELACION ENTRE DENTRO Y FUERA")
print("="*92)
print(f"  correlacion CRUDA t dentro vs t fuera : {T.td.corr(T.tf):+.4f}")
print(f"  correlacion CRUDA R dentro vs R fuera : {T.Rd.corr(T.Rf):+.4f}")
print("\n  Pero la cruda esta CONFUNDIDA: el coste depende de k y del panel, y es")
print("  identico dentro y fuera. Ademas el oro subio 143 % y el DAX 573 %, asi que")
print("  'largo' gana en los dos tramos sin saber nada. Hay que quitar la linea base")
print("  = entrar en TODAS las barras de ese panel con el mismo stop, objetivo y lado.\n")
print(f"  EXCESO sobre la linea base:")
print(f"    correlacion exceso dentro vs exceso fuera : {T.Ed.corr(T.Ef):+.4f}")
print(f"    exceso medio de las {len(T):,}: {T.Ed.mean():+.4f} dentro / {T.Ef.mean():+.4f} fuera")
print(f"  n = {len(T):,}   error estandar aprox {1/sqrt(len(T)):.4f}")
print(f"\n  ESTE es el numero que contesta el reto. Si es ~0, buscar no informa.")
print("\n  Las mejores por EXCESO dentro -> su exceso FUERA:")
print(f"    {'seleccion':<20}{'exc dentro':>12}{'exc FUERA':>12}{'% positivas fuera':>20}")
for q in (10, 50, 100, 200, 500):
    sx = T.nlargest(q, "Ed")
    print(f"    las {q:<4} mejores{sx.Ed.mean():>12.4f}{sx.Ef.mean():>12.4f}"
          f"{100*(sx.Ef>0).mean():>19.0f}%")
print(f"    {'(todas)':<20}{T.Ed.mean():>12.4f}{T.Ef.mean():>12.4f}{100*(T.Ef>0).mean():>19.0f}%")

print("\n" + "="*92); print("LA MEJOR DE LAS 20.000, DENTRO Y FUERA"); print("="*92)
for _, r in T.nlargest(6, "Ed").iterrows():
    print(f"  {r.panel:<11} {('largo' if r.lado>0 else 'corto'):<6} k{r.k:.0f} RR{r.rr:.0f}  {r.reglas[:52]}")
    print(f"     dentro n {int(r.nd):>5} R {r.Rd:+.4f} t {r.td:+.2f} exc {r.Ed:+.4f}   "
          f"FUERA n {int(r.nf):>5} R {r.Rf:+.4f} t {r.tf:+.2f} exc {r.Ef:+.4f}")
T.to_csv("/tmp/claude-0/busqueda_masiva.csv", index=False)
