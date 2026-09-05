"""Las reglas NUEVAS del live 157, sobre la configuracion que paso el preregistro.

Sus palabras:
 F1 NIVEL CON ESPACIO   "para que un maximo o minimo sea valido debe tener un
                         impulso, ser representativo y tener espacio a la
                         izquierda"        -> extremo de swing, no cualquier alto
 F2 RETROCESO RAPIDO    "llevas casi 2 horas para este retroceso en 5 minutos,
                         feisimo"          -> el retroceso tiene que ser rapido
 F3 ZONA PROHIBIDA      "la zona prohibida va del punto alto del dia anterior al
                         minimo; el 50 % marca donde no puedo operar"

  python3 bt/gpso_filtros2.py
"""
import os, sys
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
    def agr(m):
        g = d.set_index("ts").resample(f"{m}min", label="left", closed="left").agg(
            o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna()
        return g[g.n >= max(1, m*0.4)].reset_index()
    H, M5 = agr(60), agr(5)
    ht, hh, hl, hc = H.ts.to_numpy(), H.h.to_numpy(), H.l.to_numpy(), H.c.to_numpy()
    hdia = pd.DatetimeIndex(H.ts).date
    hhora = pd.DatetimeIndex(H.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None).hour
    # niveles del dia con hora y "espacio a la izquierda" medido en velas de H1
    porf = {}
    for x, g in d.groupby("dia", sort=True):
        ih, il = g.high.idxmax(), g.low.idxmin()
        porf[x] = [(float(g.high.max()), int(d.loc[ih,"loc"].hour), +1),
                   (float(g.low.min()),  int(d.loc[il,"loc"].hour), -1)]
    dias = sorted(porf); rango = {x: (porf[x][0][0], porf[x][1][0]) for x in dias}
    niv = {}
    for k, x in enumerate(dias):
        if k < NDIAS: continue
        v = []
        for j in range(k-NDIAS, k): v += [(a,b,c,dias[j]) for a,b,c in porf[dias[j]]]
        niv[x] = v
    T1, O1, HI, LO = d.ts.to_numpy(), d.open.to_numpy(), d.high.to_numpy(), d.low.to_numpy()
    mt, mh, ml = M5.ts.to_numpy(), M5.h.to_numpy(), M5.l.to_numpy()
    filas, visto = [], set()
    for i in range(len(H)):
        x = hdia[i]
        if x not in niv: continue
        ayer = dias[dias.index(x)-1] if dias.index(x) > 0 else None
        for L, hniv, tipo, dniv in niv[x]:
            for lado in (-1, +1):
                if lado < 0 and not (hh[i] > L and hc[i] < L): continue
                if lado > 0 and not (hl[i] < L and hc[i] > L): continue
                cl = (x, round(L,6), lado)
                if cl in visto: continue
                visto.add(cl)
                # F1 · espacio a la izquierda: velas de H1 antes del nivel sin superarlo
                jn = int(np.searchsorted(ht, np.datetime64(pd.Timestamp(dniv))))
                k0 = max(0, i-200)
                izq = 0
                for q in range(i-1, k0, -1):
                    if (hh[q] >= L) if tipo > 0 else (hl[q] <= L): break
                    izq += 1
                # F3 · posicion dentro del rango de AYER
                if ayer is None: continue
                aHi, aLo = rango[ayer]
                if aHi <= aLo: continue
                pos = (hc[i]-aLo)/(aHi-aLo)
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
                velas = tk - a                      # F2 · cuanto tardo el retroceso
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
                                  hniv=hniv, izq=izq, velas=velas, pos=pos))
    return pd.DataFrame(filas)

def linea(nom, g):
    if len(g) < 250: print(f"{nom:>38s}   pocas ({len(g)})"); return
    r = g[g.mot.isin(["TP","SL"])]
    z = g.R.mean()/(g.R.std(ddof=1)/np.sqrt(len(g)))
    print(f"{nom:>38s} {len(g):7d} {100*(r.mot=='TP').mean():7.1f} % "
          f"{g.R.mean():+9.3f} {z:+7.2f} {g.neta.mean():+9.3f}")

if __name__ == "__main__":
    D = pd.concat([corre(n).assign(i=n) for n in (sys.argv[1:] or list(INSTR))])
    D.to_csv("data/gpso_filtros2.csv", index=False)
    print(f"{'filtro':>38s} {'n':>7s} {'acierto':>9s} {'R bruta':>9s} {'z':>7s} {'R neta':>9s}")
    print("-"*84)
    linea("base (nivel formado 7-17 h)", D[(D.hniv>=7)&(D.hniv<17)])
    B = D[(D.hniv>=7)&(D.hniv<17)]
    print()
    for m in (5, 10, 20, 40):
        linea(f"F1 · espacio a la izquierda ≥ {m} velas H1", B[B.izq >= m])
    print()
    for m in (6, 12, 24, 48):
        linea(f"F2 · retroceso en ≤ {m} velas de M5", B[B.velas <= m])
    print()
    for lo, hi in ((0.25,0.75),(0.30,0.70),(0.35,0.65)):
        linea(f"F3 · FUERA del {int(100*lo)}-{int(100*hi)} % de ayer",
              B[(B.pos<lo)|(B.pos>hi)])
        linea(f"     (dentro, la zona prohibida)", B[(B.pos>=lo)&(B.pos<=hi)])
    print()
    linea("F1≥10 + F2≤12 + F3 fuera del 30-70", 
          B[(B.izq>=10)&(B.velas<=12)&((B.pos<0.30)|(B.pos>0.70))])
