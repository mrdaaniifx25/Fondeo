"""La estrategia publica de GPSO Trader, reconstruida por el, tal cual.

  1  NIVELES   en H1: maximo y minimo del dia anterior, y de los dias previos
  2  CONTACTO  el precio tiene que llegar al nivel. Tocarlo no basta.
  3  CIERRE    se espera al cierre de la vela de H1 que reacciona al nivel
  4  DIRECCION cierre POR ENCIMA del nivel -> compra
               cierre POR DEBAJO del nivel -> venta
               (igual si el nivel es un maximo o un minimo)
  5  ENTRADA   al cierre de esa H1
  6  STOP      detras del pico de reaccion: el extremo de esa misma vela
  7  OBJETIVO  2R

No hay ni un parametro ajustado por mi. Un solo pase, se reporta lo que salga.

  python3 bt/gpso_t5p.py [instrumento ...]
"""
import os, sys
import numpy as np, pandas as pd

NDIAS = int(os.environ.get("NDIAS", 5))
VIDA  = int(os.environ.get("VIDA", 48))     # horas para resolver
COL   = float(os.environ.get("COL", 0.0))   # colchon extra del stop, en R de la vela

INSTR = {
 "EURUSD": (["data/eurusd_m1.parquet"], 1e-4, 1.43),
 "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
 "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
 "XAUUSD": (["data/xauusd_m1.parquet"], 1e-2, 20.0),
 "GRXEUR": (["data/grxeur_m1.parquet"], 1e-0, 1.50),
 "NSXUSD": (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
 "SPXUSD": (["data/spxusd_m1.parquet"], 1e-0, 0.50),
}

def corre(nom):
    rutas, U, COSTE = INSTR[nom]
    d = pd.concat([pd.read_parquet(r) for r in rutas], ignore_index=True)
    d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
    d = d.reset_index(drop=True)
    d["dia"] = pd.DatetimeIndex(d.ts).date
    g = d.set_index("ts").resample("1h", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    H = g[g.n >= 30].reset_index()
    dia = d.groupby("dia").agg(hi=("high","max"), lo=("low","min"))
    dias = list(dia.index)
    niv = {}
    for k, x in enumerate(dias):
        if k < NDIAS: continue
        v = []
        for j in range(k-NDIAS, k):
            v += [float(dia.hi.iloc[j]), float(dia.lo.iloc[j])]
        niv[x] = sorted(set(v))
    T1, O1, HI, LO = (d.ts.to_numpy(), d.open.to_numpy(),
                      d.high.to_numpy(), d.low.to_numpy())
    ht, hh, hl, hc = (H.ts.to_numpy(), H.h.to_numpy(), H.l.to_numpy(), H.c.to_numpy())
    hdia = pd.DatetimeIndex(H.ts).date
    filas, visto = [], set()
    for i in range(len(H)):
        x = hdia[i]
        if x not in niv: continue
        for L in niv[x]:
            if not (hl[i] <= L <= hh[i]): continue        # 2 · contacto
            if   hc[i] > L: lado = 1                       # 4 · direccion
            elif hc[i] < L: lado = -1
            else: continue
            clave = (x, round(L, 6), lado)
            if clave in visto: continue
            visto.add(clave)
            ent = float(hc[i])                             # 5 · entrada
            pico = hl[i] if lado > 0 else hh[i]            # 6 · stop
            stp = pico - lado*COL*(hh[i]-hl[i])
            rgo = abs(ent - stp)
            if rgo <= 0: continue
            tp = ent + lado*2*rgo                          # 7 · objetivo
            j  = int(np.searchsorted(T1, ht[i] + np.timedelta64(1, "h")))
            j2 = int(np.searchsorted(T1, ht[i] + np.timedelta64(1+VIDA, "h")))
            if j2 <= j+1: continue
            hs, ls = HI[j:j2], LO[j:j2]
            gs = (ls <= stp) if lado > 0 else (hs >= stp)
            gt = (hs >= tp)  if lado > 0 else (ls <= tp)
            isl = int(np.argmax(gs)) if gs.any() else 10**9
            itp = int(np.argmax(gt)) if gt.any() else 10**9
            if isl == 10**9 and itp == 10**9:
                sal = float(O1[j2-1]); mot = "fuera"
                R = ((sal-ent) if lado > 0 else (ent-sal))/rgo
            else:                                          # empate = STOP
                R, mot = (-1.0, "SL") if isl <= itp else (2.0, "TP")
            filas.append((mot, R, R - COSTE*U/rgo, rgo/U, lado,
                          pd.Timestamp(ht[i]).year, pd.Timestamp(ht[i]).hour))
    return pd.DataFrame(filas, columns=["mot","R","neta","rgo","lado","anio","hora"])

if __name__ == "__main__":
    print(f"NDIAS={NDIAS}  VIDA={VIDA}h  colchón={COL}\n")
    print(f"{'instr':>7s} {'n':>7s} {'acierto':>9s} {'R bruta':>9s} {'z bruta':>9s} "
          f"{'R NETA':>9s} {'z neta':>8s} {'stop':>9s} {'coste/R':>8s}")
    print("-"*88)
    todo = []
    for nom in (sys.argv[1:] or list(INSTR)):
        d = corre(nom)
        if not len(d): print(f"{nom:>7s}  sin operaciones"); continue
        d.to_csv(f"data/gpso_{nom}.csv", index=False)
        r = d[d.mot.isin(["TP","SL"])]
        ac = 100*(r.mot == "TP").mean()
        zb = d.R.mean()/(d.R.std(ddof=1)/np.sqrt(len(d)))
        zn = d.neta.mean()/(d.neta.std(ddof=1)/np.sqrt(len(d)))
        cr = 100*(INSTR[nom][2]*INSTR[nom][1])/(d.rgo.median()*INSTR[nom][1])
        print(f"{nom:>7s} {len(d):7d} {ac:8.1f} % {d.R.mean():+9.3f} {zb:+9.2f} "
              f"{d.neta.mean():+9.3f} {zn:+8.2f} {d.rgo.median():8.1f} {cr:7.1f} %")
        todo.append(dict(instr=nom, n=len(d), ac=ac, R=d.R.mean(), zb=zb,
                         neta=d.neta.mean(), zn=zn, stop=d.rgo.median()))
    t = pd.DataFrame(todo)
    if len(t):
        print("-"*88)
        print(f"  R bruta positiva en {(t.R>0).sum()} de {len(t)}  ·  media {t.R.mean():+.3f}")
        print(f"  R NETA  positiva en {(t.neta>0).sum()} de {len(t)}  ·  media {t.neta.mean():+.3f}")
        print(f"  acierto medio {t.ac.mean():.1f} %  contra el 33,3 % geométrico")
        t.to_csv("data/gpso_resumen.csv", index=False)
