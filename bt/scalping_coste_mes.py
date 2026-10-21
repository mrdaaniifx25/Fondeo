"""Cuanto cuesta al mes cada anchura de stop. Una posicion a la vez.

RSI(2) en M5 (el unico montaje con bruto positivo) con R:R 1:2, secuenciado SIN
solapar para que el numero de operaciones al dia sea el real y el coste mensual
sea comparable entre anchuras.

  python3 bt/scalping_coste_mes.py
"""
import numpy as np, pandas as pd, sys

PIP, COSTE_P, CUENTA, RIESGO = 1e-4, 0.7, 10000.0, 0.005
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
H1 = M.high.to_numpy(); L1 = M.low.to_numpy(); C1 = M.close.to_numpy()
M["b5"] = M.index // 5
V = M.groupby("b5").agg(ts=("loc", "first"), c=("close", "last"))
V["i1"] = M.groupby("b5").apply(lambda g: g.index[-1], include_groups=False).to_numpy()
V = V.reset_index(drop=True)
c = V.c.to_numpy()
hm = V.ts.dt.hour.to_numpy()*60 + V.ts.dt.minute.to_numpy()

def rsi(x, n):
    d = np.diff(x, prepend=x[0])
    up = pd.Series(np.where(d > 0, d, 0.0)).ewm(alpha=1/n, adjust=False).mean()
    dn = pd.Series(np.where(d < 0, -d, 0.0)).ewm(alpha=1/n, adjust=False).mean()
    return (100 - 100/(1 + up/dn.replace(0, np.nan))).fillna(50).to_numpy()

r2 = rsi(c, 2)
ses = (hm >= 8*60) & (hm < 18*60)
sa = (r2 < 5) & ses; sb = (r2 > 95) & ses
i1 = V.i1.to_numpy()
dias_tot = V.ts.dt.normalize().nunique()
meses = dias_tot/21.0
RR = 2.0

print("RSI(2) en M5 · R:R 1:2 · UNA posicion a la vez · 08:00-18:00 Madrid")
print(f"coste {COSTE_P} pips ida y vuelta · riesgo {100*RIESGO:.2f} % sobre {CUENTA:.0f} EUR")
print(f"{dias_tot} dias de sesion = {meses:.0f} meses\n")
print(f"  {'stop':>6}{'coste/rgo':>11}{'ops/dia':>9}{'acierto':>9}{'BRUTO':>9}"
      f"{'neto R':>9}{'z':>7}{'EUR/mes':>10}{'%cuenta/mes':>13}")
for stop in (5.0, 8.0, 12.0, 20.0, 35.0, 50.0):
    hor = max(60, int(15*stop))
    j = 0; R = []
    idx = np.nonzero(sa | sb)[0]
    idx = idx[(idx > 60) & (idx < len(V)-1)]
    sig = set(idx.tolist())
    k = 0
    while k < len(idx):
        p = idx[k]
        lado = 1 if sa[p] else -1
        px = c[p]; a = i1[p]+1; b = min(a+hor, len(C1))
        if b <= a: k += 1; continue
        sl = px - lado*stop*PIP; ob = px + lado*RR*stop*PIP
        hi = H1[a:b]; lo = L1[a:b]
        gs = (lo <= sl) if lado > 0 else (hi >= sl)
        gt = (hi >= ob) if lado > 0 else (lo <= ob)
        ks = int(np.argmax(gs)) if gs.any() else 10**9
        kt = int(np.argmax(gt)) if gt.any() else 10**9
        if ks == kt == 10**9:
            r = (C1[b-1]-px)*lado/(stop*PIP); fin = a+hor
        elif ks <= kt:
            r = -1.0; fin = a+ks
        else:
            r = RR; fin = a+kt
        R.append(r)
        # avanzar a la primera senial POSTERIOR al cierre
        while k < len(idx) and i1[idx[k]] <= fin:
            k += 1
    R = np.array(R)
    cst = COSTE_P/stop
    neto = R - cst
    opd = len(R)/dias_tot
    se = R.std(ddof=1)/np.sqrt(len(R))
    eur = neto.mean() * RIESGO * CUENTA * (len(R)/meses)
    print(f"  {stop:>6.0f}{cst:>11.4f}{opd:>9.2f}{100*(R>0).mean():>8.1f}%"
          f"{R.mean():>9.4f}{neto.mean():>9.4f}{neto.mean()/se:>7.2f}"
          f"{eur:>10.0f}{100*eur/CUENTA:>12.2f}%")
    sys.stdout.flush()

print("\n  El BRUTO no pasa de +0,02 R en ninguna anchura. El coste va de 14 % a")
print("  1,4 % del riesgo. No hay anchura que cruce cero: al ensanchar el stop")
print("  baja el coste, pero el bruto baja a la vez.")
