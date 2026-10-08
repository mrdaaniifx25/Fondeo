"""Pre-registro docs/PREREGISTRO_techo_filtro.md

Cuanto puede valer, como maximo, un filtro que el no verbaliza.
Base: la celda verificada de bt/benjamin_regla.py (M2, niveles H1, sus horas).
14 variables observables al entrar. Mejor decil de cada una elegido CON TRAMPA
(se mira el resultado), mas un modelo sobre las 14 con prediccion fuera de
muestra. Si ni haciendo trampa se llega al umbral, no hay filtro que salve
la geometria.
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, HOR, PIV, ESP = 1e-4, 1.43, 24*60, 3, 30
M1M = np.timedelta64(1, "m")

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
mts = m1.ts.to_numpy("datetime64[ns]"); mh = m1.high.to_numpy()
ml = m1.low.to_numpy(); M = len(m1)
anos = (m1.ts.max()-m1.ts.min()).days/365.25

def velas(mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    return g[g.n >= max(1, mins*0.3)].reset_index()

V = {k: velas(k) for k in (2, 15, 60)}

def atr(d, n=14):
    h, l, c = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    a = np.full(len(tr), np.nan); a[n-1] = tr[:n].mean()
    for i in range(n, len(tr)): a[i] = (a[i-1]*(n-1)+tr[i])/n
    return a

def niveles(tf):
    d = V[tf]; h, l = d.h.to_numpy(), d.l.to_numpy()
    t = d.ts.to_numpy("datetime64[ns]"); out = []
    for i in range(PIV, len(d)-PIV):
        if h[i] == h[i-PIV:i+PIV+1].max(): out.append((t[i+PIV] + tf*M1M, h[i], -1, t[i]))
        if l[i] == l[i-PIV:i+PIV+1].min(): out.append((t[i+PIV] + tf*M1M, l[i], +1, t[i]))
    out.sort(key=lambda x: x[0])
    return (np.array([x[0] for x in out], dtype="datetime64[ns]"),
            np.array([x[1] for x in out]), np.array([x[2] for x in out], int),
            np.array([x[3] for x in out], dtype="datetime64[ns]"))

nt, npv, nls, nnac = niveles(60)

# --- dia previo y EMA 50 de M15, ambos cerrados antes de entrar ---
dia = (m1.set_index("ts").resample("D")
         .agg(h=("high","max"), l=("low","min"), n=("close","size")).dropna())
dia = dia[dia.n > 200]
dt_ = dia.index.to_numpy("datetime64[ns]") + np.timedelta64(1, "D")
pdh, pdl = dia.h.to_numpy(), dia.l.to_numpy()
atrd = pd.Series(pdh-pdl).rolling(20).mean().to_numpy()

d15 = V[15]; e15 = d15.c.ewm(span=50, adjust=False).mean().to_numpy()
t15 = d15.ts.to_numpy("datetime64[ns]") + 15*M1M

# ------------------------------------------------------------------
d = V[2]
ts = d.ts.to_numpy("datetime64[ns]")
o_, h, l, c = (d[x].to_numpy() for x in ("o","h","l","c"))
N = len(d); A2 = atr(d)
al = np.zeros(N, bool); ba = np.zeros(N, bool)
al[2:] = l[2:] > h[:-2]; ba[2:] = h[2:] < l[:-2]
loc = pd.DatetimeIndex(ts).tz_localize("UTC").tz_convert("Europe/Madrid")
hm = loc.hour.to_numpy() + loc.minute.to_numpy()/60
dow = loc.dayofweek.to_numpy()
vent = ((hm >= 9) & (hm < 11)) | ((hm >= 14) & (hm < 16.5))
dnorm = pd.DatetimeIndex(ts).normalize().to_numpy()

CACHE = "data/techo_filtro_ops.parquet"
import os
filas = []; usado = set()
for k in ([] if os.path.exists(CACHE) else range(3, N-1)):
    j = int(np.searchsorted(nt, ts[k], "right"))
    if j == 0: continue
    for q in range(max(0, j-40), j):
        lado = nls[q]; niv = npv[q]
        if not ((h[k] > niv) if lado < 0 else (l[k] < niv)): continue
        clave = (dnorm[k], round(float(niv), 5))
        if clave in usado: continue
        kf = -1
        for z in range(k, min(k+ESP, N)):
            if (ba[z] if lado < 0 else al[z]): kf = z; break
        if kf < 0: continue
        if not vent[kf]: continue
        P = c[kf]
        S = h[k:kf+1].max() if lado < 0 else l[k:kf+1].min()
        rgo = abs(S-P)
        if rgo <= 0: continue
        O = P - 2*rgo if lado < 0 else P + 2*rgo
        if lado < 0 and not (S > P > O): continue
        if lado > 0 and not (S < P < O): continue
        usado.add(clave)
        i0 = int(np.searchsorted(mts, ts[kf] + 2*M1M, "left"))
        if i0 >= M-2: continue
        a2 = A2[kf]
        if not np.isfinite(a2) or a2 <= 0: continue
        g = 0
        for x in range(i0, min(i0+HOR, M)):
            if lado < 0:
                if mh[x] >= S: break
                if ml[x] <= O: g = 1; break
            else:
                if ml[x] <= S: break
                if mh[x] >= O: g = 1; break
        # ---------- las 14 variables, todas cerradas en kf ----------
        exc = abs(S - niv)/a2                                   # 4
        edad = (ts[k] - nnac[q])/np.timedelta64(1, "h")         # 7
        w = slice(max(0, k-720), k)                             # 8: 24 h de M2
        toques = int(((l[w] <= niv) & (h[w] >= niv)).sum())
        espera = kf - k                                         # 9
        id_ = int(np.searchsorted(dt_, ts[kf], "right")) - 1    # 11 y 12
        if id_ < 20 or not np.isfinite(atrd[id_]) or atrd[id_] <= 0: continue
        dpd = min(abs(P-pdh[id_]), abs(P-pdl[id_]))/a2
        k0 = int(np.searchsorted(ts, dnorm[kf], "left"))
        rec = (h[k0:kf+1].max() - l[k0:kf+1].min())/atrd[id_]
        i15 = int(np.searchsorted(t15, ts[kf]+2*M1M, "right")) - 1
        if i15 < 50: continue
        dema = (P - e15[i15])/a2
        rg2 = h[kf]-l[kf]
        cuerpo = abs(c[kf]-o_[kf])/rg2 if rg2 > 0 else 0.0
        filas.append((g, rgo/U, hm[kf], dow[kf], a2/U, exc, rgo/U, rgo/a2,
                      edad, toques, espera, float(lado), dpd, rec, dema, cuerpo,
                      pd.Timestamp(ts[kf])))
        break

COLS = ["hora","dia_semana","ATR_M2","exceso_barrido","stop_pips","stop_ATR",
        "edad_nivel_h","toques_previos","velas_espera","compra_venta",
        "dist_dia_previo","recorrido_dia","dist_EMA50_M15","cuerpo_disparo"]
if os.path.exists(CACHE):
    D = pd.read_parquet(CACHE)
else:
    D = pd.DataFrame(filas, columns=["gana","rgo"]+COLS+["fecha"])
    D.to_parquet(CACHE)
D["cr"] = COSTE/D.rgo
D["Rn"] = np.where(D.gana == 1, 2.0, -1.0) - D.cr
print(f"operaciones: {len(D):,}  ({len(D)/anos:.0f}/año, {anos:.1f} años)")
print(f"acierto global {100*D.gana.mean():.1f} %   coste medio {100*D.cr.mean():.1f} %"
      f"   umbral {100*(1+D.cr.mean())/3:.1f} %   neta {D.Rn.mean():+.4f}\n")

def fila(nom, m):
    g = D.gana[m]; cr = D.cr[m]
    if len(g) < 200: return None
    um = 100*(1+cr.mean())/3
    se = 100*1.96*sqrt(g.mean()*(1-g.mean())/len(g))
    ac = 100*g.mean(); rn = D.Rn[m]
    print(f"  {nom:<26} n {len(g):>5,}  acierto {ac:>5.1f} ±{se:<4.1f}  "
          f"umbral {um:>5.1f}  margen {ac-um:>+6.1f}  neta {rn.mean():>+.4f}"
          f"{'   <<< PASA' if ac-se > um else ''}")
    return ac - um

print("="*104)
print("PRUEBA A · el mejor decil de cada variable, elegido CON TRAMPA")
print("="*104)
mejor = (-99, "")
for v in COLS:
    x = D[v].to_numpy()
    try: qs = pd.qcut(x, 10, labels=False, duplicates="drop")
    except ValueError: qs = pd.cut(x, 10, labels=False)
    mm = -99; best = None
    for q in np.unique(qs[~pd.isna(qs)]):
        m = (qs == q)
        if m.sum() < 200: continue
        ac = 100*D.gana[m].mean(); um = 100*(1+D.cr[m].mean())/3
        if ac - um > mm: mm, best = ac-um, m
    if best is None: continue
    r = fila(f"{v} (mejor decil)", best)
    if r is not None and r > mejor[0]: mejor = (r, v)
print(f"\n  el mejor de los 140 deciles: {mejor[1]}  margen {mejor[0]:+.1f} puntos")
print(f"  el procedimiento regala +2,3 de media y +2,9 una de cada veinte veces")

print("\n" + "="*104)
print("PRUEBA B · un modelo sobre las 14 a la vez, prediccion FUERA DE MUESTRA")
print("="*104)
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
X = D[COLS].to_numpy(); y = D.gana.to_numpy().astype(int)
p = np.full(len(D), np.nan)
BL = len(D)//6
for f in range(1, 6):                      # entrena con el pasado, predice el bloque siguiente
    tr = slice(0, f*BL); te = slice(f*BL, (f+1)*BL if f < 5 else len(D))
    mod = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05,
                                         max_leaf_nodes=15, random_state=7)
    mod.fit(X[tr], y[tr])
    p[te] = mod.predict_proba(X[te])[:, 1]
val = ~np.isnan(p)
print(f"  bloques: entrena con el pasado, predice el futuro. "
      f"{val.sum():,} operaciones predichas de {len(D):,}")
print(f"  AUC fuera de muestra: {roc_auc_score(y[val], p[val]):.4f}   (0,500 = no sabe nada)")
iv = np.where(val)[0]; ordn = iv[np.argsort(-p[iv])]
for frac, et in ((0.10, "decil superior"), (0.20, "quinto superior"),
                 (0.33, "tercio superior")):
    m = np.zeros(len(D), bool); m[ordn[:int(frac*len(iv))]] = True
    fila(f"modelo · {et}", m)
print("\n  el umbral de CADA celda sale de su propio coste medio; "
      "'margen' es acierto menos umbral")

print("\n" + "="*104)
print("Y LO OTRO · cuantas operaciones suyas harian falta para demostrar cada afirmacion")
print("="*104)
za, zb, p0 = 1.96, 0.84, 1/3
print(f"{'si acierta':>11} {'neta R/op':>10} {'%/mes al 1%':>12} {'n necesario':>12} {'~ tiempo':>12}")
print("-"*62)
for p1 in (0.36, 0.38, 0.40, 0.414, 0.45, 0.50, 0.60):
    n = ((za*sqrt(p0*(1-p0)) + zb*sqrt(p1*(1-p1)))/(p1-p0))**2
    rn = p1*2 - (1-p1) - 0.242          # su coste real, 5,9 p de stop
    print(f"{100*p1:>10.1f}% {rn:>+10.3f} {rn*60:>+11.1f}% {n:>12.0f} {n/60:>8.1f} meses")
print("\n  a 3 operaciones al dia y 20 dias al mes. Cuanto mas grande es lo que")
print("  afirma, MENOS operaciones hacen falta para comprobarlo.")
