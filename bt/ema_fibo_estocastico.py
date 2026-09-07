"""EMA + Fibonacci + ESTOCASTICO en EURUSD.

Sale de una captura de Instagram: un "trade destacado" con retroceso de
Fibonacci, media movil y un oscilador en el subpanel. La pregunta del usuario:
"parece estocastico, EMA y Fibo, no?".

EMA+Fibo ya esta medido en RESULTADOS_ema_fibo.md: 225 celdas, ninguna con
z > 2, y por debajo del percentil 20 de datos barajados. Aqui se le anade el
estocastico (14,3,3) encima, leido en la ultima vela CERRADA antes de que se
llene la orden limitada -que es lo que ve alguien operando.

  sin filtro   la rejilla de siempre
  K<=20/>=80   sobreventa / sobrecompra clasica
  K<=30/>=70   version mas permisiva
  cruce K>D    el oscilador girando a favor

900 celdas. Con tantas, lo que decide no es la mejor: es si la mejor se
distingue de la mejor de unos datos SIN NINGUNA VENTAJA. Por eso van los nulos.

  NULOS=5 python3 bt/ema_fibo_estocastico.py
"""
import os, itertools, numpy as np, pandas as pd

_src = open("bt/ema_fibo.py").read()
exec(_src[:_src.index('REAL = rejilla(d, "real")')])


def estocastico(E, kp=14, sm=3, dp=3):
    h, l, c = E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy()
    hh = pd.Series(h).rolling(kp).max().to_numpy()
    ll = pd.Series(l).rolling(kp).min().to_numpy()
    rng_ = hh - ll
    K = 100.0*(c - ll)/np.where(rng_ == 0, np.nan, rng_)
    K = pd.Series(K).rolling(sm).mean().to_numpy()      # %K lento
    Dl = pd.Series(K).rolling(dp).mean().to_numpy()
    return K, Dl


FILTROS = {
    "sin filtro":  None,
    "K<=20/>=80":  lambda K, Dp, lado: (K <= 20) if lado > 0 else (K >= 80),
    "K<=30/>=70":  lambda K, Dp, lado: (K <= 30) if lado > 0 else (K >= 70),
    "cruce K>D":   lambda K, Dp, lado: (K > Dp) if lado > 0 else (K < Dp),
}


def evalua_f(S, HL, fib, rr, K, Dl, filtro):
    """Igual que evalua(), pero mirando el oscilador al llenarse la orden.

    El estocastico se lee en la vela ANTERIOR a la del llenado, que es la
    ultima cerrada: leerlo en la del llenado seria mirar dentro de la vela.
    """
    h, l = HL; n = len(h); R = []
    for i, lado, A, B in S:
        rec = abs(B-A)
        if rec < 5*U: continue
        ent, stop = B - lado*rec*fib, A
        rgo = abs(ent-stop)
        if rgo < 3*U: continue
        tp = ent + lado*rgo*rr
        j0, j1 = i+1, min(i+1+VIDA, n)
        if j1 <= j0: continue
        hh, ll = h[j0:j1], l[j0:j1]
        e = np.flatnonzero(ll <= ent) if lado > 0 else np.flatnonzero(hh >= ent)
        if not len(e): continue
        k = e[0]
        if filtro is not None:
            q = j0 + k - 1                       # ultima vela CERRADA
            if q < 0 or not np.isfinite(K[q]) or not np.isfinite(Dl[q]): continue
            if not filtro(K[q], Dl[q], lado): continue
        st = (ll[k:] <= stop) if lado > 0 else (hh[k:] >= stop)
        ob = (hh[k+1:] >= tp) if lado > 0 else (ll[k+1:] <= tp)
        b = np.flatnonzero(st); a = np.flatnonzero(ob)
        ia = a[0]+1 if len(a) else 10**9
        ib = b[0]   if len(b) else 10**9
        if ia == ib == 10**9: continue
        R.append((rr if ia < ib else -1.0) - COSTE*U/rgo)
    return np.array(R)


def rejilla_f(base, etiq):
    out = []
    for tf in TFS:
        E = agrega(base, tf)
        K, Dl = estocastico(E)
        for per in EMAS:
            S, HL = senales(E, per)
            for fib, rr in itertools.product(FIBS, RRS):
                for nom, f in FILTROS.items():
                    R = evalua_f(S, HL, fib, rr, K, Dl, f)
                    if len(R) < 60: continue
                    z = R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))
                    out.append(dict(tf=tf, ema=per, fib=fib, rr=rr, filtro=nom,
                                    n=len(R), R=float(R.mean()), z=float(z)))
    D = pd.DataFrame(out); D["fuente"] = etiq
    return D


if __name__ == "__main__":
    REAL = rejilla_f(d, "real")
    REAL.to_csv("data/ema_fibo_estocastico.csv", index=False)
    print(f"\n=== EMA + FIBO + ESTOCASTICO · {len(REAL)} celdas reales ===\n")
    print(f"  {'filtro':>12} {'celdas':>7} {'n medio':>8} {'R neta media':>13} "
          f"{'mejor z':>8} {'z>2':>5}")
    for nom, g in REAL.groupby("filtro"):
        print(f"  {nom:>12} {len(g):>7} {g.n.mean():>8.0f} {g.R.mean():>+13.4f} "
              f"{g.z.max():>+8.2f} {int((g.z>2).sum()):>5}")
    print(f"\n  las 8 mejores de las {len(REAL)}:\n")
    print(f"  {'tf':>4} {'ema':>4} {'fib':>6} {'rr':>4} {'filtro':>12} {'n':>6} "
          f"{'R neta':>9} {'z':>7}")
    for _, r in REAL.sort_values("z", ascending=False).head(8).iterrows():
        print(f"  {int(r.tf):4d} {int(r.ema):4d} {r.fib:6.3f} {r.rr:4.1f} "
              f"{r.filtro:>12} {int(r.n):6d} {r.R:+9.4f} {r.z:+7.2f}")

    print(f"\n=== {NULOS} REJILLAS SOBRE DATOS SIN NINGUNA VENTAJA ===\n")
    mx = []
    for k in range(NULOS):
        N = rejilla_f(sintetico(d), f"nulo{k}")
        mx.append(N.z.max())
        print(f"  nulo {k+1}: {len(N)} celdas · mejor z {N.z.max():+.2f} · "
              f"celdas con z>2: {int((N.z>2).sum())}", flush=True)
    mx = np.array(mx)
    print(f"\n  mejor z REAL      {REAL.z.max():+.2f}")
    print(f"  mejor z de nulos  {mx.min():+.2f} a {mx.max():+.2f}  (media {mx.mean():+.2f})")
    print(f"  la real supera a {int((REAL.z.max() > mx).sum())} de {NULOS} nulos")
