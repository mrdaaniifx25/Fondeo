"""¿Hay materia prima para hacer scalping en EURUSD?

Tres preguntas, en orden de importancia:
  1. ¿Tienen estructura los retornos a horizonte corto? Si no, no hay nada que
     capturar con reglas de precio, se pruebe lo que se pruebe.
  2. ¿Cuanto movimiento hay frente al coste a cada horizonte?
  3. ¿Que ventaja bruta haria falta para empatar segun el tamano del stop?
"""
import numpy as np, pandas as pd
from math import sqrt, erf

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
PIP = 0.0001; COSTE = 1.2

print("=== 1. ¿HAY ESTRUCTURA? autocorrelacion de los retornos ===")
print("   Un paseo aleatorio da ~0. Negativo = rebote del spread (no operable).")
print(f"{'horizonte':>12s} {'n':>9s} {'autocorr':>10s} {'ee':>8s} {'z':>7s} {'lectura':>28s}")
for mins in (1, 5, 15, 60, 240):
    s = m1.set_index("ts").close.resample(f"{mins}min").last().dropna()
    r = np.log(s).diff().dropna()
    n = len(r)
    ac = float(r.autocorr(1))
    ee = 1/sqrt(n)
    z = ac/ee
    if abs(z) < 2: lec = "indistinguible de ruido"
    elif ac < 0:   lec = "reversion (es el spread)"
    else:          lec = "momento"
    print(f"{mins:>9d} min {n:>9,} {ac:>+10.4f} {ee:>8.4f} {z:>+7.1f} {lec:>28s}")

print("\n=== 2. RAZON DE VARIANZAS (Lo-MacKinlay) ===")
print("   VR = 1 -> paseo aleatorio puro. VR != 1 -> hay estructura explotable.")
base = np.log(m1.set_index("ts").close.resample("1min").last().dropna()).diff().dropna()
v1 = base.var()
for q in (2, 5, 15, 30, 60):
    agg = base.rolling(q).sum().dropna()[::q]
    vr = agg.var()/(q*v1)
    n = len(base)
    ee = sqrt(2*(2*q-1)*(q-1)/(3*q*n))
    print(f"   q={q:>3} velas: VR = {vr:.4f} | ee {ee:.4f} | z {(vr-1)/ee:+.1f}")

print("\n=== 3. MOVIMIENTO DISPONIBLE FRENTE AL COSTE ===")
print(f"   Coste de ida y vuelta asumido: {COSTE} pips")
print(f"{'horizonte':>12s} {'|mov| medio':>13s} {'mov/coste':>11s} {'% del mov que se lleva el coste':>34s}")
for mins in (1, 5, 15, 30, 60, 240):
    s = m1.set_index("ts").close.resample(f"{mins}min").last().dropna()
    mov = (s.diff().abs()/PIP).mean()
    print(f"{mins:>9d} min {mov:>13.2f} {mov/COSTE:>11.2f} {100*COSTE/mov:>33.0f}%")

print("\n=== 4. EL MURO DEL COSTE: ventaja bruta necesaria para EMPATAR ===")
print(f"{'stop (pips)':>12s} {'coste/riesgo':>13s} {'WR necesario a 1:1':>20s} {'WR necesario a 1:2':>20s}")
for stop in (3, 5, 8, 12, 18, 30, 50):
    c = COSTE/stop
    wr1 = (1+c)/2
    wr2 = (1+c+ (0)) / 3 + c/3*0
    # a 1:2, gana 2R-c y pierde 1R+c -> p*(2-c) = (1-p)*(1+c) -> p = (1+c)/(3)
    wr2 = (1+c)/3
    print(f"{stop:>12d} {100*c:>12.1f}% {100*wr1:>19.1f}% {100*wr2:>19.1f}%")
print("\n   Referencia: la mejor ventaja bruta de toda la investigacion fue +0.26 R,")
print("   con stops de 18 pips. Un scalper con stop de 5 pips necesita +0.24 R solo")
print("   para no perder dinero.")
