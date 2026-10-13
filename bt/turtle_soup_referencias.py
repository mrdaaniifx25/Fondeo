"""El barrido y vuelta con cada referencia posible, para ver cuales son
aritmeticamente viables antes de mirar si ganan.

Ejecucion en M5 -que es donde el opera- barriendo el extremo de la vela anterior
ya cerrada de M15, H1, H4 o D1. Stop en la mecha del barrido, objetivo 1:2.

  python3 bt/turtle_soup_referencias.py
"""
import numpy as np, pandas as pd
from math import sqrt, erf
TZ, U, COSTE = "Europe/Madrid", 1e-4, 1.43
zf = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x))) if len(x) > 2 else np.nan
p1 = lambda z: 1-0.5*(1+erf(z/sqrt(2)))

d = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
               pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").reset_index(drop=True)
d["loc"] = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
T = d["loc"].to_numpy(); Hm = d.high.to_numpy(); Lm = d.low.to_numpy(); Cm = d.close.to_numpy()

def velas(paso):
    g = d.set_index("loc").resample(f"{paso}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
        n=("close","size")).dropna()
    g = g[g.n >= max(2, paso*0.3)].reset_index()
    g["fin"] = g["loc"] + pd.Timedelta(minutes=paso)
    return g

V5 = velas(5)
t5 = V5.fin.to_numpy()
print(f"{len(V5):,} velas de M5\n")
print(f"  {'referencia':>11s} {'n':>6s} {'stop med':>9s} {'c/riesgo':>9s} "
      f"{'ventaja que':>12s} {'acierto':>9s} {'la tiene?':>10s} {'R neta':>8s} {'z':>7s}")
print(f"  {'':>11s} {'':>6s} {'':>9s} {'':>9s} {'hace falta':>12s}")
print("  " + "-"*88)
for nom, paso in (("M15", 15), ("H1", 60), ("H4", 240), ("D1", 1440)):
    R = velas(paso)
    # para cada vela de M5, cual es la vela de referencia YA CERRADA anterior
    j = np.searchsorted(R.fin.to_numpy(), t5, side="right") - 1
    ok = j >= 0
    rh = np.where(ok, R.h.to_numpy()[np.clip(j,0,None)], np.nan)
    rl = np.where(ok, R.l.to_numpy()[np.clip(j,0,None)], np.nan)
    ro = np.where(ok, R.o.to_numpy()[np.clip(j,0,None)], np.nan)
    rc = np.where(ok, R.c.to_numpy()[np.clip(j,0,None)], np.nan)
    cA, cB = np.minimum(ro, rc), np.maximum(ro, rc)
    H5, L5, C5 = V5.h.to_numpy(), V5.l.to_numpy(), V5.c.to_numpy()
    dentro = (C5 >= cA) & (C5 <= cB)
    alto = ok & (H5 > rh) & dentro
    bajo = ok & (L5 < rl) & dentro
    alto &= ~bajo; bajo &= ~(ok & (H5 > rh) & dentro & bajo & False)
    filas = []
    libre = np.datetime64("1900-01-01")
    for i in np.where(alto | bajo)[0]:
        ts = t5[i]
        if ts <= libre: continue
        lado = -1 if alto[i] else 1
        ent = float(C5[i]); stp = float(H5[i] if lado < 0 else L5[i])
        rgo = abs(ent - stp)
        if rgo < 1.5*U: continue
        tp = ent + lado*2*rgo
        fin = ts + np.timedelta64(3, "D")
        a = int(np.searchsorted(T, ts)); b = int(np.searchsorted(T, fin))
        b = min(max(b, a+1), len(T))
        hh, ll = Hm[a:b], Lm[a:b]
        largo = lado > 0
        gs, gt = ((ll <= stp, hh >= tp) if largo else (hh >= stp, ll <= tp))
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        itp = int(np.argmax(gt)) if gt.any() else 10**9
        if isl == 10**9 and itp == 10**9:
            sal = Cm[b-1]; Rr = ((sal-ent) if largo else (ent-sal))/rgo; mot = "cierre"
            libre = fin
        else:
            Rr, mot = (-1.0, "SL") if isl <= itp else (2.0, "TP")
            libre = T[a + min(isl, itp)]
        filas.append((rgo/U, Rr, mot))
    if len(filas) < 30:
        print(f"  {nom:>11s} {len(filas):6d}  muy pocas"); continue
    f = pd.DataFrame(filas, columns=["rgo","R","mot"])
    f["neta"] = f.R - COSTE/f.rgo
    res = f[f.mot != "cierre"]
    ac = (res.mot == "TP").mean()
    stop = f.rgo.median()
    falta = (COSTE/stop)/3*100        # puntos sobre el 33,3 % geometrico, a 1:2
    tiene = (ac - 1/3)*100
    print(f"  {nom:>11s} {len(f):6d} {stop:8.1f}p {100*COSTE/stop:8.1f}% "
          f"{falta:11.1f}pt {100*ac:8.1f}% {tiene:+9.1f}pt {f.neta.mean():+8.3f} "
          f"{zf(f.neta.to_numpy()):+7.2f}")
print("""
  «ventaja que hace falta» = (coste/stop)/(1+k), los puntos que hay que sacarle
  al 33,3 % geometrico solo para empatar. «la tiene?» es lo que saca de verdad.""")
