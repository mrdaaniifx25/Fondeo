"""El disparo de TRANSICION del reinicio.  Pre-registro en BC_05.

Distinto del motor de BC_04: alli se entraba cuando la temporalidad de ejecucion
YA coincidia con las mayores. Aqui se entra cuando pasa de estar EN CONTRA a
coincidir, que es lo que ellos describen.
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd
import nucleo as N, motor as M

CTX = [("1D", 24), ("12H", 12), ("4H", 4)]
EJEC_H = 1

def reiniciadas(v, lectura_rein):
    """Marca donde una vela produce una reiniciada, y en que direccion.

    Hay un rango vivo con direccion -X y vela base con sus extremos. El precio
    se lleva el extremo CONTRARIO al que definio ese rango -> reiniciada X.
    """
    va = N.activaciones(v, "B")          # los rangos se crean con su definicion escrita
    h, l, o, c = (v[x].to_numpy() for x in ("high","low","open","close"))
    lado = va["lado"].to_numpy()
    bhi, blo = va["base_hi"].to_numpy(), va["base_lo"].to_numpy()
    n = len(v)
    rein = np.zeros(n, dtype=int)
    cur_lado, cur_hi, cur_lo = 0, np.nan, np.nan
    cuerpo_hi = np.maximum(o, c); cuerpo_lo = np.minimum(o, c)
    for i in range(n):
        if cur_lado != 0:
            if cur_lado < 0 and h[i] > cur_hi:            # rango bajista, se lleva el alto
                ok = True if lectura_rein == "R1" else (cuerpo_lo[i-1] <= c[i] <= cuerpo_hi[i-1] if i else False)
                if ok: rein[i] = +1; cur_lado = 0
            elif cur_lado > 0 and l[i] < cur_lo:           # rango alcista, se lleva el bajo
                ok = True if lectura_rein == "R1" else (cuerpo_lo[i-1] <= c[i] <= cuerpo_hi[i-1] if i else False)
                if ok: rein[i] = -1; cur_lado = 0
        if lado[i] != 0:
            cur_lado, cur_hi, cur_lo = int(lado[i]), bhi[i], blo[i]
    return va.assign(rein=rein)

def opera(m1, huso, lectura, lectura_rein, colchon, unidad, coste,
          rr_min=3.0, min_ctx=2, desde=None, hasta=None,
          tope_velas=5, riesgo_min_x_coste=3.0):
    ej = reiniciadas(N.velas(m1, EJEC_H, huso, 0), lectura_rein)
    ts = ej["fin"].to_numpy()
    ctx = M.objetivos_vivos(m1, huso, lectura, ts)
    rein = ej["rein"].to_numpy()
    cl, hi, lo = ej["close"].to_numpy(), ej["high"].to_numpy(), ej["low"].to_numpy()

    filas = []
    for i in range(len(ej)):
        X = int(rein[i])
        if X == 0:
            continue
        alineados = []
        for nom, _ in CTX:
            r = ctx[nom].iloc[i]
            if not np.isfinite(r["lado"]) or int(r["lado"]) != X:
                continue
            ob = float(r["obj"])
            if (X > 0 and ob > cl[i]) or (X < 0 and ob < cl[i]):
                alineados.append((nom, ob))
        if len(alineados) < min_ctx:
            continue
        entrada = cl[i]
        objetivo = min(a[1] for a in alineados) if X > 0 else max(a[1] for a in alineados)
        stop = (lo[i] - colchon*unidad) if X > 0 else (hi[i] + colchon*unidad)
        riesgo = abs(entrada - stop)
        if riesgo <= 0 or riesgo/unidad < riesgo_min_x_coste * coste:
            continue
        rr = abs(objetivo - entrada) / riesgo
        filas.append(dict(ts=pd.Timestamp(ts[i]), lado=X, entrada=entrada, stop=stop,
                          objetivo=objetivo, riesgo_u=riesgo/unidad, rr=rr,
                          n_obj=len(alineados)))
    t = pd.DataFrame(filas)
    if t.empty: return t
    if desde is not None: t = t[t.ts >= desde]
    if hasta is not None: t = t[t.ts < hasta]
    t = t[t.rr >= rr_min].reset_index(drop=True)
    if t.empty: return t

    t1 = m1["ts"].to_numpy(); H = m1["high"].to_numpy(); L1 = m1["low"].to_numpy()
    C1 = m1["close"].to_numpy(); tope = int(tope_velas*12*60)
    res, mot = [], []
    for r in t.itertuples():
        j0 = int(np.searchsorted(t1, np.datetime64(r.ts), side="right"))
        j1 = min(j0+tope, len(t1))
        if j0 >= len(t1): res.append(np.nan); mot.append("sin datos"); continue
        hh, ll = H[j0:j1], L1[j0:j1]
        gt, gs = ((hh >= r.objetivo, ll <= r.stop) if r.lado > 0
                  else (ll <= r.objetivo, hh >= r.stop))
        it = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = C1[j1-1]; mot.append("tiempo")
            res.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/abs(r.entrada-r.stop))
        elif isl <= it: res.append(-1.0); mot.append("SL")
        else: res.append(float(r.rr)); mot.append("TP")
    t["R"] = res; t["motivo"] = mot
    t["R_neto"] = t.R - coste/t.riesgo_u
    return t.dropna(subset=["R"]).reset_index(drop=True)
