"""Lectura descriptiva del reparto, no una hipotesis nueva.

H1a y H3a son complementarios exactos: uno exige que GBPUSD NO barriera, el otro
que SI. Juntos parten la muestra en dos. Comparar las dos mitades es una sola
estadistica descriptiva del mismo contraste ya ejecutado.
"""
import numpy as np, pandas as pd
from math import sqrt, erf
import sys; sys.path.insert(0,"bt")
exec(open("bt/confluencias.py").read().split("s_tr = sig")[0])

TRr=("2020-01-01","2023-12-31")
s_tr = sig[(sig.ts>=TRr[0])&(sig.ts<=TRr[1])].copy()
m3 = np.asarray(cond(s_tr,"H3a"), dtype=bool)
m1_ = np.asarray(cond(s_tr,"H1a"), dtype=bool)
print(f"reparto: GBPUSD tambien barrio -> {m3.sum()} | no barrio -> {m1_.sum()} "
      f"| total {len(s_tr)} (solapan {int((m3&m1_).sum())})")

a = simula(s_tr[m3]).bruto      # confluencia
b = simula(s_tr[m1_]).bruto     # divergencia SMT
def pz2(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
print(f"\n  GBPUSD barre TAMBIEN (confluencia) : n {len(a):>3} | bruto/op {a.mean():+.4f}")
print(f"  GBPUSD NO barre (divergencia SMT)  : n {len(b):>3} | bruto/op {b.mean():+.4f}")
dif = a.mean()-b.mean()
se = sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
z = dif/se; p = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
print(f"\n  diferencia (confluencia - divergencia) = {dif:+.4f} R/op")
print(f"  error estandar {se:.4f} | z {z:+.2f} | p {p:.3f}")
print(f"\n  Umbral de Bonferroni para 11 contrastes: p < {0.05/11:.4f}")
print(f"  -> {'SUPERA' if p < 0.05/11 else 'NO supera'}")
