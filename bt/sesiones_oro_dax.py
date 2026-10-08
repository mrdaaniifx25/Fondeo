"""Pre-registro docs/PREREGISTRO_sesiones_oro_dax.md

La regla de asia_nivel.py + el filtro de contexto de asia_contexto.py,
portados a oro y DAX, con barrido de stop minimo en ATR de M15.
EURUSD va de control: si no reproduce, el porte esta mal.
"""
import numpy as np, pandas as pd
from math import sqrt

TZ = "Europe/Madrid"
VENTANA = (800, 1130)      # Londres, hora de Madrid
REARME, ATRAS, FIN = 10.0, 10, 2200
KS = [0.0, 0.5, 1.0, 1.5, 2.0]

INS = [("EURUSD (control)", "data/eurusd_m1.parquet", 1e-4, 1.43, 3),
       ("oro",              "data/xauusd_m1.parquet", 0.01, 35.0, 3),
       ("DAX",              "data/grxeur_m1.parquet", 1.0,   1.6, 2)]

def atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    a = np.full(len(tr), np.nan); a[n-1] = tr[:n].mean()
    for i in range(n, len(tr)): a[i] = (a[i-1]*(n-1)+tr[i])/n
    return np.roll(a, 1)                      # el ATR de la vela ANTERIOR

def recoge(ruta, U, minutos):
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    m1["b5"] = m1["loc"].dt.floor("5min")
    v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                              c=("close","last"), ts=("ts","last"), n=("ts","size")).reset_index())
    v = v[v.n >= minutos].reset_index(drop=True)
    v["dia"] = v.b5.dt.date; v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
    O, H, L, C = (v[x].to_numpy() for x in ("o","h","l","c"))

    # --- contexto: direccion de las 4 ultimas velas CERRADAS de M15 y H1 ---
    idx = m1.set_index("ts")
    def marco(regla): return idx.close.resample(regla).last().dropna()
    s15, s60 = marco("15min"), marco("1h")
    def direccion(serie, ts, atras, minu):
        lim = ts - np.timedelta64(minu, "m")
        i = serie.index.searchsorted(lim, side="right") - 1
        out = np.zeros(len(ts), int); ok = i >= atras; a = serie.to_numpy()
        out[ok] = np.sign(a[i[ok]] - a[i[ok]-atras]); return out

    # --- ATR de M15 en el momento de entrar ---
    g15 = (idx.resample("15min").agg(h=("high","max"), l=("low","min"),
                                     c=("close","last")).dropna())
    a15 = atr(g15.h.to_numpy(), g15.l.to_numpy(), g15.c.to_numpy())
    t15 = g15.index.to_numpy("datetime64[ns]")

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
        if hi <= lo: continue
        W = g[(g.hm >= VENTANA[0]) & (g.hm < VENTANA[1])]
        if len(W) < 5: continue
        i0, i1 = W.index[0], W.index[-1]
        for niv in (hi, lo):
            armado = True
            for i in range(i0, i1+1):
                toca = L[i] <= niv <= H[i]
                if not toca and min(abs(H[i]-niv), abs(L[i]-niv))/U > REARME: armado = True
                if not (armado and toca): continue
                for lado in (1, -1):
                    if gatillo(i, niv, lado) is None: continue
                    ent = C[i]; stp = L[i-1] if lado > 0 else H[i-1]
                    if abs(ent-stp) <= 0: break
                    filas.append((dia, int(i), lado, ent, stp))
                    armado = False; break
    if not filas: return None
    t = pd.DataFrame(filas, columns=["dia","i","lado","entrada","stop"])
    t["ts"] = pd.to_datetime(v.ts.to_numpy()[t.i])
    ts = t.ts.to_numpy("datetime64[ns]")
    t["fav"] = ((direccion(s15, ts, 4, 15) == t.lado) &
                (direccion(s60, ts, 4, 60) == t.lado))
    j15 = np.searchsorted(t15, ts, "right") - 1
    t["atr15"] = np.where(j15 >= 0, a15[np.clip(j15, 0, len(a15)-1)], np.nan)
    t = t[np.isfinite(t.atr15) & (t.atr15 > 0)].reset_index(drop=True)

    ts1 = m1.ts.to_numpy(); HH = m1.high.to_numpy(); LL = m1.low.to_numpy(); CC = m1.close.to_numpy()
    fd = m1["loc"].dt.date.to_numpy()
    fh = (m1["loc"].dt.hour*100 + m1["loc"].dt.minute).to_numpy()
    j0 = np.searchsorted(ts1, t.ts.to_numpy("datetime64[ns]"), side="right")
    t["j0"] = j0
    j1 = []
    for a_, d_ in zip(j0, t.dia):
        f = np.where((fd[a_:] != d_) | (fh[a_:] >= FIN))[0]
        j1.append(a_ + (int(f[0]) if len(f) else len(ts1)-a_))
    t["j1"] = np.maximum(np.array(j1), j0+1)
    return t, HH, LL, CC, U

def resuelve(t, HH, LL, CC, U, coste, k):
    R, rg = [], []
    for r in t.itertuples():
        base = abs(r.entrada - r.stop)
        rgo = max(base, k*r.atr15)
        stp = r.entrada - rgo*r.lado
        tp = r.entrada + 2*rgo*r.lado
        a_, b_ = int(r.j0), int(r.j1)
        hh, ll = HH[a_:b_], LL[a_:b_]
        gt, gs = ((hh >= tp, ll <= stp) if r.lado > 0 else (ll <= tp, hh >= stp))
        it = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = CC[b_-1]
            R.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/rgo)
        elif isl <= it: R.append(-1.0)
        else: R.append(2.0)
        rg.append(rgo/U)
    d = t.assign(R=np.array(R), rgoP=np.array(rg))
    d["neto"] = d.R - coste/d.rgoP
    return d

print(f"{'instrumento':<18}{'k·ATR':>7}{'n':>7}{'días':>7}{'stop':>9}{'coste':>8}"
      f"{'%TP':>7}{'R bruta':>10}{'NETA/op':>22}{'suma/día':>10}")
print("-"*116)
for nom, ruta, U, coste, minu in INS:
    got = recoge(ruta, U, minu)
    if got is None: print(f"{nom:<18}  (sin datos)"); continue
    t, HH, LL, CC, U = got
    tf = t[t.fav].reset_index(drop=True)
    if len(tf) < 50: print(f"{nom:<18}  (pocas: {len(tf)})"); continue
    for k in KS:
        d = resuelve(tf, HH, LL, CC, U, coste, k)
        g = d.groupby("dia").neto.sum()
        mn, ic = d.neto.mean(), 1.96*d.neto.std(ddof=1)/sqrt(len(d))
        print(f"{nom:<18}{k:>7.1f}{len(d):>7,}{len(g):>7,}{d.rgoP.median():>9.1f}"
              f"{100*(coste/d.rgoP).mean():>7.1f}%{100*(d.R==2).mean():>6.1f}%"
              f"{d.R.mean():>+10.3f}{mn:>+10.4f} [{mn-ic:>+.4f},{mn+ic:>+.4f}]"
              f"{g.mean():>+10.3f}{'  CRUZA' if mn-ic > 0 else ''}")
    print()
