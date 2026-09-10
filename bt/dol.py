"""DOL - Draw On Liquidity: niveles de temporalidad alta AUN NO TOMADOS.

Los videos insisten en que la direccion la marca un objetivo de liquidez sin
recoger (alto/bajo del dia, semana o mes anteriores) y en que solo se operan
turtle soups a favor de ese objetivo. Aqui se construye ese mapa, vela a vela y
sin mirar al futuro: un nivel nace cuando su periodo cierra y muere cuando el
precio lo atraviesa.
"""
import numpy as np, pandas as pd

def niveles(m1: pd.DataFrame):
    """Devuelve los niveles (precio, nacimiento, lado, marco) del dia, semana y
    mes anteriores, junto con el instante en que el precio los atraviesa."""
    ts = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York")
    dia_fx = pd.Index((ts + pd.Timedelta(hours=7)).date)          # corte 17:00 NY
    d = m1.copy(); d["k"] = dia_fx
    per = {}
    per["D"] = d.groupby("k").agg(high=("high","max"), low=("low","min"), fin=("ts","max"))
    d["ks"] = pd.PeriodIndex(pd.to_datetime(dia_fx), freq="W")
    per["W"] = d.groupby("ks").agg(high=("high","max"), low=("low","min"), fin=("ts","max"))
    d["km"] = pd.PeriodIndex(pd.to_datetime(dia_fx), freq="M")
    per["M"] = d.groupby("km").agg(high=("high","max"), low=("low","min"), fin=("ts","max"))

    filas = []
    for marco, g in per.items():
        g = g.sort_values("fin").reset_index(drop=True)
        for i in range(len(g)-1):
            nace = g.fin.iloc[i] + pd.Timedelta(minutes=1)
            filas.append((g.high.iloc[i], nace, True,  marco))
            filas.append((g.low.iloc[i],  nace, False, marco))
    lv = pd.DataFrame(filas, columns=["px","nace","arriba","marco"]).sort_values("nace")

    # instante en que el precio atraviesa cada nivel
    t = m1["ts"].to_numpy(); H = m1["high"].to_numpy(); L = m1["low"].to_numpy()
    muere = []
    for px, nace, arriba, _ in lv.itertuples(index=False):
        i0 = int(np.searchsorted(t, np.datetime64(nace)))
        if i0 >= len(t): muere.append(pd.NaT); continue
        g = (H[i0:] >= px) if arriba else (L[i0:] <= px)
        muere.append(pd.Timestamp(t[i0+int(np.argmax(g))]) if g.any() else pd.Timestamp("2100-01-01"))
    lv["muere"] = muere
    return lv.dropna(subset=["muere"]).reset_index(drop=True)


def mapa(ch: pd.DataFrame, lv: pd.DataFrame):
    """Para cada vela del grafico: nivel vivo mas cercano por arriba y por abajo."""
    n = len(ch)
    up_px = np.full(n, np.nan); dn_px = np.full(n, np.nan)
    up_tf = np.full(n, "", dtype=object); dn_tf = np.full(n, "", dtype=object)

    ev = []   # (instante, +1 alta / -1 baja, indice del nivel)
    for i, r in enumerate(lv.itertuples(index=False)):
        ev.append((r.nace, 1, i)); ev.append((r.muere, -1, i))
    ev.sort(key=lambda x: x[0])
    px = lv.px.to_numpy(); arriba = lv.arriba.to_numpy(); marco = lv.marco.to_numpy()

    vivos = set(); j = 0
    tsv = ch["ts"].to_numpy(); cl = ch["close"].to_numpy()
    for i in range(n):
        while j < len(ev) and np.datetime64(ev[j][0]) <= tsv[i]:
            _, tipo, k = ev[j]
            if tipo == 1: vivos.add(k)
            else: vivos.discard(k)
            j += 1
        mu = md = None
        for k in vivos:
            if arriba[k] and px[k] > cl[i]:
                if mu is None or px[k] < px[mu]: mu = k
            elif (not arriba[k]) and px[k] < cl[i]:
                if md is None or px[k] > px[md]: md = k
        if mu is not None: up_px[i], up_tf[i] = px[mu], marco[mu]
        if md is not None: dn_px[i], dn_tf[i] = px[md], marco[md]
    return pd.DataFrame({"dol_up": up_px, "dol_up_tf": up_tf,
                         "dol_dn": dn_px, "dol_dn_tf": dn_tf})
