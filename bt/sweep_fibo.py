"""Su idea, tal cual la dijo:

  "si en H1 hay liquidity sweep de la vela que crea el rango, medir con el fibo
   el retroceso y hacer la entrada hasta el otro extremo"

  RANGO   una vela de H1 cualquiera, i. Su alto y su bajo son el rango.
  SWEEP   la vela i+1 se sale del rango y CIERRA dentro otra vez:
            barre el alto  -> setup bajista     barre el bajo -> setup alcista
  FIBO    la pierna va del extremo barrido al otro extremo de la vela de sweep.
          Se espera el retroceso hasta el nivel F de esa pierna.
  ENTRADA limitada en ese nivel, dentro de las siguientes ESPERA horas.
  STOP    pasado el extremo barrido (mas un colchon).
  OBJETIVO  el otro extremo del rango  -> variante "extremo"
            o un 1:2 fijo               -> variante "1:2", para comparar

Se resuelve con M1 real, minuto a minuto, y el empate dentro del minuto cuenta
como STOP. El coste se resta al final en R.

  python3 bt/sweep_fibo.py [instrumento ...]
"""
import sys
import numpy as np, pandas as pd

FIBS   = [0.5, 0.618, 0.705, 0.79]
ESPERA = 4          # horas para que entre la limitada
VIDA   = 24         # horas para que se resuelva
COLCHON = 0.10      # el stop se pone un 10 % de la pierna pasado el extremo

INSTR = {
    "EURUSD": (["data/eurusd_m1.parquet", "data/eurusd_m1_2026_08.parquet"], 1e-4, 1.43),
    "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
    "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
    "XAUUSD": (["data/xauusd_m1.parquet", "data/xauusd_m1_2026.parquet"], 1e-2, 20.0),
    "NSXUSD": (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
    "SPXUSD": (["data/spxusd_m1.parquet"], 1e-0, 0.50),
    "GRXEUR": (["data/grxeur_m1.parquet", "data/grxeur_m1_2026.parquet"], 1e-0, 1.50),
}

def carga(rutas):
    d = pd.concat([pd.read_parquet(r) for r in rutas], ignore_index=True)
    d["ts"] = pd.to_datetime(d["ts"])
    return d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)

def h1(d):
    g = d.set_index("ts").resample("1h", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return g[g.n >= 30].reset_index()

def corre(nom):
    rutas, U, COSTE = INSTR[nom]
    d = carga(rutas)
    H = h1(d)
    # M1 en arrays, con un indice por marca de tiempo para saltar rapido
    T  = d.ts.to_numpy(); O = d.open.to_numpy()
    HI = d.high.to_numpy(); LO = d.low.to_numpy()
    ho, hh, hl, hc, ht = (H.o.to_numpy(), H.h.to_numpy(), H.l.to_numpy(),
                          H.c.to_numpy(), H.ts.to_numpy())
    filas = []
    for i in range(len(H)-2):
        # el sweep tiene que ser la vela siguiente y contigua en el tiempo
        if (ht[i+1] - ht[i]) != np.timedelta64(1, "h"): continue
        rgoA, rgoB = hl[i], hh[i]
        if rgoB <= rgoA: continue
        for lado, barre, cierra_dentro in ((-1, hh[i+1] > hh[i], hc[i+1] < hh[i]),
                                           (+1, hl[i+1] < hl[i], hc[i+1] > hl[i])):
            if not (barre and cierra_dentro): continue
            ext  = hh[i+1] if lado < 0 else hl[i+1]      # el extremo barrido
            otro = hl[i+1] if lado < 0 else hh[i+1]      # el otro lado del sweep
            pierna = abs(ext - otro)
            if pierna <= 0: continue
            stp = ext + (-lado)*COLCHON*pierna           # pasado el extremo
            obj_ext = rgoA if lado < 0 else rgoB         # el otro extremo del RANGO
            k0 = int(np.searchsorted(T, ht[i+2]))
            k1 = int(np.searchsorted(T, ht[i+2] + np.timedelta64(ESPERA, "h")))
            k2 = int(np.searchsorted(T, ht[i+2] + np.timedelta64(ESPERA+VIDA, "h")))
            if k1 <= k0 or k2 <= k1: continue
            for F in FIBS:
                ent = otro + lado*(-1)*0  # se calcula abajo, segun el lado
                ent = otro + (ext-otro)*F if lado < 0 else otro + (ext-otro)*F
                rgo = abs(ent - stp)
                if rgo <= 0: continue
                # 1 · ¿entra la limitada en las ESPERA horas?
                toca = (HI[k0:k1] >= ent) if lado < 0 else (LO[k0:k1] <= ent)
                if not toca.any(): continue
                j = k0 + int(np.argmax(toca))
                # 2 · ¿resuelve antes de que se acabe la vida?
                for etiqueta, tp in (("extremo", obj_ext), ("1:2", ent + lado*2*rgo)):
                    if (lado < 0 and tp >= ent) or (lado > 0 and tp <= ent): continue
                    hs, ls = HI[j+1:k2], LO[j+1:k2]
                    if not len(hs): continue
                    gs = (hs >= stp) if lado < 0 else (ls <= stp)
                    gt = (ls <= tp)  if lado < 0 else (hs >= tp)
                    isl = int(np.argmax(gs)) if gs.any() else 10**9
                    itp = int(np.argmax(gt)) if gt.any() else 10**9
                    if isl == 10**9 and itp == 10**9:
                        sal = float(O[k2-1]) if k2-1 < len(O) else ent
                        R = ((sal-ent) if lado > 0 else (ent-sal))/rgo; mot = "fuera"
                    else:                       # empate en el minuto: STOP
                        R, mot = (-1.0, "SL") if isl <= itp else \
                                 (abs(tp-ent)/rgo, "TP")
                    filas.append((F, etiqueta, mot, R, R - COSTE*U/rgo, rgo/U))
    return pd.DataFrame(filas, columns=["F","obj","mot","R","neta","rgo"]), COSTE

if __name__ == "__main__":
    nombres = sys.argv[1:] or list(INSTR)
    print(f"{'instr':>7s} {'fibo':>6s} {'objetivo':>9s} {'n':>7s} {'acierto':>9s} "
          f"{'R bruta':>9s} {'R NETA':>9s} {'stop':>8s} {'z neta':>8s}")
    print("-"*80)
    todo = []
    for nom in nombres:
        try: df, C = corre(nom)
        except Exception as e: print(f"{nom:>7s}  ERROR {e}"); continue
        for (F, ob), g in df.groupby(["F","obj"]):
            r = g[g.mot.isin(["TP","SL"])]
            ac = 100*(r.mot == "TP").mean() if len(r) else np.nan
            zz = g.neta.mean()/(g.neta.std(ddof=1)/np.sqrt(len(g))) if len(g) > 1 else 0
            print(f"{nom:>7s} {F:6.3f} {ob:>9s} {len(g):7d} {ac:8.1f} % "
                  f"{g.R.mean():+9.3f} {g.neta.mean():+9.3f} {g.rgo.median():7.1f} {zz:+8.2f}")
            todo.append(dict(instr=nom, F=F, obj=ob, n=len(g), ac=ac,
                             R=g.R.mean(), neta=g.neta.mean(), z=zz))
        print("-"*80)
    t = pd.DataFrame(todo)
    if len(t):
        t.to_csv("data/sweep_fibo.csv", index=False)
        print("\nRESUMEN · signo de la R neta por celda, sobre los instrumentos")
        for (F, ob), g in t.groupby(["F","obj"]):
            pos = (g.neta > 0).sum()
            print(f"  fibo {F:.3f} objetivo {ob:>7s}:  positiva en {pos} de {len(g)}"
                  f"   ·  media {g.neta.mean():+.3f}  ·  acierto medio {g.ac.mean():.1f} %")
