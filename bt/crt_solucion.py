"""La prueba que decide la idea del objetivo pendiente: fuera de muestra.

Todo lo anterior estaba medido sobre 2020-2026 entero, que es donde se
encontro la idea. Eso no vale como prueba. Aqui:

  1 se construye la regla mirando SOLO 2020-2023
  2 se suelta tal cual sobre 2024-2026, sin tocar nada
  3 se informa lo que hizo

A la idea se le dan sus mejores opciones -12 variantes del objetivo
pendiente- pero la eleccion se hace sin ver el futuro. Si sobrevive, hay
estrategia. Si no, se cierra.

  python3 bt/crt_solucion.py
"""
import numpy as np, pandas as pd

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50)}
MINS, VELAS = 720, 3
CORTE = np.datetime64("2024-01-01")


def marco(M, regla, nmin):
    B = M.set_index("ts").resample(regla, label="left", closed="left").agg(
        h=("high","max"), l=("low","min"), c=("close","last"), n=("close","size")).dropna()
    return B[B.n >= nmin]


def pendiente(B, caduca):
    """Direccion del objetivo CRT vivo en cada vela del marco. Solo pasado."""
    h, l, c = B.h.to_numpy(), B.l.to_numpy(), B.c.to_numpy()
    vivo = np.zeros(len(c), dtype=np.int8)
    for k in range(1, len(c)):
        if h[k] > h[k-1] and c[k] < h[k-1]: obj, lado = l[k-1], -1
        elif l[k] < l[k-1] and c[k] > l[k-1]: obj, lado = h[k-1], +1
        else: continue
        j = k+1
        while j < len(c) and j-k <= caduca:
            if (h[j] >= obj) if lado > 0 else (l[j] <= obj): break
            j += 1
        vivo[k+1:min(j+1, k+1+caduca, len(c))] = lado
    return vivo


def senales(par):
    ruta, U, COSTE = INSTR[par]
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    B  = marco(M, f"{MINS}min", MINS*0.3)
    Dd = marco(M, "1440min", 300)
    Ws = marco(M, "W-MON", 1500)
    ctx = {}
    for cad in (5, 10, 20):
        ctx[("D", cad)] = (Dd.index.to_numpy(), pendiente(Dd, cad))
    for cad in (3, 6, 12):
        ctx[("W", cad)] = (Ws.index.to_numpy(), pendiente(Ws, cad))
    dsig = np.sign(Dd.c.diff()).fillna(0).to_numpy().astype(np.int8)
    dfin = Dd.index.to_numpy() + np.timedelta64(1440, "m")

    h, l, c = B.h.to_numpy(), B.l.to_numpy(), B.c.to_numpy()
    ti = B.index.to_numpy()
    mh, ml, mc, mt = (M.high.to_numpy(), M.low.to_numpy(),
                      M.close.to_numpy(), M.ts.to_numpy())
    out = []
    for i in range(1, len(B)-1):
        rng = h[i-1] - l[i-1]
        if rng <= 0: continue
        if   h[i] > h[i-1] and c[i] < h[i-1]: d, stop = -1, h[i]
        elif l[i] < l[i-1] and c[i] > l[i-1]: d, stop = +1, l[i]
        else: continue
        ent = float(c[i]); rgo = abs(ent - stop)
        if rgo < 2*U: continue
        obj = ent + 1.5*rng*d
        t = ti[i] + np.timedelta64(MINS, "m")
        j0 = int(np.searchsorted(mt, t)); j1 = min(j0 + MINS*VELAS, len(mt))
        if j1 <= j0+5: continue
        hh, ll = mh[j0:j1], ml[j0:j1]
        a = np.flatnonzero(hh >= obj) if d > 0 else np.flatnonzero(ll <= obj)
        b = np.flatnonzero(ll <= stop) if d > 0 else np.flatnonzero(hh >= stop)
        ia = int(a[0]) if len(a) else 10**9; ib = int(b[0]) if len(b) else 10**9
        rr = abs(obj-ent)/rgo
        R = ((float(mc[j1-1])-ent)*d/rgo if ia == ib == 10**9 else (rr if ia < ib else -1.0))
        f = dict(par=par, t=t, d=d, rr=rr, R=R, neta=R - COSTE*U/rgo,
                 tp=int(ia < ib))
        for k, (idx, vivo) in ctx.items():
            q = int(np.searchsorted(idx, t, "right")) - 1
            f["p_"+k[0]+str(k[1])] = int(vivo[q]) if 0 <= q < len(vivo) else 0
        kd = int(np.searchsorted(dfin, t, "right"))
        f["bd"] = int(dsig[kd-1]) if kd >= 1 else 0
        out.append(f)
    return pd.DataFrame(out)


CELDAS = [(f"{m}{c}", extra) for m, cs in (("D",(5,10,20)),("W",(3,6,12)))
          for c in cs for extra in (False, True)]

if __name__ == "__main__":
    T = pd.concat([senales(p) for p in INSTR], ignore_index=True)
    T["fuera"] = T.t >= CORTE
    T.to_csv("data/crt_solucion.csv", index=False)
    A, F = T[~T.fuera], T[T.fuera]
    zz = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v) > 5 else np.nan
    an_a = (CORTE - T.t.min())/np.timedelta64(365,"D")
    an_f = (T.t.max() - CORTE)/np.timedelta64(365,"D")

    print(f"=== LA IDEA DEL OBJETIVO PENDIENTE, FUERA DE MUESTRA ===")
    print(f"    DENTRO 2020-2023 ({an_a:.1f} anos, {len(A)} senales) · "
          f"FUERA 2024-2026 ({an_f:.1f} anos, {len(F)} senales)\n")
    print("  las 12 variantes, ORDENADAS POR LO QUE HICIERON EN 2020-2023\n")
    print(f"    {'objetivo pendiente':>22} {'+sesgo':>7} | {'n':>5} {'NETA':>8} {'z':>6} "
          f"| {'n':>5} {'NETA fuera':>11} {'z':>6}")
    res = []
    for col, extra in CELDAS:
        sel = lambda X: X[(X["p_"+col] == X.d) & ((X.bd == X.d) if extra else True)]
        ga, gf = sel(A), sel(F)
        if len(ga) < 150: continue
        res.append((ga.neta.mean(), col, extra, len(ga), zz(ga.neta),
                    len(gf), gf.neta.mean(), zz(gf.neta)))
    for m, col, extra, na, za, nf, mf, zf in sorted(res, reverse=True):
        print(f"    {col:>22} {'si' if extra else '-':>7} | {na:>5} {m:>+8.4f} {za:>+6.2f} "
              f"| {nf:>5} {mf:>+11.4f} {zf:>+6.2f}")
    print(f"\n    {'SIN FILTRO':>22} {'-':>7} | {len(A):>5} {A.neta.mean():>+8.4f} "
          f"{zz(A.neta):>+6.2f} | {len(F):>5} {F.neta.mean():>+11.4f} {zz(F.neta):>+6.2f}")

    m, col, extra, na, za, nf, mf, zf = max(res)
    sel = lambda X: X[(X["p_"+col] == X.d) & ((X.bd == X.d) if extra else True)]
    G = sel(F).copy(); G["ano"] = G.t.dt.year
    print(f"\n  LA REGLA ELEGIDA MIRANDO SOLO 2020-2023: objetivo pendiente {col}"
          f"{' + sesgo diario' if extra else ''}")
    print(f"    dentro  {na:>5} operaciones   R neta {m:+.4f}")
    print(f"    FUERA   {nf:>5} operaciones   R neta {mf:+.4f}   z {zf:+.2f}\n")
    print(f"    {'':>8} {'n':>5} {'acierto':>8} {'azar':>7} {'BRUTA':>9} {'NETA':>9} {'z':>7}")
    for k, x in list(G.groupby("par")) + list(G.groupby("ano")):
        print(f"    {str(k):>8} {len(x):>5} {x.tp.mean():>7.1%} {(1/(1+x.rr)).mean():>6.1%} "
              f"{x.R.mean():>+9.4f} {x.neta.mean():>+9.4f} {zz(x.neta):>+7.2f}")
    print(f"\n  EN DINERO · cuenta 10.000 €, riesgo 1 % = 100 € por operacion")
    for et, X, an in (("2020-2023", sel(A), an_a), ("2024-2026", sel(F), an_f)):
        print(f"    {et}  {len(X)/an:>5.0f} ops/ano  {X.neta.mean()*100:>+7.2f} €/op  "
              f"{X.neta.sum()*100/an:>+9.0f} €/ano")
