"""La misma senial del video, medida en PIPS en vez de en R.

Por que: el coste son 0,7 pips SIEMPRE, independientemente del stop. Lo que
decide si gana es la ventaja en PIPS, no en R. Mirarlo en R confunde, porque
al estrechar el stop el numero en R crece sin que haya mas dinero.

  neto en pips = ventaja bruta en pips - 0,7
  ventaja en R = ventaja en pips / stop  ->  depende del stop, el dinero no

  python3 bt/mean_reversion_pips.py
"""
import numpy as np, pandas as pd, sys

PIP = 1e-4
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
H1 = M.high.to_numpy(); L1 = M.low.to_numpy(); C1 = M.close.to_numpy()
M["b15"] = M.index // 15
V = M.groupby("b15").agg(ts=("loc","first"), o=("open","first"), h=("high","max"),
                         l=("low","min"), c=("close","last"))
V["i1"] = M.groupby("b15").apply(lambda g: g.index[-1], include_groups=False).to_numpy()
V = V.reset_index(drop=True)
o=V.o.to_numpy(); h=V.h.to_numpy(); l=V.l.to_numpy(); c=V.c.to_numpy(); I1=V.i1.to_numpy()
ema20 = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
d = np.diff(c, prepend=c[0])
up = pd.Series(np.where(d>0,d,0.0)).ewm(alpha=1/14, adjust=False).mean()
dn = pd.Series(np.where(d<0,-d,0.0)).ewm(alpha=1/14, adjust=False).mean()
rsi14 = (100-100/(1+up/dn.replace(0,np.nan))).fillna(50).to_numpy()
sd = pd.Series(c).rolling(20).std().to_numpy()
med = (h+l)/2
corte = V.ts.iloc[int(0.70*len(V))]

def corre(k, stop_p, obj, hor=64):
    bl = ema20 - k*sd; bu = ema20 + k*sd
    rl = (l < bl) & (c > med) & (c > o) & (rsi14 < 30)
    rs = (h > bu) & (c < med) & (c < o) & (rsi14 > 70)
    idx = np.nonzero(rl | rs)[0]; idx = idx[(idx > 40) & (idx < len(V)-2)]
    out = []; ult = -1
    for p in idx:
        if p <= ult: continue
        lado = 1 if rl[p] else -1
        ent = o[p+1]; rgo = stop_p*PIP
        sl = ent - lado*rgo
        if obj == "ema":
            ob = ema20[p]
            if (ob-ent)*lado <= 1*PIP: continue
        else:
            ob = ent + lado*float(obj)*rgo
        a = I1[p]+1; b = min(a+hor*15, len(C1))
        if b <= a: continue
        hi = H1[a:b]; lo = L1[a:b]
        gs = (lo<=sl) if lado>0 else (hi>=sl)
        gt = (hi>=ob) if lado>0 else (lo<=ob)
        ks = int(np.argmax(gs)) if gs.any() else 10**9
        kt = int(np.argmax(gt)) if gt.any() else 10**9
        if ks==kt==10**9:
            pips = (C1[b-1]-ent)*lado/PIP; kf = hor*15
        elif ks<=kt:
            pips = -stop_p; kf = ks
        else:
            pips = (ob-ent)*lado/PIP; kf = kt
        out.append((V.ts.iloc[p], pips, kf))
        ult = p + max(1, kf//15)
    return pd.DataFrame(out, columns=["ts","pips","min"])

print("LA SEÑAL DEL VIDEO, MEDIDA EN PIPS · coste 0,7 pips ida y vuelta")
print("EUR/USD M15 · EMA20 · RSI(14) 30/70 · vela de rechazo · objetivo = EMA20\n")
print(f"  {'k':>4}{'stop':>6}{'n':>6}{'ops/anio':>10}{'acierto':>9}"
      f"{'BRUTO pips':>12}{'t':>7}{'NETO pips':>11}{'dentro':>9}{'fuera':>9}")
res=[]
for k in (1.5, 2.0):
    for stop_p in (7.0, 10.0, 15.0, 20.0, 30.0, 45.0):
        R = corre(k, stop_p, "ema")
        if len(R) < 80: continue
        t = R.pips.mean()/(R.pips.std(ddof=1)/np.sqrt(len(R)))
        dd = R.ts < corte
        print(f"  {k:>4.1f}{stop_p:>6.0f}{len(R):>6}{len(R)/5.66:>10.0f}"
              f"{100*(R.pips>0.7).mean():>8.1f}%{R.pips.mean():>12.3f}{t:>7.2f}"
              f"{R.pips.mean()-0.7:>11.3f}{R.pips[dd].mean()-0.7:>9.3f}"
              f"{R.pips[~dd].mean()-0.7:>9.3f}")
        res.append({"k":k,"stop":stop_p,"n":len(R),"bruto":R.pips.mean(),"t":t,
                    "neto":R.pips.mean()-0.7,"dentro":R.pips[dd].mean()-0.7,
                    "fuera":R.pips[~dd].mean()-0.7})
        sys.stdout.flush()
    print()
F = pd.DataFrame(res); F.to_csv("data/mean_reversion_pips.csv", index=False)
g = F[(F.dentro>0)&(F.fuera>0)]
print("  Celdas con NETO > 0 en los dos tramos:")
print("    ninguna" if g.empty else g.to_string(index=False))

if not g.empty:
    b = g.loc[g.neto.idxmax()]
    print(f"\n  MEJOR: k {b.k} · stop {b.stop:.0f} pips · {b.n:.0f} ops · "
          f"neto {b.neto:+.3f} pips/op")
    for riesgo, cuenta in ((0.005, 10000.0),):
        eur_pip = riesgo*cuenta/b.stop
        mes = b.neto*eur_pip*(b.n/5.66/12)
        print(f"  Dinero: riesgo {100*riesgo:.2f} % sobre {cuenta:.0f} -> "
              f"{eur_pip:.2f} EUR por pip -> {mes:+.0f} EUR/mes")
    print(f"  Coste de equilibrio: la ventaja bruta es {b.bruto:.3f} pips, asi que")
    print(f"  aguanta un coste de hasta {b.bruto:.2f} pips ida y vuelta.")
