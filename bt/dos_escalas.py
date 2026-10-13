"""Dos escalas distintas: agresiva en el reto, normal una vez fondeado.

Durante el reto lo unico que se arriesga es la cuota. Una vez fondeado se
arriesga un activo que produce. Son apuestas distintas y no deben llevar el
mismo tamanio. Se busca la escala de reto que minimiza el TIEMPO sin destruir
la probabilidad de pasar.
"""
import numpy as np, pandas as pd
from math import sqrt, erf
exec(open("bt/sistema.py").read().split('print("="*112); print("EL SISTEMA")')[0])
j = pd.concat([M.rename("m"), K.rename("k")], axis=1).dropna()
SER = 0.5*j.m + 0.5*j.k
BASE = SER.to_numpy(); REC = SER[SER.index.year >= 2013].to_numpy()
dd = abs(float(np.min(np.cumsum(BASE)-np.maximum.accumulate(np.cumsum(BASE)))))
rng = np.random.default_rng(77)
SIMS, TAM, CUOTA, REP = 20000, 10000, 89.0, 0.80
# reglas FundingPips, dos fases
F1, F2, DDL, DIA = 0.08, 0.05, 0.08, 0.04
F1U, DDU = 0.10, 0.06          # una fase

def pdia(r): 
    v = r.std()/sqrt(21)
    return min(1.0, 21*0.5*(1-erf(DIA/(v*sqrt(2)))))

def reto(serie, esc, fases=2, tope=60):
    """devuelve (pasa, meses) de UN intento de reto."""
    r = serie*esc/100.0; pd_ = pdia(r)
    f1, f2, lim = (F1, F2, DDL) if fases == 2 else (F1U, None, DDU)
    fase, bal, m = 1, 0.0, 0
    while m < tope:
        m += 1
        if rng.random() < pd_: return False, m
        bal += rng.choice(r)
        if bal <= -lim: return False, m
        if fase == 1 and bal >= f1:
            if fases == 1: return True, m
            fase, bal = 2, 0.0
        elif fase == 2 and bal >= f2: return True, m
    return False, m

for et_s, serie in (("MUESTRA COMPLETA", BASE), ("SOLO 2013-2026", REC)):
    for fases, etf in ((2, "DOS FASES (+8 % y +5 %, caída 8 %)"),
                       (1, "UNA FASE (+10 %, caída 6 %)")):
        print("="*112)
        print(f"{etf} · {et_s} · {SIMS:,} intentos por celda")
        print("="*112)
        print(f"{'escala':>7}{'caída hist.':>13}{'%/año':>9}{'pasa':>9}{'meses (mediana)':>17}"
              f"{'meses (p75)':>13}{'coste por':>12}{'meses hasta':>14}")
        print(f"{'':>7}{'':>13}{'':>9}{'':>9}{'de los que pasan':>17}{'':>13}"
              f"{'fondearse':>12}{'fondearse':>14}")
        print("-"*96)
        for mult in (2, 4, 6, 8, 10, 14, 20):
            esc = mult*10/dd
            res = [reto(serie, esc, fases) for _ in range(SIMS)]
            ok = [m for p, m in res if p]; pct = 100*len(ok)/SIMS
            if not ok: 
                print(f"{mult:>6}x{10*mult:>12.0f}%{serie.mean()*12*esc:>8.1f}%{pct:>8.1f}%"
                      f"{'—':>17}{'—':>13}{'—':>12}{'—':>14}"); continue
            med = np.median(ok); p75 = np.percentile(ok, 75)
            intentos = 1/(pct/100)
            coste = intentos*CUOTA
            # tiempo esperado hasta fondearse: intentos fallidos + el bueno
            fall = [m for p, m in res if not p]
            t_fall = np.mean(fall) if fall else 0
            t_total = (intentos-1)*t_fall + med
            print(f"{mult:>6}x{10*mult:>12.0f}%{serie.mean()*12*esc:>8.1f}%{pct:>8.1f}%"
                  f"{med:>16.0f}m{p75:>12.0f}m{coste:>11.0f}€{t_total:>13.0f}m")
        print()
