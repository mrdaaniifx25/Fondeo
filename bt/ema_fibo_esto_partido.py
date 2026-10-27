"""EMA + Fibo + estocastico, partido en el tiempo.

La rejilla completa dio z +4,46 en H4/EMA20/fibo 0,786/RR2 con el filtro de
sobreventa. Eso se eligio MIRANDO TODO 2020-2026, asi que no vale.

Aqui la celda se elige con 2020-2023 y se cobra con 2024-2026. Es la prueba
que ha matado todo lo demas de este repositorio.

  python3 bt/ema_fibo_esto_partido.py
"""
import itertools, numpy as np, pandas as pd

_a = open("bt/ema_fibo.py").read()
exec(_a[:_a.index('REAL = rejilla(d, "real")')])
_b = open("bt/ema_fibo_estocastico.py").read()
exec(_b[_b.index("def estocastico"):_b.index("def evalua_f")])

CORTE = np.datetime64("2024-01-01")


def evalua_t(S, HL, TS, fib, rr, K, Dl, filtro):
    """Como evalua_f pero devolviendo tambien CUANDO ocurrio cada operacion."""
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
            q = j0 + k - 1
            if q < 0 or not np.isfinite(K[q]) or not np.isfinite(Dl[q]): continue
            if not filtro(K[q], Dl[q], lado): continue
        st = (ll[k:] <= stop) if lado > 0 else (hh[k:] >= stop)
        ob = (hh[k+1:] >= tp) if lado > 0 else (ll[k+1:] <= tp)
        b = np.flatnonzero(st); a = np.flatnonzero(ob)
        ia = a[0]+1 if len(a) else 10**9
        ib = b[0]   if len(b) else 10**9
        if ia == ib == 10**9: continue
        R.append((TS[j0+k], lado, (rr if ia < ib else -1.0) - COSTE*U/rgo))
    return R


if __name__ == "__main__":
    filas = []
    for tf in TFS:
        E = agrega(d, tf)
        TS = E.ts.to_numpy()
        K, Dl = estocastico(E)
        for per in EMAS:
            S, HL = senales(E, per)
            for fib, rr in itertools.product(FIBS, RRS):
                for nom, f in FILTROS.items():
                    for ts, lado, R in evalua_t(S, HL, TS, fib, rr, K, Dl, f):
                        filas.append((tf, per, fib, rr, nom, ts, lado, R))
    T = pd.DataFrame(filas, columns=["tf","ema","fib","rr","filtro","ts","lado","R"])
    T.to_csv("data/ema_fibo_esto_ops.csv", index=False)
    T["fuera"] = T.ts >= CORTE
    z = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v) > 5 else np.nan

    res = []
    for k, g in T.groupby(["tf","ema","fib","rr","filtro"]):
        a, b = g[~g.fuera], g[g.fuera]
        if len(a) < 60 or len(b) < 40: continue
        res.append((z(a.R), k, len(a), a.R.mean(), len(b), b.R.mean(), z(b.R)))

    print(f"=== EMA+FIBO+ESTOCASTICO PARTIDO EN EL TIEMPO · {len(res)} celdas ===")
    print(f"    elegidas con 2020-2023, cobradas con 2024-2026\n")
    print(f"  {'tf':>4} {'ema':>4} {'fib':>6} {'rr':>4} {'filtro':>12} | "
          f"{'n':>5} {'NETA':>8} {'z':>6} | {'n':>5} {'NETA fuera':>11} {'z':>6}")
    for za, k, na, ma, nb, mb, zb in sorted(res, reverse=True)[:12]:
        print(f"  {k[0]:>4} {k[1]:>4} {k[2]:>6.3f} {k[3]:>4.1f} {k[4]:>12} | "
              f"{na:>5} {ma:>+8.4f} {za:>+6.2f} | {nb:>5} {mb:>+11.4f} {zb:>+6.2f}")

    za, k, na, ma, nb, mb, zb = max(res)
    print(f"\n  LA ELEGIDA SIN MIRAR EL FUTURO: {k[0]} min · EMA {k[1]} · "
          f"fibo {k[2]} · R:R {k[3]} · {k[4]}")
    print(f"    dentro 2020-2023   {na:>5} ops   R neta {ma:+.4f}   z {za:+.2f}")
    print(f"    FUERA  2024-2026   {nb:>5} ops   R neta {mb:+.4f}   z {zb:+.2f}\n")
    G = T[(T.tf==k[0])&(T.ema==k[1])&(T.fib==k[2])&(T.rr==k[3])&(T.filtro==k[4])].copy()
    G["ano"] = pd.to_datetime(G.ts).dt.year
    print(f"    {'ano':>6} {'n':>5} {'compras':>8} {'ventas':>8} {'R NETA':>9} {'z':>7}")
    for a_, x in G.groupby("ano"):
        print(f"    {a_:>6} {len(x):>5} {int((x.lado>0).sum()):>8} "
              f"{int((x.lado<0).sum()):>8} {x.R.mean():>+9.4f} {z(x.R):>+7.2f}")
    print(f"\n    por lado, fuera de muestra:")
    F = G[pd.to_datetime(G.ts) >= pd.Timestamp("2024-01-01")]
    for s, et in ((1,"compras"),(-1,"ventas")):
        x = F[F.lado==s]
        if len(x) > 5:
            print(f"      {et:>8} {len(x):>5} ops   R neta {x.R.mean():>+8.4f}   z {z(x.R):>+6.2f}")
