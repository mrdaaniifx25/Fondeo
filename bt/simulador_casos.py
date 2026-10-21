"""docs/PREREGISTRO_simulador.md · genera los 100 casos.

El fichero de salida NO contiene nada posterior a las 11:30 ni ninguna
resolucion: las operaciones se resuelven despues, aparte.
"""
import numpy as np, pandas as pd, json

U, TZ, SEMILLA = 0.0001, "Europe/Madrid", 20260828
DESDE, HASTA = "2024-01-01", "2026-01-01"

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1 = m1[(m1["loc"] >= DESDE) & (m1["loc"] < HASTA)].reset_index(drop=True)

def marco(regla):
    g = (m1.set_index("loc").resample(regla)
           .agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
                n=("close","size")))
    return g[g.n >= 1].reset_index()

m5  = marco("5min");  m5["dia"]  = m5["loc"].dt.date.astype(str)
m15 = marco("15min"); h1 = marco("1h")
m5["hm"] = m5["loc"].dt.hour*100 + m5["loc"].dt.minute

# --- universo de dias ------------------------------------------------------
elegibles = []
for dia, g in m5.groupby("dia"):
    a = g[g.hm < 800]
    if len(a) < 12: continue                     # 12 velas de 5 min = 60 de un minuto
    hi, lo = float(a.h.max()), float(a.l.min())
    if not (hi > lo): continue
    W = g[(g.hm >= 820) & (g.hm <= 1130)]
    toca = W[((W.l <= hi) & (W.h >= hi)) | ((W.l <= lo) & (W.h >= lo))]
    if len(toca) == 0: continue
    elegibles.append((dia, hi, lo, int(toca.index[0])))

print(f"días elegibles en {DESDE[:4]}-{HASTA[:4]}: {len(elegibles)}")
rng = np.random.default_rng(SEMILLA)
sel = sorted(rng.choice(len(elegibles), size=min(100, len(elegibles)), replace=False))
dias = [elegibles[i] for i in sel]
pd.DataFrame(dias, columns=["dia","asia_hi","asia_lo","i_inicio"]).to_csv(
    "data/simulador_dias.csv", index=False)

# --- construccion de cada caso --------------------------------------------
PASO = {"5min": 5, "15min": 15, "1h": 60}

def recorta(marco_, ini, fin, n=None):
    s = marco_[(marco_["loc"] >= ini) & (marco_["loc"] <= fin)]
    if n: s = s.tail(n)
    return s, [[x.loc.strftime("%d/%m %H:%M"), round(x.o,5), round(x.h,5), round(x.l,5), round(x.c,5)]
               for x in s.itertuples()]

def cuantas(sup, inf, minutos):
    """para cada vela de `inf`, cuantas velas de `sup` han CERRADO ya.
    Solo velas cerradas: asi no se filtra ni un dato del futuro."""
    cierre = (sup["loc"] + pd.Timedelta(minutes=minutos)).to_numpy()
    ahora  = (inf["loc"] + pd.Timedelta(minutes=5)).to_numpy()
    return np.searchsorted(cierre, ahora, side="right").tolist()

casos = []
for k, (dia, hi, lo, i0) in enumerate(dias, 1):
    d0 = pd.Timestamp(dia)
    g = m5[m5.dia == dia]
    ini5 = d0 + pd.Timedelta(hours=4)
    fin5 = d0 + pd.Timedelta(hours=11, minutes=30)
    s5,  v5  = recorta(m5,  ini5, fin5)
    s15, v15 = recorta(m15, d0 - pd.Timedelta(days=1), fin5, 40)
    sh1, vh1 = recorta(h1,  d0 - pd.Timedelta(days=6), fin5, 48)
    arranque = int(np.searchsorted(s5["loc"].to_numpy(), np.datetime64(m5["loc"].iloc[i0]), side="left"))
    casos.append(dict(
        n=k, dia=dia,
        dsem=["lunes","martes","miércoles","jueves","viernes","sábado","domingo"][d0.dayofweek],
        hi=round(hi,5), lo=round(lo,5),
        k0=arranque,
        m5=v5, m15=v15, h1=vh1,
        n15=cuantas(s15, s5, 15), nh1=cuantas(sh1, s5, 60),
    ))

json.dump(casos, open("data/simulador_casos.json","w"), separators=(",",":"), ensure_ascii=False)
tot = sum(len(c["m5"]) for c in casos)
print(f"casos generados: {len(casos)}  ·  velas M5 en total: {tot}")
print(f"arranque medio en la vela {np.mean([c['k0'] for c in casos]):.0f} de {np.mean([len(c['m5']) for c in casos]):.0f}")
import os; print(f"tamaño: {os.path.getsize('data/simulador_casos.json')/1e6:.2f} MB")
