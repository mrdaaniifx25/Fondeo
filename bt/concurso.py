"""Que produce un concurso de 400 traders con ventaja EXACTAMENTE CERO.

Datos del propio video: 400+ participantes, 20 dias, Bitcoin plano
(maximo +6,25 %, cierre -0,20 %). Anunciado: 1o +186,27 %, 2o +61,49 %.
"""
import numpy as np
rng = np.random.default_rng(31)
N, DIAS, SIMS, VOL_D = 400, 20, 4000, 0.025

print("CONCURSO DE 400 TRADERS · 20 DIAS · VENTAJA EXACTAMENTE CERO")
print("  Bitcoin plano. Cada uno elige su apalancamiento.\n")
print(f"{'apalanc.':>9}{'1o':>13}{'2o':>12}{'10o':>12}{'mediana':>12}{'arruinados':>13}")
print("-"*72)
for ap in (1, 2, 3, 5, 10, 20):
    tops, seg, dec, med, rev = [], [], [], [], []
    for _ in range(SIMS):
        r = rng.normal(0, VOL_D*ap, size=(N, DIAS))
        eq = np.cumprod(1+np.clip(r, -0.95, None), axis=1)
        arru = eq.min(axis=1) < 0.1
        fin = np.where(arru, 0.0, eq[:, -1])
        o = np.sort(fin)[::-1]
        tops.append(o[0]); seg.append(o[1]); dec.append(o[9])
        med.append(np.median(fin)); rev.append(100*arru.mean())
    f = lambda v: f"{100*(np.mean(v)-1):+.1f} %"
    print(f"{ap:>7}x {f(tops):>13}{f(seg):>12}{f(dec):>12}{f(med):>12}{np.mean(rev):>11.0f} %")
print("\n  Anunciado en el video:  1o +186,3 %   ·   2o +61,5 %")
print("  Con 3x de apalancamiento y ventaja cero sale 1o +154 % y 2o +129 %.\n")

print("="*72)
print("'SIETE DE LOS DIEZ PRIMEROS USABAN MIS ESTRATEGIAS'")
print("="*72)
print("  Cuantos alumnos suyos se esperan en el top 10 solo por proporcion:\n")
for p in (0.3, 0.5, 0.6, 0.7, 0.8):
    print(f"    si eran el {100*p:>3.0f} % de los 400  ->  {10*p:>4.1f} en el top 10")
print("\n  El video no dice que fraccion eran alumnos suyos. Sin ese dato,")
print("  'siete de diez' no distingue nada.")
