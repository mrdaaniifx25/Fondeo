"""¿Dónde está el máximo de  neta = ventaja x (1 + R:R) - coste/riesgo ?

El proyecto ha bajado el coste (stops anchos) pero nunca ha barrido el R:R,
que es el termino que MULTIPLICA. Se coge el CRT desnudo y se recorre el
objetivo como multiplo del riesgo.
"""
import sys; sys.path.insert(0, "bt")
import numpy as np, pandas as pd
from math import sqrt
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("EURUSD","data/eurusd_m1.parquet",1e-4,1.43),
       ("oro","data/xauusd_m1.parquet",0.01,35.0),
       ("DAX","data/grxeur_m1.parquet",1.0,1.6)]
TFS = [("H4",4), ("H12",12), ("D1",24)]
RRS = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]
HOR = 60*24*5

for tfn, tfh in TFS:
    print("\n" + "="*132); print(f"CRT en {tfn} · barrido del objetivo"); print("="*132)
    print(f"{'R:R':>5} {'n':>6} {'acierto':>9} {'azar':>7} {'exceso':>16} "
          f"{'coste':>7} {'ventaja x(1+RR)':>16} {'NETA':>20}")
    print("-"*132)
    datos = []
    for nom, ruta, U, co in INS:
        m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
        ref = velas_ref(m1, tfh, ancla_ny=1)
        if len(ref) < 60: continue
        h, l, c = (ref[x].to_numpy() for x in ("high","low","close"))
        a = C.atr(h, l, c, 20)
        seq = LM.secuencias(ref, usar_cuerpo=False)
        if seq.empty: continue
        seq = seq[seq.k == 1].copy()
        seq["rg"] = (seq.entrada - seq.stop).abs()
        seq = seq[seq.rg > 0]
        if len(seq) < 40: continue
        datos.append((seq, ref, m1, U, co))
    if not datos: continue
    for RR in RRS:
        G, CR = [], []
        for seq, ref, m1, U, co in datos:
            fin = ref["fin"].to_numpy()
            t1 = m1["ts"].to_numpy(); H = m1["high"].to_numpy(); L = m1["low"].to_numpy()
            for r in seq.itertuples():
                e, s, rg = r.entrada, r.stop, r.rg
                alc = r.alcista
                o = e + RR*rg if alc else e - RR*rg
                j0 = int(np.searchsorted(t1, fin[int(r.i_ent)], side="right"))
                j1 = min(j0+HOR, len(t1))
                if j0 >= len(t1): continue
                hh, ll = H[j0:j1], L[j0:j1]
                if alc: ga, gb = hh >= o, ll <= s
                else:   ga, gb = ll <= o, hh >= s
                ia = int(np.argmax(ga)) if ga.any() else 10**9
                ib = int(np.argmax(gb)) if gb.any() else 10**9
                if ia == 10**9 and ib == 10**9: G.append(0.0)
                else: G.append(1.0 if ia < ib else 0.0)
                CR.append(co/(rg/U))
        if len(G) < 60: continue
        G = np.array(G); CR = np.array(CR)
        azar = 1/(1+RR)
        ex = G.mean() - azar
        eic = 1.96*G.std(ddof=1)/sqrt(len(G))
        Rb = np.where(G == 1, RR, -1.0); Rn = Rb - CR
        mn = Rn.mean(); icn = 1.96*Rn.std(ddof=1)/sqrt(len(Rn))
        print(f"{RR:>5.1f} {len(G):>6,} {100*G.mean():>8.1f}% {100*azar:>6.1f}% "
              f"{100*ex:>+7.1f} [{100*(ex-eic):>+5.1f},{100*(ex+eic):>+5.1f}] "
              f"{100*np.median(CR):>6.1f}% {ex*(1+RR):>+16.4f} "
              f"{mn:>+9.4f} [{mn-icn:>+.4f},{mn+icn:>+.4f}]"
              f"{'  *' if mn-icn > 0 else ''}")
