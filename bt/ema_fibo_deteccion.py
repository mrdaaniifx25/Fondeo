"""Curva de deteccion: ¿que tamano de ventaja HABRIA visto esta rejilla?

Un cero solo significa algo si se sabe cuanto hace falta para que deje de
serlo. Se inyecta deriva a favor de las COMPRAS con una fraccion de dias del
75 %, asi que la deriva NETA es la mitad de la nominal, y se declara la neta.

  python3 bt/ema_fibo_deteccion.py
"""
import os, itertools, numpy as np, pandas as pd
exec(open("bt/ema_fibo_lado.py").read().split("print(\"\\n=== CONTROL")[0])

FRAC = 0.75
def inyecta(base, neto, frac=FRAC):
    """`neto` en pips/dia de deriva efectiva."""
    nom = neto/(2*frac-1)
    x = base.copy(); dia = x.ts.dt.date.to_numpy()
    ini = np.flatnonzero(np.r_[True, dia[1:] != dia[:-1]])
    favor = rng.random(len(ini)) < frac
    aj = np.zeros(len(x)); ac = 0.0
    for k, i in enumerate(ini):
        j = ini[k+1] if k+1 < len(ini) else len(x)
        paso = (nom*U)/(j-i) * (1 if favor[k] else -1)
        aj[i:j] = ac + np.cumsum(np.full(j-i, paso)); ac = aj[j-1]
    for c in ("open","high","low","close"): x[c] = x[c].to_numpy() + aj
    return x

print("=== CURVA DE DETECCION · solo el lado COMPRAS ===")
print(f"  {'neto':>6} {'precio final':>13} {'mejor z':>9} {'celdas z>2':>12} "
      f"{'R mejor':>9} {'R mediana':>10}")
for neto in (0.0, 0.5, 1.0, 2.0, 4.0, 8.0):
    x = d if neto == 0 else inyecta(d, neto)
    D = rejilla_l(x, f"n{neto}")
    C = D[D.lado == "compras"]
    b = C.sort_values("z").iloc[-1]
    print(f"  {neto:5.1f}p {x.close.iloc[-1]:13.4f} {C.z.max():+9.2f} "
          f"{int((C.z>2).sum()):8d}/{len(C):<3d} {b.R:+9.4f} {C.R.median():+10.4f}",
          flush=True)
print("\n  El suelo de deteccion es la primera fila con celdas z>2.")
print("  Por debajo de el, un cero de la rejilla no distingue 'no hay nada'")
print("  de 'hay algo mas pequeno que eso'.")
