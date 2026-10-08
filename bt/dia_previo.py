"""Pre-registro docs/PREREGISTRO_dia_previo.md

Maximo y minimo del dia natural anterior. Una vela de M5 (o M15) que los barre
y cierra de vuelta dentro dispara la operacion en contra del barrido.
Entrada al cierre de esa vela, stop en su extremo.
"""
import numpy as np, pandas as pd
from math import sqrt

HOR = 24*60
# el coste va en las mismas unidades que rgo/U: pips, centimos de oro, puntos
INS = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
       "oro":    ("data/xauusd_m1.parquet", 0.01, 35.0),
       "DAX":    ("data/grxeur_m1.parquet", 1.0,  1.6)}
rng = np.random.default_rng(89)
M1M = np.timedelta64(1, "m")

def velas(m1, mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(h=("high","max"), l=("low","min"), c=("close","last"),
                n=("close","size")).dropna())
    return g[g.n >= mins*0.3].reset_index()

def corre(ins, mins, objetivo, lados=None):
    ruta, U, coste = INS[ins]
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    mts = m1.ts.to_numpy("datetime64[ns]"); mh = m1.high.to_numpy()
    ml = m1.low.to_numpy(); M = len(m1)

    # niveles del dia natural anterior
    d = (m1.set_index("ts").resample("D").agg(h=("high","max"), l=("low","min"),
                                              n=("close","size")).dropna())
    d = d[d.n > 200]
    dh = d.h.shift(1); dl = d.l.shift(1)          # el dia ANTERIOR
    niv = pd.DataFrame({"ph": dh, "pl": dl}).dropna()

    V = velas(m1, mins)
    vt = V.ts.to_numpy("datetime64[ns]"); vh = V.h.to_numpy()
    vl = V.l.to_numpy(); vc = V.c.to_numpy()
    dia = pd.DatetimeIndex(vt).normalize()
    ph = niv.ph.reindex(dia).to_numpy(); pl = niv.pl.reindex(dia).to_numpy()

    filas = []; usado = set()
    for k in range(len(V)):
        if not np.isfinite(ph[k]) or not np.isfinite(pl[k]): continue
        dkey = dia[k]
        for lado, nivel, rompe, vuelve in (
                (-1, ph[k], vh[k] > ph[k], vc[k] < ph[k]),
                (+1, pl[k], vl[k] < pl[k], vc[k] > pl[k])):
            if not (rompe and vuelve): continue
            if (dkey, lado) in usado: continue
            usado.add((dkey, lado))
            P = vc[k]
            S = vh[k] if lado < 0 else vl[k]
            rgo = abs(S-P)
            if rgo <= 0: continue
            if objetivo == "opuesto": O = pl[k] if lado < 0 else ph[k]
            elif objetivo == "1:1":  O = P - rgo if lado < 0 else P + rgo
            else:                    O = P - 2*rgo if lado < 0 else P + 2*rgo
            L = lado if lados is None else lados[len(filas) % len(lados)]
            if L != lado:
                S, O = (P + rgo, P - abs(O-P)) if L < 0 else (P - rgo, P + abs(O-P))
            if L < 0 and not (S > P > O): continue
            if L > 0 and not (S < P < O): continue
            rec = abs(O-P)
            if rec <= 0: continue
            i = int(np.searchsorted(mts, vt[k] + mins*M1M, "left"))
            if i >= M - 2: continue
            g = 0
            for q in range(i, min(i+HOR, M)):
                if L < 0:
                    if mh[q] >= S: break
                    if ml[q] <= O: g = 1; break
                else:
                    if ml[q] <= S: break
                    if mh[q] >= O: g = 1; break
            filas.append((rgo/U, rec/rgo, g, rgo/(rgo+rec), pd.Timestamp(vt[k]).year))
    if not filas: return None
    D = pd.DataFrame(filas, columns=["rgo","rr","gana","azar","anio"])
    D["Rb"] = np.where(D.gana == 1, D.rr, -1.0)
    # rgo ya esta en las mismas unidades en que se declaro el coste
    D["Rn"] = D.Rb - coste/D.rgo
    return D

def linea(nom, D):
    if D is None or len(D) < 40: return print(f"  {nom:<34} (pocas)")
    ex = D.gana - D.azar; e, eic = 100*ex.mean(), 196*ex.std(ddof=1)/sqrt(len(D))
    m, ic = D.Rb.mean(), 1.96*D.Rb.std(ddof=1)/sqrt(len(D))
    mn, icn = D.Rn.mean(), 1.96*D.Rn.std(ddof=1)/sqrt(len(D))
    print(f"  {nom:<34} n {len(D):5,}  acierto {100*D.gana.mean():5.1f} % "
          f"(azar {100*D.azar.mean():4.1f})  exceso {e:+5.1f} [{e-eic:+5.1f},{e+eic:+5.1f}]"
          f"{'*' if (e-eic)*(e+eic)>0 else ' '}  R:R {D.rr.median():4.2f}  "
          f"riesgo {D.rgo.median():6.1f}  coste {100*((D.Rb-D.Rn).median()):4.1f} %  "
          f"BRUTA {m:+.4f} [{m-ic:+.4f},{m+ic:+.4f}]  NETA {mn:+.4f} [{mn-icn:+.4f},{mn+icn:+.4f}]")

for ins in INS:
    print("\n" + "="*178); print(ins); print("="*178)
    for mins, tf in ((5,"M5"), (15,"M15")):
        for objetivo in ("opuesto", "1:1", "1:2"):
            linea(f"{tf} · objetivo {objetivo}", corre(ins, mins, objetivo))
