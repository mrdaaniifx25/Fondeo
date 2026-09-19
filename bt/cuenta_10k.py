"""Que hace una cuenta de 10.000 EUR con la estrategia AMD+FVG medida.

Se usa la distribucion REAL de R neta de las 587 operaciones de EURUSD H1,
no una aproximacion. Coste 1,43 pips.
"""
import numpy as np, pandas as pd
from math import sqrt
exec(open("bt/amd_fvg.py").read().split("for tf, mins, n in")[0])

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
D = corre(velas(m1, 60), 8)
F = D[D.fvg].copy()
F["rgoP"] = F.rgo / 1e-4
F["Rn"] = F.Rb - 1.43 / F.rgoP
R = F.Rn.to_numpy()

print(f"las {len(R)} operaciones reales de EURUSD H1 con FVG")
print(f"  acierto {100*F.gana.mean():.1f} %   riesgo mediano {F.rgoP.median():.1f} pips")
print(f"  R neta: media {R.mean():+.4f}   desviacion {R.std(ddof=1):.4f}")
print(f"  la peor: {R.min():+.2f}   la mejor: {R.max():+.2f}")
print(f"  ritmo: {len(R)/5:.0f} operaciones al año, unas {len(R)/5/12:.1f} al mes\n")

CUENTA, OPS = 10000.0, 120        # un año
rng = np.random.default_rng(7)
N = 20000

print(f"CUENTA DE {CUENTA:,.0f} EUR  ·  un año  ·  {OPS} operaciones")
print(f"{'riesgo':>8}{'€/op':>8}{'lotes':>7}{'final medio':>13}{'mediana':>10}"
      f"{'peor 5%':>10}{'mejor 5%':>10}{'caida max':>11}{'P(pierde)':>11}")
for pct in (0.005, 0.01, 0.02, 0.05):
    fin = np.empty(N); dd = np.empty(N)
    for s in range(N):
        eq = CUENTA; pico = eq; peor = 0.0
        for _ in range(OPS):
            eq += pct * CUENTA * R[rng.integers(len(R))]   # riesgo fijo en euros
            if eq <= 0: eq = 0.0; break
            pico = max(pico, eq); peor = max(peor, (pico - eq) / pico)
        fin[s] = eq; dd[s] = peor
    eur = pct * CUENTA
    lotes = eur / (F.rgoP.median() * 8.60)
    print(f"{100*pct:>7.1f}%{eur:>8.0f}{lotes:>7.2f}{fin.mean():>13,.0f}"
          f"{np.median(fin):>10,.0f}{np.percentile(fin,5):>10,.0f}"
          f"{np.percentile(fin,95):>10,.0f}{100*np.median(dd):>10.1f}%"
          f"{100*(fin < CUENTA).mean():>10.1f}%")

print(f"\ny con 5 lotes, que es lo que preguntaste antes:")
eur5 = 5 * F.rgoP.median() * 8.60
print(f"  riesgo por operacion: {eur5:,.0f} EUR  =  {100*eur5/CUENTA:.0f} % de la cuenta")
fin = np.empty(N)
for s in range(N):
    eq = CUENTA
    for k in range(OPS):
        eq += eur5 * R[rng.integers(len(R))]
        if eq <= 0: eq = 0.0; break
    fin[s] = eq
print(f"  revienta la cuenta: {100*(fin <= 0).mean():.1f} % de las veces")
print(f"  acaba por debajo de 10.000: {100*(fin < CUENTA).mean():.1f} %")
