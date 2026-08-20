"""ESTRATEGIA 1 - "4 confirmaciones" (Liquidity Sweep) del video.

Reglas destiladas de la transcripcion:
  C1  El precio elimina un nivel estructural: alto/bajo de la SESION anterior
      o alto/bajo del DIA anterior.
  C2  En H4 ese barrido es un Liquidity Sweep (LS): la vela toca el nivel con
      mecha pero el precio esta de vuelta al otro lado. Si cierra con cuerpo
      mas alla es un Liquidity Run (LR) y NO hay operacion.
  C3  Lo mismo en H1.
  C4  Vela envolvente en M5 -> entrada al cierre de esa vela.
  Direccion: barrido de maximo -> venta.  Barrido de minimo -> compra.
  SL: justo por encima/debajo de la toma de liquidez.
  TP: 1R fijo.

No hay lookahead: en la vela M5 t solo se usan velas H1/H4 acumuladas hasta el
cierre de t, niveles de sesiones/dias YA cerrados, y la resolucion SL/TP empieza
en la vela M1 siguiente al cierre de t.
"""
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

PIP = 0.0001
_CACHE = None

@dataclass
class Config:
    # --- niveles ---
    usar_sesion: bool = True
    usar_dia: bool = True
    # --- confirmaciones ---
    exigir_h4: bool = True
    exigir_h1: bool = True
    h4_anchor_hour: int = 0        # H4 alineado a 00:00 UTC
    min_body_ratio: float = 0.0    # cuerpo minimo de la envolvente / rango
    # --- ejecucion ---
    sl_buffer_pips: float = 1.0
    rr: float = 1.0
    coste_pips: float = 1.2        # spread + slippage ida y vuelta
    max_trade_horas: int = 24
    # --- ventana horaria (hora local de cada plaza, None = todo el dia) ---
    kz_londres: tuple | None = (7, 11)    # Europe/London
    kz_ny: tuple | None = (8, 12)         # America/New_York
    solo_kz: bool = True
    # --- rango de fechas ---
    desde: str | None = None
    hasta: str | None = None


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCCION DE MARCOS Y NIVELES
# ═══════════════════════════════════════════════════════════════════════════
def agregar(m1: pd.DataFrame, regla: str) -> pd.DataFrame:
    g = m1.set_index("ts").resample(regla, label="left", closed="left")
    out = g.agg(open=("open", "first"), high=("high", "max"),
                low=("low", "min"), close=("close", "last")).dropna()
    return out


def sesiones_completas(m1: pd.DataFrame) -> pd.DataFrame:
    """Alto/bajo de cada sesion, con la hora UTC en que la sesion se cierra.

    Sesiones definidas en la hora local de su propia plaza, para que el horario
    de verano se gestione solo.
    """
    ts = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC")
    defs = [("Asia", "Asia/Tokyo", 0, 8),
            ("Londres", "Europe/London", 8, 16),
            ("NY", "America/New_York", 8, 17)]
    filas = []
    for nombre, tz, h_ini, h_fin in defs:
        loc = ts.tz_convert(tz)
        dentro = (loc.hour >= h_ini) & (loc.hour < h_fin)
        if not dentro.any():
            continue
        sub = m1.loc[dentro].copy()
        sub["dia"] = loc[dentro].date
        g = sub.groupby("dia").agg(high=("high", "max"), low=("low", "min"),
                                   fin=("ts", "max"))
        g["sesion"] = nombre
        filas.append(g.reset_index())
    ses = pd.concat(filas, ignore_index=True).sort_values("fin")
    # la sesion queda "cerrada" (utilizable) un minuto despues de su ultima vela
    ses["disponible"] = ses["fin"] + pd.Timedelta(minutes=1)
    return ses.reset_index(drop=True)


def dias_completos(m1: pd.DataFrame) -> pd.DataFrame:
    """Alto/bajo diario con el corte de las 17:00 de Nueva York, que es el que
    usa TradingView para los graficos diarios de FX."""
    ts = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York")
    dia_fx = (ts + pd.Timedelta(hours=7)).date      # 17:00 NY -> corte de dia
    d = m1.copy()
    d["dia_fx"] = dia_fx
    g = d.groupby("dia_fx").agg(high=("high", "max"), low=("low", "min"),
                                fin=("ts", "max")).reset_index()
    g["disponible"] = g["fin"] + pd.Timedelta(minutes=1)
    return g.sort_values("fin").reset_index(drop=True)


def _asof(m5_ts: pd.Series, tabla: pd.DataFrame, col: str) -> np.ndarray:
    """Ultimo valor de `col` cuya sesion/dia ya estaba disponible en cada M5."""
    izq = pd.DataFrame({"ts": m5_ts})
    der = tabla[["disponible", col]].rename(columns={"disponible": "ts"})
    m = pd.merge_asof(izq, der.sort_values("ts"), on="ts", direction="backward")
    return m[col].to_numpy()


# ═══════════════════════════════════════════════════════════════════════════
#  SENALES
# ═══════════════════════════════════════════════════════════════════════════
def construir_senales(m1: pd.DataFrame, cfg: Config):
    m5 = agregar(m1, "5min").reset_index().rename(columns={"ts": "ts"})

    # Extremos acumulados de la vela H1/H4 EN CURSO hasta el cierre de cada M5.
    m5["h1_id"] = m5["ts"].dt.floor("1h")
    m5["h4_id"] = (m5["ts"] - pd.Timedelta(hours=cfg.h4_anchor_hour)).dt.floor("4h")
    for pref, key in (("h1", "h1_id"), ("h4", "h4_id")):
        m5[f"{pref}_hi"] = m5.groupby(key)["high"].cummax()
        m5[f"{pref}_lo"] = m5.groupby(key)["low"].cummin()
        m5[f"{pref}_op"] = m5.groupby(key)["open"].transform("first")

    # Niveles estructurales ya cerrados.
    global _CACHE
    if _CACHE is None:
        _CACHE = (sesiones_completas(m1), dias_completos(m1))
    ses, dia = _CACHE
    m5["ses_hi"] = _asof(m5["ts"], ses, "high")
    m5["ses_lo"] = _asof(m5["ts"], ses, "low")
    m5["dia_hi"] = _asof(m5["ts"], dia, "high")
    m5["dia_lo"] = _asof(m5["ts"], dia, "low")

    # Ventana horaria.
    tsu = pd.DatetimeIndex(m5["ts"]).tz_localize("UTC")
    en_kz = np.zeros(len(m5), dtype=bool)
    if cfg.kz_londres:
        h = tsu.tz_convert("Europe/London").hour
        en_kz |= (h >= cfg.kz_londres[0]) & (h < cfg.kz_londres[1])
    if cfg.kz_ny:
        h = tsu.tz_convert("America/New_York").hour
        en_kz |= (h >= cfg.kz_ny[0]) & (h < cfg.kz_ny[1])
    m5["en_kz"] = en_kz if cfg.solo_kz else True

    # Vela envolvente en M5.
    o, c = m5["open"].to_numpy(), m5["close"].to_numpy()
    hi, lo = m5["high"].to_numpy(), m5["low"].to_numpy()
    po, pc = np.roll(o, 1), np.roll(c, 1)
    rango = np.maximum(hi - lo, 1e-12)
    cuerpo_ok = np.abs(c - o) / rango >= cfg.min_body_ratio
    env_baj = (pc > po) & (c < o) & (o >= pc) & (c <= po) & cuerpo_ok
    env_alc = (pc < po) & (c > o) & (o <= pc) & (c >= po) & cuerpo_ok
    env_baj[0] = env_alc[0] = False

    # Niveles candidatos por direccion.
    niveles_alto, niveles_bajo = [], []
    if cfg.usar_sesion:
        niveles_alto.append(m5["ses_hi"].to_numpy())
        niveles_bajo.append(m5["ses_lo"].to_numpy())
    if cfg.usar_dia:
        niveles_alto.append(m5["dia_hi"].to_numpy())
        niveles_bajo.append(m5["dia_lo"].to_numpy())

    h1_hi, h1_lo = m5["h1_hi"].to_numpy(), m5["h1_lo"].to_numpy()
    h4_hi, h4_lo = m5["h4_hi"].to_numpy(), m5["h4_lo"].to_numpy()
    h1_op, h4_op = m5["h1_op"].to_numpy(), m5["h4_op"].to_numpy()

    emb = {}   # embudo de diagnostico
    def _lado(niveles, run_hi, run_lo, es_corto):
        barrido = np.zeros(len(m5), dtype=bool)
        ls_h1 = np.zeros(len(m5), dtype=bool)
        ls_h4 = np.zeros(len(m5), dtype=bool)
        nivel_sel = np.full(len(m5), np.nan)
        for L in niveles:
            ok = ~np.isnan(L)
            if es_corto:
                # C1: el nivel fue tomado por la mecha de la vela en curso.
                b = ok & (h1_hi > L)
                # LS = mecha por encima pero CUERPO integro por debajo.
                # LR = el cuerpo se queda por encima -> no hay operacion.
                s1 = b & (np.maximum(h1_op, c) < L)
                s4 = s1 & (h4_hi > L) & (np.maximum(h4_op, c) < L)
            else:
                b = ok & (h1_lo < L)
                s1 = b & (np.minimum(h1_op, c) > L)
                s4 = s1 & (h4_lo < L) & (np.minimum(h4_op, c) > L)
            barrido |= b
            ls_h1 |= s1
            ls_h4 |= s4
            nuevo = s4 & np.isnan(nivel_sel)
            nivel_sel[nuevo] = L[nuevo]
        return barrido, ls_h1, ls_h4, nivel_sel

    b_c, l1_c, l4_c, niv_c = _lado(niveles_alto, h1_hi, h1_lo, True)
    b_l, l1_l, l4_l, niv_l = _lado(niveles_bajo, h1_hi, h1_lo, False)

    conf_c = l4_c if cfg.exigir_h4 else l1_c
    conf_l = l4_l if cfg.exigir_h4 else l1_l
    if not cfg.exigir_h1:
        conf_c, conf_l = (b_c if not cfg.exigir_h4 else conf_c), (b_l if not cfg.exigir_h4 else conf_l)

    sig_corto = conf_c & env_baj & m5["en_kz"].to_numpy()
    sig_largo = conf_l & env_alc & m5["en_kz"].to_numpy()

    emb["velas M5"] = len(m5)
    emb["en ventana horaria"] = int(m5["en_kz"].sum()) if cfg.solo_kz else len(m5)
    emb["C1 nivel barrido"] = int((b_c | b_l).sum())
    emb["C2/C3 LS en H1"] = int((l1_c | l1_l).sum())
    emb["C2/C3 LS en H1+H4"] = int((l4_c | l4_l).sum())
    emb["C4 envolvente M5"] = int((env_baj | env_alc).sum())
    emb["senales (4 de 4)"] = int((sig_corto | sig_largo).sum())

    m5["sig_corto"], m5["sig_largo"] = sig_corto, sig_largo
    m5["niv_corto"], m5["niv_largo"] = niv_c, niv_l
    return m5, emb


# ═══════════════════════════════════════════════════════════════════════════
#  SIMULACION  (resolucion SL/TP a granularidad M1)
# ═══════════════════════════════════════════════════════════════════════════
def simular(m5: pd.DataFrame, m1: pd.DataFrame, cfg: Config):
    t1 = m1["ts"].to_numpy()
    h1_, l1_ = m1["high"].to_numpy(), m1["low"].to_numpy()
    max_bars = cfg.max_trade_horas * 60

    cand = m5[(m5.sig_corto | m5.sig_largo)]
    trades, libre_desde = [], np.datetime64("1970-01-01")
    ambiguas = 0

    for r in cand.itertuples():
        entrada_ts = np.datetime64(r.ts + pd.Timedelta(minutes=5))
        if entrada_ts < libre_desde:
            continue                                    # una operacion a la vez
        corto = bool(r.sig_corto)
        entrada = r.close
        if corto:
            sl = max(r.h1_hi, r.high) + cfg.sl_buffer_pips * PIP
            riesgo = sl - entrada
            tp = entrada - cfg.rr * riesgo
        else:
            sl = min(r.h1_lo, r.low) - cfg.sl_buffer_pips * PIP
            riesgo = entrada - sl
            tp = entrada + cfg.rr * riesgo
        if riesgo <= 0:
            continue

        i0 = int(np.searchsorted(t1, entrada_ts, side="left"))
        i1 = min(i0 + max_bars, len(t1))
        if i0 >= len(t1):
            continue
        hh, ll = h1_[i0:i1], l1_[i0:i1]
        if corto:
            golpe_sl, golpe_tp = hh >= sl, ll <= tp
        else:
            golpe_sl, golpe_tp = ll <= sl, hh >= tp
        i_sl = int(np.argmax(golpe_sl)) if golpe_sl.any() else 10**9
        i_tp = int(np.argmax(golpe_tp)) if golpe_tp.any() else 10**9

        if i_sl == 10**9 and i_tp == 10**9:
            salida, motivo = m1["close"].to_numpy()[i1 - 1], "tiempo"
            i_fin = (i1 - i0) - 1
        elif i_sl <= i_tp:                    # empate en la misma M1 -> SL
            if i_sl == i_tp:
                ambiguas += 1
            salida, motivo, i_fin = sl, "SL", i_sl
        else:
            salida, motivo, i_fin = tp, "TP", i_tp

        bruto = (entrada - salida) if corto else (salida - entrada)
        neto_pips = bruto / PIP - cfg.coste_pips
        riesgo_pips = riesgo / PIP
        trades.append(dict(
            ts=r.ts, salida_ts=pd.Timestamp(t1[i0 + i_fin]),
            dir="corto" if corto else "largo", entrada=entrada, sl=sl, tp=tp,
            riesgo_pips=riesgo_pips, motivo=motivo,
            pips=neto_pips, R=neto_pips / riesgo_pips))
        libre_desde = t1[i0 + i_fin]

    return pd.DataFrame(trades), ambiguas


# ═══════════════════════════════════════════════════════════════════════════
#  METRICAS
# ═══════════════════════════════════════════════════════════════════════════
def metricas(tr: pd.DataFrame, riesgo_pct=1.0, capital=10000.0):
    if tr.empty:
        return {"operaciones": 0}
    gan = tr[tr.R > 0]
    per = tr[tr.R <= 0]
    eq, pico, maxdd = capital, capital, 0.0
    curva = []
    for R in tr["R"]:
        eq *= (1 + riesgo_pct / 100.0 * R)
        pico = max(pico, eq)
        maxdd = max(maxdd, (pico - eq) / pico)
        curva.append(eq)
    bruto_g = gan["R"].sum()
    bruto_p = -per["R"].sum()
    return {
        "operaciones": len(tr),
        "win rate %": round(100 * len(gan) / len(tr), 2),
        "R total": round(tr["R"].sum(), 2),
        "R medio": round(tr["R"].mean(), 4),
        "profit factor": round(bruto_g / bruto_p, 3) if bruto_p > 0 else float("inf"),
        "riesgo medio (pips)": round(tr["riesgo_pips"].mean(), 2),
        "riesgo mediano (pips)": round(tr["riesgo_pips"].median(), 2),
        "TP / SL / tiempo": f"{(tr.motivo=='TP').sum()} / {(tr.motivo=='SL').sum()} / {(tr.motivo=='tiempo').sum()}",
        f"equity final ({riesgo_pct}%/op)": round(eq, 2),
        "max drawdown %": round(100 * maxdd, 2),
        "_curva": curva,
    }
