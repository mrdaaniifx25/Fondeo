"""ESTRATEGIA 3 - CRT + Order Block M15 (metodo de los videos).

Reglas extraidas de las 9 transcripciones:
  Rejilla H4 anclada a las 01:00 UTC-4 -> velas a las 01,05,09,13,17,21 UTC.
  Turtle soup H4 : la vela H4 en curso toma el extremo de la anterior y el
                   precio vuelve DENTRO del rango.
  Confirmacion H1: lo mismo en la vela H1 en curso (opcional).
  Order block M15: "la vela positiva cierra por encima de la ultima vela
                   negativa" -> disparador de entrada.
  Entrada        : apertura de la vela M15 SIGUIENTE al order block.
  SL             : extremo del turtle soup -/+ colchon.
  TP             : extremo opuesto del rango H4, o multiplo R fijo.
  Horario        : el autor opera de 02:30 a ~12:00 UTC-4 (06:30-16:00 UTC).

El interruptor `usar_ob` es el objeto del experimento: con el, es el metodo de
los videos; sin el, es el CRT Trade Planner. Todo lo demas identico.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd

PIP = 0.0001

@dataclass
class Config:
    ancla_h4: int = 1          # hora UTC de anclaje de la rejilla H4
    usar_ob: bool = True       # <-- variable del experimento
    ob_ref: str = "high"       # "high" u "open" de la ultima vela negativa
    usar_h1: bool = True       # exigir turtle soup tambien en H1
    tp_modo: str = "rango"     # "rango" (extremo opuesto) o "R" (multiplo fijo)
    tp_r: float = 2.0
    sl_buffer_pips: float = 1.0
    min_rr: float = 1.0
    max_rr: float = 12.0
    min_range_atr: float = 0.0
    hora_ini: float = 6.5      # UTC
    hora_fin: float = 16.0
    una_por_rango: bool = True
    max_espera: int = 16       # velas M15 de margen entre el sweep y el OB
    coste_pips: float = 1.2
    max_trade_horas: int = 48


def preparar(m1: pd.DataFrame, cfg: Config):
    g = m1.set_index("ts").resample("15min", label="left", closed="left")
    ch = g.agg(open=("open","first"), high=("high","max"),
               low=("low","min"), close=("close","last")).dropna().reset_index()

    org = pd.Timestamp("2020-01-01") + pd.Timedelta(hours=cfg.ancla_h4)
    h4 = m1.set_index("ts").resample("4h", origin=org, label="left", closed="left").agg(
        high=("high","max"), low=("low","min"), close=("close","last")).dropna().reset_index()
    tr = pd.concat([h4.high-h4.low, (h4.high-h4.close.shift(1)).abs(),
                    (h4.low-h4.close.shift(1)).abs()], axis=1).max(axis=1)
    h4["atr"] = tr.rolling(14).mean()
    h4["r_hi"], h4["r_lo"], h4["r_atr"] = h4.high.shift(1), h4.low.shift(1), h4.atr.shift(1)
    ch["h4_id"] = ch["ts"].dt.floor("4h", ) if cfg.ancla_h4 == 0 else \
                  (ch["ts"] - pd.Timedelta(hours=cfg.ancla_h4)).dt.floor("4h") + pd.Timedelta(hours=cfg.ancla_h4)
    ch = ch.merge(h4[["ts","r_hi","r_lo","r_atr"]].rename(columns={"ts":"h4_id"}), on="h4_id", how="left")

    h1 = m1.set_index("ts").resample("1h", label="left", closed="left").agg(
        high=("high","max"), low=("low","min")).dropna().reset_index()
    h1["p_hi"], h1["p_lo"] = h1.high.shift(1), h1.low.shift(1)
    ch["h1_id"] = ch["ts"].dt.floor("1h")
    ch = ch.merge(h1[["ts","p_hi","p_lo"]].rename(columns={"ts":"h1_id"}), on="h1_id", how="left")

    # extremos acumulados de la vela H4 / H1 en curso
    for pref, key in (("h4","h4_id"), ("h1","h1_id")):
        ch[f"{pref}_run_hi"] = ch.groupby(key)["high"].cummax()
        ch[f"{pref}_run_lo"] = ch.groupby(key)["low"].cummin()
    return ch


def senales(ch: pd.DataFrame, cfg: Config):
    ts = ch["ts"].to_numpy()
    op, hi = ch["open"].to_numpy(), ch["high"].to_numpy()
    lo, cl = ch["low"].to_numpy(), ch["close"].to_numpy()
    rhi, rlo, ratr = ch["r_hi"].to_numpy(), ch["r_lo"].to_numpy(), ch["r_atr"].to_numpy()
    p_hi, p_lo = ch["p_hi"].to_numpy(), ch["p_lo"].to_numpy()
    h4hi, h4lo = ch["h4_run_hi"].to_numpy(), ch["h4_run_lo"].to_numpy()
    h1hi, h1lo = ch["h1_run_hi"].to_numpy(), ch["h1_run_lo"].to_numpy()
    h4id = ch["h4_id"].to_numpy()
    horas = pd.DatetimeIndex(ch["ts"]).hour + pd.DatetimeIndex(ch["ts"]).minute/60.0

    # order block M15: vela positiva que cierra por encima de la ultima negativa
    ref_bear = np.full(len(ch), np.nan); ref_bull = np.full(len(ch), np.nan)
    ub = un = np.nan
    for i in range(len(ch)):
        ref_bear[i], ref_bull[i] = ub, un
        if cl[i] < op[i]:  ub = hi[i] if cfg.ob_ref == "high" else op[i]
        elif cl[i] > op[i]: un = lo[i] if cfg.ob_ref == "high" else op[i]
    ob_alc = (cl > op) & ~np.isnan(ref_bear) & (cl > ref_bear)
    ob_baj = (cl < op) & ~np.isnan(ref_bull) & (cl < ref_bull)

    emb = dict(velas=len(ch), en_horario=0, ts_h4=0, ts_h4_h1=0, con_ob=0, senales=0)
    out, hecho_rango, espera = [], set(), {}

    for i in range(len(ch)-1):
        if np.isnan(rhi[i]) or np.isnan(ratr[i]): continue
        if not (cfg.hora_ini <= horas[i] < cfg.hora_fin): continue
        emb["en_horario"] += 1
        if (rhi[i]-rlo[i]) < cfg.min_range_atr*ratr[i]: continue

        for largo in (True, False):
            # turtle soup H4: barrido del extremo y precio de vuelta dentro
            if largo:
                ts4 = (h4lo[i] < rlo[i]) and (rlo[i] < cl[i] <= rhi[i])
                ts1 = (not cfg.usar_h1) or ((h1lo[i] < p_lo[i]) and (cl[i] > p_lo[i]))
                obk = ob_alc[i]
            else:
                ts4 = (h4hi[i] > rhi[i]) and (rlo[i] <= cl[i] < rhi[i])
                ts1 = (not cfg.usar_h1) or ((h1hi[i] > p_hi[i]) and (cl[i] < p_hi[i]))
                obk = ob_baj[i]
            if not ts4: continue
            emb["ts_h4"] += 1
            if not ts1: continue
            emb["ts_h4_h1"] += 1

            clave = (h4id[i], largo)
            if cfg.una_por_rango and clave in hecho_rango: continue
            # margen entre el primer turtle soup del rango y el order block
            espera.setdefault(clave, i)
            if cfg.usar_ob:
                if not obk: continue
                if i - espera[clave] > cfg.max_espera: continue
                emb["con_ob"] += 1

            entrada = op[i+1] if cfg.usar_ob else cl[i]     # power de la siguiente vela
            swpx = h4lo[i] if largo else h4hi[i]
            sl = swpx - cfg.sl_buffer_pips*PIP if largo else swpx + cfg.sl_buffer_pips*PIP
            riesgo = abs(entrada-sl)
            if riesgo <= 0: continue
            tp = (rhi[i] if largo else rlo[i]) if cfg.tp_modo == "rango" else \
                 (entrada + cfg.tp_r*riesgo if largo else entrada - cfg.tp_r*riesgo)
            rr = abs(tp-entrada)/riesgo
            coher = (entrada > sl and tp > entrada) if largo else (entrada < sl and tp < entrada)
            if not coher or rr < cfg.min_rr or rr > cfg.max_rr: continue
            emb["senales"] += 1
            hecho_rango.add(clave)
            out.append(dict(ts=ts[i], largo=largo, entrada=entrada, sl=sl, tp=tp,
                            rr=rr, riesgo_pips=riesgo/PIP))
            break
    return pd.DataFrame(out), emb


def simular(sig, m1, cfg):
    if sig.empty: return sig, 0
    t1 = m1["ts"].to_numpy(); HH = m1["high"].to_numpy()
    LL = m1["low"].to_numpy(); CC = m1["close"].to_numpy()
    filas, libre, amb = [], np.datetime64("1970-01-01"), 0
    for r in sig.itertuples():
        ets = np.datetime64(pd.Timestamp(r.ts) + pd.Timedelta(minutes=15))
        if ets < libre: continue
        i0 = int(np.searchsorted(t1, ets)); i1 = min(i0+cfg.max_trade_horas*60, len(t1))
        if i0 >= len(t1) or i1 <= i0: continue
        a, b = HH[i0:i1], LL[i0:i1]
        gsl, gtp = ((b<=r.sl, a>=r.tp) if r.largo else (a>=r.sl, b<=r.tp))
        isl = int(np.argmax(gsl)) if gsl.any() else 10**9
        itp = int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl==10**9 and itp==10**9: sal, mot, ifin = CC[i1-1], "tiempo", (i1-i0)-1
        elif isl<=itp:
            if isl==itp: amb += 1
            sal, mot, ifin = r.sl, "SL", isl
        else: sal, mot, ifin = r.tp, "TP", itp
        bruto = (sal-r.entrada) if r.largo else (r.entrada-sal)
        neto = bruto/PIP - cfg.coste_pips
        filas.append(dict(ts=r.ts, dir="largo" if r.largo else "corto", entrada=r.entrada,
                          rr=r.rr, riesgo_pips=r.riesgo_pips, motivo=mot,
                          pips=neto, R=neto/r.riesgo_pips))
        libre = t1[i0+ifin]
    return pd.DataFrame(filas), amb


def metricas(tr):
    if tr.empty: return {"operaciones": 0}
    gan, per = tr[tr.R>0], tr[tr.R<=0]
    eq, pico, dd = 10000.0, 10000.0, 0.0
    for R in tr["R"]:
        eq *= (1+0.01*R); pico = max(pico, eq); dd = max(dd, (pico-eq)/pico)
    bg, bp = gan.R.sum(), -per.R.sum()
    return {"operaciones": len(tr), "win rate %": round(100*len(gan)/len(tr),2),
            "R total": round(tr.R.sum(),2), "R medio": round(tr.R.mean(),4),
            "profit factor": round(bg/bp,3) if bp>0 else float("inf"),
            "R:R medio": round(tr.rr.mean(),2),
            "riesgo medio": round(tr.riesgo_pips.mean(),2),
            "max drawdown %": round(100*dd,2)}
