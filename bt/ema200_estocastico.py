"""Las dos ideas del usuario, sin Fibonacci.

    "EMA de 200 y de 20 solo? y estrategia de estocastico buscando reversiones"

El Fibonacci resulto ser la pieza danina: EMA+Fibo sin oscilador da z -10,29
sobre siete instrumentos. Aqui se quita del todo.

  A  retroceso a la EMA20   el precio toca la EMA20 y cierra de vuelta a favor
  B  cruce EMA20 / EMA200   el cruce clasico
  C  reversion estocastica  %K vuelve a cruzar el 20 (o el 80) desde fuera

Cada una con y sin el filtro de tendencia de la EMA200, que es la otra mitad
de lo que propone.

  stop      mas alla del extremo de las ultimas N velas
  objetivo  multiplo del riesgo
  vencido   a mercado a las 20 velas

162 celdas x 7 instrumentos. CRITERIO DECLARADO ANTES DE MIRAR: para contar,
una celda tiene que dar z agrupado por ano > 2 y ser positiva en al menos 5 de
los 7 instrumentos. Lo demas es ruido con muchas celdas.

  python3 bt/ema200_estocastico.py
"""
import itertools, numpy as np, pandas as pd

INSTR = {"EURUSD": (["data/eurusd_m1.parquet"], 1e-4, 1.43),
         "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
         "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
         "NAS100": (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
         "SPX500": (["data/spxusd_m1.parquet"], 1e-0, 0.60),
         "GER40":  (["data/grxeur_m1.parquet", "data/grxeur_m1_2026.parquet"], 1e-0, 1.00),
         "XAUUSD": (["data/xauusd_m1_2020_2022.parquet", "data/xauusd_m1.parquet",
                     "data/xauusd_m1_2026.parquet"], 1e-0, 0.30)}
TFS_, STOPS, RRS_ = (60, 240, 1440), (5, 10, 20), (1.0, 2.0, 3.0)
HOR = 20


def barras(x, m):
    B = x.set_index("ts").resample(f"{m}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return B[B.n >= max(1, m*0.3)].reset_index()


def indicadores(B):
    c = B.c.to_numpy()
    e20 = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
    e200 = pd.Series(c).ewm(span=200, adjust=False).mean().to_numpy()
    hh = pd.Series(B.h).rolling(14).max().to_numpy()
    ll = pd.Series(B.l).rolling(14).min().to_numpy()
    r = hh - ll
    K = pd.Series(100.0*(c-ll)/np.where(r == 0, np.nan, r)).rolling(3).mean().to_numpy()
    return e20, e200, K


def disparos(B, e20, e200, K, modo):
    """Devuelve (i, lado) de cada senal, decidida al CIERRE de la vela i."""
    o, h, l, c = (B.o.to_numpy(), B.h.to_numpy(), B.l.to_numpy(), B.c.to_numpy())
    n = len(c); S = []
    for i in range(210, n-1):
        if not np.isfinite(e200[i]) or not np.isfinite(K[i]) or not np.isfinite(K[i-1]):
            continue
        if modo == "A":        # el precio toca la EMA20 y cierra de vuelta a favor
            if l[i] <= e20[i] and c[i] > e20[i] and c[i-1] > e20[i-1]: S.append((i, +1))
            elif h[i] >= e20[i] and c[i] < e20[i] and c[i-1] < e20[i-1]: S.append((i, -1))
        elif modo == "B":      # cruce EMA20 / EMA200
            if e20[i] > e200[i] and e20[i-1] <= e200[i-1]: S.append((i, +1))
            elif e20[i] < e200[i] and e20[i-1] >= e200[i-1]: S.append((i, -1))
        else:                  # reversion del estocastico
            if K[i] > 20 and K[i-1] <= 20: S.append((i, +1))
            elif K[i] < 80 and K[i-1] >= 80: S.append((i, -1))
    return S


def corre(par):
    rutas, U, C = INSTR[par]
    x = pd.concat([pd.read_parquet(f) for f in rutas], ignore_index=True)
    x["ts"] = pd.to_datetime(x["ts"])
    x = x.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    filas = []
    for tf in TFS_:
        B = barras(x, tf); e20, e200, K = indicadores(B)
        h, l, c = B.h.to_numpy(), B.l.to_numpy(), B.c.to_numpy()
        TS = B.ts.to_numpy(); n = len(c)
        for modo in ("A", "B", "C"):
            S = disparos(B, e20, e200, K, modo)
            for i, lado in S:
                tend = (c[i] > e200[i]) == (lado > 0)
                ent = c[i]
                for nb in STOPS:
                    a0 = max(0, i-nb+1)
                    stop = l[a0:i+1].min() if lado > 0 else h[a0:i+1].max()
                    rgo = (ent-stop)*lado
                    if rgo < 3*U: continue
                    j0, j1 = i+1, min(i+1+HOR, n)
                    if j1 <= j0+1: continue
                    hh, ll = h[j0:j1], l[j0:j1]
                    b = np.flatnonzero(ll <= stop) if lado > 0 else np.flatnonzero(hh >= stop)
                    ib = b[0] if len(b) else 10**9
                    for rr in RRS_:
                        tp = ent + lado*rgo*rr
                        a = np.flatnonzero(hh >= tp) if lado > 0 else np.flatnonzero(ll <= tp)
                        ia = a[0] if len(a) else 10**9
                        R = ((c[j1-1]-ent)*lado/rgo if ia == ib == 10**9
                             else (rr if ia < ib else -1.0))
                        for ft in (False, True):
                            if ft and not tend: continue
                            filas.append((par, tf, modo, nb, rr, ft, TS[i],
                                          R - C*U/rgo))
    return pd.DataFrame(filas, columns=["par","tf","modo","stop","rr","tend","ts","R"])


def zano(g):
    if len(g) < 30: return np.nan
    m = g.R.mean(); r = (g.R-m).groupby(pd.to_datetime(g.ts).dt.year).sum()
    se = np.sqrt((r**2).sum())/len(g)
    return float(m/se) if se > 0 else np.nan


NOMBRE = {"A": "retroceso a la EMA20", "B": "cruce EMA20/200",
          "C": "reversion estocastica"}

if __name__ == "__main__":
    T = pd.concat([corre(p) for p in INSTR], ignore_index=True)
    T.to_csv("data/ema200_estocastico.csv", index=False)
    print(f"\n=== LAS DOS IDEAS SIN FIBONACCI · {len(T)} operaciones · 7 instrumentos ===")
    print("    z SIEMPRE agrupado por ano\n")
    print(f"  {'estrategia':>22} {'EMA200':>7} | {'n':>7} {'R neta':>9} {'z':>7} "
          f"{'instrumentos +':>15}")
    for (modo, ft), g in T.groupby(["modo","tend"]):
        pos = sum(1 for p, x in g.groupby("par") if x.R.mean() > 0)
        print(f"  {NOMBRE[modo]:>22} {'si' if ft else 'no':>7} | {len(g):>7} "
              f"{g.R.mean():>+9.4f} {zano(g):>+7.2f} {pos:>12}/7")

    print(f"\n  desglose por temporalidad (con filtro EMA200)\n")
    print(f"  {'estrategia':>22} {'tf':>6} | {'n':>7} {'R neta':>9} {'z':>7} {'inst +':>7}")
    for (modo, tf), g in T[T.tend].groupby(["modo","tf"]):
        pos = sum(1 for p, x in g.groupby("par") if x.R.mean() > 0)
        print(f"  {NOMBRE[modo]:>22} {tf:>6} | {len(g):>7} {g.R.mean():>+9.4f} "
              f"{zano(g):>+7.2f} {pos:>4}/7")

    print(f"\n  las 10 mejores celdas de las {T.groupby(['tf','modo','stop','rr','tend']).ngroups}"
          f", y si aguantan repartidas por instrumento\n")
    res = []
    for k, g in T.groupby(["tf","modo","stop","rr","tend"]):
        z_ = zano(g)
        if not np.isfinite(z_): continue
        pos = sum(1 for p, x in g.groupby("par") if x.R.mean() > 0)
        res.append((z_, k, len(g), g.R.mean(), pos))
    print(f"  {'tf':>6} {'estrategia':>22} {'stop':>5} {'rr':>4} {'EMA200':>7} "
          f"{'n':>6} {'R neta':>9} {'z':>7} {'inst +':>7}")
    for z_, k, n_, m_, pos in sorted(res, reverse=True)[:10]:
        print(f"  {k[0]:>6} {NOMBRE[k[1]]:>22} {k[2]:>5} {k[3]:>4.1f} "
              f"{'si' if k[4] else 'no':>7} {n_:>6} {m_:>+9.4f} {z_:>+7.2f} {pos:>4}/7")
    ok = [r for r in res if r[0] > 2 and r[4] >= 5]
    print(f"\n  celdas que cumplen el criterio declarado (z>2 y positivas en 5+ de 7): "
          f"{len(ok)} de {len(res)}")
