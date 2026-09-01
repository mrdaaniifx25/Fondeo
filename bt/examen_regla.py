"""La regla mecanica corrida SOLO en los 20 dias del examen, con su mismo trato.

Misma señal que bt/asia_nivel.py -niveles de Asia, gatillos A y B, armado y
rearme, entrada al cierre de la vela de M5, stop en el extremo de la vela
anterior, objetivo 1:2-, pero cortando a las 11:30 igual que el examen y
cerrando a mercado lo que quede abierto.

  python3 bt/examen_regla.py
"""
import json, numpy as np, pandas as pd
from math import sqrt, erf

U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"
VENTANA, REARME, ATRAS = (800, 1130), 10.0, 10
DIAS = {pd.Timestamp(v).date() for v in json.load(open("data/examen_dias.json")).values()}

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date
m1 = m1[m1.dia.isin(DIAS)].reset_index(drop=True)
m1["hm"] = m1["loc"].dt.hour*100 + m1["loc"].dt.minute
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date; v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
O,H,L,C = v.o.to_numpy(), v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()
T1 = m1["loc"].to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()

def gatillo(i, niv, lado):
    o, c = O[i], C[i]
    if not ((c > o) if lado > 0 else (c < o)): return None
    if (min(o,c) >= niv) if lado > 0 else (max(o,c) <= niv): return "A"
    for j in range(i-1, max(i-1-ATRAS, -1), -1):
        if (lado > 0) == (C[j] >= O[j]): continue
        ref = max(O[j], C[j]) if lado > 0 else min(O[j], C[j])
        return "B" if ((c > ref) if lado > 0 else (c < ref)) else None
    return None

filas = []
for dia, g in v.groupby("dia"):
    a = g[g.hm < 800]
    if len(a) < 60: continue
    hi, lo = float(a.h.max()), float(a.l.min())
    W = g[(g.hm >= VENTANA[0]) & (g.hm < VENTANA[1])]
    if len(W) < 5: continue
    for niv in (hi, lo):
        armado = True
        for i in range(W.index[0], W.index[-1] + 1):
            toca = L[i] <= niv <= H[i]
            if not toca and min(abs(H[i]-niv), abs(L[i]-niv))/U > REARME: armado = True
            if not (armado and toca): continue
            for lado in (1, -1):
                if gatillo(i, niv, lado) is None: continue
                ent, stp = C[i], (L[i-1] if lado > 0 else H[i-1])
                rgo = abs(ent - stp)
                if rgo <= 0: break
                filas.append(dict(dia=dia, i=int(i), lado=lado, ent=ent, sl=stp,
                                  tp=ent + 2*rgo*lado, rgo=rgo/U,
                                  ts=v.b5.iloc[i] + pd.Timedelta(minutes=5)))
                armado = False
                break

t = pd.DataFrame(filas)
# resolucion en M1, cortando a las 11:30 igual que el examen
out = []
for r in t.itertuples():
    k = int(np.searchsorted(T1, np.datetime64(r.ts)))
    fin = int(np.searchsorted(T1, np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(hours=11, minutes=30))))
    fin = min(max(fin, k+1), len(T1))
    hh, ll = H1[k:fin], L1[k:fin]
    largo = r.lado > 0
    gs, gt = ((ll <= r.sl, hh >= r.tp) if largo else (hh >= r.sl, ll <= r.tp))
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    itp = int(np.argmax(gt)) if gt.any() else 10**9
    if isl == 10**9 and itp == 10**9:
        sal = C1[fin-1]; R = ((sal-r.ent) if largo else (r.ent-sal))/U/r.rgo; mot = "cierre"
    elif isl <= itp: R, mot = -1.0, "SL"
    else: R, mot = 2.0, "TP"
    out.append((r.dia, r.ts, r.lado, R, mot, r.rgo, R - COSTE/r.rgo))
d = pd.DataFrame(out, columns=["dia","ts","lado","R","motivo","rgo","neta"])

z = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x)))
p2 = lambda zz: 2*(1-0.5*(1+erf(abs(zz)/sqrt(2))))
res = d[d.motivo != "cierre"]
print("="*68); print("LA REGLA MECÁNICA EN LOS MISMOS 20 DÍAS"); print("="*68)
print(f"  disparos               {len(d)}   en {d.dia.nunique()} días  ·  {len(d)/20:.1f} por sesión")
print(f"  resueltas              {len(res)}  ·  TP {(res.motivo=='TP').sum()} · SL {(res.motivo=='SL').sum()}")
ac = (res.motivo=='TP').mean(); se = sqrt((1/3)*(2/3)/len(res))
print(f"  ACIERTO                {100*ac:.1f} %   ·   z contra el 33,3 % = {(ac-1/3)/se:+.2f}")
print(f"  stop mediano           {d.rgo.median():.1f} p")
print(f"  R BRUTA por disparo    {d.R.mean():+.3f}")
print(f"  R NETA  por disparo    {d.neta.mean():+.3f}   ·   z = {z(d.neta.to_numpy()):+.2f}")
print(f"  suma neta              {d.neta.sum():+.2f} R  en 20 días")
por = d.groupby("dia").neta.sum().reindex(sorted(DIAS)).fillna(0)
print(f"  por sesión             {por.mean():+.3f}   ·   z = {z(por.to_numpy()):+.2f}")
d.to_csv("data/examen_regla.csv", index=False)
