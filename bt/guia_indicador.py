"""Dos momentos reales de una misma mañana para explicar el indicador: uno en su
mejor caja (cuerpo normal, lejos del nivel) y otro en la peor (cuerpo lleno).

  python3 bt/guia_indicador.py [AAAA-MM-DD]
"""
import json, sys, numpy as np, pandas as pd
TZ, U, INI = "Europe/Madrid", 1e-4, 480
MES = pd.Timestamp(sys.argv[1] if len(sys.argv) > 1 else "2026-06-01")

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
# se recorta por UTC antes de convertir: asi no se tocan los 2,4 M de filas
m1 = m1[(m1.ts >= MES) & (m1.ts <= MES + pd.Timedelta(days=45))]
m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date
m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
print(f"{m1.dia.nunique()} días cargados desde {MES.date()}")

def dia_util(DIA, m1d):
  a = m1d[m1d["min"] < INI]
  if len(a) < 300: return None
  hi, lo = float(a.high.max()), float(a.low.min())
  s = m1d[m1d["min"] >= INI].reset_index(drop=True)
  if len(s) < 120: return None
  H, L, C, O, M = (s.high.to_numpy(), s.low.to_numpy(), s.close.to_numpy(),
                   s.open.to_numpy(), s["min"].to_numpy())

  def foto(i):
      o5, c5 = float(O[i-4]), float(C[i])
      h5, l5 = float(H[i-4:i+1].max()), float(L[i-4:i+1].min())
      rango = max(h5 - l5, 1e-9)
      k = max(0, i-9)
      stopL, stopC = float(L[k:i+1].min()), float(H[k:i+1].max())
      v = []
      for q in range(max(4, i-129), i+1):
          if M[q] % 5 != 4: continue
          v.append([int(M[q-4]), round(float(O[q-4]),5), round(float(H[q-4:q+1].max()),5),
                    round(float(L[q-4:q+1].min()),5), round(float(C[q]),5)])
      return dict(dia=str(DIA), minuto=int(M[i])+1, pct=round(abs(c5-o5)/rango*100),
          toca=bool(l5 <= hi <= h5 or l5 <= lo <= h5), rango_p=round(rango/U,1),
          asiaHi=round(hi,5), asiaLo=round(lo,5),
          sesHi=round(float(H[:i+1].max()),5), sesLo=round(float(L[:i+1].min()),5),
          precio=round(c5,5), stopL=round(stopL,5), stopC=round(stopC,5),
          objL=round(c5 + 2*(c5-stopL),5), objC=round(c5 - 2*(stopC-c5),5),
          pipsL=round((c5-stopL)/U,1), pipsC=round((stopC-c5)/U,1), velas=v)

  cand = [foto(i) for i in range(24, len(s)) if M[i] % 5 == 4 and 520 <= M[i] <= 660]
  ok = [f for f in cand if not f["toca"] and 3 <= f["pipsL"] <= 12
        and 3 <= f["pipsC"] <= 12 and f["rango_p"] >= 3]
  a = [f for f in ok if f["pct"] <= 30]
  b = [f for f in ok if f["pct"] >= 80]
  return (a[0], b[0]) if a and b else None

mejor = peor = None
for DIA, g in m1.groupby("dia"):
  r = dia_util(DIA, g)
  if r: mejor, peor = r; break
assert mejor, "ningún día con los dos casos"
for n, f in (("mejor", mejor), ("peor", peor)):
    print(f"  {n}: {f['minuto']//60:02d}:{f['minuto']%60:02d} · cuerpo {f['pct']} % · "
          f"rango {f['rango_p']} p · stop compra {f['pipsL']} p · venta {f['pipsC']} p · "
          f"{len(f['velas'])} velas")
json.dump({"mejor": mejor, "peor": peor}, open("data/guia_indicador.json","w"))
