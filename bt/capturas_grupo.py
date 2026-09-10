"""Cuantas capturas de TP produce una estrategia que PIERDE dinero.

La pregunta no es si en un grupo hay gente ganando. La pregunta es cuanta gente
estaria ganando aunque la estrategia fuera mala. Se simula con dos entradas
medidas en este proyecto:

  A · la regla del nivel de Asia, medida en sus propios 50 dias: -0,685 R por
      sesion. Perdedora sin discusion.
  B · una moneda perfecta: 33,3 % de acierto a 1:2 con stop de 6 pips y 1,43 de
      coste. Ni buena ni mala, solo geometria menos coste.

  python3 bt/capturas_grupo.py
"""
import json, numpy as np, pandas as pd

RNG = np.random.default_rng(20260903)
N_GENTE, SESIONES, RIESGO = 500, 20, 0.01     # un mes de mañanas al 1 %

g = pd.read_csv("data/examen_regla4.csv"); g["dia"] = pd.to_datetime(g.dia).dt.date
dias = {pd.Timestamp(v).date() for v in json.load(open("data/examen_dias4.json")).values()}
porSesion = g.groupby("dia").neta.sum().reindex(sorted(dias)).fillna(0).to_numpy()

def moneda(n):
    """Una sesion de una moneda perfecta: 1,3 operaciones, 33,3 % a 1:2, stop 6 p."""
    ops = RNG.poisson(1.3, n)
    out = np.zeros(n)
    for i, k in enumerate(ops):
        if k == 0: continue
        gana = RNG.random(k) < 1/3
        out[i] = np.sum(np.where(gana, 2.0, -1.0)) - k*1.43/6
    return out

def simula(nombre, saca):
    fin = np.zeros(N_GENTE)
    for p in range(N_GENTE):
        fin[p] = saca(SESIONES).sum()
    pc = 100*RIESGO*fin
    print(f"\n  {nombre}")
    print(f"    de {N_GENTE} personas, tras {SESIONES} mañanas:")
    print(f"      acaban el mes en verde ............ {int((pc>0).sum()):4d}  ({100*(pc>0).mean():.0f} %)")
    print(f"      con mas del +4 % ................. {int((pc>4).sum()):4d}  ({100*(pc>4).mean():.0f} %)")
    print(f"      con mas del +8 % (pasan la fase 1)  {int((pc>8).sum()):4d}  ({100*(pc>8).mean():.0f} %)")
    print(f"      media real de la estrategia ...... {pc.mean():+.1f} %")
    # rachas: quien encadena 5 ganadoras seguidas alguna vez
    return pc

print("="*72)
print("CUÁNTAS CAPTURAS DE TP PRODUCE UNA ESTRATEGIA QUE PIERDE DINERO")
print("="*72)
simula("A · regla del nivel de Asia (medida: -0,685 R por sesión, PERDEDORA)",
       lambda n: RNG.choice(porSesion, size=n, replace=True))
simula("B · una moneda perfecta con coste (33,3 % a 1:2, stop de 6 pips)", moneda)

print("\n" + "="*72)
print("Y LAS RACHAS DE OPERACIONES SUELTAS")
print("="*72)
for ac, et in ((1/3, "moneda a 1:2 (33,3 %)"), (0.222, "la regla de Asia (22,2 % medido)")):
    for k in (3, 5, 8):
        p = ac**k
        print(f"  {et:34s} · {k} TP seguidos: 1 de cada {1/p:,.0f} intentos"
              f"  ·  en 500 personas x 30 operaciones: {500*30*p:.0f} veces al mes")
