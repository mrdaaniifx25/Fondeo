"""Las dos confluencias que la guia dice que mas suben el win rate.

DAILY BIAS  (guia, seccion 8)
  "Identifica un CRT en el grafico diario... Con el bias definido por el CRT
   diario, baja a H4, H1 o M15 y busca UNICAMENTE CRTs en esa misma direccion."

CRT NESTED  (guia, seccion 9)
  "En H4 identificas una vela cuyo minimo ha sido liquidado y el precio ha
   reentrado. Ve al grafico de M15. Dentro del rango H4, busca un nuevo patron
   CRT. El stop va debajo del minimo del CRT M15; el target puede extenderse
   hasta el maximo del CRT H4."
  El atractivo es el stop: mucho mas ajustado, asi que el R:R sube mucho.
"""
import numpy as np, pandas as pd
from crt_canonico import velas_ref, en_kz

def bias_diario(m1):
    """CRT en D1 (hora de Nueva York). Devuelve el sesgo vigente en cada dia."""
    d = velas_ref(m1, 24, 1)
    hi, lo, cl = d.high.to_numpy(), d.low.to_numpy(), d.close.to_numpy()
    filas = []
    for i in range(1, len(d)-1):
        r_hi, r_lo = hi[i-1], lo[i-1]
        b_lo, b_hi = lo[i] < r_lo, hi[i] > r_hi
        if b_lo == b_hi: continue
        if not (r_lo <= cl[i] <= r_hi): continue      # cierre de vuelta dentro
        filas.append(dict(desde=d.ini.iloc[i+1], hasta=d.fin.iloc[i+1], alcista=b_lo))
    return pd.DataFrame(filas)

def bias_en(bias, ts):
    """Sesgo vigente en un instante. None si no hay CRT diario activo."""
    m = bias[(bias.desde <= ts) & (ts <= bias.hasta)]
    return None if m.empty else bool(m.alcista.iloc[0])

def entrada_nested(sig, m15, m1, cfg, unit, coste, zonas, bias=None):
    """Busca un CRT de M15 dentro de la Vela 3 del CRT de referencia."""
    if sig.empty: return pd.DataFrame()
    T15 = m15["ts"].to_numpy(); H15 = m15["high"].to_numpy()
    L15 = m15["low"].to_numpy(); C15 = m15["close"].to_numpy(); O15 = m15["open"].to_numpy()
    T = m1["ts"].to_numpy(); H = m1["high"].to_numpy()
    L = m1["low"].to_numpy(); C = m1["close"].to_numpy()
    out, libre, por_dia = [], np.datetime64("1970-01-01"), {}
    for r in sig.itertuples():
        if bias is not None:
            b = bias_en(bias, pd.Timestamp(r.ini3))
            if b is None or b != r.largo: continue     # solo a favor del CRT diario
        i0 = int(np.searchsorted(T15, np.datetime64(pd.Timestamp(r.ini3))))
        i1 = int(np.searchsorted(T15, np.datetime64(pd.Timestamp(r.fin3)))) + 1
        if i0 >= len(T15) or i1 <= i0 or np.datetime64(pd.Timestamp(r.ini3)) < libre: continue
        for j in range(max(i0,1), min(i1, len(T15)-1)):
            # CRT anidado: la vela M15 barre la anterior y cierra de vuelta dentro
            p_hi, p_lo = H15[j-1], L15[j-1]
            if r.largo:
                if not (L15[j] < p_lo and p_lo <= C15[j] <= p_hi): continue
                sw = L15[j]
            else:
                if not (H15[j] > p_hi and p_lo <= C15[j] <= p_hi): continue
                sw = H15[j]
            # el barrido anidado debe caer DENTRO de la zona de liquidez de la referencia
            if r.largo and not (sw <= r.r_lo + 0.5*r.rango): continue
            if (not r.largo) and not (sw >= r.r_hi - 0.5*r.rango): continue
            ts_e = T15[j+1]; e = O15[j+1]
            if cfg["killzone"] and not en_kz(ts_e, zonas): continue
            dia = pd.Timestamp(ts_e).date()
            if por_dia.get(dia,0) >= cfg["tope_dia"]: continue
            sl = sw - cfg["buffer"]*unit if r.largo else sw + cfg["buffer"]*unit
            tp = r.r_hi if r.largo else r.r_lo
            riesgo = abs(e-sl); premio = abs(tp-e)
            if riesgo < max(cfg["min_riesgo_u"]*unit, 0.02*r.rango): continue
            if premio <= 0 or premio/riesgo < cfg["min_rr"] or premio/riesgo > cfg["max_rr"]: continue
            if not ((e>sl and tp>e) if r.largo else (e<sl and tp<e)): continue
            k0 = int(np.searchsorted(T, np.datetime64(pd.Timestamp(ts_e))))
            k1 = min(k0 + cfg["max_horas"]*60, len(T))
            if k0 >= len(T) or k1 <= k0: continue
            a_,b_ = H[k0:k1], L[k0:k1]
            gsl,gtp = ((b_<=sl, a_>=tp) if r.largo else (a_>=sl, b_<=tp))
            isl = int(np.argmax(gsl)) if gsl.any() else 10**9
            itp = int(np.argmax(gtp)) if gtp.any() else 10**9
            if isl==10**9 and itp==10**9: sal,mot,f = C[k1-1],"tiempo",(k1-k0)-1
            elif isl<=itp: sal,mot,f = sl,"SL",isl
            else: sal,mot,f = tp,"TP",itp
            br = (sal-e) if r.largo else (e-sal)
            out.append(dict(ts=ts_e, largo=r.largo, motivo=mot, rr=premio/riesgo,
                            riesgo_u=riesgo/unit, bruto=(br/unit)/(riesgo/unit),
                            R=(br/unit-coste)/(riesgo/unit)))
            por_dia[dia] = por_dia.get(dia,0)+1
            libre = T[min(k0+f, len(T)-1)]
            break
    return pd.DataFrame(out)
