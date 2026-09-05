"""Los 37 cortes que el usuario opero en la baraja v2, ya resueltos.

Reconstruye el dia entero en M5 -de 00:00 al cierre de Londres- con la linea
del corte donde el decidio, sus tres niveles, el punto donde toco el stop y el
punto mas lejos que llego a favor.  Sale el JSON que consume la pagina.
"""
import json
import numpy as np
import pandas as pd

U, TZ = 0.0001, "Europe/Madrid"
m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), ts=("ts","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date; v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute

# temporalidades de contexto, en hora local
def agrupa(regla):
    b = m1["loc"].dt.floor(regla)
    g = (m1.groupby(b).agg(o=("open","first"), h=("high","max"), l=("low","min"),
                           c=("close","last"), n=("ts","size")).reset_index()
                      .rename(columns={"loc": "b"}))
    return g[g.n >= 3].reset_index(drop=True)

CTX = {"1h": agrupa("1h"), "4h": agrupa("4h"), "1D": agrupa("1D")}
CUANTAS = {"1h": 48, "4h": 60, "1D": 40}

o = pd.read_csv("data/etiquetado_asia2_respuestas.csv")
ver = pd.read_csv("data/etiquetado_asia2_verdad.csv").set_index("id")
setups = {s["id"]: s for s in json.load(open("data/etiquetado_asia2_setups.json"))}
cam = pd.read_parquet("data/etiquetado_asia2_camino.parquet")
cm = {k: g for k, g in cam.groupby("id")}
MES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]

def ctx_de(regla, corte):
    """las ultimas velas de esa temporalidad hasta la del corte, inclusive"""
    g = CTX[regla]
    j = int(g.index[g.b <= corte][-1])
    ini = max(0, j - CUANTAS[regla] + 1)
    tr = g.iloc[ini:j + 1]
    return dict(velas=[[round(float(x.o),5), round(float(x.h),5), round(float(x.l),5),
                        round(float(x.c),5)] for x in tr.itertuples()],
                etiq=[f"{x.b:%d/%m}" if regla != "1h" else f"{x.b:%d} {x.b:%H}h"
                      for x in tr.itertuples()],
                i_marca=int(j - ini))


fichas = []
for r in o.itertuples():
    s = setups[r.id]
    corte = pd.Timestamp(ver.loc[r.id, "ts"]).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    dia = corte.date()
    g = v[(v.dia == dia) & (v.hm < 1400)].reset_index(drop=True)
    i_corte = int(g.index[g.b5 == corte.floor("5min")][0])

    lado, ent, sl, tp = r.lado, r.entrada, r.stop, r.obj
    rgo = abs(ent - sl)
    p = cm[r.id]; H, L = p.high.to_numpy(), p.low.to_numpy()
    tocado = (L <= sl) if lado > 0 else (H >= sl)
    i_sl_m1 = int(np.argmax(tocado)) if tocado.any() else None
    fav = (H - ent) if lado > 0 else (ent - L)
    i_mfe_m1 = int(np.argmax(np.maximum.accumulate(fav) == fav.max()))
    if i_sl_m1 is not None:
        i_mfe_m1 = int(np.argmax(fav[:i_sl_m1+1])) if i_sl_m1 > 0 else 0

    def a_m5(k):
        if k is None: return None
        t = pd.Timestamp(p.ts.to_numpy()[k]).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
        j = g.index[g.b5 == t.floor("5min")]
        return int(j[0]) if len(j) else None

    fichas.append(dict(
        id=r.id, motivo=r.motivo, lado=int(lado),
        fecha=f"{corte.day} {MES[corte.month-1]} {corte.year}", hora=f"{corte:%H:%M}",
        orden_fecha=f"{corte:%Y-%m-%d}",
        velas=[[round(float(x.o),5), round(float(x.h),5), round(float(x.l),5),
                round(float(x.c),5), int(x.hm)] for x in g.itertuples()],
        asia_hi=round(s["asia_hi"],5), asia_lo=round(s["asia_lo"],5),
        n_asia=int((g.hm < 800).sum()), i_corte=i_corte,
        i_barrido=i_corte - (len(s["velas"])-1 - s["i_barrido"]),
        entrada=round(ent,5), stop=round(sl,5), obj=round(tp,5),
        riesgo=round(rgo/U,1), rr=round(abs(tp-ent)/rgo,2),
        ctx={k: ctx_de(k, corte) for k in CTX},
        i_sl=a_m5(i_sl_m1), i_mfe=a_m5(i_mfe_m1),
        mfe=round(float(fav[:(i_sl_m1+1) if i_sl_m1 is not None else len(fav)].max()/rgo),2),
        minutos=(i_sl_m1+1) if i_sl_m1 is not None else None,
    ))

orden = {"SL": 0, "cierre Londres": 1, "TP": 2}
fichas.sort(key=lambda f: (orden[f["motivo"]], f["orden_fecha"]))
json.dump(fichas, open("data/asia2_autopsia.json", "w"))
print("fichas:", len(fichas), " ·",
      {k: sum(1 for f in fichas if f["motivo"] == k) for k in orden})
print("velas por dia:", int(np.mean([len(f["velas"]) for f in fichas])))
