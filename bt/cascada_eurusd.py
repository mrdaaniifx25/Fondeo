"""Cascada que el pidio: BIAS (D1 o H4) -> CRT en M15 -> confirmacion M5 -> M1.

Rejilla de 72 celdas y el MISMO proceso sobre datos barajados, para saber si
lo que salga supera a lo que produce buscar.

  NULOS=3 python3 bt/cascada_eurusd.py
"""
import os, itertools, numpy as np, pandas as pd

U, COSTE = 1e-4, 1.43
NULOS = int(os.environ.get("NULOS", 3))
rng = np.random.default_rng(20260906)

M = pd.read_parquet("data/eurusd_m1.parquet"); M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
print(f"EURUSD · {len(M)} minutos · {M.ts.min()} -> {M.ts.max()}")

def barras(x, k):
    g = x.set_index("ts").resample(f"{k}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return g[g.n >= max(1, k*0.3)]

def bias(B, regla):
    c = B.c.to_numpy()
    if regla == "ema20":  m = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
    elif regla == "ema50": m = pd.Series(c).ewm(span=50, adjust=False).mean().to_numpy()
    else:                                     # posicion en el rango de 20 velas
        hi = B.h.rolling(20).max().to_numpy(); lo = B.l.rolling(20).min().to_numpy()
        pos = (c-lo)/np.maximum(hi-lo, 1e-9)
        return np.where(pos > 0.5, 1, -1)
    return np.where(c > m, 1, -1)

def corre(x, tf_bias, regla, buf, rr, entrada):
    B  = barras(x, tf_bias); E = barras(x, 15)
    C5 = barras(x, 5)
    bi = bias(B, regla)
    bt = B.index.to_numpy(); bv = np.r_[np.nan, bi[:-1]]     # bias de la vela CERRADA
    eh, el_, ec, eo = (E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy(), E.o.to_numpy())
    et = E.index.to_numpy(); n = len(E)
    c5h, c5l, c5c, c5o = (C5.h.to_numpy(), C5.l.to_numpy(), C5.c.to_numpy(), C5.o.to_numpy())
    c5t = C5.index.to_numpy()
    mh, ml, mo, mt = (x.high.to_numpy(), x.low.to_numpy(), x.open.to_numpy(),
                      x.ts.to_numpy())
    R = []
    for i in range(2, n-1):
        # CRT: la vela i barre un extremo de la i-1 y CIERRA dentro
        if   eh[i] > eh[i-1] and ec[i] < eh[i-1]: lado, ext, obj = -1, eh[i], el_[i-1]
        elif el_[i] < el_[i-1] and ec[i] > el_[i-1]: lado, ext, obj = +1, el_[i], eh[i-1]
        else: continue
        k = np.searchsorted(bt, et[i], "right")-1
        if k < 1 or np.isnan(bv[k]) or bv[k] != lado: continue   # BIAS a favor
        # confirmacion en M5 tras el cierre de la vela M15
        t0 = et[i] + np.timedelta64(15, "m")
        j0 = int(np.searchsorted(c5t, t0))
        conf = None
        for j in range(j0, min(j0+12, len(C5))):
            rg = c5h[j]-c5l[j]
            if rg <= 0: continue
            if abs(c5c[j]-c5o[j])/rg < 0.5: continue      # desplazamiento
            if (lado < 0 and c5c[j] < c5o[j]) or (lado > 0 and c5c[j] > c5o[j]):
                conf = j; break
        if conf is None: continue
        # entrada en M1
        t1 = c5t[conf] + np.timedelta64(5, "m")
        a = int(np.searchsorted(mt, t1))
        if a >= len(mt)-10: continue
        px = mo[a]
        if entrada == "fvg" and conf >= 1:
            px = (c5o[conf]+c5c[conf])/2                  # 50 % del cuerpo
        stop = ext + lado*buf*U*(-1) if False else (ext + buf*U if lado < 0 else ext - buf*U)
        rgo = abs(px-stop)
        if rgo < 2*U or rgo > 60*U: continue
        tp = px + lado*rgo*rr if rr else obj
        if (tp-px)*lado <= 0: continue
        b = min(a+2880, len(mt))                          # 2 dias de vida
        if entrada == "fvg":
            t = (np.flatnonzero(mh[a:b] >= px) if lado < 0 else np.flatnonzero(ml[a:b] <= px))
            if not len(t): continue
            a = a+int(t[0])
            if a >= b-2: continue
        aa = (np.flatnonzero(ml[a+1:b] <= tp) if lado < 0 else np.flatnonzero(mh[a+1:b] >= tp))
        bb = (np.flatnonzero(mh[a:b] >= stop) if lado < 0 else np.flatnonzero(ml[a:b] <= stop))
        ia = int(aa[0])+1 if len(aa) else 10**9
        ib = int(bb[0])   if len(bb) else 10**9
        if ia == ib == 10**9: continue
        R.append((rr if ia < ib else -1.0) - COSTE*U/rgo)
    if len(R) < 50: return None
    R = np.array(R)
    return dict(n=len(R), R=float(R.mean()),
                z=float(R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))))

def rejilla(x, et=""):
    out = []
    for tfb, reg, buf, rr, ent in itertools.product(
            (240, 1440), ("ema20","ema50","rango"), (1.0, 3.0, 6.0), (2.0, 3.0),
            ("mercado","fvg")):
        r = corre(x, tfb, reg, buf, rr, ent)
        if r: out.append(dict(tfb=tfb, reg=reg, buf=buf, rr=rr, ent=ent, **r))
    return pd.DataFrame(out)

D = rejilla(M, "real"); D.to_csv("data/cascada_eurusd.csv", index=False)
print(f"\n=== REJILLA REAL · {len(D)} celdas ===")
print(f"  {'bias':>6} {'regla':>7} {'buf':>5} {'rr':>4} {'entrada':>9} {'n':>6} "
      f"{'R neta':>9} {'z':>7}")
for _, r in D.sort_values("z", ascending=False).head(8).iterrows():
    print(f"  {'D1' if r.tfb==1440 else 'H4':>6} {r.reg:>7} {r.buf:>5.1f} {r.rr:>4.0f} "
          f"{r.ent:>9} {int(r.n):>6} {r.R:>+9.4f} {r.z:>+7.2f}")
print(f"\n  mejor z {D.z.max():+.2f}  ·  celdas z>2: {int((D.z>2).sum())}/{len(D)}  ·  "
      f"celdas R>0: {int((D.R>0).sum())}/{len(D)}")

def baraja(x, bl=1440):
    lr = np.diff(np.log(x.close.to_numpy()))
    amp = ((x.high-x.low)/x.close).to_numpy()[1:]
    nb = len(lr)//bl; o = rng.permutation(nb)
    idx = (o[:,None]*bl + np.arange(bl)[None,:]).ravel()
    px = x.close.iloc[0]*np.exp(np.cumsum(lr[idx])); m = len(px)
    op = np.r_[x.close.iloc[0], px[:-1]]; a = amp[idx]*px
    return pd.DataFrame(dict(ts=x.ts.to_numpy()[:m], open=op,
        high=np.maximum(op,px)+a*rng.random(m)*0.5,
        low=np.minimum(op,px)-a*rng.random(m)*0.5, close=px))

print(f"\n=== {NULOS} NULOS · la misma rejilla sobre datos barajados ===")
mx = []
for k in range(NULOS):
    N = rejilla(baraja(M), f"n{k}")
    if not len(N): continue
    mx.append(N.z.max())
    print(f"  nulo {k+1}: mejor z {N.z.max():+.2f}  ·  celdas z>2 "
          f"{int((N.z>2).sum())}/{len(N)}  ·  celdas R>0 {int((N.R>0).sum())}/{len(N)}",
          flush=True)
if mx:
    mx = np.array(mx)
    print(f"\n  mejor z de un nulo: media {mx.mean():+.2f}  rango {mx.min():+.2f} a {mx.max():+.2f}")
    print(f"  mejor z REAL: {D.z.max():+.2f}  ->  "
          f"{'SUPERA a todos los nulos' if D.z.max() > mx.max() else 'NO supera a los nulos'}")
