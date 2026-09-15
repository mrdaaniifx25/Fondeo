"""Genera la baraja de etiquetado ciego del barrido de Asia.

Corta el grafico M5 justo en el cierre de la vela envolvente -el momento de
decidir- y guarda aparte lo que paso despues, que el usuario no ve.  El usuario
dice si opera, hacia donde, y donde pone entrada, stop y objetivo; luego se
resuelve con M1.

Salidas:
  data/etiquetado_asia_setups.json   lo que se ensena  (sin futuro)
  data/etiquetado_asia_verdad.csv    ficha de cada setup, con fecha
  data/etiquetado_asia_camino.parquet  el M1 posterior, para resolver
"""
import json
import sys
import numpy as np
import pandas as pd

RUTA, UNIDAD, TZ = "data/eurusd_m1.parquet", 0.0001, "Europe/Madrid"

# Dos barajas.  La v1 pre-selecciona con la lectura estricta -solo el primer
# barrido del dia, y si la envolvente no sale en 1 o 2 velas ese dia no hay
# nada-.  La v2 usa la lectura laxa: sigue buscando barridos mas tarde y se
# queda con el primero que si trae envolvente.  La v2 deja mas trabajo al
# criterio del usuario, y sale de la poblacion que peor rinde.
BARAJAS = {
    "v1": dict(desde="2020-01-01", hasta="2026-01-01", estricta=True,
               por_ano=10, semilla=20260827, barajar=True),
    "v2": dict(desde="2026-03-01", hasta="2026-08-01", estricta=False,
               por_ano=None, semilla=20260828, barajar=True),
}
CUAL = sys.argv[1] if len(sys.argv) > 1 else "v1"
CFG = BARAJAS[CUAL]
DESDE, HASTA = CFG["desde"], CFG["hasta"]
SUF = "" if CUAL == "v1" else "2"

rng = np.random.default_rng(CFG["semilla"])

m1 = pd.read_parquet(RUTA)
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = (pd.DatetimeIndex(m1.ts).tz_localize("UTC")
             .tz_convert(TZ).tz_localize(None))
m1["b5"] = m1["loc"].dt.floor("5min")

v = (m1.groupby("b5")
       .agg(o=("open", "first"), h=("high", "max"), l=("low", "min"),
            c=("close", "last"), ts=("ts", "last"), n=("ts", "size"))
       .reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date
v["hm"] = v.b5.dt.hour * 100 + v.b5.dt.minute
v["asia"] = v.hm < 800
v["lon"] = (v.hm >= 800) & (v.hm < 1400)


def envuelve(i, alcista):
    """la vela i envuelve por cuerpo a la i-1 y va en direccion contraria"""
    if i < 1:
        return False
    a, b = v.iloc[i - 1], v.iloc[i]
    if alcista and not (b.c > b.o):
        return False
    if not alcista and not (b.c < b.o):
        return False
    return min(b.o, b.c) <= min(a.o, a.c) and max(b.o, b.c) >= max(a.o, a.c)


# ---------------------------------------------------------------- los setups
setups = []
for dia, g in v.groupby("dia"):
    a = g[g.asia]
    if len(a) < 60:
        continue
    hi, lo = float(a.h.max()), float(a.l.min())
    L = g[g.lon]
    if L.empty:
        continue
    i0, i1 = L.index[0], L.index[-1]
    hallado = False
    for i in range(i0, i1 + 1):
        r = v.iloc[i]
        baja, alta = r.c < lo, r.c > hi
        if not (baja or alta):
            continue
        alc = baja
        for k in (1, 2):
            j = i + k
            if j > i1 or not envuelve(j, alc):
                continue
            setups.append(dict(dia=str(dia), i_barrido=int(i), i_gatillo=int(j),
                               i_fin_lon=int(i1), i_inicio=int(g.index[0]),
                               lado=1 if alc else -1, asia_hi=hi, asia_lo=lo))
            hallado = True
            break
        if CFG["estricta"] or hallado:
            break        # estricta: corta en el primer barrido, haya gatillo o no

s = pd.DataFrame(setups)
s["ts"] = v.ts.to_numpy()[s.i_gatillo]
s = s[(s.ts >= DESDE) & (s.ts < HASTA)].reset_index(drop=True)
s["ano"] = pd.to_datetime(s.ts).dt.year

s = s.drop_duplicates("dia", keep="first")     # uno por dia, nunca dos
if CFG["por_ano"]:
    elegidos = []
    for ano, g in s.groupby("ano"):
        k = min(CFG["por_ano"], len(g))
        elegidos.append(g.iloc[rng.choice(len(g), size=k, replace=False)])
    sel = pd.concat(elegidos)
else:
    sel = s
sel = sel.sort_values("ts").reset_index(drop=True)
# el orden de presentacion se baraja para que no vaya por fechas
sel = sel.iloc[rng.permutation(len(sel))].reset_index(drop=True)
sel["id"] = [f"S{n:02d}" for n in range(1, len(sel) + 1)]

print(f"baraja {CUAL} · candidatos {len(s):,}  ·  elegidos {len(sel)}  ·  "
      f"{sel.ano.value_counts().sort_index().to_dict()}")

# ---------------------------------------------- lo que se ensena y lo que no
ts1 = m1.ts.to_numpy()
fichas, caminos, mec = [], [], []
for r in sel.itertuples():
    ini = int(r.i_inicio)                       # primera vela del dia (00:00)
    fin = int(r.i_gatillo)                      # el corte: nada despues
    tr = v.iloc[ini:fin + 1]
    fichas.append(dict(
        id=r.id, lado=int(r.lado), fecha=str(v.b5.iloc[fin]),
        cierre=round(float(v.c.iloc[fin]), 5),
        velas=[[round(float(x.o), 5), round(float(x.h), 5),
                round(float(x.l), 5), round(float(x.c), 5),
                int(x.b5.hour) * 100 + int(x.b5.minute)] for x in tr.itertuples()],
        asia_hi=round(r.asia_hi, 5), asia_lo=round(r.asia_lo, 5),
        i_barrido=int(r.i_barrido) - ini,
        n_asia=int((tr.hm < 800).sum()),
    ))
    # la regla mecanica del usuario, para tener con que comparar
    prev = v.iloc[fin - 1]
    ent = float(v.c.iloc[fin])
    sl = (float(prev.l) - UNIDAD) if r.lado > 0 else (float(prev.h) + UNIDAD)
    rgo = abs(ent - sl)
    tp = r.asia_hi if r.lado > 0 else ent - 2 * rgo
    mec.append(dict(id=r.id, mec_entrada=ent, mec_sl=sl, mec_tp=tp))

    j0 = int(np.searchsorted(ts1, np.datetime64(r.ts), side="right"))
    j1 = int(np.searchsorted(ts1, v.ts.to_numpy()[int(r.i_fin_lon)], side="right"))
    cam = m1.iloc[j0:max(j1, j0 + 1)]
    caminos.append(pd.DataFrame(dict(id=r.id, ts=cam.ts.to_numpy(),
                                     high=cam.high.to_numpy(),
                                     low=cam.low.to_numpy(),
                                     close=cam.close.to_numpy())))

json.dump(fichas, open(f"data/etiquetado_asia{SUF}_setups.json", "w"))
sel.merge(pd.DataFrame(mec), on="id").to_csv(f"data/etiquetado_asia{SUF}_verdad.csv", index=False)
pd.concat(caminos).to_parquet(f"data/etiquetado_asia{SUF}_camino.parquet", index=False)
print("velas por setup:", int(np.mean([len(f['velas']) for f in fichas])),
      "  minutos guardados:", sum(len(c) for c in caminos))
