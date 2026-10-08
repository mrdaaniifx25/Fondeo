"""¿Prueba algo un papel de payout?

Se simula la carrera de dos años de una persona que compra retos de fondeo uno
detrás de otro. Cuando revienta una cuenta, compra otra. Cobra cuando cobra.
Se cuenta cuánta gente acaba con un payout REAL en la mano -- y se compara al
que no tiene ninguna ventaja con uno que sí la tiene, para ver si el papel
distingue al uno del otro.

Reglas tipo FTMO sobre cuenta de 10.000:
  fase 1 +10 %, fase 2 +5 %, pérdida diaria 5 %, pérdida total 10 %,
  reparto 80 %, retira cada +5 %. Reto 89 EUR.
"""
import numpy as np

CUENTA, PRECIO = 10_000.0, 89.0
OBJ1, OBJ2, RETIRA = 0.10, 0.05, 0.05
DIARIA, TOTAL, REPARTO = 0.05, 0.10, 0.80
RR, COSTE_R = 2.0, 0.07
DIAS, OPS_DIA = 500, 3          # dos años de mercado
N = 200_000

def carrera(p_gana, riesgo, semilla):
    rng = np.random.default_rng(semilla)
    saldo = np.full(N, CUENTA); meta = np.full(N, CUENTA*(1+OBJ1))
    fase  = np.zeros(N, np.int8)          # 0 fase1, 1 fase2, 2 fondeada
    pagado = np.full(N, PRECIO); cobrado = np.zeros(N); hubo = np.zeros(N, bool)
    fondeo = np.zeros(N, bool)
    suelo = CUENTA*(1-TOTAL); lim_dia = DIARIA*CUENTA
    gan, per = RR - COSTE_R, -1.0 - COSTE_R
    for _ in range(DIAS):
        dia0 = saldo.copy(); vivo = np.ones(N, bool)
        for _ in range(OPS_DIA):
            r = np.where(rng.random(N) < p_gana, gan, per)
            saldo = np.where(vivo, saldo + r*riesgo*CUENTA, saldo)
            rompe = vivo & ((saldo <= suelo) | (saldo <= dia0 - lim_dia))
            llega = vivo & ~rompe & (saldo >= meta)
            if rompe.any():                      # revienta -> compra otro reto
                pagado += PRECIO*rompe
                saldo = np.where(rompe, CUENTA, saldo)
                meta  = np.where(rompe, CUENTA*(1+OBJ1), meta)
                fase  = np.where(rompe, 0, fase); vivo &= ~rompe
            if llega.any():
                cobra = llega & (fase == 2)
                cobrado += np.where(cobra, (saldo-CUENTA)*REPARTO, 0.0)
                hubo |= cobra
                fondeo |= llega & (fase == 1)
                fase = np.where(llega & (fase < 2), fase+1, fase)
                meta = np.where(llega, CUENTA*(1 + np.where(fase == 0, OBJ1,
                                np.where(fase == 1, OBJ2, RETIRA))), meta)
                saldo = np.where(llega, CUENTA, saldo); vivo &= ~llega
            if not vivo.any(): break
    return pagado, cobrado, hubo, fondeo

E = lambda p: p*(RR-COSTE_R) + (1-p)*(-1.0-COSTE_R)
P0 = 1/(1+RR)                      # 33,3 % -- el precio justo. VENTAJA CERO.
P1 = (0.10 + 1.0 + COSTE_R)/(RR + 1.0)   # el que gana +0,10 R por operación

print(f"  sin ventaja : acierta {100*P0:.1f} % a 1:2  ->  {E(P0):+.3f} R por operación")
print(f"  con ventaja : acierta {100*P1:.1f} % a 1:2  ->  {E(P1):+.3f} R por operación")
print(f"  (2 años, {DIAS*OPS_DIA:,} operaciones, {N:,} personas por celda)\n")
print(f"{'':<14}{'riesgo':>7} {'llega a fondearse':>18} {'ENSEÑA PAYOUT':>15} "
      f"{'pagado':>9} {'cobrado':>9} {'neto medio':>12} {'% que gana':>11}")
print("-"*104)
for nom, p in (("sin ventaja", P0), ("con ventaja", P1)):
    for i, riesgo in enumerate((0.01, 0.02, 0.05)):
        pg, cb, hb, fd = carrera(p, riesgo, 100+i)
        neto = cb - pg
        print(f"{nom if i==0 else '':<14}{100*riesgo:>6.0f}% {100*fd.mean():>17.1f}% "
              f"{100*hb.mean():>14.1f}% {pg.mean():>8,.0f}€ {cb.mean():>8,.0f}€ "
              f"{neto.mean():>+11,.0f}€ {100*(neto>0).mean():>10.1f}%")
    print()
