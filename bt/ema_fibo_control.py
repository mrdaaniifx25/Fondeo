"""Control POSITIVO de la rejilla EMA+Fibo, despues de la correccion.

El nulo demuestra que el motor no FABRICA ventajas. Falta lo contrario:
demostrar que, corregido, no las DESTRUYE. Se inyecta una deriva conocida en
EURUSD y se comprueba que la rejilla la encuentra.

La deriva se inyecta a favor de las COMPRAS y solo en una fraccion de los
dias, para que no sea trivialmente detectable.

  PIPS=3 DIAS=0.6 python3 bt/ema_fibo_control.py
"""
import os, itertools, numpy as np, pandas as pd
PIPS = float(os.environ.get("PIPS", 3.0))    # pips de deriva por dia inyectado
FRAC = float(os.environ.get("DIAS", 0.6))    # fraccion de dias con deriva
exec(open("bt/ema_fibo.py").read().split("def evalua(")[0].replace(
     'NULOS = int(os.environ.get("NULOS", 10))','NULOS = 0'))

def inyecta(base, pips, frac):
    x = base.copy()
    dia = x.ts.dt.date.to_numpy()
    ini = np.flatnonzero(np.r_[True, dia[1:] != dia[:-1]])
    favor = rng.random(len(ini)) < frac
    aj = np.zeros(len(x))
    for k, i in enumerate(ini):
        j = ini[k+1] if k+1 < len(ini) else len(x)
        paso = (pips*U)/(j-i) * (1 if favor[k] else -1)
        aj[i:j] = np.cumsum(np.full(j-i, paso))
        if j < len(x): aj[j:] += aj[j-1]
    for c in ("open","high","low","close"): x[c] = x[c].to_numpy() + aj
    return x

exec(open("bt/ema_fibo.py").read().split("def evalua(")[1].split("def rejilla(")[0]
     .replace("def rejilla", "XX", 1).join(["def evalua(", ""]))
exec("def rejilla" + open("bt/ema_fibo.py").read().split("def rejilla")[1]
     .split("REAL = rejilla")[0])

for pips, frac in ((0.0, 0.5), (1.0, 0.6), (3.0, 0.6), (8.0, 0.9)):
    D = rejilla(inyecta(d, pips, frac) if pips else d, f"p{pips}")
    print(f"  deriva {pips:4.1f} pips en el {frac*100:.0f} % de los dias  ->  "
          f"mejor z {D.z.max():+7.2f}   celdas z>2 {int((D.z>2).sum()):3d}/{len(D)}"
          f"   R de la mejor {D.sort_values('z').iloc[-1].R:+.4f}", flush=True)
