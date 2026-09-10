"""EMA+Fibo separando COMPRAS de VENTAS.

El control positivo revelo que la rejilla agregada no puede ver una ventaja
direccional: sube las compras y hunde las ventas por igual y se cancelan. Aqui
cada celda se parte en tres: todo, solo compras, solo ventas.

Eso triplica las celdas (675), asi que el nulo se corre tambien por lado.

  NULOS=5 python3 bt/ema_fibo_lado.py
"""
import os, itertools, numpy as np, pandas as pd
exec(open("bt/ema_fibo.py").read().split("def evalua(")[0])
NULOS = int(os.environ.get("NULOS", 5))

def evalua_l(S, HL, fib, rr):
    h, l = HL; n = len(h); out = []
    for i, lado, A, Bp in S:
        rec = abs(Bp-A)
        if rec < 5*U: continue
        ent = Bp - lado*rec*fib; stop = A; rgo = abs(ent-stop)
        if rgo < 3*U: continue
        tp = ent + lado*rgo*rr
        j0, j1 = i+1, min(i+1+VIDA, n)
        if j1 <= j0: continue
        hh, ll = h[j0:j1], l[j0:j1]
        e = np.flatnonzero(ll <= ent) if lado > 0 else np.flatnonzero(hh >= ent)
        if not len(e): continue
        k = e[0]
        st = (ll[k:] <= stop)   if lado > 0 else (hh[k:] >= stop)
        ob = (hh[k+1:] >= tp)   if lado > 0 else (ll[k+1:] <= tp)
        b = np.flatnonzero(st); a = np.flatnonzero(ob)
        ia = a[0]+1 if len(a) else 10**9
        ib = b[0]   if len(b) else 10**9
        if ia == ib == 10**9: continue
        out.append(((rr if ia < ib else -1.0) - COSTE*U/rgo, lado))
    return np.array(out) if out else np.zeros((0,2))

def z(v):
    return float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v) > 2 else np.nan

def rejilla_l(base, etiq):
    out = []
    for tf in TFS:
        E = agrega(base, tf)
        for per in EMAS:
            S, HL = senales(E, per)
            for fib, rr in itertools.product(FIBS, RRS):
                X = evalua_l(S, HL, fib, rr)
                if len(X) < 60: continue
                for nom, m in (("todo", np.ones(len(X), bool)),
                               ("compras", X[:,1] > 0), ("ventas", X[:,1] < 0)):
                    v = X[m, 0]
                    if len(v) < 60: continue
                    out.append(dict(tf=tf, ema=per, fib=fib, rr=rr, lado=nom,
                                    n=len(v), R=float(v.mean()), z=z(v)))
    D = pd.DataFrame(out); D["fuente"] = etiq
    return D

print("\n=== CONTROL POSITIVO, ahora por lado ===")
def inyecta(base, pips, frac):
    x = base.copy(); dia = x.ts.dt.date.to_numpy()
    ini = np.flatnonzero(np.r_[True, dia[1:] != dia[:-1]])
    favor = rng.random(len(ini)) < frac
    aj = np.zeros(len(x)); ac = 0.0
    for k, i in enumerate(ini):
        j = ini[k+1] if k+1 < len(ini) else len(x)
        paso = (pips*U)/(j-i) * (1 if favor[k] else -1)
        aj[i:j] = ac + np.cumsum(np.full(j-i, paso)); ac = aj[j-1]
    for c in ("open","high","low","close"): x[c] = x[c].to_numpy() + aj
    return x
for pips in (0.0, 1.0, 3.0):
    D = rejilla_l(d if pips == 0 else inyecta(d, pips, 0.6), f"p{pips}")
    C = D[D.lado == "compras"]
    print(f"  deriva {pips:4.1f} pips  ->  COMPRAS: mejor z {C.z.max():+6.2f}  "
          f"celdas z>2 {int((C.z>2).sum()):3d}/{len(C)}  R de la mejor "
          f"{C.sort_values('z').iloc[-1].R:+.4f}", flush=True)

REAL = rejilla_l(d, "real"); REAL.to_csv("data/ema_fibo_lado.csv", index=False)
print(f"\n=== REJILLA REAL POR LADO · {len(REAL)} celdas ===")
for nom in ("todo", "compras", "ventas"):
    S_ = REAL[REAL.lado == nom]
    print(f"  {nom:8s} mejor z {S_.z.max():+6.2f}   celdas z>2 "
          f"{int((S_.z>2).sum()):3d}/{len(S_)}   R de la mejor "
          f"{S_.sort_values('z').iloc[-1].R:+.4f}")
print(f"\n  las 6 mejores de todas:")
for _, r in REAL.sort_values("z", ascending=False).head(6).iterrows():
    print(f"    tf {int(r.tf):3d} ema {int(r.ema):3d} fib {r.fib:.3f} rr {r.rr:.0f} "
          f"{r.lado:8s} n {int(r.n):6d}  R {r.R:+.4f}  z {r.z:+6.2f}")

print(f"\n=== {NULOS} NULOS POR LADO ===")
mx = []
for k in range(NULOS):
    N = rejilla_l(sintetico(d), f"nulo{k}")
    mx.append(N.z.max())
    print(f"  nulo {k+1}: mejor z {N.z.max():+6.2f}  celdas z>2 "
          f"{int((N.z>2).sum()):3d}/{len(N)}", flush=True)
mx = np.array(mx)
print(f"\n  mejor z de un nulo: media {mx.mean():+.2f}  rango {mx.min():+.2f} a {mx.max():+.2f}")
print(f"  mejor z real: {REAL.z.max():+.2f}   ->   percentil "
      f"{float((mx < REAL.z.max()).mean())*100:.0f} % de los nulos")
