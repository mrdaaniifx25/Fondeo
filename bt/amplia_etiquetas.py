"""Anade H1 y M5 a la muestra ciega YA SORTEADA, sin tocar la muestra.

El usuario pidio ver el rango marcado en H4 y en H1, y la entrada en M5.
Eso cambia lo que se MUESTRA, no lo que se mide: los 300 casos son los mismos,
con los mismos identificadores, el mismo orden y la misma semilla. El fichero
de la verdad no se abre aqui.

La regla que no se puede romper: ninguna vela, en ningun marco, puede terminar
despues del instante de entrada. Se comprueba caso por caso al final, rehaciendo
el calculo desde los datos en bruto.
"""
import sys; sys.path.insert(0, "bt")
import json
import numpy as np, pandas as pd
from crt_canonico import velas_ref

RUTA = {"EURUSD": "data/eurusd_m1.parquet", "NAS100": "data/nsxusd_m1.parquet"}
N_H1, N_M5 = 44, 60          # velas visibles hacia atras en cada marco

def velas_ny(m1, freq, min_n):
    """Velas ancladas al reloj de Nueva York, como velas_ref pero en cualquier
    tramo y con un umbral de cobertura suave: aqui solo se dibuja, no se mide,
    y perder una vela floja abriria un hueco justo antes de la entrada."""
    ny = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York")
    d = m1.copy()
    d["id"] = ny.tz_localize(None).floor(freq)
    g = d.groupby("id").agg(open=("open", "first"), high=("high", "max"),
                            low=("low", "min"), close=("close", "last"),
                            fin=("ts", "max"), n=("ts", "size")).reset_index()
    return g[g.n >= min_n].reset_index(drop=True)

casos = json.load(open("data/etiquetas_casos.json"))
por_ins = {}
for c in casos:
    por_ins.setdefault(c["ins"], []).append(c)

fallos, huecos = [], 0
for ins, grupo in por_ins.items():
    m1 = pd.read_parquet(RUTA[ins]); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").reset_index(drop=True)

    H4 = velas_ref(m1, 4, ancla_ny=1)          # la rejilla del estudio, intacta
    H1 = velas_ny(m1, "1h", 5)
    M5 = velas_ny(m1, "5min", 2)
    fila4 = {pd.Timestamp(t): k for k, t in enumerate(H4["id"])}

    for c in grupo:
        dec = c["dec"]
        k4 = fila4.get(pd.Timestamp(c["hora"]))
        if k4 is None or k4 < 1:
            fallos.append((c["id"], "no encuentro la vela de H4")); continue

        # la vela dibujada como entrada y la localizada tienen que ser la misma
        loc = [round(float(H4[x].iloc[k4]), dec) for x in ("open", "high", "low", "close")]
        if loc != c["velas"][c["i_ent"]][1:]:
            fallos.append((c["id"], "la vela de entrada no cuadra")); continue

        # el rango es la vela base; su extremo opuesto es el objetivo declarado
        r_hi = round(float(H4["high"].iloc[k4 - 1]), dec)
        r_lo = round(float(H4["low"].iloc[k4 - 1]), dec)
        esperado = r_hi if c["largo"] else r_lo
        if abs(esperado - c["objetivo"]) > 10.0 ** (-dec) * 1.5:
            fallos.append((c["id"], "el objetivo no es el extremo de la base")); continue

        t_ent = pd.Timestamp(H4["fin"].iloc[k4])       # instante de entrada, UTC
        ini_base = pd.Timestamp(H4["id"].iloc[k4 - 1]) # arranque de la vela base
        ini_ent = pd.Timestamp(H4["id"].iloc[k4])      # arranque de la de entrada
        c["rango_hi"], c["rango_lo"] = r_hi, r_lo

        corte = False
        for V, cuantas, clave, marcas in ((H1, N_H1, "v1", ("i_base1", "i_ent1")),
                                          (M5, N_M5, "v5", (None, "i_ent5"))):
            j = int(np.searchsorted(V["fin"].to_numpy(), t_ent.to_datetime64(), side="right"))
            if j < cuantas:
                fallos.append((c["id"], "historico corto")); corte = True; break
            tramo = V.iloc[j - cuantas:j]
            ids = [pd.Timestamp(t) for t in tramo["id"]]
            c[clave] = [[round(float(r.open), dec), round(float(r.high), dec),
                         round(float(r.low), dec), round(float(r.close), dec)]
                        for r in tramo.itertuples()]
            # indices por MARCA DE TIEMPO, no por posicion: si falta una vela
            # floja el hueco no descoloca el rango
            if marcas[0]:
                c[marcas[0]] = next((n for n, t in enumerate(ids) if t >= ini_base), 0)
            c[marcas[1]] = next((n for n, t in enumerate(ids) if t >= ini_ent), cuantas - 1)
            if pd.Timestamp(tramo["fin"].iloc[-1]) > t_ent:
                fallos.append((c["id"], "se pasa de la entrada")); corte = True; break
        if corte:
            c.pop("v1", None); c.pop("v5", None)

print(f"casos con problema: {len(fallos)}")
for f in fallos[:12]: print("  ", f)

buenos = [c for c in casos if "v1" in c and "v5" in c]
print(f"casos completos: {len(buenos)} de {len(casos)}")

# AUDITORIA, rehecha desde el parquet sin fiarse de lo anterior
for ins, grupo in por_ins.items():
    m1 = pd.read_parquet(RUTA[ins]); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").reset_index(drop=True)
    H4 = velas_ref(m1, 4, ancla_ny=1)
    fila4 = {pd.Timestamp(t): k for k, t in enumerate(H4["id"])}
    for c in grupo:
        if "v1" not in c: continue
        tol = 10.0 ** (-c["dec"]) * 1.5
        t_ent = pd.Timestamp(H4["fin"].iloc[fila4[pd.Timestamp(c["hora"])]])
        # los tres marcos tienen que cerrar EXACTAMENTE en el precio de entrada:
        # si alguno llevara una vela de mas, este cierre no coincidiria
        assert abs(c["velas"][-1][4] - c["entrada"]) <= tol, ("H4", c["id"])
        assert abs(c["v1"][-1][3] - c["entrada"]) <= tol, ("H1", c["id"])
        assert abs(c["v5"][-1][3] - c["entrada"]) <= tol, ("M5", c["id"])
        # y el maximo del tramo dibujado no puede superar al de las velas reales
        real = m1[m1.ts <= t_ent].tail(N_M5 * 5)
        assert max(v[1] for v in c["v5"]) <= round(float(real.high.max()), c["dec"]) + tol, c["id"]
print("auditoria: los tres marcos cierran exactamente en el precio de entrada")

json.dump(buenos, open("data/etiquetas_casos_3tf.json", "w"), separators=(",", ":"))
print(f"fichero: {len(open('data/etiquetas_casos_3tf.json').read())/1024:.0f} KB")
