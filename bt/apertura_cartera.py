"""La MISMA celda ganadora, aplicada a todos los instrumentos disponibles.

No se optimiza nada: 08:00 Londres, buffer 3 pips, objetivo 3R, con filtro de
sesgo. Los mismos parametros que ganaron en EURUSD.

Compromiso declarado ANTES de correrlo: se usa el AGREGADO de todos los
instrumentos, funcionen o no. Seleccionar despues los que salieron bien seria
volver a hacer trampa.

  python3 bt/apertura_cartera.py
"""
import os, numpy as np, pandas as pd
APERT, BUF, RR = 480, 3.0, 3.0
INFO = {
 "EURUSD": (["data/eurusd_m1.parquet"], 1e-4, 1.43),
 "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
 "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
 "XAUUSD": (["data/xauusd_m1.parquet","data/xauusd_m1_2026.parquet"], 1e-2, 20.0),
 "US100":  (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
 "US500":  (["data/spxusd_m1.parquet"], 1e-0, 0.60),
 "GER40":  (["data/grxeur_m1.parquet","data/grxeur_m1_2026.parquet"], 1e-0, 1.20),
}

def corre(par):
    rutas, U, COSTE = INFO[par]
    X = pd.concat([pd.read_parquet(r) for r in rutas], ignore_index=True)
    X["ts"] = pd.to_datetime(X["ts"])
    X = X.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    lo = X.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/London").dt.tz_localize(None)
    X["t"]=lo; X["d"]=lo.dt.date; X["m"]=lo.dt.hour*60+lo.dt.minute
    X = X[(lo.dt.dayofweek<5).to_numpy()].reset_index(drop=True)
    D1 = X.set_index("t").resample("1440min").agg(c=("close","last")).dropna()
    b1 = np.sign(D1.c.diff()).to_numpy()
    G = {d: g for d, g in X.groupby("d")}; dias = sorted(G)
    R, F = [], []
    for k in range(1, len(dias)):
        g = G[dias[k]]
        sg = int(b1[min(k,len(b1)-1)]) if not np.isnan(b1[min(k,len(b1)-1)]) else 0
        A = g[(g["m"] >= APERT) & (g["m"] < APERT+15)]
        if len(A) < 10: continue
        AH, AL = float(A.high.max()), float(A.low.min())
        if (AH-AL)/U < 4: continue
        W = g[(g["m"] >= APERT+15) & (g["m"] <= APERT+315)]
        if len(W) < 60: continue
        E = W.set_index("t").resample("5min", label="left", closed="left").agg(
            o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna()
        E = E[E.n >= 2]
        if len(E) < 8: continue
        o,h,l,c = E.o.to_numpy(), E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy()
        for i in range(len(E)-2):
            if   h[i] > AH and c[i] < AH: lado, ext = -1, h[i]
            elif l[i] < AL and c[i] > AL: lado, ext = +1, l[i]
            else: continue
            if sg != lado: break
            conf = None
            for j in range(i+1, min(i+7, len(E))):
                rg = h[j]-l[j]
                if rg <= 0 or abs(c[j]-o[j])/rg < 0.5: continue
                if (lado<0 and c[j]<o[j]) or (lado>0 and c[j]>o[j]): conf=j; break
            if conf is None: break
            P = g[g["t"] >= E.index[conf] + pd.Timedelta(minutes=5)]
            if len(P) < 30: break
            px = float(P.open.iloc[0])
            stop = ext + BUF*U if lado<0 else ext - BUF*U
            rgo = abs(px-stop)
            if rgo < 2*U or rgo > 40*U: break
            tp = px + lado*rgo*RR
            ph, pl = P.high.to_numpy(), P.low.to_numpy()
            aa = (np.flatnonzero(pl[1:]<=tp) if lado<0 else np.flatnonzero(ph[1:]>=tp))
            bb = (np.flatnonzero(ph>=stop)  if lado<0 else np.flatnonzero(pl<=stop))
            ia = int(aa[0])+1 if len(aa) else 10**9
            ib = int(bb[0])   if len(bb) else 10**9
            if ia == ib == 10**9: break
            R.append((RR if ia<ib else -1.0) - COSTE/(rgo/U)); F.append(dias[k]); break
    return np.array(R), F

print("=== LA MISMA CELDA (08:00 · buffer 3 · 3R · con sesgo) EN TODO ===\n")
print(f"  {'instr':>8} {'n':>6} {'op/dia':>8} {'R neta':>9} {'z':>7} {'acierto':>9}")
tot, todas = [], {}
for par in INFO:
    try:
        R, F = corre(par)
    except Exception as e:
        print(f"  {par:>8}  error: {type(e).__name__}"); continue
    if len(R) < 40: print(f"  {par:>8} {len(R):>6}  muestra corta"); continue
    z = R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))
    nd = len(set(F))
    print(f"  {par:>8} {len(R):>6} {len(R)/max(nd,1):>8.2f} {R.mean():>+9.4f} "
          f"{z:>+7.2f} {(R>0).mean()*100:>8.1f}%", flush=True)
    tot.append(R); todas[par] = (R, F)
if tot:
    A = np.concatenate(tot)
    z = A.mean()/(A.std(ddof=1)/np.sqrt(len(A)))
    print(f"\n  {'AGREGADO':>8} {len(A):>6} {'':>8} {A.mean():>+9.4f} {z:>+7.2f} "
          f"{(A>0).mean()*100:>8.1f}%")
    print(f"\n  instrumentos positivos: {sum(1 for p,(R,_) in todas.items() if R.mean()>0)}"
          f"/{len(todas)}")
    dias_tot = len(set().union(*[set(F) for _,F in todas.values()]))
    print(f"  operaciones al dia con la cartera entera: {len(A)/max(dias_tot,1):.2f}")
