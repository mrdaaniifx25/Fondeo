"""Pre-registro docs/PREREGISTRO_ema_sr.md

Niveles de H1 (pivotes de 5+5, usables 5 velas despues) + ruptura de la EMA 50
en M5 confirmada en M1. Stop en el alto, objetivo en el bajo (y al reves para
compras). Entrada al cierre de la vela de M5 que confirma.
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, HOR = 1e-4, 1.43, 20*60
PIV, VIVOS, CERCA = 5, 20, 0.25
M1M = np.timedelta64(1, "m")
rng = np.random.default_rng(41)

def velas(m1, mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(h=("high","max"), l=("low","min"), c=("close","last"),
                n=("close","size")).dropna())
    return g[g.n >= mins*0.3].reset_index()

def ema(x, n):
    a = np.empty(len(x)); a[:] = np.nan
    if len(x) < n: return a
    k = 2.0/(n+1); a[n-1] = x[:n].mean()
    for i in range(n, len(x)): a[i] = x[i]*k + a[i-1]*(1-k)
    return a

def rma(x, n):
    a = np.full(len(x), np.nan)
    if len(x) < n: return a
    a[n-1] = np.nanmean(x[:n])
    for i in range(n, len(x)): a[i] = (a[i-1]*(n-1) + x[i])/n
    return a

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
mts = m1.ts.to_numpy("datetime64[ns]"); mh = m1.high.to_numpy()
ml = m1.low.to_numpy(); mc = m1.close.to_numpy(); M = len(m1)
e1 = ema(mc, 50)                                   # EMA 50 en M1

V1 = velas(m1, 60); V5 = velas(m1, 5)
t60 = V1.ts.to_numpy("datetime64[ns]"); h60, l60, c60 = V1.h.to_numpy(), V1.l.to_numpy(), V1.c.to_numpy()
t5 = V5.ts.to_numpy("datetime64[ns]"); h5, l5, c5 = V5.h.to_numpy(), V5.l.to_numpy(), V5.c.to_numpy()
e5 = ema(c5, 50)
pc = np.roll(c60,1); pc[0] = c60[0]
atr60 = np.roll(rma(np.maximum(h60-l60, np.maximum(abs(h60-pc), abs(l60-pc))), 14), 1)

# --- niveles de H1: pivotes 5+5, disponibles 5 velas DESPUES de formarse
niv_t, niv_p = [], []
for i in range(PIV, len(V1)-PIV):
    if h60[i] == h60[i-PIV:i+PIV+1].max(): niv_t.append(t60[i+PIV]); niv_p.append(h60[i])
    if l60[i] == l60[i-PIV:i+PIV+1].min(): niv_t.append(t60[i+PIV]); niv_p.append(l60[i])
o = np.argsort(np.array(niv_t, dtype="datetime64[ns]"))
niv_t = np.array(niv_t, dtype="datetime64[ns]")[o]; niv_p = np.array(niv_p)[o]

def cerca(t, p, tol):
    j = int(np.searchsorted(niv_t, t, "right"))
    if j == 0: return False
    k = max(0, j-VIVOS)
    return bool(np.any(np.abs(niv_p[k:j] - p) <= tol))

# --- rupturas de la EMA 50 en M5
cruz_al = np.zeros(len(c5), bool); cruz_ba = np.zeros(len(c5), bool)
ok = np.isfinite(e5); ok[0] = False
cruz_al[1:] = ok[1:] & (c5[1:] > e5[1:]) & (c5[:-1] <= e5[:-1])
cruz_ba[1:] = ok[1:] & (c5[1:] < e5[1:]) & (c5[:-1] >= e5[:-1])

sucesos = []
for k in np.flatnonzero(cruz_al | cruz_ba):
    if k < 20: continue
    lado = 1 if cruz_al[k] else -1
    t_ent = t5[k] + 5*M1M
    i = int(np.searchsorted(mts, t_ent, "left"))
    if i >= M - HOR - 1 or not np.isfinite(e1[i-1]): continue
    m1_ok = (mc[i-1] > e1[i-1]) if lado > 0 else (mc[i-1] < e1[i-1])
    j60 = int(np.searchsorted(t60, t5[k], "right")) - 1
    if j60 < 0 or not np.isfinite(atr60[j60]): continue
    en_niv = cerca(t5[k], c5[k], CERCA*atr60[j60])
    sucesos.append(dict(k=k, lado=lado, t=t_ent, P=c5[k], m1=m1_ok, niv=en_niv, i=i))

def resuelve(i, stop, obj, lado):
    for q in range(i, min(i+HOR, M)):
        if lado < 0:
            if mh[q] >= stop: return 0
            if ml[q] <= obj: return 1
        else:
            if ml[q] <= stop: return 0
            if mh[q] >= obj: return 1
    return 0

def celda(exige_niv, N, exige_m1, lados=None):
    out = []
    for n_, s in enumerate(sucesos):
        if exige_niv and not s["niv"]: continue
        if exige_m1 and not s["m1"]: continue
        k = s["k"]
        if k < N: continue
        lado = s["lado"] if lados is None else lados[n_]
        alto = h5[k-N+1:k+1].max(); bajo = l5[k-N+1:k+1].min()
        P = s["P"]
        stop, obj = (alto, bajo) if lado < 0 else (bajo, alto)
        if lado < 0 and not (stop > P > obj): continue
        if lado > 0 and not (stop < P < obj): continue
        rgo, rec = abs(stop-P)/U, abs(obj-P)/U
        if rgo <= 0 or rec <= 0: continue
        g = resuelve(s["i"], stop, obj, lado)
        out.append((rgo, rec/rgo, g, rgo/(rgo+rec),
                    lado*(mc[min(s["i"]+60, M-1)] - P)/U, pd.Timestamp(s["t"]).year))
    if not out: return None
    D = pd.DataFrame(out, columns=["rgo","rr","gana","azar","der1h","anio"])
    D["Rb"] = np.where(D.gana == 1, D.rr, -1.0); D["Rn"] = D.Rb - COSTE/D.rgo
    return D

def linea(nom, D):
    if D is None or len(D) < 40: print(f"  {nom:<34} (pocas)"); return
    m, ic = D.Rb.mean(), 1.96*D.Rb.std(ddof=1)/sqrt(len(D))
    mn, icn = D.Rn.mean(), 1.96*D.Rn.std(ddof=1)/sqrt(len(D))
    ex = (D.gana - D.azar); e, eic = 100*ex.mean(), 196*ex.std(ddof=1)/sqrt(len(D))
    d, dic = D.der1h.mean(), 1.96*D.der1h.std(ddof=1)/sqrt(len(D))
    print(f"  {nom:<34} n {len(D):5,}  acierto {100*D.gana.mean():5.1f} % "
          f"(azar {100*D.azar.mean():4.1f})  exceso {e:+5.1f} [{e-eic:+5.1f},{e+eic:+5.1f}]"
          f"{'*' if (e-eic)*(e+eic)>0 else ' '}  R:R {D.rr.median():4.2f}  "
          f"riesgo {D.rgo.median():4.1f} p  BRUTA {m:+.4f} [{m-ic:+.4f},{m+ic:+.4f}]  "
          f"NETA {mn:+.4f} [{mn-icn:+.4f},{mn+icn:+.4f}]  deriva 1h {d:+5.2f} [{d-dic:+5.2f},{d+dic:+5.2f}]")

print(f"\nEURUSD · rupturas de la EMA 50 en M5: {len(sucesos):,}\n" + "="*186)
for niv in (True, False):
    for N in (10, 20):
        for m1c in (True, False):
            linea(f"{'nivel H1' if niv else 'sin nivel':<10} N={N:<3} "
                  f"{'M1 confirma' if m1c else 'sin M1'}", celda(niv, N, m1c))
print("="*186)
print("\nnulos sobre la celda principal (nivel H1, N=10, M1 confirma)")
base = celda(True, 10, True)
lados = np.array([s["lado"] for s in sucesos])
linea("  N1 lados barajados", celda(True, 10, True, rng.permutation(lados)))
linea("  N3 la senal al reves", celda(True, 10, True, -lados))
if base is not None:
    print("\npor anio, la celda principal")
    for y in sorted(base.anio.unique()):
        s = base[base.anio == y]
        if len(s) >= 25:
            print(f"    {y}  n {len(s):4,}  exceso {100*(s.gana-s.azar).mean():+5.1f}  "
                  f"BRUTA {s.Rb.mean():+.4f}  NETA {s.Rn.mean():+.4f}")
