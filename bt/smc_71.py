"""La estrategia de las cuatro casillas, tal cual la explica.

  1 SESGO H4      rango de las ultimas H4V velas de H4. Por encima del 50 % =
                  premium -> solo ventas. Por debajo = discount -> solo compras.
  2 BARRIDO       una vela de M15 pincha con la MECHA un fractal previo y CIERRA
                  de vuelta dentro. Barrido de altos -> ventas.
  3 BOS + FVG     despues del barrido, un CIERRE de cuerpo rompe un fractal del
                  lado contrario (break of structure), y dentro de esa pierna
                  hay un hueco de tres velas (fair value gap).
  4 FIBO 71 %     el fibo va del extremo barrido (100 %) al extremo del BOS (0 %).
                  ENTRADA limitada en el 71 %  ·  STOP en el 100 %  ·  TP en el 0 %
                  -> riesgo 29 %, beneficio 71 %, R:R = 2,45  (azar = 29,0 %)

  La orden vive hasta que se toca uno de los dos extremos del fibo.

  python3 bt/smc_71.py [instrumento ...]
"""
import os, sys
import numpy as np, pandas as pd

TF   = int(os.environ.get("TF", 15))     # temporalidad de ejecucion
H4V  = int(os.environ.get("H4V", 20))    # cuantas velas de H4 forman el rango
ENTR = float(os.environ.get("ENTR", 0.71))
VIDA = int(os.environ.get("VIDA", 96))   # horas de vida de la idea
EXIGE_FVG = os.environ.get("FVG", "si") == "si"
EXIGE_H4  = os.environ.get("H4", "si") == "si"
PESIMISTA = os.environ.get("PESIM", "no") == "si"
SUF       = os.environ.get("SUF", "")

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
    def agr(m):
        g = d.set_index("ts").resample(f"{m}min", label="left", closed="left").agg(
            o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna()
        return g[g.n >= max(1, m*0.4)].reset_index()
    E, H4 = agr(TF), agr(240)
    t, o, h, l, c = (E.ts.to_numpy(), E.o.to_numpy(), E.h.to_numpy(),
                     E.l.to_numpy(), E.c.to_numpy())
    n = len(E)
    # fractales de Williams, confirmados dos velas despues (causal)
    fh = np.zeros(n, bool); fl = np.zeros(n, bool)
    for i in range(2, n-2):
        if h[i] > h[i-1] and h[i] > h[i-2] and h[i] > h[i+1] and h[i] > h[i+2]: fh[i] = True
        if l[i] < l[i-1] and l[i] < l[i-2] and l[i] < l[i+1] and l[i] < l[i+2]: fl[i] = True
    # rango de H4 y posicion dentro de el, con velas de H4 ya CERRADAS
    h4t = H4.ts.to_numpy()
    h4hi = pd.Series(H4.h).rolling(H4V).max().to_numpy()
    h4lo = pd.Series(H4.l).rolling(H4V).min().to_numpy()
    filas = []
    for i in range(30, n-1):
        # los fractales usables son los confirmados: formados en j con j+2 <= i
        # 2 · barrido: mecha pasa un fractal alto previo y el cuerpo cierra dentro
        for lado in (-1, +1):
            if lado < 0:
                prev = [h[j] for j in range(max(2,i-60), i-1) if fh[j] and j+2 <= i]
                if not prev: continue
                niv = prev[-1]                       # el MAS RECIENTE, no el mas alto
                if not (h[i] > niv and c[i] < niv): continue
                ext = h[i]
            else:
                prev = [l[j] for j in range(max(2,i-60), i-1) if fl[j] and j+2 <= i]
                if not prev: continue
                niv = prev[-1]                       # el MAS RECIENTE
                if not (l[i] < niv and c[i] > niv): continue
                ext = l[i]
            # 1 · sesgo de H4 (premium -> ventas, discount -> compras)
            k4 = int(np.searchsorted(h4t, t[i], side="right")) - 2   # ya cerrada
            if k4 < H4V: continue
            hi4, lo4 = h4hi[k4], h4lo[k4]
            if not np.isfinite(hi4) or hi4 <= lo4: continue
            pos = (c[i]-lo4)/(hi4-lo4)
            if EXIGE_H4:
                if lado < 0 and pos < 0.50: continue      # ventas solo en premium
                if lado > 0 and pos > 0.50: continue      # compras solo en discount
            # 3 · break of structure con cierre de cuerpo + hueco de tres velas
            bos = None
            for k in range(i+1, min(i+40, n)):
                fr = [l[j] for j in range(max(2,k-60), k-1) if fl[j] and j+2 <= k] \
                     if lado < 0 else \
                     [h[j] for j in range(max(2,k-60), k-1) if fh[j] and j+2 <= k]
                if not fr: continue
                lim = fr[-1]                         # el mas reciente
                if (c[k] < lim) if lado < 0 else (c[k] > lim):
                    bos = k; break
                # se anula si el precio se pasa del extremo barrido antes del BOS
                if (h[k] > ext) if lado < 0 else (l[k] < ext): break
            if bos is None: continue
            # el extremo de la pierna del BOS
            fin = min(l[i:bos+1]) if lado < 0 else max(h[i:bos+1])
            rng = abs(ext - fin)
            if rng <= 0: continue
            # hueco de tres velas dentro de la pierna
            hay = False
            for k in range(i+1, bos):
                if k+1 >= n: break
                if (l[k-1] > h[k+1]) if lado < 0 else (h[k-1] < l[k+1]): hay = True; break
            if EXIGE_FVG and not hay: continue
            ent = fin + lado*(-1)*(ENTR*rng) if False else \
                  (fin + ENTR*rng if lado < 0 else fin - ENTR*rng)
            stp, tp = ext, fin
            rgo = abs(ent-stp)
            if rgo <= 0: continue
            # 4 · limitada viva hasta que se toque uno de los dos extremos
            j2 = min(n, bos + 1 + int(VIDA*60/TF))
            lleno = None
            for k in range(bos+1, j2):
                if (h[k] >= stp) if lado < 0 else (l[k] <= stp): break   # invalida
                if (l[k] <= tp) if lado < 0 else (h[k] >= tp): break     # se fue sin mi
                if (h[k] >= ent) if lado < 0 else (l[k] <= ent): lleno = k; break
            if lleno is None: continue
            R = None
            for k in range(lleno if PESIMISTA else lleno+1, j2):
                golpeS = (h[k] >= stp) if lado < 0 else (l[k] <= stp)
                golpeT = (l[k] <= tp)  if lado < 0 else (h[k] >= tp)
                if golpeS: R = -1.0; break            # empate en la vela = stop
                if golpeT: R = abs(tp-ent)/rgo; break
            if R is None:
                sal = c[min(j2,n)-1]
                R = ((sal-ent) if lado > 0 else (ent-sal))/rgo
            filas.append(dict(R=R, neta=R-COSTE*U/rgo, rgo=rgo/U, lado=lado,
                              gana=R > 0, fvg=hay, pos=pos,
                              anio=pd.Timestamp(t[i]).year))
    return pd.DataFrame(filas)

if __name__ == "__main__":
    print(f"TF=M{TF} · rango H4 de {H4V} velas · entrada al {ENTR:.0%} · "
          f"FVG={'sí' if EXIGE_FVG else 'no'} · filtro H4={'sí' if EXIGE_H4 else 'no'}")
    print(f"azar geométrico con R:R {ENTR/(1-ENTR):.2f} = {100*(1-ENTR):.1f} %\n")
    print(f"{'instr':>7s} {'n':>6s} {'acierto':>9s} {'R bruta':>9s} {'z':>7s} "
          f"{'R NETA':>9s} {'stop':>8s} {'coste/R':>8s}")
    print("-"*76)
    tot = []
    for nm in (sys.argv[1:] or list(INSTR)):
        g = corre(nm)
        if len(g) < 30: print(f"{nm:>7s}  {len(g)} operaciones"); continue
        g.to_csv(f"data/smc71{SUF}_{nm}.csv", index=False)
        z = g.R.mean()/(g.R.std(ddof=1)/np.sqrt(len(g)))
        cr = 100*INSTR[nm][2]/g.rgo.median()
        print(f"{nm:>7s} {len(g):6d} {100*g.gana.mean():8.1f} % {g.R.mean():+9.3f} "
              f"{z:+7.2f} {g.neta.mean():+9.3f} {g.rgo.median():7.1f} {cr:7.1f} %")
        tot.append(dict(i=nm, n=len(g), ac=100*g.gana.mean(), R=g.R.mean(),
                        neta=g.neta.mean()))
    t = pd.DataFrame(tot)
    if len(t):
        print("-"*76)
        print(f"  acierto medio {t.ac.mean():.1f} %  contra el azar de {100*(1-ENTR):.1f} %")
        print(f"  R bruta media {t.R.mean():+.3f}  ·  positiva en {(t.R>0).sum()}/{len(t)}")
        print(f"  R NETA  media {t.neta.mean():+.3f}  ·  positiva en {(t.neta>0).sum()}/{len(t)}")
