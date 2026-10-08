"""El AMD en dinero, con stop y objetivo medidos igual (los dos por toque)
y el camino resuelto en M1, que es lo unico que no se inventa el orden
dentro de la vela. Si stop y objetivo caen en el mismo minuto: perdida.
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, ESPM, ESPD = 1e-4, 1.43, 20, 20

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
t1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy()

def velas(mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    return g[g.n >= mins * 0.3].reset_index()

def atr(h, l, c, n):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return np.roll(pd.Series(tr).rolling(n).mean().to_numpy(), 1)

def resuelve(ts, stop, obj, largo, limite):
    i = int(np.searchsorted(t1, np.datetime64(ts), side="left"))
    fin = int(np.searchsorted(t1, np.datetime64(limite), side="right"))
    for k in range(i, min(fin, len(t1))):
        if largo:
            if L1[k] <= stop: return 0
            if H1[k] >= obj:  return 1
        else:
            if H1[k] >= stop: return 0
            if L1[k] <= obj:  return 1
    return 0                      # se agota el plazo: no llego, cuenta como fallo

def corre(mins, n, mins_tf):
    V = velas(mins)
    h = V.h.to_numpy(); l = V.l.to_numpy(); c = V.c.to_numpy()
    ts = V.ts.to_numpy(); N = len(V)
    a14 = atr(h, l, c, 14)
    hi = pd.Series(h).rolling(n).max().to_numpy()
    lo = pd.Series(l).rolling(n).min().to_numpy()
    normal = a14 * sqrt(n)
    ratio = np.where(normal > 0, (hi - lo) / normal, np.nan)
    filas = []; i = n
    while i < N - 1:
        if not np.isfinite(ratio[i]): i += 1; continue
        rHi, rLo, r0 = hi[i], lo[i], ratio[i]
        if not (rHi > rLo): i += 1; continue
        manip = -1; lado = 0; ext = np.nan; j = i + 1
        while j < min(i + 1 + ESPM, N):
            if h[j] > rHi or l[j] < rLo:
                arr = h[j] > rHi and rLo < c[j] < rHi
                aba = l[j] < rLo and rLo < c[j] < rHi
                if arr or aba:
                    manip = j; lado = -1 if arr else 1
                    ext = h[j] if arr else l[j]
                break
            j += 1
        if manip < 0: i = max(j, i + 1); continue
        P = c[manip]; stop = ext; obj = rLo if lado < 0 else rHi
        rgo = abs(stop - P); rec = abs(obj - P)
        if rgo <= 0 or rec <= 0: i = manip + 1; continue
        # entra al CIERRE de la vela de la manipulacion
        t_ent = pd.Timestamp(ts[manip]) + pd.Timedelta(minutes=mins_tf)
        t_fin = t_ent + pd.Timedelta(minutes=mins_tf * ESPD)
        g = resuelve(t_ent, stop, obj, lado > 0, t_fin)
        filas.append((r0, rgo / U, rec / rgo, g))
        i = manip + 1
    D = pd.DataFrame(filas, columns=["ratio","rgoP","rr","gana"])
    D["Rb"] = np.where(D.gana == 1, D.rr, -1.0)
    D["Rn"] = D.Rb - COSTE / D.rgoP
    return D

for tf, mins, n in (("M15", 15, 12), ("H1", 60, 12), ("H4", 240, 8)):
    D = corre(mins, n, mins)
    D["q"] = pd.qcut(D.ratio.rank(method="first"), 5, labels=False) + 1
    print(f"\n{tf}  n={n}   ·   {len(D):,} secuencias   ·   stop y objetivo "
          f"medidos igual, camino en M1")
    print(f"{'quintil':>8}{'estrechez':>11}{'n':>8}{'acierto':>9}{'justo':>8}"
          f"{'R:R':>7}{'riesgo':>9}{'coste':>7}{'BRUTA':>10}{'NETA':>10}{'IC95':>20}")
    for q, S in D.groupby("q"):
        justo = 100 / (1 + S.rr.median())
        m, s = S.Rn.mean(), S.Rn.std(ddof=1); ic = 1.96 * s / sqrt(len(S))
        print(f"{q:>8}{S.ratio.median():>11.2f}{len(S):>8,}{100*S.gana.mean():>8.1f} %"
              f"{justo:>7.1f} %{S.rr.median():>7.1f}{S.rgoP.median():>8.1f} p"
              f"{100*COSTE/S.rgoP.median():>6.0f} %{S.Rb.mean():>+10.4f}{m:>+10.4f}"
              f"   [{m-ic:+.3f}, {m+ic:+.3f}]")
