"""¿Funciona en algun par? ¿Y si el oscilador de la captura era un RSI?

Dos preguntas del usuario, una sola medicion. Se corre la misma rejilla con
CUATRO filtros -ninguno, estocastico, RSI 30/70 y RSI 40/60- sobre los TRES
instrumentos, y el z se agrupa por ano desde el principio.

Esa ultima parte es la leccion de RESULTADOS_ema_fibo_estocastico.md: el z
que trata cada operacion como independiente daba +3,18 donde el agrupado por
ano daba +0,41. Aqui no se repite el error.

Criterio declarado antes de mirar: para que algo cuente tiene que dar z
agrupado > 2 en un par Y no ser negativo en los otros dos. Un efecto que
cambia de signo entre pares no es un efecto.

  python3 bt/ema_fibo_osciladores.py
"""
import itertools, numpy as np, pandas as pd

_a = open("bt/ema_fibo.py").read()
exec(_a[:_a.index('REAL = rejilla(d, "real")')])

import os
# Los tres de siempre, mas CUATRO que no han intervenido en ninguna eleccion.
# El oro sale de los ficheros que subio el usuario, 2020-2026 completo.
INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50)}
NUEVOS = {"NAS100": (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
          "SPX500": (["data/spxusd_m1.parquet"], 1e-0, 0.60),
          "GER40":  (["data/grxeur_m1.parquet", "data/grxeur_m1_2026.parquet"], 1e-0, 1.00),
          "XAUUSD": (["data/xauusd_m1_2020_2022.parquet", "data/xauusd_m1.parquet",
                      "data/xauusd_m1_2026.parquet"], 1e-0, 0.30)}
if os.environ.get("NUEVOS"):
    INSTR = {k: (v[0], v[1], v[2]) for k, v in NUEVOS.items()}
TF, EMAS_, FIBS_, RRS_ = 240, (10, 20, 50), (0.382, 0.5, 0.618, 0.705, 0.786), (1.0, 2.0, 3.0)


def estocastico(E, kp=14, sm=3):
    h, l, c = E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy()
    hh = pd.Series(h).rolling(kp).max().to_numpy()
    ll = pd.Series(l).rolling(kp).min().to_numpy()
    r = hh - ll
    K = 100.0*(c - ll)/np.where(r == 0, np.nan, r)
    return pd.Series(K).rolling(sm).mean().to_numpy()


def rsi(E, per=14):
    c = E.c.to_numpy(); d_ = np.diff(c, prepend=c[0])
    g = pd.Series(np.where(d_ > 0, d_, 0.0)).ewm(alpha=1/per, adjust=False).mean()
    p = pd.Series(np.where(d_ < 0, -d_, 0.0)).ewm(alpha=1/per, adjust=False).mean()
    rs = g/p.replace(0, np.nan)
    return (100 - 100/(1+rs)).to_numpy()


FILTROS = {
    "sin filtro": lambda K, R, lado: True,
    "estocastico <=20/>=80": lambda K, R, lado: (K <= 20) if lado > 0 else (K >= 80),
    "RSI <=30/>=70": lambda K, R, lado: (R <= 30) if lado > 0 else (R >= 70),
    "RSI <=40/>=60": lambda K, R, lado: (R <= 40) if lado > 0 else (R >= 60),
}


def corre(par):
    ruta, U_, C_ = INSTR[par]
    if isinstance(ruta, str): ruta = [ruta]
    x = pd.concat([pd.read_parquet(f) for f in ruta], ignore_index=True)
    x["ts"] = pd.to_datetime(x["ts"])
    x = x.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    E = agrega(x, TF); TS = E.ts.to_numpy()
    K, Rv = estocastico(E), rsi(E)
    h, l = E.h.to_numpy(), E.l.to_numpy(); n = len(h)
    filas = []
    for per in EMAS_:
        S, _ = senales(E, per)
        for i, lado, A, B in S:
            rec = abs(B-A)
            if rec < 5*U_: continue
            for fib in FIBS_:
                ent, stop = B - lado*rec*fib, A
                rgo = abs(ent-stop)
                if rgo < 3*U_: continue
                j0, j1 = i+1, min(i+1+VIDA, n)
                if j1 <= j0: continue
                hh, ll = h[j0:j1], l[j0:j1]
                e = np.flatnonzero(ll <= ent) if lado > 0 else np.flatnonzero(hh >= ent)
                if not len(e): continue
                k = e[0]; q = j0+k-1
                if q < 0 or not np.isfinite(K[q]) or not np.isfinite(Rv[q]): continue
                st = (ll[k:] <= stop) if lado > 0 else (hh[k:] >= stop)
                b = np.flatnonzero(st); ib = b[0] if len(b) else 10**9
                for rr in RRS_:
                    tp = ent + lado*rgo*rr
                    ob = (hh[k+1:] >= tp) if lado > 0 else (ll[k+1:] <= tp)
                    a = np.flatnonzero(ob); ia = a[0]+1 if len(a) else 10**9
                    if ia == ib == 10**9: continue
                    R = (rr if ia < ib else -1.0) - C_*U_/rgo
                    for nom, f in FILTROS.items():
                        if f(K[q], Rv[q], lado):
                            filas.append((par, per, fib, rr, nom, TS[j0+k], R))
    return pd.DataFrame(filas, columns=["par","ema","fib","rr","filtro","ts","R"])


def zano(g):
    """z con error estandar agrupado por ano: el numero honesto."""
    if len(g) < 30: return np.nan
    m = g.R.mean()
    r = (g.R - m).groupby(pd.to_datetime(g.ts).dt.year).sum()
    se = np.sqrt((r**2).sum())/len(g)
    return float(m/se) if se > 0 else np.nan


if __name__ == "__main__":
    T = pd.concat([corre(p) for p in INSTR], ignore_index=True)
    T.to_csv("data/ema_fibo_osciladores%s.csv" % os.environ.get("SUF",""), index=False)
    print(f"\n=== EMA + FIBO + OSCILADOR · H4 · {len(T)} operaciones · 3 pares ===")
    print("    z SIEMPRE agrupado por ano\n")
    print(f"  {'filtro':>22} | " + " | ".join(f"{p:>18}" for p in INSTR) + " |    LOS TRES")
    print(f"  {'':>22} | " + " | ".join(f"{'n':>6}{'R':>7}{'z':>6}" for p in INSTR)
          + " |   R      z")
    for nom in FILTROS:
        g = T[T.filtro == nom]
        fila = f"  {nom:>22} | "
        for p in INSTR:
            x = g[g.par == p]
            fila += f"{len(x):>6}{x.R.mean():>+7.3f}{zano(x):>+6.2f} | "
        fila += f"{g.R.mean():>+6.3f} {zano(g):>+6.2f}"
        print(fila)

    print(f"\n  la MEJOR celda de cada par y cada filtro (z agrupado por ano)\n")
    print(f"  {'par':>7} {'filtro':>22} {'ema':>4} {'fib':>6} {'rr':>4} {'n':>6} "
          f"{'R neta':>8} {'z':>7} | {'en los otros dos pares':>24}")
    for p in INSTR:
        for nom in FILTROS:
            g = T[(T.par == p) & (T.filtro == nom)]
            best, k_ = None, None
            for k, x in g.groupby(["ema","fib","rr"]):
                z_ = zano(x)
                if np.isfinite(z_) and (best is None or z_ > best): best, k_ = z_, k
            if k_ is None: continue
            o = T[(T.par != p) & (T.filtro == nom) & (T.ema == k_[0]) &
                  (T.fib == k_[1]) & (T.rr == k_[2])]
            det = " · ".join(f"{q}: {zano(o[o.par==q]):+.2f}" for q in INSTR if q != p)
            x = g[(g.ema==k_[0]) & (g.fib==k_[1]) & (g.rr==k_[2])]
            print(f"  {p:>7} {nom:>22} {k_[0]:>4} {k_[1]:>6.3f} {k_[2]:>4.1f} {len(x):>6} "
                  f"{x.R.mean():>+8.4f} {best:>+7.2f} | {det:>24}")
