"""¿Cuánto se puede sacar, de verdad, de 10.000 EUR?

Se usa lo MEJOR que se ha medido en el proyecto: el CRT en H12.
  bruta +0,125 R · neta +0,072 R · 46,1 % de acierto · R:R mediano 1,38
  471 operaciones al anio repartidas entre 5 instrumentos
  IC 95 % de la neta: [-0,027, +0,136]  <- el cero esta DENTRO

Se simula el anio 20.000 veces con la ventaja en el centro y en los dos
extremos del intervalo, para enseñar el abanico y no un numero solo.
"""
import numpy as np

CUENTA, N, OPS = 10_000, 20_000, 471
P, RR = 0.461, 1.38
rng = np.random.default_rng(101)

def anio(ventaja, riesgo, n=N):
    """ajusta el acierto para que la neta media sea 'ventaja' con ese R:R"""
    p = (ventaja + 1) / (RR + 1)
    fin = np.full(n, CUENTA); pico = np.full(n, CUENTA); dd = np.zeros(n)
    for _ in range(OPS):
        r = np.where(rng.random(n) < p, RR, -1.0)
        fin = fin * (1 + r*riesgo)
        pico = np.maximum(pico, fin)
        dd = np.maximum(dd, (pico-fin)/pico)
    return fin, dd

print(f"Lo mejor medido: CRT en H12, {OPS} operaciones al anio entre 5 instrumentos")
print(f"IC 95 % de la ventaja: [-0,027, +0,072, +0,136]\n")
for riesgo in (0.005, 0.01, 0.02):
    print(f"{'':>3}RIESGO {100*riesgo:.1f} % POR OPERACION")
    print(f"{'ventaja':>22} {'mediana fin':>13} {'al mes':>9} {'caida max':>11} "
          f"{'anios que pierden':>18} {'revienta (-10%)':>16}")
    print("   " + "-"*95)
    for nom, v in (("peor del IC  -0,027", -0.027), ("el centro    +0,072", 0.072),
                   ("mejor del IC +0,136", 0.136)):
        fin, dd = anio(v, riesgo)
        med = np.median(fin)
        print(f"{nom:>22} {med:>12,.0f}€ {(med-CUENTA)/12:>+8,.0f}€ "
              f"{100*np.median(dd):>10.1f}% {100*(fin < CUENTA).mean():>17.1f}% "
              f"{100*(dd > 0.10).mean():>15.1f}%")
    print()
