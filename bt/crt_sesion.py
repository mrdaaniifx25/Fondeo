"""El rango CRT DINAMICO por sesion (modelo SmartRisk) y su logica de sesiones.

    "instead of relying on fixed hours, I focus on the highest and lowest
     15-minute candles of the previous trading session or kill zone
     and use those as my range candles"
    "price accumulates during Asia, manipulates during London,
     distributes during New York ... but if price EXPANDS during Asia,
     then London is more likely to accumulate and the manipulation
     happens in New York"

Dos mediciones distintas.

MEDICION 1 · el trade. La vela M15 mas alta de la sesion previa es el rango
superior; la mas baja, el inferior. Se barre su extremo, se cierra de vuelta
dentro, y el objetivo es el OTRO extremo DE ESA VELA (no de la sesion). Eso
es lo que lo separa del barrido asiatico ya medido, donde el objetivo era el
extremo opuesto de la sesion entera.

MEDICION 2 · la logica de sesiones. Si Asia es estrecha (acumula) el extremo
del dia se forma en Londres; si Asia es ancha (expande) se forma en Nueva
York. Esto no necesita coste ni entrada: es una frecuencia.

Control de deteccion en la 1: la misma mecanica aplicada a la sesion que no
deberia funcionar (operar Asia con el rango de la sesion de NY anterior).

  python3 bt/crt_sesion.py
"""
import numpy as np, pandas as pd

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
         "NAS100": ("data/nsxusd_m1.parquet", 1e-0, 1.50),
         "SPX500": ("data/spxusd_m1.parquet", 1e-0, 0.60)}
# sesiones en hora de Nueva York, sobre el dia que empieza a las 18:00 del
# dia anterior (el dia FX). Se guardan como (inicio, fin) en horas desde 18:00.
SES = {"ASIA": (1, 9), "LONDRES": (9, 14), "NY": (14, 19)}
# operar X con el rango de Y, tomado hace D dias FX. El tercero es el control
# de deteccion: hay que ir al dia ANTERIOR o se lee el futuro.
PARES = [("LONDRES", "ASIA", 0), ("NY", "LONDRES", 0), ("ASIA", "NY", 1)]


def carga(par):
    ruta, U, COSTE = INSTR[par]
    M = pd.read_parquet(ruta)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    t = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    M["t"] = t
    M["fx"] = (t - pd.Timedelta("18h")).dt.floor("1440min")   # dia FX
    M["k15"] = t.dt.floor("15min")
    return M, U, COSTE


def corre(par):
    M, U, COSTE = carga(par)
    h, l, c = (M[x].to_numpy(np.float64) for x in ("high", "low", "close"))
    tt = M.t.to_numpy()
    b = M.groupby("k15", sort=False).agg(h=("high", "max"), l=("low", "min"))
    kt = b.index.to_numpy(); bh, bl = b.h.to_numpy(), b.l.to_numpy()
    dias = pd.unique(M.fx.to_numpy())
    ops, anch = [], []
    for d in dias:
        base = d + np.timedelta64(18, "h")
        lim = {}
        for s, (a, z) in SES.items():
            lim[s] = (np.searchsorted(tt, base + np.timedelta64(a, "h")),
                      np.searchsorted(tt, base + np.timedelta64(z, "h")))
        if any(j - i < 60 for i, j in lim.values()):
            continue
        # --- MEDICION 2: anchura de Asia y donde cae el extremo del dia ---
        ia, za = lim["ASIA"]
        i0, z0 = lim["ASIA"][0], lim["NY"][1]
        alto, bajo = int(np.argmax(h[i0:z0])) + i0, int(np.argmin(l[i0:z0])) + i0
        cual = lambda k: next((s for s, (i, j) in lim.items() if i <= k < j), "OTRA")
        anch.append(dict(par=par, dia=pd.Timestamp(d),
                         asia=(h[ia:za].max() - l[ia:za].min()) / U,
                         ses_alto=cual(alto), ses_bajo=cual(bajo)))
        # --- MEDICION 1: el trade -----------------------------------------
        for op, rg, atras in PARES:
            if atras:
                a_, z_ = SES[rg]
                i1 = int(np.searchsorted(tt, base - np.timedelta64(24 * atras, "h")
                                         + np.timedelta64(a_, "h")))
                z1 = int(np.searchsorted(tt, base - np.timedelta64(24 * atras, "h")
                                         + np.timedelta64(z_, "h")))
            else:
                i1, z1 = lim[rg]
            if z1 <= i1 or z1 > lim[op][0]:
                continue
            i2, z2 = lim[op]
            k0 = int(np.searchsorted(kt, tt[i1])); k1 = int(np.searchsorted(kt, tt[z1]))
            if k1 - k0 < 8:
                continue
            ka = k0 + int(np.argmax(bh[k0:k1]))     # vela M15 mas alta
            kb = k0 + int(np.argmin(bl[k0:k1]))     # vela M15 mas baja
            ses_hi, ses_lo = bh[ka], bl[kb]
            med = (ses_hi + ses_lo) / 2
            w_h, w_l = h[i2:z2], l[i2:z2]
            sh = np.flatnonzero(w_h >= ses_hi); sl = np.flatnonzero(w_l <= ses_lo)
            ph = int(sh[0]) if len(sh) else 10 ** 9
            pl = int(sl[0]) if len(sl) else 10 ** 9
            if ph == pl == 10 ** 9:
                continue
            lado = 1 if pl < ph else -1
            s = i2 + min(ph, pl)
            # la vela M15 del rango que fue barrida, y su extremo opuesto
            vhi, vlo = (bh[kb], bl[kb]) if lado > 0 else (bh[ka], bl[ka])
            dentro = vlo if lado < 0 else vhi        # objetivo "vela"
            # confirmacion: primera vela M5 que cierra de vuelta dentro del nivel
            e = s
            ext = l[s] if lado > 0 else h[s]
            while e < z2 - 1:
                e += 1
                ext = min(ext, l[e]) if lado > 0 else max(ext, h[e])
                if (e - s) % 5 == 4 and (c[e] > ses_lo if lado > 0 else c[e] < ses_hi):
                    break
            else:
                continue
            e += 1
            if e >= z2 - 5:
                continue
            ent = float(c[e - 1])
            rgo = (ent - ext) * lado
            if rgo < 2 * U:
                continue
            fin = min(int(np.searchsorted(tt, base + np.timedelta64(24, "h"))), len(M))
            if fin <= e + 5:
                continue
            hh, ll = h[e:fin], l[e:fin]
            bb = np.flatnonzero(ll <= ext) if lado > 0 else np.flatnonzero(hh >= ext)
            ib = int(bb[0]) if len(bb) else 10 ** 9
            objs = {"vela": dentro, "medio": med,
                    "sesion": ses_hi if lado > 0 else ses_lo,
                    "2.5R": ent + 2.5 * rgo * lado}
            for nom, tp in objs.items():
                if (tp - ent) * lado <= 0:
                    continue
                aa = np.flatnonzero(hh >= tp) if lado > 0 else np.flatnonzero(ll <= tp)
                ia_ = int(aa[0]) if len(aa) else 10 ** 9
                rr = abs(tp - ent) / rgo
                R = ((float(c[fin - 1]) - ent) * lado / rgo if ia_ == ib == 10 ** 9
                     else (rr if ia_ < ib else -1.0))
                ops.append(dict(par=par, dia=pd.Timestamp(d), opera=op, rango=rg,
                                lado=lado, objetivo=nom, R=R, rr=rr,
                                coste=COSTE * U / rgo, tp_tocado=int(ia_ < ib)))
    return pd.DataFrame(ops), pd.DataFrame(anch)


def zc(g):
    v = g.R
    if len(v) < 10:
        return np.nan
    cl = g.par + "|" + g.dia.astype(str)
    m = v.mean(); r = (v - m).groupby(cl).sum()
    se = np.sqrt((r ** 2).sum()) / len(v)
    return float(m / se) if se > 0 else np.nan


if __name__ == "__main__":
    res = [corre(p) for p in INSTR]
    D = pd.concat([x[0] for x in res], ignore_index=True)
    A = pd.concat([x[1] for x in res], ignore_index=True)
    D.to_csv("data/crt_sesion.csv", index=False); A.to_csv("data/crt_sesion_anchura.csv", index=False)
    D["N"] = D.R - D.coste
    print(f"=== RANGO CRT DINAMICO POR SESION · {len(D)} filas · 5 instrumentos ===")
    print("    z con error estandar agrupado por instrumento-dia\n")
    print("  1 · EL TRADE  (barrer la vela M15 extrema de la sesion previa)\n")
    print(f"    {'opera':>8} {'rango de':>9} {'objetivo':>9} {'n':>5} {'R:R':>6} "
          f"{'acierto':>8} {'geom':>7} {'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
    for (op, rg, ob), g in D.groupby(["opera", "rango", "objetivo"]):
        mk = " <-" if (op, rg) == ("LONDRES", "ASIA") and ob == "vela" else ""
        print(f"    {op:>8} {rg:>9} {ob:>9} {len(g):>5} {g.rr.mean():>6.2f} "
              f"{g.tp_tocado.mean():>7.1%} {(1/(1+g.rr)).mean():>6.1%} "
              f"{g.R.mean():>+9.4f} {zc(g):>+7.2f} {g.N.mean():>+9.4f}{mk}")
    print()
    print("  2 · LA LOGICA DE SESIONES  (¿predice Asia donde se forma el extremo?)\n")
    A["rel"] = A.groupby("par").asia.transform(lambda s: s / s.rolling(20, min_periods=10).median().shift(1))
    A = A.dropna(subset=["rel"])
    A["tipo"] = np.where(A.rel < 0.8, "ASIA ESTRECHA", np.where(A.rel > 1.2, "ASIA ANCHA", "normal"))
    print(f"    {'asia':>14} {'n':>5} | {'alto ASIA':>10} {'alto LON':>9} {'alto NY':>8} "
          f"| {'bajo ASIA':>10} {'bajo LON':>9} {'bajo NY':>8}")
    for k, g in A.groupby("tipo"):
        print(f"    {k:>14} {len(g):>5} | {(g.ses_alto=='ASIA').mean():>9.1%} "
              f"{(g.ses_alto=='LONDRES').mean():>8.1%} {(g.ses_alto=='NY').mean():>7.1%} "
              f"| {(g.ses_bajo=='ASIA').mean():>9.1%} "
              f"{(g.ses_bajo=='LONDRES').mean():>8.1%} {(g.ses_bajo=='NY').mean():>7.1%}")
    print("\n    la afirmacion: ASIA ESTRECHA -> el extremo en LONDRES;")
    print("                   ASIA ANCHA    -> el extremo en NUEVA YORK")
