"""El modelo "9 a.m. CR" y las dos variantes mecanicas de Brad Gould.

Del video de backtesting:
    "the 8 a.m. candle range high and low on the 1 hour, and the
     9:00 a.m. candle range high and low on the 15 minute.
     these are the two steps that you must follow"
    "you target the 1 hour high ... partials at the midpoint"
    "the higher time frame is what dictates the lower time frame"

Del video de Brad Gould, dos afirmaciones que SI son mecanicas:
    agresiva  = entrar en cuanto la vela cierra de vuelta dentro del rango
    conservadora = esperar el retroceso al 50% de la vela de liquidacion
    stop encima de la VELA DE LIQUIDACION, no encima del extremo del rango
    ("based on data, not vibes")

Lo genuinamente nuevo frente a todo lo ya medido en este repo: el ancla
horaria fija. Todos los CRT anteriores usaban rangos rodantes vela a vela.

Control de deteccion: el MISMO modelo anclado a otras horas. Si las 9:00 de
Nueva York tienen algo, el ancla 09 tiene que separarse de las demas.
Celda primaria declarada antes de mirar: ancla 09, rango M15, entrada
agresiva, stop en la vela de liquidacion, objetivo extremo opuesto del H1.

  python3 bt/crt_9am.py
"""
import numpy as np, pandas as pd, itertools, sys

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
         "NAS100": ("data/nsxusd_m1.parquet", 1e-0, 1.50),
         "SPX500": ("data/spxusd_m1.parquet", 1e-0, 0.60)}
ANCLAS = (3, 6, 9, 12, 15)      # hora NY de la vela M15; el H1 es la anterior
VENTANA = 180                   # minutos de busqueda del barrido
ESPERA = 120                    # minutos que aguanta la orden limitada
HOR = 480                       # tope de la operativa


def carga(par):
    ruta, U, COSTE = INSTR[par]
    M = pd.read_parquet(ruta)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    t = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    M["t"] = t
    M["k5"] = t.dt.floor("5min")
    return M, U, COSTE


def corre(par):
    M, U, COSTE = carga(par)
    o, h, l, c = (M[x].to_numpy(np.float64) for x in ("open", "high", "low", "close"))
    tt = M.t.to_numpy()
    m5 = M.groupby("k5", sort=False).agg(
        h=("high", "max"), l=("low", "min"), c=("close", "last"),
        i0=("open", "size")).reset_index()
    idx5 = np.searchsorted(tt, m5.k5.to_numpy())           # primer minuto de cada M5
    f5 = np.concatenate([idx5[1:], [len(M)]])              # fin (exclusivo)
    h5, l5, c5 = m5.h.to_numpy(), m5.l.to_numpy(), m5.c.to_numpy()
    dias = pd.unique(M.t.dt.floor("1440min").to_numpy())
    filas = []
    for d0 in dias:
        for A in ANCLAS:
            a = d0 + np.timedelta64(A, "h")
            i_h1 = np.searchsorted(tt, a - np.timedelta64(60, "m"))
            i_m0 = np.searchsorted(tt, a)
            i_m1 = np.searchsorted(tt, a + np.timedelta64(15, "m"))
            i_w1 = np.searchsorted(tt, a + np.timedelta64(15 + VENTANA, "m"))
            if i_m0 - i_h1 < 30 or i_m1 - i_m0 < 8 or i_w1 - i_m1 < 30:
                continue
            H1 = (l[i_h1:i_m0].min(), h[i_h1:i_m0].max())
            M15 = (l[i_m0:i_m1].min(), h[i_m0:i_m1].max())
            if H1[1] - H1[0] < 2 * U:
                continue
            for nr, (lo, hi) in (("M15", M15), ("H1", H1)):
                if hi - lo < 2 * U:
                    continue
                w_l, w_h = l[i_m1:i_w1], h[i_m1:i_w1]
                sl = np.flatnonzero(w_l <= lo)
                sh = np.flatnonzero(w_h >= hi)
                pl = int(sl[0]) if len(sl) else 10 ** 9
                ph = int(sh[0]) if len(sh) else 10 ** 9
                if pl == ph == 10 ** 9:
                    continue
                lado = 1 if pl < ph else -1
                s = i_m1 + min(pl, ph)                     # minuto del barrido
                niv = lo if lado > 0 else hi
                # confirmacion: primera vela M5 que cierra de vuelta dentro
                k = int(np.searchsorted(idx5, s, "right")) - 1
                kf = None
                while k + 1 < len(m5) and idx5[k] < i_w1 + 60:
                    if (c5[k] > lo if lado > 0 else c5[k] < hi):
                        kf = k
                        break
                    k += 1
                if kf is None or f5[kf] >= len(M):
                    continue
                # extremo del barrido y vela de liquidacion (la del extremo)
                seg = slice(s, f5[kf])
                if lado > 0:
                    ext = float(l[seg].min())
                else:
                    ext = float(h[seg].max())
                k5a = int(np.searchsorted(idx5, s, "right")) - 1
                sub = np.arange(k5a, kf + 1)
                kl = sub[np.argmin(l5[sub])] if lado > 0 else sub[np.argmax(h5[sub])]
                mid_liq = (h5[kl] + l5[kl]) / 2.0
                base = dict(par=par, fecha=pd.Timestamp(d0), ancla=A, rango=nr,
                            lado=lado)
                # --- dos modelos de entrada -------------------------------
                for ent_nom in ("agresiva", "conservadora"):
                    if ent_nom == "agresiva":
                        e = int(f5[kf])                    # primer minuto tras el cierre
                        ent = float(c5[kf])
                    else:
                        e0, e1 = int(f5[kf]), min(int(f5[kf]) + ESPERA, len(M))
                        if e1 <= e0 + 2:
                            continue
                        toca = (np.flatnonzero(l[e0:e1] <= mid_liq) if lado > 0
                                else np.flatnonzero(h[e0:e1] >= mid_liq))
                        muere = (np.flatnonzero(l[e0:e1] <= ext) if lado > 0
                                 else np.flatnonzero(h[e0:e1] >= ext))
                        if not len(toca):
                            continue
                        if len(muere) and muere[0] < toca[0]:
                            continue                       # invalidada antes de entrar
                        e = e0 + int(toca[0]) + 1
                        ent = float(mid_liq)
                    if e >= len(M) - 5:
                        continue
                    fin = min(e + HOR, len(M),
                              int(np.searchsorted(tt, d0 + np.timedelta64(20, "h"))))
                    if fin <= e + 5:
                        continue
                    hh, ll = h[e:fin], l[e:fin]
                    for st_nom, stop in (("liquidacion", ext), ("rango", niv)):
                        rgo = (ent - stop) * lado
                        if rgo < 2 * U:
                            continue
                        b = (np.flatnonzero(ll <= stop) if lado > 0
                             else np.flatnonzero(hh >= stop))
                        ib = int(b[0]) if len(b) else 10 ** 9
                        obj = {"CR": H1[1] if lado > 0 else H1[0],
                               "50%": (H1[0] + H1[1]) / 2,
                               "3R": ent + 3 * rgo * lado}
                        for ob_nom, tp in obj.items():
                            if (tp - ent) * lado <= 0:
                                continue
                            a_ = (np.flatnonzero(hh >= tp) if lado > 0
                                  else np.flatnonzero(ll <= tp))
                            ia = int(a_[0]) if len(a_) else 10 ** 9
                            rr = abs(tp - ent) / rgo
                            if ia == ib == 10 ** 9:
                                R = (float(c[fin - 1]) - ent) * lado / rgo
                            else:
                                R = rr if ia < ib else -1.0
                            filas.append(dict(base, entrada=ent_nom, stop=st_nom,
                                              objetivo=ob_nom, R=R, rr=rr,
                                              coste=COSTE * U / rgo))
    return pd.DataFrame(filas)


def zc(g):
    """z con error estandar agrupado por instrumento-dia."""
    v = g.R
    if len(v) < 10:
        return np.nan
    cl = (g.par + "|" + g.fecha.astype(str))
    m = v.mean()
    r = (v - m).groupby(cl).sum()
    se = np.sqrt((r ** 2).sum()) / len(v)
    return float(m / se) if se > 0 else np.nan


if __name__ == "__main__":
    D = pd.concat([corre(p) for p in INSTR], ignore_index=True)
    D.to_csv("data/crt_9am.csv", index=False)
    D["N"] = D.R - D.coste
    print(f"=== MODELO 9 a.m. CR · {len(D)} filas · 5 instrumentos · 2020-2026 ===")
    print("    z con error estandar agrupado por instrumento-dia\n")

    P = D[(D.ancla == 9) & (D.rango == "M15") & (D.entrada == "agresiva")
          & (D.stop == "liquidacion") & (D.objetivo == "CR")]
    print("  CELDA PRIMARIA DECLARADA  (ancla 09 · rango M15 · agresiva · "
          "stop liquidacion · objetivo CR)")
    print(f"    n {len(P)}   R:R {P.rr.mean():.2f}   acierto {(P.R>0).mean():.1%}   "
          f"esperado {(1/(1+P.rr)).mean():.1%}")
    print(f"    R BRUTA {P.R.mean():+.4f}  (z {zc(P):+.2f})    "
          f"R NETA {P.N.mean():+.4f}\n")

    print("  A · CONTROL DE DETECCION: la misma celda anclada a otras horas NY\n")
    print(f"    {'ancla':>6} {'n':>5} {'R:R':>6} {'acierto':>8} {'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
    Q = D[(D.rango == "M15") & (D.entrada == "agresiva") & (D.stop == "liquidacion")
          & (D.objetivo == "CR")]
    for k, g in Q.groupby("ancla"):
        mk = " <-" if k == 9 else ""
        print(f"    {k:>4}:00 {len(g):>5} {g.rr.mean():>6.2f} {(g.R>0).mean():>7.1%} "
              f"{g.R.mean():>+9.4f} {zc(g):>+7.2f} {g.N.mean():>+9.4f}{mk}")
    print()

    print("  B · las dos afirmaciones mecanicas de Brad Gould (ancla 09, objetivo CR)\n")
    print(f"    {'rango':>5} {'entrada':>13} {'stop':>12} {'n':>5} {'R:R':>6} "
          f"{'acierto':>8} {'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
    for (nr, en, st), g in D[(D.ancla == 9) & (D.objetivo == "CR")].groupby(
            ["rango", "entrada", "stop"]):
        print(f"    {nr:>5} {en:>13} {st:>12} {len(g):>5} {g.rr.mean():>6.2f} "
              f"{(g.R>0).mean():>7.1%} {g.R.mean():>+9.4f} {zc(g):>+7.2f} {g.N.mean():>+9.4f}")
    print()

    print("  C · el objetivo (ancla 09, rango M15, agresiva, stop liquidacion)\n")
    print(f"    {'objetivo':>9} {'n':>5} {'R:R':>6} {'acierto':>8} {'esperado':>9} "
          f"{'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
    for k, g in D[(D.ancla == 9) & (D.rango == "M15") & (D.entrada == "agresiva")
                  & (D.stop == "liquidacion")].groupby("objetivo"):
        print(f"    {k:>9} {len(g):>5} {g.rr.mean():>6.2f} {(g.R>0).mean():>7.1%} "
              f"{(1/(1+g.rr)).mean():>8.1%} {g.R.mean():>+9.4f} {zc(g):>+7.2f} "
              f"{g.N.mean():>+9.4f}")
    print()

    print("  D · celda primaria por instrumento\n")
    print(f"    {'instr':>7} {'n':>5} {'R:R':>6} {'acierto':>8} {'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
    for k, g in P.groupby("par"):
        print(f"    {k:>7} {len(g):>5} {g.rr.mean():>6.2f} {(g.R>0).mean():>7.1%} "
              f"{g.R.mean():>+9.4f} {zc(g):>+7.2f} {g.N.mean():>+9.4f}")
    print()

    print("  E · celda primaria por ano\n")
    P = P.copy(); P["ano"] = P.fecha.dt.year
    print(f"    {'ano':>6} {'n':>5} {'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
    for k, g in P.groupby("ano"):
        print(f"    {k:>6} {len(g):>5} {g.R.mean():>+9.4f} {zc(g):>+7.2f} {g.N.mean():>+9.4f}")
