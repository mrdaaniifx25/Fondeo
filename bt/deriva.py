"""Pre-registro docs/PREREGISTRO_deriva.md

Sin stop ni objetivo. Pasados h minutos de mercado desde que dispara la senal,
cuanto se ha movido el precio A FAVOR, de media, en pips.

El teorema de la barrera no dice nada de esta magnitud. Si el precio fuese un
paseo sin memoria la media seria 0. Y usa el TAMANO del movimiento, no solo el
signo, asi que detecta derivas que una prueba de acierto no ve.
"""
import numpy as np, pandas as pd
from math import sqrt

LIMITE, ESPM, ESPF = 0.90, 20, 5
HORAS = [1, 4, 12, 24, 72, 168]
NBOOT = 10000
INS = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
       "oro":    ("data/xauusd_m1.parquet", 0.01, None),
       "DAX":    ("data/grxeur_m1.parquet", 1.0,  None)}
rng = np.random.default_rng(31)

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

def sucesos(V, n):
    """Devuelve tres listas de (instante de entrada, lado)."""
    h, l, c = V.h.to_numpy(), V.l.to_numpy(), V.c.to_numpy(); N = len(V)
    ts = V.ts.to_numpy("datetime64[ns]"); M1M = np.timedelta64(1,"m")
    pc = np.roll(c,1); pc[0] = c[0]
    tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
    atr = np.roll(rma(tr,14), 1)
    hi = pd.Series(h).rolling(n).max().to_numpy()
    lo = pd.Series(l).rolling(n).min().to_numpy()
    ratio = (hi-lo)/(atr*np.sqrt(n))
    al = np.zeros(N, bool); ba = np.zeros(N, bool)
    al[2:] = l[2:] > h[:-2]; ba[2:] = h[2:] < l[:-2]

    amdfvg = []; finta = []
    i = n
    while i < N-1:
        if not np.isfinite(ratio[i]) or ratio[i] > LIMITE: i += 1; continue
        rHi, rLo = hi[i], lo[i]
        if rHi <= rLo: i += 1; continue
        manip = -1; lado = 0; j = i+1
        while j < min(i+1+ESPM, N):
            if h[j] > rHi or l[j] < rLo:
                arr = h[j] > rHi and rLo < c[j] < rHi
                aba = l[j] < rLo and rLo < c[j] < rHi
                if arr or aba: manip = j; lado = -1 if arr else 1
                break
            j += 1
        if manip < 0: i = max(j, i+1); continue
        finta.append((ts[manip] + 60*M1M, lado))
        for k in range(manip, min(manip+1+ESPF, N)):
            if (ba[k] if lado < 0 else al[k]):
                amdfvg.append((ts[k] + 60*M1M, lado)); break
        i = manip+1

    solo = [(ts[k] + 60*M1M, -1 if ba[k] else 1) for k in range(N) if al[k] or ba[k]]
    base = [(ts[k] + 60*M1M, 1 if k % 2 == 0 else -1) for k in range(n, N, 7)]
    return {"amdfvg": amdfvg, "finta": finta, "fvg": solo, "base": base}

def mide(ev, mts, mc, U):
    """matriz n x len(HORAS) con el movimiento a favor en pips, y los meses."""
    if not ev: return None, None
    t = np.array([x[0] for x in ev], dtype="datetime64[ns]")
    s = np.array([x[1] for x in ev], float)
    idx = np.searchsorted(mts, t, "left")
    ok = idx < len(mts) - max(HORAS)*60 - 1
    idx, s, t = idx[ok], s[ok], t[ok]
    if len(idx) < 30: return None, None
    P0 = mc[idx]
    R = np.column_stack([s * (mc[idx + hh*60] - P0) / U for hh in HORAS])
    mes = pd.PeriodIndex(pd.DatetimeIndex(t), freq="M").astype(str).to_numpy()
    return R, mes

def bloques(R, mes):
    """bootstrap por bloques de mes natural. Devuelve (media, lo, hi) por columna."""
    grupos = {}
    for k, m in enumerate(mes): grupos.setdefault(m, []).append(k)
    claves = list(grupos); idxs = [np.array(grupos[k]) for k in claves]
    G = len(claves)
    med = R.mean(0)
    sim = np.empty((NBOOT, R.shape[1]))
    for b in range(NBOOT):
        pick = rng.integers(0, G, G)
        sel = np.concatenate([idxs[p] for p in pick])
        sim[b] = R[sel].mean(0)
    lo = np.percentile(sim, 2.5, axis=0); hi = np.percentile(sim, 97.5, axis=0)
    return med, lo, hi

def fila(nom, R, mes, coste):
    med, lo, hi = bloques(R, mes)
    print(f"  {nom:<26} n {len(R):5,}", end="")
    for q in range(len(HORAS)):
        marca = " "
        if coste is not None and lo[q] > coste: marca = "*"
        elif lo[q] > 0: marca = "+"
        print(f" |{med[q]:+6.2f} [{lo[q]:+6.2f},{hi[q]:+6.2f}]{marca}", end="")
    print()

for ins, (ruta, U, coste) in INS.items():
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    mts = m1.ts.to_numpy("datetime64[ns]"); mc = m1.close.to_numpy()
    ev = sucesos(velas(m1, 60), 8)

    print("\n" + "="*190)
    u = "pips" if ins == "EURUSD" else "unidades"
    print(f"{ins}   movimiento a favor en {u}, media [IC95 bootstrap por meses]"
          + (f"   coste {coste}" if coste else ""))
    print("="*190)
    print(f"  {'senal':<26} {'n':>7}" + "".join(f" |{('h='+str(x)):^22}" for x in HORAS))
    for k in ("amdfvg", "finta", "fvg", "base"):
        R, mes = mide(ev[k], mts, mc, U)
        if R is None: continue
        fila(k, R, mes, coste)
        if k != "amdfvg": continue
        # ---- los tres nulos, solo para la senal principal
        t = np.array([x[0] for x in ev[k]], dtype="datetime64[ns]")
        s = np.array([x[1] for x in ev[k]], float)
        N1 = list(zip(t, rng.permutation(s)))
        fila("  N1 lados barajados", *mide(N1, mts, mc, U), coste)
        ri = rng.integers(100, len(mts) - max(HORAS)*60 - 2, len(t))
        N2 = list(zip(mts[ri], rng.choice(s, len(t))))
        fila("  N2 instantes al azar", *mide(N2, mts, mc, U), coste)
        N3 = list(zip(t, -s))
        fila("  N3 la senal al reves", *mide(N3, mts, mc, U), coste)
print("\n  * = el IC95 entero por encima del coste     + = el IC95 entero por encima de cero")
