"""Las operaciones se solapan. Cuanto miente eso a los intervalos de confianza.

Una operacion puede estar abierta hasta 60 horas, y en ese tiempo se abren
otras. Comparten el mismo recorrido de precio, asi que no son observaciones
independientes. El error estandar de toda la vida -desviacion partido por raiz
de n- supone independencia, y si no la hay se queda corto: los z salen mas
grandes de lo que deberian y todo parece mas significativo de lo que es.

Aqui se mide cuanto. Dos formas:
  · la autocorrelacion de la serie de R ordenada por tiempo
  · un bootstrap por bloques moviles, que respeta la dependencia local
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd

CELDAS = ["data/bc_UTC_B.csv", "data/bc_Madrid_B.csv", "data/bc_NY_B.csv"]
rng = np.random.default_rng(20260827)

def bootstrap_bloques(x, largo, reps=4000):
    """Remuestrea bloques contiguos de `largo` operaciones. Si hay dependencia
    dentro del bloque, la conserva, y la dispersion resultante es la buena."""
    n = len(x)
    if n < largo * 3:
        return np.nan
    nb = int(np.ceil(n / largo))
    ini = rng.integers(0, n - largo + 1, size=(reps, nb))
    idx = (ini[:, :, None] + np.arange(largo)[None, None, :]).reshape(reps, -1)[:, :n]
    return x[idx].mean(axis=1).std(ddof=1)

print("="*104)
print("¿SON INDEPENDIENTES LAS OPERACIONES?")
print("="*104)

for ruta in CELDAS:
    d = pd.read_csv(ruta)
    d["ts"] = pd.to_datetime(d.ts)
    print(f"\n{ruta.split('/')[-1]}   n = {len(d):,}")
    # dentro de cada instrumento, ordenadas por tiempo
    acs = []
    for ins, g in d.groupby("ins"):
        g = g.sort_values("ts")
        x = g.R_neto.to_numpy()
        if len(x) < 60: continue
        ac = [float(np.corrcoef(x[:-k], x[k:])[0, 1]) for k in (1, 2, 3, 5, 10)]
        acs.append(ac)
        sep = g.ts.diff().dt.total_seconds().median()/3600
        print(f"   {ins:8s} n={len(x):>5,}  separación mediana entre entradas "
              f"{sep:>6.1f} h   autocorr r1 {ac[0]:+.3f}  r2 {ac[1]:+.3f}  "
              f"r3 {ac[2]:+.3f}  r5 {ac[3]:+.3f}  r10 {ac[4]:+.3f}")
    x = d.sort_values("ts").R_neto.to_numpy()
    ee_ing = x.std(ddof=1)/np.sqrt(len(x))
    print(f"   {'':8s} error estándar ingenuo          {ee_ing:.4f}   ->  z {x.mean()/ee_ing:+.2f}")
    for L in (5, 20, 50):
        ee_b = bootstrap_bloques(x, L)
        if np.isfinite(ee_b):
            print(f"   {'':8s} bootstrap por bloques de {L:>2d}      {ee_b:.4f}   ->  z "
                  f"{x.mean()/ee_b:+.2f}   (×{ee_b/ee_ing:.2f})")

print("\n" + "="*104)
print("Un factor cercano a 1 quiere decir que el error estándar de siempre vale.")
print("Un factor de 1,5 o más quiere decir que todos los z del proyecto están")
print("inflados en esa proporción, y hay que dividirlos antes de creérselos.")
