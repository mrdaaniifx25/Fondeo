"""Pre-registro docs/PREREGISTRO_benjamin_v3.md

Sus niveles + sus horarios + su disparo, con tres vueltas:
entrada en M15/H1, stop por ATR, objetivo en el nivel opuesto.
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, HOR, PIV, ESP = 1e-4, 1.43, 48*60, 3, 12
M1M = np.timedelta64(1, "m")
rng = np.random.default_rng(151)

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

def atr(d, n=14):
    h, l, c = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    a = np.full(len(tr), np.nan); a[n-1] = tr[:n].mean()
    for i in range(n, len(tr)): a[i] = (a[i-1]*(n-1)+tr[i])/n
    return np.roll(a, 1)

def piv(d, tf):
    h, l = d.h.to_numpy(), d.l.to_numpy(); t = d.ts.to_numpy("datetime64[ns]")
    return [(t[i+PIV]+tf*M1M, h[i], -1) for i in range(PIV, len(d)-PIV)
            if h[i] == h[i-PIV:i+PIV+1].max()] + \
           [(t[i+PIV]+tf*M1M, l[i], +1) for i in range(PIV, len(d)-PIV)
            if l[i] == l[i-PIV:i+PIV+1].min()]
def ext(regla):
    g = (m1.set_index("ts").resample(regla).agg(h=("high","max"), l=("low","min"),
                                                n=("close","size")).dropna())
    g = g[g.n > 200]; t = g.index.to_numpy("datetime64[ns]")
    return [(t[i+1], g.h.iloc[i], -1) for i in range(len(g)-1)] + \
           [(t[i+1], g.l.iloc[i], +1) for i in range(len(g)-1)]

NIV = sorted(piv(velas(60), 60) + piv(velas(240), 240) + ext("D") + ext("W"),
             key=lambda x: x[0])
nt = np.array([x[0] for x in NIV], dtype="datetime64[ns]")
npv = np.array([x[1] for x in NIV]); nls = np.array([x[2] for x in NIV], int)

def corre(tfe, modo_stop, modo_obj, horario=True, barajar=False):
    d = velas(tfe); ts = d.ts.to_numpy("datetime64[ns]")
    h, l, c = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy(); N = len(d)
    A = atr(d)
    al = np.zeros(N, bool); ba = np.zeros(N, bool)
    al[2:] = l[2:] > h[:-2]; ba[2:] = h[2:] < l[:-2]
    loc = pd.DatetimeIndex(ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    hm = loc.hour.to_numpy() + loc.minute.to_numpy()/60
    vent = ((hm >= 9) & (hm < 11)) | ((hm >= 14) & (hm < 16.5))
    dia = pd.DatetimeIndex(ts).normalize().to_numpy()
    filas = []; usado = set()
    for k in range(5, N-1):
        if horario and not vent[k]: continue
        if not np.isfinite(A[k]) or A[k] <= 0: continue
        j = int(np.searchsorted(nt, ts[k], "right"))
        for q in range(max(0, j-80), j):
            lado = nls[q]; niv = npv[q]
            if not ((h[k] > niv) if lado < 0 else (l[k] < niv)): continue
            clave = (dia[k], round(float(niv), 5))
            if clave in usado: continue
            # giro: cierre de vuelta dentro + hueco a favor en ESP velas
            kf = -1; e = h[k] if lado < 0 else l[k]
            for z in range(k, min(k+ESP, N)):
                e = max(e, h[z]) if lado < 0 else min(e, l[z])
                if z > k and (ba[z] if lado < 0 else al[z]): kf = z; break
            if kf < 0: continue
            P = c[kf]
            if modo_stop == "barrido": S = e
            else:
                mult = 1.0 if modo_stop == "atr1" else 1.5
                S = P + mult*A[kf] if lado < 0 else P - mult*A[kf]
                S = max(S, e) if lado < 0 else min(S, e)
            rgo = abs(S-P)
            if rgo <= 0: continue
            if modo_obj == "1:2":
                O = P - 2*rgo if lado < 0 else P + 2*rgo
            else:
                # nivel opuesto mas cercano vivo
                cand = [npv[x] for x in range(max(0, j-80), j)
                        if (npv[x] < P if lado < 0 else npv[x] > P)]
                if not cand: continue
                O = max(cand) if lado < 0 else min(cand)
            L = lado if not barajar else (1 if rng.random() < .5 else -1)
            if L != lado: S, O = (P+rgo, P-abs(O-P)) if L < 0 else (P-rgo, P+abs(O-P))
            if L < 0 and not (S > P > O): continue
            if L > 0 and not (S < P < O): continue
            rec = abs(O-P)
            if rec <= 0: continue
            usado.add(clave)
            i0 = int(np.searchsorted(mts, ts[kf] + tfe*M1M, "left"))
            if i0 >= M-2: continue
            g = 0
            for x in range(i0, min(i0+HOR, M)):
                if L < 0:
                    if mh[x] >= S: break
                    if ml[x] <= O: g = 1; break
                else:
                    if ml[x] <= S: break
                    if mh[x] >= O: g = 1; break
            filas.append((rgo/U, rec/rgo, g, rgo/(rgo+rec))); break
    if not filas: return None
    D = pd.DataFrame(filas, columns=["rgo","rr","gana","azar"])
    D["Rb"] = np.where(D.gana == 1, D.rr, -1.0); D["Rn"] = D.Rb - COSTE/D.rgo
    return D

def linea(nom, D):
    if D is None or len(D) < 30: return print(f"  {nom:<44} (pocas)")
    ex = D.gana - D.azar; e, eic = 100*ex.mean(), 196*ex.std(ddof=1)/sqrt(len(D))
    m, ic = D.Rb.mean(), 1.96*D.Rb.std(ddof=1)/sqrt(len(D))
    mn, icn = D.Rn.mean(), 1.96*D.Rn.std(ddof=1)/sqrt(len(D))
    print(f"  {nom:<44} n {len(D):5,} ({len(D)/anos:4.0f}/a)  acierto {100*D.gana.mean():5.1f} "
          f"(azar {100*D.azar.mean():4.1f})  exceso {e:+5.1f} [{e-eic:+5.1f},{e+eic:+5.1f}]"
          f"{'*' if (e-eic)*(e+eic)>0 else ' '}  R:R {D.rr.median():4.2f}  riesgo {D.rgo.median():5.1f}p "
          f" coste {100*(COSTE/D.rgo).median():4.1f}%  BRUTA {m:+.3f}  "
          f"NETA {mn:+.4f} [{mn-icn:+.4f},{mn+icn:+.4f}]{'   CRUZA +0,05' if mn-icn > 0.05 else ''}")

print(f"La base de Benjamin con las tres vueltas · EURUSD {anos:.1f} años\n" + "="*186)
for tfe, tn in ((15,"M15"), (60,"H1")):
    for ms in ("barrido", "atr1", "atr15"):
        for mo in ("1:2", "opuesto"):
            linea(f"{tn} · stop {ms} · objetivo {mo}", corre(tfe, ms, mo))
    print()
