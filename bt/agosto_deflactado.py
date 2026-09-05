"""Agosto 2026 recalculado con las operaciones que el usuario NO tomo
pero dice que habria tomado.

Sus 13 explicaciones sobre los 13 disparos de la regla que se salto:
  - 11 veces: "no estaba pendiente del grafico pero si hubiese tomado la operacion"
  - R03 y R09: habria entrado, pero en otra vela y con otro stop -> no son
    la misma operacion, quedan fuera.

Ademas separa el tramo 08:00-09:00, que dice que no operaria por preferencia
("la primera hora es la de apertura y no me gusta entrar directamente").
"""
import numpy as np, pandas as pd

COSTE, EUR = 1.2, 150.0

# --- lo que el opero -------------------------------------------------------
ver = pd.read_csv("data/agosto_verificacion.csv")
ver = ver[ver.suyo != "abierta"].copy()          # T21 quedo sin resolver
ver["Rf"] = np.where(ver.mot.isin(["TP", "SL"]), ver.R,
                     np.where(ver.suyo == "TP", ver.rr, -1.0))
ver["fecha"] = pd.to_datetime(ver.fecha)
suyas = ver[["id", "fecha", "Rf", "rgo"]].rename(columns={"Rf": "R", "rgo": "riesgo"})
suyas["origen"] = "suya"

# --- los disparos de la regla que se salto ---------------------------------
t = pd.read_csv("data/asia_nivel.csv", parse_dates=["ts"])
a = t[t.ts >= "2026-08-01"].copy()
a["fecha"] = pd.to_datetime(a.dia)
a["hm"] = a.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.hour * 100 \
        + a.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.minute

SUYOS = {("2026-08-03", -1), ("2026-08-06", -1), ("2026-08-11", -1)}   # y 07-ago tipo B
saltados = a[~a.apply(lambda r: (str(r.dia), r.lado) in SUYOS, axis=1)]
saltados = saltados[~((saltados.dia == "2026-08-07") & (saltados.tipo == "B"))]
# R03 = 07-ago tipo A ; R09 = 17-ago tipo A  -> dijo que habria entrado de otra forma
once = saltados[saltados.tipo != "A"].copy()
once["origen"] = "no tomada"
once = once[["dia", "fecha", "R", "riesgo", "hm", "origen"]].rename(columns={"dia": "id"})

assert len(once) == 11, len(once)

def bloque(nom, d):
    d = d.copy()
    d["neto"] = d.R - COSTE / d.riesgo
    dia = d.groupby("fecha").agg(R=("R", "mean"), neto=("neto", "mean"))
    ee = dia.neto.std(ddof=1) / np.sqrt(len(dia))
    print(f"\n{nom}")
    print(f"  {len(d)} operaciones en {len(dia)} dias  ·  acierto {100*(d.R>0).mean():.1f} %")
    print(f"  por dia: bruta {dia.R.mean():+.3f} · neta {dia.neto.mean():+.3f} ± {ee:.3f}"
          f" (z {dia.neto.mean()/ee:+.2f}) · {int((dia.neto>0).sum())} de {len(dia)} en positivo")
    print(f"  en euros a {EUR:.0f} EUR de riesgo: {d.neto.sum()*EUR:+.0f} EUR")

print("=" * 78)
print("AGOSTO 2026 · lo que opero y lo que dice que habria operado")
print("=" * 78)
print(f"\nLAS 11 QUE DICE QUE SI HABRIA TOMADO")
print(f"  TP {int((once.R>0).sum())} · SL {int((once.R<0).sum())}"
      f"  ->  acierto {100*(once.R>0).mean():.1f} %   ·  R bruta media {once.R.mean():+.3f}")
pre9 = once[once.hm < 900]
print(f"  de esas, {len(pre9)} son entre las 08:00 y las 09:00"
      f" (TP {int((pre9.R>0).sum())} · SL {int((pre9.R<0).sum())})")

col = ["fecha", "R", "riesgo"]
bloque("TAL COMO LO OPERO", suyas[col])
bloque("SI HUBIESE ESTADO DELANTE SIEMPRE  (+11)", pd.concat([suyas[col], once[col]]))
bloque("SI HUBIESE ESTADO DELANTE PERO SOLO DESDE LAS 09:00  (+6)",
       pd.concat([suyas[col], once[once.hm >= 900][col]]))
