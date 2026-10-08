"""Pre-registro docs/PREREGISTRO_benjamin_regla.md

EURUSD · nivel de H1/H4 · barrido · bajar a M2/M5 · impulso + imbalance ·
stop por encima del extremo del barrido · objetivo 1:2 · Londres y NY.
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, HOR, PIV, ESP = 1e-4, 1.43, 24*60, 3, 30
M1M = np.timedelta64(1, "m")
rng = np.random.default_rng(97)

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
mts = m1.ts.to_numpy("datetime64[ns]"); mh = m1.high.to_numpy()
ml = m1.low.to_numpy(); M = len(m1)
anos = (m1.ts.max()-m1.ts.min()).days/365.25

def velas(mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(h=("high","max"), l=("low","min"), c=("close","last"),
                n=("close","size")).dropna())
    return g[g.n >= max(1, mins*0.3)].reset_index()

V = {k: velas(k) for k in (2, 5, 60, 240)}

def niveles(tf):
    d = V[tf]; h, l = d.h.to_numpy(), d.l.to_numpy()
    t = d.ts.to_numpy("datetime64[ns]")
    out = []
    for i in range(PIV, len(d)-PIV):
        if h[i] == h[i-PIV:i+PIV+1].max(): out.append((t[i+PIV] + tf*M1M, h[i], -1))
        if l[i] == l[i-PIV:i+PIV+1].min(): out.append((t[i+PIV] + tf*M1M, l[i], +1))
    out.sort(key=lambda x: x[0])
    return (np.array([x[0] for x in out], dtype="datetime64[ns]"),
            np.array([x[1] for x in out]), np.array([x[2] for x in out], int))

NIV = {tf: niveles(tf) for tf in (60, 240)}

def corre(tf_ent, tf_niv, solo_horario, barajar=False):
    d = V[tf_ent]
    ts = d.ts.to_numpy("datetime64[ns]"); h, l, c = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    N = len(d)
    al = np.zeros(N, bool); ba = np.zeros(N, bool)
    al[2:] = l[2:] > h[:-2]; ba[2:] = h[2:] < l[:-2]
    nt, np_, nl = NIV[tf_niv]
    loc = pd.DatetimeIndex(ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    hm = loc.hour.to_numpy() + loc.minute.to_numpy()/60
    vent = ((hm >= 9) & (hm < 11)) | ((hm >= 14) & (hm < 16.5))
    dia = pd.DatetimeIndex(ts).normalize().to_numpy()

    filas = []; usado = set()
    for k in range(3, N-1):
        j = int(np.searchsorted(nt, ts[k], "right"))
        if j == 0: continue
        for q in range(max(0, j-40), j):
            lado = nl[q]; niv = np_[q]
            barre = (h[k] > niv) if lado < 0 else (l[k] < niv)
            if not barre: continue
            clave = (dia[k], round(float(niv), 5))
            if clave in usado: continue
            # buscar impulso + imbalance a favor del giro en las ESP velas siguientes
            kf = -1
            for z in range(k, min(k+ESP, N)):
                if (ba[z] if lado < 0 else al[z]): kf = z; break
            if kf < 0: continue
            if solo_horario and not vent[kf]: continue
            P = c[kf]
            S = h[k:kf+1].max() if lado < 0 else l[k:kf+1].min()
            rgo = abs(S-P)
            if rgo <= 0: continue
            L = lado if not barajar else (1 if rng.random() < .5 else -1)
            if L != lado: S = P + rgo if L < 0 else P - rgo
            O = P - 2*rgo if L < 0 else P + 2*rgo
            if L < 0 and not (S > P > O): continue
            if L > 0 and not (S < P < O): continue
            usado.add(clave)
            i0 = int(np.searchsorted(mts, ts[kf] + tf_ent*M1M, "left"))
            if i0 >= M-2: continue
            g = 0
            for x in range(i0, min(i0+HOR, M)):
                if L < 0:
                    if mh[x] >= S: break
                    if ml[x] <= O: g = 1; break
                else:
                    if ml[x] <= S: break
                    if mh[x] >= O: g = 1; break
            filas.append((rgo/U, g, pd.Timestamp(ts[kf]).year))
            break
    if not filas: return None
    D = pd.DataFrame(filas, columns=["rgo","gana","anio"])
    D["Rb"] = np.where(D.gana == 1, 2.0, -1.0)
    D["Rn"] = D.Rb - COSTE/D.rgo
    return D

def linea(nom, D):
    if D is None or len(D) < 30: return print(f"  {nom:<34} (pocas)")
    ex = D.gana - 1/3; e, eic = 100*ex.mean(), 196*ex.std(ddof=1)/sqrt(len(D))
    mn, icn = D.Rn.mean(), 1.96*D.Rn.std(ddof=1)/sqrt(len(D))
    cst = (COSTE/D.rgo).median()
    print(f"  {nom:<34} n {len(D):5,} ({len(D)/anos:4.0f}/año)  acierto {100*D.gana.mean():5.1f} % "
          f"(azar 33,3)  exceso {e:+5.1f} [{e-eic:+5.1f},{e+eic:+5.1f}]"
          f"{'*' if (e-eic)*(e+eic)>0 else ' '}  riesgo {D.rgo.median():5.1f}p  "
          f"coste {100*cst:4.1f} %  umbral {100*(1+cst)/3:4.1f} %  "
          f"NETA {mn:+.4f} [{mn-icn:+.4f},{mn+icn:+.4f}]")

print(f"La regla de Benjamin · EURUSD {m1.ts.min():%Y}-{m1.ts.max():%Y} ({anos:.1f} años)\n" + "="*168)
for tfe in (2, 5):
    for tfn in (60, 240):
        for sh, et in ((True, "SUS HORAS"), (False, "todo el día")):
            linea(f"M{tfe} · nivel H{tfn//60} · {et}", corre(tfe, tfn, sh))
    print()
print("="*168 + "\nnulos sobre la celda principal (M2 · H1 · sus horas)")
linea("  lados barajados", corre(2, 60, True, barajar=True))
