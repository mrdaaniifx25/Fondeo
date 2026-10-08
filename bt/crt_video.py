"""La cascada CRT del curso en video: D1 -> H4 -> H1 -> M15, objetivo en H4.

Pre-registro: docs/PREREGISTRO_crt_cascada_video.md. Un solo pase.

Los cinco pasos del video, literales:
  1 rango = vela DIARIA anterior ya cerrada
  2 el dia en curso ACTIVA un extremo (barre minimo -> alcista)
  3 H4 activado en la misma direccion
  4 H1 activado en la misma direccion
  5 M15 CONFIRMADO: barre y cierra de vuelta dentro, sin romper el opuesto
    -> entrada en la apertura de la M15 siguiente
    -> stop detras de la mecha del barrido
    -> objetivo el extremo opuesto del rango H4

  python3 bt/crt_video.py
"""
import numpy as np, pandas as pd
from math import sqrt

INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 1.43),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 35.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  1.6)]
HOR = 2 * 1440          # tope: dos dias de minutos


def lado_activado(M, clave):
    """Por minuto: +1 si la vela en curso barrio el MINIMO de la anterior (sesgo
    alcista), -1 si barrio el maximo, 0 si ninguno o los dos. Y los extremos
    del rango de referencia. Solo mira hacia atras."""
    g = M.groupby(clave, sort=False)
    cmin = g.low.cummin().to_numpy()
    cmax = g.high.cummax().to_numpy()
    bar = g.agg(h=("high", "max"), l=("low", "min"))
    ph = M[clave].map(bar.h.shift(1)).to_numpy()
    pl = M[clave].map(bar.l.shift(1)).to_numpy()
    bl, bh = cmin <= pl, cmax >= ph
    lado = np.where(bl & ~bh, 1, np.where(bh & ~bl, -1, 0)).astype(np.int8)
    return lado, ph, pl


def corre(nom, ruta, U, coste):
    M = pd.read_parquet(ruta)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    t = (M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York")
          .dt.tz_localize(None))
    M["kD"]  = t.dt.floor("1440min")
    M["kH4"] = t.dt.floor("240min")
    M["kH1"] = t.dt.floor("60min")
    M["k15"] = t.dt.floor("15min")

    lD, _, _      = lado_activado(M, "kD")
    lH4, h4h, h4l = lado_activado(M, "kH4")
    lH1, _, _     = lado_activado(M, "kH1")

    # --- velas M15 cerradas -------------------------------------------------
    q = M.groupby("k15", sort=False).agg(o=("open","first"), h=("high","max"),
                                         l=("low","min"), c=("close","last"))
    q = q[q.index.notna()]
    ph15, pl15 = q.h.shift(1).to_numpy(), q.l.shift(1).to_numpy()
    O,H,L,C = (q[k].to_numpy() for k in "ohlc")

    # confirmacion CRT en M15: barre un extremo y CIERRA de vuelta dentro,
    # sin haberse llevado el opuesto
    up = (L <= pl15) & (C > pl15) & (C < ph15) & (H < ph15)
    dn = (H >= ph15) & (C < ph15) & (C > pl15) & (L > pl15)
    sig15 = np.where(up, 1, np.where(dn, -1, 0)).astype(np.int8)

    # ultimo minuto de cada vela M15 = donde se lee el contexto
    fin = M.groupby("k15", sort=False).apply(lambda d: d.index[-1]).reindex(q.index)
    fin = fin.to_numpy()
    idx15 = {k: i for i, k in enumerate(q.index)}
    prox = np.full(len(q), -1)          # indice de minuto de la apertura siguiente
    kk = list(q.index)
    for i in range(len(kk) - 1):
        prox[i] = fin[i] + 1

    HH, LL, OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()
    ts = M.ts.to_numpy()

    ops = []
    for i in np.nonzero(sig15)[0]:
        if i + 1 >= len(q): continue
        j = int(fin[i])                     # minuto de cierre de la M15 senal
        e = j + 1                           # apertura de la siguiente
        if e >= len(M): continue
        s = int(sig15[i])
        # contexto leido en el cierre de la vela de confirmacion
        al = int(lD[j] == s) + int(lH4[j] == s) + int(lH1[j] == s)
        ent = OO[e]
        stop = L[i] if s > 0 else H[i]      # detras de la mecha del barrido
        obj = h4h[j] if s > 0 else h4l[j]   # extremo opuesto del rango H4
        if not np.isfinite(obj): continue
        rgo = (ent - stop) * s
        rec = (obj - ent) * s
        if rgo <= 0 or rec <= 0: continue
        ops.append((nom, ts[e], s, al, ent, stop, obj, rgo / U, rec / U, e))

    if not ops: return pd.DataFrame()
    D = pd.DataFrame(ops, columns="ins ts lado alin ent stop obj rgo rec e".split())

    # --- resolucion minuto a minuto ----------------------------------------
    R, Rp = [], []
    for _, r in D.iterrows():
        a, b = int(r.e), min(int(r.e) + HOR, len(M))
        hh, ll = HH[a:b], LL[a:b]
        s, ent, rgo, rec = r.lado, r.ent, r.rgo * U, r.rec * U
        if s > 0:
            ks = np.nonzero(ll <= ent - rgo)[0]; kt = np.nonzero(hh >= ent + rec)[0]
            ps = np.nonzero(hh >= ent + rgo)[0]; pt = np.nonzero(ll <= ent - rec)[0]
        else:
            ks = np.nonzero(hh >= ent + rgo)[0]; kt = np.nonzero(ll <= ent - rec)[0]
            ps = np.nonzero(ll <= ent - rgo)[0]; pt = np.nonzero(hh >= ent + rec)[0]
        fs = ks[0] if len(ks) else 10**9;  ft = kt[0] if len(kt) else 10**9
        R.append(rec/rgo if ft < fs else (-1.0 if fs < 10**9 else 0.0))
        gs = ps[0] if len(ps) else 10**9;  gt = pt[0] if len(pt) else 10**9
        Rp.append(rec/rgo if gt < gs else (-1.0 if gs < 10**9 else 0.0))
    D["R"], D["Rpla"] = R, Rp
    D["cr"] = coste / D.rgo
    D["neta"] = D.R - D.cr
    D["dia"] = pd.to_datetime(D.ts).dt.floor("D")
    return D


def z(x, gr):
    """z de la media con error estandar agrupado."""
    if len(x) < 5: return float("nan")
    g = pd.DataFrame({"x": x.to_numpy(), "g": gr.to_numpy()}).groupby("g").x
    m, k = x.mean(), g.ngroup if False else g.count().shape[0]
    su = g.apply(lambda v: (v - m).sum())
    return m * len(x) / sqrt((su ** 2).sum()) if (su ** 2).sum() > 0 else float("nan")


T = pd.concat([corre(*a) for a in INS], ignore_index=True)
T["gr"] = T.ins + T.dia.astype(str)
P = T[T.alin == 3].copy()                   # la celda del video
uno = P.sort_values("ts").drop_duplicates(["ins", "dia"])   # una por dia

print(f"{'':<34}{'n':>6}{'R:R':>7}{'acierto':>9}{'geom':>8}"
      f"{'coste':>8}{'BRUTA':>9}{'z':>7}{'NETA':>9}{'z':>7}")

def ficha(et, D):
    if not len(D): return
    rr = (D.rec / D.rgo).mean()
    ac = (D.R > 0).mean()
    geo = (D.rgo / (D.rgo + D.rec)).mean()
    print(f"  {et:<32}{len(D):>6}{rr:>7.2f}{100*ac:>8.1f}%{100*geo:>7.1f}%"
          f"{100*D.cr.mean():>7.1f}%{D.R.mean():>+9.4f}{z(D.R, D.gr):>+7.2f}"
          f"{D.neta.mean():>+9.4f}{z(D.neta, D.gr):>+7.2f}")

print("\nPRINCIPAL  ·  las cuatro alineadas, objetivo extremo opuesto de H4")
ficha("una operacion por dia", uno)
ficha("todas las senales", P)
print("\nCONTROL 1  ·  placebo de direccion (lado invertido, misma geometria)")
pl = uno.copy(); pl["R"] = pl.Rpla; pl["neta"] = pl.Rpla - pl.cr
ficha("placebo", pl)
print("\nCONTROL 2  ·  monotonia de la cascada (cuantas temporalidades alineadas)")
for a in (0, 1, 2, 3):
    d = T[T.alin == a].sort_values("ts").drop_duplicates(["ins", "dia"])
    ficha(f"{a} alineadas", d)
print("\nPor instrumento (celda principal, una por dia)")
for nom, _, _, _ in INS:
    ficha(nom, uno[uno.ins == nom])
print("\nPor ano (celda principal, una por dia)")
for y in sorted(uno.dia.dt.year.unique()):
    ficha(str(y), uno[uno.dia.dt.year == y])
