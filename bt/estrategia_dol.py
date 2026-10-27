"""CRT + order block + DOL. El DOL puede actuar como FILTRO de direccion,
como OBJETIVO de la operacion, o ambas cosas."""
from dataclasses import dataclass
import numpy as np, pandas as pd
PIP = 0.0001

@dataclass
class C:
    usar_ob: bool = True
    usar_h1: bool = True
    dol_filtro: bool = False      # solo operar si el DOL apunta en la direccion
    dol_target: bool = False      # objetivo = el DOL en vez de un multiplo R
    dol_marcos: tuple = ("D","W","M")
    tp_r: float = 3.0
    min_rr: float = 0.0
    max_rr: float = 99.0
    sl_buffer_pips: float = 1.0
    hora_ini: float = 6.5
    hora_fin: float = 16.0
    una_por_rango: bool = True
    max_espera: int = 16
    coste_pips: float = 1.2
    max_trade_horas: int = 168

def senales(ch, cfg: C):
    op,hi,lo,cl = (ch[c].to_numpy() for c in ("open","high","low","close"))
    rhi,rlo = ch["r_hi"].to_numpy(), ch["r_lo"].to_numpy()
    p_hi,p_lo = ch["p_hi"].to_numpy(), ch["p_lo"].to_numpy()
    h4hi,h4lo = ch["h4_run_hi"].to_numpy(), ch["h4_run_lo"].to_numpy()
    h1hi,h1lo = ch["h1_run_hi"].to_numpy(), ch["h1_run_lo"].to_numpy()
    h4id = ch["h4_id"].to_numpy()
    dup, ddn = ch["dol_up"].to_numpy(), ch["dol_dn"].to_numpy()
    dupt, ddnt = ch["dol_up_tf"].to_numpy(), ch["dol_dn_tf"].to_numpy()
    ts = ch["ts"].to_numpy()
    idx = pd.DatetimeIndex(ch["ts"]); horas = idx.hour + idx.minute/60.0

    ref_bear = np.full(len(ch), np.nan); ref_bull = np.full(len(ch), np.nan)
    ub = un = np.nan
    for i in range(len(ch)):
        ref_bear[i], ref_bull[i] = ub, un
        if cl[i] < op[i]: ub = hi[i]
        elif cl[i] > op[i]: un = lo[i]
    ob_alc = (cl>op) & ~np.isnan(ref_bear) & (cl>ref_bear)
    ob_baj = (cl<op) & ~np.isnan(ref_bull) & (cl<ref_bull)

    out, hecho, espera = [], set(), {}
    emb = dict(ts_h4h1=0, con_ob=0, dol_ok=0, senales=0)
    for i in range(len(ch)-1):
        if np.isnan(rhi[i]): continue
        if not (cfg.hora_ini <= horas[i] < cfg.hora_fin): continue
        for largo in (True, False):
            if largo:
                ts4 = (h4lo[i] < rlo[i]) and (rlo[i] < cl[i] <= rhi[i])
                ts1 = (not cfg.usar_h1) or ((h1lo[i] < p_lo[i]) and (cl[i] > p_lo[i]))
                obk = ob_alc[i]
            else:
                ts4 = (h4hi[i] > rhi[i]) and (rlo[i] <= cl[i] < rhi[i])
                ts1 = (not cfg.usar_h1) or ((h1hi[i] > p_hi[i]) and (cl[i] < p_hi[i]))
                obk = ob_baj[i]
            if not (ts4 and ts1): continue
            emb["ts_h4h1"] += 1
            clave = (h4id[i], largo)
            if cfg.una_por_rango and clave in hecho: continue
            espera.setdefault(clave, i)
            if cfg.usar_ob:
                if not obk or i-espera[clave] > cfg.max_espera: continue
                emb["con_ob"] += 1

            # --- DOL ---
            objetivo = dup[i] if largo else ddn[i]
            marco_ok = (dupt[i] if largo else ddnt[i]) in cfg.dol_marcos
            contrario = ddn[i] if largo else dup[i]
            if cfg.dol_filtro:
                if np.isnan(objetivo) or not marco_ok: continue
                # el objetivo a favor debe estar mas cerca que el contrario
                if not np.isnan(contrario):
                    d_fav = abs(objetivo-cl[i]); d_con = abs(contrario-cl[i])
                    if d_fav > d_con: continue
                emb["dol_ok"] += 1

            entrada = op[i+1] if cfg.usar_ob else cl[i]
            swpx = h4lo[i] if largo else h4hi[i]
            sl = swpx - cfg.sl_buffer_pips*PIP if largo else swpx + cfg.sl_buffer_pips*PIP
            riesgo = abs(entrada-sl)
            if riesgo <= 0: continue
            if cfg.dol_target:
                if np.isnan(objetivo) or not marco_ok: continue
                tp = objetivo
            else:
                tp = entrada + cfg.tp_r*riesgo if largo else entrada - cfg.tp_r*riesgo
            rr = abs(tp-entrada)/riesgo
            coher = (entrada > sl and tp > entrada) if largo else (entrada < sl and tp < entrada)
            if not coher or rr < cfg.min_rr or rr > cfg.max_rr: continue
            emb["senales"] += 1; hecho.add(clave)
            out.append(dict(ts=ts[i], largo=largo, entrada=entrada, sl=sl, tp=tp,
                            rr=rr, riesgo_pips=riesgo/PIP))
            break
    return pd.DataFrame(out), emb

def simular(sig, m1, cfg):
    if sig.empty: return sig
    t1=m1["ts"].to_numpy(); HH=m1["high"].to_numpy(); LL=m1["low"].to_numpy(); CC=m1["close"].to_numpy()
    filas, libre = [], np.datetime64("1970-01-01")
    for r in sig.itertuples():
        ets = np.datetime64(pd.Timestamp(r.ts)+pd.Timedelta(minutes=15))
        if ets < libre: continue
        i0=int(np.searchsorted(t1,ets)); i1=min(i0+cfg.max_trade_horas*60,len(t1))
        if i0>=len(t1) or i1<=i0: continue
        a,b=HH[i0:i1],LL[i0:i1]
        gsl,gtp=((b<=r.sl,a>=r.tp) if r.largo else (a>=r.sl,b<=r.tp))
        isl=int(np.argmax(gsl)) if gsl.any() else 10**9
        itp=int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl==10**9 and itp==10**9: sal,mot,ifin=CC[i1-1],"tiempo",(i1-i0)-1
        elif isl<=itp: sal,mot,ifin=r.sl,"SL",isl
        else: sal,mot,ifin=r.tp,"TP",itp
        br=(sal-r.entrada) if r.largo else (r.entrada-sal)
        neto=br/PIP-cfg.coste_pips
        filas.append(dict(ts=r.ts, dir="largo" if r.largo else "corto", entrada=r.entrada,
                          rr=r.rr, riesgo_pips=r.riesgo_pips, motivo=mot,
                          pips=neto, R=neto/r.riesgo_pips))
        libre=t1[i0+ifin]
    return pd.DataFrame(filas)
