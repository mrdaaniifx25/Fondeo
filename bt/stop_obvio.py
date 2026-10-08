"""Pre-registro docs/PREREGISTRO_stop.md

NIVEL   : stop en el maximo/minimo reciente de M5. Objetivo a 2x esa distancia.
CONTROL : misma distancia, misma geometria, pero en otro instante al azar.

Los dos brazos tienen azar = 1/3 exacto. Si NIVEL acierta menos que CONTROL,
la diferencia no es geometria: es el sitio donde esta puesta la barrera.
"""
import numpy as np, pandas as pd

HOR, NREP, NBOOT = 20*60, 20_000, 2000
rng = np.random.default_rng(67)

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
mts = m1.ts.to_numpy("datetime64[ns]"); mh = m1.high.to_numpy()
ml = m1.low.to_numpy(); mc = m1.close.to_numpy(); M = len(m1)
mes = pd.PeriodIndex(pd.DatetimeIndex(mts), freq="M").astype(str).to_numpy()

def resuelve(i, stop, obj, lado):
    for k in range(i, min(i+HOR, M)):
        if lado < 0:
            if mh[k] >= stop: return 0
            if ml[k] <= obj:  return 1
        else:
            if ml[k] <= stop: return 0
            if mh[k] >= obj:  return 1
    return 0

def bloques(x, g):
    gr = {}
    for k, m in enumerate(g): gr.setdefault(m, []).append(k)
    idx = [np.array(v) for v in gr.values()]; G = len(idx)
    sim = np.empty(NBOOT)
    for b in range(NBOOT):
        sel = np.concatenate([idx[p] for p in rng.integers(0, G, G)])
        sim[b] = x[sel].mean()
    return x.mean(), np.percentile(sim, 2.5), np.percentile(sim, 97.5)

tope = M - HOR - 2
print(f"{'N':>4} {'brazo':<10} {'n':>6} {'acierto':>9} {'IC95 (bloques de mes)':>24} "
      f"{'azar':>7} {'exceso':>8}   {'D mediana':>10}")
print("-"*92)
GUARDA = {}
for N in (10, 20, 50):
    pasos = N*5
    gN, gC, mN, mC, DD = [], [], [], [], []
    hecho = 0
    while hecho < NREP:
        i = int(rng.integers(pasos+10, tope))
        lado = -1 if rng.random() < .5 else 1
        P = mc[i-1]
        D = (mh[i-pasos:i].max() - P) if lado < 0 else (P - ml[i-pasos:i].min())
        if not np.isfinite(D) or D <= 1e-5: continue
        # NIVEL: el stop ES el extremo reciente
        sN = P + D*(-lado)*-1 if False else (P + D if lado < 0 else P - D)
        oN = P - 2*D if lado < 0 else P + 2*D
        gN.append(resuelve(i, sN, oN, lado)); mN.append(mes[i]); DD.append(D)
        # CONTROL: misma D y mismo lado, en otro instante cualquiera
        j = int(rng.integers(pasos+10, tope)); Q = mc[j-1]
        sC = Q + D if lado < 0 else Q - D
        oC = Q - 2*D if lado < 0 else Q + 2*D
        gC.append(resuelve(j, sC, oC, lado)); mC.append(mes[j])
        hecho += 1
    gN = np.array(gN, float); gC = np.array(gC, float)
    for nom, g, mm in (("NIVEL", gN, np.array(mN)), ("CONTROL", gC, np.array(mC))):
        m, lo, hi = bloques(g, mm)
        print(f"{N:>4} {nom:<10} {len(g):>6} {100*m:>8.2f}% "
              f"[{100*lo:>9.2f}, {100*hi:>8.2f}] {100/3:>6.2f}% {100*(m-1/3):>+7.2f}"
              f"{'' if lo <= 1/3 <= hi else '   <- fuera del azar':<22}"
              f"{1e4*np.median(DD):>10.1f} p" if nom == "NIVEL" else
              f"{N:>4} {nom:<10} {len(g):>6} {100*m:>8.2f}% "
              f"[{100*lo:>9.2f}, {100*hi:>8.2f}] {100/3:>6.2f}% {100*(m-1/3):>+7.2f}"
              f"{'' if lo <= 1/3 <= hi else '   <- fuera del azar'}")
    d = gN - gC
    md, ld, hd = bloques(d, np.array(mN))
    print(f"{'':>4} {'NIVEL-CONTROL':<10} {'':>6} {100*md:>+8.2f} "
          f"[{100*ld:>9.2f}, {100*hd:>8.2f}]"
          f"{'   <- la diferencia no toca el cero' if ld*hd > 0 else '   (toca el cero)'}")
    GUARDA[N] = (gN.mean(), gC.mean(), md, ld, hd)
    print()
