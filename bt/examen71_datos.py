"""Los casos del examen 8: las señales de la estrategia del 71 % en M30.

De cada señal se guarda LO QUE SE VE en el momento en que dispara -las velas de
M30 hasta el cierre de la ruptura de estructura, ni una mas- y su desenlace,
que el no vera hasta despues de decidir.

  python3 bt/examen71_datos.py
"""
import json, os
import numpy as np, pandas as pd

TF, H4V, ENTR, VENT, VIDA, RETRO = 30, 20, 0.71, 8, 96, 60
VELAS_ANTES = 60          # cuantas velas de M30 se le enseñan antes del barrido
POR_INSTR   = 40          # se sortean estas de cada instrumento

INSTR = {
 "A": ("data/eurusd_m1.parquet", 1e-4, 1.43),
 "B": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
 "C": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
 "D": ("data/nsxusd_m1.parquet", 1e-0, 1.50),
 "E": ("data/spxusd_m1.parquet", 1e-0, 0.50),
 "F": ("data/grxeur_m1.parquet", 1e-0, 1.50),
}

def casos(clave, ruta, U, COSTE):
    d = pd.read_parquet(ruta)
    d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
    d = d.reset_index(drop=True)
    def agr(m):
        g = d.set_index("ts").resample(f"{m}min", label="left", closed="left").agg(
            o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna()
        return g[g.n >= max(1, m*0.4)].reset_index()
    E, H4 = agr(TF), agr(240)
    t, o, h, l, c = (E.ts.to_numpy(), E.o.to_numpy(), E.h.to_numpy(),
                     E.l.to_numpy(), E.c.to_numpy())
    n = len(E)
    fh = np.zeros(n, bool); fl = np.zeros(n, bool)
    for i in range(2, n-2):
        if h[i] > h[i-1] and h[i] > h[i-2] and h[i] > h[i+1] and h[i] > h[i+2]: fh[i] = True
        if l[i] < l[i-1] and l[i] < l[i-2] and l[i] < l[i+1] and l[i] < l[i+2]: fl[i] = True
    h4t = H4.ts.to_numpy()
    h4hi = pd.Series(H4.h).rolling(H4V).max().to_numpy()
    h4lo = pd.Series(H4.l).rolling(H4V).min().to_numpy()
    fuera = []
    for i in range(VELAS_ANTES + 5, n-1):
        for lado in (-1, +1):
            pj = [j for j in range(max(2,i-RETRO), i-1) if (fh[j] if lado<0 else fl[j]) and j+2 <= i]
            if not pj: continue
            jf = pj[-1]; niv = (h[jf] if lado < 0 else l[jf])
            if lado < 0 and not (h[i] > niv and c[i] < niv): continue
            if lado > 0 and not (l[i] < niv and c[i] > niv): continue
            k4 = int(np.searchsorted(h4t, t[i], side="right")) - 2
            if k4 < H4V: continue
            hi4, lo4 = h4hi[k4], h4lo[k4]
            if not np.isfinite(hi4) or hi4 <= lo4: continue
            pos = (c[i]-lo4)/(hi4-lo4)
            if lado < 0 and pos < 0.50: continue
            if lado > 0 and pos > 0.50: continue
            ext = h[i] if lado < 0 else l[i]
            bos = None
            for k in range(i+1, min(i+40, n)):
                fr = [j for j in range(max(2,k-RETRO), k-1) if (fl[j] if lado<0 else fh[j]) and j+2 <= k]
                if not fr: continue
                lim = (l[fr[-1]] if lado < 0 else h[fr[-1]])
                if (c[k] < lim) if lado < 0 else (c[k] > lim): bos = k; break
                if (h[k] > ext) if lado < 0 else (l[k] < ext): break
            if bos is None: continue
            fin = float(min(l[i:bos+1]) if lado < 0 else max(h[i:bos+1]))
            rng = abs(ext - fin)
            if rng <= 0: continue
            ent = fin + ENTR*rng if lado < 0 else fin - ENTR*rng
            stp, tp = float(ext), fin
            rgo = abs(ent-stp)
            if rgo <= 0: continue
            j2 = min(n, bos + 1 + int(VIDA*60/TF))
            lleno = None
            for k in range(bos+1, j2):
                if (h[k] >= stp) if lado < 0 else (l[k] <= stp): break
                if (l[k] <= tp) if lado < 0 else (h[k] >= tp): break
                if (h[k] >= ent) if lado < 0 else (l[k] <= ent): lleno = k; break
            if lleno is None: continue
            R = None
            for k in range(lleno+1, j2):
                if ((h[k] >= stp) if lado < 0 else (l[k] <= stp)): R = -1.0; break
                if ((l[k] <= tp)  if lado < 0 else (h[k] >= tp)):  R = abs(tp-ent)/rgo; break
            mot = "SL" if R == -1.0 else ("TP" if R is not None else "fuera")
            if R is None:
                sal = float(c[min(j2,n)-1])
                R = ((sal-ent) if lado > 0 else (ent-sal))/rgo
            a0 = max(0, i - VELAS_ANTES)
            P = lambda x: round(float(x), 6)
            velas = [[P(o[k]), P(h[k]), P(l[k]), P(c[k])] for k in range(a0, bos+1)]
            fuera.append(dict(k=clave, sw=i-a0, bos=bos-a0, lado=lado, v=velas,
                              niv=P(niv), ext=P(ext), fin=P(fin), ent=P(ent),
                              sl=P(stp), tp=P(tp), pos=round(float(pos),3),
                              hi4=P(hi4), lo4=P(lo4),
                              rgo=round(rgo/U,1), mot=mot, R=round(float(R),2),
                              neta=round(float(R - COSTE*U/rgo),3),
                              anio=int(pd.Timestamp(t[i]).year)))
    return fuera

todo = []
for cl, (ruta, U, C) in INSTR.items():
    cs = casos(cl, ruta, U, C)
    rng = np.random.default_rng(20260905 + ord(cl))
    if len(cs) > POR_INSTR:
        idx = sorted(rng.choice(len(cs), POR_INSTR, replace=False))
        cs = [cs[i] for i in idx]
    print(f"  {cl}: {len(cs)} casos")
    todo += cs
rng = np.random.default_rng(20260905)
orden = rng.permutation(len(todo))
todo = [todo[i] for i in orden]
for k, x in enumerate(todo, 1): x["n"] = k
json.dump(todo, open("data/examen71.json","w"), separators=(",",":"))
r = [x for x in todo if x["mot"] in ("TP","SL")]
print(f"\n{len(todo)} casos · acierto de la regla a ciegas "
      f"{100*np.mean([x['mot']=='TP' for x in r]):.1f} % sobre {len(r)} resueltas")
print(f"R bruta media {np.mean([x['R'] for x in todo]):+.3f} · "
      f"R NETA media {np.mean([x['neta'] for x in todo]):+.3f}")
print(f"tamaño: {round(os.path.getsize('data/examen71.json')/1024)} KB")
