"""AMD + FVG. Pre-registro docs/PREREGISTRO_amd_fvg.md"""
import numpy as np, pandas as pd
from math import sqrt

LIMITE, ESPM, ESPD, ESPF = 0.90, 20, 20, 5
INS = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
       "oro":    ("data/xauusd_m1.parquet", 0.01, None),
       "DAX":    ("data/grxeur_m1.parquet", 1.0,  None)}

def velas(m1, mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(h=("high","max"), l=("low","min"), c=("close","last"),
                n=("close","size")).dropna())
    return g[g.n >= mins*0.3].reset_index()

def rma(x, n):
    a = np.full(len(x), np.nan)
    if len(x) < n: return a
    a[n-1] = np.nanmean(x[:n])
    for i in range(n, len(x)): a[i] = (a[i-1]*(n-1) + x[i]) / n
    return a

def corre(V, n):
    h, l, c = V.h.to_numpy(), V.l.to_numpy(), V.c.to_numpy(); N = len(V)
    pc = np.roll(c,1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    atr = np.roll(rma(tr,14), 1)
    hi = pd.Series(h).rolling(n).max().to_numpy()
    lo = pd.Series(l).rolling(n).min().to_numpy()
    ratio = (hi-lo)/(atr*np.sqrt(n))
    # FVG por vela, causal
    fvg_alc = np.zeros(N, bool); fvg_baj = np.zeros(N, bool)
    fvg_alc[2:] = l[2:] > h[:-2]
    fvg_baj[2:] = h[2:] < l[:-2]

    filas = []; i = n
    while i < N-1:
        if not np.isfinite(ratio[i]) or ratio[i] > LIMITE: i += 1; continue
        rHi, rLo = hi[i], lo[i]
        if rHi <= rLo: i += 1; continue
        manip = -1; lado = 0; ext = np.nan; j = i+1
        while j < min(i+1+ESPM, N):
            if h[j] > rHi or l[j] < rLo:
                arr = h[j] > rHi and rLo < c[j] < rHi
                aba = l[j] < rLo and rLo < c[j] < rHi
                if arr or aba:
                    manip = j; lado = -1 if arr else 1
                    ext = h[j] if arr else l[j]
                break
            j += 1
        if manip < 0: i = max(j, i+1); continue

        # ¿hay FVG a favor del giro en las ESPF velas siguientes?
        kf = -1
        for k in range(manip, min(manip+1+ESPF, N)):
            if (fvg_baj[k] if lado < 0 else fvg_alc[k]): kf = k; break
        entra = kf if kf >= 0 else manip           # sin FVG: al cierre de la M
        P = c[entra]
        stop = max(ext, h[manip:entra+1].max()) if lado < 0 else min(ext, l[manip:entra+1].min())
        obj = rLo if lado < 0 else rHi
        rgo = abs(stop - P); rec = abs(obj - P)
        if rgo <= 0 or rec <= 0: i = manip+1; continue
        dv, dc = rec, abs(stop - P)
        azar = dc / (dv + dc)
        gana = 0; k = entra+1
        while k < min(entra+1+ESPD, N):
            # las dos barreras medidas IGUAL, las dos por toque. Con el stop
            # por mecha y el objetivo por cierre, la operacion sale hundida por
            # como se mide y no por lo que hace el precio.
            if lado < 0:
                if h[k] >= stop: break
                if l[k] <= obj: gana = 1; break
            else:
                if l[k] <= stop: break
                if h[k] >= obj: gana = 1; break
            k += 1
        filas.append((kf >= 0, lado, rgo, rec/rgo, gana, azar, V.ts.iloc[entra]))
        i = manip+1
    D = pd.DataFrame(filas, columns=["fvg","lado","rgo","rr","gana","azar","t"])
    D["anio"] = pd.DatetimeIndex(D.t).year
    D["Rb"] = np.where(D.gana == 1, D.rr, -1.0)
    return D

def linea(nom, S, U, coste):
    if len(S) < 40: print(f"{nom:>22}  n {len(S):5d}  (pocas)"); return
    m, s = S.Rb.mean(), S.Rb.std(ddof=1); ic = 1.96*s/sqrt(len(S))
    ex = (S.gana - S.azar).mean()
    txt = (f"{nom:>22}  n {len(S):5,}  completa {100*S.gana.mean():5.1f} % "
           f"(azar {100*S.azar.mean():4.1f}, exceso {100*ex:+5.1f})  "
           f"R:R {S.rr.median():4.1f}  riesgo {(S.rgo/U).median():5.1f}  "
           f"BRUTA {m:+.4f}  IC95 [{m-ic:+.4f}, {m+ic:+.4f}]")
    if coste:
        Rn = S.Rb - coste / (S.rgo / U)
        txt += f"  NETA {Rn.mean():+.4f}"
    print(txt)

for tf, mins, n in (("H1", 60, 8),):
    print("\n" + "="*150); print(f"{tf}   (rango de {n} velas)"); print("="*150)
    for ins, (ruta, U, coste) in INS.items():
        m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
        D = corre(velas(m1, mins), n)
        print(f"  --- {ins} ---")
        F = D[D.fvg]
        linea("CON FVG · todo", F, U, coste)
        linea("SIN FVG · todo", D[~D.fvg], U, coste)
        cor = 2024 if ins == "EURUSD" else 2025
        linea(f"CON FVG < {cor}", F[F.anio < cor], U, coste)
        linea(f"CON FVG >= {cor}", F[F.anio >= cor], U, coste)
        for y in sorted(F.anio.unique()):
            linea(f"   {y}", F[F.anio == y], U, coste)
