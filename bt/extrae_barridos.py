"""Saca barridos reales para que el senale DONDE entra. Extraccion, no medicion.

Se ensenan velas POSTERIORES al barrido a proposito: sin ellas no puede senalar
una entrada. Por eso estos casos NO valen para medir su acierto; valen para
aprender su regla, que luego se mide sobre las 14.637 que no ha visto.
"""
import json, numpy as np, pandas as pd

U = 1e-4
ANTES, DESPUES = 24, 12          # velas de M5 alrededor del barrido
N_CASOS = 60
SEMILLA = 20260916

SES = {"asia": (0, 8), "londres": (8, 14), "ny": (14, 23)}
PAREJA = [("londres", "asia"), ("ny", "londres")]

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
loc = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert("Europe/Madrid").tz_localize(None)
m1["loc"] = loc; m1["dia"] = loc.normalize(); m1["h"] = loc.hour

M5 = (m1.set_index("loc").resample("5min", label="left", closed="left")
        .agg(o=("open","first"), h5=("high","max"), l5=("low","min"),
             c=("close","last"), n=("close","size")).dropna())
M5 = M5[M5.n >= 2].reset_index().rename(columns={"loc":"t"})
M5["dia"] = pd.DatetimeIndex(M5.t).normalize()
M5["hora"] = pd.DatetimeIndex(M5.t).hour
T5 = M5.t.to_numpy()

rangos = {n: m1[(m1.h >= a) & (m1.h < b)].groupby("dia").agg(hi=("high","max"), lo=("low","min"))
          for n, (a, b) in SES.items()}

cand = []
for ses, ref in PAREJA:
    a, b = SES[ses]
    V = M5[(M5.hora >= a) & (M5.hora < b)]
    R = rangos[ref]
    for dia, W in V.groupby("dia"):
        if dia not in R.index: continue
        nh, nl = float(R.hi[dia]), float(R.lo[dia])
        if not (np.isfinite(nh) and np.isfinite(nl)): continue
        hh = W.h5.to_numpy(); ll = W.l5.to_numpy(); cc = W.c.to_numpy()
        idx = W.index.to_numpy()
        for lado, niv in ((-1, nh), (1, nl)):
            fuera = False; ext = np.nan
            for k in range(len(W)):
                cruza = (hh[k] > niv) if lado < 0 else (ll[k] < niv)
                if not fuera:
                    if not cruza: continue
                    fuera = True; ext = hh[k] if lado < 0 else ll[k]
                else:
                    ext = max(ext, hh[k]) if lado < 0 else min(ext, ll[k])
                vuelve = (cc[k] < niv) if lado < 0 else (cc[k] > niv)
                if not vuelve: continue
                fuera = False
                cand.append((int(idx[k]), lado, niv, float(ext), ses))
                ext = np.nan

print(f"barridos disponibles: {len(cand)}")
rng = np.random.default_rng(SEMILLA)
pick = rng.choice(len(cand), size=N_CASOS, replace=False)

o5 = M5.o.to_numpy(); h5 = M5.h5.to_numpy(); l5 = M5.l5.to_numpy(); c5 = M5.c.to_numpy()
casos = []
for z in sorted(pick):
    g, lado, niv, ext, ses = cand[z]
    j0, j1 = g - ANTES, g + DESPUES
    if j0 < 0 or j1 >= len(M5): continue
    # el tramo tiene que ser continuo: sin saltos de fin de semana por medio
    if (T5[j1] - T5[j0]) > np.timedelta64((ANTES + DESPUES + 4) * 5, "m"): continue
    velas = [[round(float(o5[j]), 5), round(float(h5[j]), 5),
              round(float(l5[j]), 5), round(float(c5[j]), 5)] for j in range(j0, j1 + 1)]
    casos.append(dict(
        id=f"b{z:06d}", ses=ses, lado=int(lado),
        niv=round(niv, 5), ext=round(ext, 5),
        i_barr=g - j0, velas=velas,
        rgo=round(abs(ext - float(c5[g])) / U, 1),
        hora=pd.Timestamp(T5[g]).strftime("%Y-%m-%d %H:%M")))

rng.shuffle(casos)
for n, c in enumerate(casos): c["n"] = n + 1
json.dump(casos, open("data/barridos_casos.json", "w"), separators=(",", ":"))
print(f"casos: {len(casos)}   fichero {len(open('data/barridos_casos.json').read())/1024:.0f} KB")
print(pd.Series([c["ses"] for c in casos]).value_counts().to_string())
print(pd.Series([c["lado"] for c in casos]).value_counts().to_string())
