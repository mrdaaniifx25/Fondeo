"""Pre-registro docs/PREREGISTRO_gestion_fondeo.md

La gestion de riesgo del video de cuentas de fondeo, simulada.

Su tesis: a igual esperanza, R:R bajo con acierto alto aprueba mas.
Lo que este proyecto mide: esperanza CERO. Y ahi el teorema de la barrera
dice que el tamanio no cambia la probabilidad... salvo por el coste, que se
paga POR OPERACION. Asi que arriesgar menos = mas operaciones = mas coste.

  python3 bt/gestion_fondeo.py
"""
import numpy as np
rng = np.random.default_rng(20261019)
N, TOPE = 200_000, 4000

FORMATOS = {
    "futuros 50k (DD 4 %, objetivo 6 %)":  dict(dd=0.04, obj=0.06, fases=1),
    "forex 10k 2 fases (DD 10 %, 8+5 %)":  dict(dd=0.10, obj=(0.08, 0.05), fases=2),
}

def carrera(p, rr, riesgo, coste, dd, obj, fases, n=N):
    """Devuelve (tasa de aprobacion, operaciones medianas hasta resolver)."""
    objs = obj if isinstance(obj, tuple) else (obj,)
    vivos = np.ones(n, bool)
    saldo = np.zeros(n)          # P&L acumulado en fraccion de cuenta
    pico = np.zeros(n)
    ops = np.zeros(n)
    fase = np.zeros(n, int)
    meta = np.array([objs[0]]*n)
    for _ in range(TOPE):
        if not vivos.any(): break
        k = vivos.sum()
        gana = rng.random(k) < p
        r = np.where(gana, rr, -1.0) - coste
        saldo[vivos] += r*riesgo
        ops[vivos] += 1
        pico[vivos] = np.maximum(pico[vivos], saldo[vivos])
        # drawdown desde el pico (el formato de fondeo mas comun)
        muerto = vivos & (saldo - pico <= -dd)
        vivos &= ~muerto
        paso = vivos & (saldo >= meta)
        if paso.any():
            if fases == 1:
                vivos &= ~paso
                fase[paso] = 1
            else:
                nuevo = paso & (fase == 0)
                fin   = paso & (fase == 1)
                fase[nuevo] = 1
                saldo[nuevo] = 0.0; pico[nuevo] = 0.0      # la fase 2 empieza limpia
                meta[nuevo] = objs[1]
                fase[fin] = 2
                vivos &= ~fin
    aprob = (fase == (1 if fases == 1 else 2)).mean()
    return aprob, float(np.median(ops))

def esperanza(p, rr, coste): return p*rr - (1-p) - coste
def acierto_para(e, rr, coste): return (1 + e + coste)/(1 + rr)

COSTE = 0.10        # coste tipico en R medido en este proyecto (10 % del riesgo)

print("="*100)
print("1 · SU TESIS · a IGUAL esperanza, ¿gana el R:R bajo con acierto alto?")
print("="*100)
for E in (0.05, 0.10):
    print(f"\n  esperanza {E:+.2f} R por operación   (coste {COSTE:.2f} R ya descontado)")
    for et, F in FORMATOS.items():
        print(f"    {et}")
        print(f"      {'R:R':>5}{'acierto':>9}{'riesgo 0,5 %':>14}{'riesgo 1,0 %':>14}"
              f"{'riesgo 1,5 %':>14}{'riesgo 2,5 %':>14}")
        for rr in (0.5, 1.0, 2.0, 3.0, 5.0):
            p = acierto_para(E, rr, COSTE)
            if not (0 < p < 1): continue
            fila = f"      {rr:>5.1f}{100*p:>8.1f}%"
            for rg in (0.005, 0.010, 0.015, 0.025):
                a, _ = carrera(p, rr, rg, COSTE, F["dd"], F["obj"], F["fases"])
                fila += f"{100*a:>13.1f}%"
            print(fila)

print("\n" + "="*100)
print("2 · PRINCIPAL · a esperanza CERO (lo que mide este proyecto)")
print("="*100)
print("  Con ventaja bruta nula y coste real. ¿Qué riesgo por operación conviene?")
for et, F in FORMATOS.items():
    print(f"\n    {et}")
    print(f"      {'R:R':>5}{'acierto':>9}" + "".join(f"{f'{100*r:.2f} %':>11}"
          for r in (0.0025, 0.005, 0.01, 0.015, 0.025, 0.04)))
    for rr in (1.0, 2.0, 3.0):
        p = acierto_para(0.0, rr, COSTE)
        fila = f"      {rr:>5.1f}{100*p:>8.1f}%"
        for rg in (0.0025, 0.005, 0.01, 0.015, 0.025, 0.04):
            a, _ = carrera(p, rr, rg, COSTE, F["dd"], F["obj"], F["fases"])
            fila += f"{100*a:>10.1f}%"
        print(fila)
print("\n  (el 'acierto' de esta tabla es el que hace la esperanza CERO con coste 0,10)")

print("\n" + "="*100)
print("3 · ¿QUÉ ESPERANZA hace falta para aprobar el 50 % al 1,5 % de riesgo?")
print("="*100)
for et, F in FORMATOS.items():
    print(f"\n    {et}")
    print(f"      {'R:R':>5}{'esperanza':>12}{'acierto':>10}{'aprobados':>12}")
    for rr in (1.0, 2.0, 3.0):
        lo, hi = 0.0, 0.60
        for _ in range(16):
            mid = (lo+hi)/2
            p = acierto_para(mid, rr, COSTE)
            if p >= 1: hi = mid; continue
            a, _ = carrera(p, rr, 0.015, COSTE, F["dd"], F["obj"], F["fases"], n=40000)
            lo, hi = (lo, mid) if a > 0.50 else (mid, hi)
        E = (lo+hi)/2; p = acierto_para(E, rr, COSTE)
        a, _ = carrera(p, rr, 0.015, COSTE, F["dd"], F["obj"], F["fases"])
        print(f"      {rr:>5.1f}{E:>+12.3f}{100*p:>9.1f}%{100*a:>11.1f}%")

print("\n" + "="*100)
print("4 · EL EMBUDO DEL VÍDEO, explicado")
print("="*100)
print("  Él cita: 100.000 pagan -> 10.000 pasan fase 1 -> 2.400 se fondean -> 72 retiran.")
F = FORMATOS["forex 10k 2 fases (DD 10 %, 8+5 %)"]
print(f"\n      {'esperanza':>11}{'acierto R:R2':>14}{'pasan fase 1':>14}{'se fondean':>13}")
for E in (-0.10, -0.05, 0.0, 0.05, 0.10):
    p = acierto_para(E, 2.0, COSTE)
    if not (0 < p < 1): continue
    a1, _ = carrera(p, 2.0, 0.015, COSTE, F["dd"], (0.08,), 1)
    a2, _ = carrera(p, 2.0, 0.015, COSTE, F["dd"], F["obj"], 2)
    print(f"      {E:>+11.2f}{100*p:>13.1f}%{100*a1:>13.1f}%{100*a2:>12.1f}%")
print("\n  real del vídeo:                       10,0 %        2,4 %")
