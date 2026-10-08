"""CRT canonico segun la guia de Rubén Villahermosa (tradingwyckoff.com).

Diferencias corregidas respecto a mi implementacion anterior:
  1 REJILLA: la vela de referencia se ancla a la 01:00 de NUEVA YORK (con cambio
    de hora), no a la 01:00 UTC. La guia dice "velas 4H que cierran a la 1am y
    5am EST"; 1am EST = 7:00 CET = 6:00 UTC en invierno. Yo usaba 01:00 UTC.
  2 ENTRADA EN VELA 3: la guia llama "Error #1, el mayor destructor de cuentas"
    a entrar en la Vela 2. La confirmacion llega con la Vela 3.
  3 ORDEN STOP, no a mercado: Buy Stop en el maximo de la Vela 2 (agresiva) o de
    la Vela 3 (conservadora).
  4 CIERRE DE LA VELA 2 dentro del rango (interpretacion estricta).
  5 KILLZONES discretas en CET, excluyendo el almuerzo europeo 11:00-13:00.
  6 R:R minimo 1.5, no 1.0.
  7 MITIGACION: una zona solo vale la primera vez.
  8 Tope de 2-3 operaciones al dia.
"""
import numpy as np, pandas as pd
from math import sqrt, erf

# killzones en hora CET (Europe/Madrid), de la guia
KZ_FX  = [(8.0,11.0), (13.0,16.0), (16.0,18.0)]        # Londres, NY forex, London Close
KZ_IDX = [(8.0,11.0), (15.5,17.0), (16.0,18.0)]        # Londres, NY indices, London Close

def velas_ref(m1, tf_horas, ancla_ny=1):
    """Velas de referencia ancladas a la hora local de Nueva York."""
    ny = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York")
    d = m1.copy()
    d["ny"] = ny.tz_localize(None)
    org = pd.Timestamp("2020-01-01") + pd.Timedelta(hours=ancla_ny)
    d["id"] = d["ny"].dt.floor(f"{tf_horas}h") if ancla_ny == 0 else \
              (d["ny"] - pd.Timedelta(hours=ancla_ny)).dt.floor(f"{tf_horas}h") + pd.Timedelta(hours=ancla_ny)
    g = d.groupby("id").agg(open=("open","first"), high=("high","max"),
                            low=("low","min"), close=("close","last"),
                            ini=("ts","min"), fin=("ts","max"), n=("ts","size")).reset_index()
    return g[g.n >= tf_horas*60*0.5].reset_index(drop=True)

def en_kz(ts_utc, zonas):
    ce = pd.Timestamp(ts_utc).tz_localize("UTC").tz_convert("Europe/Madrid")
    h = ce.hour + ce.minute/60
    return any(a <= h < b for a,b in zonas)

def senales(ref, cfg):
    """Recorre las velas de referencia buscando el patron de 3 velas."""
    hi, lo, op, cl = (ref[c].to_numpy() for c in ("high","low","open","close"))
    ini, fin = ref["ini"].to_numpy(), ref["fin"].to_numpy()
    out = []
    for i in range(1, len(ref)-1):
        r_hi, r_lo = hi[i-1], lo[i-1]              # Vela 1: el rango
        rango = r_hi - r_lo
        if rango <= 0: continue
        # Vela 2: liquidacion
        barre_lo = lo[i] < r_lo
        barre_hi = hi[i] > r_hi
        if barre_lo == barre_hi: continue           # ninguno o los dos: se descarta
        largo = barre_lo
        # interpretacion estricta: el CUERPO de la vela 2 cierra dentro del rango
        if cfg["cierre_estricto"] and not (r_lo <= cl[i] <= r_hi): continue
        # Vela 3: donde vive la orden
        j = i + 1
        disparo = hi[i] if cfg["entrada"] == "v2" else None   # conservadora se fija dentro
        sw = lo[i] if largo else hi[i]                        # extremo del barrido
        out.append(dict(k=i, j=j, largo=largo, r_hi=r_hi, r_lo=r_lo,
                        v2_hi=hi[i], v2_lo=lo[i], sweep=sw,
                        ini3=ini[j], fin3=fin[j], rango=rango))
    return pd.DataFrame(out)

def ejecuta(sig, m1, cfg, unit, coste, zonas):
    """Coloca la orden stop durante la Vela 3 y resuelve sobre M1."""
    if sig.empty: return pd.DataFrame()
    T = m1["ts"].to_numpy(); H = m1["high"].to_numpy()
    L = m1["low"].to_numpy(); C = m1["close"].to_numpy(); O = m1["open"].to_numpy()
    out, libre, por_dia = [], np.datetime64("1970-01-01"), {}
    for r in sig.itertuples():
        i0 = int(np.searchsorted(T, np.datetime64(pd.Timestamp(r.ini3))))
        i1 = int(np.searchsorted(T, np.datetime64(pd.Timestamp(r.fin3)))) + 1
        if i0 >= len(T) or i1 <= i0: continue
        if np.datetime64(pd.Timestamp(r.ini3)) < libre: continue
        niv = r.v2_hi if r.largo else r.v2_lo       # disparo agresivo: extremo de Vela 2
        if cfg["entrada"] == "v3":
            # conservadora: maximo/minimo de la primera vela de reaccion dentro de Vela 3.
            # Se aproxima con el extremo de la primera hora de la Vela 3.
            k = min(i0+60, i1)
            niv = H[i0:k].max() if r.largo else L[i0:k].min()
            i0 = k
            if i0 >= i1: continue
        # buscar el disparo de la orden stop dentro de la Vela 3
        g = (H[i0:i1] >= niv) if r.largo else (L[i0:i1] <= niv)
        if not g.any(): continue
        it = i0 + int(np.argmax(g))
        e = max(niv, O[it]) if r.largo else min(niv, O[it])   # hueco: peor precio
        ts_e = T[it]
        if cfg["killzone"] and not en_kz(ts_e, zonas): continue
        dia = pd.Timestamp(ts_e).date()
        if por_dia.get(dia, 0) >= cfg["tope_dia"]: continue
        sl = r.sweep - cfg["buffer"]*unit if r.largo else r.sweep + cfg["buffer"]*unit
        tp = r.r_hi if r.largo else r.r_lo
        riesgo = abs(e-sl); premio = abs(tp-e)
        if riesgo <= 0 or premio <= 0: continue
        if premio/riesgo < cfg["min_rr"]: continue
        if not ((e > sl and tp > e) if r.largo else (e < sl and tp < e)): continue
        i2 = min(it + cfg["max_horas"]*60, len(T))
        a, b = H[it:i2], L[it:i2]
        gsl, gtp = ((b <= sl, a >= tp) if r.largo else (a >= sl, b <= tp))
        isl = int(np.argmax(gsl)) if gsl.any() else 10**9
        itp = int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl == 10**9 and itp == 10**9: sal, mot, f = C[i2-1], "tiempo", (i2-it)-1
        elif isl <= itp: sal, mot, f = sl, "SL", isl
        else: sal, mot, f = tp, "TP", itp
        br = (sal-e) if r.largo else (e-sal)
        out.append(dict(ts=ts_e, largo=r.largo, motivo=mot, rr=premio/riesgo,
                        riesgo_u=riesgo/unit, bruto=(br/unit)/(riesgo/unit),
                        R=(br/unit - coste)/(riesgo/unit)))
        por_dia[dia] = por_dia.get(dia, 0) + 1
        libre = T[min(it+f, len(T)-1)]
    return pd.DataFrame(out)

def pz(x):
    n = len(x)
    if n < 3: return 0.0, 1.0
    se = x.std(ddof=1)/sqrt(n); z = x.mean()/se if se > 0 else 0.0
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

def pf(R):
    g, p = R[R > 0].sum(), -R[R <= 0].sum()
    return g/p if p > 0 else float("inf")
