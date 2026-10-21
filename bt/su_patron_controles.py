"""Controles de bt/su_patron_londres.py: z de la bruta, diferencia contra el
control ciego con error agrupado, y el corte por direccion de la semana.

  python3 bt/su_patron_controles.py
"""
import numpy as np, pandas as pd
from math import sqrt
src = open("bt/su_patron_londres.py").read().split('print(f"{\'\':<34}')[0]
exec(compile(src,"s","exec"))
P = genera(8, 11, "barrido", "atr", 2.0)
C = genera(8, 11, "ciego",   "atr", 2.0)
Pm = genera(8, 11, "barrido", "mecha", 2.0)
print(f"{'':<30}{'n':>6}{'acierto':>9}{'geom':>7}{'exceso':>8}{'BRUTA':>9}{'z bru':>7}{'NETA':>9}{'z net':>7}")
for et, D in (("SU PATRON · stop ATR", P), ("SU PATRON · stop mecha", Pm),
              ("CONTROL ciego", C), ("  ciego solo cortos", C[C.lado<0]),
              ("  ciego solo largos", C[C.lado>0])):
    geo = (D.rgo/(D.rgo+D.rr*D.rgo)).mean()
    print(f"  {et:<28}{len(D):>6}{100*(D.R>0).mean():>8.1f}%{100*geo:>6.1f}%"
          f"{100*((D.R>0).mean()-geo):>+8.1f}{D.R.mean():>+9.4f}{z(D.R,D.dia.astype(str)):>+7.2f}"
          f"{D.n.mean():>+9.4f}{z(D.n,D.dia.astype(str)):>+7.2f}")

# diferencia patron vs ciego, con error agrupado por dia
a = P[["dia","R"]].assign(g=1); c = C[["dia","R"]].assign(g=0)
X = pd.concat([a,c]); d = P.R.mean()-C.R.mean()
va = P.R.var(ddof=1)/P.dia.nunique(); vc = C.R.var(ddof=1)/C.dia.nunique()
print(f"\n  DIFERENCIA bruta (patron - ciego): {d:+.4f}   z aprox {d/sqrt(va+vc):+.2f}")
pa, pc = (P.R>0).mean(), (C.R>0).mean()
se = sqrt(pa*(1-pa)/len(P) + pc*(1-pc)/len(C))
print(f"  DIFERENCIA de acierto: {100*(pa-pc):+.1f} pp   z {(pa-pc)/se:+.2f}")

print("\n  QUE PASA EN SEMANAS MUY DIRECCIONALES (como la suya, -120 pips)")
dia = M.groupby("dia").close.agg(["first","last"])
sem = dia.assign(s=pd.to_datetime(dia.index).to_period("W")).groupby("s").agg(
    a=("first","first"), b=("last","last"))
sem["mv"] = (sem.b/sem.a - 1)*10000
P2 = P.copy(); P2["sm"] = pd.to_datetime(P2.dia).dt.to_period("W")
P2["mv"] = P2["sm"].map(sem["mv"])
P2["afav"] = np.where(P2.lado<0, -P2.mv, P2.mv)
print(f"  {'tramo':<34}{'n':>6}{'acierto':>9}{'BRUTA':>9}{'NETA':>9}")
for et, m in (("semana >80 pips A FAVOR del lado", P2.afav>80),
              ("semana 0-80 a favor", (P2.afav>0)&(P2.afav<=80)),
              ("semana EN CONTRA del lado", P2.afav<=0)):
    D = P2[m]
    if len(D)<30: continue
    print(f"  {et:<34}{len(D):>6}{100*(D.R>0).mean():>8.1f}%{D.R.mean():>+9.4f}{D.n.mean():>+9.4f}")
