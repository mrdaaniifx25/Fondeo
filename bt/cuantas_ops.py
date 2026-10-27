"""Cuantas operaciones da esto realmente, contadas sobre la senial historica."""
import numpy as np, pandas as pd
exec(open("bt/sistema.py").read().split('print("="*112); print("EL SISTEMA")')[0])

sm, sk = sig_mom(), sig_carry()
SEN = (0.5*sm.add(sk.reindex_like(sm).fillna(0), fill_value=0)).where(OKm)
SEN = SEN.where(SEN.abs() >= 0.25, 0.0)          # el filtro de |señal| >= 0,25
SEN = SEN[SEN.index.year >= 2000]                 # periodo con todas las divisas vivas

viva = SEN.notna() & (SEN != 0)
print(f"periodo: {SEN.index.min():%Y-%m} a {SEN.index.max():%Y-%m}  ({len(SEN)} meses)\n")
print(f"  posiciones abiertas a la vez, mediana ....... {viva.sum(axis=1).median():.0f}")
print(f"  posiciones abiertas a la vez, rango ......... "
      f"{viva.sum(axis=1).quantile(.1):.0f} a {viva.sum(axis=1).quantile(.9):.0f}")

ant = SEN.shift(1)
abre  = (viva & ~(ant.notna() & (ant != 0)))                       # entra de cero
cierra= (~viva & (ant.notna() & (ant != 0)))                       # sale a cero
gira  = (viva & (ant.notna() & (ant != 0)) & (np.sign(SEN) != np.sign(ant)))
ajusta= (viva & (ant.notna() & (ant != 0)) & (np.sign(SEN) == np.sign(ant))
         & (SEN != ant))

print(f"\n  AL MES, de media:")
print(f"    posiciones que abres de cero ............ {abre.sum(axis=1).mean():.1f}")
print(f"    posiciones que cierras del todo ......... {cierra.sum(axis=1).mean():.1f}")
print(f"    posiciones que giran (venta -> compra) .. {gira.sum(axis=1).mean():.1f}")
print(f"    posiciones que solo cambian de tamaño ... {ajusta.sum(axis=1).mean():.1f}")
print(f"    posiciones que no tocas ................. "
      f"{(viva & (SEN == ant)).sum(axis=1).mean():.1f}")
ordenes = (abre.sum(axis=1) + cierra.sum(axis=1) + 2*gira.sum(axis=1) + ajusta.sum(axis=1))
print(f"\n    ORDENES QUE MANDAS AL MES ............... {ordenes.mean():.1f}  "
      f"(mediana {ordenes.median():.0f}, rango {ordenes.quantile(.1):.0f}-{ordenes.quantile(.9):.0f})")
print(f"    ordenes al año .......................... {12*ordenes.mean():.0f}")

print(f"\n  CUANTO DURA CADA POSICION:")
dur = []
for c in SEN.columns:
    s = np.sign(SEN[c].fillna(0)).to_numpy(); n = 0
    for i in range(len(s)):
        if s[i] != 0 and (i == 0 or s[i] == s[i-1]): n += 1
        else:
            if n: dur.append(n)
            n = 1 if s[i] != 0 else 0
    if n: dur.append(n)
dur = np.array(dur)
print(f"    mediana .................. {np.median(dur):.0f} meses")
print(f"    la mitad duran entre ..... {np.percentile(dur,25):.0f} y {np.percentile(dur,75):.0f} meses")
print(f"    la mas larga ............. {dur.max():.0f} meses")
print(f"\n  Y en tres años de cuenta fondeada: unas {36*ordenes.mean():.0f} ordenes en total.")
