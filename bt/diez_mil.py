"""10.000 EUR: la cuenta fondeada como billete de loteria con esperanza positiva.

La clave que no habia usado: en una cuenta fondeada la perdida esta LIMITADA
a la cuota. Asi que apalancar hasta reventarla no es irracional si el valor
esperado por reto es positivo. Se mide con los 632 meses reales.
"""
import numpy as np, pandas as pd
from math import sqrt, erf
exec(open("bt/sistema.py").read().split('print("="*112); print("EL SISTEMA")')[0])
j = pd.concat([M.rename("m"), K.rename("k")], axis=1).dropna()
SER = 0.5*j.m + 0.5*j.k
BASE = SER.to_numpy()
REC  = SER[SER.index.year >= 2013].to_numpy()
dd = abs(float(np.min(np.cumsum(BASE)-np.maximum.accumulate(np.cumsum(BASE)))))
rng = np.random.default_rng(11)
MESES, SIMS, F1, F2, DD, DIARIO, REP = 36, 30000, 0.08, 0.04, 0.10, 0.05, 0.80

def carrera(r, cuenta, cuota, meses=MESES):
    vol_d = r.std()/sqrt(21)
    p_dia = min(1.0, 21*0.5*(1-erf(DIARIO/(vol_d*sqrt(2)))))
    net, pag, nre = [], [], []
    for _ in range(SIMS):
        m = 0; g = 0.0; c = 0.0; primer = True; k = 0
        while m < meses:
            g += cuota; k += 1; fase, bal = 1, 0.0
            while m < meses:                      # reto
                m += 1
                if rng.random() < p_dia: bal = -DD; break
                bal += rng.choice(r)
                if bal <= -DD: break
                if bal >= (F1 if fase == 1 else F2):
                    if fase == 1: fase, bal = 2, 0.0
                    else: break
            if bal <= -DD: continue
            if m >= meses: break
            bal, pico = 0.0, 0.0
            while m < meses:                      # fondeada, caida dinamica
                m += 1
                if rng.random() < p_dia: bal = pico-DD; break
                bal += rng.choice(r); pico = max(pico, bal)
                if bal <= pico-DD: break
                if bal > 0:
                    c += bal*cuenta*REP; bal = 0.0; pico = 0.0
                    if primer: c += cuota; primer = False
            if bal > pico-DD: break
        net.append(c-g); pag.append(c); nre.append(k)
    return np.array(net), np.array(pag), np.array(nre)

for et, S in (("MUESTRA COMPLETA (1971-2026)", BASE), ("SOLO 2013-2026, el tramo flojo", REC)):
    print("="*118)
    print(f"CUENTA DE 10.000 EUR · reto 89 EUR · 3 años · {SIMS:,} carreras · {et}")
    print("="*118)
    print(f"{'escala':>7}{'caída hist.':>13}{'%/año':>9}{'retos':>8}{'% gana':>9}"
          f"{'mediana €/mes':>15}{'media €/mes':>13}{'p75':>8}{'p90':>8}")
    print("-"*90)
    for mult in (1, 2, 4, 6, 8, 12, 16):
        r = S*(mult*10/dd)/100.0
        n, p, k = carrera(r, 10000, 89.0)
        print(f"{mult:>6}x{10*mult:>12.0f}%{S.mean()*12*(mult*10/dd):>8.1f}%"
              f"{k.mean():>8.1f}{100*(n>0).mean():>8.1f}%{np.median(n)/MESES:>+14.0f}€"
              f"{n.mean()/MESES:>+12.0f}€{np.percentile(n,75)/MESES:>+7.0f}€"
              f"{np.percentile(n,90)/MESES:>+7.0f}€")
    print()
