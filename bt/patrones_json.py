"""Datos para la pagina: cada entrada con sus tres velas de M5 y su contexto."""
import json, numpy as np, pandas as pd
TZ, INI, FIN = "Europe/Madrid", 480, 690
S = pd.read_csv("data/cuerpo_vela.csv"); S["dia"] = pd.to_datetime(S.dia).dt.date
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(set(S.dia))]
v = m1.assign(b=(m1["min"]//5)*5).groupby(["dia","b"]).agg(
      o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
      n=("close","size")).reset_index()
v = v[v.n >= 3]; v["cierre_min"] = v.b + 5
IDX = {(r.dia, r.cierre_min): (r.o, r.h, r.l, r.c) for r in v.itertuples()}

BLOQ = {}
for nb, dj in enumerate(["data/examen_dias.json","data/examen_dias2.json",
                         "data/examen_dias3.json","data/examen_dias4.json"], 1):
    for d in json.load(open(dj)).values(): BLOQ[pd.Timestamp(d).date()] = nb

out = []
for r in S.itertuples():
    velas = []
    for k in (2, 1, 0):
        q = IDX.get((r.dia, r.cierre_min - 5*k))
        if q: velas.append([round(x, 5) for x in q])
    if len(velas) < 3: continue
    hh = int(r.ent_min)//60; mm = int(r.ent_min) % 60
    out.append(dict(
        dia=str(r.dia), bloque=BLOQ.get(r.dia, 0),
        hora=f"{hh:02d}:{mm:02d}", lado=int(r.lado_t), mot=r.mot,
        R=round(float(r.R), 2), neta=round(float(r.neta), 2), stop=round(float(r.rgo), 1),
        velas=velas, patron=("" if r.patrones == "ninguno" else r.patrones),
        cuerpo=r.cuerpo, frac=round(float(r.frac_cuerpo), 2), cierre=r.cierre,
        verde=bool(r.verde), toca=bool(r.toca),
        m15dir=int(r.m15dir), m15tend=int(r.m15tend), m5tend=int(r.m5tend),
        m15pos=round(float(r.m15pos), 2)))
json.dump(out, open("data/patrones_web.json","w"), ensure_ascii=False)
print(len(out), "operaciones ·", sum(1 for x in out if x["mot"]=="TP"), "TP ·",
      sum(1 for x in out if x["mot"]=="SL"), "SL ·",
      sum(1 for x in out if x["mot"]=="cierre"), "cierres")
print(round(len(json.dumps(out))/1024), "KB")
