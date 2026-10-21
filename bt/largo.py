"""Pre-registro docs/PREREGISTRO_largo.md

Momento en series temporales sobre barras semanales y mensuales.
Todo en unidades de ruido, para poder comparar con el coste.
"""
import numpy as np, pandas as pd
from math import sqrt

INS = {"EURUSD": ("data/eurusd_m1.parquet", 1.43e-4),
       "oro":    ("data/xauusd_m1.parquet", 0.35),
       "DAX":    ("data/grxeur_m1.parquet", 1.6)}
rng = np.random.default_rng(53)

def barras(ruta, regla):
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts")
    g = m1.set_index("ts").resample(regla).agg(c=("close","last"), n=("close","size")).dropna()
    return g[g.n > 200].c.to_numpy()

def momento(c, K):
    """señal en t (sólo pasado), rendimiento de t a t+1."""
    if len(c) < K+3: return None, None
    s = np.sign(c[K:-1] - c[:-K-1])
    r = c[K+1:] - c[K:-1]
    m = s != 0
    return s[m], r[m]

for regla, nom, por_anio in (("W", "semanas", 52), ("ME", "meses", 12)):
    print("\n" + "="*112); print(f"BARRAS {nom.upper()}"); print("="*112)
    datos = {}
    for ins, (ruta, coste) in INS.items():
        c = barras(ruta, regla)
        datos[ins] = (c, coste)
        print(f"  {ins:<8} {len(c):>4} barras")
    print()
    print(f"{'K':>3} {'instrumento':<10} {'n':>5} {'efecto/ruido':>14} {'IC95':>22} "
          f"{'coste/ruido':>12} {'nulo':>9}")
    print("-"*112)
    for K in (1, 3, 6, 12):
        juntos_s, juntos_r = [], []
        for ins, (c, coste) in datos.items():
            s, r = momento(c, K)
            if s is None or len(s) < 20: continue
            sig = r.std(ddof=1); x = s*r/sig
            m, ic = x.mean(), 1.96*x.std(ddof=1)/sqrt(len(x))
            cs = coste/sig
            print(f"{K:>3} {ins:<10} {len(x):>5} {m:>+14.4f} [{m-ic:>+8.4f},{m+ic:>+8.4f}] "
                  f"{cs:>12.4f}")
            juntos_s.append(s); juntos_r.append(r/sig)
        if juntos_s:
            x = np.concatenate([a*b for a, b in zip(juntos_s, juntos_r)])
            m, ic = x.mean(), 1.96*x.std(ddof=1)/sqrt(len(x))
            xn = np.concatenate([rng.permutation(a)*b for a, b in zip(juntos_s, juntos_r)])
            mn = xn.mean()
            marca = ""
            if m-ic > 0: marca = "  <- fuera del cero"
            print(f"{K:>3} {'LOS TRES':<10} {len(x):>5} {m:>+14.4f} [{m-ic:>+8.4f},{m+ic:>+8.4f}] "
                  f"{'':>12} {mn:>+9.4f}{marca}")
            print(f"{'':>3} {'':10} {'':5} {'   ic +-':>14} {ic:>8.4f}   "
                  f"(hace falta n={int(len(x)*(ic/0.055)**2):,} para ver un efecto de 0,055)")
        print()

# ---------------------------------------------------------------------------
# Dos comprobaciones que el resultado de arriba necesita antes de poder leerse.
print("\n" + "="*112)
print("COMPROBACION 1 · ¿el nulo de una sola baraja dice algo? (1.000 barajas)")
print("="*112)
for regla, nom in (("W","semanas"), ("ME","meses")):
    datos = {i: (barras(r, regla), c) for i, (r, c) in INS.items()}
    for K in (1, 3):
        S, R = [], []
        for ins, (c, _) in datos.items():
            s, r = momento(c, K)
            if s is None or len(s) < 20: continue
            S.append(s); R.append(r/r.std(ddof=1))
        real = np.concatenate([a*b for a, b in zip(S, R)]).mean()
        sim = np.array([np.concatenate([rng.permutation(a)*b for a, b in zip(S, R)]).mean()
                        for _ in range(1000)])
        print(f"  {nom:<8} K={K:<3} real {real:+.4f}   nulos: media {sim.mean():+.4f}, "
              f"desviacion {sim.std():.4f}, del 2,5 % al 97,5 % [{np.percentile(sim,2.5):+.4f}, "
              f"{np.percentile(sim,97.5):+.4f}]   -> el real esta en el percentil "
              f"{100*(sim < real).mean():.0f}")

print("\n" + "="*112)
print("COMPROBACION 2 · ¿es momento, o es que el oro subio y ya esta?")
print("="*112)
for regla, nom in (("W","semanas"), ("ME","meses")):
    for ins, (ruta, _) in INS.items():
        c = barras(ruta, regla)
        for K in (3,):
            s, r = momento(c, K)
            if s is None: continue
            largo = 100*(s > 0).mean()
            subida = 100*(c[-1]/c[0] - 1)
            # si la senal esta casi siempre larga, no mide momento: mide la tendencia
            print(f"  {nom:<8} {ins:<8} K={K}  senal larga el {largo:5.1f} % del tiempo   "
                  f"el instrumento subio {subida:+7.1f} % en la muestra"
                  f"{'   <- sesgada' if largo > 65 or largo < 35 else ''}")
