"""Seguimiento de la UNICA celda positiva de bt/sistema_tres_instrumentos.py:
oro en la ventana de Nueva York. Particion temporal y anio a anio.

  python3 bt/sistema_oro_ny.py
"""
import numpy as np, pandas as pd
from math import sqrt
src = open("bt/sistema_tres_instrumentos.py").read().split("T = []")[0]
exec(compile(src, "s", "exec"))
D = corre("oro","data/xauusd_m1.parquet",1e-2,12.0,35.0,"NY","America/New_York",8,12)
D["n"] = D.R - D.cr
nd = D.dia.nunique()
print(f"LA UNICA CELDA POSITIVA  ·  oro · Nueva York 08-12")
print(f"  n {len(D)}  dias {nd}  ({len(D)/nd:.2f}/dia)  riesgo mediano {D.rgo.median():.0f} "
      f"(= {D.rgo.median()*1e-2:.2f} $)  coste {100*D.cr.mean():.1f} % del riesgo")
def f(et, S):
    if len(S) < 50: return print(f"  {et:<22} (pocas: {len(S)})")
    nn = S.R - S.cr
    print(f"  {et:<22}{len(S):>6}{100*(S.R>0).mean():>8.1f}%{pf(S.R):>7.2f}{pf(nn):>7.2f}"
          f"{nn.mean():>+9.4f}{z(nn,S.dia.astype(str)):>+7.2f}{S.Rbh.mean():>+9.4f}"
          f"{nn.mean()-S.Rbh.mean():>+9.4f}{100*nn.sum()/S.dia.nunique()*21:>+9.0f}")
print(f"\n  {'tramo':<22}{'n':>6}{'acierto':>9}{'PFbru':>7}{'PFnet':>7}{'R neta':>9}"
      f"{'z':>7}{'B&H':>9}{'exceso':>9}{'EUR/mes':>9}")
print("  " + "-"*94)
f("completa", D)
f("2023-2024", D[D.dia.dt.year <= 2024])
f("2025-2026", D[D.dia.dt.year >= 2025])
for y in sorted(D.dia.dt.year.unique()): f(str(y), D[D.dia.dt.year == y])
print(f"\n  placebos: invertida {(D.Rinv-D.cr).mean():+.4f}   siempre largo "
      f"{(D.Rlar-D.cr).mean():+.4f}   comprar y aguantar {D.Rbh.mean():+.4f}")
print(f"  % de operaciones en largo: {100*(D.lado>0).mean():.0f} %")
sd = (D.n.std(ddof=1))
print(f"\n  SUELO: con n={len(D)} y desv {sd:.2f}, para z=+2 haria falta R neta "
      f">= {2*sd/sqrt(len(D)):+.4f}. Observado {D.n.mean():+.4f}.")
