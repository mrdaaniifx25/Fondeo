"""Pre-registro docs/PREREGISTRO_rr_extremo.md

Las mismas ~30.000 entradas de bt/benjamin_regla.py, resueltas a R:R de 2 a 30.
Solo cambia el objetivo. Con placebo de lados barajados en TODAS las celdas.
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, PIV, ESP = 1e-4, 1.43, 3, 30
RRS = [2, 3, 5, 8, 12, 20, 30]
HORIZONTES = {"1 día": 60*24, "5 días": 60*24*5, "20 días": 60*24*20}
M1M = np.timedelta64(1, "m")
rng = np.random.default_rng(97)

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
mts = m1.ts.to_numpy(); mh = m1.high.to_numpy(); ml = m1.low.to_numpy()
mc = m1.close.to_numpy(); M = len(m1)

def velas(mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(h=("high","max"), l=("low","min"), c=("close","last"),
                n=("close","size")).dropna())
    return g[g.n >= max(1, mins*0.3)].reset_index()
V = {k: velas(k) for k in (2, 60)}

def niveles(tf):
    d = V[tf]; h, l = d.h.to_numpy(), d.l.to_numpy()
    t = d.ts.to_numpy("datetime64[ns]"); out = []
    for i in range(PIV, len(d)-PIV):
        if h[i] == h[i-PIV:i+PIV+1].max(): out.append((t[i+PIV]+tf*M1M, h[i], -1))
        if l[i] == l[i-PIV:i+PIV+1].min(): out.append((t[i+PIV]+tf*M1M, l[i], +1))
    out.sort(key=lambda x: x[0])
    return (np.array([x[0] for x in out], dtype="datetime64[ns]"),
            np.array([x[1] for x in out]), np.array([x[2] for x in out], int))
nt, npv, nls = niveles(60)

# --------- se recogen las entradas UNA vez (identicas a benjamin_regla) -------
d = V[2]; ts = d.ts.to_numpy("datetime64[ns]")
h, l, c = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy(); N = len(d)
al = np.zeros(N, bool); ba = np.zeros(N, bool)
al[2:] = l[2:] > h[:-2]; ba[2:] = h[2:] < l[:-2]
loc = pd.DatetimeIndex(ts).tz_localize("UTC").tz_convert("Europe/Madrid")
hm = loc.hour.to_numpy() + loc.minute.to_numpy()/60
vent = ((hm >= 9) & (hm < 11)) | ((hm >= 14) & (hm < 16.5))
dia = pd.DatetimeIndex(ts).normalize().to_numpy()

ENT = []; usado = set()
for k in range(3, N-1):
    j = int(np.searchsorted(nt, ts[k], "right"))
    if j == 0: continue
    for q in range(max(0, j-40), j):
        lado = nls[q]; niv = npv[q]
        if not ((h[k] > niv) if lado < 0 else (l[k] < niv)): continue
        clave = (dia[k], round(float(niv), 5))
        if clave in usado: continue
        kf = -1
        for z in range(k, min(k+ESP, N)):
            if (ba[z] if lado < 0 else al[z]): kf = z; break
        if kf < 0 or not vent[kf]: continue
        P = c[kf]; S = h[k:kf+1].max() if lado < 0 else l[k:kf+1].min()
        rgo = abs(S-P)
        if rgo <= 0: continue
        usado.add(clave)
        i0 = int(np.searchsorted(mts, ts[kf] + 2*M1M, "left"))
        if i0 >= M-2: continue
        ENT.append((P, rgo, lado, i0))
        break
print(f"entradas: {len(ENT):,}   stop mediano {np.median([e[1] for e in ENT])/U:.1f} p\n")

def resuelve(RR, HOR, baraja=False):
    G, CR, SIN, RR_real = [], [], [], []
    for P, rgo, lado, i0 in ENT:
        L = lado if not baraja else (1 if rng.random() < .5 else -1)
        S = P + rgo if L < 0 else P - rgo
        O = P - RR*rgo if L < 0 else P + RR*rgo
        j1 = min(i0+HOR, M)
        hh, ll = mh[i0:j1], ml[i0:j1]
        gt, gs = ((ll <= O, hh >= S) if L < 0 else (hh >= O, ll <= S))
        it = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = mc[j1-1]
            RR_real.append(((P-sal) if L < 0 else (sal-P))/rgo); G.append(0); SIN.append(1)
        elif isl <= it: RR_real.append(-1.0); G.append(0); SIN.append(0)
        else: RR_real.append(float(RR)); G.append(1); SIN.append(0)
        CR.append(COSTE/(rgo/U))
    G = np.array(G, float); R = np.array(RR_real) - np.array(CR)
    return G, R, np.array(SIN, float), np.array(CR)

def linea(et, RR, G, R, SIN, CR, ind="  "):
    azar = 1/(1+RR); ac = G.mean()
    ex = 100*(ac-azar); razon = ac/azar if azar > 0 else np.nan
    mn, ic = R.mean(), 1.96*R.std(ddof=1)/sqrt(len(R))
    um = 100*(1+CR.mean())/(1+RR)
    print(f"{ind}{et:<16}{100*azar:>7.2f}%{100*ac:>8.2f}%{um:>8.2f}%{ex:>+8.2f}"
          f"{razon:>8.3f}{100*SIN.mean():>8.1f}%{mn:>+9.4f} [{mn-ic:>+.4f},{mn+ic:>+.4f}]"
          f"{'  CRUZA' if mn-ic > 0 else ''}")

for hnom, HOR in HORIZONTES.items():
    print("="*118)
    print(f"HORIZONTE {hnom}")
    print("="*118)
    print(f"  {'R:R':<16}{'azar':>7}{'acierto':>8}{'umbral':>8}{'exceso':>8}"
          f"{'razón':>8}{'sin res.':>8}{'NETA':>26}")
    print("  " + "-"*108)
    for RR in RRS:
        linea(f"{RR}:1", RR, *resuelve(RR, HOR))
    print(f"  {'-'*40} placebo, lados barajados {'-'*40}")
    for RR in RRS:
        linea(f"{RR}:1 barajado", RR, *resuelve(RR, HOR, baraja=True))
    print()
