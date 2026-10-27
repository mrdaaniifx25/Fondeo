"""Prepara los 17 casos de compra en el alto de Asia para paginas/compras_alto_asia.html

8 son suyas (7 TP / 1 SL) y 9 son disparos de la regla que no tomo (2 TP / 7 SL).
De sus 12 compras de agosto solo entran 8: los datos M1 de HistData llegan al
21 de agosto, asi que T09, T11, T14 y T15 se quedan sin velas.
"""
import pandas as pd, json
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1.ts); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert("Europe/Madrid").tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date.astype(str); v["hm"] = v.b5.dt.strftime("%H:%M")
asia = {d: (float(g[g.b5.dt.hour < 8].h.max()), float(g[g.b5.dt.hour < 8].l.min()))
        for d, g in v.groupby("dia") if len(g[g.b5.dt.hour < 8]) >= 60}

casos = []
o = pd.read_csv("data/agosto_operaciones.csv")
ver = pd.read_csv("data/agosto_verificacion.csv").set_index("id")
for r in o[(o.lado == 1) & (o.fecha <= "2026-08-21")].itertuples():
    res = ver.loc[r.id, "mot"]
    casos.append(dict(ref=r.id, grupo="suya", dia=r.fecha, hm=r.hora, ent=r.entrada,
                      stop=r.stop, tp=r.tp, res=res if res in ("TP","SL") else ver.loc[r.id,"suyo"]))

t = pd.read_csv("data/asia_nivel.csv", parse_dates=["ts"]); a = t[t.ts >= "2026-08-01"].copy()
loc = a.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
a["hm"] = (loc + pd.Timedelta(minutes=-4)).dt.strftime("%H:%M")
SUY = {("2026-08-03",-1), ("2026-08-06",-1), ("2026-08-11",-1)}
s = a[~a.apply(lambda r: (str(r.dia), r.lado) in SUY, axis=1)]
s = s[~((s.dia == "2026-08-07") & (s.tipo == "B"))]; s = s[s.tipo != "A"]
for i, r in enumerate(s[s.lado == 1].itertuples(), 1):
    casos.append(dict(ref=f"N{i:02d}", grupo="no tomada", dia=str(r.dia), hm=r.hm,
                      ent=r.entrada, stop=r.stop, tp=r.obj, res=r.motivo))

for c in casos:
    g = v[v.dia == c["dia"]].reset_index(drop=True)
    k = int(g.index[g.hm == c["hm"]][0])
    w = g.iloc[max(0, k-11):k+1]
    c["velas"] = [dict(t=x.hm, o=round(x.o,5), h=round(x.h,5), l=round(x.l,5), c=round(x.c,5))
                  for x in w.itertuples()]
    c["ahi"], c["alo"] = asia[c["dia"]]
    c["rgo"] = round(abs(c["ent"] - c["stop"]) / 1e-4, 1)
print(json.dumps(casos, separators=(",",":")))
