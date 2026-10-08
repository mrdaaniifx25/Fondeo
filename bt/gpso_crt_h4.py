"""La regla CRT del live 159, sin probar hasta ahora.

Sus palabras:
  "la clave es que cuando al precio de 4 horas le falta el mismo tiempo para
   cerrar que a la vela de una hora, esa entrada tiene mucha mayor probabilidad"
  "no una manipulacion que me deje la entrada en una hora, sino que ademas
   tengo una manipulacion que me lo deja en la temporalidad de 4 horas"

  A · ALINEACION  la H1 del barrido es la ULTIMA hora de su vela de H4
  B · DOBLE       la vela de H4 tambien barre el nivel y cierra dentro

La rejilla de H4 depende del huso del grafico, asi que se prueban las dos que
usa la gente: la de UTC y la de Madrid.

  python3 bt/gpso_crt_h4.py
"""
import numpy as np, pandas as pd

TZ, F, COLCHON, MINLEG, VENT, VIDA, NDIAS = "Europe/Madrid", 0.790, 0.10, 1.0, 8, 24, 5
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
    def agr(m, ix="ts"):
        g = d.set_index(ix).resample(f"{m}min", label="left", closed="left").agg(
            o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna()
        return g[g.n >= max(1, m*0.4)].reset_index()
    H, M5 = agr(60), agr(5)
    H4u = agr(240, "ts")                      # rejilla de H4 en UTC
    H4m = agr(240, "loc")                     # rejilla de H4 en hora de Madrid
    porf = {}
    for x, g in d.groupby("dia", sort=True):
        ih, il = g.high.idxmax(), g.low.idxmin()
        porf[x] = [(float(g.high.max()), int(d.loc[ih,"loc"].hour)),
                   (float(g.low.min()),  int(d.loc[il,"loc"].hour))]
    dias = sorted(porf); niv = {}
    for k, x in enumerate(dias):
        if k < NDIAS: continue
        v = []
        for j in range(k-NDIAS, k): v += porf[dias[j]]
        niv[x] = v
    T1, O1, HI, LO = d.ts.to_numpy(), d.open.to_numpy(), d.high.to_numpy(), d.low.to_numpy()
    ht, hh, hl, hc = H.ts.to_numpy(), H.h.to_numpy(), H.l.to_numpy(), H.c.to_numpy()
    hdia = pd.DatetimeIndex(H.ts).date
    hutc = pd.DatetimeIndex(H.ts).hour
    hloc = pd.DatetimeIndex(H.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    hmad = hloc.hour
    mt, mh, ml = M5.ts.to_numpy(), M5.h.to_numpy(), M5.l.to_numpy()
    def busca4(Hx, col, t):
        k = int(np.searchsorted(Hx[col].to_numpy(), t, side="right")) - 1
        return None if k < 0 else (float(Hx.h.iloc[k]), float(Hx.l.iloc[k]),
                                   float(Hx.c.iloc[k]))
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
                # A · ¿es la ULTIMA hora de la vela de H4?
                aliU = (int(hutc[i]) % 4) == 3
                aliM = (int(hmad[i]) % 4) == 3
                # B · ¿la vela de H4 tambien barre y cierra dentro?
                v4 = busca4(H4u, "ts", ht[i])
                dob = False
                if v4:
                    h4, l4, c4 = v4
                    dob = ((h4 > L and c4 < L) if lado < 0 else (l4 < L and c4 > L))
                ext = hh[i] if lado < 0 else hl[i]
                rgoH = hh[i]-hl[i]
                if rgoH <= 0: continue
                a = int(np.searchsorted(mt, ht[i] + np.timedelta64(60,"m")))
                b = int(np.searchsorted(mt, ht[i] + np.timedelta64(60+VENT*60,"m")))
                if b <= a+1: continue
                run = ext; armado = False; ent = None
                for k in range(a, b):
                    if not armado: armado = abs(ext-run) >= MINLEG*rgoH
                    if armado:
                        lvl = run + (ext-run)*F
                        if (mh[k] >= lvl) if lado < 0 else (ml[k] <= lvl):
                            ent, tk = float(lvl), k; break
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
                                  hniv=hniv, aliU=aliU, aliM=aliM, dob=dob))
    return pd.DataFrame(filas)

D = pd.concat([corre(n).assign(i=n) for n in INSTR])
D.to_csv("data/gpso_crt_h4.csv", index=False)
def f(nom, g):
    if len(g) < 150: print(f"{nom:>40s}   pocas ({len(g)})"); return
    r = g[g.mot.isin(["TP","SL"])]
    z = g.R.mean()/(g.R.std(ddof=1)/np.sqrt(len(g)))
    pos = sum(g[g.i==i].R.mean() > 0 for i in sorted(D.i.unique()) if (g.i==i).sum()>60)
    tot = sum((g.i==i).sum() > 60 for i in sorted(D.i.unique()))
    print(f"{nom:>40s} {len(g):6d} {100*(r.mot=='TP').mean():7.1f} % "
          f"{g.R.mean():+9.3f} {z:+7.2f} {g.neta.mean():+9.3f}   {pos}/{tot}")
print(f"{'':>40s} {'n':>6s} {'acierto':>9s} {'R bruta':>9s} {'z':>7s} {'R neta':>9s}   pos")
print("-"*92)
f("TODO", D)
print()
f("A · última hora de la H4 (rejilla UTC)", D[D.aliU])
f("    NO última hora (UTC)", D[~D.aliU])
f("A · última hora de la H4 (rejilla Madrid)", D[D.aliM])
f("    NO última hora (Madrid)", D[~D.aliM])
print()
f("B · la H4 también barre y cierra dentro", D[D.dob])
f("    la H4 no lo hace", D[~D.dob])
print()
f("A + B juntos (su CRT completo)", D[D.aliU & D.dob])
print()
f("A + B + nivel de sesión (13-17 h)", D[D.aliU & D.dob & D.hniv.between(13,17)])
