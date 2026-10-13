"""El esquema del video: 200 EUR -> varias cuentas pequenas -> bola de nieve.

Su plan, tal cual lo cuenta:
  - 210 EUR = 3 cuentas de 10.000 a 70 EUR
  - dos fases: +8 % y +5 %, drawdown total 10 %
  - al pasar, hacer un 3 % y retirar el 80 % = 240 EUR
  - luego retirar ~2 % cada 14 dias
  - reinvertir los beneficios en mas cuentas

Su afirmacion clave: "pasar 1 de cada 3 es el PEOR de los casos".
Se simula con ventaja CERO para ver si el esquema se sostiene solo.

CORRECCION 21/09: la primera version retiraba en el instante exacto en que la
cuenta tocaba +3 % y la reseteaba a 10.000 con el suelo fijo en 9.000. Eso es
un trinquete: convierte un paseo aleatorio en algo que solo sube, y daba
+5.758 EUR con ventaja cero, o sea las prop pagando por nada. En la realidad
los retiros son CADA 14 DIAS: cobras lo que haya ese dia, no el pico.
"""
import numpy as np

PRECIO, CUENTA = 70.0, 10_000.0
F1, F2, DD, DIA, SPLIT = 0.08, 0.05, 0.10, 0.05, 0.80
RR, COSTE_R = 2.0, 0.07
OPS_DIA, DIAS = 3, 500          # dos anios
N = 100_000
rng = np.random.default_rng(13)

def carrera(p_gana, riesgo, capital0=210.0):
    """Sigue el plan del video durante dos anios. Devuelve (caja, pasadas, retiros)."""
    caja = np.full(N, capital0)
    # estado de hasta 8 cuentas por persona
    MAX = 8
    saldo = np.zeros((N, MAX)); fase = np.full((N, MAX), -1, np.int8)
    meta = np.zeros((N, MAX)); dia0 = np.zeros((N, MAX))
    pasadas = np.zeros(N); retirado = np.zeros(N); compradas = np.zeros(N)

    def compra():
        libre = fase < 0
        puede = (caja >= PRECIO) & libre.any(1)
        idx = np.argmax(libre, 1)
        f = puede
        caja[f] -= PRECIO; compradas[f] += 1
        saldo[f, idx[f]] = CUENTA; fase[f, idx[f]] = 0
        meta[f, idx[f]] = CUENTA*(1+F1); dia0[f, idx[f]] = CUENTA

    for _ in range(3): compra()          # las tres primeras
    gan, per = RR - COSTE_R, -1.0 - COSTE_R
    for d in range(DIAS):
        viva = fase >= 0
        dia0[viva] = saldo[viva]
        for _ in range(OPS_DIA):
            viva = fase >= 0
            if not viva.any(): break
            r = np.where(rng.random((N, MAX)) < p_gana, gan, per)
            saldo = np.where(viva, saldo + r*riesgo*CUENTA, saldo)
            rompe = viva & ((saldo <= CUENTA*(1-DD)) | (saldo <= dia0 - DIA*CUENTA))
            fase = np.where(rompe, -1, fase); saldo = np.where(rompe, 0, saldo)
            viva = fase >= 0
            llega = viva & (saldo >= meta)
            # fase 0 -> 1
            a = llega & (fase == 0)
            fase = np.where(a, 1, fase); saldo = np.where(a, CUENTA, saldo)
            meta = np.where(a, CUENTA*(1+F2), meta); dia0 = np.where(a, CUENTA, dia0)
            # fase 1 -> fondeada (meta de retiro 3 %)
            b = llega & (fase == 1)
            fase = np.where(b, 2, fase); saldo = np.where(b, CUENTA, saldo)
            meta = np.where(b, CUENTA*1.03, meta); dia0 = np.where(b, CUENTA, dia0)
            pasadas += b.sum(1)
            # fondeada: ya no se retira al tocar el 3 %. Se retira por calendario.
            c = llega & (fase == 2)
            meta = np.where(c, 1e12, meta)     # sin barrera superior
        # --- retiro por calendario, cada 14 dias naturales (10 de mercado)
        if d % 10 == 9:
            fond = fase == 2
            ben = np.where(fond, np.maximum(saldo-CUENTA, 0.0), 0.0)
            pago = (ben*SPLIT).sum(1)
            caja += pago; retirado += pago
            saldo = np.where(fond & (saldo > CUENTA), CUENTA, saldo)
        if d % 5 == 0: compra()          # reinvierte cuando puede
    return caja, pasadas, retirado, compradas

P0 = 1/(1+RR)                 # 33,3 % = el precio justo. VENTAJA CERO.
print(f"Su plan, con ventaja EXACTAMENTE CERO ({100*P0:.1f} % a 1:2, menos coste)\n")
print(f"{'riesgo':>7} {'retos':>7} {'pasa 1 de':>10} {'retirado':>11} {'gastado':>10} "
      f"{'NETO medio':>12} {'% que gana':>11} {'llega a 10k':>12}")
print("-"*86)
for riesgo in (0.005, 0.01, 0.02):
    caja, pas, ret, comp = carrera(P0, riesgo)
    gasto = comp*PRECIO
    neto = ret - gasto
    print(f"{100*riesgo:>6.1f}% {comp.mean():>7.1f} {comp.mean()/max(pas.mean(),1e-9):>10.1f} "
          f"{ret.mean():>10,.0f}€ {gasto.mean():>9,.0f}€ {neto.mean():>+11,.0f}€ "
          f"{100*(neto>0).mean():>10.1f}% {100*(caja>=10_000).mean():>11.2f}%")
