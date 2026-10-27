"""Su regla del barrido de sesion, medida. Pre-registro docs/PREREGISTRO_barrido_sesion.md

Su especificacion del 16-09-2026, literal:
  nivel = extremo de la sesion de referencia
  barrido = la vela de M5 perfora el nivel y CIERRA del lado de dentro
  confirmacion en M5
  stop = extremo alcanzado en el barrido
  objetivo = 2R
"""
import numpy as np, pandas as pd
from math import erf, sqrt

U, COSTE, RR = 1e-4, 1.43, 2.0
CADUCA = 12          # velas de M5 desde el barrido
HOR    = 60 * 24 * 3 # minutos maximos que puede durar una operacion

# hora de Madrid, de su indicador Sesiones
SES = {"asia": (0, 8), "londres": (8, 14), "ny": (14, 23)}
# que sesion barre los extremos de cual
PAREJA = [("londres", "asia"), ("ny", "londres")]

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
loc = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert("Europe/Madrid").tz_localize(None)
m1["loc"] = loc
m1["dia"] = loc.normalize()
m1["h"] = loc.hour

M5 = (m1.set_index("loc").resample("5min", label="left", closed="left")
        .agg(o=("open","first"), h5=("high","max"), l5=("low","min"),
             c=("close","last"), n=("close","size"), ts=("ts","first")).dropna())
M5 = M5[M5.n >= 2].reset_index().rename(columns={"loc":"t"})
M5["dia"] = pd.DatetimeIndex(M5.t).normalize()
M5["hora"] = pd.DatetimeIndex(M5.t).hour

# rangos de cada sesion y dia
rangos = {}
for nom, (a, b) in SES.items():
    g = m1[(m1.h >= a) & (m1.h < b)].groupby("dia").agg(hi=("high","max"), lo=("low","min"))
    rangos[nom] = g

t1 = m1.ts.to_numpy(); h1 = m1.high.to_numpy(); l1 = m1.low.to_numpy()

# Se entra al CIERRE de la vela de M5, no en su marca de tiempo, que es su
# primer minuto. Resolver desde la marca meteria el recorrido de la propia
# vela de entrada dentro de la operacion: eso ya ha pasado cuando entras.
def resuelve(t_ent, ent, stop, obj, largo):
    """Camino en M1 desde el CIERRE de la vela de entrada, no desde su inicio."""
    i = int(np.searchsorted(t1, np.datetime64(t_ent) + np.timedelta64(5, "m"),
                            side="left"))
    fin = min(len(t1), i + HOR)
    for k in range(i, fin):
        if largo:
            if l1[k] <= stop: return 0
            if h1[k] >= obj:  return 1
        else:
            if h1[k] >= stop: return 0
            if l1[k] <= obj:  return 1
    return None

ops = []
sin_regla = 0
for ses, ref in PAREJA:
    a, b = SES[ses]
    V = M5[(M5.hora >= a) & (M5.hora < b)]
    R = rangos[ref]
    for dia, W in V.groupby("dia"):
        if dia not in R.index: continue
        niv_hi, niv_lo = float(R.hi[dia]), float(R.lo[dia])
        if not np.isfinite(niv_hi) or not np.isfinite(niv_lo): continue
        o  = W.o.to_numpy();  hh = W.h5.to_numpy()
        ll = W.l5.to_numpy(); cc = W.c.to_numpy()
        tt = W.ts.to_numpy(); tl = W.t.to_numpy()
        usado = {"hi": False, "lo": False}
        for k in range(len(W)):
            for lado, niv, clave in ((-1, niv_hi, "hi"), (1, niv_lo, "lo")):
                # barrido: perfora el nivel y cierra del lado de dentro
                if lado < 0:
                    barre = hh[k] > niv and cc[k] < niv
                    ext = hh[k]
                else:
                    barre = ll[k] < niv and cc[k] > niv
                    ext = ll[k]
                if not barre: continue
                sin_regla += 1
                if usado[clave]: continue

                # C1 · entrada al cierre de la propia vela del barrido
                e1 = cc[k]
                r1 = abs(e1 - ext)
                if r1 > 0:
                    ops.append(dict(conf="C1", ses=ses, clave=clave, lado=lado,
                        t=tl[k], ent=e1, stop=ext, rgo=r1,
                        obj=e1 + lado * RR * r1, tent=tt[k]))

                # C2 · su confirmacion: cierre de M5 a favor, y despues
                #      romperse el extremo OPUESTO de la vela del barrido
                disp = ll[k] if lado < 0 else hh[k]
                visto = False
                for j in range(k, min(k + 1 + CADUCA, len(W))):
                    if not visto:
                        afavor = (cc[j] > o[j]) if lado > 0 else (cc[j] < o[j])
                        if afavor: visto = True
                        if j == k: continue
                    if not visto: continue
                    toca = (hh[j] >= disp) if lado > 0 else (ll[j] <= disp)
                    if toca:
                        r2 = abs(disp - ext)
                        if r2 > 0:
                            ops.append(dict(conf="C2", ses=ses, clave=clave, lado=lado,
                                t=tl[j], ent=disp, stop=ext, rgo=r2,
                                obj=disp + lado * RR * r2, tent=tt[j]))
                        break
                usado[clave] = True

D = pd.DataFrame(ops)
print(f"barridos brutos (sin la regla de un nivel una operacion): {sin_regla}")
print(f"senales: {len(D)}   C1 {len(D[D.conf=='C1'])}   C2 {len(D[D.conf=='C2'])}")

res = [resuelve(r.tent, r.ent, r.stop, r.obj, r.lado > 0) for r in D.itertuples()]
D["gano"] = res
D = D[D.gano.notna()].copy()
D["gano"] = D.gano.astype(int)
D["rgoP"] = D.rgo / U
D["cpc"]  = 100 * COSTE / D.rgoP
D["Rb"]   = np.where(D.gano == 1, RR, -1.0)
D["Rn"]   = D.Rb - COSTE / D.rgoP

def z2p(z): return 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))

def linea(nom, S):
    if len(S) < 2:
        print(f"{nom:>26}  n {len(S):5d}   (muy pocas)"); return
    m, s = S.Rn.mean(), S.Rn.std(ddof=1)
    ic = 1.96 * s / sqrt(len(S)); z = m / (s / sqrt(len(S)))
    nec = 100 * (1/3 + COSTE / (3 * S.rgoP.median()))
    print(f"{nom:>26}  n {len(S):5d}  acierto {100*S.gano.mean():5.1f} %  "
          f"(necesita {nec:4.1f})  riesgo {S.rgoP.median():5.1f} p  "
          f"coste {S.cpc.median():5.1f} %  bruta {S.Rb.mean():+.4f}  "
          f"NETA {m:+.4f}  IC95 [{m-ic:+.4f}, {m+ic:+.4f}]  z {z:+.2f}")

print("\n" + "=" * 128)
print("CELDA PRINCIPAL: C2, Londres + Nueva York juntas")
print("=" * 128)
P = D[D.conf == "C2"]
linea("celda principal", P)

print("\n--- las dos confirmaciones ---")
for c in ("C1", "C2"): linea(c, D[D.conf == c])

print("\n--- por sesion ---")
for c in ("C1", "C2"):
    for s in ("londres", "ny"): linea(f"{c} {s}", D[(D.conf == c) & (D.ses == s)])

print("\n--- por nivel barrido (C2) ---")
for k, nom in (("hi", "barre el maximo"), ("lo", "barre el minimo")):
    linea(f"C2 {nom}", P[P.clave == k])

print("\n--- por año (C2) ---")
for y in sorted(pd.DatetimeIndex(P.t).year.unique()):
    linea(f"C2 {y}", P[pd.DatetimeIndex(P.t).year == y])

print("\n--- reparto del riesgo en pips (C2) ---")
print(P.rgoP.describe(percentiles=[.1,.25,.5,.75,.9]).round(1).to_string())
print(f"\noperaciones al dia (C2): {len(P) / P.t.dt.normalize().nunique():.2f}")
D.to_csv("data/barrido_sesion.csv", index=False)
