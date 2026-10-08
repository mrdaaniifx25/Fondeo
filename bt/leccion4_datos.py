"""Datos para la leccion 4: las tres formas de entrar, en operaciones reales.

Para cada CRT se guardan las velas del entorno y lo que habria hecho cada una
de las tres entradas -al cierre, al 50 % de retroceso y al borde del rango-
incluyendo si la orden limitada llego a llenarse.

  python3 bt/leccion4_datos.py
"""
import json, numpy as np, pandas as pd

U, COSTE, HOR = 1e-4, 1.43, 240*3
M = pd.read_parquet("data/eurusd_m1.parquet"); M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
B = M.set_index("ts").shift(-1, freq="h").resample("240min", label="left", closed="left").agg(
    o=("open","first"), h=("high","max"), l=("low","min"),
    c=("close","last"), n=("close","size")).dropna()
B = B[B.n >= 72]; B.index = B.index + pd.Timedelta(hours=1)
o, h, l, c = (B[x].to_numpy() for x in "ohlc"); ti = B.index.to_numpy()
mh, ml, mc, mt = M.high.to_numpy(), M.low.to_numpy(), M.close.to_numpy(), M.ts.to_numpy()

casos = []
for i in range(2, len(B)-7):
    t = pd.Timestamp(ti[i])
    if t.year != 2026: continue
    r1 = h[i-1]-l[i-1]
    if r1 <= 0: continue
    if h[i] > h[i-1] and c[i] < h[i-1]: lado, stop, obj, borde = -1, h[i], l[i-1], h[i-1]
    elif l[i] < l[i-1] and c[i] > l[i-1]: lado, stop, obj, borde = +1, l[i], h[i-1], l[i-1]
    else: continue
    ent = c[i]; rgo = abs(ent-stop)
    if rgo < 5e-4 or (obj-ent)*lado <= 0: continue
    if h[i]-l[i] > r1: continue                       # regla de la leccion 3
    if abs(obj-ent)/rgo < 1.2: continue               # que sea operable
    j0 = int(np.searchsorted(mt, ti[i]+np.timedelta64(240,"m")))
    j1 = min(j0+HOR, len(mt))
    if j1 <= j0+10: continue
    hh, ll = mh[j0:j1], ml[j0:j1]

    def resuelve(px, k0=0):
        rg = abs(px-stop); rr = abs(obj-px)/rg
        a = np.flatnonzero(hh[k0:] >= obj) if lado > 0 else np.flatnonzero(ll[k0:] <= obj)
        b = np.flatnonzero(ll[k0:] <= stop) if lado > 0 else np.flatnonzero(hh[k0:] >= stop)
        ia = int(a[0]) if len(a) else 10**9
        ib = int(b[0]) if len(b) else 10**9
        if ia == ib == 10**9:
            R, q = (float(mc[j1-1])-px)*lado/rg, "abierta"
        else:
            R, q = (rr if ia < ib else -1.0), ("objetivo" if ia < ib else "stop")
        return dict(px=round(px,5), rr=round(rr,2), R=round(R,3),
                    neta=round(R - COSTE*U/rg, 3), q=q, rgo=round(rg/U,1))

    fila = {"t": t.strftime("%d/%m %H:%M"), "lado": lado,
            "rango": [round(l[i-1],5), round(h[i-1],5)],
            "stop": round(stop,5), "obj": round(obj,5),
            "velas": [[round(o[k],5), round(h[k],5), round(l[k],5), round(c[k],5)]
                      for k in range(i-2, min(i+6, len(B)))],
            "iv": 2,                                   # indice de la vela 2 en la lista
            "agr": resuelve(ent)}
    for nom, px in (("c50", ent - lado*rgo*0.5), ("cbo", borde)):
        toca = np.flatnonzero(ll <= px) if lado > 0 else np.flatnonzero(hh >= px)
        muere = np.flatnonzero(ll <= stop) if lado > 0 else np.flatnonzero(hh >= stop)
        if not len(toca) or (len(muere) and muere[0] < toca[0]):
            fila[nom] = {"px": round(px,5), "lleno": False}
        else:
            fila[nom] = dict(resuelve(px, int(toca[0])+1), lleno=True)
    casos.append(fila)

# resumen agregado sobre TODOS los CRT (no solo los filtrados), para las barras
tot = {"agr": [], "c50": [], "cbo": []}
for i in range(1, len(B)-1):
    r1 = h[i-1]-l[i-1]
    if r1 <= 0: continue
    if h[i] > h[i-1] and c[i] < h[i-1]: lado, stop, obj, borde = -1, h[i], l[i-1], h[i-1]
    elif l[i] < l[i-1] and c[i] > l[i-1]: lado, stop, obj, borde = +1, l[i], h[i-1], l[i-1]
    else: continue
    ent = c[i]; rgo = abs(ent-stop)
    if rgo < 2e-4 or (obj-ent)*lado <= 0: continue
    j0 = int(np.searchsorted(mt, ti[i]+np.timedelta64(240,"m"))); j1 = min(j0+HOR, len(mt))
    if j1 <= j0+3: continue
    hh, ll = mh[j0:j1], ml[j0:j1]
    def res2(px, k0=0):
        rg = abs(px-stop); rr = abs(obj-px)/rg
        a = np.flatnonzero(hh[k0:] >= obj) if lado > 0 else np.flatnonzero(ll[k0:] <= obj)
        b = np.flatnonzero(ll[k0:] <= stop) if lado > 0 else np.flatnonzero(hh[k0:] >= stop)
        ia = int(a[0]) if len(a) else 10**9; ib = int(b[0]) if len(b) else 10**9
        R = (float(mc[j1-1])-px)*lado/rg if ia == ib == 10**9 else (rr if ia < ib else -1.0)
        return [rr, R, R - COSTE*U/rg, int(ia < ib)]
    tot["agr"].append(res2(ent))
    for nom, px in (("c50", ent - lado*rgo*0.5), ("cbo", borde)):
        if abs(px-stop) < 1e-5: continue
        toca = np.flatnonzero(ll <= px) if lado > 0 else np.flatnonzero(hh >= px)
        muere = np.flatnonzero(ll <= stop) if lado > 0 else np.flatnonzero(hh >= stop)
        if len(toca) and not (len(muere) and muere[0] < toca[0]):
            tot[nom].append(res2(px, int(toca[0])+1))
agg = {}
n0 = len(tot["agr"])
for k, v in tot.items():
    a = np.array(v)
    agg[k] = dict(n=len(a), rr=round(a[:,0].mean(),2), bruta=round(a[:,1].mean(),4),
                  neta=round(a[:,2].mean(),4), acierto=round(a[:,3].mean(),4),
                  lleno=round(len(a)/n0,3))
D = {"casos": casos, "agg": agg}
open("data/leccion4.json","w").write(json.dumps(D, separators=(",",":")))
print(f"{len(casos)} casos de 2026 · agregado sobre {n0} CRT")
for k, v in agg.items():
    print(f"  {k}: n {v['n']:>5}  R:R {v['rr']:>5.2f}  acierto {v['acierto']:>6.1%}  "
          f"bruta {v['bruta']:>+7.4f}  neta {v['neta']:>+7.4f}  se llena {v['lleno']:.0%}")
