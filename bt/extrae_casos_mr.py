"""Extrae casos REALES de la estrategia para el artefacto visual.

Mismas reglas que bt/mr_tope_dia.py y que pine/mean_reversion_m15.pine.
Saca ventanas de velas M15 con sus indicadores y lo que hace la estrategia.

  python3 bt/extrae_casos_mr.py
"""
import numpy as np, pandas as pd, json, sys

PIP, COSTE_P, K, STOP_P, MAXP, HOR = 1e-4, 0.7, 1.5, 15.0, 2, 64
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
H1=M.high.to_numpy(); L1=M.low.to_numpy(); C1=M.close.to_numpy()
M["b15"] = M.index // 15
V = M.groupby("b15").agg(ts=("loc","first"), o=("open","first"), h=("high","max"),
                         l=("low","min"), c=("close","last"))
V["i1"] = M.groupby("b15").apply(lambda g: g.index[-1], include_groups=False).to_numpy()
V = V.reset_index(drop=True)
o=V.o.to_numpy(); h=V.h.to_numpy(); l=V.l.to_numpy(); c=V.c.to_numpy(); I1=V.i1.to_numpy()
ema = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
dd = np.diff(c, prepend=c[0])
up = pd.Series(np.where(dd>0,dd,0.0)).ewm(alpha=1/14, adjust=False).mean()
dn = pd.Series(np.where(dd<0,-dd,0.0)).ewm(alpha=1/14, adjust=False).mean()
rsi = (100-100/(1+up/dn.replace(0,np.nan))).fillna(50).to_numpy()
sdp = pd.Series(c).rolling(20).std().to_numpy()          # muestral, como el backtest
bu = ema + K*sdp; bl = ema - K*sdp
mid = (h+l)/2
crudoC = (l < bl) & (c > mid) & (c > o) & (rsi < 30)
crudoV = (h > bu) & (c < mid) & (c > 0) & (c < o) & (rsi > 70)
dia = pd.Series(V.ts).dt.normalize().to_numpy()

# ---- recorrer igual que el backtest, guardando TODO lo que pasa
idx = np.nonzero(crudoC | crudoV)[0]; idx = idx[(idx>40) & (idx<len(V)-2)]
ev = []          # cada señal y que se hizo con ella
ult=-1; dia_act=None; perd=0
for p in idx:
    lado = 1 if crudoC[p] else -1
    base = {"i": int(p), "lado": int(lado), "dia": str(pd.Timestamp(dia[p]).date())}
    if dia[p] != dia_act:
        dia_act, perd = dia[p], 0
    if p <= ult:
        ev.append({**base, "accion": "descartada_posicion_viva"}); continue
    if perd >= MAXP:
        ev.append({**base, "accion": "descartada_dia_cerrado"}); continue
    ent = o[p+1]; rgo = STOP_P*PIP; sl = ent - lado*rgo; ob = ema[p]
    if (ob-ent)*lado <= PIP:
        ev.append({**base, "accion": "descartada_objetivo_cerca",
                   "ent": float(ent), "obj": float(ob)}); continue
    a = I1[p]+1; b = min(a+HOR*15, len(C1))
    hi=H1[a:b]; lo=L1[a:b]
    gs = (lo<=sl) if lado>0 else (hi>=sl)
    gt = (hi>=ob) if lado>0 else (lo<=ob)
    ks = int(np.argmax(gs)) if gs.any() else 10**9
    kt = int(np.argmax(gt)) if gt.any() else 10**9
    if ks==kt==10**9: pips, kf, razon, pxs = (C1[b-1]-ent)*lado/PIP, HOR*15, "tiempo", float(C1[b-1])
    elif ks<=kt:      pips, kf, razon, pxs = -STOP_P, ks, "stop", float(sl)
    else:             pips, kf, razon, pxs = (ob-ent)*lado/PIP, kt, "objetivo", float(ob)
    neto = pips - COSTE_P
    perd = perd+1 if neto <= 0 else 0
    isal = p + max(1, kf//15)
    ev.append({**base, "accion": "operada", "ent": float(ent), "sl": float(sl),
               "obj": float(ob), "pxs": pxs, "razon": razon, "pips": float(pips),
               "neto": float(neto), "i_sal": int(min(isal, len(V)-1)),
               "min": int(kf), "perd_tras": int(perd)})
    ult = isal
E = pd.DataFrame(ev)
print(f"señales {len(E)} · operadas {(E.accion=='operada').sum()}")
print(E.accion.value_counts().to_string())

def ventana(i0, i1, extra_izq=14, extra_der=12):
    a = max(0, i0-extra_izq); b = min(len(V)-1, i1+extra_der)
    out = []
    for j in range(a, b+1):
        out.append({"t": pd.Timestamp(V.ts.iloc[j]).strftime("%d/%m %H:%M"),
                    "o": round(float(o[j]),5), "h": round(float(h[j]),5),
                    "l": round(float(l[j]),5), "c": round(float(c[j]),5),
                    "e": round(float(ema[j]),5), "bu": round(float(bu[j]),5),
                    "bl": round(float(bl[j]),5), "r": round(float(rsi[j]),1)})
    return a, out

CASOS = []
def add(clave, titulo, leccion, i0, i1, marcas):
    a, velas = ventana(i0, i1)
    CASOS.append({"clave": clave, "titulo": titulo, "leccion": leccion,
                  "base": int(a), "velas": velas, "marcas": marcas})

op = E[E.accion=="operada"]
# 1 compra que gana · la de objetivo mas limpio
s = op[(op.lado==1)&(op.razon=="objetivo")].sort_values("pips", ascending=False).iloc[3]
add("compra_gana", "Compra que llega al objetivo",
    "Las cuatro condiciones se cumplen, entras en la apertura de la vela siguiente "
    "y el precio vuelve a la media. Es el caso que funciona y pasa el 27 % de las veces.",
    int(s.i), int(s.i_sal), [{"i": int(s.i), "tipo": "señal", "lado": 1},
     {"i": int(s.i)+1, "tipo": "entrada", "lado": 1, "ent": s.ent, "sl": s.sl,
      "obj": s.obj, "i_sal": int(s.i_sal), "razon": s.razon, "pips": round(s.pips,1),
      "neto": round(s.neto,1)}])
# 2 compra que pierde
s = op[(op.lado==1)&(op.razon=="stop")].iloc[25]
add("compra_pierde", "Compra que se va al stop",
    "Misma señal, mismas cuatro condiciones, y el precio sigue cayendo. Pierdes los "
    "15 pips y ya llevas 1 de las 2 que cierran el día. No hay nada que hacer distinto.",
    int(s.i), int(s.i_sal), [{"i": int(s.i), "tipo": "señal", "lado": 1},
     {"i": int(s.i)+1, "tipo": "entrada", "lado": 1, "ent": s.ent, "sl": s.sl,
      "obj": s.obj, "i_sal": int(s.i_sal), "razon": s.razon, "pips": round(s.pips,1),
      "neto": round(s.neto,1)}])
# 3 venta que gana
s = op[(op.lado==-1)&(op.razon=="objetivo")].sort_values("pips", ascending=False).iloc[3]
add("venta_gana", "Venta que llega al objetivo",
    "El espejo exacto: el máximo perfora la banda de arriba, RSI por encima de 70, "
    "vela roja que cierra en la mitad baja. Vendes en la apertura siguiente.",
    int(s.i), int(s.i_sal), [{"i": int(s.i), "tipo": "señal", "lado": -1},
     {"i": int(s.i)+1, "tipo": "entrada", "lado": -1, "ent": s.ent, "sl": s.sl,
      "obj": s.obj, "i_sal": int(s.i_sal), "razon": s.razon, "pips": round(s.pips,1),
      "neto": round(s.neto,1)}])
# 4 salida por tiempo
s = op[op.razon=="tiempo"].iloc[2]
add("por_tiempo", "Ni stop ni objetivo: sales por tiempo",
    "Pasan 16 horas y el precio no ha tocado ninguno de los dos. Cierras a mercado "
    "donde esté. Pasa en el 12 % de las operaciones y casi siempre sales cerca de cero.",
    int(s.i), int(s.i_sal), [{"i": int(s.i), "tipo": "señal", "lado": int(s.lado)},
     {"i": int(s.i)+1, "tipo": "entrada", "lado": int(s.lado), "ent": s.ent, "sl": s.sl,
      "obj": s.obj, "i_sal": int(s.i_sal), "razon": s.razon, "pips": round(s.pips,1),
      "neto": round(s.neto,1)}])
# 5 descartada: objetivo demasiado cerca
d = E[E.accion=="descartada_objetivo_cerca"]
if len(d):
    s = d.iloc[len(d)//2]
    add("obj_cerca", "Señal que NO se toma: el objetivo está pegado",
        "Las cuatro condiciones se cumplen, pero la EMA20 está a menos de 1 pip de la "
        "entrada. No hay recorrido que ganar y el peaje se lo come. Se descarta.",
        int(s.i), int(s.i)+6, [{"i": int(s.i), "tipo": "descartada", "lado": int(s.lado),
         "motivo": "El objetivo está a menos de 1 pip"}])
# 6 descartada por posicion viva
d = E[E.accion=="descartada_posicion_viva"]
s = d.iloc[len(d)//2]
prev = op[op.i < s.i].iloc[-1]
add("pos_viva", "Señal que NO se toma: ya tienes una abierta",
    "Aparece una señal nueva mientras la anterior sigue viva. Se ignora. Nunca dos "
    "posiciones a la vez: es lo que mantiene el riesgo del día bajo control.",
    int(prev.i), int(max(s.i, prev.i_sal)),
    [{"i": int(prev.i), "tipo": "señal", "lado": int(prev.lado)},
     {"i": int(prev.i)+1, "tipo": "entrada", "lado": int(prev.lado), "ent": prev.ent,
      "sl": prev.sl, "obj": prev.obj, "i_sal": int(prev.i_sal), "razon": prev.razon,
      "pips": round(prev.pips,1), "neto": round(prev.neto,1)},
     {"i": int(s.i), "tipo": "descartada", "lado": int(s.lado),
      "motivo": "Ya hay una posición abierta"}])
# 7 el dia que se cierra: dos perdidas seguidas y una tercera señal ignorada
cerr = None
for d_, g in E.groupby("dia"):
    ops = g[g.accion=="operada"]
    ig = g[g.accion=="descartada_dia_cerrado"]
    if len(ops) >= 2 and len(ig) >= 1 and (ops.perd_tras.max() >= 2):
        cerr = (d_, ops, ig); break
if cerr:
    d_, ops, ig = cerr
    dos = ops[ops.perd_tras > 0].head(2)
    if len(dos) < 2: dos = ops.head(2)
    marcas = []
    for _, s in dos.iterrows():
        marcas.append({"i": int(s.i), "tipo": "señal", "lado": int(s.lado)})
        marcas.append({"i": int(s.i)+1, "tipo": "entrada", "lado": int(s.lado),
                       "ent": s.ent, "sl": s.sl, "obj": s.obj, "i_sal": int(s.i_sal),
                       "razon": s.razon, "pips": round(s.pips,1), "neto": round(s.neto,1)})
    si = ig.iloc[0]
    marcas.append({"i": int(si.i), "tipo": "descartada", "lado": int(si.lado),
                   "motivo": "DÍA CERRADO: 2 pérdidas seguidas"})
    add("dia_cerrado", "El día que se cierra: la regla de las 2 pérdidas",
        "Dos pérdidas seguidas y cierras la plataforma. La tercera señal del día se "
        "ignora, aunque sea buena. Esta regla vale 41 puntos de aprobación y es la "
        "parte de la estrategia que más dinero salva.",
        int(dos.i.min()), int(max(si.i, dos.i_sal.max())), marcas)

print(f"\ncasos: {[x['clave'] for x in CASOS]}")
res = {"casos": CASOS, "resumen": {
    "n": int((E.accion=='operada').sum()),
    "acierto": round(100*float((op.neto>0).mean()),1),
    "objetivo": round(100*float((op.razon=='objetivo').mean()),1),
    "stop": round(100*float((op.razon=='stop').mean()),1),
    "tiempo": round(100*float((op.razon=='tiempo').mean()),1),
    "neto": round(float(op.neto.mean()),3),
    "descartadas": int((E.accion!='operada').sum())}}
open("data/casos_mr.json","w").write(json.dumps(res, ensure_ascii=False))
print(json.dumps(res["resumen"], ensure_ascii=False))
print(f"bytes: {len(json.dumps(res))}")
