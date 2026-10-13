"""El CRT diario del NASDAQ tal como lo describe la nota de voz:
rango diario, objetivo en el extremo opuesto, y FILTRO de direccion semanal
("esperas el rango a favor del objetivo").

La pregunta concreta: ¿anade algo ese filtro sobre el +0,042 bruto ya medido?

  python3 bt/crt_semanal.py
"""
import numpy as np, pandas as pd
INSTR = {"NAS100": ("data/nsxusd_m1.parquet", 1e-0, 1.50),
         "SPX500": ("data/spxusd_m1.parquet", 1e-0, 0.60),
         "EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43)}

def corre(par):
    ruta, U, COSTE = INSTR[par]
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    M["t"] = ny
    D = M.set_index("t").resample("1440min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    D = D[D.n >= 400]
    # direccion SEMANAL, usando solo semanas ya cerradas
    W = M.set_index("t").resample("W-SUN", label="right", closed="right").agg(
        c=("close","last")).dropna()
    wdir = np.sign(W.c.diff()).shift(1)              # la semana ANTERIOR, cerrada
    mh, ml, mt = M.high.to_numpy(), M.low.to_numpy(), M.t.to_numpy()
    dh, dl, di = D.h.to_numpy(), D.l.to_numpy(), D.index.to_numpy()
    R = []
    for i in range(1, len(D)-1):
        # la vela i barre un extremo de la i-1 y cierra dentro
        if   dh[i] > dh[i-1] and D.c.iloc[i] < dh[i-1]: lado, ext, obj = -1, dh[i], dl[i-1]
        elif dl[i] < dl[i-1] and D.c.iloc[i] > dl[i-1]: lado, ext, obj = +1, dl[i], dh[i-1]
        else: continue
        k = W.index.searchsorted(di[i])
        wd = wdir.iloc[min(k, len(wdir)-1)]
        wd = 0 if np.isnan(wd) else int(wd)
        ent = float(D.c.iloc[i]); stop = ext
        rgo = abs(ent-stop)
        if rgo < 2*U: continue
        if (obj-ent)*lado <= 0: continue
        j0 = int(np.searchsorted(mt, di[i] + np.timedelta64(1440,"m")))
        j1 = min(j0 + 1440*3, len(mt))
        if j1 <= j0+10: continue
        h_, l_ = mh[j0:j1], ml[j0:j1]
        a = np.flatnonzero(h_ >= obj) if lado > 0 else np.flatnonzero(l_ <= obj)
        b = np.flatnonzero(l_ <= stop) if lado > 0 else np.flatnonzero(h_ >= stop)
        ia = int(a[0]) if len(a) else 10**9
        ib = int(b[0]) if len(b) else 10**9
        if ia == ib == 10**9: continue
        rr = abs(obj-ent)/rgo
        R.append(((rr if ia < ib else -1.0), COSTE/(rgo/U), lado, wd))
    return np.array(R)

z = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v) > 2 else np.nan
print("=== CRT DIARIO · ¿aporta el filtro de direccion SEMANAL? ===\n")
print(f"  {'instr':>7} {'filtro':>16} {'n':>5} {'R BRUTA':>9} {'z':>7} {'R NETA':>9} {'z':>7}")
for par in INSTR:
    X = corre(par)
    if len(X) < 40: print(f"  {par:>7}  muestra corta"); continue
    br, co, lado, wd = X[:,0], X[:,1], X[:,2], X[:,3]
    nt = br - co
    for et, m in (("todas", np.ones(len(br), bool)),
                  ("semanal a favor", lado == wd),
                  ("semanal en contra", (wd != 0) & (lado != wd))):
        if m.sum() < 30: continue
        print(f"  {par:>7} {et:>16} {int(m.sum()):>5} {br[m].mean():>+9.4f} "
              f"{z(br[m]):>+7.2f} {nt[m].mean():>+9.4f} {z(nt[m]):>+7.2f}")
    print()
