"""Extrae una ventana real para VERIFICAR que los rangos salen de donde deben.

Para cada vela M15 guarda los niveles que estarian en vigor (el alto y bajo de
la vela ANTERIOR ya cerrada de D1, H4, H1 y M15) y de que vela padre salen,
con su ventana horaria exacta. La pagina recalcula los padres a partir de las
propias M15 y comprueba que coinciden.

  python3 bt/extrae_rangos.py
"""
import numpy as np, pandas as pd, json, sys

PIP = 1e-4
M = pd.read_parquet("data/eurusd_m1.parquet")
ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")
M["k15"] = M.ts.dt.floor("15min")
M["k60"] = M.ts.dt.floor("1h")
M["k240"] = M.ts.dt.floor("4h")

def agr(clave):
    V = M.groupby(clave).agg(o=("open","first"), h=("high","max"),
                             l=("low","min"), c=("close","last"), n=("close","size"))
    return V[V.n >= 3]

V15, V60, V240, VD = agr("k15"), agr("k60"), agr("k240"), agr("dfx")
print(f"M15 {len(V15)} · H1 {len(V60)} · H4 {len(V240)} · D1 {len(VD)}")

# ---- ventana: 4 dias con barridos de D1 por los dos lados, para que se vea
ini = pd.Timestamp("2026-03-02 00:00")
fin = ini + pd.Timedelta(days=4)
w = V15[(V15.index >= ini) & (V15.index < fin)]
if len(w) < 200:
    w = V15.iloc[-384:]
    ini, fin = w.index[0], w.index[-1] + pd.Timedelta(minutes=15)
print(f"ventana: {ini} -> {fin}  ({len(w)} velas M15)")

# mapa de cada M15 a su padre en cada temporalidad
idx15 = w.index
padre = {}
padre["H1"]  = idx15.floor("1h")
padre["H4"]  = idx15.floor("4h")
nyw = idx15.tz_localize("UTC").tz_convert("America/New_York").tz_localize(None)
padre["D1"]  = (nyw - pd.Timedelta(hours=17)).floor("D")

# instante EXACTO en que cierra cada vela de cada temporalidad: la ultima M15
# que le pertenece, mas 15 minutos. Sirve para probar que el nivel en vigor
# viene de una vela YA CERRADA (sin mirar al futuro).
def cierres(clave_m15):
    g = pd.Series(V15.index, index=clave_m15).groupby(level=0).max()
    return (g + pd.Timedelta(minutes=15))

CIE = {}
CIE["H1"]  = cierres(V15.index.floor("1h"))
CIE["H4"]  = cierres(V15.index.floor("4h"))
ny15 = V15.index.tz_localize("UTC").tz_convert("America/New_York").tz_localize(None)
CIE["D1"]  = cierres((ny15 - pd.Timedelta(hours=17)).floor("D"))
CIE["M15"] = pd.Series(V15.index + pd.Timedelta(minutes=15), index=V15.index)

def previa(V, claves, tf):
    """Para cada vela, el alto/bajo de la vela ANTERIOR de esa temporalidad,
    y el instante en que esa vela anterior cerro."""
    pos = {k: i for i, k in enumerate(V.index)}
    ah, al, pt, pc = [], [], [], []
    for k in claves:
        i = pos.get(k, None)
        if i is None or i == 0:
            ah.append(None); al.append(None); pt.append(None); pc.append(None); continue
        kp = V.index[i-1]
        ah.append(round(float(V.h.iloc[i-1]), 5))
        al.append(round(float(V.l.iloc[i-1]), 5))
        pt.append(str(kp))
        pc.append(str(CIE[tf].get(kp, pd.NaT)))
    return ah, al, pt, pc

niv = {}
for nom, V, cl in (("D1", VD, padre["D1"]), ("H4", V240, padre["H4"]),
                   ("H1", V60, padre["H1"])):
    a, b, t, c = previa(V, cl, nom)
    niv[nom] = {"alto": a, "bajo": b, "padre": t, "cierre": c}
# M15: la vela inmediatamente anterior
pos15 = {k: i for i, k in enumerate(V15.index)}
a15, b15, t15, c15 = [], [], [], []
for k in idx15:
    i = pos15[k]
    a15.append(round(float(V15.h.iloc[i-1]), 5) if i > 0 else None)
    b15.append(round(float(V15.l.iloc[i-1]), 5) if i > 0 else None)
    t15.append(str(V15.index[i-1]) if i > 0 else None)
    c15.append(str(V15.index[i-1] + pd.Timedelta(minutes=15)) if i > 0 else None)
niv["M15"] = {"alto": a15, "bajo": b15, "padre": t15, "cierre": c15}

velas = [{"t": str(k), "o": round(float(r.o),5), "h": round(float(r.h),5),
          "l": round(float(r.l),5), "c": round(float(r.c),5),
          "pD": str(padre["D1"][i]), "p4": str(padre["H4"][i]), "p1": str(padre["H1"][i])}
         for i, (k, r) in enumerate(w.iterrows())]

# ---- las velas padre que caen dentro de la ventana, para la tabla de control
def dentro(V, a, b):
    s = V[(V.index >= a) & (V.index < b)]
    return [{"t": str(k), "o": round(float(r.o),5), "h": round(float(r.h),5),
             "l": round(float(r.l),5), "c": round(float(r.c),5), "n": int(r.n)}
            for k, r in s.iterrows()]
padres = {"D1": dentro(VD, padre["D1"][0], fin), "H4": dentro(V240, ini, fin),
          "H1": dentro(V60, ini, fin)}
print({k: len(v) for k, v in padres.items()})

# ---- medianas historicas, para el contraste
med = {k: round(float(np.median((V.h - V.l)/PIP)), 1)
       for k, V in (("D1",VD),("H4",V240),("H1",V60),("M15",V15))}
print("medianas:", med)

sal = {"ini": str(ini), "fin": str(fin), "velas": velas, "niveles": niv,
       "padres": padres, "medianas": med}
open("data/rangos_verificacion.json","w").write(json.dumps(sal, ensure_ascii=False))
import os; print("bytes:", os.path.getsize("data/rangos_verificacion.json"))
