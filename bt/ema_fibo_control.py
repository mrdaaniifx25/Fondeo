"""Control POSITIVO de la rejilla EMA+Fibo, despues de la correccion.

El nulo demuestra que el motor no FABRICA ventajas. Falta lo contrario:
que, corregido, tampoco las DESTRUYE. Se inyecta una deriva conocida en
EURUSD, a favor de las compras y solo en una fraccion de los dias, y se
comprueba que la rejilla la encuentra.

  python3 bt/ema_fibo_control.py
"""
import os, itertools, numpy as np, pandas as pd
exec(open("bt/ema_fibo.py").read().split("REAL = rejilla")[0])

def inyecta(base, pips, frac):
    """Deriva de `pips` al dia, a favor de compras en una fraccion `frac`."""
    x = base.copy()
    dia = x.ts.dt.date.to_numpy()
    ini = np.flatnonzero(np.r_[True, dia[1:] != dia[:-1]])
    favor = rng.random(len(ini)) < frac
    aj = np.zeros(len(x)); base_ac = 0.0
    for k, i in enumerate(ini):
        j = ini[k+1] if k+1 < len(ini) else len(x)
        paso = (pips*U)/(j-i) * (1 if favor[k] else -1)
        aj[i:j] = base_ac + np.cumsum(np.full(j-i, paso))
        base_ac = aj[j-1]
    for c in ("open","high","low","close"): x[c] = x[c].to_numpy() + aj
    return x

print("\n=== CONTROL POSITIVO · deriva inyectada, ¿la encuentra la rejilla? ===")
for pips, frac in ((0.0, 0.5), (1.0, 0.6), (3.0, 0.6), (8.0, 0.9)):
    D = rejilla(d if pips == 0 else inyecta(d, pips, frac), f"p{pips}")
    b = D.sort_values("z").iloc[-1]
    print(f"  deriva {pips:4.1f} pips en el {frac*100:3.0f} % de los dias  ->  "
          f"mejor z {D.z.max():+7.2f}   celdas z>2 {int((D.z>2).sum()):3d}/{len(D)}"
          f"   R {b.R:+.4f}   (tf {int(b.tf)} ema {int(b.ema)})", flush=True)
