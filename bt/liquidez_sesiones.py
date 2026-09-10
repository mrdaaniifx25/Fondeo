"""Teoria del usuario: cuando se liquida el maximo o minimo de una sesion previa,
el precio se va al lado opuesto, o a la liquidez pendiente de sesiones anteriores.

Se mide como operacion completa, no como "acaba llegando":
   suceso  el precio atraviesa un nivel de sesion que seguia VIVO (sin tocar)
   entrada al cierre de la vela M15 que vuelve dentro del rango de esa sesion
   sentido contrario al barrido
   objetivo (A) el extremo opuesto de ESA MISMA sesion
            (B) el nivel de sesion vivo mas cercano del lado contrario
   stop     el extremo del barrido mas un colchon
"""
import numpy as np, pandas as pd
from math import sqrt, erf

# sesiones en hora de Nueva York, las que usa el usuario
SES = {"Asia": (18, 1), "Londres": (2, 8), "NuevaYork": (8, 14)}

def sesiones(m1):
    """Rango de cada sesion cerrada, con su hora de fin."""
    ny = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York").tz_localize(None)
    d = m1.copy(); d["ny"] = ny; d["h"] = ny.hour
    # dia de sesion: se desplaza 6 h para que Asia (18:00-01:00) caiga entera en uno
    d["ds"] = (d["ny"] + pd.Timedelta(hours=6)).dt.date
    filas = []
    for nom, (h0, h1) in SES.items():
        if h0 < h1:
            m = (d.h >= h0) & (d.h < h1)
        else:                       # cruza medianoche
            m = (d.h >= h0) | (d.h < h1)
        g = d[m].groupby("ds").agg(hi=("high","max"), lo=("low","min"),
                                   ini=("ts","min"), fin=("ts","max"), n=("ts","size"))
        g = g[g.n >= 60]
        for k, r in g.iterrows():
            filas.append(dict(ses=nom, dia=k, hi=r.hi, lo=r.lo, ini=r.ini, fin=r.fin))
    return pd.DataFrame(filas).sort_values("fin").reset_index(drop=True)

def niveles(ses, m1):
    """Cada extremo de sesion es un nivel que nace al cerrar la sesion y muere
    cuando el precio lo atraviesa por primera vez."""
    t = m1["ts"].to_numpy(); H = m1["high"].to_numpy(); L = m1["low"].to_numpy()
    filas = []
    for r in ses.itertuples():
        nace = np.datetime64(pd.Timestamp(r.fin)) + np.timedelta64(1, "m")
        i0 = int(np.searchsorted(t, nace))
        for px, arriba in ((r.hi, True), (r.lo, False)):
            if i0 >= len(t):
                muere = pd.Timestamp("2100-01-01"); imuere = 10**9
            else:
                g = (H[i0:] > px) if arriba else (L[i0:] < px)
                if g.any():
                    imuere = i0 + int(np.argmax(g)); muere = pd.Timestamp(t[imuere])
                else:
                    imuere = 10**9; muere = pd.Timestamp("2100-01-01")
            filas.append(dict(ses=r.ses, px=px, arriba=arriba, otro=r.lo if arriba else r.hi,
                              nace=pd.Timestamp(nace), muere=muere, imuere=imuere,
                              hi=r.hi, lo=r.lo))
    return pd.DataFrame(filas).sort_values("nace").reset_index(drop=True)

def pz(x):
    n = len(x)
    if n < 3: return 0.0, 1.0
    se = x.std(ddof=1)/sqrt(n); z = x.mean()/se if se > 0 else 0.0
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

def pf(R):
    g, p = R[R>0].sum(), -R[R<=0].sum()
    return g/p if p>0 else float("inf")
