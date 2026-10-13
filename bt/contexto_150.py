"""Reconstruye lo que se veia en el grafico en el minuto exacto de cada una de
sus 150 entradas, para poder sacar su regla de entrada de lo que HIZO en vez de
lo que recuerda.

Este fichero solo comprueba que la reconstruccion es fiable: que el precio de
entrada que apunto la pagina coincide con el M1 real de ese dia y ese minuto.
Si eso cuadra en las 150, el mapa dia<->sesion y la zona horaria son correctos y
se puede medir cualquier cosa sobre ese instante.

  python3 bt/contexto_150.py
"""
import json, re, sys
import numpy as np, pandas as pd

TZ, U = "Europe/Madrid", 1e-4
LIN = re.compile(
    r"^S(?P<ses>\d+) · (?P<h>\d\d):(?P<m>\d\d) (?P<lado>COMPRA|VENTA) ent (?P<ent>[\d.]+) "
    r"sl (?P<sl>[\d.]+) \((?P<rgo>[\d.]+)p\) tp (?P<tp>[\d.]+) -> (?P<mot>\S+) "
    r"(?P<R>[+-][\d.]+) R a las (?P<hs>\d\d):(?P<ms>\d\d)")
BLOQUES = [("data/examen_respuestas_1.txt", "data/examen_dias.json"),
           ("data/examen_respuestas_2.txt", "data/examen_dias2.json"),
           ("data/examen_respuestas_3.txt", "data/examen_dias3.json"),
           ("data/examen_respuestas_4.txt", "data/examen_dias4.json")]

filas = []
for b, (f, dj) in enumerate(BLOQUES, 1):
    dias = {int(k): pd.Timestamp(v).date() for k, v in json.load(open(dj)).items()}
    for l in open(f, encoding="utf-8"):
        m = LIN.match(l.strip())
        if not m: continue
        d = m.groupdict()
        filas.append(dict(bloque=b, ses=int(d["ses"]), dia=dias[int(d["ses"])],
                          ent_min=int(d["h"])*60+int(d["m"]),
                          sal_min=int(d["hs"])*60+int(d["ms"]),
                          lado=1 if d["lado"] == "COMPRA" else -1,
                          ent=float(d["ent"]), sl=float(d["sl"]), tp=float(d["tp"]),
                          rgo=float(d["rgo"]), mot=d["mot"], R=float(d["R"])))
t = pd.DataFrame(filas)
print(f"{len(t)} operaciones · {t.dia.nunique()} días distintos "
      f"· {len(set(t.dia))} sin repetir entre bloques")

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date
m1 = m1[m1.dia.isin(set(t.dia))].reset_index(drop=True)
m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
print(f"{len(m1):,} velas de M1 cargadas para esos días")

# el minuto exacto de cada entrada
idx = m1.set_index(["dia", "min"])
falta, dif = 0, []
for r in t.itertuples():
    try: v = idx.loc[(r.dia, r.ent_min)]
    except KeyError: falta += 1; dif.append(np.nan); continue
    v = v.iloc[0] if isinstance(v, pd.DataFrame) else v
    # entra a mercado dentro de esa vela: el precio tiene que caer en su rango
    dentro = v.low - 1e-9 <= r.ent <= v.high + 1e-9
    dif.append(0.0 if dentro else min(abs(r.ent - v.high), abs(r.ent - v.low))/U)
t["desvio_p"] = dif
ok = int((t.desvio_p == 0).sum())
print(f"\ncomprobación · precio de entrada dentro del rango de esa vela de M1:")
print(f"  {ok} de {len(t)}   ·   minutos sin vela: {falta}")
if ok < len(t):
    mal = t[(t.desvio_p > 0) | t.desvio_p.isna()]
    print(f"  desvío mediano de las que no cuadran: {mal.desvio_p.median():.2f} pips")
    print(mal[["bloque","ses","dia","ent_min","ent","desvio_p"]].head(12).to_string(index=False))
t.to_csv("data/operaciones_150.csv", index=False)
print("\nescrito data/operaciones_150.csv")
