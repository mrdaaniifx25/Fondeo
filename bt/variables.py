"""Generacion mecanica de variables. Ninguna lleva nombre de metodologia.

Si el barrido de liquidez, el FVG o el order block contienen informacion, esa
informacion tiene que aparecer reflejada en alguna de estas medidas, porque son
descripciones completas del estado del precio. No se les pone nombre a proposito.
"""
import numpy as np, pandas as pd

def m15(m1):
    return m1.set_index("ts").resample("15min",label="left",closed="left").agg(
        open=("open","first"),high=("high","max"),low=("low","min"),
        close=("close","last")).dropna().reset_index()

def atr(df, n):
    pc = df.close.shift(1)
    tr = pd.concat([df.high-df.low,(df.high-pc).abs(),(df.low-pc).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()

def construye(d, cruz=None):
    """d: velas M15. cruz: dict con otros instrumentos ya alineados."""
    X = pd.DataFrame(index=d.index)
    c,h,l,o = d.close, d.high, d.low, d.open
    a48 = atr(d,48)

    # 1 retornos a varios horizontes
    for n in (1,2,4,8,12,24,48,96,192):
        X[f"ret_{n}"] = c/c.shift(n) - 1

    # 2 aceleracion: diferencia entre horizontes
    X["acel_4_12"]  = X.ret_4 - X.ret_12
    X["acel_12_48"] = X.ret_12 - X.ret_48
    X["acel_48_192"]= X.ret_48 - X.ret_192

    # 3 volatilidad y sus cocientes
    for n in (12,48,192):
        X[f"vol_{n}"] = atr(d,n)/c
    X["vol_r_12_96"]  = atr(d,12)/atr(d,96)
    X["vol_r_48_192"] = atr(d,48)/atr(d,192)
    X["rango_rel"]    = (h-l)/a48

    # 4 posicion dentro del rango de las ultimas n velas
    for n in (12,48,192,672):
        mx, mn = h.rolling(n).max(), l.rolling(n).min()
        X[f"pos_{n}"] = (c-mn)/(mx-mn).replace(0,np.nan)

    # 5 distancia a extremos en unidades de volatilidad
    for n in (12,48,192,672):
        X[f"dmax_{n}"] = (h.rolling(n).max()-c)/a48
        X[f"dmin_{n}"] = (c-l.rolling(n).min())/a48

    # 6 forma de la vela
    rng = (h-l).replace(0,np.nan)
    X["cuerpo"]   = (c-o)/rng
    X["mecha_sup"]= (h-np.maximum(o,c))/rng
    X["mecha_inf"]= (np.minimum(o,c)-l)/rng
    X["cuerpo_m4"]   = X.cuerpo.rolling(4).mean()
    X["mecha_sup_m4"]= X.mecha_sup.rolling(4).mean()
    X["mecha_inf_m4"]= X.mecha_inf.rolling(4).mean()

    # 7 racha de velas en la misma direccion
    signo = np.sign(c-o).fillna(0)
    racha = signo.groupby((signo!=signo.shift()).cumsum()).cumcount()+1
    X["racha"] = racha*signo

    # 8 tiempo
    ny = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert("America/New_York")
    mad= pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    hm = mad.hour + mad.minute/60
    X["hora_sin"] = np.sin(2*np.pi*hm/24)
    X["hora_cos"] = np.cos(2*np.pi*hm/24)
    X["dia_sem"]  = mad.dayofweek
    X["dia_mes"]  = mad.day
    X["min_dia"]  = hm

    # 9 cruzadas con otros instrumentos
    if cruz:
        for nom, cd in cruz.items():
            cc = cd.close.reindex(d.index)
            for n in (4,12,48):
                X[f"{nom}_ret_{n}"] = cc/cc.shift(n) - 1
                X[f"{nom}_dif_{n}"] = X[f"{nom}_ret_{n}"] - X[f"ret_{n}"]
    return X

def objetivo(d, n):
    """Retorno de las siguientes n velas, normalizado por volatilidad."""
    a = atr(d,48)
    return (d.close.shift(-n)/d.close - 1)/(a/d.close)
