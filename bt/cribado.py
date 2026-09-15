"""Cribado con nulo por permutacion circular.

El barajado simple destruiria la autocorrelacion de la serie y haria el nulo
demasiado facil de batir. Un DESPLAZAMIENTO CIRCULAR conserva toda la estructura
temporal del objetivo y solo rompe su alineacion con las variables, que es
exactamente lo que hay que romper.

Se guarda el MAXIMO estadistico sobre las 54 variables en cada permutacion. Eso
da la distribucion de "la mejor variable posible cuando no hay nada", y absorbe
de golpe el numero de contrastes, la correlacion entre variables y la
autocorrelacion de la serie.
"""
import numpy as np, pandas as pd

def rangos_z(a):
    # rangos medios sin scipy: pandas resuelve los empates igual que rankdata
    r = pd.Series(a).rank(method="average").to_numpy()
    return (r - r.mean())/r.std()

def prepara(X, y, mask):
    Xv = X[mask]; yv = y[mask]
    ok = np.isfinite(Xv).all(axis=1) & np.isfinite(yv)
    Xv, yv = Xv[ok], yv[ok]
    F = np.column_stack([rangos_z(Xv[:,j]) for j in range(Xv.shape[1])])
    Y = rangos_z(yv)
    return F, Y

def correlaciones(F, Y):
    return (F.T @ Y) / len(Y)

def nulo(F, Y, n_perm=200, semilla=0):
    rng = np.random.default_rng(semilla)
    n = len(Y); out = np.empty(n_perm)
    for i in range(n_perm):
        s = int(rng.integers(n//20, n - n//20))   # desplazamiento circular amplio
        out[i] = np.abs(correlaciones(F, np.roll(Y, s))).max()
    return out

def deciles(x, y):
    """Retorno medio del decil superior menos el del inferior, en unidades del objetivo."""
    q = pd.qcut(pd.Series(x), 10, labels=False, duplicates="drop")
    s = pd.Series(y).groupby(q).mean()
    return float(s.iloc[-1] - s.iloc[0])
