"""¿Que hace falta REALMENTE para pasar un reto de fondeo?

Monte Carlo con la distribucion de R real de la mejor estrategia encontrada
(CRT + order block + DOL diario), y con versiones de ventaja distinta, contra
las reglas tipicas: objetivo +10%, perdida maxima total 10%, diaria 5%.
"""
import numpy as np, pandas as pd

tr = pd.read_csv("data/trades_final.csv")
R = tr.R.to_numpy()
print(f"Distribucion real: {len(R)} operaciones | R medio {R.mean():+.4f} "
      f"| desviacion {R.std():.3f} | ~54 al ano\n")

def simula(R_pool, riesgo, n=20000, objetivo=0.10, dd_max=0.10, tope_ops=400, semilla=0):
    rng = np.random.default_rng(semilla)
    pasa = falla = expira = 0
    ops_pasar = []
    for _ in range(n):
        eq = 1.0; pico = 1.0
        for k in range(tope_ops):
            eq *= (1 + riesgo*rng.choice(R_pool))
            pico = max(pico, eq)
            if eq <= 1 - dd_max: falla += 1; break
            if eq >= 1 + objetivo: pasa += 1; ops_pasar.append(k+1); break
        else:
            expira += 1
    return pasa/n, falla/n, expira/n, (np.mean(ops_pasar) if ops_pasar else np.nan)

print("=== CON LA VENTAJA REAL MEDIDA (R medio +0.170 neto) ===")
print(f"{'riesgo/op':>10s} {'pasa':>7s} {'quiebra':>8s} {'expira':>7s} {'ops si pasa':>12s} {'meses aprox':>12s}")
for riesgo in (0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02):
    p,f,e,o = simula(R, riesgo)
    meses = o/54*12 if o==o else float('nan')
    print(f"{100*riesgo:>9.2f}% {100*p:>6.1f}% {100*f:>7.1f}% {100*e:>6.1f}% "
          f"{o:>12.0f} {meses:>12.1f}")

print("\n=== SENSIBILIDAD A LA VENTAJA: ¿y si la real fuera menor? ===")
print("   (se escala el R medio manteniendo la forma de la distribucion)")
print(f"{'R medio':>9s} {'riesgo 0.5%':>12s} {'riesgo 1%':>12s} {'riesgo 2%':>12s}")
for factor, etiqueta in ((0.0,"0.000"), (0.5,"0.085"), (1.0,"0.170"), (1.5,"0.255")):
    Rf = (R - R.mean()) + R.mean()*factor
    fila = []
    for riesgo in (0.005, 0.01, 0.02):
        p,_,_,_ = simula(Rf, riesgo, n=10000)
        fila.append(f"{100*p:>11.1f}%")
    print(f"{etiqueta:>9s} " + " ".join(fila))

print("\n=== LA CUENTA QUE NADIE HACE: coste esperado de aprobar ===")
print("   Suponiendo 100 EUR por intento de reto:")
for riesgo in (0.005, 0.01, 0.02):
    p,_,_,_ = simula(R, riesgo, n=20000)
    if p > 0.01:
        print(f"   riesgo {100*riesgo:.1f}%/op -> pasa {100*p:.1f}% -> "
              f"{1/p:.1f} intentos de media -> {100/p:.0f} EUR por cuenta lograda")

print("\n=== VENTAJA CERO: el caso de las otras tres estrategias ===")
R0 = (R - R.mean())
for riesgo in (0.005, 0.01, 0.02):
    p,f,e,_ = simula(R0, riesgo, n=20000)
    print(f"   riesgo {100*riesgo:.1f}%/op -> pasa {100*p:.1f}% | quiebra {100*f:.1f}% | expira {100*e:.1f}%")
