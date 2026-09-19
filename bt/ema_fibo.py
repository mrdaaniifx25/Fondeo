"""EMA + Fibonacci en EURUSD, la rejilla entera. Y la misma rejilla sobre
datos SIN ninguna ventaja, para saber que produce buscar.

  tendencia   cierre por encima/debajo de la EMA(N) -> solo compras/ventas
  impulso     ultima pierna confirmada por fractales de Williams (causal)
  entrada     orden limitada en el retroceso de Fibonacci F de esa pierna
  stop        en el origen de la pierna (el 100 % del fibo)
  objetivo    multiplo R:R del riesgo
  vida        96 velas; si no entra, se anula

El NULO es EURUSD remuestreado por bloques de 60 minutos: misma volatilidad,
mismo agrupamiento de volatilidad, ningun patron de mas de una hora.

  NULOS=10 python3 bt/ema_fibo.py
"""
import os, itertools, numpy as np, pandas as pd

TFS  = (15, 60, 240)
EMAS = (10, 20, 50, 100, 200)
FIBS = (0.382, 0.500, 0.618, 0.705, 0.786)
RRS  = (1.0, 2.0, 3.0)
VIDA, U, COSTE = 96, 1e-4, 1.43          # coste medido en docs/COSTE_real.md
NULOS = int(os.environ.get("NULOS", 10))
BLOQ  = 60
rng   = np.random.default_rng(20260905)

d = pd.read_parquet("data/eurusd_m1.parquet")
d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
d = d.reset_index(drop=True)
print(f"EURUSD · {len(d)} minutos · {d.ts.min()} -> {d.ts.max()}")

def sintetico(base):
    """Mismos retornos, en bloques barajados: sin patrones de mas de 60 min."""
    lr = np.diff(np.log(base.close.to_numpy()))
    nb = len(lr)//BLOQ
    st = rng.integers(0, len(lr)-BLOQ, size=nb)
    nl = (st[:, None] + np.arange(BLOQ)[None, :]).ravel()
    px = base.close.iloc[0]*np.exp(np.cumsum(lr[nl]))
    n  = len(px)
    o  = np.concatenate([[base.close.iloc[0]], px[:-1]])
    # alto y bajo sinteticos coherentes con el rango real medio de cada minuto
    amp = (base.high - base.low).to_numpy()[:n]
    hi  = np.maximum(o, px) + amp*rng.random(n)*0.5
    lo  = np.minimum(o, px) - amp*rng.random(n)*0.5
    return pd.DataFrame(dict(ts=base.ts.to_numpy()[:n], open=o,
                             high=hi, low=lo, close=px))

def agrega(x, m):
    g = x.set_index("ts").resample(f"{m}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return g[g.n >= max(1, m*0.4)].reset_index()

def senales(E, per):
    """Devuelve (i, lado, A, B): pierna de A a B confirmada en la barra i."""
    o,h,l,c = (E.o.to_numpy(), E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy())
    n = len(c)
    ema = pd.Series(c).ewm(span=per, adjust=False).mean().to_numpy()
    # fractales confirmados dos velas despues -> usables en i >= j+2
    fh = np.zeros(n, bool); fl = np.zeros(n, bool)
    fh[2:n-2] = ((h[2:n-2] > h[1:n-3]) & (h[2:n-2] > h[0:n-4]) &
                 (h[2:n-2] > h[3:n-1]) & (h[2:n-2] > h[4:n]))
    fl[2:n-2] = ((l[2:n-2] < l[1:n-3]) & (l[2:n-2] < l[0:n-4]) &
                 (l[2:n-2] < l[3:n-1]) & (l[2:n-2] < l[4:n]))
    # ultimo fractal alto y bajo CONFIRMADO en cada barra
    ih = np.where(fh, np.arange(n), -1); ih = np.maximum.accumulate(np.roll(ih, 2))
    il = np.where(fl, np.arange(n), -1); il = np.maximum.accumulate(np.roll(il, 2))
    ih[:4] = -1; il[:4] = -1
    S = []
    alc = c > ema
    for i in range(210, n-1):
        if ih[i] < 0 or il[i] < 0: continue
        if alc[i] and il[i] < ih[i]:            # pierna al alza: bajo -> alto
            S.append((i, +1, l[il[i]], h[ih[i]]))
        elif (not alc[i]) and ih[i] < il[i]:    # pierna a la baja: alto -> bajo
            S.append((i, -1, h[ih[i]], l[il[i]]))
    return S, (E.h.to_numpy(), E.l.to_numpy())

def evalua(S, HL, fib, rr):
    h, l = HL; n = len(h); R = []
    for i, lado, A, B in S:
        rec = abs(B-A)
        if rec < 5*U: continue
        ent  = B - lado*rec*fib
        stop = A
        rgo  = abs(ent-stop)
        if rgo < 3*U: continue
        tp   = ent + lado*rgo*rr
        j0, j1 = i+1, min(i+1+VIDA, n)
        if j1 <= j0: continue
        hh, ll = h[j0:j1], l[j0:j1]
        # ¿entra?
        e = np.flatnonzero(ll <= ent) if lado > 0 else np.flatnonzero(hh >= ent)
        if not len(e): continue
        k = e[0]
        # La barra que EJECUTA la orden limitada no puede contar como objetivo:
        # su maximo (en compras) es casi siempre anterior al llenado, porque el
        # precio venia de arriba. Contarlo es mirar al futuro dentro de la vela.
        # El stop SI se mira en esa barra, que es lo conservador.
        st = (ll[k:] <= stop) if lado > 0 else (hh[k:] >= stop)
        ob = (hh[k+1:] >= tp) if lado > 0 else (ll[k+1:] <= tp)
        b = np.flatnonzero(st); a = np.flatnonzero(ob)
        ia = a[0]+1 if len(a) else 10**9
        ib = b[0]   if len(b) else 10**9
        if ia == ib == 10**9: continue
        R.append((rr if ia < ib else -1.0) - COSTE*U/rgo)    # empate = stop
    return np.array(R)

def rejilla(base, etiq):
    out = []
    for tf in TFS:
        E = agrega(base, tf)
        for per in EMAS:
            S, HL = senales(E, per)
            for fib, rr in itertools.product(FIBS, RRS):
                R = evalua(S, HL, fib, rr)
                if len(R) < 60: continue
                z = R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))
                out.append(dict(tf=tf, ema=per, fib=fib, rr=rr,
                                n=len(R), R=float(R.mean()), z=float(z)))
    D = pd.DataFrame(out); D["fuente"] = etiq
    return D

REAL = rejilla(d, "real")
REAL.to_csv("data/ema_fibo_real.csv", index=False)
print(f"\n=== REJILLA REAL · {len(REAL)} celdas ===")
B = REAL.sort_values("z", ascending=False)
print(f"  {'tf':>4} {'ema':>4} {'fib':>6} {'rr':>4} {'n':>6} {'R neta':>9} {'z':>7}")
for _, r in B.head(8).iterrows():
    print(f"  {int(r.tf):4d} {int(r.ema):4d} {r.fib:6.3f} {r.rr:4.1f} "
          f"{int(r.n):6d} {r.R:+9.4f} {r.z:+7.2f}")
print(f"\n  mejor z {B.z.max():+.2f}   ·   celdas con z > 2: "
      f"{int((REAL.z>2).sum())}/{len(REAL)}   ·   z medio {REAL.z.mean():+.3f}")

print(f"\n=== {NULOS} REJILLAS SOBRE DATOS SIN VENTAJA ===")
mx = []
for k in range(NULOS):
    N = rejilla(sintetico(d), f"nulo{k}")
    mx.append(N.z.max())
    print(f"  nulo {k+1:2d}: {len(N)} celdas · mejor z {N.z.max():+.2f} · "
          f"celdas z>2 {int((N.z>2).sum())}", flush=True)
mx = np.array(mx)
print(f"\n  el mejor z de una rejilla SIN VENTAJA:")
print(f"    media {mx.mean():+.2f}   ·   rango {mx.min():+.2f} a {mx.max():+.2f}")
print(f"  el mejor z de la rejilla REAL: {B.z.max():+.2f}")
print(f"  percentil de lo real dentro de los nulos: "
      f"{float((mx < B.z.max()).mean())*100:.0f} %")
