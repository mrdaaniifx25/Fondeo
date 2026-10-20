"""Donde cruza cero el scalping: la frontera del diferencial.

EXTENSION EXPLORATORIA, no pre-registrada: la sugiere el resultado de
bt/scalping.py. Las 63 celdas salieron negativas, pero al sumar el coste de
vuelta el BRUTO de los montajes de reversion es +0,01 a +0,03. Si el bruto es
+0,025 y el coste es 0,7/stop, el cruce por cero esta en stop ~28 pips.

Esto mide donde esta esa frontera y si aguanta fuera de muestra.

  python3 bt/scalping_frontera.py
"""
import numpy as np, pandas as pd, sys

PIP = 1e-4
COSTE_P = 0.7
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
H1 = M.high.to_numpy(); L1 = M.low.to_numpy(); C1 = M.close.to_numpy()
M["b5"] = M.index // 5
V = M.groupby("b5").agg(ts=("loc", "first"), o=("open", "first"), h=("high", "max"),
                        l=("low", "min"), c=("close", "last"))
V["i1"] = M.groupby("b5").apply(lambda g: g.index[-1], include_groups=False).to_numpy()
V = V.reset_index(drop=True)
c = V.c.to_numpy(); h = V.h.to_numpy(); l = V.l.to_numpy()
hm = V.ts.dt.hour.to_numpy()*60 + V.ts.dt.minute.to_numpy()
dia = V.ts.dt.normalize().to_numpy()

def rsi(x, n):
    d = np.diff(x, prepend=x[0])
    up = pd.Series(np.where(d > 0, d, 0.0)).ewm(alpha=1/n, adjust=False).mean()
    dn = pd.Series(np.where(d < 0, -d, 0.0)).ewm(alpha=1/n, adjust=False).mean()
    return (100 - 100/(1 + up/dn.replace(0, np.nan))).fillna(50).to_numpy()

r2 = rsi(c, 2)
ma20 = pd.Series(c).rolling(20).mean().to_numpy()
sd20 = pd.Series(c).rolling(20).std().to_numpy()
mx12 = pd.Series(h).rolling(12).max().shift(1).to_numpy()
mn12 = pd.Series(l).rolling(12).min().shift(1).to_numpy()
ses = (hm >= 8*60) & (hm < 18*60)
MON = {
    "RSI(2) extremo":      (r2 < 5, r2 > 95),
    "fade de Bollinger":   (c < ma20 - 2*sd20, c > ma20 + 2*sd20),
    "barrido 12 velas":    ((l < mn12) & (c > mn12), (h > mx12) & (c < mx12)),
}

def resuelve(i1, px, lado, stop, rr, hor):
    a = i1 + 1; b = min(a + hor, len(C1))
    if b <= a: return np.nan
    sl = px - lado*stop*PIP; ob = px + lado*rr*stop*PIP
    hi = H1[a:b]; lo = L1[a:b]
    gs = (lo <= sl) if lado > 0 else (hi >= sl)
    gt = (hi >= ob) if lado > 0 else (lo <= ob)
    ks = int(np.argmax(gs)) if gs.any() else 10**9
    kt = int(np.argmax(gt)) if gt.any() else 10**9
    if ks == kt == 10**9:
        return (C1[b-1]-px)*lado/(stop*PIP), 0
    return (-1.0, 1) if ks <= kt else (rr, 1)

corte = np.datetime64(V.ts.iloc[int(0.70*len(V))])
print("Frontera del diferencial · EUR/USD M5 · coste 0,7 pips ida y vuelta")
print(f"corte 70/30: {corte}\n")
print(f"  {'montaje':<20}{'stop':>5}{'R:R':>5}{'hor':>5}{'n':>7}{'coste':>8}"
      f"{'%res':>6}{'BRUTO':>9}{'neto':>9}{'z':>7}{'DENTRO':>9}{'FUERA':>9}")
res = []
for nom, (sa, sb) in MON.items():
    sa2 = sa & ses; sb2 = sb & ses
    idx = np.nonzero(sa2 | sb2)[0]
    idx = idx[(idx > 60) & (idx < len(V)-1)]
    lado = np.where(sa2[idx], 1, -1)
    i1 = V.i1.to_numpy()[idx]; px = c[idx]; ts = V.ts.to_numpy()[idx]
    for stop in (20.0, 28.0, 35.0, 50.0):
        hor = int(15*stop)
        for rr in (1.0, 1.5, 2.0):
            sal = [resuelve(a, p, s, stop, rr, hor) for a, p, s in zip(i1, px, lado)]
            r = np.array([x[0] for x in sal]); fin = np.array([x[1] for x in sal])
            cst = COSTE_P/stop
            neto = r - cst
            d = ts < corte
            se = r.std(ddof=1)/np.sqrt(len(r))
            print(f"  {nom:<20}{stop:>5.0f}{rr:>5.1f}{hor:>5}{len(r):>7}{cst:>8.4f}"
                  f"{100*fin.mean():>5.0f}%{r.mean():>9.4f}{neto.mean():>9.4f}"
                  f"{neto.mean()/se:>7.2f}{neto[d].mean():>9.4f}{neto[~d].mean():>9.4f}")
            res.append({"m": nom, "stop": stop, "rr": rr, "bruto": r.mean(),
                        "neto": neto.mean(), "z": neto.mean()/se,
                        "dentro": neto[d].mean(), "fuera": neto[~d].mean(),
                        "n": len(r), "nf": (~d).sum()})
            sys.stdout.flush()
    print()

F = pd.DataFrame(res)
F.to_csv("data/scalping_frontera.csv", index=False)
print("  Celdas con neto >= 0 en AMBOS tramos:")
g = F[(F.dentro >= 0) & (F.fuera >= 0)]
print("    ninguna" if g.empty else g.to_string(index=False))
print("\n  Celdas con neto >= -0,01 (practicamente justo) en AMBOS tramos:")
g2 = F[(F.dentro >= -0.01) & (F.fuera >= -0.01)]
print("    ninguna" if g2.empty else g2[["m","stop","rr","bruto","neto","dentro","fuera","n"]].to_string(index=False))
print(f"\n  liston por seleccion con {len(F)} celdas: E[max|z|] ~ {np.sqrt(2*np.log(len(F))):.2f}")
