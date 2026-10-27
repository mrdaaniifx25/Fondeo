"""Pre-registro docs/PREREGISTRO_rsi_h1.md

RSI(14) en sobreventa/sobrecompra + zona de soporte/resistencia + vela de
giro, en H1. Objetivo 1:2. Tal y como lo explica el video.
"""
import numpy as np, pandas as pd
from math import sqrt

TZ, PIV, HOR = "Europe/Madrid", 5, 24*10
INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 1.43),
       ("oro",    "data/xauusd_m1.parquet", 0.01, 35.0),
       ("DAX",    "data/grxeur_m1.parquet", 1.0,   1.6)]
rng = np.random.default_rng(23)

def atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    a = np.full(len(tr), np.nan); a[n-1] = tr[:n].mean()
    for i in range(n, len(tr)): a[i] = (a[i-1]*(n-1)+tr[i])/n
    return np.roll(a, 1)

def rsi(c, n=14):
    d = np.diff(c, prepend=c[0])
    g = np.where(d > 0, d, 0.0); p = np.where(d < 0, -d, 0.0)
    ag = np.full(len(c), np.nan); ap = np.full(len(c), np.nan)
    ag[n] = g[1:n+1].mean(); ap[n] = p[1:n+1].mean()
    for i in range(n+1, len(c)):
        ag[i] = (ag[i-1]*(n-1)+g[i])/n; ap[i] = (ap[i-1]*(n-1)+p[i])/n
    rs = np.where(ap > 0, ag/np.maximum(ap, 1e-12), 100.0)
    return 100 - 100/(1+rs)

def prepara(ruta):
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    g = (m1.set_index("loc").resample("1h", label="left", closed="left")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    g = g[g.n > 20].reset_index().rename(columns={"loc":"t"})
    return m1, g

def corre(nom, ruta, U, coste, umb, dist, RR, sin_nivel=False, sin_rsi=False, baraja=False):
    m1, d = PREP[nom]
    T = d.t.to_numpy("datetime64[ns]")
    O, H, L, C = (d[x].to_numpy() for x in ("o","h","l","c"))
    A = atr(H, L, C); R = rsi(C); N = len(d)
    MT = m1["loc"].to_numpy("datetime64[ns]")
    MH, ML, MC = m1.high.to_numpy(), m1.low.to_numpy(), m1.close.to_numpy()
    # pivotes de H1 formados ANTES (5 velas a cada lado)
    ph = np.array([i for i in range(PIV, N-PIV) if H[i] == H[i-PIV:i+PIV+1].max()])
    pl = np.array([i for i in range(PIV, N-PIV) if L[i] == L[i-PIV:i+PIV+1].min()])
    ops = []
    for i in range(60, N-1):
        a = A[i]
        if not np.isfinite(a) or a <= 0 or not np.isfinite(R[i]): continue
        for lado in (+1, -1):
            if not sin_rsi:
                if lado > 0 and not R[i] < umb[0]: continue
                if lado < 0 and not R[i] > umb[1]: continue
            if not sin_nivel:
                cand = pl[(pl < i-PIV) & (pl > i-300)] if lado > 0 else ph[(ph < i-PIV) & (ph > i-300)]
                if len(cand) == 0: continue
                niv = L[cand] if lado > 0 else H[cand]
                cerca = np.min(np.abs(C[i]-niv))
                if cerca > dist*a: continue
            # vela de giro: envolvente o martillo/estrella
            cuerpo = abs(C[i]-O[i]); rgv = H[i]-L[i]
            if rgv <= 0: continue
            if lado > 0:
                env = C[i] > O[i] and O[i] <= min(O[i-1],C[i-1]) and C[i] >= max(O[i-1],C[i-1])
                mar = (min(O[i],C[i])-L[i]) >= 2*cuerpo and C[i] > O[i]
                giro = env or mar
            else:
                env = C[i] < O[i] and O[i] >= max(O[i-1],C[i-1]) and C[i] <= min(O[i-1],C[i-1])
                mar = (H[i]-max(O[i],C[i])) >= 2*cuerpo and C[i] < O[i]
                giro = env or mar
            if not giro: continue
            Lx = lado if not baraja else (1 if rng.random() < .5 else -1)
            P = C[i]
            S = (min(L[i-2:i+1]) - 0.1*a) if Lx > 0 else (max(H[i-2:i+1]) + 0.1*a)
            rgo = abs(S-P)
            if rgo <= 0: continue
            TP = P + RR*rgo*Lx
            j0 = int(np.searchsorted(MT, T[i]+np.timedelta64(1,"h"), "left"))
            if j0 >= len(MT)-2: continue
            j1 = min(j0+HOR*60, len(MT))
            hh, ll = MH[j0:j1], ML[j0:j1]
            gt, gs = ((hh >= TP, ll <= S) if Lx > 0 else (ll <= TP, hh >= S))
            it = int(np.argmax(gt)) if gt.any() else 10**9
            isl = int(np.argmax(gs)) if gs.any() else 10**9
            if it == 10**9 and isl == 10**9:
                sal = MC[j1-1]; r_ = ((sal-P) if Lx > 0 else (P-sal))/rgo; mot = "cierre"
            elif isl <= it: r_, mot = -1.0, "SL"
            else: r_, mot = float(RR), "TP"
            ops.append((rgo/U, r_, mot, pd.Timestamp(T[i])))
            break
    if not ops: return pd.DataFrame()
    D = pd.DataFrame(ops, columns=["rgo","R","motivo","fecha"])
    D["neto"] = D.R - coste/D.rgo
    return D

def ficha(et, D, RR, coste, ind="  "):
    if len(D) < 30: return print(f"{ind}{et:<40} n {len(D):>4}  (insuficiente)")
    cr = (coste/D.rgo).mean(); az = 100/(1+RR); um = 100*(1+cr)/(1+RR)
    ac = 100*(D.motivo == "TP").mean()
    mn, ic = D.neto.mean(), 1.96*D.neto.std(ddof=1)/sqrt(len(D))
    print(f"{ind}{et:<40} n {len(D):>4}  riesgo {D.rgo.median():>7.1f}  coste {100*cr:>5.1f}%  "
          f"acierto {ac:>5.1f}%  azar {az:>4.1f}  umbral {um:>5.1f}  "
          f"NETA {mn:>+8.4f} [{mn-ic:>+.4f},{mn+ic:>+.4f}]{'  CRUZA' if mn-ic > 0 else ''}")

PREP = {}
for nom, ruta, U, co in INS:
    PREP[nom] = prepara(ruta)
    print(f"{nom}: {len(PREP[nom][1]):,} velas de H1")

print("\n" + "="*132)
print("PRINCIPAL declarado · EURUSD · RSI 30/70 · nivel a menos de 0,5 ATR · objetivo 2R")
print("="*132)
D = corre("EURUSD", None, 1e-4, 1.43, (30,70), 0.5, 2)
ficha("la señal completa", D, 2, 1.43)

print("\n  CONTROLES")
ficha("placebo · lados barajados", corre("EURUSD", None, 1e-4, 1.43, (30,70), 0.5, 2, baraja=True), 2, 1.43)
ficha("sin el filtro de NIVEL (sólo RSI + vela)", corre("EURUSD", None, 1e-4, 1.43, (30,70), 0.5, 2, sin_nivel=True), 2, 1.43)
ficha("sin el filtro de RSI (sólo nivel + vela)", corre("EURUSD", None, 1e-4, 1.43, (30,70), 0.5, 2, sin_rsi=True), 2, 1.43)

print("\n" + "="*132); print("LAS 18 CELDAS · EURUSD"); print("="*132)
for umb in ((30,70), (20,80)):
    for dist in (0.25, 0.5, 1.0):
        for RR in (1, 2, 3):
            ficha(f"RSI {umb[0]}/{umb[1]} · {dist} ATR · {RR}R",
                  corre("EURUSD", None, 1e-4, 1.43, umb, dist, RR), RR, 1.43)
    print()

print("="*132); print("REPLICA · oro y DAX, la celda principal"); print("="*132)
for nom, ruta, U, co in INS[1:]:
    ficha(nom, corre(nom, ruta, U, co, (30,70), 0.5, 2), 2, co)
