"""Verificacion independiente de crt_fib.py.

Reimplementacion de la MISMA especificacion con otra estructura: velas diarias
por agrupacion directa de fechas de Nueva York, busqueda de setups vectorizada,
y ejecucion con maquina de estados explicita escrita de cero. Si las dos
implementaciones coinciden operacion por operacion, el motor esta bien.

Especificacion (D1 de referencia, Fibonacci 50% en M5):
  V1 = vela diaria i-1     V2 = vela diaria i (cerrada)   V3 = vela diaria i+1
  alcista si  min(V2) < min(V1)  y  min(V1) <= cierre(V2) <= max(V1)
  A = min(V2);  B = maximo M5 acumulado en V3 leido de velas ya cerradas
  entrada limitada en  B - 0.5*(B-A)   si  B-A >= 0.20 * rango(V1)
  SL = A - 1 tick        TP = max(V1)
  guardas: riesgo >= max(3 ticks, 5% del rango), 1.5 <= R:R <= 15
  killzone en hora de Madrid, tope 3 al dia, vida maxima 48 h
"""
import numpy as np, pandas as pd

FIB, MIN_LEG, BUF = 0.50, 0.20, 1.0
MIN_RR, MAX_RR, MIN_RIESGO_T, MIN_RIESGO_R = 1.5, 15.0, 3.0, 0.05
TOPE_DIA, MAX_H = 3, 48
VENTANAS = [(8.0, 11.0), (13.0, 16.0), (16.0, 18.0)]

def diarias(m1):
    """Velas D1 por fecha de Nueva York, agrupando directamente."""
    ny = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert("America/New_York")
    # el dia de mercado arranca a la 01:00 NY, asi que se resta una hora
    clave = (ny - pd.Timedelta(hours=1)).date
    t = m1.assign(k=clave)
    g = t.groupby("k", sort=True).agg(hi=("high","max"), lo=("low","min"),
                                      ci=("close","last"), t0=("ts","min"),
                                      t1=("ts","max"), n=("ts","size"))
    return g[g.n >= 720].reset_index()      # medio dia de velas minimo

def busca_setups(d):
    """Vectorizado: compara cada vela con la anterior y con la siguiente."""
    hi, lo, ci = d.hi.values, d.lo.values, d.ci.values
    v1h, v1l = hi[:-2], lo[:-2]                 # V1
    v2l, v2h, v2c = lo[1:-1], hi[1:-1], ci[1:-1]  # V2
    rango = v1h - v1l
    alc = (v2l < v1l) & (v2h <= v1h)
    baj = (v2h > v1h) & (v2l >= v1l)
    dentro = (v2c >= v1l) & (v2c <= v1h)
    ok = (alc ^ baj) & dentro & (rango > 0)
    idx = np.where(ok)[0]
    return pd.DataFrame(dict(
        largo = alc[idx], v1h = v1h[idx], v1l = v1l[idx], rango = rango[idx],
        A = np.where(alc[idx], v2l[idx], v2h[idx]),
        t0 = d.t0.values[2:][idx], t1 = d.t1.values[2:][idx]))

def madrid_h(ts):
    t = pd.Timestamp(ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    return t.hour + t.minute/60

def ejecuta(setups, m5, m1, unit, coste):
    t5 = m5.ts.values; h5 = m5.high.values; l5 = m5.low.values; o5 = m5.open.values
    t1 = m1.ts.values; h1 = m1.high.values; l1 = m1.low.values; c1 = m1.close.values
    ops, ocupado_hasta, cuenta = [], np.datetime64("1970-01-01"), {}
    for s in setups.itertuples():
        if np.datetime64(pd.Timestamp(s.t0)) < ocupado_hasta:
            continue
        a = int(np.searchsorted(t5, np.datetime64(pd.Timestamp(s.t0))))
        b = int(np.searchsorted(t5, np.datetime64(pd.Timestamp(s.t1)))) + 1
        B = None
        for k in range(a, min(b, len(t5))):
            if B is not None:
                impulso = (B - s.A) if s.largo else (s.A - B)
                if impulso >= MIN_LEG * s.rango:
                    lim = B - FIB*impulso if s.largo else B + FIB*impulso
                    cruza = (l5[k] <= lim) if s.largo else (h5[k] >= lim)
                    if cruza:
                        px = min(lim, o5[k]) if s.largo else max(lim, o5[k])
                        if not any(x <= madrid_h(t5[k]) < y for x, y in VENTANAS):
                            B = max(B, h5[k]) if s.largo else min(B, l5[k]); continue
                        dd = pd.Timestamp(t5[k]).date()
                        if cuenta.get(dd, 0) >= TOPE_DIA:
                            B = max(B, h5[k]) if s.largo else min(B, l5[k]); continue
                        stop = s.A - BUF*unit if s.largo else s.A + BUF*unit
                        obj  = s.v1h if s.largo else s.v1l
                        rg, pr = abs(px-stop), abs(obj-px)
                        if rg < max(MIN_RIESGO_T*unit, MIN_RIESGO_R*s.rango): break
                        if rg <= 0 or pr <= 0: break
                        if not (MIN_RR <= pr/rg <= MAX_RR): break
                        if s.largo and not (px > stop and obj > px): break
                        if (not s.largo) and not (px < stop and obj < px): break
                        p = int(np.searchsorted(t1, np.datetime64(pd.Timestamp(t5[k]))))
                        q = min(p + MAX_H*60, len(t1))
                        if p >= len(t1) or q <= p: break
                        alto, bajo = h1[p:q], l1[p:q]
                        tocaS = (bajo <= stop) if s.largo else (alto >= stop)
                        tocaO = (alto >= obj) if s.largo else (bajo <= obj)
                        iS = int(np.argmax(tocaS)) if tocaS.any() else 10**9
                        iO = int(np.argmax(tocaO)) if tocaO.any() else 10**9
                        if iS == 10**9 and iO == 10**9:
                            sal, mot, fin = c1[q-1], "tiempo", (q-p)-1
                        elif iS <= iO: sal, mot, fin = stop, "SL", iS
                        else:          sal, mot, fin = obj, "TP", iO
                        gan = (sal-px) if s.largo else (px-sal)
                        ops.append(dict(ts=t5[k], largo=bool(s.largo), motivo=mot,
                                        entrada=px, sl=stop, tp=obj,
                                        riesgo_u=rg/unit, bruto=gan/rg,
                                        R=(gan/unit - coste)/(rg/unit)))
                        cuenta[dd] = cuenta.get(dd, 0) + 1
                        ocupado_hasta = t1[min(p+fin, len(t1)-1)]
                        break
            v = h5[k] if s.largo else l5[k]
            B = v if B is None else (max(B, v) if s.largo else min(B, v))
    return pd.DataFrame(ops)
