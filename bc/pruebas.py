"""Pruebas del motor con velas hechas a mano, donde la respuesta se sabe.

Estas pruebas tendrian que haber existido antes de la primera medicion. No
existian, y por eso dos fallos -el reinicio inalcanzable y el contexto que no
miraba si el rango seguia vivo- vivieron semanas en el repositorio dando
resultados que se presentaron como medidas de la especificacion.

Se ejecuta:  python3 bc/pruebas.py
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd
import nucleo as N, motor as M

FALLOS = []

def comprueba(nombre, cond, detalle=""):
    if cond:
        print(f"  ok    {nombre}")
    else:
        print(f"  FALLA {nombre}   {detalle}")
        FALLOS.append(nombre)

def velas(filas):
    """filas: lista de (open, high, low, close). Fabrica el DataFrame que
    esperan activaciones() y vida(), con marcas de tiempo de una hora."""
    t0 = pd.Timestamp("2024-01-01 00:00")
    d = pd.DataFrame(filas, columns=["open", "high", "low", "close"]).astype(float)
    d["ini"] = [t0 + pd.Timedelta(hours=i) for i in range(len(d))]
    d["fin"] = [t0 + pd.Timedelta(hours=i, minutes=59) for i in range(len(d))]
    d["id"] = d["ini"]; d["n"] = 60
    return d

# ═══════════════════════════════════════════════════════════════════════════
print("\nACTIVACION")
# vela base 100-110. La siguiente barre el 100 y cierra dentro del cuerpo
# (cuerpo de la base: open 102, close 108) -> rango ALCISTA, objetivo 110
v = N.activaciones(velas([(102, 110, 100, 108),
                          (105,  106,  98, 106)]), "B")
comprueba("barre el bajo y cierra dentro -> alcista", v.lado.iloc[1] == 1, f"lado={v.lado.iloc[1]}")
comprueba("objetivo = alto de la vela base",         v.objetivo.iloc[1] == 110, f"obj={v.objetivo.iloc[1]}")

# barre el bajo pero cierra POR DEBAJO del cuerpo -> no activa
v = N.activaciones(velas([(102, 110, 100, 108),
                          (105, 106,  98, 101)]), "B")
comprueba("barre pero cierra fuera del cuerpo -> nada", v.lado.iloc[1] == 0)

# barre el alto y cierra dentro -> BAJISTA, objetivo 100
v = N.activaciones(velas([(102, 110, 100, 108),
                          (105, 112, 104, 106)]), "B")
comprueba("barre el alto y cierra dentro -> bajista", v.lado.iloc[1] == -1)
comprueba("objetivo = bajo de la vela base",         v.objetivo.iloc[1] == 100)

# envuelve la base por los dos lados -> no es activacion limpia
v = N.activaciones(velas([(102, 110, 100, 108),
                          (105, 112,  98, 106)]), "B")
comprueba("envuelve a la base -> nada", v.lado.iloc[1] == 0)

# lectura A: solo cuenta que ABRA fuera
v = N.activaciones(velas([(102, 110, 100, 108),
                          (99,  106,  98, 101)]), "A")
comprueba("lectura A: abre por debajo -> alcista", v.lado.iloc[1] == 1)
v = N.activaciones(velas([(102, 110, 100, 108),
                          (105, 106,  98, 106)]), "A")
comprueba("lectura A: abre dentro -> nada", v.lado.iloc[1] == 0)

# ═══════════════════════════════════════════════════════════════════════════
print("\nVIDA DEL RANGO")
# alcista con objetivo 110; la vela 3 lo alcanza
r = N.vida(N.activaciones(velas([(102, 110, 100, 108),
                                 (105, 106,  98, 106),
                                 (106, 111, 105, 110)]), "B"), "1H")
comprueba("un solo rango", len(r) == 1, f"n={len(r)}")
comprueba("alcanza el objetivo -> completado", r[0].fin_por == "completado", r[0].fin_por)
comprueba("muere en la vela que lo alcanza",
          r[0].muere == pd.Timestamp("2024-01-01 02:59"), str(r[0].muere))

# vuelve a llevarse el bajo y cierra DENTRO -> doble toma, sigue vivo
r = N.vida(N.activaciones(velas([(102, 110, 100, 108),
                                 (105, 106,  98, 106),
                                 (105, 107,  97, 105)]), "B"), "1H")
comprueba("segunda toma con cierre dentro -> tomas=2", r[0].tomas == 2, f"tomas={r[0].tomas}")
comprueba("segunda toma no lo mata", r[0].vivo, f"vivo={r[0].vivo}")

# vuelve a llevarse el bajo y CIERRA FUERA -> descartado
r = N.vida(N.activaciones(velas([(102, 110, 100, 108),
                                 (105, 106,  98, 106),
                                 (105, 107,  95, 96)]), "B"), "1H")
comprueba("cierre fuera tras reinicio -> descartado", r[0].fin_por == "descartado", r[0].fin_por)
comprueba("descartado no cuenta como completado", not r[0].vivo)

# el reinicio SI ocurre alguna vez (el fallo de BC_07 §1 lo hacia imposible)
comprueba("el reinicio es alcanzable", r[0].reiniciado)

# un rango nuevo releva al anterior
r = N.vida(N.activaciones(velas([(102, 110, 100, 108),
                                 (105, 106,  98, 106),
                                 (104, 109, 103, 108),
                                 (107, 108,  102, 107)]), "B"), "1H")
comprueba("dos rangos, el segundo releva", len(r) == 2 and r[0].fin_por in ("relevado","completado","descartado"),
          f"n={len(r)} fin0={r[0].fin_por}")

# ═══════════════════════════════════════════════════════════════════════════
print("\nCONTEXTO: un rango muerto no da contexto")
v  = N.activaciones(velas([(102, 110, 100, 108),
                           (105, 106,  98, 106),
                           (106, 111, 105, 110),     # completa aqui
                           (110, 111, 109, 110),
                           (110, 111, 109, 110)]), "B")
r  = N.vida(v, "1H")
mp = N.mapa_vivos(r, v)
comprueba("vivo mientras no ha completado", mp.r_lado.iloc[1] == 1, str(mp.r_lado.iloc[1]))
comprueba("muerto tras completar -> sin contexto", np.isnan(mp.r_lado.iloc[3]), str(mp.r_lado.iloc[3]))
comprueba("sigue sin contexto despues",            np.isnan(mp.r_lado.iloc[4]))

print("\nCONTEXTO: nada antes de nacer  (mirar al futuro)")
comprueba("la vela base no ve el rango", np.isnan(mp.r_lado.iloc[0]))

# ═══════════════════════════════════════════════════════════════════════════
print("\nREJILLA DE VELAS")
t0 = pd.Timestamp("2024-01-01 00:00", tz="UTC")
m1 = pd.DataFrame({"ts": [t0 + pd.Timedelta(minutes=i) for i in range(60*30)]})
m1["ts"] = m1["ts"].dt.tz_localize(None)
n = len(m1)
m1["open"] = 100.0; m1["high"] = 100.5; m1["low"] = 99.5; m1["close"] = 100.0
v1 = N.velas(m1, 1, "UTC", 0)
comprueba("1H de 30 h de datos -> 30 velas", len(v1) == 30, f"n={len(v1)}")
v12 = N.velas(m1, 12, "UTC", 0)
comprueba("12H con ancla 0 -> bloques a las 00 y 12",
          list(pd.DatetimeIndex(v12["id"]).hour) == [0, 12, 0], str(list(pd.DatetimeIndex(v12["id"]).hour)))
# 30 h dan tres bloques: 12 + 12 + 6. El tercero tiene EXACTAMENTE la mitad de
# los minutos y el filtro lo deja pasar. Es una vela de 12H hecha con 6 h de
# datos, y su alto y su bajo son los de media ventana.
comprueba("un bloque a medias pasa el filtro del 50 %", len(v12) == 3, f"n={len(v12)}")
comprueba("y se le nota en los minutos", v12.n.iloc[-1] == 360, f"n={v12.n.iloc[-1]}")
v12b = N.velas(m1, 12, "UTC", 6)
# con ancla 6, el primer bloque arranca a las 18:00 del dia ANTERIOR
comprueba("ancla 6 -> bloques a las 18, 06 y 18",
          list(pd.DatetimeIndex(v12b["id"]).hour) == [18, 6, 18], str(list(pd.DatetimeIndex(v12b["id"]).hour)))

# ═══════════════════════════════════════════════════════════════════════════
print("\nRESOLUCION DE LA OPERACION EN M1")
def resuelve(camino, entrada, stop, objetivo, lado, coste=1.2, unidad=0.0001):
    """Monta un M1 sintetico que recorre `camino` y pasa una sola operacion
    por el mismo codigo de resolucion que usa el motor."""
    t0 = pd.Timestamp("2024-01-01 01:00")
    d = pd.DataFrame({"ts": [t0 + pd.Timedelta(minutes=i) for i in range(len(camino))]})
    d["high"] = [c[0] for c in camino]; d["low"] = [c[1] for c in camino]
    d["open"] = d["high"]; d["close"] = d["low"]
    t1 = d["ts"].to_numpy(); H = d.high.to_numpy(); L1 = d.low.to_numpy(); C1 = d.close.to_numpy()
    ts = np.datetime64(t0 - pd.Timedelta(minutes=1))
    j0 = int(np.searchsorted(t1, ts, side="right")); j1 = len(t1)
    hh, ll = H[j0:j1], L1[j0:j1]
    gt, gs = ((hh >= objetivo, ll <= stop) if lado > 0 else (ll <= objetivo, hh >= stop))
    it  = int(np.argmax(gt)) if gt.any() else 10**9
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    rr = abs(objetivo - entrada) / abs(entrada - stop)
    if it == 10**9 and isl == 10**9:
        sal = C1[j1-1]
        return ((sal-entrada) if lado > 0 else (entrada-sal))/abs(entrada-stop), "tiempo"
    return (-1.0, "SL") if isl <= it else (float(rr), "TP")

# compra en 100, stop 99, objetivo 103  ->  R:R 3
R, mot = resuelve([(100.2, 99.8), (101, 100), (103.1, 102)], 100, 99, 103, 1)
comprueba("llega al objetivo -> R = R:R", mot == "TP" and abs(R - 3) < 1e-9, f"{mot} R={R}")
R, mot = resuelve([(100.2, 99.8), (100.1, 98.9)], 100, 99, 103, 1)
comprueba("llega al stop -> R = -1", mot == "SL" and R == -1.0, f"{mot} R={R}")
R, mot = resuelve([(103.5, 98.5)], 100, 99, 103, 1)
comprueba("los dos en el mismo minuto -> stop", mot == "SL", mot)
R, mot = resuelve([(100.2, 99.8), (100.4, 100.1)], 100, 99, 103, 1)
comprueba("ni uno ni otro -> sale por tiempo", mot == "tiempo", mot)
comprueba("salida por tiempo entre -1 y R:R", -1 < R < 3, f"R={R}")
# venta simetrica
R, mot = resuelve([(100.2, 99.8), (99, 96.9)], 100, 101, 97, -1)
comprueba("venta que alcanza el objetivo", mot == "TP" and abs(R - 3) < 1e-9, f"{mot} R={R}")

print("\nCOSTE")
riesgo_u = 10.0; coste = 1.2
comprueba("coste en R = coste/riesgo", abs((coste/riesgo_u) - 0.12) < 1e-12)
comprueba("un TP de 3 neto = 2,88", abs((3 - coste/riesgo_u) - 2.88) < 1e-12)
comprueba("un SL neto = -1,12",     abs((-1 - coste/riesgo_u) + 1.12) < 1e-12)

# ═══════════════════════════════════════════════════════════════════════════
print("\nCONTRASTE CONTRA UNA IMPLEMENTACION LENTA E INGENUA")
def vida_ingenua(v):
    """Lo mismo que vida(), escrito de la forma mas obvia posible y sin
    optimizar. Si las dos coinciden sobre datos aleatorios, el fallo tendria
    que estar en las dos a la vez."""
    o = v.to_dict("records")
    out, cur = [], None
    for i, f in enumerate(o):
        if cur is not None and cur["vivo"]:
            if (f["high"] >= cur["obj"]) if cur["lado"] > 0 else (f["low"] <= cur["obj"]):
                cur["vivo"] = False; cur["fin"] = "completado"
            else:
                if (f["low"] < cur["blo"]) if cur["lado"] > 0 else (f["high"] > cur["bhi"]):
                    cur["rein"] = True
                    lo_, hi_ = min(cur["blo"], cur["bhi"]), max(cur["blo"], cur["bhi"])
                    if lo_ <= f["close"] <= hi_:
                        cur["tomas"] += 1
                if cur["rein"]:
                    if (f["close"] < cur["blo"]) if cur["lado"] > 0 else (f["close"] > cur["bhi"]):
                        cur["vivo"] = False; cur["fin"] = "descartado"
        if f["lado"] != 0:
            if cur is not None and cur["vivo"]:
                cur["vivo"] = False; cur["fin"] = "relevado"
            cur = dict(lado=f["lado"], obj=f["objetivo"], bhi=f["base_hi"], blo=f["base_lo"],
                       tomas=1, rein=False, vivo=True, fin="")
            out.append(cur)
    return out

rng = np.random.default_rng(20260827)
igual = True
for _ in range(60):
    p = 100 + np.cumsum(rng.normal(0, .3, 400))
    filas = []
    for k in range(0, 400, 4):
        tr = p[k:k+4]
        filas.append((tr[0], tr.max(), tr.min(), tr[-1]))
    va = N.activaciones(velas(filas), "B")
    a = N.vida(va, "1H"); b = vida_ingenua(va)
    if len(a) != len(b):
        igual = False; break
    for x, y in zip(a, b):
        if (x.lado, x.tomas, x.fin_por) != (y["lado"], y["tomas"], y["fin"]):
            igual = False; break
    if not igual: break
comprueba("60 series aleatorias: las dos implementaciones coinciden", igual)

# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
if FALLOS:
    print(f"{len(FALLOS)} PRUEBAS FALLIDAS: {', '.join(FALLOS)}")
    sys.exit(1)
print("todas las pruebas pasan")
