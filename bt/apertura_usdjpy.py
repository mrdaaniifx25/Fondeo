"""USDJPY con la UNIDAD y el COSTE correctos.

El pase anterior dio "sin operaciones" y no era el mercado: U estaba fijado a
1e-4 para todos los pares, y un pip de USDJPY es 1e-2. El filtro
"rgo > 40*U" rechazaba todo lo que tuviera stop mayor de medio pip.

  PAR=USDJPY python3 bt/apertura_usdjpy.py
"""
import os, itertools, numpy as np, pandas as pd
PAR = os.environ.get("PAR", "USDJPY")
INFO = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
        "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
        "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
        "XAUUSD": ("data/xauusd_m1.parquet", 1e-2, 20.0)}
ruta, U, COSTE = INFO[PAR]
rng = np.random.default_rng(20260906)

X = pd.read_parquet(ruta); X["ts"] = pd.to_datetime(X["ts"])
X = X.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
lo = X.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/London").dt.tz_localize(None)
X["t"]=lo; X["d"]=lo.dt.date; X["m"]=lo.dt.hour*60+lo.dt.minute
X = X[(lo.dt.dayofweek<5).to_numpy()].reset_index(drop=True)
print(f"{PAR} · {len(X)} minutos · pip {U} · coste {COSTE} pips")

def dia_estr(g, apert, buf, rr, usa_bias, sesgo):
    A = g[(g["m"] >= apert) & (g["m"] < apert+15)]
    if len(A) < 10: return None
    AH, AL = float(A.high.max()), float(A.low.min())
    if (AH-AL)/U < 4: return None
    W = g[(g["m"] >= apert+15) & (g["m"] <= apert+15+300)]
    if len(W) < 60: return None
    E = W.set_index("t").resample("5min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    E = E[E.n >= 2]
    if len(E) < 8: return None
    o,h,l,c = E.o.to_numpy(), E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy()
    n = len(E)
    for i in range(n-2):
        if   h[i] > AH and c[i] < AH: lado, ext, obj = -1, h[i], AL
        elif l[i] < AL and c[i] > AL: lado, ext, obj = +1, l[i], AH
        else: continue
        if usa_bias and sesgo != lado: return None
        conf = None
        for j in range(i+1, min(i+7, n)):
            rg = h[j]-l[j]
            if rg <= 0 or abs(c[j]-o[j])/rg < 0.5: continue
            if (lado < 0 and c[j] < o[j]) or (lado > 0 and c[j] > o[j]): conf = j; break
        if conf is None: return None
        P = g[g["t"] >= E.index[conf] + pd.Timedelta(minutes=5)]
        if len(P) < 30: return None
        px = float(P.open.iloc[0])
        stop = ext + buf*U if lado < 0 else ext - buf*U
        rgo = abs(px-stop)
        if rgo < 2*U or rgo > 40*U: return None
        tp = px + lado*rgo*rr if rr else obj
        if (tp-px)*lado <= 0: return None
        ph, pl = P.high.to_numpy(), P.low.to_numpy()
        aa = (np.flatnonzero(pl[1:] <= tp) if lado < 0 else np.flatnonzero(ph[1:] >= tp))
        bb = (np.flatnonzero(ph >= stop) if lado < 0 else np.flatnonzero(pl <= stop))
        ia = int(aa[0])+1 if len(aa) else 10**9
        ib = int(bb[0])   if len(bb) else 10**9
        if ia == ib == 10**9: return None
        gan = abs(tp-px)/rgo
        return (gan if ia < ib else -1.0) - COSTE/(rgo/U)
    return None

D1 = X.set_index("t").resample("1440min").agg(c=("close","last")).dropna()
b1 = np.sign(D1.c.diff()).to_numpy()
G = {d: g for d, g in X.groupby("d")}; dias = sorted(G)
out = []
for apert, buf, rr, ub in itertools.product((480,540,780),(1.0,3.0),(2.0,3.0,0),(False,True)):
    R = []
    for k in range(1, len(dias)):
        sg = int(b1[min(k,len(b1)-1)]) if not np.isnan(b1[min(k,len(b1)-1)]) else 0
        r = dia_estr(G[dias[k]], apert, buf, rr, ub, sg)
        if r is not None: R.append(r)
    if len(R) < 60: continue
    R = np.array(R)
    out.append(dict(apert=apert, buf=buf, rr=rr, bias=ub, n=len(R), R=float(R.mean()),
                    z=float(R.mean()/(R.std(ddof=1)/np.sqrt(len(R))))))
D = pd.DataFrame(out)
print(f"\n=== {PAR} · {len(D)} celdas ===")
print(f"  {'apert':>7} {'buf':>5} {'rr':>5} {'bias':>6} {'n':>6} {'R neta':>9} {'z':>7}")
for _, r in D.sort_values("z", ascending=False).head(6).iterrows():
    hh=f"{int(r.apert)//60:02d}:{int(r.apert)%60:02d}"
    print(f"  {hh:>7} {r.buf:>5.1f} {('opuesto' if r.rr==0 else f'{r.rr:.0f}'):>5} "
          f"{str(bool(r.bias)):>6} {int(r.n):>6} {r.R:>+9.4f} {r.z:>+7.2f}")
print(f"\n  mejor z {D.z.max():+.2f} · celdas z>2 {int((D.z>2).sum())}/{len(D)} · "
      f"celdas R>0 {int((D.R>0).sum())}/{len(D)}")
