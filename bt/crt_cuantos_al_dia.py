"""¿Cuantos CRT hay cada dia, y cuantos ganan?

    "cada dia hay un trade ganador con CRT que lo veo y a nosotros no nos
     salen los numeros... aunque sea a toro pasado pero si se dan las
     condiciones"

Las dos cosas pueden ser ciertas a la vez, y este script mide exactamente
cuanto de ciertas. Se cuentan TODOS los CRT de cada dia y se mira cuantos
ganan y cuantos pierden.

  python3 bt/crt_cuantos_al_dia.py
"""
import numpy as np, pandas as pd

U, COSTE = 1e-4, 1.43
M = pd.read_parquet("data/eurusd_m1.parquet")
M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
mh, ml, mc, mt = (M.high.to_numpy(), M.low.to_numpy(),
                  M.close.to_numpy(), M.ts.to_numpy())


def senales(mins, velas=3):
    B = M.set_index("ts").resample(f"{mins}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    B = B[B.n >= max(1, mins*0.3)]
    h, l, c = B.h.to_numpy(), B.l.to_numpy(), B.c.to_numpy()
    ti = B.index.to_numpy(); out = []
    for i in range(1, len(B)-1):
        if h[i] > h[i-1] and c[i] < h[i-1]: lado, stop, obj = -1, h[i], l[i-1]
        elif l[i] < l[i-1] and c[i] > l[i-1]: lado, stop, obj = +1, l[i], h[i-1]
        else: continue
        ent = c[i]; rgo = abs(ent-stop)
        if rgo < 2*U or (obj-ent)*lado <= 0: continue
        j0 = int(np.searchsorted(mt, ti[i] + np.timedelta64(mins, "m")))
        j1 = min(j0 + mins*velas, len(mt))
        if j1 <= j0+3: continue
        hh, ll = mh[j0:j1], ml[j0:j1]
        a = np.flatnonzero(hh >= obj) if lado > 0 else np.flatnonzero(ll <= obj)
        b = np.flatnonzero(ll <= stop) if lado > 0 else np.flatnonzero(hh >= stop)
        ia = int(a[0]) if len(a) else 10**9
        ib = int(b[0]) if len(b) else 10**9
        rr = abs(obj-ent)/rgo
        gana = ia < ib
        R = (rr if gana else (-1.0 if ib < 10**9 else
             (float(mc[j1-1])-ent)*lado/rgo))
        out.append((pd.Timestamp(ti[i]).date(), int(gana), R, R - COSTE*U/rgo))
    return pd.DataFrame(out, columns=["dia","gana","R","neta"])


print("=== EURUSD · TODOS los CRT, contados por dia ===\n")
print(f"  {'marco':>7} {'senales':>9} {'al dia':>8} {'ganan':>7} {'pierden':>8} "
      f"{'dias con >=1':>14} {'R neta media':>13} {'suma neta':>11}")
for mins, nom in ((15,"M15"), (60,"H1"), (240,"H4"), (720,"H12")):
    D = senales(mins)
    g = D.groupby("dia").agg(n=("gana","size"), w=("gana","sum"))
    print(f"  {nom:>7} {len(D):>9} {g.n.mean():>8.1f} {D.gana.mean():>6.1%} "
          f"{1-D.gana.mean():>7.1%} {(g.w >= 1).mean():>13.1%} "
          f"{D.neta.mean():>+13.4f} {D.neta.sum():>+10.1f} R")

print("\n  las dos frases son ciertas a la vez:\n")
D = senales(15)
g = D.groupby("dia").agg(n=("gana","size"), w=("gana","sum"))
print(f"    en M15, un dia cualquiera trae {g.n.mean():.0f} CRT de media")
print(f"    y {(g.w >= 1).mean():.0%} de los dias tienen AL MENOS UNO que gana")
print(f"    pero de cada 10 CRT, ganan {D.gana.mean()*10:.0f} y pierden {10-D.gana.mean()*10:.0f}")
print(f"    y el conjunto pierde {abs(D.neta.sum()):.0f} R en 6,5 anos")
print(f"\n    dias con 2 o mas ganadores: {(g.w >= 2).mean():.0%}")
print(f"    dias con 3 o mas ganadores: {(g.w >= 3).mean():.0%}")
