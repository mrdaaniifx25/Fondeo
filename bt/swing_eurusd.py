"""Estrategia de swing en EURUSD desde cero, con stops anchos.

Preregistro en docs/PREREGISTRO_swing_eurusd.md.

La mitad del mapa que este proyecto no habia tocado: stops de 60 a 400 pips,
donde el coste vale el 1-3 % del riesgo en vez del 13-27 %.

  python3 bt/swing_eurusd.py
"""
import os, itertools, numpy as np, pandas as pd

PAR   = os.environ.get("PAR", "EURUSD")
NULOS = int(os.environ.get("NULOS", 5))
BLOQ  = 20                                   # bloques de 20 dias
rng   = np.random.default_rng(20260905)
INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
         "XAUUSD": ("data/xauusd_m1.parquet", 1e-2, 20.0)}
NS   = (5, 10, 20, 40, 60, 120, 250)
SS   = (1.0, 2.0, 3.0, 5.0)
ruta, U, COSTE = INSTR[PAR]

def diarias(ruta):
    """Velas diarias con cierre a las 17:00 de Nueva York, convencion FX."""
    x = pd.read_parquet(ruta); x["ts"] = pd.to_datetime(x["ts"])
    ny = x.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    d  = (ny - pd.Timedelta(hours=17)).dt.date          # el dia FX
    g = x.assign(d=d).groupby("d").agg(o=("open","first"), h=("high","max"),
        l=("low","min"), c=("close","last"), n=("close","size"))
    g = g[g.n >= 400]
    g.index = pd.to_datetime(g.index)
    return g[g.index.dayofweek < 5]

def atr(g, k=20):
    tr = pd.concat([g.h-g.l, (g.h-g.c.shift()).abs(), (g.l-g.c.shift()).abs()],
                   axis=1).max(axis=1)
    return tr.rolling(k).mean()

def senal(g, fam, N):
    c = g.c
    if fam == "A": s = np.sign(c - c.shift(N))
    elif fam == "B":
        s = pd.Series(0.0, index=c.index)
        s[c >= c.shift(1).rolling(N).max()] = +1
        s[c <= c.shift(1).rolling(N).min()] = -1
        s = s.replace(0, np.nan).ffill()
    else:
        m = c.shift(1).rolling(N).mean(); sd = c.shift(1).rolling(N).std()
        s = -np.sign((c - m)/sd).where(((c-m)/sd).abs() > 1.0)
        s = s.ffill(limit=N)
    return s.shift(1)                       # la senal de hoy opera MANANA

def corre(g, fam, N, S):
    """Devuelve la serie de P&L diaria en unidades de R (R = S x ATR)."""
    A = atr(g).shift(1)
    s = senal(g, fam, N).reindex(g.index)
    r = (g.c - g.c.shift(1))                # en precio
    riesgo = S*A                            # tamano del stop, en precio
    pos = s.fillna(0.0)
    # stop: si la vela va S x ATR en contra desde el cierre previo, se corta ahi
    peor = np.where(pos > 0, (g.l - g.c.shift(1)), (g.c.shift(1) - g.h))
    tocado = peor <= -riesgo
    pnl_bruto = np.where(tocado, -riesgo, pos*r)
    pnl_bruto = np.where(pos == 0, 0.0, pnl_bruto)
    cambia = pos.diff().abs().fillna(0) > 0
    pnl = (pnl_bruto - np.where(cambia, COSTE*U, 0.0))/riesgo
    return pd.Series(pnl, index=g.index).replace([np.inf,-np.inf], np.nan).dropna()

def stats(p):
    if len(p) < 100: return None
    m, sd = p.mean(), p.std(ddof=1)
    t = m/(sd/np.sqrt(len(p)))
    # bootstrap de bloques, que conserva la autocorrelacion
    nb = len(p)//BLOQ
    v = p.to_numpy()[:nb*BLOQ].reshape(nb, BLOQ)
    bs = v[rng.integers(0, nb, size=(2000, nb))].mean(axis=(1,2))
    return dict(n=len(p), R=float(m), t=float(t),
                sharpe=float(m/sd*np.sqrt(252)),
                lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                tb=float(m/bs.std(ddof=1)))

def rejilla(g, etiq=""):
    out = []
    for fam, N, S in itertools.product("ABC", NS, SS):
        p = corre(g, fam, N, S)
        for per, sub in (("ajuste", p[p.index.year <= 2023]),
                         ("fuera",  p[p.index.year >= 2024])):
            st = stats(sub)
            if st: out.append(dict(fam=fam, N=N, S=S, per=per, etiq=etiq, **st))
    return pd.DataFrame(out)

def baraja(g):
    """Permutacion de bloques de 20 dias sobre los retornos logaritmicos."""
    lr = np.log(g.c).diff().dropna().to_numpy()
    amp = ((g.h-g.l)/g.c).to_numpy()[1:]
    nb = len(lr)//BLOQ
    o = rng.permutation(nb)
    idx = (o[:,None]*BLOQ + np.arange(BLOQ)[None,:]).ravel()
    px = g.c.iloc[0]*np.exp(np.cumsum(lr[idx])); m = len(px)
    op = np.r_[g.c.iloc[0], px[:-1]]; a = amp[idx]*px
    return pd.DataFrame(dict(o=op, h=np.maximum(op,px)+a*rng.random(m)*0.5,
        l=np.minimum(op,px)-a*rng.random(m)*0.5, c=px), index=g.index[:m])

G = diarias(ruta)
print(f"{PAR} · {len(G)} dias · {G.index[0].date()} -> {G.index[-1].date()}")
print(f"  ATR(20) mediano {atr(G).median()/U:.1f} pips  ->  "
      f"stop de {atr(G).median()/U*1:.0f} a {atr(G).median()/U*5:.0f} pips")
print(f"  coste/riesgo: de {COSTE/(atr(G).median()/U*5)*100:.1f} % a "
      f"{COSTE/(atr(G).median()/U*1)*100:.1f} %\n")

D = rejilla(G, "real"); D.to_csv(f"data/swing_{PAR}.csv", index=False)
A = D[D.per=="ajuste"].set_index(["fam","N","S"])
F = D[D.per=="fuera"].set_index(["fam","N","S"])
J = A[["R","t","sharpe"]].join(F[["R","t","sharpe"]], rsuffix="_f").dropna()

print("=== las 8 mejores del AJUSTE 2020-2023, y su comportamiento despues ===")
print(f"  {'fam':>4} {'N':>4} {'S':>4} | {'R aj':>8} {'t':>6} {'Sh':>6} | "
      f"{'R fuera':>8} {'t':>6} {'Sh':>6}")
for i, r in J.sort_values("t", ascending=False).head(8).iterrows():
    print(f"  {i[0]:>4} {i[1]:>4} {i[2]:>4.0f} | {r.R:+8.4f} {r.t:+6.2f} "
          f"{r.sharpe:+6.2f} | {r.R_f:+8.4f} {r.t_f:+6.2f} {r.sharpe_f:+6.2f}")
print(f"\n  correlacion ajuste/fuera de muestra ({len(J)} celdas): "
      f"{np.corrcoef(J.t, J.t_f)[0,1]:+.3f}")
print(f"  mejor t fuera de muestra: {J.t_f.max():+.2f}   ·   "
      f"celdas con t>2 fuera: {int((J.t_f>2).sum())}/{len(J)}")

print("\n=== signo medio por familia y plazo (t del AJUSTE completo) ===")
T = D[D.per=="ajuste"].pivot_table(index="N", columns="fam", values="t", aggfunc="mean")
print(T.round(2).to_string())

print(f"\n=== {NULOS} NULOS ===")
mx = []
for k in range(NULOS):
    Nl = rejilla(baraja(G), f"nulo{k}")
    v = Nl[Nl.per=="ajuste"].t.max(); mx.append(v)
    print(f"  nulo {k+1}: mejor t {v:+.2f}   celdas t>2 "
          f"{int((Nl[Nl.per=='ajuste'].t>2).sum())}/{len(Nl[Nl.per=='ajuste'])}",
          flush=True)
mx = np.array(mx)
print(f"\n  mejor t de un nulo: media {mx.mean():+.2f}  rango {mx.min():+.2f} a {mx.max():+.2f}")
print(f"  mejor t real (ajuste): {D[D.per=='ajuste'].t.max():+.2f}")

# --------------------------------------------------------------------------
# El estadistico correcto no es "el mejor t de 84 celdas" -eso mide la
# busqueda- sino si el PATRON de signos (momento y rotura a favor, reversion
# en contra) aparece de verdad. Se compara con los nulos y con otros pares.
# --------------------------------------------------------------------------
def patron(D):
    """t medio de A y B menos t medio de C, sobre todas las celdas."""
    a = D[(D.per=="ajuste") & (D.fam.isin(list("AB")))].t.mean()
    c = D[(D.per=="ajuste") & (D.fam=="C")].t.mean()
    return a - c, a, c

print("\n" + "="*70)
print("EL PATRON DE SIGNOS · (momento+rotura) menos reversion")
print("="*70)
p, a, c = patron(D)
print(f"  {PAR:8s} REAL      AB {a:+.3f}   C {c:+.3f}   patron {p:+.3f}")
pn = []
for k in range(NULOS):
    Nl = rejilla(baraja(G), f"n{k}")
    q, aa, cc = patron(Nl); pn.append(q)
    print(f"  {'':8s} nulo {k+1}    AB {aa:+.3f}   C {cc:+.3f}   patron {q:+.3f}",
          flush=True)
pn = np.array(pn)
print(f"\n  patron real {p:+.3f}   ·   nulos: media {pn.mean():+.3f}, "
      f"rango {pn.min():+.3f} a {pn.max():+.3f}")
print(f"  ¿supera el real a TODOS los nulos? "
      f"{'SI' if p > pn.max() else 'NO'}")

print("\n=== el mismo patron en los otros pares (replicacion) ===")
for otro in ("GBPUSD", "USDJPY", "XAUUSD"):
    try:
        r2, U2, C2 = INSTR[otro]
        COSTE, U = C2, U2
        G2 = diarias(r2)
        D2 = rejilla(G2, otro)
        q, aa, cc = patron(D2)
        print(f"  {otro:8s} AB {aa:+.3f}   C {cc:+.3f}   patron {q:+.3f}   "
              f"({len(G2)} dias)", flush=True)
    except Exception as e:
        print(f"  {otro:8s} error: {type(e).__name__}")
