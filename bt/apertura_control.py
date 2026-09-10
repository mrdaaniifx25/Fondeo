"""Control POSITIVO de la estrategia de la vela de apertura.

Los nulos demuestran que el motor no FABRICA ventaja. Falta lo contrario:
que no la DESTRUYE. Se inyecta una deriva conocida y se comprueba que la
rejilla la encuentra, y a partir de que tamano.

La deriva se declara en NETO: pips efectivos por dia, no nominales. El
control de EMA+Fibo fallo hoy por confundir las dos cosas.

  python3 bt/apertura_control.py
"""
import os, numpy as np, pandas as pd
os.environ.setdefault("NULOS","0")
exec(open("bt/apertura_eurusd.py").read().split("D = rejilla(M)")[0])
U = 1e-4
FRAC = 0.75

def inyecta(base, neto, frac=FRAC):
    """`neto` pips/dia de deriva efectiva a favor de las COMPRAS."""
    nom = neto/(2*frac-1)
    x = base.copy()
    dia = x["d"].to_numpy()
    ini = np.flatnonzero(np.r_[True, dia[1:] != dia[:-1]])
    favor = rng.random(len(ini)) < frac
    aj = np.zeros(len(x)); ac = 0.0
    for k, i in enumerate(ini):
        j = ini[k+1] if k+1 < len(ini) else len(x)
        paso = (nom*U)/(j-i) * (1 if favor[k] else -1)
        aj[i:j] = ac + np.cumsum(np.full(j-i, paso)); ac = aj[j-1]
    for c in ("open","high","low","close"): x[c] = x[c].to_numpy() + aj
    return x

print("=== CONTROL POSITIVO · ¿encuentra el motor una ventaja inyectada? ===")
print("   deriva NETA en pips/dia, a favor de las compras\n")
print(f"  {'neto':>7} {'precio final':>13} {'mejor z':>9} {'celdas z>2':>12} "
      f"{'celdas R>0':>12} {'R de la mejor':>14}")
for neto in (0.0, 1.0, 3.0, 8.0):
    x = M if neto == 0 else inyecta(M, neto)
    R = rejilla(x)
    if not len(R): print(f"  {neto:6.1f}p  sin operaciones"); continue
    b = R.sort_values("z").iloc[-1]
    print(f"  {neto:6.1f}p {x.close.iloc[-1]:13.4f} {R.z.max():+9.2f} "
          f"{int((R.z>2).sum()):8d}/{len(R):<3d} {int((R.R>0).sum()):8d}/{len(R):<3d} "
          f"{b.R:>+14.4f}", flush=True)
print(f"\n  Si la fila de 0,0 es la REAL y las de deriva la superan de forma")
print(f"  creciente, el motor esta calibrado en las dos direcciones.")
