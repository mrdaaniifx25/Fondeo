"""La celda fijada, en instrumentos que no se han usado para elegirla.

El corte temporal dejo el asunto abierto: la familia fibo 0,705-0,786 con
sobreventa es floja en 2020-2023 (+0,05) y fuerte en 2024-2026 (+0,47). Eso
no es sobreajuste -no se puede ajustar a lo que no miraste- pero tampoco es
prueba: podria ser un tramo con suerte.

Los PARAMETROS YA ESTAN FIJADOS. Aqui se aplican tal cual a GBPUSD y USDJPY,
que no han intervenido en ninguna eleccion, y se parte por anos.

Si la familia aguanta en tres instrumentos y en los dos tramos, es real.
Si solo vive en EURUSD 2024-2026, es un tramo con suerte.

  python3 bt/ema_fibo_esto_instrumentos.py
"""
import itertools, numpy as np, pandas as pd

_a = open("bt/ema_fibo.py").read()
exec(_a[:_a.index('REAL = rejilla(d, "real")')])
_b = open("bt/ema_fibo_estocastico.py").read()
exec(_b[_b.index("def estocastico"):_b.index("def evalua_f")])

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50)}
CELDAS = [(240, e, f, r) for e in (10, 20) for f in (0.705, 0.786) for r in (1.0, 2.0, 3.0)]


def corre(par):
    ruta, U_, C_ = INSTR[par]
    x = pd.read_parquet(ruta); x["ts"] = pd.to_datetime(x["ts"])
    x = x.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    E = agrega(x, 240); TS = E.ts.to_numpy()
    K, Dl = estocastico(E)
    h, l = E.h.to_numpy(), E.l.to_numpy(); n = len(h)
    filas = []
    for tf, per, fib, rr in CELDAS:
        S, _ = senales(E, per)
        for i, lado, A, B in S:
            rec = abs(B-A)
            if rec < 5*U_: continue
            ent, stop = B - lado*rec*fib, A
            rgo = abs(ent-stop)
            if rgo < 3*U_: continue
            tp = ent + lado*rgo*rr
            j0, j1 = i+1, min(i+1+VIDA, n)
            if j1 <= j0: continue
            hh, ll = h[j0:j1], l[j0:j1]
            e = np.flatnonzero(ll <= ent) if lado > 0 else np.flatnonzero(hh >= ent)
            if not len(e): continue
            k = e[0]; q = j0+k-1
            if q < 0 or not np.isfinite(K[q]): continue
            if not ((K[q] <= 20) if lado > 0 else (K[q] >= 80)): continue
            st = (ll[k:] <= stop) if lado > 0 else (hh[k:] >= stop)
            ob = (hh[k+1:] >= tp) if lado > 0 else (ll[k+1:] <= tp)
            b = np.flatnonzero(st); a = np.flatnonzero(ob)
            ia = a[0]+1 if len(a) else 10**9
            ib = b[0]   if len(b) else 10**9
            if ia == ib == 10**9: continue
            filas.append((par, per, fib, rr, TS[j0+k], lado,
                          (rr if ia < ib else -1.0) - C_*U_/rgo))
    return pd.DataFrame(filas, columns=["par","ema","fib","rr","ts","lado","R"])


if __name__ == "__main__":
    T = pd.concat([corre(p) for p in INSTR], ignore_index=True)
    T.to_csv("data/ema_fibo_esto_instrumentos.csv", index=False)
    T["ano"] = pd.to_datetime(T.ts).dt.year
    T["fuera"] = T.ts >= np.datetime64("2024-01-01")
    z = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v) > 5 else np.nan

    print(f"=== LA FAMILIA FIJADA (H4 · EMA 10/20 · fibo 0,705-0,786 · sobreventa) ===")
    print(f"    12 celdas, parametros CONGELADOS, aplicados a tres instrumentos\n")
    print(f"  {'':>8} | {'n':>5} {'2020-2023':>10} {'z':>6} | {'n':>5} "
          f"{'2024-2026':>10} {'z':>6} | {'TODO':>9} {'z':>6}")
    for par, g in T.groupby("par"):
        a, b = g[~g.fuera], g[g.fuera]
        print(f"  {par:>8} | {len(a):>5} {a.R.mean():>+10.4f} {z(a.R):>+6.2f} | "
              f"{len(b):>5} {b.R.mean():>+10.4f} {z(b.R):>+6.2f} | "
              f"{g.R.mean():>+9.4f} {z(g.R):>+6.2f}")
    a, b = T[~T.fuera], T[T.fuera]
    print(f"  {'LOS TRES':>8} | {len(a):>5} {a.R.mean():>+10.4f} {z(a.R):>+6.2f} | "
          f"{len(b):>5} {b.R.mean():>+10.4f} {z(b.R):>+6.2f} | "
          f"{T.R.mean():>+9.4f} {z(T.R):>+6.2f}")

    print(f"\n  por ano, los tres instrumentos juntos\n")
    print(f"    {'ano':>6} {'n':>6} {'R neta':>9} {'z':>7}")
    for k, g in T.groupby("ano"):
        print(f"    {k:>6} {len(g):>6} {g.R.mean():>+9.4f} {z(g.R):>+7.2f}")

    print(f"\n  las 12 celdas en los DOS instrumentos nuevos (GBPUSD + USDJPY)\n")
    N = T[T.par != "EURUSD"]
    print(f"    {'ema':>4} {'fib':>6} {'rr':>4} {'n':>6} {'R neta':>9} {'z':>7}")
    for k, g in N.groupby(["ema","fib","rr"]):
        print(f"    {k[0]:>4} {k[1]:>6.3f} {k[2]:>4.1f} {len(g):>6} "
              f"{g.R.mean():>+9.4f} {z(g.R):>+7.2f}")
