"""Regla congelada del cribado de cero (docs/CANDIDATA_cero.md).

Esto es la ESPECIFICACION, no una busqueda. Todo numero que aparece aqui viene
de data/umbrales_cero.txt, fijado con 2020-2023 de EURUSD y escrito en el disco
ANTES de abrir ningun periodo de confirmacion. Este modulo no ajusta nada.
"""
import numpy as np, pandas as pd

# las 15 variables que superaron el percentil 99 del nulo por permutacion
# circular, con el SIGNO de su correlacion en descubrimiento. El signo sirve
# para orientarlas todas en la misma direccion economica: dmax_12 y dmax_48
# miden "lo lejos que esta el precio por DEBAJO del maximo", asi que su signo
# positivo dice lo mismo que el negativo de las otras trece.
VARS = {
    "ret_1": -1, "ret_2": -1, "ret_4": -1, "ret_8": -1, "ret_12": -1,
    "pos_12": -1, "pos_48": -1,
    "dmax_12": +1, "dmin_12": -1, "dmax_48": +1, "dmin_48": -1,
    "cuerpo": -1, "cuerpo_m4": -1, "mecha_inf_m4": -1, "racha": -1,
}

def lee_umbrales(ruta="data/umbrales_cero.txt"):
    d = {}
    for ln in open(ruta):
        if "=" in ln:
            k, v = ln.strip().split("=")
            d[k] = float(v)
    return d

def rango_movil(s, n):
    """Rango percentil de cada valor dentro de las n velas anteriores, el
    actual incluido. Solo mira hacia atras.

    method="min" no es un detalle: `racha` es entera y esta llena de empates,
    y con el reparto medio de empates la senal compuesta se desplaza. Es el
    reparto con el que se calcularon los umbrales congelados."""
    return s.rolling(n, min_periods=n).rank(pct=True, method="min")

def senal(X, ventana):
    """Senal compuesta en [-1, 0]: menos la media de los rangos percentiles.

    Las variables NO se reorientan por signo; van tal cual, como se calculo en
    descubrimiento. Trece de las quince suben cuando el precio acaba de subir,
    asi que la lectura practica es directa:
        senal muy negativa  -> precio estirado hacia ARRIBA  -> vender
        senal cerca de 0    -> precio estirado hacia ABAJO   -> comprar"""
    return -pd.concat([rango_movil(X[v], ventana) for v in VARS],
                      axis=1).mean(axis=1)

def operaciones(d, X, umb, atr48_pips, coste_pips, unidad,
                atr_min=None, ancho=None):
    """Aplica la regla y devuelve una tabla de operaciones.

    d: velas M15 (ts, open, high, low, close). X: variables de variables.py
    umb: dict de umbrales. atr48_pips: ATR(48) en pips. unidad: tamano del pip.
    atr_min / ancho: solo para reexpresar la regla en otro instrumento; si van
    a None se usan los numeros congelados tal cual.
    """
    n = int(umb["HORIZONTE"]); ven = int(umb["VENTANA_RANGO"])
    s = senal(X, ven)
    alta = umb["SENAL_ALTA"] if ancho is None else ancho[0]
    baja = umb["SENAL_BAJA"] if ancho is None else ancho[1]
    amin = umb["ATR48_MIN"] if atr_min is None else atr_min

    vol = atr48_pips >= amin
    # reversion: se compra lo que acaba de caer y se vende lo que acaba de subir
    comprar = vol & (s >= alta)     # media de rangos baja = ha caido
    vender  = vol & (s <= baja)     # media de rangos alta = ha subido

    c = d.close.to_numpy()
    fut = pd.Series(c, index=d.index).shift(-n)
    lado = np.where(comprar, 1, np.where(vender, -1, 0))
    bruto = lado * (fut.to_numpy() - c) / unidad
    m = (lado != 0) & np.isfinite(bruto)

    return pd.DataFrame({
        "ts": d.ts[m].to_numpy(),
        "lado": lado[m],
        "senal": s[m].to_numpy(),
        "atr": atr48_pips[m].to_numpy(),
        "bruto": bruto[m],
        "neto": bruto[m] - coste_pips,
    })

def resumen(t, anos):
    if len(t) == 0:
        return dict(n=0)
    b, x = t.bruto.to_numpy(), t.neto.to_numpy()
    ee = x.std(ddof=1) / np.sqrt(len(x))
    return dict(n=len(t), por_ano=len(t)/anos, bruto=b.mean(), neto=x.mean(),
                ee=ee, ic_lo=x.mean()-1.96*ee, ic_hi=x.mean()+1.96*ee,
                aciertos=float((b > 0).mean()))
