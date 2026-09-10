"""Sesiones para el examen: 08:00-11:30 hora de Madrid, elegidas al azar.

Regla de construccion, para que no pueda colarse el futuro:
  - del pasado se mandan velas YA CERRADAS antes de las 08:00 (H4, M15, M5)
  - de la sesion se manda SOLO M1, y el navegador construye con ella las velas
    de M5, M15 y H4 segun avanza el cursor. Asi la vela en formacion es real y
    nada posterior al minuto actual existe en el fichero.
  - el fichero se corta en las 11:30. No hay nada despues.

  python3 bt/examen_datos.py
"""
import json, sys, numpy as np, pandas as pd

TZ = "Europe/Madrid"
SEMILLA = int(sys.argv[1]) if len(sys.argv) > 1 else 20260901
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20
SUFIJO  = sys.argv[3] if len(sys.argv) > 3 else ""
EXCLUYE = set()
for f in sys.argv[4:]:                       # dias ya usados en otro bloque
    EXCLUYE |= {pd.Timestamp(v).date() for v in json.load(open(f)).values()}
INI, FIN, PRE = 800, 1130, 600        # sesion, y desde que hora se manda M1
H_H4, H_M15, H_M5 = 60, 80, 96        # velas cerradas de historia

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date
m1["hm"] = m1["loc"].dt.hour*100 + m1["loc"].dt.minute
P = lambda x: int(round(float(x)*100000))

def velas(d, minutos):
    """Agrega a `minutos`, devolviendo solo velas con datos suficientes."""
    g = d.set_index("loc").resample(f"{minutos}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return g[g.n >= max(1, minutos*0.4)].reset_index().rename(columns={"loc": "t"})

# dias candidatos: laborables con Asia completa y sesion completa
ok = []
for dia, g in m1.groupby("dia"):
    if pd.Timestamp(dia).weekday() > 4: continue
    a = g[g.hm < INI]
    s = g[(g.hm >= INI) & (g.hm <= FIN)]
    if len(a) < 420 or len(s) < 200: continue      # Asia casi entera y sesion entera
    if dia in EXCLUYE: continue
    ok.append(dia)
print(f"{len(ok):,} días elegibles")

rng = np.random.default_rng(SEMILLA)
elegidos = sorted(rng.choice(len(ok), size=N, replace=False))
sesiones = []
for k, idx in enumerate(elegidos, 1):
    dia = ok[idx]
    t0 = pd.Timestamp(dia) + pd.Timedelta(hours=INI//100)
    ventana = m1[(m1["loc"] >= t0 - pd.Timedelta(days=25)) & (m1["loc"] < t0)]
    hist = m1[(m1.dia == dia) & (m1.hm < INI)]
    ses  = m1[(m1.dia == dia) & (m1.hm >= INI) & (m1.hm <= FIN)]
    asia = m1[(m1.dia == dia) & (m1.hm < INI)]        # 00:00-08:00
    if asia.empty: continue

    def cierra(minutos, cuantas):
        v = velas(ventana, minutos)
        v = v[v.t + pd.Timedelta(minutes=minutos) <= t0]   # solo CERRADAS
        v = v.tail(cuantas)
        return [[int((r.t - t0).total_seconds()//60), P(r.o), P(r.h), P(r.l), P(r.c)]
                for r in v.itertuples()]

    m1v = pd.concat([hist[hist.hm >= PRE], ses])
    barras = [[int((r.loc_ - t0).total_seconds()//60), P(r.open), P(r.high), P(r.low), P(r.close)]
              for r in m1v.rename(columns={"loc":"loc_"}).itertuples()]
    sesiones.append(dict(n=k, hi=P(asia.high.max()), lo=P(asia.low.min()),
                         h4=cierra(240, H_H4), m15=cierra(15, H_M15),
                         m5=cierra(5, H_M5), m1=barras))
    print(f"  {k:2d}  {dia}  m1 {len(barras):4d}  h4 {len(sesiones[-1]['h4']):3d}  "
          f"m15 {len(sesiones[-1]['m15']):3d}  m5 {len(sesiones[-1]['m5']):3d}")

# el fichero de respuestas, que NO se publica
claves = {s["n"]: d for s, d in zip(sesiones, [ok[i] for i in elegidos])}
json.dump({str(k): str(v) for k, v in claves.items()},
          open(f"data/examen_dias{SUFIJO}.json", "w"), indent=1)
txt = json.dumps(sesiones, separators=(",", ":"))
open(f"data/examen_sesiones{SUFIJO}.json", "w").write(txt)
print(f"\n{len(sesiones)} sesiones · {len(txt)/1024:,.0f} KB")
print(f"comprobación de corte: el minuto más alto es {max(b[0] for s in sesiones for b in s['m1'])}"
      f" (11:30 son {(FIN//100)*60 + FIN%100 - (INI//100)*60})")
