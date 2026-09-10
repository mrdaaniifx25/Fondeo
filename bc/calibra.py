"""FASE 1 de la calibracion. NO mira ningun resultado de operacion.

Se busca que combinacion de (huso, lectura de activacion) hace que la estructura
que ELLOS narran aparezca donde ELLOS dicen. Criterio fijado en BC_03 §3.
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd
import nucleo as N

# lo que ellos narran, transcrito de BC_01 §9
CASOS = [
    dict(nom="S&P 500 · 22-07-2026", ruta="data/spxusd_m1.parquet",
         dia="2026-07-22", tf="12H", horas=12, lado=+1,
         cita="«En 12 horas identificamos la activacion de rango y un posible objetivo»"),
    dict(nom="NASDAQ · 30-07-2026", ruta="data/nsxusd_m1.parquet",
         dia="2026-07-30", tf="1D", horas=24, lado=0,
         cita="«Objetivo diario activado y completado»"),
]

print("="*100)
print("CALIBRACION · fase 1 · no se mira ningun resultado de operacion")
print("  criterio (BC_03 §3): ¿hay rango activo en la temporalidad y direccion que ellos nombran?")
print("="*100)

for c in CASOS:
    print(f"\n{c['nom']}   {c['tf']}   {c['cita']}")

tabla = []
cache = {}
for huso in N.HUSOS:
    for lectura in ("A", "B", "C"):
        aciertos, detalle = 0, []
        for c in CASOS:
            k = (c["ruta"], c["horas"], huso)
            if k not in cache:
                m1 = pd.read_parquet(c["ruta"]); m1["ts"] = pd.to_datetime(m1["ts"])
                cache[k] = N.velas(m1, c["horas"], huso, 0)
            v = N.activaciones(cache[k], lectura)
            rangos = N.vida(v, c["tf"])
            # ellos dicen "identificamos la activacion... lo que nos permitio
            # ANTICIPAR": el contexto es anterior a la operacion. Lo que hay que
            # comprobar es que el rango estuviera VIVO ese dia, no que naciera.
            dia = pd.Timestamp(c["dia"]).date()
            fin_dia = pd.Timestamp(c["dia"]) + pd.Timedelta(days=1)
            vivos = [r for r in rangos
                     if r.nace < fin_dia and r.nace >= fin_dia - pd.Timedelta(days=5)]
            if not vivos:
                detalle.append("ningun rango en los 5 dias previos"); continue
            lados = sorted({r.lado for r in vivos})
            ok = (c["lado"] == 0) or (c["lado"] in lados)
            aciertos += int(ok)
            ult = vivos[-1]
            detalle.append(("SI " if ok else "no ") +
                           f"({len(vivos)} rangos, lados {lados}, ult {str(ult.nace)[:10]})")
        tabla.append(dict(huso=huso, lectura=lectura, aciertos=aciertos,
                          d1=detalle[0], d2=detalle[1] if len(detalle) > 1 else ""))

T = pd.DataFrame(tabla).sort_values("aciertos", ascending=False)
print("\n" + "="*100)
print(f"{'huso':10s} {'lectura':8s} {'aciertos':>9s}   {'S&P 22-07':28s} {'NASDAQ 30-07'}")
print("="*100)
for r in T.itertuples():
    print(f"{r.huso:10s} {r.lectura:8s} {r.aciertos:>9d}   {r.d1:28s} {r.d2}")

mx = T.aciertos.max()
gan = T[T.aciertos == mx]
print("\n" + "="*100)
if mx == 0:
    print("NINGUNA combinacion reproduce ninguna de sus operaciones.")
    print("Segun BC_03 §3, eso significa que la especificacion NO es su metodo.")
else:
    print(f"Maximo de aciertos: {mx} de {len(CASOS)}.  Combinaciones empatadas: {len(gan)}")
    print(gan[["huso","lectura"]].to_string(index=False))
    if len(gan) > 1:
        print("\nHay empate -> segun BC_03 §4 todas pasan a la fase 2 y el umbral sube al 99 %.")
T.to_csv("data/bc_calibracion.csv", index=False)
