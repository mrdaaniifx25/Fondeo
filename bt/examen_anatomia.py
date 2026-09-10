"""Los 23 momentos del examen, abiertos y comparados con los 33 de la regla.

EXPLORATORIO. Con 23 casos y una docena de variables, algo saldra "significativo"
por azar. Nada de aqui es un hallazgo: son hipotesis para el segundo bloque.

  python3 bt/examen_anatomia.py
"""
import json, re, numpy as np, pandas as pd
from math import sqrt

U, TZ = 0.0001, "Europe/Madrid"
dias = {int(k): pd.Timestamp(v).date() for k, v in json.load(open("data/examen_dias.json")).items()}

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date
m1 = m1[m1.dia.isin(set(dias.values()))].reset_index(drop=True)
m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute

POR_DIA = {d: g.reset_index(drop=True) for d, g in m1.groupby("dia")}
ASIA = {d: (float(g[g["min"] < 480].high.max()), float(g[g["min"] < 480].low.min()))
        for d, g in POR_DIA.items()}

def rasgos(dia, minuto, lado):
    """Todo lo que se puede saber en el instante de entrar, sin mirar adelante."""
    g = POR_DIA[dia]
    hi, lo = ASIA[dia]
    ses = g[(g["min"] >= 480) & (g["min"] <= minuto)]
    if len(ses) < 2: return None
    p = float(ses.close.iloc[-1])
    rango = (hi - lo)/U
    # ¿se ha roto ya algun nivel de Asia en lo que va de sesion?
    roto_hi = bool((ses.high > hi).any()); roto_lo = bool((ses.low < lo).any())
    d_hi, d_lo = (p - hi)/U, (p - lo)/U
    cerca_alto = abs(d_hi) <= abs(d_lo)
    nivel = hi if cerca_alto else lo
    dist = abs(p - nivel)/U
    # de que lado del nivel cercano esta, y si opera hacia el o en su contra
    fuera = (p > hi) if cerca_alto else (p < lo)
    # la vela de M5 ya cerrada justo antes
    b5 = ses[ses["min"] < (minuto//5)*5]
    v5 = ses[(ses["min"] >= (minuto//5)*5 - 5) & (ses["min"] < (minuto//5)*5)]
    cuerpo5 = (float(v5.close.iloc[-1]) - float(v5.open.iloc[0]))/U if len(v5) else np.nan
    # recorrido reciente y volatilidad
    u30 = ses.tail(30)
    rango30 = (float(u30.high.max()) - float(u30.low.min()))/U
    mov08 = (p - float(ses.close.iloc[0]))/U
    # minutos desde el primer toque del nivel cercano en la sesion
    toca = ses[(ses.low <= nivel) & (ses.high >= nivel)]
    desde = int(minuto - toca["min"].iloc[0]) if len(toca) else -1
    return dict(hora=minuto, lado=lado, rango_asia=rango, dist_nivel=dist,
                nivel="alto" if cerca_alto else "bajo", fuera_del_rango=fuera,
                roto=roto_hi or roto_lo, pos_rango=100*(p-lo)/(hi-lo),
                cuerpo_m5=cuerpo5, rango30=rango30, mov_desde_08=mov08,
                min_desde_toque=desde,
                a_favor_ruptura=(lado > 0) == cerca_alto)

# --- sus 23
su = []
for l in open("data/examen_respuestas_1.txt"):
    m = re.match(r"S(\d+) · (\d\d):(\d\d) (COMPRA|VENTA) ent \S+ sl \S+ \(([\d.]+)p\) tp \S+ -> \S+ ([+-][\d.]+) R", l.strip())
    if not m: continue
    s = int(m.group(1)); mm = int(m.group(2))*60 + int(m.group(3))
    lado = 1 if m.group(4) == "COMPRA" else -1
    r = rasgos(dias[s], mm, lado)
    if r: r.update(quien="él", s=s, rgo=float(m.group(5)), R=float(m.group(6))); su.append(r)

# --- los 33 de la regla
reg = pd.read_csv("data/examen_regla.csv"); reg["ts"] = pd.to_datetime(reg.ts)
rr = []
for r in reg.itertuples():
    d = r.ts.date(); mm = r.ts.hour*60 + r.ts.minute
    x = rasgos(d, mm, int(r.lado))
    if x: x.update(quien="regla", s=-1, rgo=r.rgo, R=r.R); rr.append(x)

d = pd.DataFrame(su + rr)
d.to_csv("data/examen_anatomia.csv", index=False)
A, B = d[d.quien == "él"], d[d.quien == "regla"]
print(f"{len(A)} suyas · {len(B)} de la regla\n")

NUM = ["hora","rango_asia","dist_nivel","pos_rango","cuerpo_m5","rango30",
       "mov_desde_08","min_desde_toque","rgo"]
print("="*94)
print("QUÉ SEPARA SUS MOMENTOS DE LOS DE LA REGLA")
print("="*94)
print(f"  {'':18s} {'él (mediana)':>14s} {'regla':>10s} {'dif':>9s} {'t':>7s}")
print("  " + "-"*66)
for c in NUM:
    a, b = A[c].dropna(), B[c].dropna()
    if len(a) < 3 or len(b) < 3: continue
    ee = sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    t = (a.mean()-b.mean())/ee if ee > 0 else 0
    print(f"  {c:18s} {a.median():14.1f} {b.median():10.1f} "
          f"{a.mean()-b.mean():+9.1f} {t:+7.2f}")

print("\n  " + "-"*66)
for c in ["nivel","fuera_del_rango","roto","a_favor_ruptura"]:
    pa = 100*A[c].astype(str).eq(A[c].astype(str).mode()[0]).mean()
    print(f"  {c:18s} él: " + " · ".join(f"{k}={v}" for k,v in A[c].value_counts().items())
          + "   |   regla: " + " · ".join(f"{k}={v}" for k,v in B[c].value_counts().items()))

print("\n" + "="*94)
print("DENTRO DE SUS 23: QUÉ SEPARA LAS GANADORAS DE LAS PERDEDORAS")
print("="*94)
G, P = A[A.R > 0], A[A.R < 0]
print(f"  {len(G)} ganadoras · {len(P)} perdedoras")
print(f"  {'':18s} {'gana':>10s} {'pierde':>10s} {'dif':>9s} {'t':>7s}")
print("  " + "-"*58)
for c in NUM:
    g, p = G[c].dropna(), P[c].dropna()
    if len(g) < 3 or len(p) < 3: continue
    ee = sqrt(g.var(ddof=1)/len(g) + p.var(ddof=1)/len(p))
    t = (g.mean()-p.mean())/ee if ee > 0 else 0
    print(f"  {c:18s} {g.median():10.1f} {p.median():10.1f} {g.mean()-p.mean():+9.1f} {t:+7.2f}")
