"""Estabilidad por anio de la celda recomendada, y P(pasar) usando SOLO los
anios recientes. Si el resultado vive en 2020-2021, esta muerto."""
import numpy as np, pandas as pd, importlib.util
spec = importlib.util.spec_from_file_location("aw", "bt/alto_winrate.py")

import os
os.environ.setdefault("SIMS","20000")
exec(open("bt/alto_winrate.py").read().split("# ---------------------------------------------------------------- pase")[0])

CEL = [("NASDAQ", "A", 0.50, 1, 1, 5), ("NASDAQ", "A", 0.50, 1, 3, 9),
       ("NASDAQ", "A", 0.50, 1,10, 9), ("SP500",  "A", 0.50, 1, 1, 3)]

for nom, ent_nom, f, a, b, ctr in CEL:
    ruta, DPP, CPTS = INSTR[nom]
    S = sesiones(ruta)
    rango = float(np.median([hh.max()-ll.min() for _,_,_,hh,ll,_ in S]))
    sl = f*rango; tp = sl*a/b; coste = CPTS
    print(f"\n{nom} · compra 09:35 NY · stop {sl:.1f} · TP {tp:.1f} (1:{b//a}) "
          f"· x{ctr} micros · riesgo {sl*ctr*DPP:.0f} $")
    reg = []
    for dia, mm, oo, hh, ll, cc in S:
        k5 = int(np.searchsorted(mm, 9*60+35))
        if k5 >= len(mm)-10: continue
        r, g = resuelve(hh, ll, cc, k5, float(oo[k5]), tp, sl, +1)
        reg.append((dia.year, r, g-coste))
    T = pd.DataFrame(reg, columns=["anio","r","pnl"])
    print(f"   {'anio':>6} {'n':>5} {'acierto':>9} {'R neto':>9} {'$ / op':>9}")
    for y, g in T.groupby("anio"):
        print(f"   {y:>6} {len(g):>5} {np.mean(g.pnl>0)*100:8.1f}% "
              f"{np.mean(g.pnl)/sl:+9.3f} {np.mean(g.pnl)*ctr*DPP:+9.2f}")
    print(f"   {'TOTAL':>6} {len(T):>5} {np.mean(T.pnl>0)*100:8.1f}% "
          f"{np.mean(T.pnl)/sl:+9.3f} {np.mean(T.pnl)*ctr*DPP:+9.2f}")
    for desde, et in ((2020,"todo 2020-2026"), (2024,"solo 2024-2026")):
        u = T[T.anio>=desde].pnl.to_numpy()*ctr*DPP
        pe,_ = evalua(u,"estatico"); pd_,_ = evalua(u,"dinamico")
        print(f"   {et:16s} n={len(u):5d}  neto {u.mean():+7.2f}$/op  "
              f"P(pasar) estatico {pe*100:5.1f} %  dinamico {pd_*100:5.1f} %")
