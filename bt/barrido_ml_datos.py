"""Construye el conjunto etiquetado: cada barrido x cada vela de entrada.

TODAS las variables se calculan solo con lo ocurrido hasta el cierre de la vela
de entrada. Es donde el proyecto se pillo una fuga en agosto.
"""
import numpy as np, pandas as pd

U, COSTE, RR, NVEL = 1e-4, 1.43, 2.0, 13
SES = {"asia": (0, 8), "londres": (8, 14), "ny": (14, 23)}
PAREJA = [("londres", "asia"), ("ny", "londres")]

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
loc = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert("Europe/Madrid").tz_localize(None)
m1["loc"] = loc; m1["dia"] = loc.normalize(); m1["h"] = loc.hour

M5 = (m1.set_index("loc").resample("5min", label="left", closed="left")
        .agg(o=("open","first"), h5=("high","max"), l5=("low","min"),
             c=("close","last"), n=("close","size"), ts=("ts","first")).dropna())
M5 = M5[M5.n >= 2].reset_index().rename(columns={"loc":"t"})
M5["dia"] = pd.DatetimeIndex(M5.t).normalize()
M5["hora"] = pd.DatetimeIndex(M5.t).hour

# ATR de M5 y de H1, ambos DESPLAZADOS: solo velas ya cerradas
tr = np.maximum(M5.h5 - M5.l5,
      np.maximum((M5.h5 - M5.c.shift(1)).abs(), (M5.l5 - M5.c.shift(1)).abs()))
M5["atr5"] = tr.rolling(48).mean().shift(1)
M5["atr1h"] = tr.rolling(12).mean().shift(1)
M5["r3"]  = (M5.c / M5.c.shift(3)  - 1).shift(0)
M5["r6"]  = (M5.c / M5.c.shift(6)  - 1).shift(0)
M5["r12"] = (M5.c / M5.c.shift(12) - 1).shift(0)

rangos = {n: m1[(m1.h >= a) & (m1.h < b)].groupby("dia").agg(hi=("high","max"), lo=("low","min"))
          for n, (a, b) in SES.items()}

t1 = m1.ts.to_numpy(); h1v = m1.high.to_numpy(); l1v = m1.low.to_numpy()

# Se entra al CIERRE de la vela de M5, no en su marca de tiempo, que es su
# primer minuto. Resolver desde la marca meteria el recorrido de la propia
# vela de entrada dentro de la operacion: eso ya ha pasado cuando entras.
def resuelve(ts_ent, stop, obj, largo):
    # se entra al CIERRE de la vela de M5, cinco minutos despues de su marca
    i = int(np.searchsorted(t1, np.datetime64(ts_ent) + np.timedelta64(5, "m"),
                            side="left"))
    for k in range(i, min(len(t1), i + 60 * 24 * 3)):
        if largo:
            if l1v[k] <= stop: return 0
            if h1v[k] >= obj:  return 1
        else:
            if h1v[k] >= stop: return 0
            if l1v[k] <= obj:  return 1
    return None

filas = []
for ses, ref in PAREJA:
    a, b = SES[ses]
    V = M5[(M5.hora >= a) & (M5.hora < b)]
    R = rangos[ref]
    for dia, W in V.groupby("dia"):
        if dia not in R.index: continue
        nh, nl = float(R.hi[dia]), float(R.lo[dia])
        if not (np.isfinite(nh) and np.isfinite(nl)) or nh <= nl: continue
        o = W.o.to_numpy(); hh = W.h5.to_numpy(); ll = W.l5.to_numpy(); cc = W.c.to_numpy()
        tt = W.ts.to_numpy(); tl = W.t.to_numpy(); N = len(W)
        a5 = W.atr5.to_numpy(); a1 = W.atr1h.to_numpy()
        q3 = W.r3.to_numpy(); q6 = W.r6.to_numpy(); q12 = W.r12.to_numpy()

        for lado, niv, otro, clave in ((-1, nh, nl, "hi"), (1, nl, nh, "lo")):
            fuera = False; ext = np.nan; previos = 0
            for k in range(N):
                cruza = (hh[k] > niv) if lado < 0 else (ll[k] < niv)
                if not fuera:
                    if not cruza: continue
                    fuera = True; ext = hh[k] if lado < 0 else ll[k]
                else:
                    ext = max(ext, hh[k]) if lado < 0 else min(ext, ll[k])
                vuelve = (cc[k] < niv) if lado < 0 else (cc[k] > niv)
                if not vuelve: continue
                fuera = False
                ob, hb, lb, cb = o[k], hh[k], ll[k], cc[k]
                disp = lb if lado < 0 else hb
                prof = abs(ext - niv) / U
                for off in range(0, NVEL):
                    j = k + off
                    if j >= N: break
                    ent = cc[j]
                    rgo = abs(ent - ext)
                    if rgo <= 0: continue
                    obj = ent + lado * RR * rgo
                    g = resuelve(tt[j], ext, obj, lado > 0)
                    if g is None: continue
                    rp = rgo / U
                    filas.append((
                        pd.Timestamp(tl[j]),
                        off, rp, 100 * COSTE / rp, prof,
                        abs(cb - ob) / U, abs(hb - lb) / U,
                        abs(ent - niv) / U,
                        abs(otro - ent) / U,                       # recorrido disponible
                        (nh - nl) / U,
                        (a5[j] / U if np.isfinite(a5[j]) else np.nan),
                        (a1[j] / U if np.isfinite(a1[j]) else np.nan),
                        1 if ses == "londres" else 0,
                        int(pd.Timestamp(tl[j]).hour),
                        int(pd.Timestamp(tl[j]).dayofweek),
                        lado,
                        q3[j], q6[j], q12[j],
                        previos,
                        1 if ((cc[j] < disp) if lado < 0 else (cc[j] > disp)) else 0,
                        g, g * RR - (1 - g) - COSTE / rp))
                previos += 1
                ext = np.nan

COLS = ["t","off","rgoP","costepc","prof","cuerpo","rango_vela","dist_niv",
        "recorrido","rango_ref","atr5","atr1h","londres","hora","dow","lado",
        "r3","r6","r12","previos","cerro_mas_alla","gana","Rn"]
D = pd.DataFrame(filas, columns=COLS)
D["anio"] = pd.DatetimeIndex(D.t).year
D.to_parquet("data/barrido_ml.parquet", index=False)
print(f"filas: {len(D):,}")
print(D.groupby("anio").agg(n=("Rn","size"), acierto=("gana","mean"),
                            Rn=("Rn","mean")).round(4).to_string())
