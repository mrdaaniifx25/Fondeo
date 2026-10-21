"""SWING MOMENTUM EURUSD · segun el encargo del usuario.

REGLAS CONGELADAS ANTES DE CORRER (sin mirar resultados):
  tendencia  EMA(50) diaria > EMA(200) -> solo compras ; < -> solo ventas
  gatillo    el cierre diario rompe el maximo (minimo) de los 20 dias previos
  entrada    APERTURA del dia siguiente
  stop       entrada -+ 2,0 x ATR(14) diaria
  objetivo   entrada +- 4,0 x ATR(14)      -> R:R 1:2 exacto
  tope       20 dias habiles, cierre a mercado
  una posicion a la vez
  riesgo     0,5 % del capital ; tamanio = riesgo / distancia al stop
  coste      0,04 % por lado (0,08 % ida y vuelta)

Las SALIDAS se resuelven minuto a minuto con el M1: no hay ambiguedad
intrabarra. Nada de la barra de senal se usa para decidir la entrada.

  python3 bt/swing_momentum_eurusd.py
"""
import numpy as np, pandas as pd
from math import sqrt

RIESGO, COSTE_LADO, RR, KSTOP, TOPE = 0.005, 0.0004, 2.0, 2.0, 20
CAP0 = 10000.0

M = pd.read_parquet("data/eurusd_m1.parquet")
M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)   # ASC, por seguridad
ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
# dia FX: cierra a las 17:00 de Nueva York
M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")
g = M.groupby("dfx", sort=True)
D = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
          ini=("open", lambda x: x.index[0]), fin=("close", lambda x: x.index[-1]))
D = D[D.index.notna()]
D = D[g.size() >= 300]                       # dias completos
print(f"días: {len(D):,}   de {D.index.min():%Y-%m-%d} a {D.index.max():%Y-%m-%d}")

# --------- indicadores, TODOS desplazados: se leen al cierre de ayer ---------
D["e50"]  = D.c.ewm(span=50,  adjust=False).mean()
D["e200"] = D.c.ewm(span=200, adjust=False).mean()
tr = pd.concat([D.h-D.l, (D.h-D.c.shift(1)).abs(), (D.l-D.c.shift(1)).abs()], axis=1).max(axis=1)
D["atr"] = tr.rolling(14).mean()
D["max20"] = D.h.rolling(20).max()
D["min20"] = D.l.rolling(20).min()

HH, LL, CC, OO = (M[k].to_numpy() for k in ("high","low","close","open"))
INI, FIN = D.ini.to_numpy().astype(int), D.fin.to_numpy().astype(int)
C,H,L,O,E50,E200,ATR,MX,MN = (D[k].to_numpy() for k in
    ("c","h","l","o","e50","e200","atr","max20","min20"))
FECHA = D.index

def corre(kstop=KSTOP, rr=RR, coste=COSTE_LADO, tope=TOPE, lento=200, rapido=50, canal=20):
    e_l = pd.Series(C).ewm(span=rapido, adjust=False).mean().to_numpy()
    e_s = pd.Series(C).ewm(span=lento,  adjust=False).mean().to_numpy()
    mx  = pd.Series(H).rolling(canal).max().to_numpy()
    mn  = pd.Series(L).rolling(canal).min().to_numpy()
    ops, i, n = [], max(lento, canal) + 1, len(D)
    while i < n - 1:
        if not np.isfinite(ATR[i]) or ATR[i] <= 0: i += 1; continue
        alc = e_l[i] > e_s[i]
        # gatillo: el cierre de HOY rompe el canal de los dias ANTERIORES
        largo  =  alc and C[i] > mx[i-1]
        corto  = (not alc) and C[i] < mn[i-1]
        if not (largo or corto): i += 1; continue
        lado = 1 if largo else -1
        e = i + 1                                  # entrada en la apertura de maniana
        ent = O[e]
        rgo = kstop * ATR[i]
        sl  = ent - lado*rgo
        tp  = ent + lado*rr*rgo
        a, b = INI[e], FIN[min(e + tope - 1, n-1)]
        hh, ll = HH[a:b+1], LL[a:b+1]
        if lado > 0: ks = np.nonzero(ll <= sl)[0]; kt = np.nonzero(hh >= tp)[0]
        else:        ks = np.nonzero(hh >= sl)[0]; kt = np.nonzero(ll <= tp)[0]
        fs = ks[0] if len(ks) else 10**9
        ft = kt[0] if len(kt) else 10**9
        if ft < fs:   sal, motivo = tp, "objetivo"
        elif fs < 10**9: sal, motivo = sl, "stop"
        else:         sal, motivo = CC[b], "tiempo"
        # dia de salida, para saber cuando queda libre la posicion
        dsal = e + tope - 1
        for k2 in range(e, min(e + tope, n)):
            if FIN[k2] >= a + min(fs, ft) if min(fs, ft) < 10**9 else False:
                dsal = k2; break
        else: dsal = min(e + tope - 1, n-1)
        bruto = (sal - ent) * lado / rgo                       # en R, antes de costes
        cR = (2 * coste * ent) / rgo                           # ida y vuelta, en R
        ops.append((FECHA[e], lado, ent, sl, tp, sal, motivo, rgo,
                    bruto, bruto - cR, cR, dsal))
        i = dsal + 1                                           # una posicion a la vez
    T = pd.DataFrame(ops, columns="fecha lado ent sl tp sal motivo rgo R Rn cR dsal".split())
    return T

def metricas(T, et):
    if len(T) < 5: return print(f"  {et:<26} (muy pocas: {len(T)})")
    gan = T.Rn > 0
    pf_g, pf_p = T.Rn[T.Rn > 0].sum(), -T.Rn[T.Rn < 0].sum()
    eq = CAP0 * (1 + RIESGO * T.Rn).cumprod()
    dd = float(((eq - eq.cummax()) / eq.cummax()).min())
    ret = float(eq.iloc[-1] / CAP0 - 1)
    anios = (T.fecha.iloc[-1] - T.fecha.iloc[0]).days / 365.25
    print(f"  {et:<26}{len(T):>5}{100*gan.mean():>9.1f}%{T.Rn.mean():>+9.3f}"
          f"{(pf_g/pf_p if pf_p>0 else np.inf):>8.2f}{100*dd:>9.1f}%{100*ret:>9.1f}%"
          f"{len(T)/max(anios,.1):>8.1f}")
    return dict(n=len(T), wr=100*gan.mean(), exp=T.Rn.mean(),
                pf=pf_g/pf_p if pf_p>0 else np.inf, dd=100*dd, ret=100*ret)

T = corre()
corte = T.fecha.iloc[int(len(T)*0.70)]
IS, OS = T[T.fecha < corte], T[T.fecha >= corte]
CAB = f"  {'':<26}{'n':>5}{'win rate':>10}{'exp R':>9}{'PF':>8}{'maxDD':>10}{'retorno':>10}{'ops/año':>8}"
print(f"\ncorte dentro/fuera: {corte:%Y-%m-%d}\n")
print("="*92); print("1 · LA ESTRATEGIA BASE"); print("="*92); print(CAB)
mi = metricas(IS, "DENTRO (ajuste, 70 %)")
mo = metricas(OS, "FUERA (validación, 30 %)")
mt = metricas(T,  "muestra completa")
print(f"\n  exigido fuera: win rate > 39,33 % y expectativa > 0")
if mo: print(f"  obtenido:      win rate {mo['wr']:.1f} %   expectativa {mo['exp']:+.3f} R")

print("\n" + "="*92); print("2 · ROBUSTEZ · meseta de stop y objetivo"); print("="*92)
print(f"  {'k stop':>8}{'R:R':>6}" + "".join(f"{f'{x}':>13}" for x in
      ["n","win rate","exp R","PF"]))
for k in (1.0, 1.5, 2.0, 2.5, 3.0):
    for r in (1.5, 2.0, 2.5):
        X = corre(kstop=k, rr=r)
        if len(X) < 10: continue
        g2 = X.Rn > 0; p, q = X.Rn[X.Rn>0].sum(), -X.Rn[X.Rn<0].sum()
        print(f"  {k:>8.1f}{r:>6.1f}{len(X):>13}{100*g2.mean():>12.1f}%"
              f"{X.Rn.mean():>+13.3f}{(p/q if q>0 else np.inf):>13.2f}")

print("\n" + "="*92); print("3 · ROBUSTEZ · coste doble y parámetros vecinos"); print("="*92)
print(CAB)
metricas(corre(coste=0.0008), "coste DOBLE (0,08 %/lado)")
for lo, ra, ca, et in ((150,50,20,"EMA 50/150"), (250,50,20,"EMA 50/250"),
                       (200,30,20,"EMA 30/200"), (200,50,10,"canal 10"),
                       (200,50,40,"canal 40"), (200,50,20,"tope 40 días")):
    metricas(corre(lento=lo, rapido=ra, canal=ca, tope=40 if "tope" in et else TOPE), et)

print("\n" + "="*92); print("4 · ¿DEPENDE DE UNOS POCOS TRAMOS?"); print("="*92)
T["anio"] = T.fecha.dt.year
print(f"  {'año':>6}{'n':>5}{'win rate':>10}{'exp R':>9}{'suma R':>9}")
for a, s in T.groupby("anio"):
    print(f"  {a:>6}{len(s):>5}{100*(s.Rn>0).mean():>9.1f}%{s.Rn.mean():>+9.3f}{s.Rn.sum():>+9.2f}")
mej = T.Rn.nlargest(2).sum()
print(f"\n  suma total {T.Rn.sum():+.2f} R   ·   las 2 mejores aportan {mej:+.2f} R"
      f"   ·   sin ellas: {T.Rn.sum()-mej:+.2f} R")
print(f"\n  apalancamiento: tamaño = {RIESGO:.3%} / (stop {T.rgo.median()/T.ent.median():.3%}) "
      f"= {RIESGO/(T.rgo.median()/T.ent.median()):.2f}x   (tope 10x)")
print(f"  coste en R: {T.cR.mean():.3f} de media")
