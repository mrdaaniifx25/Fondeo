"""Cuanto se fue en contra cada operacion antes de resolverse.

Hace falta para saber si el limite diario del 5 % se toca con la perdida
FLOTANTE de una posicion abierta, no solo con la cerrada. El documento de
FundingPips no dice si el limite se mide sobre saldo o sobre equity, asi que se
calculan las dos cosas.

  python3 bt/examen_mae.py
"""
import json, re, numpy as np, pandas as pd
TZ = "Europe/Madrid"

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"]=pd.to_datetime(m1.ts); m1=m1.sort_values("ts").reset_index(drop=True)
m1["loc"]=pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"]=m1["loc"].dt.date; m1["min"]=m1["loc"].dt.hour*60+m1["loc"].dt.minute
POR = {d: g.reset_index(drop=True) for d, g in m1.groupby("dia")}

filas = []
for f, dj, bl in (("data/examen_respuestas_1.txt","data/examen_dias.json",1),
                  ("data/examen_respuestas_2.txt","data/examen_dias2.json",2),
                  ("data/examen_respuestas_3.txt","data/examen_dias3.json",3)):
    dias = {int(k): pd.Timestamp(v).date() for k,v in json.load(open(dj)).items()}
    for l in open(f):
        m = re.match(r"S(\d+) · (\d\d):(\d\d) (COMPRA|VENTA) ent ([\d.]+) sl ([\d.]+) "
                     r"\(([\d.]+)p\) tp ([\d.]+) -> (\S+) ([+-][\d.]+) R a las (\d\d):(\d\d)", l.strip())
        if not m: continue
        s = int(m.group(1)); d = dias[s]
        e0 = int(m.group(2))*60 + int(m.group(3))          # minuto de entrada
        e1 = int(m.group(11))*60 + int(m.group(12))        # minuto de salida
        lado = 1 if m.group(4) == "COMPRA" else -1
        ent, rgo, mot, R = float(m.group(5)), float(m.group(7)), m.group(9), float(m.group(10))
        g = POR[d]
        tramo = g[(g["min"] >= e0) & (g["min"] <= e1)]
        if tramo.empty: continue
        peor = (tramo.low.min() - ent) if lado > 0 else (ent - tramo.high.max())
        filas.append(dict(bloque=bl, ses=s, dia=d, rgo=rgo, R=R, mot=mot,
                          mae=max(0.0, -peor/1e-4/rgo)))       # en R, siempre >= 0
d = pd.DataFrame(filas)
d.to_csv("data/examen_mae.csv", index=False)
print(f"{len(d)} operaciones\n")
print("CUÁNTO SE VA EN CONTRA ANTES DE RESOLVERSE, EN R")
print(f"  mediana {d.mae.median():.2f} R  ·  media {d.mae.mean():.2f} R  ·  máximo {d.mae.max():.2f} R")
for q in (0.5, 0.75, 0.9, 0.95, 1.0):
    print(f"    percentil {100*q:3.0f}: {d.mae.quantile(q):.2f} R")
print("\n  por desenlace:")
for mot in ("TP", "SL", "cierre"):
    s = d[d.mot == mot]
    if len(s): print(f"    {mot:7s} n={len(s):3d}  MAE mediana {s.mae.median():.2f} R  ·  p90 {s.mae.quantile(.9):.2f} R")
print("\n  peor caída flotante ACUMULADA en una sesión (suma de cerradas + flotante abierta):")
peor = []
for (bl, ses), g in d.groupby(["bloque","ses"]):
    acum, mn = 0.0, 0.0
    for r in g.itertuples():
        mn = min(mn, acum - r.mae)     # con la abierta en su peor momento
        acum += r.R
        mn = min(mn, acum)
    peor.append(mn)
peor = np.array(peor)
print(f"    mediana {np.median(peor):.2f} R  ·  peor sesión {peor.min():.2f} R")
print(f"    sesiones que bajarían de -5 R: {(peor <= -5).sum()} de {len(peor)}")
