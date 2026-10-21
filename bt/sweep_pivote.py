"""Su stop (pivote de estructura) sin su gatillo (cambio de estructura).
Ampliacion del pre-registro docs/PREREGISTRO_sweep_choch.md
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, RR, K = 1e-4, 1.43, 2.0, 2

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
t1 = m1.ts.to_numpy(); h1v = m1.high.to_numpy(); l1v = m1.low.to_numpy()

def velas(mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    return g[g.n >= mins * 0.3].reset_index()

def resuelve(ts, stop, obj, largo):
    i = int(np.searchsorted(t1, np.datetime64(ts), side="right"))
    for k in range(i, min(len(t1), i + 60*24*3)):
        if largo:
            if l1v[k] <= stop: return 0
            if h1v[k] >= obj:  return 1
        else:
            if h1v[k] >= stop: return 0
            if l1v[k] <= obj:  return 1
    return None

def corre(tf_alto, tf_bajo):
    H = velas(tf_alto); L = velas(tf_bajo)
    Ht = H.ts.to_numpy(); ph = np.roll(H.h.to_numpy(),1); pl = np.roll(H.l.to_numpy(),1)
    ph[0] = pl[0] = np.nan
    Lt = L.ts.to_numpy(); Lh = L.h.to_numpy(); Ll = L.l.to_numpy(); Lc = L.c.to_numpy()
    n = len(L); iH = np.searchsorted(Ht, Lt, side="right") - 1

    esMax = np.zeros(n, bool); esMin = np.zeros(n, bool)
    for j in range(K, n-K):
        v = Lh[j-K:j+K+1]; esMax[j] = (v.argmax() == K)
        w = Ll[j-K:j+K+1]; esMin[j] = (w.argmin() == K)

    ops = []
    ultMax = ultMin = np.nan
    hechoV = hechoC = -1
    for j in range(K, n):
        p = j - K
        if esMax[p]: ultMax = Lh[p]
        if esMin[p]: ultMin = Ll[p]
        k = iH[j]
        if k < 1 or not np.isfinite(ph[k]): continue
        ini = int(np.searchsorted(Lt, Ht[k], side="left"))
        if j <= ini: continue
        hasta_hi = Lh[ini:j+1].max(); hasta_lo = Ll[ini:j+1].min()

        for lado, cond, ext, piv in (
            ("venta",  hasta_hi > ph[k] and Lc[j] < ph[k], hasta_hi, ultMax),
            ("compra", hasta_lo < pl[k] and Lc[j] > pl[k], hasta_lo, ultMin)):
            if not cond or not np.isfinite(piv): continue
            if lado == "venta" and hechoV == k: continue
            if lado == "compra" and hechoC == k: continue
            largo = lado == "compra"
            for off in (0, 1, 2):
                jj = j + off
                if jj >= n: break
                ent = Lc[jj]
                # el extremo del barrido y el pivote se RECALCULAN en la vela de
                # entrada: usar los de la vela j seria darle al stop un pase
                # gratis por lo ocurrido entre j y jj, que es mirar al futuro
                ext_jj = Lh[ini:jj+1].max() if not largo else Ll[ini:jj+1].min()
                piv_jj = piv
                for q in range(j - K + 1, jj - K + 1):
                    if q < 0 or q >= n: continue
                    if not largo and esMax[q]: piv_jj = Lh[q]
                    if largo and esMin[q]: piv_jj = Ll[q]
                for snom, stop in (("S1", piv_jj),
                                   ("S2", max(piv_jj, ext_jj) if not largo else min(piv_jj, ext_jj))):
                    rgo = (stop - ent) if not largo else (ent - stop)
                    if rgo <= 0: continue
                    obj = ent + (RR*rgo if largo else -RR*rgo)
                    ops.append((f"E{off}+{snom}", lado,
                                Lt[jj] + np.timedelta64(tf_bajo, 'm'),
                                ent, stop, obj, rgo/U, largo))
            if lado == "venta": hechoV = k
            else: hechoC = k

    D = pd.DataFrame(ops, columns=["celda","lado","t","ent","stop","obj","rgoP","largo"])
    D["gana"] = [resuelve(r.t, r.stop, r.obj, r.largo) for r in D.itertuples()]
    D = D[D.gana.notna()].copy(); D["gana"] = D.gana.astype(int)
    D["Rb"] = 3*D.gana - 1
    D["Rn"] = D.Rb - COSTE/D.rgoP
    D["anio"] = pd.DatetimeIndex(D.t).year
    return D

def linea(nom, S, marca=""):
    if len(S) < 25: print(f"{nom:>14}  n {len(S):5d}  (pocas)"); return
    m, s = S.Rn.mean(), S.Rn.std(ddof=1)
    ic = 1.96*s/sqrt(len(S)); z = m/(s/sqrt(len(S)))
    zb = S.Rb.mean()/(S.Rb.std(ddof=1)/sqrt(len(S)))
    print(f"{nom:>14}  n {len(S):5d}  acierto {100*S.gana.mean():5.1f} %  "
          f"riesgo {S.rgoP.median():5.1f} p  coste {100*COSTE/S.rgoP.median():5.1f} %  "
          f"bruta {S.Rb.mean():+.4f} (z {zb:+.2f})  NETA {m:+.4f}  "
          f"IC95 [{m-ic:+.4f}, {m+ic:+.4f}]  z {z:+.2f} {marca}")

for alto, bajo, nom in ((240, 15, "H4 + M15"), (60, 5, "H1 + M5")):
    D = corre(alto, bajo)
    dias = pd.DatetimeIndex(D.t).normalize().nunique()
    print("="*142); print(nom); print("="*142)
    for c in ("E0+S2","E0+S1","E1+S2","E1+S1","E2+S2","E2+S1"):
        S = D[D.celda == c]
        linea(c, S, "<- CELDA PRINCIPAL" if (c=="E0+S2" and alto==240) else
                    f"({len(S)/max(dias,1):.2f}/dia)")
    P = D[D.celda == "E0+S2"]
    if len(P) > 100:
        print("  por año:")
        for y in sorted(P.anio.unique()): linea(f"  {y}", P[P.anio==y])
    D.to_csv(f"data/sweep_pivote_{alto}_{bajo}.csv", index=False)
    print()
