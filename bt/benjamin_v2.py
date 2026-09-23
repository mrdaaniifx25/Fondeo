"""Pre-registro docs/PREREGISTRO_benjamin_v2.md

Barrido de nivel (semanal/diario/H4/H1) en Londres o NY -> cambio de estructura
con cuerpo -> desequilibrio -> entrada al mitigar el hueco -> stop en el
extremo del barrido -> objetivo 1:2.
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, HOR, PIV = 1e-4, 1.43, 24*60, 3
ESP_CHOCH, ESP_FVG, ESP_MIT = 40, 20, 30
M1M = np.timedelta64(1, "m")
rng = np.random.default_rng(131)

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

# ---- niveles: semanal, diario, H4, H1
def piv(d, tf):
    h, l = d.h.to_numpy(), d.l.to_numpy(); t = d.ts.to_numpy("datetime64[ns]")
    o = []
    for i in range(PIV, len(d)-PIV):
        if h[i] == h[i-PIV:i+PIV+1].max(): o.append((t[i+PIV]+tf*M1M, h[i], -1))
        if l[i] == l[i-PIV:i+PIV+1].min(): o.append((t[i+PIV]+tf*M1M, l[i], +1))
    return o
def extremos(regla, dur):
    g = (m1.set_index("ts").resample(regla).agg(h=("high","max"), l=("low","min"),
                                                n=("close","size")).dropna())
    g = g[g.n > 200]; t = g.index.to_numpy("datetime64[ns]")
    o = []
    for i in range(len(g)-1):
        o.append((t[i+1], g.h.iloc[i], -1)); o.append((t[i+1], g.l.iloc[i], +1))
    return o
NIV = piv(velas(60), 60) + piv(velas(240), 240) + extremos("D", 1) + extremos("W", 1)
NIV.sort(key=lambda x: x[0])
nt = np.array([x[0] for x in NIV], dtype="datetime64[ns]")
npv = np.array([x[1] for x in NIV]); nls = np.array([x[2] for x in NIV], int)

def corre(tfe, mitiga, barajar=False):
    d = velas(tfe); ts = d.ts.to_numpy("datetime64[ns]")
    h, l, c = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy(); N = len(d)
    al = np.zeros(N, bool); ba = np.zeros(N, bool)
    al[2:] = l[2:] > h[:-2]; ba[2:] = h[2:] < l[:-2]
    loc = pd.DatetimeIndex(ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    hm = loc.hour.to_numpy() + loc.minute.to_numpy()/60
    vent = ((hm >= 9) & (hm < 11)) | ((hm >= 14) & (hm < 16.5))
    dia = pd.DatetimeIndex(ts).normalize().to_numpy()
    filas = []; usado = set()
    for k in range(5, N-1):
        if not vent[k]: continue
        j = int(np.searchsorted(nt, ts[k], "right"))
        for q in range(max(0, j-60), j):
            lado = nls[q]; niv = npv[q]
            if not ((h[k] > niv) if lado < 0 else (l[k] < niv)): continue
            clave = (dia[k], round(float(niv), 5))
            if clave in usado: continue
            ext = h[k] if lado < 0 else l[k]
            # --- cambio de estructura CON CUERPO a favor del giro
            kc = -1
            for z in range(k+1, min(k+ESP_CHOCH, N)):
                ext = max(ext, h[z]) if lado < 0 else min(ext, l[z])
                if lado < 0:
                    piso = l[k:z].min()
                    if c[z] < piso: kc = z; break
                else:
                    techo = h[k:z].max()
                    if c[z] > techo: kc = z; break
            if kc < 0: continue
            # --- desequilibrio despues del cambio
            kf = -1
            for z in range(kc, min(kc+ESP_FVG, N)):
                if (ba[z] if lado < 0 else al[z]): kf = z; break
            if kf < 0: continue
            borde = l[kf-2] if lado < 0 else h[kf-2]   # el borde del hueco
            if mitiga:
                ke = -1
                for z in range(kf+1, min(kf+ESP_MIT, N)):
                    ext = max(ext, h[z]) if lado < 0 else min(ext, l[z])
                    if (h[z] >= borde) if lado < 0 else (l[z] <= borde): ke = z; break
                if ke < 0: continue
                P = borde; t_ent = ts[ke] + tfe*M1M
            else:
                P = c[kf]; t_ent = ts[kf] + tfe*M1M
            S = ext
            rgo = abs(S-P)
            if rgo <= 0: continue
            L = lado if not barajar else (1 if rng.random() < .5 else -1)
            if L != lado: S = P + rgo if L < 0 else P - rgo
            O = P - 2*rgo if L < 0 else P + 2*rgo
            if L < 0 and not (S > P > O): continue
            if L > 0 and not (S < P < O): continue
            usado.add(clave)
            i0 = int(np.searchsorted(mts, t_ent, "left"))
            if i0 >= M-2: continue
            g = 0
            for x in range(i0, min(i0+HOR, M)):
                if L < 0:
                    if mh[x] >= S: break
                    if ml[x] <= O: g = 1; break
                else:
                    if ml[x] <= S: break
                    if mh[x] >= O: g = 1; break
            filas.append((rgo/U, g)); break
    if not filas: return None
    D = pd.DataFrame(filas, columns=["rgo","gana"])
    D["Rb"] = np.where(D.gana == 1, 2.0, -1.0); D["Rn"] = D.Rb - COSTE/D.rgo
    return D

def linea(nom, D):
    if D is None or len(D) < 30: return print(f"  {nom:<40} (pocas: {0 if D is None else len(D)})")
    cst = (COSTE/D.rgo).median(); umb = (1+cst)/3
    p = D.gana.mean(); ic = 1.96*sqrt(p*(1-p)/len(D))
    mn, icn = D.Rn.mean(), 1.96*D.Rn.std(ddof=1)/sqrt(len(D))
    print(f"  {nom:<40} n {len(D):5,} ({len(D)/anos:5.0f}/año)  acierto {100*p:5.1f} % "
          f"[{100*(p-ic):5.1f},{100*(p+ic):5.1f}]  riesgo {D.rgo.median():5.1f}p  "
          f"coste {100*cst:4.1f} %  UMBRAL {100*umb:5.1f} %  "
          f"{'PASA' if p-ic > umb else '  no'}  NETA {mn:+.4f} [{mn-icn:+.4f},{mn+icn:+.4f}]")

print(f"La regla de Benjamin COMPLETA · EURUSD {anos:.1f} años\n" + "="*163)
for tfe in (1, 2, 5):
    for mit, et in ((True, "entra al MITIGAR el hueco"), (False, "entra a mercado al cierre")):
        linea(f"M{tfe} · {et}", corre(tfe, mit))
print("="*163 + "\nnulo (lados barajados) sobre M2 al mitigar")
linea("  lados barajados", corre(2, True, barajar=True))
