"""¿Se puede escalar desde 80 EUR encadenando cuentas de fondeo?

Modelo: cada mes se compran las evaluaciones que el capital permita, las
cuentas fondeadas vivas producen retiradas o mueren, y lo retirado vuelve a
comprar evaluaciones. Si el capital baja de la cuota mas barata, se acabo.

  python3 bt/escalado_fondeo.py
"""
import numpy as np
rng = np.random.default_rng(2026)
SIMS, MESES = 50000, 12
TARIFA = [(5000,49),(10000,89),(25000,189),(50000,349),(100000,549)]
RETIRO, REPARTO = 0.05, 0.80
P_RET, P_MUE = 0.45, 0.22        # por mes y cuenta viva -> 2,05 retiradas de media

def corre(p_pasa, cap0, meses=MESES, agresivo=True, reserva=0):
    cap = np.full(SIMS, float(cap0))
    cuentas = [[] for _ in range(SIMS)]      # tamanos de cuentas vivas
    retirado = np.zeros(SIMS)
    for m in range(meses):
        for s in range(SIMS):
            # 1 · las cuentas vivas retiran o mueren
            vivas = []
            for c in cuentas[s]:
                u = rng.random()
                if u < P_RET:
                    g = c*RETIRO*REPARTO; cap[s] += g; retirado[s] += g; vivas.append(c)
                elif u < P_RET+P_MUE: pass
                else: vivas.append(c)
            cuentas[s] = vivas
            # 2 · comprar evaluaciones con lo que haya
            while True:
                opts = [(t,q) for t,q in TARIFA if q <= cap[s]-reserva]
                if not opts: break
                t,q = (opts[-1] if agresivo else opts[0])
                cap[s] -= q
                if rng.random() < p_pasa: cuentas[s].append(t)
    total = cap + 0.0
    return retirado, total, np.array([len(c) for c in cuentas])

print("=== ESCALAR DESDE 80 EUR EN 12 MESES ===\n")
for p, et in ((0.369, "P = 36,9 % (mi simulacion)"),
              (0.167, "P = 16,7 % (el unico dato REAL observado)")):
    for cap0 in (80, 300, 1000):
        ret, fin, nc = corre(p, cap0)
        arruina = float((fin < 49).mean())
        print(f"  {et:42s} capital inicial {cap0:5d} EUR")
        print(f"     capital final:  mediana {np.median(fin):8,.0f} EUR   "
              f"media {fin.mean():8,.0f} EUR")
        print(f"     ARRUINADO (< 49 EUR) al cabo de 12 meses:  {arruina*100:5.1f} %")
        print(f"     P(acabar con mas de 10.000 EUR): "
              f"{float((fin>=10000).mean())*100:5.1f} %")
        print(f"     P(acabar por encima de lo que puso): "
              f"{float((fin>cap0).mean())*100:5.1f} %")
        print()
