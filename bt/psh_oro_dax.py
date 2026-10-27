"""Pre-registro docs/PREREGISTRO_psh_oro_dax.md

El PSH de su spec (maximo de la sesion anterior, solo cortos), replicado en
oro y DAX. EURUSD va de referencia, no de prueba.
"""
import numpy as np, pandas as pd
from math import sqrt

TZ = "Europe/Madrid"
VENTANAS = {"Londres": (900, 1100), "NuevaYork": (1400, 1630)}
H4_ATRAS = H1_ATRAS = 6
FIN_DIA, ESPERA = 2300, 12
MARGENES = [0.0, 0.33, 0.66, 1.0]          # x ATR(M5)

INS = [("EURUSD (referencia)", "data/eurusd_m1.parquet", 1e-4, 1.43, 1.0, 3),
       ("oro",                 "data/xauusd_m1.parquet", 0.01, 35.0, 25.0, 3),
       ("DAX",                 "data/grxeur_m1.parquet", 1.0,   1.6,  1.0, 2)]

def atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    a = np.full(len(tr), np.nan); a[n-1] = tr[:n].mean()
    for i in range(n, len(tr)): a[i] = (a[i-1]*(n-1)+tr[i])/n
    return np.roll(a, 1)

def prepara(ruta, minu):
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    Lc = m1["loc"]; m1["dia"] = Lc.dt.normalize(); m1["hm"] = Lc.dt.hour*100 + Lc.dt.minute
    def velas(mins):
        g = (m1.set_index("loc").resample(f"{mins}min", label="left", closed="left",
                                          origin="start_day")
               .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                    c=("close","last"), n=("close","size")).dropna())
        g = g[g.n >= max(1, mins*0.3)].reset_index().rename(columns={"loc":"t"})
        g["fin"] = g.t + pd.Timedelta(minutes=mins)
        return g
    return m1, velas(5), velas(60), velas(240)

def corre(ruta, U, coste, spread, minu, margen, con_cadena):
    m1, V5, V60, V240 = prepara(ruta, minu)
    MH, ML, MC = m1.high.to_numpy(), m1.low.to_numpy(), m1.close.to_numpy()
    MT = m1["loc"].to_numpy("datetime64[ns]")
    MHM, MDIA = m1.hm.to_numpy(), m1.dia.to_numpy()
    O5, H5, L5, C5 = (V5[x].to_numpy() for x in ("o","h","l","c"))
    T5 = V5.t.to_numpy("datetime64[ns]"); F5 = V5.fin.to_numpy("datetime64[ns]")
    A5 = atr(H5, L5, C5)
    HM5 = (pd.DatetimeIndex(V5.t).hour*100 + pd.DatetimeIndex(V5.t).minute).to_numpy()
    D5 = pd.DatetimeIndex(V5.t).normalize().to_numpy()
    F60 = V60.fin.to_numpy("datetime64[ns]"); H60, L60, C60 = V60.h.to_numpy(), V60.l.to_numpy(), V60.c.to_numpy()
    F240 = V240.fin.to_numpy("datetime64[ns]"); H240, C240 = V240.h.to_numpy(), V240.c.to_numpy()

    asia = m1[m1.hm < 800].groupby("dia").agg(h=("high","max"), n=("close","size"))
    asia = asia[asia.n > 120]
    lon = m1[(m1.hm >= 800) & (m1.hm < 1400)].groupby("dia").agg(h=("high","max"), n=("close","size"))
    lon = lon[lon.n > 120]

    def envolvente_baj(i):
        if C5[i] >= O5[i]: return False
        for j in range(i-1, max(i-13, -1), -1):
            if C5[j] < O5[j]: continue
            return O5[i] >= max(O5[j], C5[j]) and C5[i] <= min(O5[j], C5[j])
        return False

    ops = []
    for d in np.unique(D5):
        perdido = False
        for ses, (a, b) in VENTANAS.items():
            if perdido: break
            S = asia if ses == "Londres" else lon
            dd = pd.Timestamp(d)
            if dd not in S.index: continue
            niv = float(S.h[dd])
            idx = np.where((D5 == d) & (HM5 >= a) & (HM5 < b))[0]
            if len(idx) < 3: continue
            hecho = False
            for i in idx:
                if hecho: break
                if C5[i] > niv: break                       # RUN: nivel muerto
                if not (H5[i] > niv and C5[i] < niv): continue
                if not np.isfinite(A5[i]) or A5[i] <= 0: continue
                if con_cadena:
                    k4 = int(np.searchsorted(F240, T5[i], "right"))
                    if not any(H240[q] > niv and C240[q] < niv
                               for q in range(max(0, k4-H4_ATRAS), k4)): continue
                    k1 = int(np.searchsorted(F60, T5[i], "right"))
                    if not any(H60[q] > niv and C60[q] < niv
                               for q in range(max(0, k1-H1_ATRAS), k1)): continue
                ext = H5[i]
                for z in range(i, min(i+ESPERA+1, len(V5))):
                    if D5[z] != d or HM5[z] >= b: break
                    ext = max(ext, H5[z])
                    if z == i or not envolvente_baj(z): continue
                    P = C5[z]; SL = ext + spread*U + margen*A5[z]
                    rgo = SL - P
                    if rgo <= 0: break
                    TP = P - 2*rgo
                    j0 = int(np.searchsorted(MT, F5[z], "left"))
                    jf = np.where((MDIA[j0:] != d) | (MHM[j0:] >= FIN_DIA))[0]
                    j1 = max(j0 + (int(jf[0]) if len(jf) else len(MT)-j0), j0+1)
                    hh, ll = MH[j0:j1], ML[j0:j1]
                    gt, gs = ll <= TP, hh >= SL
                    it = int(np.argmax(gt)) if gt.any() else 10**9
                    isl = int(np.argmax(gs)) if gs.any() else 10**9
                    if it == 10**9 and isl == 10**9:
                        R, mot = (P - MC[j1-1])/rgo, "cierre"
                    elif isl <= it: R, mot = -1.0, "SL"
                    else: R, mot = 2.0, "TP"
                    ops.append(dict(fecha=pd.Timestamp(T5[z]), sesion=ses,
                                    rgo=rgo/U, R=R, motivo=mot))
                    hecho = True
                    if R < 0: perdido = True
                    break
    if not ops: return pd.DataFrame()
    D = pd.DataFrame(ops); D["neto"] = D.R - coste/D.rgo
    return D

def ficha(et, D, coste):
    if len(D) == 0: return print(f"  {et:<34} sin operaciones")
    cr = (coste/D.rgo).mean(); um = 100*(1+cr)/3
    mb, icb = D.R.mean(), 1.96*D.R.std(ddof=1)/sqrt(len(D))
    mn, icn = D.neto.mean(), 1.96*D.neto.std(ddof=1)/sqrt(len(D))
    flag = "  (n<50: NO SE PUEDE SABER)" if len(D) < 50 else ("  CRUZA" if mn-icn > 0 else "")
    print(f"  {et:<34} n {len(D):>4}  riesgo {D.rgo.median():>7.1f}  coste {100*cr:>5.1f}%  "
          f"TP {100*(D.motivo=='TP').mean():>5.1f}%  umbral {um:>5.1f}  "
          f"bruta {mb:>+7.3f} [{mb-icb:>+.3f},{mb+icb:>+.3f}]  neta {mn:>+7.3f}{flag}")

for cad, tit in ((True, "CON la cadena H4+H1 (donde apareció el candidato)"),
                 (False, "SIN la cadena H4+H1 (la que tiene muestra)")):
    print("\n" + "="*146); print(f"PSH · SOLO CORTOS · {tit}"); print("="*146)
    for nom, ruta, U, coste, spread, minu in INS:
        for mar in MARGENES:
            ficha(f"{nom} · margen {mar:.2f}×ATR", corre(ruta, U, coste, spread, minu, mar, cad), coste)
        print()

print("\n" + "="*146)
print("POSTERIOR AL PRE-REGISTRO · los tres juntos, sin cadena, margen 0,33×ATR")
print("="*146)
print("  NO estaba declarado. Es la forma mas justa de preguntar 'hay algo o no',")
print("  juntando toda la muestra en vez de mirar instrumento por instrumento.")
todo = []
for nom, ruta, U, coste, spread, minu in INS:
    D = corre(ruta, U, coste, spread, minu, 0.33, False)
    if len(D): D["ins"] = nom; D["cr"] = coste/D.rgo; todo.append(D)
T = pd.concat(todo, ignore_index=True)
mb, icb = T.R.mean(), 1.96*T.R.std(ddof=1)/sqrt(len(T))
mn, icn = T.neto.mean(), 1.96*T.neto.std(ddof=1)/sqrt(len(T))
print(f"\n  n {len(T):,}   coste medio {100*T.cr.mean():.1f} % del riesgo")
print(f"  BRUTA {mb:+.4f} [{mb-icb:+.4f},{mb+icb:+.4f}]    "
      f"{'cruza' if mb-icb > 0 else 'el cero dentro'}")
print(f"  NETA  {mn:+.4f} [{mn-icn:+.4f},{mn+icn:+.4f}]    "
      f"{'cruza' if mn-icn > 0 else 'el cero dentro'}")
print(f"\n  el azar de un 1:2 es 33,3 % y aqui se acierta {100*(T.motivo=='TP').mean():.1f} %")
print(f"  el umbral con el coste medio es {100*(1+T.cr.mean())/3:.1f} %")
print("\n  por instrumento, la bruta y su intervalo:")
for nom, g in T.groupby("ins"):
    m_, i_ = g.R.mean(), 1.96*g.R.std(ddof=1)/sqrt(len(g))
    print(f"    {nom:<22} n {len(g):>4}  bruta {m_:>+7.3f} [{m_-i_:>+.3f},{m_+i_:>+.3f}]")
