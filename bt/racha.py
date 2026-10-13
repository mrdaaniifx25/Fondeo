"""¿El resultado de una operación dice algo de la siguiente?

Es la tesis del vídeo que mandó el usuario: «si ayer me saltó el stop y hoy
aparece el mismo setup, lo tomo igual». Si el resultado anterior no predice el
siguiente, tiene razón.

IMPORTANTE: sólo vale con operaciones que NO se solapan. Si dos operaciones
consecutivas comparten ventana de tiempo y van en sentidos opuestos, salen
anticorrelacionadas por construcción y no por el mercado.
"""
import numpy as np, pandas as pd, os
from math import sqrt
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def prueba(nom, g):
    g = np.asarray(g, float)
    if len(g) < 100: return print(f"  {nom:<44} (pocas: {len(g)})")
    ant, sig = g[:-1], g[1:]
    tg, tp = sig[ant == 1], sig[ant == 0]
    if len(tg) < 30 or len(tp) < 30: return print(f"  {nom:<44} (pocas)")
    a, b = tg.mean(), tp.mean()
    se = sqrt(a*(1-a)/len(tg) + b*(1-b)/len(tp)); d = a-b; ic = 1.96*se
    print(f"  {nom:<44} n {len(g):5,}  tras GANAR {100*a:5.1f} %   tras PERDER {100*b:5.1f} %"
          f"   diferencia {100*d:+5.1f} [{100*(d-ic):+5.1f}, {100*(d+ic):+5.1f}]"
          f"{'  <- PREDICE' if abs(d) > ic else '  sin senal'}")

src = open("bt/dia_previo.py").read().replace(
    'for ins in INS:\n    print("\\n" + "="*178); print(ins); print("="*178)\n'
    '    for mins, tf in ((5,"M5"), (15,"M15")):\n'
    '        for objetivo in ("opuesto", "1:1", "1:2"):\n'
    '            linea(f"{tf} · objetivo {objetivo}", corre(ins, mins, objetivo))', '')
ns = {}; exec(compile(src, "dia_previo", "exec"), ns)

print("Operaciones SEPARADAS (0,84 al dia, sin solape). Esta es la prueba buena.\n" + "="*146)
for ins in ("EURUSD", "oro", "DAX"):
    for obj in ("1:1", "1:2"):
        D = ns["corre"](ins, 15, obj)
        if D is not None: prueba(f"dia previo · {ins} · M15 · {obj}", D.gana.to_numpy())

print("\nOperaciones SOLAPADAS, para ensenar por que no valen\n" + "="*146)
src2 = open("bt/ema_sr.py").read().split('print(f"\\nEURUSD · rupturas')[0]
ns2 = {}; exec(compile(src2, "ema_sr", "exec"), ns2)
s = [x for x in ns2["sucesos"] if x["niv"] and x["m1"]]
lad = np.array([x["lado"] for x in s])
t = pd.DatetimeIndex([x["t"] for x in s])
sep = pd.Series(t).diff().dt.total_seconds().div(3600).median()
for N in (10, 20):
    D = ns2["celda"](True, N, True)
    if D is not None: prueba(f"EMA 50 + S/R · EURUSD · N={N}", D.gana.to_numpy())
print(f"\n  ...y la razon: {100*(lad[:-1] != lad[1:]).mean():.1f} % de las consecutivas van en")
print(f"  sentido OPUESTO y se separan {sep:.2f} horas, con un horizonte de 20. Se pisan")
print( "  unas a otras, asi que si una gana la otra tiende a perder. Es aritmetica, no mercado.")
