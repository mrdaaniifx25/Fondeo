"""Lo que el describio primero, y era lo correcto:

  la PRIMERA vela de M15 de la apertura marca maximo y minimo
  -> se espera un barrido de uno de los dos extremos en M5
  -> confirmacion (desplazamiento) en M5
  -> entrada en M1
  -> objetivo el extremo opuesto de esa vela M15, o R:R fijo

Un setup al dia como maximo. Filtro de BIAS de D1 o H4 opcional.

  python3 bt/apertura_eurusd.py
"""
import os, itertools, numpy as np, pandas as pd
U, COSTE = 1e-4, 1.43
NULOS = int(os.environ.get("NULOS", 3))
rng = np.random.default_rng(20260906)

M = pd.read_parquet("data/eurusd_m1.parquet"); M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
lon = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/London").dt.tz_localize(None)
M["t"] = lon; M["d"] = lon.dt.date; M["m"] = lon.dt.hour*60 + lon.dt.minute
M = M[(lon.dt.dayofweek < 5).to_numpy()].reset_index(drop=True)
print(f"EURUSD · {len(M)} minutos · {M.d.min()} -> {M.d.max()}")

def dia_estr(g, gp, apert, buf, rr, usa_bias, sesgo):
    """apert = minuto de la apertura. Devuelve R neta o None."""
    A = g[(g["m"] >= apert) & (g["m"] < apert+15)]
    if len(A) < 10: return None
    AH, AL = float(A.high.max()), float(A.low.min())
    if (AH-AL)/U < 4: return None                      # vela plana, sin nivel
    W = g[(g["m"] >= apert+15) & (g["m"] <= apert+15+300)]   # 5 h de ventana
    if len(W) < 60: return None
    E = W.set_index("t").resample("5min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    E = E[E.n >= 2]
    if len(E) < 8: return None
    o,h,l,c = E.o.to_numpy(), E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy()
    n = len(E)
    for i in range(n-2):
        # barrido de un extremo con cierre de vuelta dentro
        if   h[i] > AH and c[i] < AH: lado, ext, obj = -1, h[i], AL
        elif l[i] < AL and c[i] > AL: lado, ext, obj = +1, l[i], AH
        else: continue
        if usa_bias and sesgo != lado: return None
        # confirmacion: desplazamiento en la direccion, dentro de 6 velas M5
        conf = None
        for j in range(i+1, min(i+7, n)):
            rg = h[j]-l[j]
            if rg <= 0: continue
            if abs(c[j]-o[j])/rg < 0.5: continue
            if (lado < 0 and c[j] < o[j]) or (lado > 0 and c[j] > o[j]): conf = j; break
        if conf is None: return None
        t1 = E.index[conf] + pd.Timedelta(minutes=5)
        P = g[g["t"] >= t1]
        if len(P) < 30: return None
        px = float(P.open.iloc[0])
        stop = ext + buf*U if lado < 0 else ext - buf*U
        rgo = abs(px-stop)
        if rgo < 2*U or rgo > 40*U: return None
        tp = px + lado*rgo*rr if rr else obj
        if (tp-px)*lado <= 0: return None
        ph, pl = P.high.to_numpy(), P.low.to_numpy()
        aa = (np.flatnonzero(pl[1:] <= tp) if lado < 0 else np.flatnonzero(ph[1:] >= tp))
        bb = (np.flatnonzero(ph <= 1e9) if False else
              (np.flatnonzero(ph >= stop) if lado < 0 else np.flatnonzero(pl <= stop)))
        ia = int(aa[0])+1 if len(aa) else 10**9
        ib = int(bb[0])   if len(bb) else 10**9
        if ia == ib == 10**9: return None
        # FALLO CORREGIDO: con objetivo "extremo opuesto" (rr=0) las ganadoras
        # se puntuaban como 0,0 R en vez de su R real. Se calcula siempre a
        # partir de la distancia real al objetivo.
        gan = abs(tp-px)/rgo
        return (gan if ia < ib else -1.0) - COSTE/(rgo/U)
    return None

def rejilla(MM, et=""):
    MM = MM.copy()
    D1 = MM.set_index("t").resample("1440min").agg(c=("close","last")).dropna()
    b1 = np.sign(D1.c.diff()).to_numpy()
    G = {d: g for d, g in MM.groupby("d")}
    dias = sorted(G)
    out = []
    for apert, buf, rr, ub in itertools.product((480, 540, 780), (1.0, 3.0),
                                                (2.0, 3.0, 0), (False, True)):
        R = []
        for k in range(1, len(dias)):
            g = G[dias[k]]
            sg = int(b1[min(k, len(b1)-1)]) if not np.isnan(b1[min(k,len(b1)-1)]) else 0
            r = dia_estr(g, G[dias[k-1]], apert, buf, rr, ub, sg)
            if r is not None: R.append(r)
        if len(R) < 60: continue
        R = np.array(R)
        out.append(dict(apert=apert, buf=buf, rr=rr, bias=ub, n=len(R),
                        R=float(R.mean()),
                        z=float(R.mean()/(R.std(ddof=1)/np.sqrt(len(R))))))
    return pd.DataFrame(out)

D = rejilla(M); D.to_csv("data/apertura_eurusd.csv", index=False)
print(f"\n=== REJILLA REAL · {len(D)} celdas ===")
print(f"  {'apert':>7} {'buf':>5} {'rr':>5} {'bias':>6} {'n':>6} {'ops/dia':>8} "
      f"{'R neta':>9} {'z':>7}")
for _, r in D.sort_values("z", ascending=False).head(10).iterrows():
    hh = f"{int(r.apert)//60:02d}:{int(r.apert)%60:02d}"
    print(f"  {hh:>7} {r.buf:>5.1f} {('opuesto' if r.rr==0 else f'{r.rr:.0f}'):>5} "
          f"{str(bool(r.bias)):>6} {int(r.n):>6} {r.n/1700:>8.2f} {r.R:>+9.4f} {r.z:>+7.2f}")
print(f"\n  mejor z {D.z.max():+.2f}  ·  celdas z>2 {int((D.z>2).sum())}/{len(D)}  ·  "
      f"celdas R>0 {int((D.R>0).sum())}/{len(D)}")

# --------------------------------------------------------------------------
# EL NULO · la MISMA rejilla sobre EURUSD con los bloques permutados.
# Sin esto, un z de +4,72 sobre 36 celdas no significa nada: hoy mismo una
# rejilla de 225 celdas sobre datos barajados dio +3,64.
# --------------------------------------------------------------------------
def baraja(x, bl=1440):
    lr = np.diff(np.log(x.close.to_numpy()))
    amp = ((x.high-x.low)/x.close).to_numpy()[1:]
    nb = len(lr)//bl; o = rng.permutation(nb)
    idx = (o[:,None]*bl + np.arange(bl)[None,:]).ravel()
    px = x.close.iloc[0]*np.exp(np.cumsum(lr[idx])); m = len(px)
    op = np.r_[x.close.iloc[0], px[:-1]]; a = amp[idx]*px
    y = x.iloc[:m].copy()
    y["open"], y["close"] = op, px
    y["high"] = np.maximum(op, px) + a*rng.random(m)*0.5
    y["low"]  = np.minimum(op, px) - a*rng.random(m)*0.5
    return y

print(f"\n=== {NULOS} NULOS ===")
mx = []
for k in range(NULOS):
    N = rejilla(baraja(M))
    if not len(N): continue
    mx.append(N.z.max())
    print(f"  nulo {k+1}: mejor z {N.z.max():+.2f}  ·  celdas z>2 "
          f"{int((N.z>2).sum())}/{len(N)}  ·  celdas R>0 {int((N.R>0).sum())}/{len(N)}",
          flush=True)
if mx:
    mx = np.array(mx)
    print(f"\n  mejor z de un nulo: media {mx.mean():+.2f}  "
          f"rango {mx.min():+.2f} a {mx.max():+.2f}")
    print(f"  mejor z REAL: {D.z.max():+.2f}  ->  "
          f"{'SUPERA a todos los nulos' if D.z.max() > mx.max() else 'NO supera'}")
