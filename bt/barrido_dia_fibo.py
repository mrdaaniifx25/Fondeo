"""Su idea, la segunda:

  "marcar en H1 el alto y el bajo de los dias anteriores, esperar un liquidity
   sweep -que barra el alto y la vela cierre por debajo-, tirar el fibonacci en
   M5, esperar el retroceso a la zona de descuento y entrar hasta el proximo alto"

  NIVELES  altos y bajos de los NDIAS dias previos (mismo dia, no).
  SWEEP    una vela de H1 se sale del nivel y CIERRA de vuelta dentro.
             barre un ALTO -> corto     ·     barre un BAJO -> largo
           Un solo sweep por nivel y dia.
  PIERNA   se sigue en M5 desde el cierre del sweep. El extremo va corriendo.
           Se ARMA cuando la pierna llega a MINLEG veces el rango de la vela H1.
  FIBO     entrada limitada en el nivel F del retroceso de la pierna VIVA, o sea
           calculado con el extremo de ese momento. Es causal: nada del futuro.
  STOP     un COLCHON de la pierna pasado el extremo barrido.
  OBJETIVO "nivel"  = el nivel de dia previo mas cercano en la direccion del trade
           "1:2"    = ratio fijo, para poder comparar con todo lo demas.
  VIDA     VENTANA horas para que entre, VIDA horas para que resuelva.

Empate dentro del minuto = STOP. El coste se resta en R.

  python3 bt/barrido_dia_fibo.py [instrumento ...]
"""
import os, sys
import numpy as np, pandas as pd

FIBS    = [0.500, 0.618, 0.705, 0.790]
NDIAS   = 5      # cuantos dias previos se marcan
MINLEG  = 1.0    # la pierna tiene que valer esto por el rango de la vela de sweep
COLCHON = float(os.environ.get("COLCHON", 0.10))
VENTANA = 8      # horas para que entre la limitada, desde el cierre del sweep
VIDA    = int(os.environ.get("VIDA", 24))   # horas para que resuelva
TF      = int(os.environ.get("TF", 5))   # temporalidad donde se dibuja el fibo

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
    # velas de H1 y de M5, construidas desde M1
    def agr(minutos):
        g = d.set_index("ts").resample(f"{minutos}min", label="left", closed="left").agg(
            o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna()
        return g[g.n >= max(1, minutos*0.4)].reset_index()
    H, M5 = agr(60), agr(TF)
    dia = d.groupby("dia").agg(hi=("high","max"), lo=("low","min"))
    dias = list(dia.index); pos = {x: k for k, x in enumerate(dias)}
    niv = {}                                   # dia -> niveles de los NDIAS previos
    for k, x in enumerate(dias):
        if k < NDIAS: continue
        v = []
        for j in range(k-NDIAS, k):
            v += [float(dia.hi.iloc[j]), float(dia.lo.iloc[j])]
        niv[x] = sorted(set(v))
    # arrays
    T1, O1, H1a, L1a = (d.ts.to_numpy(), d.open.to_numpy(),
                        d.high.to_numpy(), d.low.to_numpy())
    ht, ho, hh, hl, hc = (H.ts.to_numpy(), H.o.to_numpy(), H.h.to_numpy(),
                          H.l.to_numpy(), H.c.to_numpy())
    hdia = pd.DatetimeIndex(H.ts).date
    m5t, m5h, m5l = M5.ts.to_numpy(), M5.h.to_numpy(), M5.l.to_numpy()
    filas, visto = [], set()
    for i in range(len(H)):
        x = hdia[i]
        if x not in niv: continue
        for nivel in niv[x]:
            for lado in (-1, +1):
                if lado < 0 and not (hh[i] > nivel and hc[i] < nivel): continue
                if lado > 0 and not (hl[i] < nivel and hc[i] > nivel): continue
                clave = (x, round(nivel, 6), lado)
                if clave in visto: continue
                visto.add(clave)
                ext = hh[i] if lado < 0 else hl[i]        # el extremo barrido
                rgoH = hh[i] - hl[i]
                if rgoH <= 0: continue
                t0 = ht[i] + np.timedelta64(60, "m")      # el sweep ya ha cerrado
                a = int(np.searchsorted(m5t, t0))
                b = int(np.searchsorted(m5t, t0 + np.timedelta64(VENTANA, "h")))
                if b <= a: continue
                # ── se camina M5 hacia delante, con el extremo vivo ──────────
                run = ext
                for F in FIBS: pass
                for F in FIBS:
                    run = ext; armado = False; ent = None; tEnt = None
                    for k in range(a, b):
                        # el nivel se calcula con lo que YA se sabia antes de esta
                        # vela. Usar el minimo de la misma vela para el fibo y su
                        # maximo para disparar seria mirar dentro del minuto.
                        pierna = abs(ext - run)
                        if not armado: armado = pierna >= MINLEG*rgoH
                        if armado:
                            lvl = run + (ext-run)*F
                            toca = (m5h[k] >= lvl) if lado < 0 else (m5l[k] <= lvl)
                            if toca: ent, tEnt = float(lvl), m5t[k]; break
                        run = min(run, m5l[k]) if lado < 0 else max(run, m5h[k])
                    if ent is None: continue
                    stp = ext + (-lado)*COLCHON*abs(ext-run)
                    rgo = abs(ent - stp)
                    if rgo <= 0: continue
                    # objetivo "nivel": el mas cercano en la direccion del trade
                    cand = [v for v in niv[x] if (v < ent if lado < 0 else v > ent)]
                    obj_niv = (max(cand) if lado < 0 else min(cand)) if cand else None
                    # tEnt es la APERTURA de la vela de M5 en la que entra: el
                    # relleno cae en algun punto de esos cinco minutos y no se
                    # cual. Se resuelve desde que esa vela CIERRA, que es lo
                    # conservador; contar desde j+1 regalaria minutos que quiza
                    # son anteriores al relleno.
                    j = int(np.searchsorted(T1, tEnt + np.timedelta64(TF, "m")))
                    j2 = int(np.searchsorted(T1, tEnt + np.timedelta64(VIDA, "h")))
                    if j2 <= j+1: continue
                    hs, ls = H1a[j:j2], L1a[j:j2]
                    for et, tp in (("nivel", obj_niv), ("1:2", ent + lado*2*rgo)):
                        if tp is None: continue
                        if (lado < 0 and tp >= ent) or (lado > 0 and tp <= ent): continue
                        gs = (hs >= stp) if lado < 0 else (ls <= stp)
                        gt = (ls <= tp)  if lado < 0 else (hs >= tp)
                        isl = int(np.argmax(gs)) if gs.any() else 10**9
                        itp = int(np.argmax(gt)) if gt.any() else 10**9
                        if isl == 10**9 and itp == 10**9:
                            sal = float(O1[j2-1]); mot = "fuera"
                            R = ((sal-ent) if lado > 0 else (ent-sal))/rgo
                        else:
                            R, mot = (-1.0, "SL") if isl <= itp else \
                                     (abs(tp-ent)/rgo, "TP")
                        filas.append((F, et, mot, R, R - COSTE*U/rgo, rgo/U, lado,
                                      pd.Timestamp(tEnt).year))
    return pd.DataFrame(filas, columns=["F","obj","mot","R","neta","rgo","lado","anio"])

if __name__ == "__main__":
    nombres = sys.argv[1:] or ["EURUSD","GBPUSD","USDJPY"]
    print(f"fibo dibujado en M{TF}")
    print(f"{'instr':>7s} {'fibo':>6s} {'objetivo':>9s} {'n':>6s} {'acierto':>9s} "
          f"{'R bruta':>9s} {'R NETA':>9s} {'stop':>8s} {'z':>8s}")
    print("-"*80)
    todo = []
    for nom in nombres:
        df = corre(nom)
        df.to_csv(f"data/bdf_ops_{nom}_tf{TF}_c{COLCHON}.csv", index=False)
        if not len(df): print(f"{nom:>7s}  sin operaciones"); continue
        for (F, ob), g in df.groupby(["F","obj"]):
            r = g[g.mot.isin(["TP","SL"])]
            ac = 100*(r.mot == "TP").mean() if len(r) else np.nan
            z = g.neta.mean()/(g.neta.std(ddof=1)/np.sqrt(len(g))) if len(g) > 1 else 0
            print(f"{nom:>7s} {F:6.3f} {ob:>9s} {len(g):6d} {ac:8.1f} % "
                  f"{g.R.mean():+9.3f} {g.neta.mean():+9.3f} {g.rgo.median():7.1f} {z:+8.2f}")
            todo.append(dict(instr=nom, F=F, obj=ob, n=len(g), ac=ac, R=g.R.mean(),
                             neta=g.neta.mean(), z=z, stop=g.rgo.median()))
        print("-"*80)
    t = pd.DataFrame(todo)
    if len(t):
        t.to_csv(f"data/barrido_dia_fibo_tf{TF}.csv", index=False)
        print("\nRESUMEN por celda, sobre los instrumentos")
        for (F, ob), g in t.groupby(["F","obj"]):
            print(f"  fibo {F:.3f} obj {ob:>6s}: R neta positiva en {(g.neta>0).sum()} de {len(g)}"
                  f"  ·  bruta media {g.R.mean():+.3f}  ·  neta media {g.neta.mean():+.3f}"
                  f"  ·  acierto {g.ac.mean():.1f} %")
