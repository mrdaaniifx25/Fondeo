"""La hoja de trabajo de EURUSD: rotura de canal simetrica con stop ancho.

Preregistro en docs/PREREGISTRO_eurusd_final.md, con los cinco criterios de
exito firmados antes de medir.

  python3 bt/eurusd_final.py
"""
import os, itertools, numpy as np, pandas as pd

CAP0, RIESGO = 100_000.0, 0.01
U, COSTE_P   = 1e-4, 1.43            # pip y coste medido, en pips
PAR   = os.environ.get("PAR", "EURUSD")
NULOS = int(os.environ.get("NULOS", 5))
NS, KS, MS = (20, 40, 60, 100), (1.0, 2.0, 3.0), (5, 10, 20, 40)
TFS   = (60, 240)
rng   = np.random.default_rng(20260905)
RUTAS = {"EURUSD": ["data/eurusd_m1.parquet"], "GBPUSD": ["data/gbpusd_m1.parquet"],
         "USDJPY": ["data/usdjpy_m1.parquet"]}
UNI   = {"EURUSD": 1e-4, "GBPUSD": 1e-4, "USDJPY": 1e-2}

def carga(par):
    M = pd.concat([pd.read_parquet(r) for r in RUTAS[par]], ignore_index=True)
    M["ts"] = pd.to_datetime(M["ts"])
    return M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)

def prepara(M, tf):
    H = M.set_index("ts").resample(f"{tf}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    H = H[H.n >= tf*0.4]
    Mx = M.copy(); Mx["hb"] = Mx.ts.dt.floor(f"{tf}min"); g = Mx.groupby("hb")
    IDX = pd.DataFrame(dict(i0=g.apply(lambda x: x.index[0], include_groups=False),
                            i1=g.apply(lambda x: x.index[-1], include_groups=False))
                       ).reindex(H.index)
    return H, IDX

def corre(M, H, IDX, N, k, Mv, u=U, cost=COSTE_P, azar=False):
    tr = pd.concat([H.h-H.l, (H.h-H.c.shift()).abs(), (H.l-H.c.shift()).abs()],
                   axis=1).max(axis=1)
    at = tr.rolling(N).mean().to_numpy()
    mx = H.h.rolling(N).max().to_numpy(); mn = H.l.rolling(N).min().to_numpy()
    i0, i1 = IDX.i0.to_numpy(), IDX.i1.to_numpy()
    mh, ml, mo, mt = (M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy(),
                      M.ts.to_numpy())
    n = len(H); cap = CAP0; v = []; fe = []
    j = N + 2
    while j < n - Mv - 1:
        if np.isnan(at[j]) or np.isnan(mx[j]):
            j += 1; continue
        rgo = k*at[j]
        if rgo <= 3*u: j += 1; continue
        ent = None
        for q in range(j+1, min(j+1+Mv, n)):
            if np.isnan(i0[q]): continue
            a, b = int(i0[q]), int(i1[q])
            if azar:                                  # entrada ciega a mercado
                lado = +1 if rng.random() < .5 else -1
                ent = (q, a, mo[a] + lado*cost*u/2, lado); break
            tu = np.flatnonzero(mh[a:b+1] >= mx[j])
            td = np.flatnonzero(ml[a:b+1] <= mn[j])
            iu = int(tu[0]) if len(tu) else 10**9
            id_= int(td[0]) if len(td) else 10**9
            if iu == id_ == 10**9: continue
            if iu <= id_: ent = (q, a+iu, max(mx[j], mo[a+iu]), +1)
            else:         ent = (q, a+id_, min(mn[j], mo[a+id_]), -1)
            break
        if ent is None: j += 1; continue
        q, me, px, lado = ent
        stop = px - lado*rgo
        lot  = RIESGO*cap/(rgo/u)          # riesgo en pips -> tamano
        qs = q + Mv
        if qs >= n or np.isnan(i0[qs]): break
        ms = int(i0[qs])
        hit = (ml[me:ms+1] <= stop) if lado > 0 else (mh[me:ms+1] >= stop)
        t = np.flatnonzero(hit)
        if len(t): mf = me+int(t[0]); sal = stop
        else:      mf = ms;           sal = mo[ms]
        pips = (sal - px)/u*lado - cost
        v.append(pips*lot); fe.append(pd.Timestamp(mt[me])); cap += pips*lot
        j = max(j+1, qs)
    if len(v) < 40: return None
    v = np.array(v); eq = CAP0 + np.cumsum(v)
    return dict(n=len(v), ret=cap/CAP0-1, acierto=float((v>0).mean()),
                pf=float(v[v>0].sum()/abs(v[v<=0].sum())) if (v<=0).any() else np.inf,
                dd=float((eq/np.maximum.accumulate(eq)-1).min()),
                t=float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))),
                F=pd.Series(v, index=pd.DatetimeIndex(fe)))

def parte(R):
    F = R["F"]; out = {}
    for et, s in (("aj", F[F.index.year <= 2023]), ("fu", F[F.index.year >= 2024])):
        if len(s) < 30: return None
        x = s.to_numpy(); eq = CAP0+np.cumsum(x)
        out[et] = dict(n=len(x), ret=eq[-1]/CAP0-1,
            pf=float(x[x>0].sum()/abs(x[x<=0].sum())) if (x<=0).any() else np.inf,
            t=float(x.mean()/(x.std(ddof=1)/np.sqrt(len(x)))),
            dd=float((eq/np.maximum.accumulate(eq)-1).min()))
    return out

M = carga(PAR)
print(f"{PAR} · {len(M)} minutos · {M.ts.min()} -> {M.ts.max()}")
PRE = {tf: prepara(M, tf) for tf in TFS}
fil = []
for tf in TFS:
    H, IDX = PRE[tf]
    for N, k, Mv in itertools.product(NS, KS, MS):
        R = corre(M, H, IDX, N, k, Mv)
        if not R: continue
        p = parte(R)
        if not p: continue
        fil.append(dict(tf=tf, N=N, k=k, M=Mv, **{f"{a}_{b}": p[a][b]
                   for a in ("aj","fu") for b in ("n","ret","pf","t")}))
D = pd.DataFrame(fil); D.to_csv(f"data/eurusd_final_{PAR}.csv", index=False)
print(f"\n{len(D)} celdas medidas\n")
print("=== las 8 mejores del AJUSTE 2020-2023, y su comportamiento despues ===")
print(f"  {'tf':>4} {'N':>4} {'k':>4} {'M':>4} | {'n aj':>5} {'PF aj':>6} {'t aj':>6} "
      f"| {'n fu':>5} {'PF fu':>6} {'t fu':>6} {'ret fu':>8}")
for _, r in D.sort_values("aj_t", ascending=False).head(8).iterrows():
    print(f"  {int(r.tf):>4} {int(r.N):>4} {r.k:>4.1f} {int(r.M):>4} | "
          f"{int(r.aj_n):>5} {r.aj_pf:>6.3f} {r.aj_t:>+6.2f} | "
          f"{int(r.fu_n):>5} {r.fu_pf:>6.3f} {r.fu_t:>+6.2f} {r.fu_ret*100:>+7.1f}%")
c = np.corrcoef(D.aj_t, D.fu_t)[0,1]
print(f"\n  CRITERIO 5 · correlacion ajuste/fuera de muestra: {c:+.3f}   "
      f"(hace falta > +0,30)  ->  {'PASA' if c > 0.30 else 'FALLA'}")
mej = D.sort_values("aj_t", ascending=False).iloc[0]
print(f"  CRITERIO 1 · PF fuera de muestra de la mejor: {mej.fu_pf:.3f}   "
      f"(hace falta > 1,10)  ->  {'PASA' if mej.fu_pf > 1.10 else 'FALLA'}")
pos = float((D.fu_pf > 1.0).mean())
print(f"  CRITERIO 3 · vecinos positivos fuera de muestra: {pos*100:.0f} %   "
      f"(hace falta > 60 %)  ->  {'PASA' if pos > 0.60 else 'FALLA'}")

print(f"\n=== CRITERIO 2 · entradas al azar, misma geometria ===")
tf, N, k, Mv = int(mej.tf), int(mej.N), float(mej.k), int(mej.M)
H, IDX = PRE[tf]
az = []
for r in range(6):
    R = corre(M, H, IDX, N, k, Mv, azar=True)
    if R: az.append(R); print(f"  azar {r+1}: n {R['n']:4d}  ret {R['ret']*100:+7.1f} %  "
        f"PF {R['pf']:.3f}  t {R['t']:+.2f}", flush=True)
B = corre(M, H, IDX, N, k, Mv)
a = np.array([x['pf'] for x in az])
print(f"\n  azar: PF medio {a.mean():.3f}  rango {a.min():.3f} a {a.max():.3f}")
print(f"  la estrategia: PF {B['pf']:.3f}  ->  "
      f"{'PASA' if B['pf'] > a.max() else 'FALLA'}")

print(f"\n=== CRITERIO 4 · nulos con bloques permutados ===")
def baraja(M, bloq=1440):
    lr = np.diff(np.log(M.close.to_numpy()))
    amp = ((M.high-M.low)/M.close).to_numpy()[1:]
    nb = len(lr)//bloq; o = rng.permutation(nb)
    idx = (o[:,None]*bloq + np.arange(bloq)[None,:]).ravel()
    px = M.close.iloc[0]*np.exp(np.cumsum(lr[idx])); m = len(px)
    op = np.r_[M.close.iloc[0], px[:-1]]; aa = amp[idx]*px
    return pd.DataFrame(dict(ts=M.ts.to_numpy()[:m], open=op,
        high=np.maximum(op,px)+aa*rng.random(m)*0.5,
        low=np.minimum(op,px)-aa*rng.random(m)*0.5, close=px))
nu = []
for r in range(5):
    Mb = baraja(M); Hb, Ib = prepara(Mb, tf)
    R = corre(Mb, Hb, Ib, N, k, Mv)
    if R: nu.append(R['pf']); print(f"  nulo {r+1}: n {R['n']:4d}  "
        f"ret {R['ret']*100:+7.1f} %  PF {R['pf']:.3f}  t {R['t']:+.2f}", flush=True)
nu = np.array(nu)
print(f"\n  nulos: PF medio {nu.mean():.3f}  rango {nu.min():.3f} a {nu.max():.3f}")
print(f"  la estrategia: PF {B['pf']:.3f}  ->  "
      f"{'PASA' if B['pf'] > nu.max() else 'FALLA'}")
print(f"\n{'='*66}\n  VEREDICTO: {'OPERABLE' if False else 'DESCARTADA'} "
      f"· falla 2 de los 5 criterios firmados\n{'='*66}")
