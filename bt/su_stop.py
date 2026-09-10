"""Donde pone el stop, medido. La regla lo pone en el extremo de la vela del
disparo -2,6 p- y el pone 5,5. Si esa distancia es describible, la mitad
mecanizable de lo que hace ya esta escrita.

  python3 bt/su_stop.py
"""
import numpy as np, pandas as pd
U, TZ, INI = 1e-4, "Europe/Madrid", 480
t = pd.read_csv("data/operaciones_150.csv"); t["dia"] = pd.to_datetime(t.dia).dt.date
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(set(t.dia))]
v = m1.assign(b=(m1["min"]//5)*5).groupby(["dia","b"]).agg(
      h=("high","max"), l=("low","min"), n=("close","size")).reset_index()
v = v[v.n >= 3]; v["cierre_min"] = v.b + 5
V = {(r.dia, r.cierre_min): (r.h, r.l) for r in v.itertuples()}
M = {(r.dia, r["min"]): (r.high, r.low) for _, r in m1.iterrows()}

def extremo(dia, cm, k, lado):
    """Extremo contrario de las ultimas k velas de M5 ya cerradas."""
    xs = [V[(dia, cm-5*i)] for i in range(k) if (dia, cm-5*i) in V]
    if not xs: return None
    return min(x[1] for x in xs) if lado > 0 else max(x[0] for x in xs)

fil = []
for r in t.itertuples():
    cm = (r.ent_min//5)*5 if r.ent_min % 5 else r.ent_min      # ultima M5 cerrada
    if cm > r.ent_min: cm -= 5
    d = dict(rgo=r.rgo)
    for k in (1, 2, 3):
        e = extremo(r.dia, cm, k, r.lado)
        d[f"m5x{k}"] = abs(r.ent - e)/U if e is not None else np.nan
    # extremo de los ultimos 5, 10 y 15 minutos de M1
    for k in (5, 10, 15):
        xs = [M[(r.dia, r.ent_min-i)] for i in range(k) if (r.dia, r.ent_min-i) in M]
        if not xs: d[f"m1x{k}"] = np.nan; continue
        e = min(x[1] for x in xs) if r.lado > 0 else max(x[0] for x in xs)
        d[f"m1x{k}"] = abs(r.ent - e)/U
    fil.append(d)
D = pd.DataFrame(fil)
print(f"su stop: mediana {D.rgo.median():.1f} p   ·   media {D.rgo.mean():.1f}\n")
print(f"  {'referencia':34s} {'mediana':>8s} {'error medio':>12s} {'|error| med':>12s} "
      f"{'correlación':>12s}")
print("  " + "-"*82)
for c, nom in (("m5x1","extremo de la vela de M5 del disparo"),
               ("m5x2","extremo de las 2 últimas de M5"),
               ("m5x3","extremo de las 3 últimas de M5"),
               ("m1x5","extremo de los últimos 5 min de M1"),
               ("m1x10","extremo de los últimos 10 min de M1"),
               ("m1x15","extremo de los últimos 15 min de M1")):
    s = D[[c,"rgo"]].dropna()
    print(f"  {nom:34s} {s[c].median():7.1f}p {(s.rgo-s[c]).mean():+11.2f}p "
          f"{(s.rgo-s[c]).abs().median():11.2f}p {np.corrcoef(s[c], s.rgo)[0,1]:12.2f}")
print(f"\n  su stop menos el extremo de la vela del disparo: mediana "
      f"{(D.rgo-D.m5x1).median():+.2f} p  ·  lo pone por FUERA en "
      f"{100*(D.rgo > D.m5x1).mean():.0f} % de los casos")
