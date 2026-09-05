"""Sus 86 operaciones con una ejecucion PESIMISTA.

El examen le da el precio exacto. En real hay tres castigos, y son asimetricos:
  - entra peor de lo que ve            -> desliz de entrada S
  - el stop se llena peor que el stop  -> hueco G
  - el objetivo se llena justo, nunca mejor

Se mide contra el riesgo QUE EL DIMENSIONO -el stop que puso-, que es lo que
determina el lotaje y por tanto el dinero.

  python3 bt/examen_ejecucion.py
"""
import re, numpy as np, pandas as pd
from math import sqrt, erf
COSTE = 1.43
z  = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x)))

ops = []
for f in ("data/examen_respuestas_1.txt", "data/examen_respuestas_2.txt",
          "data/examen_respuestas_3.txt"):
    for l in open(f):
        m = re.match(r"S\d+ · \d\d:\d\d \S+ ent \S+ sl \S+ \(([\d.]+)p\) tp \S+ -> (\S+) "
                     r"([+-][\d.]+) R", l.strip())
        if m: ops.append((float(m.group(1)), m.group(2), float(m.group(3))))
d = pd.DataFrame(ops, columns=["stop", "motivo", "R"])
print(f"{len(d)} operaciones · stop mediano {d.stop.median():.1f} p\n")

def neta(S, G, coste=COSTE):
    """S = desliz de entrada, G = hueco al saltar el stop, en pips."""
    out = []
    for r in d.itertuples():
        s = r.stop
        if r.motivo == "TP":   x = (2*s - S - coste)/s
        elif r.motivo == "SL": x = -(s + S + G + coste)/s
        else:                  x = r.R - (S + coste)/s      # cierre a mercado
        out.append(x)
    return np.array(out)

print(f"  {'desliz entrada':>15s} {'hueco stop':>11s} {'R neta/op':>10s} {'z':>7s} "
      f"{'acierto que haría falta':>24s}")
print("  " + "-"*72)
for S, G, nom in ((0.0, 0.0, "sin castigo"), (0.2, 0.3, "leve"), (0.5, 0.5, "normal"),
                  (1.0, 1.0, "duro"), (1.5, 2.0, "brutal")):
    x = neta(S, G)
    # acierto de equilibrio con esos castigos y su stop mediano
    s = d.stop.median()
    p = (s + S + G + COSTE) / (2*s - S - COSTE + s + S + G + COSTE)
    print(f"  {S:14.1f}p {G:10.1f}p {x.mean():+10.3f} {z(x):+7.2f} "
          f"{100*p:23.1f} %   {nom}")

print(f"\n  su acierto medido: {100*(d.motivo=='TP').mean():.1f} %")
print("\n  Con el castigo 'duro' -1 pip de desliz al entrar y 1 pip de hueco al")
print("  saltar el stop, ADEMÁS del 1,43 de coste- seguiría necesitando acertar")
print(f"  el {100*((d.stop.median()+1+1+COSTE)/(2*d.stop.median()-1-COSTE+d.stop.median()+1+1+COSTE)):.1f} %, y acierta el {100*(d.motivo=='TP').mean():.1f} %.")
