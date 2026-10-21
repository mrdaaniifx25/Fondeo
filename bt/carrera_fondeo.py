"""La carrera de fondeo con el sistema real de bt/sistema.py.

No es un modelo con ventaja inventada: los rendimientos mensuales salen por
remuestreo de los 632 meses medidos. Se simula reto, cuenta fondeada, muerte
de la cuenta y recompra, durante 3 anios.
"""
import numpy as np, pandas as pd
from math import sqrt, erf
exec(open("bt/sistema.py").read().split('print("="*112); print("EL SISTEMA")')[0])

j = pd.concat([M.rename("m"), K.rename("k")], axis=1).dropna()
BASE = (0.5*j.m + 0.5*j.k).to_numpy()          # en unidades de ruido
dd_base = float(np.min(np.cumsum(BASE) - np.maximum.accumulate(np.cumsum(BASE))))
print(f"serie base: {len(BASE)} meses, peor caida {dd_base:.2f} unidades\n")

rng = np.random.default_rng(7)
MESES, SIMS = 36, 20000
F1, F2, DD, DIARIO, REPARTO = 0.08, 0.04, 0.10, 0.05, 0.80

def carrera(escala, cuenta, cuota, reembolso=True):
    """escala: 10/|dd| pone la peor caida historica en el 10 %."""
    r = BASE*escala/100.0                      # rendimiento mensual en tanto por uno
    vol_d = r.std()/sqrt(21)                   # volatilidad diaria implicita
    p_dia = 21*0.5*(1 - erf(DIARIO/(vol_d*sqrt(2))))   # P(un dia < -5 %) al mes
    ret = []; pagos = []; vivos = 0
    for _ in range(SIMS):
        m = 0; gastado = 0.0; cobrado = 0.0; primer_pago = True
        while m < MESES:
            gastado += cuota; fase, pico, bal = 1, 0.0, 0.0
            # --- reto ---
            while m < MESES:
                x = rng.choice(r); m += 1
                if rng.random() < p_dia: bal = -DD; break      # limite diario
                bal += x
                if bal <= -DD: break
                obj = F1 if fase == 1 else F2
                if bal >= obj:
                    if fase == 1: fase, bal = 2, 0.0
                    else: break
            if bal <= -DD: continue            # reventado en el reto, otro
            if m >= MESES: break
            # --- cuenta fondeada ---
            bal = 0.0
            while m < MESES:
                x = rng.choice(r); m += 1
                if rng.random() < p_dia: bal = -DD; break
                bal += x
                if bal <= -DD: break
                if bal > 0:                     # retira todo lo que pase de cero
                    pago = bal*cuenta*REPARTO
                    cobrado += pago; bal = 0.0
                    if primer_pago and reembolso: cobrado += cuota; primer_pago = False
            if bal > -DD: vivos += 1; break     # sigue viva al final
        ret.append(cobrado - gastado); pagos.append(cobrado)
    ret = np.array(ret)
    return dict(neto=ret.mean(), mediana=np.median(ret), gana=100*(ret > 0).mean(),
                mes=ret.mean()/MESES, viva=100*vivos/SIMS, p_dia=p_dia)

for cuenta, cuota in ((50000, 250.0), (100000, 500.0), (200000, 1000.0)):
    print("="*112)
    print(f"CUENTA DE {cuenta:,} EUR   ·   reto {cuota:.0f} EUR   ·   3 anios   ·   {SIMS:,} carreras")
    print("="*112)
    print(f"{'escala':>7}{'peor caída hist.':>18}{'%/año':>9}{'sigue viva':>12}"
          f"{'% que gana':>12}{'neto medio':>13}{'€/mes':>9}")
    print("-"*90)
    for mult in (0.5, 1.0, 1.5, 2.0, 3.0):
        esc = mult*10/abs(dd_base)
        r = carrera(esc, cuenta, cuota)
        anual = BASE.mean()*12*esc
        print(f"{mult:>6.1f}x{10*mult:>17.0f} %{anual:>8.2f}%{r['viva']:>11.1f}%"
              f"{r['gana']:>11.1f}%{r['neto']:>+12,.0f}€{r['mes']:>+8.0f}€")
    print()

# ============ LOS DOS CONTROLES QUE DECIDEN SI LO DE ARRIBA ES REAL ==========
print("="*112)
print("CONTROL 1 · LA MISMA SIMULACION CON VENTAJA EXACTAMENTE CERO")
print("="*112)
print("  Mismos rendimientos, misma volatilidad, pero con la media puesta a cero.")
print("  Si esto tambien da dinero, la simulacion mide la asimetria de la")
print("  fondeadora (retiras las ganancias, el limite se queda quieto) y NO el sistema.\n")
BASE_REAL = BASE.copy()
BASE = BASE_REAL - BASE_REAL.mean()
print(f"{'escala':>7}{'%/año':>9}{'sigue viva':>12}{'% que gana':>12}{'neto medio':>13}{'€/mes':>9}")
print("-"*65)
for mult in (1.0, 1.5, 2.0, 3.0):
    esc = mult*10/abs(dd_base); r = carrera(esc, 100000, 500.0)
    print(f"{mult:>6.1f}x{BASE.mean()*12*esc:>8.2f}%{r['viva']:>11.1f}%{r['gana']:>11.1f}%"
          f"{r['neto']:>+12,.0f}€{r['mes']:>+8.0f}€")
BASE = BASE_REAL

print("\n" + "="*112)
print("CONTROL 2 · CON PERDIDA MAXIMA *DINAMICA* (la que usan casi todas hoy)")
print("="*112)
print("  El limite del 10 % se mide desde el PICO de balance, no desde el inicio.")
print("  Eso mata el mecanismo de retirar y volver a empezar con el colchon entero.\n")

def carrera_trail(escala, cuenta, cuota, cero=False):
    r = (BASE - (BASE.mean() if cero else 0))*escala/100.0
    vol_d = r.std()/sqrt(21)
    p_dia = 21*0.5*(1 - erf(DIARIO/(vol_d*sqrt(2))))
    ret = []; vivos = 0
    for _ in range(SIMS):
        m = 0; gastado = 0.0; cobrado = 0.0; primer = True
        while m < MESES:
            gastado += cuota; fase, bal = 1, 0.0
            while m < MESES:
                x = rng.choice(r); m += 1
                if rng.random() < p_dia: bal = -DD; break
                bal += x
                if bal <= -DD: break
                if bal >= (F1 if fase == 1 else F2):
                    if fase == 1: fase, bal = 2, 0.0
                    else: break
            if bal <= -DD: continue
            if m >= MESES: break
            bal, pico = 0.0, 0.0
            while m < MESES:
                x = rng.choice(r); m += 1
                if rng.random() < p_dia: bal = pico - DD; break
                bal += x; pico = max(pico, bal)
                if bal <= pico - DD: break
                if bal > 0:
                    cobrado += bal*cuenta*REPARTO
                    bal = 0.0; pico = 0.0      # retirar reinicia el balance, no el historial
                    if primer: cobrado += cuota; primer = False
            if bal > pico - DD: vivos += 1; break
        ret.append(cobrado - gastado)
    ret = np.array(ret)
    return ret.mean(), 100*(ret > 0).mean(), 100*vivos/SIMS

print(f"{'escala':>7}{'':>4}{'con el sistema':>28}{'':>6}{'con ventaja CERO':>24}")
print(f"{'':>11}{'€/mes':>10}{'% gana':>10}{'viva':>8}{'':>6}{'€/mes':>10}{'% gana':>10}{'viva':>8}")
print("-"*76)
for mult in (1.0, 1.5, 2.0, 3.0):
    esc = mult*10/abs(dd_base)
    a, ga, va = carrera_trail(esc, 100000, 500.0, cero=False)
    b, gb, vb = carrera_trail(esc, 100000, 500.0, cero=True)
    print(f"{mult:>6.1f}x{'':>4}{a/MESES:>+9.0f}€{ga:>9.1f}%{va:>7.1f}%{'':>6}"
          f"{b/MESES:>+9.0f}€{gb:>9.1f}%{vb:>7.1f}%")

print("\n" + "="*112)
print("LA DISTRIBUCION · cuenta de 100.000, escala 2x, perdida maxima dinamica, 3 anios")
print("="*112)
def detalle(escala, cuenta, cuota):
    r = BASE*escala/100.0
    vol_d = r.std()/sqrt(21); p_dia = 21*0.5*(1-erf(DIARIO/(vol_d*sqrt(2))))
    ret, retos, meses_reto = [], [], []
    for _ in range(SIMS):
        m = 0; gast = 0.0; cob = 0.0; primer = True; nret = 0
        while m < MESES:
            gast += cuota; nret += 1; fase, bal = 1, 0.0; m0 = m
            while m < MESES:
                x = rng.choice(r); m += 1
                if rng.random() < p_dia: bal = -DD; break
                bal += x
                if bal <= -DD: break
                if bal >= (F1 if fase == 1 else F2):
                    if fase == 1: fase, bal = 2, 0.0
                    else: meses_reto.append(m-m0); break
            if bal <= -DD: continue
            if m >= MESES: break
            bal, pico = 0.0, 0.0
            while m < MESES:
                x = rng.choice(r); m += 1
                if rng.random() < p_dia: bal = pico-DD; break
                bal += x; pico = max(pico, bal)
                if bal <= pico-DD: break
                if bal > 0:
                    cob += bal*cuenta*REPARTO; bal = 0.0; pico = 0.0
                    if primer: cob += cuota; primer = False
            if bal > pico-DD: break
        ret.append(cob-gast); retos.append(nret)
    return np.array(ret), np.array(retos), np.array(meses_reto)

R3, NR, MR = detalle(2.0*10/abs(dd_base), 100000, 500.0)
print(f"  {'percentil':<14}{'neto en 3 años':>18}{'€/mes':>10}")
print("  " + "-"*44)
for q in (5, 10, 25, 50, 75, 90, 95):
    v = np.percentile(R3, q)
    print(f"  {'p'+str(q):<14}{v:>+17,.0f}€{v/MESES:>+9.0f}€")
print(f"\n  media            {R3.mean():>+17,.0f}€{R3.mean()/MESES:>+9.0f}€")
print(f"  carreras que ganan dinero: {100*(R3>0).mean():.1f} %")
print(f"  retos comprados, mediana:  {int(np.median(NR))}  (media {NR.mean():.1f})")
print(f"  meses en pasar el reto, mediana: {np.median(MR):.0f}")
print(f"\n  lo que se arriesga de verdad: {500*NR.mean():,.0f} € de cuotas de media.")

print("\n" + "="*112)
print("EL CASO MALO · la misma carrera con SOLO los meses de 2013-2026")
print("="*112)
print("  Es el tramo flojo: Sharpe +0,45 frente a +1,00 de la muestra completa.")
print("  Si el futuro se parece a los ultimos trece anios y no a los cincuenta")
print("  anteriores, esto es lo que sale.\n")
serie = (0.5*j.m + 0.5*j.k)
REC = serie[serie.index.year >= 2013].to_numpy()
dd_rec = float(np.min(np.cumsum(REC) - np.maximum.accumulate(np.cumsum(REC))))
BASE_G = BASE.copy(); BASE = REC
print(f"{'escala':>8}{'%/año':>9}{'sigue viva':>12}{'% que gana':>12}{'mediana €/mes':>16}{'media €/mes':>14}")
print("-"*72)
for mult in (1.0, 1.5, 2.0, 3.0):
    esc = mult*10/abs(dd_base)
    Rx, _, _ = detalle(esc, 100000, 500.0)
    a, ga, va = carrera_trail(esc, 100000, 500.0)
    print(f"{mult:>7.1f}x{REC.mean()*12*esc:>8.2f}%{va:>11.1f}%{100*(Rx>0).mean():>11.1f}%"
          f"{np.median(Rx)/MESES:>+15.0f}€{Rx.mean()/MESES:>+13.0f}€")
BASE = BASE_G
