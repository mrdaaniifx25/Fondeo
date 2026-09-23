"""EL PLAN. Cuantas cuentas, de que tamanio, en que orden y en cuanto tiempo.

Rendimientos por remuestreo de los 632 meses medidos. Se simula la carrera
entera: comprar retos, pasarlos, cobrar, reinvertir en mas cuentas hasta
llegar al objetivo, y a partir de ahi retirar todo.
"""
import numpy as np, pandas as pd
from math import sqrt, erf
exec(open("bt/sistema.py").read().split('print("="*112); print("EL SISTEMA")')[0])
j = pd.concat([M.rename("m"), K.rename("k")], axis=1).dropna()
SER = 0.5*j.m + 0.5*j.k
BASE = SER.to_numpy()
REC  = SER[SER.index.year >= 2013].to_numpy()
dd = abs(float(np.min(np.cumsum(BASE)-np.maximum.accumulate(np.cumsum(BASE)))))
rng = np.random.default_rng(2026)

F1, F2, DD, DIARIO, REP = 0.08, 0.04, 0.10, 0.05, 0.80
# precios tipicos de reto (FundingPips / FTMO), y lo que cuesta cada euro fondeado
PRECIO = {10000: 89.0, 25000: 189.0, 50000: 289.0, 100000: 489.0}
print("COSTE DE CADA EURO FONDEADO")
for c, p in PRECIO.items():
    print(f"  cuenta {c:>7,} EUR   reto {p:>6.0f} EUR   = {100*p/c:.2f} % del tamanio")
print("\n  -> las cuentas grandes son MAS BARATAS por euro fondeado.\n")

class Cuenta:
    __slots__ = ("tam","escala","fase","bal","pico","viva","refund","cobrado")
    def __init__(s, tam, escala):
        s.tam, s.escala, s.fase = tam, escala, 1
        s.bal, s.pico, s.viva, s.refund, s.cobrado = 0.0, 0.0, True, False, 0.0

def simula(objetivo_mes, tam, escala, presupuesto, max_cuentas, meses, serie, sims=4000):
    r = serie*escala/100.0
    vol_d = r.std()/sqrt(21)
    p_dia = min(1.0, 21*0.5*(1-erf(DIARIO/(vol_d*sqrt(2)))))
    cuota = PRECIO[tam]
    llega, tiempos, gastos, netos, rentas = 0, [], [], [], []
    for _ in range(sims):
        caja = presupuesto; gastado = 0.0; cobrado = 0.0
        cuentas = []; fondeadas_max = 0; t_obj = None; renta12 = []
        for m in range(meses):
            # --- comprar retos con lo que haya en caja ---
            while caja >= cuota and len(cuentas) < max_cuentas:
                caja -= cuota; gastado += cuota
                cuentas.append(Cuenta(tam, escala))
            mes_cobrado = 0.0
            for c in cuentas:
                if not c.viva: continue
                if rng.random() < p_dia: c.viva = False; continue
                c.bal += rng.choice(r); c.pico = max(c.pico, c.bal)
                lim = -DD if c.fase <= 2 else c.pico - DD
                if c.bal <= lim: c.viva = False; continue
                if c.fase == 1 and c.bal >= F1: c.fase, c.bal, c.pico = 2, 0.0, 0.0
                elif c.fase == 2 and c.bal >= F2: c.fase, c.bal, c.pico = 3, 0.0, 0.0
                elif c.fase == 3 and c.bal > 0:
                    pago = c.bal*c.tam*REP; c.bal, c.pico = 0.0, 0.0
                    if not c.refund: pago += cuota; c.refund = True
                    c.cobrado += pago; mes_cobrado += pago
            cuentas = [c for c in cuentas if c.viva]
            nf = sum(1 for c in cuentas if c.fase == 3)
            fondeadas_max = max(fondeadas_max, nf)
            cobrado += mes_cobrado
            renta12.append(mes_cobrado)
            if len(cuentas) < max_cuentas: caja += mes_cobrado      # reinvertir
            # objetivo: media movil de 12 meses por encima del objetivo
            if t_obj is None and len(renta12) >= 12 and np.mean(renta12[-12:]) >= objetivo_mes:
                t_obj = m+1
        if t_obj: llega += 1; tiempos.append(t_obj)
        gastos.append(gastado); netos.append(cobrado-gastado)
        rentas.append(np.mean(renta12[-12:]) if len(renta12) >= 12 else 0.0)
    return dict(pct=100*llega/sims, mediana_t=np.median(tiempos) if tiempos else np.nan,
                gasto=np.mean(gastos), neto=np.mean(netos),
                renta=np.median(rentas), renta_m=np.mean(rentas))

OBJ, MESES = 300.0, 48
for et, serie in (("MUESTRA COMPLETA", BASE), ("SOLO 2013-2026 (el tramo flojo)", REC)):
    print("="*118)
    print(f"CAMINO HASTA {OBJ:.0f} EUR/MES · escala 4x · {MESES} meses · {et}")
    print("="*118)
    print(f"{'tamaño':>9}{'presupuesto':>13}{'máx cuentas':>13}{'llega al objetivo':>19}"
          f"{'mediana meses':>15}{'gasto en retos':>16}{'renta mediana':>15}")
    print("-"*102)
    for tam, maxc, pres in ((10000, 4, 89.0), (10000, 4, 356.0), (10000, 6, 89.0),
                            (25000, 2, 189.0), (50000, 1, 289.0), (50000, 2, 578.0),
                            (100000, 1, 489.0)):
        R = simula(OBJ, tam, 4*10/dd, pres, maxc, MESES, serie)
        print(f"{tam:>9,}{pres:>12.0f}€{maxc:>13}{R['pct']:>18.1f}%"
              f"{R['mediana_t']:>15.0f}{R['gasto']:>15.0f}€{R['renta']:>14.0f}€")
    print()
