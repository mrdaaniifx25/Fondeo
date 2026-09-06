"""Los filtros que se le ven usar EN DIRECTO, sobre la version que paso el
preregistro (barrido de nivel diario + retroceso al fibo + stop al extremo).

Del directo 160, sus palabras:
  A  HORA DEL NIVEL  "si esta a las 6 de la mañana ese maximo no me sirve,
                      si esta a las 7 si me sirve"  -> el nivel se filtra por
                      la hora a la que se formo
  C  CERCANIA        "si esto empieza a tener un impulso alcista que sea muy
                      fuerte no me sirve de nada, necesito que el precio se
                      quede cercano a esta zona"    -> pierna maxima
  D  HORA DE OPERAR  el opera a las 14:30-15:30 de Madrid

  python3 bt/gpso_filtros.py
"""
import os, sys
import numpy as np, pandas as pd

TZ, F, COLCHON, MINLEG, VENT, VIDA = "Europe/Madrid", 0.790, 0.10, 1.0, 8, 24
NDIAS = 5
INSTR = {
 "EURUSD": (["data/eurusd_m1.parquet"], 1e-4, 1.43),
 "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
 "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
 "NSXUSD": (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
}

def corre(nom):
    rutas, U, COSTE = INSTR[nom]
    d = pd.concat([pd.read_parquet(r) for r in rutas], ignore_index=True)
    d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
    d = d.reset_index(drop=True)
    loc = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    d["loc"] = loc; d["dia"] = loc.date
    def agr(m, col="ts"):
        g = d.set_index("ts").resample(f"{m}min", label="left", closed="left").agg(
            o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna()
        return g[g.n >= max(1, m*0.4)].reset_index()
    H, M5 = agr(60), agr(5)
    # niveles CON la hora a la que se formaron
    filas_niv = {}
    for x, g in d.groupby("dia", sort=True):
        ih, il = g.high.idxmax(), g.low.idxmin()
        filas_niv[x] = [(float(g.high.max()), int(d.loc[ih,"loc"].hour)),
                        (float(g.low.min()),  int(d.loc[il,"loc"].hour))]
    dias = sorted(filas_niv)
    niv = {}
    for k, x in enumerate(dias):
        if k < NDIAS: continue
        v = []
        for j in range(k-NDIAS, k): v += filas_niv[dias[j]]
        niv[x] = v
    T1, O1, HI, LO = d.ts.to_numpy(), d.open.to_numpy(), d.high.to_numpy(), d.low.to_numpy()
    ht, hh, hl, hc = H.ts.to_numpy(), H.h.to_numpy(), H.l.to_numpy(), H.c.to_numpy()
    hdia = pd.DatetimeIndex(H.ts).date
    hloc = pd.DatetimeIndex(H.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    hhora = hloc.hour
    mt, mh, ml = M5.ts.to_numpy(), M5.h.to_numpy(), M5.l.to_numpy()
    filas, visto = [], set()
    for i in range(len(H)):
        x = hdia[i]
        if x not in niv: continue
        for L, hniv in niv[x]:
            for lado in (-1, +1):
                if lado < 0 and not (hh[i] > L and hc[i] < L): continue
                if lado > 0 and not (hl[i] < L and hc[i] > L): continue
                cl = (x, round(L,6), lado)
                if cl in visto: continue
                visto.add(cl)
                ext = hh[i] if lado < 0 else hl[i]
                rgoH = hh[i]-hl[i]
                if rgoH <= 0: continue
                a = int(np.searchsorted(mt, ht[i] + np.timedelta64(60,"m")))
                b = int(np.searchsorted(mt, ht[i] + np.timedelta64(60+VENT*60,"m")))
                if b <= a+1: continue
                run = ext; armado = False; ent = None
                for k in range(a, b):
                    pierna = abs(ext-run)
                    if not armado: armado = pierna >= MINLEG*rgoH
                    if armado:
                        lvl = run + (ext-run)*F
                        if (mh[k] >= lvl) if lado < 0 else (ml[k] <= lvl):
                            ent, tk, pierna_f = float(lvl), k, pierna; break
                    run = min(run, ml[k]) if lado < 0 else max(run, mh[k])
                if ent is None: continue
                stp = ext + (-lado)*COLCHON*abs(ext-run)
                rgo = abs(ent-stp)
                if rgo <= 0: continue
                tp = ent + lado*2*rgo
                j  = int(np.searchsorted(T1, mt[tk] + np.timedelta64(5,"m")))
                j2 = int(np.searchsorted(T1, mt[tk] + np.timedelta64(VIDA,"h")))
                if j2 <= j+1: continue
                hs, ls = HI[j:j2], LO[j:j2]
                gs = (hs >= stp) if lado < 0 else (ls <= stp)
                gt = (ls <= tp)  if lado < 0 else (hs >= tp)
                isl = int(np.argmax(gs)) if gs.any() else 10**9
                itp = int(np.argmax(gt)) if gt.any() else 10**9
                if isl == 10**9 and itp == 10**9:
                    sal = float(O1[j2-1]); mot = "fuera"
                    R = ((sal-ent) if lado > 0 else (ent-sal))/rgo
                else:
                    R, mot = (-1.0,"SL") if isl <= itp else (2.0,"TP")
                filas.append(dict(R=R, neta=R-COSTE*U/rgo, mot=mot, rgo=rgo/U,
                                  hniv=hniv, hop=int(hhora[i]),
                                  ratio=pierna_f/rgoH))
    return pd.DataFrame(filas)

def linea(nom, g):
    if len(g) < 200: print(f"{nom:>34s}   pocas ({len(g)})"); return
    r = g[g.mot.isin(["TP","SL"])]
    z = g.R.mean()/(g.R.std(ddof=1)/np.sqrt(len(g)))
    print(f"{nom:>34s} {len(g):7d} {100*(r.mot=='TP').mean():7.1f} % "
          f"{g.R.mean():+9.3f} {z:+7.2f} {g.neta.mean():+9.3f}")

if __name__ == "__main__":
    D = pd.concat([corre(n).assign(i=n) for n in (sys.argv[1:] or list(INSTR))])
    print(f"{'filtro':>34s} {'n':>7s} {'acierto':>9s} {'R bruta':>9s} {'z':>7s} {'R neta':>9s}")
    print("-"*80)
    linea("SIN FILTROS (lo que ya pasó)", D)
    print()
    for lo, hi in ((7,17),(8,18),(9,18),(2,7)):
        linea(f"A · nivel formado entre {lo} y {hi} h", D[(D.hniv>=lo)&(D.hniv<hi)])
    print()
    for m in (1.5, 2.0, 3.0):
        linea(f"C · pierna < {m}× la vela de H1", D[D.ratio < m])
    print()
    for lo, hi in ((8,12),(14,17),(9,18),(15,17)):
        linea(f"D · opera entre {lo} y {hi} h Madrid", D[(D.hop>=lo)&(D.hop<hi)])
    print()
    m = (D.hniv>=7)&(D.hniv<17)&(D.ratio<2.0)&(D.hop>=8)&(D.hop<18)
    linea("A + C + D juntos", D[m])
    D.to_csv("data/gpso_filtros.csv", index=False)
