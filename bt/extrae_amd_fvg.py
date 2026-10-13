"""Saca ejemplos reales de AMD+FVG en EURUSD H1, con todo lo que hay que pintar.
Misma logica exacta que bt/amd_fvg.py, que es la que se midio."""
import json
import numpy as np, pandas as pd

U, LIMITE, NR, ESPM, ESPF, ESPD, COSTE = 1e-4, 0.90, 8, 20, 5, 20, 1.43
ANTES, DESPUES = 10, 4
SEMILLA = 20260919

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
V = (m1.set_index("ts").resample("60min", label="left", closed="left")
       .agg(o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna())
V = V[V.n >= 18].reset_index()

h, l, c, o = (V[x].to_numpy() for x in ("h","l","c","o")); N = len(V)
ts = V.ts.to_numpy()
pc = np.roll(c,1); pc[0] = c[0]
tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
a = np.full(N, np.nan); a[13] = np.nanmean(tr[:14])
for i in range(14, N): a[i] = (a[i-1]*13 + tr[i]) / 14
atr = np.roll(a, 1)
hi = pd.Series(h).rolling(NR).max().to_numpy()
lo = pd.Series(l).rolling(NR).min().to_numpy()
ratio = (hi-lo)/(atr*np.sqrt(NR))
fvgB = np.zeros(N, bool); fvgA = np.zeros(N, bool)
fvgB[2:] = h[2:] < l[:-2]
fvgA[2:] = l[2:] > h[:-2]

ops = []; i = NR
while i < N-1:
    if not np.isfinite(ratio[i]) or ratio[i] > LIMITE: i += 1; continue
    rHi, rLo = hi[i], lo[i]
    if rHi <= rLo: i += 1; continue
    manip = -1; lado = 0; ext = np.nan; j = i+1
    while j < min(i+1+ESPM, N):
        if h[j] > rHi or l[j] < rLo:
            arr = h[j] > rHi and rLo < c[j] < rHi
            aba = l[j] < rLo and rLo < c[j] < rHi
            if arr or aba: manip = j; lado = -1 if arr else 1; ext = h[j] if arr else l[j]
            break
        j += 1
    if manip < 0: i = max(j, i+1); continue
    kf = -1
    for k in range(manip, min(manip+1+ESPF, N)):
        ext = max(ext, h[k]) if lado < 0 else min(ext, l[k])
        if (fvgB[k] if lado < 0 else fvgA[k]): kf = k; break
    if kf < 0: i = manip+1; continue
    ent, stop = c[kf], ext
    obj = rLo if lado < 0 else rHi
    rgo, rec = abs(stop-ent), abs(obj-ent)
    if rgo <= 0 or rec <= 0: i = manip+1; continue
    # el objetivo tiene que estar POR DELANTE del precio de entrada: si ya esta
    # rebasado, esa operacion no existe. Ver docs/CORRECCION_objetivo_rebasado.md
    if (ent <= obj) if lado < 0 else (ent >= obj): i = manip+1; continue
    gana = 0; fin = min(kf+1+ESPD, N)-1
    for k in range(kf+1, min(kf+1+ESPD, N)):
        if lado < 0:
            if h[k] >= stop: fin = k; break
            if l[k] <= obj: gana = 1; fin = k; break
        else:
            if l[k] <= stop: fin = k; break
            if h[k] >= obj: gana = 1; fin = k; break
    ops.append(dict(i0=i-NR+1, i1=i, m=manip, f=kf, fin=fin, lado=lado,
        rHi=rHi, rLo=rLo, ent=ent, stop=stop, obj=obj, gana=gana,
        rgoP=rgo/U, rr=rec/rgo))
    i = manip+1

D = pd.DataFrame(ops)
print(f"operaciones: {len(D)}   acierto {100*D.gana.mean():.1f} %")
rng = np.random.default_rng(SEMILLA)
sel = []
for g in (1, 0):
    idx = D.index[D.gana == g].to_numpy()
    sel.extend(rng.choice(idx, size=12, replace=False))
casos = []
for z in sorted(sel):
    r = D.loc[z]
    j0, j1 = int(r.i0)-ANTES, int(r.fin)+DESPUES
    if j0 < 0 or j1 >= N: continue
    gl = l[int(r.f)] if r.lado > 0 else h[int(r.f)]
    gh = h[int(r.f)-2] if r.lado > 0 else l[int(r.f)-2]
    casos.append(dict(
        velas=[[round(float(o[k]),5), round(float(h[k]),5), round(float(l[k]),5),
                round(float(c[k]),5)] for k in range(j0, j1+1)],
        horas=[pd.Timestamp(ts[k]).strftime("%d/%m %H:%M") for k in range(j0, j1+1)],
        a0=int(r.i0)-j0, a1=int(r.i1)-j0, m=int(r.m)-j0, f=int(r.f)-j0,
        fin=int(r.fin)-j0, lado=int(r.lado),
        rHi=round(float(r.rHi),5), rLo=round(float(r.rLo),5),
        ent=round(float(r.ent),5), stop=round(float(r.stop),5),
        obj=round(float(r.obj),5), gana=int(r.gana),
        rgo=round(float(r.rgoP),1), rr=round(float(r.rr),2),
        coste=round(100*COSTE/float(r.rgoP),1),
        fecha=pd.Timestamp(ts[int(r.f)]).strftime("%Y-%m-%d %H:%M")))
rng.shuffle(casos)
for n, x in enumerate(casos): x["n"] = n+1
json.dump(casos, open("data/amd_fvg_casos.json","w"), separators=(",",":"))
print(f"ejemplos: {len(casos)}   {len(open('data/amd_fvg_casos.json').read())/1024:.0f} KB")
