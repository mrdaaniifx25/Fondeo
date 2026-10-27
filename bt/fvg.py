"""Las cuatro afirmaciones sobre el FVG. Pre-registro docs/PREREGISTRO_fvg.md"""
import numpy as np, pandas as pd
from math import sqrt

HOR = 50
TFS = {"M15": 15, "H1": 60, "H4": 240, "D1": 1440}
INS = {"EURUSD": "data/eurusd_m1.parquet",
       "oro": "data/xauusd_m1.parquet", "DAX": "data/grxeur_m1.parquet"}

def velas(m1, mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    return g[g.n >= mins * 0.3].reset_index()

def rma(x, n):
    a = np.full(len(x), np.nan)
    if len(x) < n: return a
    a[n-1] = np.nanmean(x[:n])
    for i in range(n, len(x)): a[i] = (a[i-1]*(n-1) + x[i]) / n
    return a

def analiza(V):
    h, l, c = V.h.to_numpy(), V.l.to_numpy(), V.c.to_numpy()
    N = len(V)
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    atr = np.roll(rma(tr, 14), 1)              # solo velas ya cerradas

    # recorrido maximo a cada lado en las HOR velas SIGUIENTES, en ATR
    exc_ab = np.full(N, np.nan); exc_ar = np.full(N, np.nan)
    vuelta = np.full(N, np.nan)
    for i in range(N-1):
        j = min(i+1+HOR, N)
        if j <= i+1 or not np.isfinite(atr[i]) or atr[i] <= 0: continue
        exc_ab[i] = (c[i] - l[i+1:j].min()) / atr[i]
        exc_ar[i] = (h[i+1:j].max() - c[i]) / atr[i]

    alc = np.zeros(N, bool); baj = np.zeros(N, bool)
    alc[2:] = l[2:] > h[:-2]
    baj[2:] = h[2:] < l[:-2]
    esFVG = alc | baj

    rango = h - l
    r3 = np.full(N, np.nan)
    m = np.roll(rango, 1) > 0
    r3[m] = rango[m] / np.roll(rango, 1)[m]

    # distancia del cierre al borde del hueco, en ATR
    d = np.full(N, np.nan)
    d[alc] = (c[alc] - l[alc]) / atr[alc]
    d[baj] = (h[baj] - c[baj]) / atr[baj]

    ok = esFVG & np.isfinite(d) & np.isfinite(atr) & (d >= 0)
    ok &= np.where(alc, np.isfinite(exc_ab), np.isfinite(exc_ar))

    # LISTON: distribucion del recorrido en velas que NO son FVG
    base_ab = exc_ab[~esFVG & np.isfinite(exc_ab)]
    base_ar = exc_ar[~esFVG & np.isfinite(exc_ar)]
    base_ab.sort(); base_ar.sort()

    idx = np.where(ok)[0]
    filas = []
    for i in idx:
        es_alc = alc[i]
        exc = exc_ab[i] if es_alc else exc_ar[i]
        b = base_ab if es_alc else base_ar
        # P(recorrer al menos d) entre las velas que no son FVG
        p = 1.0 - np.searchsorted(b, d[i], "left") / len(b)
        # ¿cuantas velas tarda en volver?
        t = np.nan
        if exc >= d[i]:
            j = min(i+1+HOR, N)
            if es_alc:
                w = np.where(l[i+1:j] <= c[i] - d[i]*atr[i])[0]
            else:
                w = np.where(h[i+1:j] >= c[i] + d[i]*atr[i])[0]
            if len(w): t = w[0] + 1
        filas.append((i, es_alc, d[i], float(exc >= d[i]), p, r3[i], t))
    return pd.DataFrame(filas, columns=["i","alcista","d","vuelve","base","r3","velas"])

def linea(nom, S):
    if len(S) < 50: print(f"{nom:>26}  n {len(S):6d}  (pocos)"); return
    ex = S.vuelve - S.base
    m, s = ex.mean(), ex.std(ddof=1); ic = 1.96*s/sqrt(len(S))
    print(f"{nom:>26}  n {len(S):6,}  vuelve {100*S.vuelve.mean():5.1f} %  "
          f"liston {100*S.base.mean():5.1f} %  EXCESO {100*m:+6.1f} %  "
          f"IC95 [{100*(m-ic):+5.1f}, {100*(m+ic):+5.1f}]  "
          f"velas {S.velas.median():4.0f}")

for ins, ruta in INS.items():
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    print("\n" + "="*132); print(ins.upper()); print("="*132)
    for tf, mins in TFS.items():
        V = velas(m1, mins)
        if len(V) < 500: continue
        D = analiza(V)
        if len(D) < 50: continue
        linea(f"{tf}  TODOS", D)
        for nom, sel in (("consolidacion", D.r3 <= 0.50),
                         ("intermedio", (D.r3 > 0.50) & (D.r3 < 1.00)),
                         ("breakaway", D.r3 >= 1.00)):
            linea(f"   {nom}", D[sel & D.r3.notna()])
        linea("   alcistas", D[D.alcista])
        linea("   bajistas", D[~D.alcista])
        D.to_csv(f"data/fvg_{ins}_{tf}.csv", index=False)
