"""ESTRATEGIA 2 - CRT Trade Planner (nico66fx), modo Intra.

Reglas leidas del Pine v6:
  Rango  = ultima vela H4 YA CERRADA (high/low). Filtro: alto del rango >=
           minRangeATR x ATR(14) de H4.
  Barrido= la vela del grafico excede rangeHigh (sesgo corto) o rangeLow
           (sesgo largo). Con reArm, un barrido mas profundo mueve el extremo.
  Confirm= una vela del grafico CIERRA de vuelta dentro del rango.
  Entrada= ese cierre.
  SL     = mecha del barrido -/+ slBufferATR x ATR H4.
  TP     = extremo OPUESTO del rango.
  Filtros= R:R minimo, kill zone, una operacion a la vez, una direccion por
           rango, tope de senales por dia.

Diferencia clave con la estrategia 1: el R:R NO es fijo. Depende de donde caiga
el cierre dentro del rango, asi que hay que mirar su distribucion.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd

PIP = 0.0001

@dataclass
class Config:
    htf_horas: int = 4
    chart: str = "15min"
    min_rr: float = 1.0
    sl_buffer_atr: float = 0.50
    min_range_atr: float = 0.50
    one_trade: bool = True
    one_dir: bool = True
    re_arm: bool = True
    only_kz: bool = True
    kz: tuple = ((7, 0, 10, 0), (12, 30, 15, 0))   # (h,m,h,m) en kz_tz
    kz_tz: str = "UTC"
    daily_cap: int = 2
    coste_pips: float = 1.2
    max_trade_horas: int = 72


def marcos(m1: pd.DataFrame, cfg: Config):
    """Vela del grafico + rango H4 ya cerrado alineado a cada vela."""
    g = m1.set_index("ts").resample(cfg.chart, label="left", closed="left")
    ch = g.agg(open=("open","first"), high=("high","max"),
               low=("low","min"), close=("close","last")).dropna().reset_index()

    regla = f"{cfg.htf_horas}h"
    h = m1.set_index("ts").resample(regla, label="left", closed="left")
    htf = h.agg(high=("high","max"), low=("low","min"),
                close=("close","last")).dropna().reset_index()

    # ATR(14) de H4 sobre velas cerradas
    tr = pd.concat([
        htf.high - htf.low,
        (htf.high - htf.close.shift(1)).abs(),
        (htf.low  - htf.close.shift(1)).abs()], axis=1).max(axis=1)
    htf["atr"] = tr.rolling(14).mean()

    # La vela HTF k usa el rango de la vela k-1 (patron [1] + lookahead_on).
    htf["r_hi"] = htf["high"].shift(1)
    htf["r_lo"] = htf["low"].shift(1)
    htf["r_atr"] = htf["atr"].shift(1)

    ch["htf_id"] = ch["ts"].dt.floor(regla)
    ch = ch.merge(htf[["ts","r_hi","r_lo","r_atr"]].rename(columns={"ts":"htf_id"}),
                  on="htf_id", how="left")
    return ch


def _en_kz(ts: pd.Series, cfg: Config) -> np.ndarray:
    loc = pd.DatetimeIndex(ts).tz_localize("UTC").tz_convert(cfg.kz_tz)
    mins = loc.hour * 60 + loc.minute
    out = np.zeros(len(ts), dtype=bool)
    for h1, m1_, h2, m2 in cfg.kz:
        out |= (mins >= h1*60+m1_) & (mins < h2*60+m2)
    return out


def senales(ch: pd.DataFrame, cfg: Config):
    """Maquina de estados del rango, vela a vela. Devuelve las senales y el embudo."""
    ts   = ch["ts"].to_numpy()
    hi   = ch["high"].to_numpy();  lo = ch["low"].to_numpy()
    cl   = ch["close"].to_numpy()
    rhi  = ch["r_hi"].to_numpy();  rlo = ch["r_lo"].to_numpy()
    ratr = ch["r_atr"].to_numpy()
    htf_id = ch["htf_id"].to_numpy()
    kz   = _en_kz(ch["ts"], cfg) if cfg.only_kz else np.ones(len(ch), dtype=bool)
    dia  = pd.DatetimeIndex(ch["ts"]).normalize().to_numpy()

    swept_hi = swept_lo = False
    sw_hi_px = sw_lo_px = np.nan
    dir_done = False
    dia_actual = None; n_dia = 0
    htf_actual = None

    emb = dict(velas=len(ch), rango_valido=0, barridos=0, cierres_dentro=0,
               en_kz=int(kz.sum()), pasa_rr=0, senales=0)
    out = []

    for i in range(len(ch)):
        if np.isnan(rhi[i]) or np.isnan(ratr[i]):
            continue
        if htf_id[i] != htf_actual:                 # nueva vela H4 -> reinicio
            htf_actual = htf_id[i]
            swept_hi = swept_lo = False
            sw_hi_px = sw_lo_px = np.nan
            dir_done = False
        if dia[i] != dia_actual:
            dia_actual = dia[i]; n_dia = 0

        rango_ok = (rhi[i] - rlo[i]) >= cfg.min_range_atr * ratr[i]
        if rango_ok:
            emb["rango_valido"] += 1

        # --- barrido (estado vivo, leido ANTES de mutarlo) ---
        era_hi, era_lo = swept_hi, swept_lo
        if hi[i] > rhi[i]:
            if not swept_hi:
                swept_hi, sw_hi_px = True, hi[i]
            elif cfg.re_arm and hi[i] > sw_hi_px:
                sw_hi_px = hi[i]
        if lo[i] < rlo[i]:
            if not swept_lo:
                swept_lo, sw_lo_px = True, lo[i]
            elif cfg.re_arm and lo[i] < sw_lo_px:
                sw_lo_px = lo[i]
        if (swept_hi and not era_hi) or (swept_lo and not era_lo):
            emb["barridos"] += 1

        # --- confirmacion: cierre de vuelta dentro ---
        back_lo = swept_lo and rlo[i] < cl[i] <= rhi[i]
        back_hi = swept_hi and rlo[i] <= cl[i] < rhi[i]
        if back_lo or back_hi:
            emb["cierres_dentro"] += 1

        puerta = (rango_ok and kz[i] and (not dir_done or not cfg.one_dir)
                  and (cfg.daily_cap == 0 or n_dia < cfg.daily_cap))
        if not puerta:
            continue

        for largo, activo in ((True, back_lo), (False, back_hi)):
            if not activo:
                continue
            entrada = cl[i]
            swpx = sw_lo_px if largo else sw_hi_px
            if np.isnan(swpx):
                continue
            sl = swpx - cfg.sl_buffer_atr*ratr[i] if largo else swpx + cfg.sl_buffer_atr*ratr[i]
            tp = rhi[i] if largo else rlo[i]
            riesgo = abs(entrada - sl); premio = abs(tp - entrada)
            if riesgo <= 0:
                continue
            coher = (rlo[i] <= entrada <= rhi[i]) and (
                (entrada > sl and tp > entrada) if largo else (entrada < sl and tp < entrada))
            rr = premio / riesgo
            if not coher:
                continue
            if rr < cfg.min_rr:
                continue
            emb["pasa_rr"] += 1; emb["senales"] += 1
            out.append(dict(ts=ts[i], largo=largo, entrada=entrada, sl=sl, tp=tp,
                            riesgo_pips=riesgo/PIP, rr=rr))
            dir_done = True; n_dia += 1
            break

    return pd.DataFrame(out), emb


def simular(sig: pd.DataFrame, m1: pd.DataFrame, cfg: Config):
    """Resuelve cada plan sobre velas M1 posteriores al cierre de la senal."""
    if sig.empty:
        return sig, 0
    t1 = m1["ts"].to_numpy(); HH = m1["high"].to_numpy()
    LL = m1["low"].to_numpy(); CC = m1["close"].to_numpy()
    paso = pd.Timedelta(cfg.chart)
    filas, libre, amb = [], np.datetime64("1970-01-01"), 0

    for r in sig.itertuples():
        ets = np.datetime64(pd.Timestamp(r.ts) + paso)
        if cfg.one_trade and ets < libre:
            continue
        i0 = int(np.searchsorted(t1, ets)); i1 = min(i0 + cfg.max_trade_horas*60, len(t1))
        if i0 >= len(t1) or i1 <= i0:
            continue
        a, b = HH[i0:i1], LL[i0:i1]
        gsl, gtp = ((b <= r.sl, a >= r.tp) if r.largo else (a >= r.sl, b <= r.tp))
        isl = int(np.argmax(gsl)) if gsl.any() else 10**9
        itp = int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl == 10**9 and itp == 10**9:
            sal, mot, ifin = CC[i1-1], "tiempo", (i1-i0)-1
        elif isl <= itp:
            if isl == itp: amb += 1
            sal, mot, ifin = r.sl, "SL", isl
        else:
            sal, mot, ifin = r.tp, "TP", itp
        bruto = (sal - r.entrada) if r.largo else (r.entrada - sal)
        neto = bruto/PIP - cfg.coste_pips
        filas.append(dict(ts=r.ts, salida_ts=pd.Timestamp(t1[i0+ifin]),
                          dir="largo" if r.largo else "corto", entrada=r.entrada,
                          sl=r.sl, tp=r.tp, rr=r.rr, riesgo_pips=r.riesgo_pips,
                          motivo=mot, pips=neto, R=neto/r.riesgo_pips))
        libre = t1[i0+ifin]
    return pd.DataFrame(filas), amb


def metricas(tr: pd.DataFrame, riesgo_pct=1.0, capital=10000.0):
    if tr.empty:
        return {"operaciones": 0}
    gan, per = tr[tr.R > 0], tr[tr.R <= 0]
    eq, pico, dd, curva = capital, capital, 0.0, []
    for R in tr["R"]:
        eq *= (1 + riesgo_pct/100.0 * R)
        pico = max(pico, eq); dd = max(dd, (pico-eq)/pico); curva.append(eq)
    bg, bp = gan["R"].sum(), -per["R"].sum()
    return {"operaciones": len(tr),
            "win rate %": round(100*len(gan)/len(tr), 2),
            "R total": round(tr["R"].sum(), 2),
            "R medio": round(tr["R"].mean(), 4),
            "profit factor": round(bg/bp, 3) if bp > 0 else float("inf"),
            "R:R medio del plan": round(tr["rr"].mean(), 2),
            "riesgo medio (pips)": round(tr["riesgo_pips"].mean(), 2),
            "TP / SL / tiempo": f"{(tr.motivo=='TP').sum()} / {(tr.motivo=='SL').sum()} / {(tr.motivo=='tiempo').sum()}",
            "equity final": round(eq, 2),
            "max drawdown %": round(100*dd, 2),
            "_curva": curva}
