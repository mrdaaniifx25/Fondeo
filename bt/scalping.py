"""Scalping en M5 con salidas resueltas minuto a minuto. Lo pidio el.

Pre-registro: docs/PREREGISTRO_scalping.md

Siete montajes clasicos x 3 stops x 3 R:R = 63 celdas. Reparto 70/30 por
tiempo. Con 63 celdas el maximo |z| por azar es ~2,65: una celda tiene que
batir eso dentro y seguir positiva fuera.

  python3 bt/scalping.py
"""
import numpy as np, pandas as pd, sys

PIP = 1e-4
COSTE_P, HOR = 0.7, 120
STOPS = (8.0, 12.0, 20.0)
RRS = (1.0, 1.5, 2.0)

M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
H1 = M.high.to_numpy(); L1 = M.low.to_numpy(); C1 = M.close.to_numpy()
print(f"M1: {len(M)} velas  {M['loc'].iloc[0]} -> {M['loc'].iloc[-1]}")

# ---- velas de 5 minutos
M["b5"] = M.index // 5
V = M.groupby("b5").agg(ts=("loc", "first"), o=("open", "first"), h=("high", "max"),
                        l=("low", "min"), c=("close", "last"), fin=("close", "size"))
V["i1"] = M.groupby("b5").apply(lambda g: g.index[-1], include_groups=False).to_numpy()
V = V.reset_index(drop=True)
print(f"M5: {len(V)} velas")

c = V.c.to_numpy(); h = V.h.to_numpy(); l = V.l.to_numpy(); o = V.o.to_numpy()
hm = V.ts.dt.hour.to_numpy() * 60 + V.ts.dt.minute.to_numpy()
dia = V.ts.dt.normalize().to_numpy()

def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()

def rsi(x, n):
    d = np.diff(x, prepend=x[0])
    up = pd.Series(np.where(d > 0, d, 0.0)).ewm(alpha=1/n, adjust=False).mean()
    dn = pd.Series(np.where(d < 0, -d, 0.0)).ewm(alpha=1/n, adjust=False).mean()
    return (100 - 100/(1 + up/dn.replace(0, np.nan))).fillna(50).to_numpy()

e9, e21, e50 = ema(c, 9), ema(c, 21), ema(c, 50)
r2 = rsi(c, 2)
ma20 = pd.Series(c).rolling(20).mean().to_numpy()
sd20 = pd.Series(c).rolling(20).std().to_numpy()
tp = (h + l + c) / 3
D = pd.Series(dia)
vw = pd.Series(tp).groupby(D).transform(lambda s: s.expanding().mean()).to_numpy()
vsd = pd.Series(tp).groupby(D).transform(lambda s: s.expanding().std()).to_numpy()
mx12 = pd.Series(h).rolling(12).max().shift(1).to_numpy()
mn12 = pd.Series(l).rolling(12).min().shift(1).to_numpy()
# rango de las 3 primeras velas de Londres (08:00-08:15 Madrid)
esL = (hm >= 8*60) & (hm < 8*60+15)
rh = pd.Series(np.where(esL, h, np.nan)).groupby(D).transform("max").to_numpy()
rl = pd.Series(np.where(esL, l, np.nan)).groupby(D).transform("min").to_numpy()

sesion = (hm >= 8*60) & (hm < 18*60)
cruza_a = (e9 > e21) & (np.roll(e9, 1) <= np.roll(e21, 1))
cruza_b = (e9 < e21) & (np.roll(e9, 1) >= np.roll(e21, 1))
sube3 = (c > o) & (np.roll(c, 1) > np.roll(o, 1)) & (np.roll(c, 2) > np.roll(o, 2))
baja3 = (c < o) & (np.roll(c, 1) < np.roll(o, 1)) & (np.roll(c, 2) < np.roll(o, 2))

MONTAJES = {
    "1 cruce EMA 9/21 + EMA50": (cruza_a & (e21 > e50), cruza_b & (e21 < e50)),
    "2 RSI(2) extremo":         (r2 < 5, r2 > 95),
    "3 rotura rango Londres":   ((c > rh) & (np.roll(c, 1) <= np.roll(rh, 1)) & (hm >= 8*60+15),
                                 (c < rl) & (np.roll(c, 1) >= np.roll(rl, 1)) & (hm >= 8*60+15)),
    "4 reversion a VWAP":       (c < vw - vsd, c > vw + vsd),
    "5 fade de Bollinger":      (c < ma20 - 2*sd20, c > ma20 + 2*sd20),
    "6 momentum 3 velas":       (sube3, baja3),
    "7 barrido 12 velas (CRT)": ((l < mn12) & (c > mn12), (h > mx12) & (c < mx12)),
}

def resuelve(i1, px, lado, stop, rr):
    """Desde el minuto siguiente al cierre de la vela M5. Devuelve R bruto."""
    a = i1 + 1
    b = min(a + HOR, len(C1))
    if b <= a:
        return np.nan
    sl = px - lado*stop*PIP
    ob = px + lado*rr*stop*PIP
    hi = H1[a:b]; lo = L1[a:b]
    gs = (lo <= sl) if lado > 0 else (hi >= sl)
    gt = (hi >= ob) if lado > 0 else (lo <= ob)
    ks = int(np.argmax(gs)) if gs.any() else 10**9
    kt = int(np.argmax(gt)) if gt.any() else 10**9
    if ks == kt == 10**9:
        return (C1[b-1] - px) * lado / (stop*PIP)
    return -1.0 if ks <= kt else rr

corte = V.ts.iloc[int(0.70*len(V))]
print(f"corte 70/30: {corte}\n")
print(f"  {'montaje':<26}{'stop':>5}{'R:R':>6}{'n':>6}{'umbral':>8}{'acierto':>9}"
      f"{'neto':>9}{'z':>7}{'n fuera':>9}{'fuera':>9}")
filas = []
for nom, (sa, sb) in MONTAJES.items():
    sa = sa & sesion; sb = sb & sesion
    idx = np.nonzero(sa | sb)[0]
    idx = idx[(idx > 60) & (idx < len(V)-1)]
    lado = np.where(sa[idx], 1, -1)
    i1 = V.i1.to_numpy()[idx]; px = c[idx]
    ts = V.ts.to_numpy()[idx]
    for stop in STOPS:
        for rr in RRS:
            r = np.array([resuelve(a, p, s, stop, rr) for a, p, s in zip(i1, px, lado)])
            ok = np.isfinite(r)
            cst = COSTE_P / stop
            neto = r[ok] - cst
            dentro = ts[ok] < np.datetime64(corte)
            n = ok.sum()
            if n < 100:
                continue
            se = r[ok].std(ddof=1) / np.sqrt(n)
            umb = (1 + cst) / (1 + rr)
            filas.append({"m": nom, "stop": stop, "rr": rr, "n": n,
                          "umbral": umb, "win": (r[ok] > 0).mean(),
                          "neto": neto.mean(), "z": neto.mean()/se,
                          "nf": (~dentro).sum(),
                          "nd": neto[dentro].mean() if dentro.any() else np.nan,
                          "nfv": neto[~dentro].mean() if (~dentro).any() else np.nan,
                          "coste": cst})
            f = filas[-1]
            print(f"  {nom:<26}{stop:>5.0f}{rr:>6.1f}{n:>6}{100*umb:>7.1f}%"
                  f"{100*f['win']:>8.1f}%{f['neto']:>9.4f}{f['z']:>7.2f}"
                  f"{f['nf']:>9}{f['nfv']:>9.4f}")
            sys.stdout.flush()

F = pd.DataFrame(filas)
F.to_csv("data/scalping_rejilla.csv", index=False)
print(f"\n  celdas: {len(F)} · liston por seleccion con {len(F)} celdas: "
      f"E[max|z|] ~ {np.sqrt(2*np.log(len(F))):.2f}")
print("\n  TOP 5 por z dentro de muestra:")
for _, x in F.nlargest(5, "z").iterrows():
    print(f"    {x.m:<26} stop {x.stop:>4.0f} R:R {x.rr:.1f}  z {x.z:+.2f}  "
          f"dentro {x.nd:+.4f}  FUERA {x.nfv:+.4f}")
print("\n  TOP 5 por neto FUERA de muestra:")
for _, x in F.nlargest(5, "nfv").iterrows():
    print(f"    {x.m:<26} stop {x.stop:>4.0f} R:R {x.rr:.1f}  FUERA {x.nfv:+.4f}  "
          f"(n fuera {x.nf:.0f})  z dentro {x.z:+.2f}")
