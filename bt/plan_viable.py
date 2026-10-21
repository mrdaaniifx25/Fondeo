"""¿Que ventaja hace falta para que el plan del video funcione?

El plan (partir el capital en cuentas pequenas y reinvertir) es un
multiplicador. Se barre la ventaja por operacion y se mira donde cruza.

Dos modelos de drawdown, para acotar:
  FIJO     suelo en el 90 % del inicial, siempre. Generoso: retirar beneficios
           con el suelo quieto es un trinquete.
  MOVIL    suelo = maximo alcanzado - 10 %. Estricto. Lo usan varias prop.
"""
import numpy as np
PRECIO, CUENTA = 70.0, 10_000.0
F1, F2, DD, DIA, SPLIT = 0.08, 0.05, 0.10, 0.05, 0.80
RR, COSTE_R, OPS_DIA, DIAS = 2.0, 0.07, 3, 500
N, MAX = 20_000, 8
rng = np.random.default_rng(29)

def carrera(ventaja, riesgo, movil):
    p = (ventaja + 1)/(RR + 1)
    caja = np.full(N, 210.0)
    saldo = np.zeros((N, MAX)); fase = np.full((N, MAX), -1, np.int8)
    meta = np.zeros((N, MAX)); dia0 = np.zeros((N, MAX)); pico = np.zeros((N, MAX))
    ret = np.zeros(N); comp = np.zeros(N)
    def compra():
        libre = fase < 0; idx = np.argmax(libre, 1)
        f = (caja >= PRECIO) & libre.any(1)
        caja[f] -= PRECIO; comp[f] += 1
        saldo[f, idx[f]] = CUENTA; fase[f, idx[f]] = 0
        meta[f, idx[f]] = CUENTA*(1+F1); dia0[f, idx[f]] = CUENTA
        pico[f, idx[f]] = CUENTA
    for _ in range(3): compra()
    gan, per = RR - COSTE_R, -1.0 - COSTE_R
    for d in range(DIAS):
        v = fase >= 0; dia0[v] = saldo[v]
        for _ in range(OPS_DIA):
            v = fase >= 0
            if not v.any(): break
            r = np.where(rng.random((N, MAX)) < p, gan, per)
            saldo = np.where(v, saldo + r*riesgo*CUENTA, saldo)
            pico = np.where(v, np.maximum(pico, saldo), pico)
            suelo = (pico - DD*CUENTA) if movil else np.full_like(saldo, CUENTA*(1-DD))
            rompe = v & ((saldo <= suelo) | (saldo <= dia0 - DIA*CUENTA))
            fase = np.where(rompe, -1, fase); saldo = np.where(rompe, 0, saldo)
            v = fase >= 0; llega = v & (saldo >= meta)
            a = llega & (fase == 0)
            fase = np.where(a, 1, fase); saldo = np.where(a, CUENTA, saldo)
            meta = np.where(a, CUENTA*(1+F2), meta); dia0 = np.where(a, CUENTA, dia0)
            pico = np.where(a, CUENTA, pico)
            b = llega & (fase == 1)
            fase = np.where(b, 2, fase); saldo = np.where(b, CUENTA, saldo)
            meta = np.where(b, 1e12, meta); dia0 = np.where(b, CUENTA, dia0)
            pico = np.where(b, CUENTA, pico)
        if d % 10 == 9:
            fon = fase == 2
            pago = (np.where(fon, np.maximum(saldo-CUENTA, 0.0), 0.0)*SPLIT).sum(1)
            caja += pago; ret += pago
            saldo = np.where(fon & (saldo > CUENTA), CUENTA, saldo)
            pico = np.where(fon, np.minimum(pico, CUENTA), pico)
        if d % 5 == 0: compra()
    return ret - comp*PRECIO, caja

print("El plan del video, dos anios, empezando con 210 EUR\n")
for movil in (False, True):
    print(f"{'  DRAWDOWN ' + ('MOVIL (estricto)' if movil else 'FIJO (generoso)'):<38}")
    print(f"{'ventaja/op':>11} {'riesgo':>8} {'neto medio':>12} {'% que gana':>11} {'llega a 10k':>12}")
    print("   " + "-"*54)
    for ventaja in (-0.05, 0.00, 0.05, 0.10, 0.20):
        for riesgo in (0.005, 0.01):
            neto, caja = carrera(ventaja, riesgo, movil)
            print(f"{ventaja:>+11.2f} {100*riesgo:>7.1f}% {neto.mean():>+11,.0f}€ "
                  f"{100*(neto>0).mean():>10.1f}% {100*(caja>=10_000).mean():>11.2f}%")
    print()
