"""El reto de FundingPips con su perfil real de operaciones.

Monte Carlo remuestreando SESIONES ENTERAS con reemplazo -no operaciones
sueltas- porque dentro de un dia estan correlacionadas: si el dia va mal, va mal
para las dos o tres operaciones.

PARAMETROS DEL RETO: son los estandar de un reto de dos fases. El tiene que
confirmarlos, y si cambian se vuelve a correr cambiando la tabla de arriba.

  python3 bt/reto_fundingpips.py
"""
import json, re, numpy as np, pandas as pd

CUENTA   = 10_000
OBJ1, OBJ2 = 0.08, 0.05       # objetivo de beneficio de cada fase
LIM_DIA  = 0.05               # perdida maxima en un dia, sobre el saldo inicial
LIM_TOT  = 0.10               # perdida maxima total, sobre el saldo inicial
DIAS_MAX = 60                 # tope de dias por fase
DIAS_MIN = 3                  # dias minimos operados
COSTE, N = 1.43, 20_000

def sesiones(pares):
    """Lista de sesiones; cada una es la secuencia de R netas de ese dia."""
    out = []
    for f, dj in pares:
        dias = {int(k): v for k, v in json.load(open(dj)).items()}
        por = {}
        for l in open(f):
            m = re.match(r"S(\d+) · \d\d:\d\d \S+ ent \S+ sl \S+ \(([\d.]+)p\) tp \S+ "
                         r"-> \S+ ([+-][\d.]+) R", l.strip())
            if not m: continue
            s = int(m.group(1)); rg = float(m.group(2)); R = float(m.group(3))
            por.setdefault(s, []).append(R - COSTE/rg)
        for s in dias:                       # las sesiones sin operar cuentan como 0
            out.append(por.get(s, []))
    return out

TODO  = sesiones([("data/examen_respuestas_1.txt", "data/examen_dias.json"),
                  ("data/examen_respuestas_2.txt", "data/examen_dias2.json"),
                  ("data/examen_respuestas_3.txt", "data/examen_dias3.json")])
FLOJO = sesiones([("data/examen_respuestas_1.txt", "data/examen_dias.json"),
                  ("data/examen_respuestas_2.txt", "data/examen_dias2.json")])

def fase(ses, riesgo, objetivo, rng, saldo0):
    """Devuelve 'pasa', 'revienta' o 'tiempo'. El riesgo es fijo sobre el inicial."""
    unidad = saldo0 * riesgo
    saldo, pico = saldo0, saldo0
    suelo_tot = saldo0 - CUENTA*LIM_TOT
    for dia in range(DIAS_MAX):
        s = ses[rng.integers(len(ses))]
        ini_dia = saldo
        suelo_dia = ini_dia - CUENTA*LIM_DIA
        for R in s:
            saldo += R*unidad
            if saldo <= suelo_dia or saldo <= suelo_tot:
                return "revienta", dia+1, saldo
        if saldo >= saldo0 + CUENTA*objetivo and dia+1 >= DIAS_MIN:
            return "pasa", dia+1, saldo
    return "tiempo", DIAS_MAX, saldo

def corre(ses, nombre):
    rng = np.random.default_rng(20260904)
    print(f"\n{'='*86}\n{nombre}   ·   {len(ses)} sesiones en la urna   ·   "
          f"{sum(len(s) for s in ses)} operaciones\n{'='*86}")
    ops = [r for s in ses for r in s]
    print(f"  R neta media por operación {np.mean(ops):+.3f}  ·  por sesión "
          f"{np.mean([sum(s) for s in ses]):+.3f}  ·  sesiones sin operar "
          f"{100*np.mean([len(s)==0 for s in ses]):.0f} %")
    print(f"\n  {'riesgo':>7s} {'pasa fase 1':>12s} {'revienta':>10s} {'sin tiempo':>11s} "
          f"{'días (mediana)':>15s} {'pasa las DOS':>13s}")
    print("  " + "-"*74)
    for riesgo in (0.0025, 0.005, 0.0075, 0.01, 0.015, 0.02):
        res, dias, dobles = [], [], 0
        for _ in range(N):
            r1, d1, s1 = fase(ses, riesgo, OBJ1, rng, CUENTA)
            res.append(r1)
            if r1 == "pasa":
                dias.append(d1)
                r2, _, _ = fase(ses, riesgo, OBJ2, rng, CUENTA)
                if r2 == "pasa": dobles += 1
        p = lambda k: 100*sum(1 for x in res if x == k)/N
        print(f"  {100*riesgo:6.2f}% {p('pasa'):11.1f}% {p('revienta'):9.1f}% "
              f"{p('tiempo'):10.1f}% {np.median(dias) if dias else float('nan'):14.0f} "
              f"{100*dobles/N:12.1f}%")

print("="*86)
print("EL RETO DE FUNDINGPIPS CON SU PERFIL REAL")
print(f"  cuenta {CUENTA:,} · objetivo fase 1 {100*OBJ1:.0f} % · fase 2 {100*OBJ2:.0f} % · "
      f"límite diario {100*LIM_DIA:.0f} % · límite total {100*LIM_TOT:.0f} %")
print(f"  {N:,} simulaciones · se remuestrean sesiones enteras con reemplazo")
print("="*86)
corre(TODO,  "CASO BASE · los tres bloques, 86 operaciones")
corre(FLOJO, "CASO PRUDENTE · solo bloques 1 y 2, 53 operaciones (sin el 81 %)")


# ---------------------------------------------------------------- estrés
def estructura(ses):
    """Se queda con la FORMA de sus sesiones: cuántas operaciones y con qué stop."""
    stops = []
    for f, dj in (("data/examen_respuestas_1.txt","data/examen_dias.json"),
                  ("data/examen_respuestas_2.txt","data/examen_dias2.json"),
                  ("data/examen_respuestas_3.txt","data/examen_dias3.json")):
        for l in open(f):
            m = re.match(r"S\d+ · \d\d:\d\d \S+ ent \S+ sl \S+ \(([\d.]+)p\)", l.strip())
            if m: stops.append(float(m.group(1)))
    return [len(s) for s in ses], np.array(stops)

def sintetico(cuantas, stops, p, rng):
    """Sesiones con su misma forma, pero con el acierto que se le imponga."""
    out = []
    for k in cuantas:
        s = []
        for _ in range(k):
            st = stops[rng.integers(len(stops))]
            s.append((2.0 if rng.random() < p else -1.0) - COSTE/st)
        out.append(s)
    return out

print("\n" + "="*86)
print("PRUEBA DE ESFUERZO · ¿y si en directo su acierto es peor?")
print("  misma forma de sesión y mismos stops; solo cambia el acierto")
print("="*86)
cuantas, stops = estructura(TODO)
print(f"  su acierto medido: 65,4 %   ·   punto de equilibrio con stop de "
      f"{np.median(stops):.1f} p: {100*(1+COSTE/np.median(stops))/3:.1f} %")
print(f"\n  {'acierto':>8s} {'R neta/op':>10s} {'pasa fase 1':>12s} {'revienta':>10s} "
      f"{'pasa las DOS':>13s} {'al mes al 1 %':>14s}")
print("  " + "-"*72)
rng = np.random.default_rng(20260905)
for p in (0.65, 0.60, 0.55, 0.50, 0.45, 0.42, 0.40, 0.375, 0.35):
    ses = sintetico(cuantas*40, stops, p, rng)         # urna grande, misma forma
    ops = [r for s in ses for r in s]
    res, dobles = [], 0
    M = 4000
    for _ in range(M):
        r1, _, _ = fase(ses, 0.01, OBJ1, rng, CUENTA)
        res.append(r1)
        if r1 == "pasa":
            r2, _, _ = fase(ses, 0.01, OBJ2, rng, CUENTA)
            if r2 == "pasa": dobles += 1
    q = lambda k: 100*sum(1 for x in res if x==k)/M
    mes = np.mean([sum(s) for s in ses])*21*100        # 21 sesiones, 100 € por R
    print(f"  {100*p:7.1f}% {np.mean(ops):+10.3f} {q('pasa'):11.1f}% {q('revienta'):9.1f}% "
          f"{100*dobles/M:12.1f}% {mes:+13.0f} €")
