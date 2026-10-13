"""CRT con entrada por retroceso de Fibonacci en M5.

El setup se identifica en la vela de referencia (H1/H4/D1) con las reglas de la
guia. La ENTRADA cambia: en vez de orden stop a mercado, se coloca una orden
LIMITADA en un retroceso de Fibonacci del impulso de reaccion, mirado en M5.

Para un CRT alcista:
   A = minimo del barrido (extremo de la Vela 2)
   B = maximo acumulado en M5 desde A, leido SIEMPRE de velas ya cerradas
   nivel de entrada = B - r*(B-A)      con r el retroceso (0.618 = 61,8%)
   SL  = A - colchon        (donde manda la guia: tras la mecha de manipulacion)
   TP  = extremo opuesto del rango de la Vela 1

Cuanto mas profundo el retroceso, mejor precio y menor riesgo, pero menos ordenes
se llenan. Ese es exactamente el compromiso que se mide aqui.
"""
import numpy as np, pandas as pd
from math import sqrt, erf
from crt_canonico import velas_ref, en_kz, pz, pf, KZ_FX, KZ_IDX

def setups(ref, cierre_estricto=True):
    hi, lo, cl = (ref[c].to_numpy() for c in ("high","low","close"))
    ini, fin = ref["ini"].to_numpy(), ref["fin"].to_numpy()
    out = []
    for i in range(1, len(ref)-1):
        r_hi, r_lo = hi[i-1], lo[i-1]
        rango = r_hi - r_lo
        if rango <= 0: continue
        b_lo, b_hi = lo[i] < r_lo, hi[i] > r_hi
        if b_lo == b_hi: continue
        if cierre_estricto and not (r_lo <= cl[i] <= r_hi): continue
        out.append(dict(largo=b_lo, r_hi=r_hi, r_lo=r_lo, rango=rango,
                        A=lo[i] if b_lo else hi[i],
                        ini3=ini[i+1], fin3=fin[i+1]))
    return pd.DataFrame(out)

def ejecuta_fib(sig, m5, m1, cfg, unit, coste, zonas):
    if sig.empty: return pd.DataFrame()
    T5 = m5["ts"].to_numpy(); H5 = m5["high"].to_numpy()
    L5 = m5["low"].to_numpy(); O5 = m5["open"].to_numpy()
    T = m1["ts"].to_numpy(); H = m1["high"].to_numpy()
    L = m1["low"].to_numpy(); C = m1["close"].to_numpy()
    out, libre, por_dia = [], np.datetime64("1970-01-01"), {}
    for r in sig.itertuples():
        i0 = int(np.searchsorted(T5, np.datetime64(pd.Timestamp(r.ini3))))
        i1 = int(np.searchsorted(T5, np.datetime64(pd.Timestamp(r.fin3)))) + 1
        if i0 >= len(T5) or i1 <= i0: continue
        if np.datetime64(pd.Timestamp(r.ini3)) < libre: continue
        A = r.A
        B = None; hecho = False
        for j in range(i0, min(i1, len(T5))):
            # nivel calculado con B de velas YA CERRADAS: nada de mirar al futuro
            if B is not None:
                leg = (B - A) if r.largo else (A - B)
                if leg >= cfg["min_leg"]*r.rango:
                    niv = B - cfg["fib"]*leg if r.largo else B + cfg["fib"]*leg
                    toca = (L5[j] <= niv) if r.largo else (H5[j] >= niv)
                    if toca:
                        e = min(niv, O5[j]) if r.largo else max(niv, O5[j])
                        ts_e = T5[j]
                        if cfg["killzone"] and not en_kz(ts_e, zonas): 
                            B = max(B, H5[j]) if r.largo else min(B, L5[j]); continue
                        dia = pd.Timestamp(ts_e).date()
                        if por_dia.get(dia,0) >= cfg["tope_dia"]:
                            B = max(B, H5[j]) if r.largo else min(B, L5[j]); continue
                        sl = A - cfg["buffer"]*unit if r.largo else A + cfg["buffer"]*unit
                        tp = r.r_hi if r.largo else r.r_lo
                        riesgo = abs(e-sl); premio = abs(tp-e)
                        # guardas contra rellenos degenerados: si el precio abre con
                        # hueco por debajo del nivel, la entrada puede caer pegada al
                        # stop y el riesgo se va a cero, lo que dispara la R a valores
                        # absurdos. Un stop asi no es operable.
                        if riesgo < max(cfg["min_riesgo_u"]*unit, 0.05*r.rango):
                            hecho = True; break
                        if riesgo<=0 or premio<=0 or premio/riesgo < cfg["min_rr"]:
                            hecho = True; break
                        if premio/riesgo > cfg["max_rr"]:
                            hecho = True; break
                        if not ((e>sl and tp>e) if r.largo else (e<sl and tp<e)):
                            hecho = True; break
                        k0 = int(np.searchsorted(T, ts_e))
                        k1 = min(k0 + cfg["max_horas"]*60, len(T))
                        if k0>=len(T) or k1<=k0: hecho=True; break
                        a_,b_ = H[k0:k1], L[k0:k1]
                        gsl,gtp = ((b_<=sl, a_>=tp) if r.largo else (a_>=sl, b_<=tp))
                        isl = int(np.argmax(gsl)) if gsl.any() else 10**9
                        itp = int(np.argmax(gtp)) if gtp.any() else 10**9
                        if isl==10**9 and itp==10**9: sal,mot,f = C[k1-1],"tiempo",(k1-k0)-1
                        elif isl<=itp: sal,mot,f = sl,"SL",isl
                        else: sal,mot,f = tp,"TP",itp
                        br = (sal-e) if r.largo else (e-sal)
                        out.append(dict(ts=ts_e, largo=r.largo, motivo=mot,
                                        rr=premio/riesgo, riesgo_u=riesgo/unit,
                                        bruto=(br/unit)/(riesgo/unit),
                                        R=(br/unit-coste)/(riesgo/unit)))
                        por_dia[dia] = por_dia.get(dia,0)+1
                        libre = T[min(k0+f, len(T)-1)]
                        hecho = True; break
            val = H5[j] if r.largo else L5[j]
            B = val if B is None else (max(B, val) if r.largo else min(B, val))
        if hecho: continue
    return pd.DataFrame(out)
