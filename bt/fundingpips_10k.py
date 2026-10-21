"""Su cuenta REAL: FundingPips 10k, dos fases, con limite DIARIO.

  fase 1  +8 %      fase 2  +5 %
  perdida diaria maxima  3 %      drawdown total  10 %

El limite diario no estaba en bt/gestion_fondeo.py y es el que de verdad mata:
si arriesga r por operacion y hace n operaciones al dia, el peor dia posible es
n*r. Con 4 al dia al 1 % son 4 % > 3 %: la cuenta muere en un solo dia malo.

  python3 bt/fundingpips_10k.py
"""
import numpy as np
rng = np.random.default_rng(20261019)
N = 120_000
DIAS_TOPE = 400
F1, F2, DIA, TOT = 0.08, 0.05, 0.03, 0.10


def carrera(p, rr, riesgo, coste, ops_dia, trailing=False, n=N):
    """Simula hasta pasar las dos fases, reventar, o agotar DIAS_TOPE."""
    saldo = np.zeros(n)            # P&L acumulado, fraccion de la cuenta
    pico = np.zeros(n)
    fase = np.zeros(n, int)        # 0 = fase 1, 1 = fase 2, 2 = fondeado
    vivo = np.ones(n, bool)
    dias = np.zeros(n)
    meta = np.full(n, F1)
    for _ in range(DIAS_TOPE):
        if not vivo.any(): break
        k = int(vivo.sum())
        ini = saldo[vivo].copy()           # saldo al abrir el dia
        dia_pl = np.zeros(k)
        muerto_dia = np.zeros(k, bool)
        for _o in range(ops_dia):
            act = ~muerto_dia
            if not act.any(): break
            g = rng.random(k) < p
            r = (np.where(g, rr, -1.0) - coste) * riesgo
            dia_pl = np.where(act, dia_pl + r, dia_pl)
            # limite DIARIO: se mide sobre el saldo de apertura del dia
            muerto_dia |= (dia_pl <= -DIA)
        saldo[vivo] = ini + dia_pl
        pico[vivo] = np.maximum(pico[vivo], saldo[vivo])
        dias[vivo] += 1
        base = (pico[vivo] if trailing else np.zeros(k))
        fuera = (saldo[vivo] - base <= -TOT) | muerto_dia
        idx = np.nonzero(vivo)[0]
        vivo[idx[fuera]] = False
        # objetivos
        ok = np.nonzero(vivo)[0]
        if len(ok):
            paso = saldo[ok] >= meta[ok]
            sube = ok[paso & (fase[ok] == 0)]
            fin = ok[paso & (fase[ok] == 1)]
            fase[sube] = 1; saldo[sube] = 0.0; pico[sube] = 0.0; meta[sube] = F2
            fase[fin] = 2; vivo[fin] = False
    return (fase == 2).mean(), float(np.median(dias[fase == 2])) if (fase == 2).any() else np.nan


print("SU CUENTA · FundingPips 10k · fase 1 +8 % · fase 2 +5 % · día -3 % · total -10 %")
print("Coste 0,10 R (el medido en su patrón de Londres con stop de 1,5 x ATR)\n")
COSTE = 0.10

print("="*96)
print("1 · EL LÍMITE DIARIO MANDA: operaciones al día x riesgo por operación")
print("="*96)
print("  Si hace n operaciones y pierde todas, el día cae n x riesgo. El tope es 3 %.\n")
print(f"  {'ops/día':>8}" + "".join(f"{f'{100*r:.2f} %':>10}" for r in
      (0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02)))
for nd in (1, 2, 3, 4, 6):
    fila = f"  {nd:>8}"
    for r in (0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02):
        peor = nd*r
        fila += f"{('  ' + f'{100*peor:.1f}%' + ('' if peor <= DIA else ' X')):>10}"
    print(fila)
print("\n  X = un solo día malo completo revienta la cuenta.")

for E, et in ((0.00, "ESPERANZA CERO · lo que mide este proyecto"),
              (0.05, "esperanza +0,05 R"), (0.10, "esperanza +0,10 R")):
    print("\n" + "="*96); print(f"2 · {et}"); print("="*96)
    for rr in (1.0, 2.0):
        p = (1 + E + COSTE)/(1 + rr)
        if not (0 < p < 1): continue
        print(f"\n  R:R {rr:.0f}  ·  acierto necesario {100*p:.1f} %")
        print(f"  {'ops/día':>8}" + "".join(f"{f'{100*r:.2f} %':>12}" for r in
              (0.0025, 0.005, 0.0075, 0.01, 0.015)))
        for nd in (1, 2, 3, 4):
            fila = f"  {nd:>8}"
            for r in (0.0025, 0.005, 0.0075, 0.01, 0.015):
                a, d = carrera(p, rr, r, COSTE, nd)
                fila += f"{f'{100*a:.1f}%':>12}"
            print(fila)
        print(f"  {'':>8}" + "  (% que pasa LAS DOS fases)")

print("\n" + "="*96)
print("3 · LA MEJOR CELDA a esperanza cero, con los días que tarda")
print("="*96)
mejor = (0, None)
for rr in (1.0, 2.0, 3.0):
    p = (1 + 0.0 + COSTE)/(1 + rr)
    for nd in (1, 2, 3, 4):
        for r in (0.0025, 0.005, 0.0075, 0.01, 0.015):
            if nd*r > DIA: continue
            a, d = carrera(p, rr, r, COSTE, nd, n=60000)
            if a > mejor[0]: mejor = (a, (rr, p, nd, r, d))
a, (rr, p, nd, r, d) = mejor
print(f"  R:R {rr:.0f} · acierto {100*p:.1f} % · {nd} operación(es)/día · riesgo {100*r:.2f} %")
print(f"  pasa las dos fases el {100*a:.1f} % de las veces, en {d:.0f} días de mediana")
print(f"  peor día posible: {100*nd*r:.1f} % de 3,0 % permitido")
