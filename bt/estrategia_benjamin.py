"""Estrategia del video 'convertir 120 en 1000 dolares' (Benjamin).

Reglas transcritas literalmente:
  · Solo EURUSD
  · Marcar un maximo o minimo en H1 o H4
  · Cuando el precio LIQUIDA ese extremo -> buscar la operacion CONTRARIA
        liquida un maximo -> ventas | liquida un minimo -> compras
  · Solo en dos ventanas, hora de Espana:
        Londres    09:00 - 11:00
        Nueva York 14:00 - 16:30
  · Tras la liquidacion, bajar a M1-M5 (el prefiere M2) y buscar
        impulso + imbalance = un FVG de tres velas donde la 1a y la 3a no se tocan
  · Entrada en ese imbalance, stop "cubriendote en los maximos", objetivo 1:2
"""
import numpy as np, pandas as pd
from math import sqrt, erf

U, COSTE = 0.0001, 1.2
# ventanas en hora de Espana, tal como las dice el video
SES = [(9.0, 11.0), (14.0, 16.5)]

def pivotes(df, izq=2, der=2):
    """Maximos y minimos de giro: extremo mayor/menor que sus vecinos."""
    h, l = df.high.to_numpy(), df.low.to_numpy()
    n = len(df)
    ph = np.zeros(n, bool); pl = np.zeros(n, bool)
    for i in range(izq, n - der):
        if h[i] == max(h[i-izq:i+der+1]) and h[i] > h[i-1] and h[i] > h[i+1]: ph[i] = True
        if l[i] == min(l[i-izq:i+der+1]) and l[i] < l[i-1] and l[i] < l[i+1]: pl[i] = True
    return ph, pl

def marcos(m1, tf):
    ny = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York").tz_localize(None)
    d = m1.assign(ny=ny)
    if tf == "H1":
        d["id"] = d.ny.dt.floor("1h"); minimo = 30
    else:
        d["id"] = (d.ny - pd.Timedelta(hours=1)).dt.floor("4h") + pd.Timedelta(hours=1); minimo = 120
    g = d.groupby("id").agg(high=("high","max"), low=("low","min"),
                            fin=("ts","max"), n=("ts","size"))
    return g[g.n >= minimo].reset_index()

def niveles_vivos(g, m1):
    """Cada pivote es un nivel que nace al confirmarse y muere al ser barrido."""
    ph, pl = pivotes(g)
    t = m1["ts"].to_numpy(); H = m1["high"].to_numpy(); L = m1["low"].to_numpy()
    filas = []
    fin = g.fin.to_numpy(); hi = g.high.to_numpy(); lo = g.low.to_numpy()
    for i in range(len(g) - 2):
        if not (ph[i] or pl[i]): continue
        # el pivote no se confirma hasta que cierran las dos velas siguientes
        nace = np.datetime64(pd.Timestamp(fin[i+2])) + np.timedelta64(1, "m")
        i0 = int(np.searchsorted(t, nace))
        if i0 >= len(t): continue
        for px, arriba, ok in ((hi[i], True, ph[i]), (lo[i], False, pl[i])):
            if not ok: continue
            gg = (H[i0:] > px) if arriba else (L[i0:] < px)
            if not gg.any(): continue
            k = i0 + int(np.argmax(gg))
            filas.append(dict(px=px, arriba=bool(arriba), ibarr=k, tbarr=pd.Timestamp(t[k])))
    return pd.DataFrame(filas).sort_values("ibarr").reset_index(drop=True)

def en_sesion(ts):
    t = pd.Timestamp(ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    h = t.hour + t.minute/60
    return any(a <= h < b for a, b in SES)

def pz(x):
    n = len(x)
    if n < 3: return 0.0, 1.0
    se = x.std(ddof=1)/sqrt(n); z = x.mean()/se if se > 0 else 0.0
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

def pf(R):
    g, p = R[R>0].sum(), -R[R<=0].sum()
    return g/p if p>0 else float("inf")
