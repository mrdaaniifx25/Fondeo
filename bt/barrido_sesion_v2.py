"""Su regla del barrido de sesion, con SUS correcciones del 16-09-2026.

Cambios frente a v1, los tres que el corrigio:
  4  el stop va al extremo de la EXCURSION entera, no al de la vela que cierra
  5  se intentan TODOS los barridos, no uno por nivel
  7  la confirmacion no caduca: vale hasta el final de la sesion
"""
import numpy as np, pandas as pd
from math import erf, sqrt

U, COSTE, RR = 1e-4, 1.43, 2.0
HOR = 60 * 24 * 3

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

rangos = {n: m1[(m1.h >= a) & (m1.h < b)].groupby("dia").agg(hi=("high","max"), lo=("low","min"))
          for n, (a, b) in SES.items()}

t1 = m1.ts.to_numpy(); h1 = m1.high.to_numpy(); l1 = m1.low.to_numpy()

def resuelve(t_ent, stop, obj, largo):
    i = int(np.searchsorted(t1, np.datetime64(t_ent), side="right"))
    for k in range(i, min(len(t1), i + HOR)):
        if largo:
            if l1[k] <= stop: return 0
            if h1[k] >= obj:  return 1
        else:
            if h1[k] >= stop: return 0
            if l1[k] <= obj:  return 1
    return None

ops = []; n_barridos = 0
for ses, ref in PAREJA:
    a, b = SES[ses]
    V = M5[(M5.hora >= a) & (M5.hora < b)]
    R = rangos[ref]
    for dia, W in V.groupby("dia"):
        if dia not in R.index: continue
        nh, nl = float(R.hi[dia]), float(R.lo[dia])
        if not (np.isfinite(nh) and np.isfinite(nl)): continue
        o = W.o.to_numpy(); hh = W.h5.to_numpy(); ll = W.l5.to_numpy()
        cc = W.c.to_numpy(); tt = W.ts.to_numpy(); tl = W.t.to_numpy()
        N = len(W)

        for lado, niv, clave in ((-1, nh, "hi"), (1, nl, "lo")):
            fuera = False; ext = np.nan
            for k in range(N):
                cruza = (hh[k] > niv) if lado < 0 else (ll[k] < niv)
                if not fuera:
                    if not cruza: continue
                    fuera = True
                    ext = hh[k] if lado < 0 else ll[k]
                else:
                    ext = max(ext, hh[k]) if lado < 0 else min(ext, ll[k])
                # ¿cierra de vuelta dentro? entonces la excursion termina aqui
                vuelve = (cc[k] < niv) if lado < 0 else (cc[k] > niv)
                if not vuelve: continue
                fuera = False
                n_barridos += 1

                # C1 · al cierre de la vela que recupera el nivel
                r1 = abs(cc[k] - ext)
                if r1 > 0:
                    ops.append(dict(conf="C1", ses=ses, clave=clave, lado=lado,
                        t=tl[k], tent=tt[k], ent=cc[k], stop=ext, rgo=r1,
                        obj=cc[k] + lado * RR * r1))

                # C2 · un cierre de M5 a favor y despues romper el extremo
                #      opuesto de esa vela. Sin caducidad: hasta fin de sesion.
                disp = ll[k] if lado < 0 else hh[k]
                visto = False
                for j in range(k, N):
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
                                t=tl[j], tent=tt[j], ent=disp, stop=ext, rgo=r2,
                                obj=disp + lado * RR * r2))
                        break
                ext = np.nan

D = pd.DataFrame(ops)
print(f"barridos (excursion completa): {n_barridos}")
print(f"senales: C1 {len(D[D.conf=='C1'])}   C2 {len(D[D.conf=='C2'])}")

D["gano"] = [resuelve(r.tent, r.stop, r.obj, r.lado > 0) for r in D.itertuples()]
D = D[D.gano.notna()].copy(); D["gano"] = D.gano.astype(int)
D["rgoP"] = D.rgo / U
D["cpc"] = 100 * COSTE / D.rgoP
D["Rb"] = np.where(D.gano == 1, RR, -1.0)
D["Rn"] = D.Rb - COSTE / D.rgoP

def linea(nom, S):
    if len(S) < 30: print(f"{nom:>24}  n {len(S):5d}  (pocas)"); return
    m, s = S.Rn.mean(), S.Rn.std(ddof=1)
    ic = 1.96 * s / sqrt(len(S)); z = m / (s / sqrt(len(S)))
    zb = S.Rb.mean() / (S.Rb.std(ddof=1) / sqrt(len(S)))
    nec = 100 * (1/3 + COSTE / (3 * S.rgoP.median()))
    print(f"{nom:>24}  n {len(S):5d}  acierto {100*S.gano.mean():5.1f} % (nec {nec:4.1f})  "
          f"riesgo {S.rgoP.median():5.1f} p  coste {S.cpc.median():5.1f} %  "
          f"bruta {S.Rb.mean():+.4f} (z {zb:+.2f})  NETA {m:+.4f}  "
          f"IC95 [{m-ic:+.4f}, {m+ic:+.4f}]  z {z:+.2f}")

print("\n" + "=" * 140)
print("CELDA PRINCIPAL: C2, Londres + Nueva York")
print("=" * 140)
P = D[D.conf == "C2"]
linea("celda principal", P)
print("\n--- confirmaciones ---")
for c in ("C1", "C2"): linea(c, D[D.conf == c])
print("\n--- por sesion (C2) ---")
for s in ("londres", "ny"): linea(s, P[P.ses == s])
print("\n--- por nivel (C2) ---")
for k, n in (("hi", "barre el maximo"), ("lo", "barre el minimo")): linea(n, P[P.clave == k])
print("\n--- por año (C2) ---")
for y in sorted(pd.DatetimeIndex(P.t).year.unique()):
    linea(str(y), P[pd.DatetimeIndex(P.t).year == y])
print("\n--- riesgo en pips (C2) ---")
print(P.rgoP.describe(percentiles=[.1,.25,.5,.75,.9]).round(1).to_string())
print(f"\noperaciones al dia (C2): {len(P)/P.t.dt.normalize().nunique():.2f}")
D.to_csv("data/barrido_sesion_v2.csv", index=False)
