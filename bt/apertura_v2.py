"""Version CORREGIDA: el sesgo usa el dia ANTERIOR ya cerrado.

FALLO ENCONTRADO: la version anterior usaba b1[k] = signo del cierre diario
del PROPIO dia k contra el de k-1. Operando a las 08:00, ese cierre ocurre 16
horas DESPUES. Miraba al futuro, y era la pieza que hacia funcionar la
estrategia: las seis mejores celdas de los tres instrumentos llevaban sesgo.

Ahora: sesgo = signo del cierre del dia k-1 contra el del dia k-2, ambos
completamente cerrados antes de que empiece el dia k.

  PAR=EURUSD python3 bt/apertura_v2.py
"""
import os, itertools, numpy as np, pandas as pd
PAR = os.environ.get("PAR", "EURUSD")
INFO = {"EURUSD": (["data/eurusd_m1.parquet"], 1e-4, 1.43),
        "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
        "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
        "US100":  (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
        "US500":  (["data/spxusd_m1.parquet"], 1e-0, 0.60),
        "GER40":  (["data/grxeur_m1.parquet","data/grxeur_m1_2026.parquet"], 1e-0, 1.20)}
rutas, U, COSTE = INFO[PAR]
X = pd.concat([pd.read_parquet(r) for r in rutas], ignore_index=True)
X["ts"]=pd.to_datetime(X["ts"]); X = X.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
lo = X.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/London").dt.tz_localize(None)
X["t"]=lo; X["d"]=lo.dt.date; X["m"]=lo.dt.hour*60+lo.dt.minute
X = X[(lo.dt.dayofweek<5).to_numpy()].reset_index(drop=True)

G = {d: g for d, g in X.groupby("d")}; dias = sorted(G)
# cierre de cada dia de mercado, indexado igual que `dias`
cierre = np.array([float(G[d].close.iloc[-1]) for d in dias])
# sesgo utilizable el dia k: signo de cierre[k-1] - cierre[k-2]  (los dos cerrados)
SESGO = np.full(len(dias), 0)
SESGO[2:] = np.sign(cierre[1:-1] - cierre[:-2]).astype(int)
print(f"{PAR} · {len(dias)} dias · sesgo del dia k = signo(cierre[k-1]-cierre[k-2])")

def dia_estr(g, apert, buf, rr, usa_bias, sesgo):
    A = g[(g["m"] >= apert) & (g["m"] < apert+15)]
    if len(A) < 10: return None
    AH, AL = float(A.high.max()), float(A.low.min())
    if (AH-AL)/U < 4: return None
    W = g[(g["m"] >= apert+15) & (g["m"] <= apert+315)]
    if len(W) < 60: return None
    E = W.set_index("t").resample("5min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    E = E[E.n >= 2]
    if len(E) < 8: return None
    o,h,l,c = E.o.to_numpy(), E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy()
    for i in range(len(E)-2):
        if   h[i] > AH and c[i] < AH: lado, ext = -1, h[i]
        elif l[i] < AL and c[i] > AL: lado, ext = +1, l[i]
        else: continue
        if usa_bias and sesgo != lado: return None
        conf = None
        for j in range(i+1, min(i+7, len(E))):
            rg = h[j]-l[j]
            if rg <= 0 or abs(c[j]-o[j])/rg < 0.5: continue
            if (lado<0 and c[j]<o[j]) or (lado>0 and c[j]>o[j]): conf=j; break
        if conf is None: return None
        P = g[g["t"] >= E.index[conf] + pd.Timedelta(minutes=5)]
        if len(P) < 30: return None
        px = float(P.open.iloc[0])
        stop = ext + buf*U if lado<0 else ext - buf*U
        rgo = abs(px-stop)
        if rgo < 2*U or rgo > 40*U: return None
        tp = px + lado*rgo*rr
        ph, pl = P.high.to_numpy(), P.low.to_numpy()
        aa = (np.flatnonzero(pl[1:]<=tp) if lado<0 else np.flatnonzero(ph[1:]>=tp))
        bb = (np.flatnonzero(ph>=stop)  if lado<0 else np.flatnonzero(pl<=stop))
        ia = int(aa[0])+1 if len(aa) else 10**9
        ib = int(bb[0])   if len(bb) else 10**9
        if ia == ib == 10**9: return None
        return (rr if ia<ib else -1.0) - COSTE/(rgo/U)
    return None

out = []
for apert, buf, rr, ub in itertools.product((480,540,780),(1.0,3.0),(2.0,3.0),(False,True)):
    R = [r for k in range(2, len(dias))
         if (r := dia_estr(G[dias[k]], apert, buf, rr, ub, int(SESGO[k]))) is not None]
    if len(R) < 60: continue
    R = np.array(R)
    out.append(dict(apert=apert, buf=buf, rr=rr, bias=ub, n=len(R), R=float(R.mean()),
                    z=float(R.mean()/(R.std(ddof=1)/np.sqrt(len(R))))))
D = pd.DataFrame(out)
print(f"\n=== {PAR} · {len(D)} celdas · SESGO CORREGIDO ===")
print(f"  {'apert':>7} {'buf':>5} {'rr':>4} {'bias':>6} {'n':>6} {'R neta':>9} {'z':>7}")
for _, r in D.sort_values("z", ascending=False).head(8).iterrows():
    hh=f"{int(r.apert)//60:02d}:{int(r.apert)%60:02d}"
    print(f"  {hh:>7} {r.buf:>5.1f} {r.rr:>4.0f} {str(bool(r.bias)):>6} {int(r.n):>6} "
          f"{r.R:>+9.4f} {r.z:>+7.2f}")
print(f"\n  mejor z {D.z.max():+.2f} · celdas z>2 {int((D.z>2).sum())}/{len(D)} · "
      f"celdas R>0 {int((D.R>0).sum())}/{len(D)}")
