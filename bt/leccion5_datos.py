"""Datos para la leccion 5: donde va el stop.

Tres cosas:
  1 la excursion adversa maxima de cada operacion, medida en el riesgo base
    (el extremo del barrido). Es "cuanto se fue en tu contra antes de girar".
  2 el agregado para 17 anchos de stop distintos, para el deslizador.
  3 unos cuantos casos reales para el navegador.

  python3 bt/leccion5_datos.py
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

BUF = [round(x,2) for x in np.arange(0, 1.55, 0.10)]     # 0 % .. 150 %
ops, casos = [], []
for i in range(2, len(B)-7):
    r1 = h[i-1]-l[i-1]
    if r1 <= 0: continue
    if h[i] > h[i-1] and c[i] < h[i-1]: lado, ext, obj, borde = -1, h[i], l[i-1], h[i-1]
    elif l[i] < l[i-1] and c[i] > l[i-1]: lado, ext, obj, borde = +1, l[i], h[i-1], l[i-1]
    else: continue
    ent = c[i]; base = abs(ent-ext)
    if base < 2e-4 or (obj-ent)*lado <= 0: continue
    j0 = int(np.searchsorted(mt, ti[i]+np.timedelta64(240,"m"))); j1 = min(j0+HOR, len(mt))
    if j1 <= j0+3: continue
    hh, ll = mh[j0:j1], ml[j0:j1]
    a = np.flatnonzero(hh >= obj) if lado > 0 else np.flatnonzero(ll <= obj)
    ia = int(a[0]) if len(a) else 10**9
    # excursion adversa maxima ANTES de llegar al objetivo (o hasta el final)
    fin = ia if ia < 10**9 else len(hh)-1
    peor = (ent - ll[:fin+1].min())*lado if lado > 0 else (hh[:fin+1].max() - ent)*lado*-1
    peor = (ent - ll[:fin+1].min()) if lado > 0 else (hh[:fin+1].max() - ent)
    ops.append([base/U, peor/base, int(ia < 10**9), abs(obj-ent)/base,
                (float(mc[j1-1])-ent)*lado/base, abs(ent-borde)/base])
    if len(casos) < 60 and pd.Timestamp(ti[i]).year == 2026 and base > 8e-4:
        casos.append({"t": pd.Timestamp(ti[i]).strftime("%d/%m %H:%M"), "lado": lado,
            "rango":[round(l[i-1],5), round(h[i-1],5)], "ent": round(ent,5),
            "ext": round(ext,5), "obj": round(obj,5), "borde": round(borde,5),
            "base": round(base/U,1), "peor": round(peor/base,2),
            "gana": int(ia < 10**9),
            "velas": [[round(o[k],5), round(h[k],5), round(l[k],5), round(c[k],5)]
                      for k in range(i-2, min(i+6, len(B)))], "iv": 2})
A = np.array(ops)          # base_pips, peor/base, llega_obj, rr_base, mtm, borde/base
# --- agregado por ancho de stop
agg = []
for k in BUF:
    rgo = A[:,0]*(1+k)                       # en pips
    rr  = A[:,3]/(1+k)
    # gana si el objetivo se alcanza Y la excursion adversa no supero el stop
    gana = (A[:,2] == 1) & (A[:,1] <= (1+k))
    perd = A[:,1] > (1+k)
    R = np.where(gana, rr, np.where(perd, -1.0, A[:,4]/(1+k)))
    agg.append(dict(buf=k, riesgo=round(rgo.mean(),1), coste=round((COSTE/rgo).mean(),4),
                    rr=round(rr.mean(),2), acierto=round(gana.mean(),4),
                    geo=round((1/(1+rr)).mean(),4), bruta=round(R.mean(),4),
                    neta=round((R-COSTE/rgo).mean(),4)))
# --- la opcion del borde, aparte
rgo_b = A[:,0]*A[:,5]; ok = A[:,5] > 0.05
rr_b = A[ok,3]/A[ok,5]
gana_b = (A[ok,2]==1) & (A[ok,1] <= A[ok,5]); perd_b = A[ok,1] > A[ok,5]
Rb = np.where(gana_b, rr_b, np.where(perd_b, -1.0, A[ok,4]/A[ok,5]))
borde = dict(n=int(ok.sum()), riesgo=round(rgo_b[ok].mean(),1),
             coste=round((COSTE/rgo_b[ok]).mean(),4), rr=round(rr_b.mean(),2),
             acierto=round(gana_b.mean(),4), bruta=round(Rb.mean(),4),
             neta=round((Rb-COSTE/rgo_b[ok]).mean(),4))
# --- histograma de la excursion adversa, solo de las que ACABAN llegando al objetivo
gan = A[A[:,2]==1, 1]
bins = np.arange(0, 3.05, 0.15)
hist = np.histogram(np.clip(gan,0,3), bins=bins)[0].tolist()
D = {"agg": agg, "borde": borde, "casos": casos, "n": len(A),
     "hist": {"bins": [round(x,2) for x in bins.tolist()], "v": hist,
              "n": int((A[:,2]==1).sum())},
     "pct": {str(p): round(float(np.percentile(gan, p)),2) for p in (50,70,80,90,95)}}
open("data/leccion5.json","w").write(json.dumps(D, separators=(",",":")))
print(f"{len(A)} CRT · {len(casos)} casos · JSON listo\n")
print(f"  {'colchon':>8} {'riesgo':>8} {'coste':>7} {'R:R':>6} {'acierto':>8} {'BRUTA':>9} {'NETA':>9}")
for r in agg[::3]:
    print(f"  {r['buf']:>7.0%} {r['riesgo']:>7.1f}p {r['coste']:>6.1%} {r['rr']:>6.2f} "
          f"{r['acierto']:>7.1%} {r['bruta']:>+9.4f} {r['neta']:>+9.4f}")
print(f"\n  de las que acaban llegando al objetivo, cuanto se fueron en contra antes:")
for p,v in D["pct"].items(): print(f"    percentil {p}: {v} veces el riesgo base")
