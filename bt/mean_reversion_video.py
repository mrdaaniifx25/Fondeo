"""La estrategia del video (@Elpsicologodeltrading), medida con sus reglas.

Pre-registro: docs/PREREGISTRO_mean_reversion_video.md

M15, EUR/USD, EMA 20, RSI(14) 30/70, vela de rechazo, stop detras del extremo
reciente, objetivo la vuelta a la EMA 20. Salidas minuto a minuto con el M1.

Lo nuevo que prueba: objetivo VARIABLE (la media, que se mueve) y PARCIALES.
Es la dimension de gestion de la posicion, nunca explorada en este proyecto.

  python3 bt/mean_reversion_video.py
"""
import numpy as np, pandas as pd, sys

PIP = 1e-4
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
H1 = M.high.to_numpy(); L1 = M.low.to_numpy(); C1 = M.close.to_numpy()
M["b15"] = M.index // 15
V = M.groupby("b15").agg(ts=("loc", "first"), o=("open", "first"), h=("high", "max"),
                         l=("low", "min"), c=("close", "last"))
V["i1"] = M.groupby("b15").apply(lambda g: g.index[-1], include_groups=False).to_numpy()
V = V.reset_index(drop=True)
o = V.o.to_numpy(); h = V.h.to_numpy(); l = V.l.to_numpy(); c = V.c.to_numpy()
print(f"M15: {len(V)} velas  {V.ts.iloc[0]} -> {V.ts.iloc[-1]}")

ema20 = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
d = np.diff(c, prepend=c[0])
up = pd.Series(np.where(d > 0, d, 0.0)).ewm(alpha=1/14, adjust=False).mean()
dn = pd.Series(np.where(d < 0, -d, 0.0)).ewm(alpha=1/14, adjust=False).mean()
rsi14 = (100 - 100/(1 + up/dn.replace(0, np.nan))).fillna(50).to_numpy()
sd = pd.Series(c).rolling(20).std().to_numpy()
mn3 = pd.Series(l).rolling(3).min().to_numpy()
mx3 = pd.Series(h).rolling(3).max().to_numpy()
cuerpo_medio = (h + l) / 2

def seniales(k):
    bl = ema20 - k*sd; bu = ema20 + k*sd
    # vela de rechazo larga: perfora la banda por abajo y cierra en la mitad alta
    rl = (l < bl) & (c > cuerpo_medio) & (c > o) & (rsi14 < 30)
    rs = (h > bu) & (c < cuerpo_medio) & (c < o) & (rsi14 > 70)
    return rl, rs

def corre(k, modo, coste_p=0.7, hor=16*4):
    """modo: 'ema_fija' | 'ema_dinamica' | 'parcial' | 'fijo1' | 'fijo2'"""
    rl, rs = seniales(k)
    idx = np.nonzero(rl | rs)[0]
    idx = idx[(idx > 40) & (idx < len(V)-2)]
    res = []
    ult_fin = -1
    for p in idx:
        if p <= ult_fin:                       # una posicion a la vez
            continue
        lado = 1 if rl[p] else -1
        ent = o[p+1]                           # apertura de la vela SIGUIENTE
        if lado > 0:
            sl = mn3[p] - PIP
        else:
            sl = mx3[p] + PIP
        rgo = (ent - sl)*lado
        if rgo <= 2*PIP or rgo > 60*PIP:
            continue
        a = V.i1.to_numpy()[p] + 1
        b = min(a + hor*15, len(C1))
        if b <= a:
            continue
        cst = (coste_p*PIP)/rgo
        hi = H1[a:b]; lo = L1[a:b]
        gs = (lo <= sl) if lado > 0 else (hi >= sl)
        ks = int(np.argmax(gs)) if gs.any() else 10**9
        if modo == "ema_fija":
            ob = ema20[p]
        elif modo == "fijo1":
            ob = ent + lado*1.0*rgo
        elif modo == "fijo2":
            ob = ent + lado*2.0*rgo
        else:
            ob = None
        if ob is not None:
            gt = (hi >= ob) if lado > 0 else (lo <= ob)
            kt = int(np.argmax(gt)) if gt.any() else 10**9
            if ks == kt == 10**9:
                r = (C1[b-1]-ent)*lado/rgo
            elif ks <= kt:
                r = -1.0
            else:
                r = (ob-ent)*lado/rgo
            res.append((V.ts.iloc[p], r - cst, r, rgo, cst, ks if ks < 10**9 else hor*15))
            ult_fin = p + max(1, (min(ks, kt) if min(ks, kt) < 10**9 else hor*15)//15)
            continue
        # objetivo DINAMICO: la EMA20 de cada vela M15, recalculada
        kt = 10**9; pxt = None
        for q in range(p+1, min(p+1+hor, len(V))):
            aq = V.i1.to_numpy()[q-1] + 1
            bq = V.i1.to_numpy()[q] + 1
            if bq > b: break
            e = ema20[q-1]                      # la EMA conocida al abrir la vela q
            seg_h = H1[aq:bq]; seg_l = L1[aq:bq]
            if len(seg_h) == 0: break
            gsq = (seg_l <= sl) if lado > 0 else (seg_h >= sl)
            gtq = (seg_h >= e) if lado > 0 else (seg_l <= e)
            k_s = int(np.argmax(gsq)) if gsq.any() else 10**9
            k_t = int(np.argmax(gtq)) if gtq.any() else 10**9
            if k_s == k_t == 10**9:
                continue
            if k_s <= k_t:
                kt = -1; pxt = sl; ks = (aq-a)+k_s
            else:
                kt = (aq-a)+k_t; pxt = e
            break
        if pxt is None:
            r = (C1[b-1]-ent)*lado/rgo
        elif kt == -1:
            r = -1.0
        else:
            r = (pxt-ent)*lado/rgo
        if modo == "parcial" and pxt is not None and kt != -1:
            # mitad fuera en la media, resto a 2R con stop a entrada
            r1 = (pxt-ent)*lado/rgo
            a2 = a + kt + 1; b2 = min(a2 + hor*15, len(C1))
            if b2 > a2:
                ob2 = ent + lado*2.0*rgo
                hi2 = H1[a2:b2]; lo2 = L1[a2:b2]
                g2s = (lo2 <= ent) if lado > 0 else (hi2 >= ent)
                g2t = (hi2 >= ob2) if lado > 0 else (lo2 <= ob2)
                k2s = int(np.argmax(g2s)) if g2s.any() else 10**9
                k2t = int(np.argmax(g2t)) if g2t.any() else 10**9
                r2 = 0.0 if k2s <= k2t else 2.0
                if k2s == k2t == 10**9:
                    r2 = (C1[b2-1]-ent)*lado/rgo
                r = 0.5*r1 + 0.5*r2
        res.append((V.ts.iloc[p], r - cst, r, rgo, cst,
                    (kt if kt > 0 else ks)))
        ult_fin = p + max(1, (kt if kt > 0 else hor*15)//15)
    return pd.DataFrame(res, columns=["ts", "neto", "bruto", "rgo", "coste", "min"])

corte = V.ts.iloc[int(0.70*len(V))]
print(f"corte 70/30: {corte}\n")
MODOS = [("ema_fija", "A objetivo EMA20 congelada"),
         ("ema_dinamica", "B objetivo EMA20 dinamica"),
         ("parcial", "C parcial 50% en la media"),
         ("fijo1", "D control: objetivo 1R"),
         ("fijo2", "E control: objetivo 2R")]
print(f"  {'k':>4}{'modo':<30}{'n':>6}{'stop(p)':>9}{'coste':>8}{'acierto':>9}"
      f"{'BRUTO':>9}{'neto':>9}{'z':>7}{'PF':>7}{'FUERA':>9}")
out = []
for k in (1.5, 2.0, 2.5):
    for modo, nom in MODOS:
        R = corre(k, modo)
        if len(R) < 60:
            print(f"  {k:>4.1f}{nom:<30}{len(R):>6}  (muestra insuficiente)")
            continue
        se = R.bruto.std(ddof=1)/np.sqrt(len(R))
        pf = (R.neto[R.neto > 0].sum()/abs(R.neto[R.neto < 0].sum())
              if (R.neto < 0).any() else np.nan)
        d = R.ts < corte
        print(f"  {k:>4.1f}{nom:<30}{len(R):>6}{R.rgo.median()/PIP:>9.1f}"
              f"{R.coste.mean():>8.4f}{100*(R.neto>0).mean():>8.1f}%{R.bruto.mean():>9.4f}"
              f"{R.neto.mean():>9.4f}{R.neto.mean()/se:>7.2f}{pf:>7.2f}"
              f"{R.neto[~d].mean():>9.4f}")
        out.append({"k": k, "modo": modo, "n": len(R), "win": (R.neto > 0).mean(),
                    "bruto": R.bruto.mean(), "neto": R.neto.mean(),
                    "z": R.neto.mean()/se, "pf": pf,
                    "dentro": R.neto[d].mean(), "fuera": R.neto[~d].mean(),
                    "stop": R.rgo.median()/PIP, "coste": R.coste.mean()})
        sys.stdout.flush()
    print()
pd.DataFrame(out).to_csv("data/mean_reversion_video.csv", index=False)
F = pd.DataFrame(out)
print("  Celdas con neto >= 0 en los DOS tramos:")
g = F[(F.dentro >= 0) & (F.fuera >= 0)]
print("    ninguna" if g.empty else g.to_string(index=False))
