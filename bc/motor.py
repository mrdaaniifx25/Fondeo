"""Simulacion de operaciones segun docs/BC_02_especificacion.md.

Decision de especificacion que hay que declarar, porque el material no la fija:
cuando hay varios objetivos vivos de temporalidad mayor en la misma direccion,
se toma el MAS CERCANO. Es la lectura conservadora -da el R:R mas bajo, o sea
menos operaciones pasan el filtro de 3- y por tanto la que menos favorece al
metodo. Se anota el numero de objetivos alineados por separado.
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd
import nucleo as N

CTX = [("1D", 24), ("12H", 12), ("4H", 4)]      # temporalidades de contexto
EJEC_H = 1                                       # por defecto 1H  ·  BC_02 §5
# El material habla de 1H, 15M, 10M, 5M y 2M, y sus dos operaciones documentadas
# entran en 15M y en 10M. Hasta BC_09 esto era una constante.  ·  BC_09

def objetivos_vivos(m1, huso, lectura, ts_ejec):
    """Para cada instante de ejecucion, los objetivos de contexto todavia vivos."""
    cols = {}
    for nom, horas in CTX:
        v = N.activaciones(N.velas(m1, horas, huso, 0), lectura)
        rangos = [r for r in N.vida(v, nom)]
        if not rangos:
            cols[nom] = pd.DataFrame({"lado": np.nan, "obj": np.nan, "tomas": np.nan},
                                     index=range(len(ts_ejec)))
            continue
        t = pd.DataFrame([dict(ts=r.nace, muere=r.muere, lado=r.lado, obj=r.objetivo,
                               tomas=r.tomas) for r in rangos]).sort_values("ts")
        m = pd.merge_asof(pd.DataFrame({"ts": ts_ejec}).sort_values("ts"),
                          t, on="ts", direction="backward")
        # sin esta mascara la funcion no devuelve objetivos VIVOS: devuelve el
        # ultimo rango creado, completado o descartado incluido.
        muerto = m["muere"].notna() & (m["ts"] >= m["muere"])
        for c in ("lado", "obj", "tomas"):
            m.loc[muerto, c] = np.nan
        cols[nom] = m[["lado", "obj", "tomas"]].reset_index(drop=True)
    return cols

def opera(m1, huso, lectura, colchon, unidad, coste, rr_min=3.0,
          desde=None, hasta=None, tope_velas=5, riesgo_min_x_coste=3.0,
          ejec_h=None):
    """riesgo_min_x_coste: el stop tiene que estar al menos a N veces el coste.

    No es un filtro de rendimiento, es de EJECUTABILIDAD. Un stop de 1,9 pips
    con 1,2 pips de coste no se puede operar: el deslizamiento solo ya se lo
    come, y ademas dispara el R:R a valores absurdos -se han visto de 1198- que
    envenenan la media. Se aplica igual a todas las celdas.
    """
    ej = N.activaciones(N.velas(m1, EJEC_H if ejec_h is None else ejec_h, huso, 0), lectura)
    ts = ej["fin"].to_numpy()
    ctx = objetivos_vivos(m1, huso, lectura, ts)

    lado_e = ej["lado"].to_numpy()
    cl, hi, lo = ej["close"].to_numpy(), ej["high"].to_numpy(), ej["low"].to_numpy()

    filas = []
    for i in range(len(ej)):
        L = int(lado_e[i])
        if L == 0:
            continue
        # objetivos de contexto vivos y en la MISMA direccion
        alineados = []
        for nom, _ in CTX:
            r = ctx[nom].iloc[i]
            if not np.isfinite(r["lado"]) or int(r["lado"]) != L:
                continue
            o = float(r["obj"])
            if (L > 0 and o > cl[i]) or (L < 0 and o < cl[i]):
                alineados.append((nom, o, int(r["tomas"])))
        if not alineados:
            continue
        entrada = cl[i]
        objetivo = min(a[1] for a in alineados) if L > 0 else max(a[1] for a in alineados)
        stop = (lo[i] - colchon*unidad) if L > 0 else (hi[i] + colchon*unidad)
        riesgo = abs(entrada - stop)
        if riesgo <= 0 or riesgo/unidad < riesgo_min_x_coste * coste:
            continue
        rr = abs(objetivo - entrada) / riesgo
        filas.append(dict(i=i, ts=pd.Timestamp(ts[i]), lado=L, entrada=entrada,
                          stop=stop, objetivo=objetivo, riesgo_u=riesgo/unidad, rr=rr,
                          n_obj=len(alineados), tf_obj=min(alineados, key=lambda a: abs(a[1]-entrada))[0],
                          tomas=max(a[2] for a in alineados)))
    t = pd.DataFrame(filas)
    if t.empty:
        return t
    if desde is not None: t = t[t.ts >= desde]
    if hasta is not None: t = t[t.ts < hasta]
    t = t[t.rr >= rr_min].reset_index(drop=True)
    if t.empty:
        return t

    # resolucion en M1
    t1 = m1["ts"].to_numpy(); H = m1["high"].to_numpy(); L1 = m1["low"].to_numpy()
    C1 = m1["close"].to_numpy()
    res, mot = [], []
    tope = int(tope_velas * 12 * 60)     # 5 velas de 12H  ·  BC_02 §9
    for r in t.itertuples():
        j0 = int(np.searchsorted(t1, np.datetime64(r.ts), side="right"))
        j1 = min(j0 + tope, len(t1))
        if j0 >= len(t1):
            res.append(np.nan); mot.append("sin datos"); continue
        hh, ll = H[j0:j1], L1[j0:j1]
        if r.lado > 0:
            gt, gs = hh >= r.objetivo, ll <= r.stop
        else:
            gt, gs = ll <= r.objetivo, hh >= r.stop
        it = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = C1[j1-1]; mot.append("tiempo")
            res.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/abs(r.entrada-r.stop))
        elif isl <= it:                          # empate -> stop  ·  BC_02 §9
            res.append(-1.0); mot.append("SL")
        else:
            res.append(float(r.rr)); mot.append("TP")
    t["R"] = res
    t["motivo"] = mot
    t["R_neto"] = t.R - coste/t.riesgo_u
    return t.dropna(subset=["R"]).reset_index(drop=True)
