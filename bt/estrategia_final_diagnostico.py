"""Diagnostico de bt/estrategia_final.py: ano a ano y saturacion del universo.

  python3 bt/estrategia_final_diagnostico.py
"""
import numpy as np, pandas as pd
from math import sqrt
src=open("bt/estrategia_final.py").read().split('CAB = f"')[0]
exec(compile(src,"ef","exec"))
mo = serie(mezcla(OPER), OPER); mc = serie(mezcla(list(P.columns)), list(P.columns))
print("efecto anual (suma de meses), universo operable y completo\n")
a1=mo.groupby(mo.index.year).sum(); a2=mc.groupby(mc.index.year).sum()
for y in range(2010,2027):
    if y in a1.index:
        print(f"  {y}   operable {a1[y]:>+7.2f}     completo {a2.get(y,float('nan')):>+7.2f}")
import sys

print("\n=== cuantos instrumentos hacen falta? (2013-2026, universo completo) ===")
todo=list(P.columns)
for n in (5,10,14,20,25):
    rng2=np.random.default_rng(7); sh=[]
    for _ in range(30):
        cols=list(rng2.choice(todo,size=n,replace=False))
        m=serie(mezcla(cols),cols); m=m[m.index.year>=2013]
        if len(m)>=24 and m.std(ddof=1)>0: sh.append(m.mean()/m.std(ddof=1)*sqrt(12))
    print(f"  {n:>2} instrumentos: Sharpe mediano {np.median(sh):>+5.2f}   [{np.percentile(sh,10):+.2f},{np.percentile(sh,90):+.2f}]")

print("\n=== y en la muestra COMPLETA (1971-2026), mismo test ===")
for n in (5,10,14,20,25):
    rng2=np.random.default_rng(7); sh=[]
    for _ in range(30):
        cols=list(rng2.choice(todo,size=n,replace=False))
        m=serie(mezcla(cols),cols)
        if len(m)>=24 and m.std(ddof=1)>0: sh.append(m.mean()/m.std(ddof=1)*sqrt(12))
    print(f"  {n:>2} instrumentos: Sharpe mediano {np.median(sh):>+5.2f}   [{np.percentile(sh,10):+.2f},{np.percentile(sh,90):+.2f}]")
