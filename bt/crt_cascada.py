"""CRT como CONTEXTO, no como patron: la cascada de rangos hacia un objetivo superior.

Es lo que describe la clase: no se opera el rango diario esperando que se
complete, se espera a que el precio barra el low semanal y luego se van
encadenando rangos a favor (dia, 4h, 1h, M15) hasta el OBJETIVO SEMANAL.

    "nos crea un rango alcista un dia, 4 horas, 1 hora, M15,
     y nos enfoca hasta el objetivo semanal"
    "yo no tengo por que esperar que el precio vaya a completar el rango diario"
    "es simplemente esperar los rangos a favor del objetivo"

Dos cosas nuevas frente a todo lo ya medido:

  1 el OBJETIVO es el extremo del rango SEMANAL, no el de la propia vela.
    Eso cambia el R:R por completo (stop de M15, objetivo de semana).
  2 la CASCADA: cuantas temporalidades intermedias estan alineadas.

Contraste primario declarado antes de mirar: R bruta media segun el numero
de temporalidades alineadas (0,1,2,3 de D1/H4/H1), con objetivo semanal,
agrupando los cinco instrumentos. Es un contraste INTERNO: el resto de
cubos es el control. Todo lo demas es exploratorio.

  python3 bt/crt_cascada.py
"""
import numpy as np, pandas as pd, sys

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
         "NAS100": ("data/nsxusd_m1.parquet", 1e-0, 1.50),
         "SPX500": ("data/spxusd_m1.parquet", 1e-0, 0.60)}
HOR = 5 * 1440          # tope de la operativa: 5 dias de minutos
DOM = pd.Timestamp("1970-01-04")   # un domingo, origen de la semana


def contexto(M, clave):
    """Por minuto: lado del rango de esa temporalidad (+1/-1/0) y su objetivo.

    Rango = vela ANTERIOR ya cerrada. 'Activado' = la vela en curso ya se ha
    llevado uno de los dos extremos. Si se ha llevado los dos, no hay lado.
    Solo mira hacia atras: el cummin/cummax es dentro de la vela en curso.
    """
    g = M.groupby(clave, sort=False)
    cmin = g.low.cummin().to_numpy()
    cmax = g.high.cummax().to_numpy()
    bar = g.agg(h=("high", "max"), l=("low", "min"))
    ph = M[clave].map(bar.h.shift(1)).to_numpy()
    pl = M[clave].map(bar.l.shift(1)).to_numpy()
    bl, bh = cmin <= pl, cmax >= ph
    lado = np.where(bl & ~bh, 1, np.where(bh & ~bl, -1, 0)).astype(np.int8)
    obj = np.where(lado > 0, ph, np.where(lado < 0, pl, np.nan))
    return lado, obj


def corre(par):
    ruta, U, COSTE = INSTR[par]
    M = pd.read_parquet(ruta)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    t = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    dia = t.dt.floor("1440min")
    M["kW"] = DOM + pd.to_timedelta(((dia - DOM).dt.days // 7) * 7, unit="D")
    M["kD"] = dia
    M["kH4"] = t.dt.floor("240min")
    M["kH1"] = t.dt.floor("60min")
    M["k15"] = t.dt.floor("15min")

    ctx = {k: contexto(M, "k" + k) for k in ("W", "D", "H4", "H1")}
    lW, oW = ctx["W"]

    idx = np.arange(len(M), dtype=np.int64)
    M["i"] = idx
    b = M.groupby("k15", sort=False).agg(
        o=("open", "first"), h=("high", "max"), l=("low", "min"),
        c=("close", "last"), i0=("i", "first"), i1=("i", "last"), n=("close", "size"))
    kt = b.index.to_numpy()
    bo, bh, bl, bc = (b[x].to_numpy() for x in "ohlc")
    i0, i1 = b.i0.to_numpy(), b.i1.to_numpy()
    mh, ml, mc = M.high.to_numpy(), M.low.to_numpy(), M.close.to_numpy()
    mt = M.ts.to_numpy()
    kW = M.kW.to_numpy()

    q15 = np.timedelta64(15, "m")
    filas = []
    ultimo_dia = None
    for j in range(1, len(b) - 1):
        # las tres velas M15 tienen que ser consecutivas de verdad
        if kt[j] - kt[j - 1] != q15 or kt[j + 1] - kt[j] != q15:
            continue
        # confirmacion en M15: barre el extremo de la vela previa y CIERRA dentro
        if bl[j] < bl[j - 1] and bc[j] > bl[j - 1]:
            lado = 1
        elif bh[j] > bh[j - 1] and bc[j] < bh[j - 1]:
            lado = -1
        else:
            continue
        p = i1[j]                       # contexto leido al cierre de la vela j
        if lW[p] != lado:
            continue                    # sin objetivo semanal a favor no hay trade
        conf = (int(ctx["D"][0][p] == lado) + int(ctx["H4"][0][p] == lado)
                + int(ctx["H1"][0][p] == lado))
        e = i0[j + 1]
        ent = float(M.open.iat[e])
        ext = bl[j] if lado > 0 else bh[j]
        rgo = abs(ent - ext)
        if rgo < 2 * U:
            continue
        tps = {"W": float(oW[p]),
               "D": float(ctx["D"][1][p]),
               "H4": float(ctx["H4"][1][p])}
        if not np.isfinite(tps["W"]) or (tps["W"] - ent) * lado <= 0:
            continue
        d = kt[j].astype("datetime64[D]")
        if d == ultimo_dia:
            continue                    # una operacion por dia como mucho
        ultimo_dia = d
        fin = min(e + HOR, len(M),
                  int(np.searchsorted(mt, kW[e] + np.timedelta64(7, "D"))))
        if fin <= e + 5:
            continue
        hh, ll = mh[e:fin], ml[e:fin]
        s = np.flatnonzero(ll <= ext) if lado > 0 else np.flatnonzero(hh >= ext)
        ib = int(s[0]) if len(s) else 10 ** 9
        f = dict(par=par, fecha=pd.Timestamp(kt[j]), wk=str(kW[e])[:10],
                 lado=lado, conf=conf, rgo_u=rgo / U)
        for nom, tp in tps.items():
            if not np.isfinite(tp) or (tp - ent) * lado <= 0:
                f[f"R_{nom}"], f[f"rr_{nom}"] = np.nan, np.nan
                continue
            a = np.flatnonzero(hh >= tp) if lado > 0 else np.flatnonzero(ll <= tp)
            ia = int(a[0]) if len(a) else 10 ** 9
            rr = abs(tp - ent) / rgo
            if ia == ib == 10 ** 9:
                R = (float(mc[fin - 1]) - ent) * lado / rgo   # a mercado al vencer
            else:
                R = rr if ia < ib else -1.0
            f[f"R_{nom}"], f[f"rr_{nom}"] = R, rr
        f["coste"] = COSTE * U / rgo
        filas.append(f)
    return pd.DataFrame(filas)


def zc(D, col):
    """z con error estandar agrupado por instrumento-semana."""
    v = D[col].dropna()
    if len(v) < 8:
        return np.nan
    g = (D.par + "|" + D.wk).loc[v.index]
    m = v.mean()
    r = (v - m).groupby(g).sum()
    se = np.sqrt((r ** 2).sum()) / len(v)
    return float(m / se) if se > 0 else np.nan


if __name__ == "__main__":
    D = pd.concat([corre(p) for p in INSTR], ignore_index=True)
    D.to_csv("data/crt_cascada.csv", index=False)
    for k in ("W", "D", "H4"):
        D[f"N_{k}"] = D[f"R_{k}"] - D.coste

    print(f"=== CRT EN CASCADA · objetivo de temporalidad superior · {len(D)} entradas ===")
    print(f"    {len(D)} entradas M15 con contexto semanal a favor, 5 instrumentos, 2020-2026")
    print(f"    z entre parentesis: error estandar agrupado por instrumento-semana\n")

    print("  A · CONTRASTE PRIMARIO: R bruta con objetivo SEMANAL segun cascada\n")
    print(f"    {'alineadas':>10} {'n':>5} {'R:R':>6} {'acierto':>8} {'esperado':>8} "
          f"{'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
    for k, g in D.groupby("conf"):
        v = g.R_W.dropna()
        ac = float((v > 0).mean())
        esp = float((1 / (1 + g.rr_W)).mean())
        print(f"    {k:>10} {len(v):>5} {g.rr_W.mean():>6.2f} {ac:>7.1%} {esp:>8.1%} "
              f"{v.mean():>+9.4f} {zc(g,'R_W'):>+7.2f} {g.N_W.mean():>+9.4f}")
    v = D.R_W.dropna()
    print(f"    {'TODAS':>10} {len(v):>5} {D.rr_W.mean():>6.2f} {float((v>0).mean()):>7.1%} "
          f"{float((1/(1+D.rr_W)).mean()):>8.1%} {v.mean():>+9.4f} {zc(D,'R_W'):>+7.2f} "
          f"{D.N_W.mean():>+9.4f}\n")

    print("  B · el mismo trade con objetivos MAS CERCANOS (exploratorio)\n")
    print(f"    {'objetivo':>10} {'n':>5} {'R:R':>6} {'acierto':>8} {'esperado':>8} "
          f"{'R BRUTA':>9} {'z':>7} {'R NETA':>9} {'z':>7}")
    for k, et in (("W", "semanal"), ("D", "diario"), ("H4", "4 horas")):
        v = D[f"R_{k}"].dropna()
        esp = float((1 / (1 + D[f"rr_{k}"])).mean())
        print(f"    {et:>10} {len(v):>5} {D[f'rr_{k}'].mean():>6.2f} "
              f"{float((v>0).mean()):>7.1%} {esp:>8.1%} {v.mean():>+9.4f} "
              f"{zc(D,f'R_{k}'):>+7.2f} {D[f'N_{k}'].mean():>+9.4f} {zc(D,f'N_{k}'):>+7.2f}")
    print()

    print("  C · por instrumento (objetivo semanal)\n")
    print(f"    {'instr':>8} {'n':>5} {'R:R':>6} {'R BRUTA':>9} {'z':>7} {'R NETA':>9} {'z':>7}")
    for k, g in D.groupby("par"):
        print(f"    {k:>8} {len(g):>5} {g.rr_W.mean():>6.2f} {g.R_W.mean():>+9.4f} "
              f"{zc(g,'R_W'):>+7.2f} {g.N_W.mean():>+9.4f} {zc(g,'N_W'):>+7.2f}")
    print()

    print("  D · por coste/riesgo: el stop de M15 es diminuto frente al coste\n")
    D["cr"] = pd.cut(D.coste, [0, .05, .10, .20, .40, 9])
    print(f"    {'coste/riesgo':>14} {'n':>5} {'R:R':>6} {'R BRUTA':>9} {'z':>7} {'R NETA':>9} {'z':>7}")
    for k, g in D.groupby("cr", observed=True):
        print(f"    {str(k):>14} {len(g):>5} {g.rr_W.mean():>6.2f} {g.R_W.mean():>+9.4f} "
              f"{zc(g,'R_W'):>+7.2f} {g.N_W.mean():>+9.4f} {zc(g,'N_W'):>+7.2f}")
    print()

    print("  E · por ano (objetivo semanal, todo junto)\n")
    D["ano"] = D.fecha.dt.year
    print(f"    {'ano':>6} {'n':>5} {'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
    for k, g in D.groupby("ano"):
        print(f"    {k:>6} {len(g):>5} {g.R_W.mean():>+9.4f} {zc(g,'R_W'):>+7.2f} "
              f"{g.N_W.mean():>+9.4f}")
