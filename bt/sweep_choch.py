"""Barrido en H4/H1 + cambio de estructura en M15/M5.
Pre-registro docs/PREREGISTRO_sweep_choch.md
"""
import sys
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, RR = 1e-4, 1.43, 2.0
K = 2                       # fractal: 2 velas a cada lado

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
t1 = m1.ts.to_numpy(); h1v = m1.high.to_numpy(); l1v = m1.low.to_numpy()

def velas(mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    return g[g.n >= mins * 0.3].reset_index()

def resuelve(ts, stop, obj, largo):
    i = int(np.searchsorted(t1, np.datetime64(ts), side="right"))
    for k in range(i, min(len(t1), i + 60 * 24 * 3)):
        if largo:
            if l1v[k] <= stop: return 0
            if h1v[k] >= obj:  return 1
        else:
            if h1v[k] >= stop: return 0
            if l1v[k] <= obj:  return 1
    return None

def corre(tf_alto, tf_bajo):
    H = velas(tf_alto); L = velas(tf_bajo)
    Ht = H.ts.to_numpy(); Hh = H.h.to_numpy(); Hl = H.l.to_numpy()
    ph, pl = np.roll(Hh, 1), np.roll(Hl, 1)          # vela ANTERIOR ya cerrada
    ph[0] = pl[0] = np.nan
    paso = np.timedelta64(tf_alto, "m")

    Lt = L.ts.to_numpy(); Lh = L.h.to_numpy(); Ll = L.l.to_numpy(); Lc = L.c.to_numpy()
    n = len(L)
    # a que vela de H pertenece cada vela de L
    iH = np.searchsorted(Ht, Lt, side="right") - 1

    # pivotes fractales, CONFIRMADOS K velas despues: en la vela j solo se
    # conoce el pivote de j-K
    esMax = np.zeros(n, bool); esMin = np.zeros(n, bool)
    for j in range(K, n - K):
        v = Lh[j-K:j+K+1]; esMax[j] = Lh[j] == v.max() and (v.argmax() == K)
        w = Ll[j-K:j+K+1]; esMin[j] = Ll[j] == w.min() and (w.argmin() == K)

    ops = []
    ultMax = ultMin = np.nan          # pivotes ya confirmados
    pMax = pMin = np.nan
    usado = -1
    for j in range(K, n):
        # confirmar el pivote de j-K con lo visto hasta j
        p = j - K
        if esMax[p]: ultMax, pMax = Lh[p], p
        if esMin[p]: ultMin, pMin = Ll[p], p

        k = iH[j]
        if k < 1 or not np.isfinite(ph[k]): continue
        if k == usado: continue
        # el barrido tiene que estar EN CURSO dentro de esta vela de H:
        # maximo/minimo de la vela de H hasta AHORA, solo con velas de L cerradas
        ini = int(np.searchsorted(Lt, Ht[k], side="left"))
        if j <= ini: continue
        hasta_hi = Lh[ini:j+1].max(); hasta_lo = Ll[ini:j+1].min()

        # VENTA: ha barrido el maximo anterior y el precio ha vuelto dentro
        if hasta_hi > ph[k] and Lc[j] < ph[k] and np.isfinite(ultMin) and np.isfinite(ultMax):
            if pMin > pMax and Lc[j] < ultMin:          # cierra bajo el ultimo minimo
                stop = max(ultMax, hasta_hi) if False else ultMax
                ent = Lc[j]
                if stop > ent:
                    rgo = stop - ent
                    ops.append(("venta", Lt[j], ent, stop, ent - RR * rgo, rgo / U, False))
                    usado = k; continue
        # COMPRA
        if hasta_lo < pl[k] and Lc[j] > pl[k] and np.isfinite(ultMax) and np.isfinite(ultMin):
            if pMax > pMin and Lc[j] > ultMax:
                stop = ultMin
                ent = Lc[j]
                if stop < ent:
                    rgo = ent - stop
                    ops.append(("compra", Lt[j], ent, stop, ent + RR * rgo, rgo / U, True))
                    usado = k

    D = pd.DataFrame(ops, columns=["lado","t","ent","stop","obj","rgoP","largo"])
    if not len(D): return D
    D["gana"] = [resuelve(r.t, r.stop, r.obj, r.largo) for r in D.itertuples()]
    D = D[D.gana.notna()].copy(); D["gana"] = D.gana.astype(int)
    D["Rb"] = 3 * D.gana - 1
    D["Rn"] = D.Rb - COSTE / D.rgoP
    D["anio"] = pd.DatetimeIndex(D.t).year
    return D

def linea(nom, S):
    if len(S) < 25: print(f"{nom:>26}  n {len(S):5d}  (pocas)"); return
    m, s = S.Rn.mean(), S.Rn.std(ddof=1)
    ic = 1.96 * s / sqrt(len(S)); z = m / (s / sqrt(len(S)))
    zb = S.Rb.mean() / (S.Rb.std(ddof=1) / sqrt(len(S)))
    nec = 100 * (1/3 + COSTE / (3 * S.rgoP.median()))
    print(f"{nom:>26}  n {len(S):5d}  acierto {100*S.gana.mean():5.1f} % (nec {nec:4.1f})  "
          f"riesgo {S.rgoP.median():5.1f} p  coste {100*COSTE/S.rgoP.median():5.1f} %  "
          f"bruta {S.Rb.mean():+.4f} (z {zb:+.2f})  NETA {m:+.4f}  "
          f"IC95 [{m-ic:+.4f}, {m+ic:+.4f}]  z {z:+.2f}")

for alto, bajo, nom in ((240, 15, "H4 + M15"), (60, 5, "H1 + M5")):
    D = corre(alto, bajo)
    print("=" * 140)
    dias = pd.DatetimeIndex(D.t).normalize().nunique() if len(D) else 1
    print(f"{nom}   ·   {len(D)} operaciones   ·   {len(D)/max(dias,1):.2f} al dia")
    print("=" * 140)
    if not len(D): continue
    linea("TODO", D)
    for lado in ("compra", "venta"): linea(lado, D[D.lado == lado])
    for y in sorted(D.anio.unique()): linea(str(y), D[D.anio == y])
    print("  riesgo en pips:", D.rgoP.describe(percentiles=[.1,.25,.5,.75,.9]).round(1).to_dict())
    D.to_csv(f"data/sweep_choch_{alto}_{bajo}.csv", index=False)
    print()
