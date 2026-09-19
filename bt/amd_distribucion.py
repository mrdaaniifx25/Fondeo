"""Hasta donde llega de verdad el precio tras la manipulacion.

Si mi umbral de D (cruzar el rango entero) es demasiado exigente, aqui se ve:
se mide el recorrido real a favor en las 20 velas siguientes, en fracciones
del ancho del rango. 1,00 = llego al extremo contrario.
"""
import numpy as np, pandas as pd
from math import sqrt

ESPM, ESPD, LIMITE = 20, 20, 0.90

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").drop_duplicates("ts")

def velas(mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(h=("high","max"), l=("low","min"), c=("close","last"),
                n=("close","size")).dropna())
    return g[g.n >= mins*0.3].reset_index()

def rma(x, n):
    a = np.full(len(x), np.nan)
    if len(x) < n: return a
    a[n-1] = np.nanmean(x[:n])
    for i in range(n, len(x)): a[i] = (a[i-1]*(n-1) + x[i]) / n
    return a

def corre(mins, n, nom):
    V = velas(mins)
    h, l, c = V.h.to_numpy(), V.l.to_numpy(), V.c.to_numpy(); N = len(V)
    pc = np.roll(c,1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    atr = np.roll(rma(tr,14), 1)
    hi = pd.Series(h).rolling(n).max().to_numpy()
    lo = pd.Series(l).rolling(n).min().to_numpy()
    ratio = (hi-lo)/(atr*np.sqrt(n))
    rec = []; i = n
    while i < N-1:
        if not np.isfinite(ratio[i]) or ratio[i] > LIMITE: i += 1; continue
        rHi, rLo = hi[i], lo[i]
        if rHi <= rLo: i += 1; continue
        manip = -1; lado = 0; j = i+1
        while j < min(i+1+ESPM, N):
            if h[j] > rHi or l[j] < rLo:
                arr = h[j] > rHi and rLo < c[j] < rHi
                aba = l[j] < rLo and rLo < c[j] < rHi
                if arr or aba: manip = j; lado = -1 if arr else 1
                break
            j += 1
        if manip < 0: i = max(j, i+1); continue
        k1, k2 = manip+1, min(manip+1+ESPD, N)
        if k2 > k1:
            ancho = rHi - rLo
            if lado < 0:
                # barrio arriba: se espera caida. Cuanto baja desde rHi
                mfe = (rHi - l[k1:k2].min()) / ancho
                mfc = (rHi - c[k1:k2].min()) / ancho     # medido en cierres
            else:
                mfe = (h[k1:k2].max() - rLo) / ancho
                mfc = (c[k1:k2].max() - rLo) / ancho
            rec.append((mfe, mfc))
        i = manip + 1
    D = pd.DataFrame(rec, columns=["mecha","cierre"])
    print(f"\n{nom}   ·   {len(D):,} manipulaciones desde un rango apretado")
    print("  recorrido a favor, en fracciones del ancho del rango (1,00 = extremo contrario)")
    q = [.1,.25,.5,.75,.9]
    print("       ", "  ".join(f"p{int(x*100)}" for x in q))
    print("  mecha ", "  ".join(f"{v:.2f}" for v in D.mecha.quantile(q)))
    print("  cierre", "  ".join(f"{v:.2f}" for v in D.cierre.quantile(q)))
    print("  ¿que % alcanza cada umbral? (por cierre)")
    for u in (0.25, 0.50, 0.75, 1.00, 1.25):
        print(f"     {u:.2f} del rango  ->  {100*(D.cierre >= u).mean():5.1f} %")

for tf, mins, n in (("M15", 15, 12), ("H1", 60, 8), ("H4", 240, 8)):
    corre(mins, n, f"{tf}  n={n}")
