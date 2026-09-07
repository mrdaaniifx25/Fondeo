"""Auditoria de la celda ganadora: ¿hace algo el estocastico, o vale cualquier
subconjunto del mismo tamano?

La celda es H4 · EMA 20 · fibo 0,786 · R:R 2 con sobreventa. El filtro solo
QUITA operaciones del conjunto sin filtrar, asi que la pregunta se contesta
sola: se comparan las 779 que elige el estocastico contra 4.000 subconjuntos
AL AZAR del mismo tamano sacados de las mismas operaciones.

Si el estocastico no informa, caera en medio de esa nube.

Y una segunda prueba: leer el estocastico N velas ANTES del llenado. Si la
ventaja solo aparece pegada a la vela de entrada y se evapora al alejarse una
o dos velas, huele a fuga; si decae despacio, es contexto de verdad.

  python3 bt/ema_fibo_esto_auditoria.py
"""
import numpy as np, pandas as pd

_a = open("bt/ema_fibo.py").read()
exec(_a[:_a.index('REAL = rejilla(d, "real")')])
_b = open("bt/ema_fibo_estocastico.py").read()
exec(_b[_b.index("def estocastico"):_b.index("def evalua_f")])

TF, EMA, FIB, RR, DESF = 240, 20, 0.786, 2.0, (0, 1, 2, 3, 5, 10)


def ops(desf):
    """Todas las operaciones de la celda, con el %K leido `desf`+1 velas antes."""
    E = agrega(d, TF); K, Dl = estocastico(E)
    S, HL = senales(E, EMA)
    h, l = HL; n = len(h); out = []
    for i, lado, A, B in S:
        rec = abs(B-A)
        if rec < 5*U: continue
        ent, stop = B - lado*rec*FIB, A
        rgo = abs(ent-stop)
        if rgo < 3*U: continue
        tp = ent + lado*rgo*RR
        j0, j1 = i+1, min(i+1+VIDA, n)
        if j1 <= j0: continue
        hh, ll = h[j0:j1], l[j0:j1]
        e = np.flatnonzero(ll <= ent) if lado > 0 else np.flatnonzero(hh >= ent)
        if not len(e): continue
        k = e[0]; q = j0 + k - 1 - desf
        if q < 0 or not np.isfinite(K[q]): continue
        st = (ll[k:] <= stop) if lado > 0 else (hh[k:] >= stop)
        ob = (hh[k+1:] >= tp) if lado > 0 else (ll[k+1:] <= tp)
        b = np.flatnonzero(st); a = np.flatnonzero(ob)
        ia = a[0]+1 if len(a) else 10**9
        ib = b[0]   if len(b) else 10**9
        if ia == ib == 10**9: continue
        R = (RR if ia < ib else -1.0) - COSTE*U/rgo
        pasa = (K[q] <= 20) if lado > 0 else (K[q] >= 80)
        out.append((R, bool(pasa), lado))
    return pd.DataFrame(out, columns=["R", "pasa", "lado"])


z = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v) > 5 else np.nan
T = ops(0)
F = T[T.pasa]
print(f"=== AUDITORIA · H4 · EMA {EMA} · fibo {FIB} · R:R {RR} ===\n")
print(f"  todas las operaciones de la celda : {len(T):>5}   R neta {T.R.mean():+.4f}"
      f"   z {z(T.R):+.2f}")
print(f"  las que elige el estocastico      : {len(F):>5}   R neta {F.R.mean():+.4f}"
      f"   z {z(F.R):+.2f}")
print(f"  las que descarta                  : {len(T)-len(F):>5}   "
      f"R neta {T[~T.pasa].R.mean():+.4f}   z {z(T[~T.pasa].R):+.2f}\n")

rg = np.random.default_rng(3)
v = T.R.to_numpy(); m = len(F)
nulo = np.array([v[rg.choice(len(v), m, replace=False)].mean() for _ in range(4000)])
p = float((nulo >= F.R.mean()).mean())
print(f"  4.000 subconjuntos AL AZAR de {m} operaciones de esas mismas:")
print(f"    media {nulo.mean():+.4f}   desviacion {nulo.std():.4f}")
print(f"    el estocastico esta a {(F.R.mean()-nulo.mean())/nulo.std():+.2f} desviaciones")
print(f"    p = {p:.4f}   (fraccion de subconjuntos al azar que igualan o superan)\n")

print("  ¿y si se lee el estocastico mas atras en el tiempo?\n")
print(f"    {'velas antes':>12} {'n':>6} {'R neta':>9} {'z':>7}")
for k in DESF:
    G = ops(k); g = G[G.pasa]
    print(f"    {k+1:>12} {len(g):>6} {g.R.mean():>+9.4f} {z(g.R):>+7.2f}")

print(f"\n  por lado (con el desfase normal):")
for s, et in ((1, "compras"), (-1, "ventas")):
    x = F[F.lado == s]
    if len(x) > 5:
        print(f"    {et:>8} {len(x):>5} ops   R neta {x.R.mean():>+8.4f}   z {z(x.R):>+6.2f}")
