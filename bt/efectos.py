"""E1-E3. Efectos con MUESTRA GRANDE y mecanismo conocido, no figuras del grafico.

Declarado antes de ejecutar:
  E1 nocturno frente a diurno en indices. Hipotesis publicada y muy replicada:
     casi toda la prima de riesgo de la renta variable se acumula de cierre a
     apertura. Muestra ~1700 dias por indice. Criterio: la diferencia debe ser
     positiva con p<0.01 Y sobrevivir al coste de financiacion nocturna.
  E2 calendario: dia de la semana y cambio de mes, en los 5 instrumentos.
     Criterio: p<0.01 tras corregir por el numero de casillas probadas.
  E3 filtro de tendencia lento como control de caida sobre exposicion larga al
     indice. NO se pide que bata a comprar y mantener en rentabilidad: se pide
     que capture la mayor parte con MENOS caida maxima. Criterio: retorno/caida
     mejor que comprar y mantener.
"""
import numpy as np, pandas as pd
from math import sqrt, erf

def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se if se>0 else 0.0
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

def ny(m1):
    d=m1.copy()
    d["ny"]=pd.DatetimeIndex(d["ts"]).tz_localize("UTC").tz_convert("America/New_York")
    return d

def sesiones(m1):
    """Apertura 09:30 y cierre 16:00 de Nueva York, con las velas M1 reales."""
    d=ny(m1); d["dia"]=d.ny.dt.date; d["hm"]=d.ny.dt.hour*60+d.ny.dt.minute
    ses=d[(d.hm>=570)&(d.hm<=960)]
    g=ses.groupby("dia").agg(ap=("open","first"), ci=("close","last"), n=("ts","size"))
    g=g[g.n>=300]
    g["dentro"]=g.ci/g.ap-1                      # 09:30 -> 16:00
    g["fuera"] =g.ap/g.ci.shift(1)-1             # 16:00 previo -> 09:30
    return g.dropna()
