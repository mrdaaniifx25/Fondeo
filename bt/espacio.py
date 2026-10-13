"""Pre-registro docs/PREREGISTRO_espacio.md

Existe ALGUNA funcion de las 22 variables que prediga la direccion?
Sin condicionar a ningun patron: toda vela de M15 en sus horas entra.
"""
import numpy as np, pandas as pd
from math import sqrt

TZ, U, COSTE = "Europe/Madrid", 1e-4, 1.43
VENT = [(900, 1100), (1400, 1630)]
HOR = 4*60                                   # objetivo: 4 horas por delante

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
L = m1["loc"]; m1["dia"] = L.dt.normalize(); m1["hm"] = L.dt.hour*100 + L.dt.minute
M1C = m1.close.to_numpy(); M1T = m1["loc"].to_numpy("datetime64[ns]")
M1H, M1L = m1.high.to_numpy(), m1.low.to_numpy()

def atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    a = np.full(len(tr), np.nan); a[n-1] = tr[:n].mean()
    for i in range(n, len(tr)): a[i] = (a[i-1]*(n-1)+tr[i])/n
    return np.roll(a, 1)

def velas(mins):
    g = (m1.set_index("loc").resample(f"{mins}min", label="left", closed="left",
                                      origin="start_day")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    return g[g.n >= max(1, mins*0.3)].reset_index().rename(columns={"loc":"t"})

V15 = velas(15)
T = V15.t.to_numpy("datetime64[ns]"); O, H, Lo, C = (V15[x].to_numpy() for x in ("o","h","l","c"))
A15 = atr(H, Lo, C); A15L = pd.Series(atr(H, Lo, C, 96)).to_numpy()
HM = (pd.DatetimeIndex(V15.t).hour*100 + pd.DatetimeIndex(V15.t).minute).to_numpy()
DW = pd.DatetimeIndex(V15.t).dayofweek.to_numpy()
DIA = pd.DatetimeIndex(V15.t).normalize().to_numpy()
EMA = pd.Series(C).ewm(span=50, adjust=False).mean().to_numpy()

# --- rangos de referencia ---
asia = m1[m1.hm < 800].groupby("dia").agg(hi=("high","max"), lo=("low","min"), n=("close","size"))
asia = asia[asia.n > 120]
d_ = m1.groupby("dia").agg(hi=("high","max"), lo=("low","min"), op=("open","first"), n=("close","size"))
d_ = d_[d_.n > 200]
PDH = d_.hi.shift(1); PDL = d_.lo.shift(1)
ATRD = (d_.hi-d_.lo).rolling(20).mean().shift(1)
sem = m1.set_index("loc").resample("W").agg(hi=("high","max"), lo=("low","min"),
                                            n=("close","size"))
sem = sem[sem.n > 1000]; PWH = sem.hi.shift(1); PWL = sem.lo.shift(1)
swk = pd.DatetimeIndex(V15.t).to_period("W").to_timestamp("W")

filas, y, fechas = [], [], []
for i in range(100, len(V15)-1):
    if not any(a <= HM[i] < b for a, b in VENT): continue
    dd = pd.Timestamp(DIA[i])
    if dd not in asia.index or dd not in d_.index: continue
    a = A15[i]; ad = ATRD.get(dd, np.nan)
    if not (np.isfinite(a) and a > 0 and np.isfinite(ad) and ad > 0): continue
    ph, pl = PDH.get(dd, np.nan), PDL.get(dd, np.nan)
    if not (np.isfinite(ph) and np.isfinite(pl)): continue
    wk = pd.Timestamp(swk[i]); wh, wl = PWH.get(wk, np.nan), PWL.get(wk, np.nan)
    if not (np.isfinite(wh) and np.isfinite(wl)): continue
    ahi, alo = float(asia.hi[dd]), float(asia.lo[dd])
    if ahi <= alo: continue
    P = C[i]
    # ¿se ha barrido ya hoy?
    k0 = int(np.searchsorted(M1T, DIA[i], "left")); k1 = int(np.searchsorted(M1T, T[i], "right"))
    hoy_h, hoy_l = M1H[k0:k1], M1L[k0:k1]
    if len(hoy_h) < 10: continue
    j0 = int(np.searchsorted(M1T, T[i] + np.timedelta64(15, "m"), "left"))
    j1 = min(j0 + HOR, len(M1C))
    if j1 <= j0 + 30: continue
    ses = 0 if HM[i] < 1200 else 1
    ini = (900 if ses == 0 else 1400)
    desde = (HM[i]//100)*60 + HM[i] % 100 - ((ini//100)*60 + ini % 100)
    filas.append([ses, HM[i]//100, desde, DW[i],
                  (P-alo)/(ahi-alo), (ahi-alo)/a,
                  (P-ph)/a, (P-pl)/a, (P-wh)/a, (P-wl)/a,
                  float(hoy_h.max() > ahi), float(hoy_l.min() < alo),
                  float(hoy_h.max() > ph), float(hoy_l.min() < pl),
                  (P-C[i-4])/a, (P-C[i-16])/a, (P-C[i-96])/a,
                  a/U, a/A15L[i] if np.isfinite(A15L[i]) and A15L[i] > 0 else 1.0,
                  (P-float(d_.op[dd]))/a,
                  (hoy_h.max()-hoy_l.min())/ad, (P-EMA[i])/a])
    y.append(1 if M1C[j1-1] > P else 0)
    fechas.append(pd.Timestamp(T[i]))

COLS = ["sesion","hora","min_desde_apertura","dia_semana","pos_en_asia","ancho_asia",
        "dist_PDH","dist_PDL","dist_PWH","dist_PWL","asia_alto_barrido","asia_bajo_barrido",
        "PDH_barrido","PDL_barrido","mom_1h","mom_4h","mom_1d","ATR_M15","ATR_corto_largo",
        "dist_apertura","recorrido_dia","dist_EMA50"]
X = np.array(filas, float); y = np.array(y); F = pd.DatetimeIndex(fechas)
print(f"muestra: {len(X):,} velas de M15  ·  {F.min():%Y-%m} a {F.max():%Y-%m}")
print(f"base: sube el {100*y.mean():.2f} % de las veces\n")

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

def evalua(yy, et):
    p = np.full(len(X), np.nan); BL = len(X)//6; aucs = []
    for f in range(1, 6):
        tr = slice(0, f*BL); te = slice(f*BL, (f+1)*BL if f < 5 else len(X))
        mod = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05,
                                             max_leaf_nodes=31, random_state=3)
        mod.fit(X[tr], yy[tr]); p[te] = mod.predict_proba(X[te])[:, 1]
        aucs.append(roc_auc_score(yy[te], p[te]))
    v = ~np.isnan(p)
    auc = roc_auc_score(yy[v], p[v])
    print(f"  {et:<34} AUC {auc:.4f}   por bloque: "
          + " ".join(f"{a:.3f}" for a in aucs))
    return p, v, auc

print("="*104); print("EL MODELO SOBRE LAS 22 VARIABLES"); print("="*104)
p, v, auc = evalua(y, "todas las variables")
print("\n  CONTROLES")
rng = np.random.default_rng(5)
evalua(rng.permutation(y), "control · etiquetas barajadas")
Xf = X.copy(); ses_cols = [0,1,2,3,10,11,12,13]
X_full = X; X = X[:, ses_cols]
evalua(y, "sólo las variables de sesión")
X = X_full

print("\n" + "="*104); print("EL DECIL SUPERIOR · donde el modelo más confía"); print("="*104)
iv = np.where(v)[0]
for frac, et in ((0.05, "el 5 % superior"), (0.10, "el decil superior"),
                 (0.25, "el cuarto superior")):
    n = int(frac*len(iv))
    alto = iv[np.argsort(-p[iv])[:n]]; bajo = iv[np.argsort(p[iv])[:n]]
    print(f"  {et:<22} n {n:>5,}  sube el {100*y[alto].mean():>5.2f} %   "
          f"(el 'más bajista': sube el {100*y[bajo].mean():.2f} %)   "
          f"diferencia {100*(y[alto].mean()-y[bajo].mean()):>+5.2f} puntos")

print("\n" + "="*104); print("QUE VARIABLES USA"); print("="*104)
from sklearn.inspection import permutation_importance
mod = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05,
                                     max_leaf_nodes=31, random_state=3)
n0 = int(len(X)*0.7); mod.fit(X[:n0], y[:n0])
imp = permutation_importance(mod, X[n0:], y[n0:], n_repeats=5, random_state=1,
                             scoring="roc_auc")
for k in np.argsort(-imp.importances_mean)[:8]:
    print(f"  {COLS[k]:<24} {imp.importances_mean[k]:>+8.5f} ± {imp.importances_std[k]:.5f}")

print("\n" + "="*104)
print("LA CORRECCION QUE HACE FALTA · muestras que NO se solapan")
print("="*104)
print("  Velas de M15 con objetivo a 4 horas se solapan 16 veces. Las muestras no")
print("  son independientes y el AUC y los intervalos salen inflados. Se repite")
print("  tomando una vela de cada 16, que ya no comparten futuro.\n")
paso = 16
idx = np.arange(0, len(X), paso)
Xs, ys, Fs = X[idx], y[idx], F[idx]
print(f"  muestra independiente: {len(Xs):,} velas (de {len(X):,})")

def evalua_s(XX, yy, et):
    p = np.full(len(XX), np.nan); BL = len(XX)//6; aucs = []
    for f in range(1, 6):
        tr = slice(0, f*BL); te = slice(f*BL, (f+1)*BL if f < 5 else len(XX))
        mod = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05,
                                             max_leaf_nodes=31, random_state=3)
        mod.fit(XX[tr], yy[tr]); p[te] = mod.predict_proba(XX[te])[:, 1]
        aucs.append(roc_auc_score(yy[te], p[te]))
    v = ~np.isnan(p); auc = roc_auc_score(yy[v], p[v])
    print(f"  {et:<34} AUC {auc:.4f}   por bloque: " + " ".join(f"{a:.3f}" for a in aucs))
    return p, v, auc

ps, vs, aucs_ = evalua_s(Xs, ys, "todas las variables")
rng2 = np.random.default_rng(11)
_, _, a0 = evalua_s(Xs, rng2.permutation(ys), "control · etiquetas barajadas")
print(f"\n  senal menos ruido de fondo: {aucs_-0.5:+.4f} contra {a0-0.5:+.4f} del control")

ivs = np.where(vs)[0]
print("\n  el decil superior, ya sin solape:")
for frac, et in ((0.10, "decil superior"), (0.25, "cuarto superior")):
    n = int(frac*len(ivs))
    alto = ivs[np.argsort(-ps[ivs])[:n]]; bajo = ivs[np.argsort(ps[ivs])[:n]]
    dif = ys[alto].mean()-ys[bajo].mean()
    ee = sqrt(ys[alto].var(ddof=1)/n + ys[bajo].var(ddof=1)/n)
    print(f"    {et:<18} n {n:>4}  arriba {100*ys[alto].mean():>5.2f} %  "
          f"abajo {100*ys[bajo].mean():>5.2f} %  diferencia {100*dif:>+5.2f} "
          f"[{100*(dif-1.96*ee):>+5.2f},{100*(dif+1.96*ee):>+5.2f}]  t {dif/ee:>+5.2f}")

print("\n  y con el solape, para que se vea lo que inflaba:")
iv = np.where(v)[0]; n = int(0.10*len(iv))
alto = iv[np.argsort(-p[iv])[:n]]; bajo = iv[np.argsort(p[iv])[:n]]
dif = y[alto].mean()-y[bajo].mean()
ee_mal = sqrt(y[alto].var(ddof=1)/n + y[bajo].var(ddof=1)/n)
print(f"    decil superior     n {n:>4}  diferencia {100*dif:>+5.2f}  "
      f"t aparente {dif/ee_mal:>+5.2f}  ·  t real dividiendo por raiz(16) = {dif/ee_mal/4:>+5.2f}")
