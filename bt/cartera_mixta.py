"""Momento + carry, mitad y mitad. SIN optimizar nada: no hay parametro que
elegir, son las dos series ya medidas a igual peso de riesgo. Se declara asi
para que no quepa ajuste posterior.
"""
import numpy as np, pandas as pd
from math import sqrt

def lee(n):
    s = pd.read_csv(f"data/ext/serie_{n}.csv", index_col=0, parse_dates=True).iloc[:, 0]
    return s.dropna()

M, CG, CT = lee("momento"), lee("carry_g10"), lee("carry_todas")

def ficha(et, x):
    if len(x) < 24: return
    t = x.mean()/(x.std(ddof=1)/sqrt(len(x))); sh = x.mean()/x.std(ddof=1)*sqrt(12)
    dd = float((x.cumsum() - x.cumsum().cummax()).min())
    k = 10.0/abs(dd) if dd < 0 else np.nan
    eur = 50000*x.mean()*12*k/100/12
    print(f"  {et:<34} meses {len(x):>4}  t {t:>+6.2f}  Sharpe {sh:>+5.2f}  "
          f"asim {x.skew():>+5.2f}  peor mes {x.min()/x.std(ddof=1):>+5.1f}σ  "
          f"peor caída {dd:>+6.2f}  ->{eur:>+6.0f} €/mes")

for nom, C in (("G10", CG), ("todas las divisas", CT)):
    print("="*118)
    print(f"MOMENTO + CARRY ({nom}) · mitad y mitad, escalado a que la peor caída histórica sea del 10 %")
    print("="*118)
    j = pd.concat([M.rename("mom"), C.rename("car")], axis=1).dropna()
    mix = 0.5*j.mom + 0.5*j.car
    print(f"  correlación entre las dos: {j.mom.corr(j.car):+.3f}\n")
    ficha("momento solo", j.mom)
    ficha("carry solo", j.car)
    ficha("MEZCLA 50/50", mix)
    print()
    for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026")):
        m_ = mix[(mix.index.year >= int(a)) & (mix.index.year <= int(b))]
        ficha(f"  mezcla {a}-{b}", m_)
    print()
