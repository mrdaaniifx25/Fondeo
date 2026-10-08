"""Analizador del bloque 8. Se escribe y se PRUEBA antes de que el opere.

  python3 bt/examen71_lee.py [fichero]
"""
import re, sys
from math import sqrt, erf
import numpy as np, pandas as pd

p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
LIN = re.compile(r"^#(?P<n>\d+) (?P<k>[A-F]) (?P<d>TOMO|PASO)\s+(?P<lado>COMPRA|VENTA)\s+"
                 r"(?P<rgo>[\d.]+)u -> (?P<mot>TP|SL|fuera)\s+(?P<R>[+-][\d.]+) R\s+"
                 r"neta (?P<neta>[+-][\d.]+)\s+(?P<anio>\d{4})\s*$")

def lee(ruta):
    f = []
    for l in open(ruta, encoding="utf-8"):
        m = LIN.match(l.strip())
        if m:
            d = m.groupdict()
            f.append(dict(n=int(d["n"]), k=d["k"], si=d["d"] == "TOMO",
                          lado=1 if d["lado"] == "COMPRA" else -1,
                          rgo=float(d["rgo"]), mot=d["mot"], R=float(d["R"]),
                          neta=float(d["neta"]), anio=int(d["anio"])))
    return pd.DataFrame(f).drop_duplicates(subset=["n"], keep="last")

if __name__ == "__main__":
    D = lee(sys.argv[1] if len(sys.argv) > 1 else "data/examen71_prueba.txt")
    print(f"{len(D)} decisiones · toma {int(D.si.sum())} · deja {int((~D.si).sum())}")
    if len(D) < 20: sys.exit()
    A, B = D[D.si], D[~D.si]
    print(f"\n{'':>22s} {'n':>5s} {'acierto':>9s} {'R bruta':>9s} {'R NETA':>9s}")
    print("-"*58)
    for nom, g in (("TODAS (regla ciega)", D), ("las que TOMA", A), ("las que DEJA", B)):
        if not len(g): continue
        r = g[g.mot.isin(["TP","SL"])]
        ac = 100*(r.mot == "TP").mean() if len(r) else float("nan")
        print(f"{nom:>22s} {len(g):5d} {ac:8.1f} % {g.R.mean():+9.3f} {g.neta.mean():+9.3f}")
    if len(A) > 2 and len(B) > 2:
        dif = A.neta.mean() - B.neta.mean()
        se = sqrt(A.neta.var(ddof=1)/len(A) + B.neta.var(ddof=1)/len(B))
        z = dif/se if se else 0.0
        print(f"\nPRINCIPAL · R neta tomadas − dejadas")
        print(f"  diferencia {dif:+.3f} R   ·   z = {z:+.2f}   ·   p = {p2(z):.3f}"
              f"   ·   {'PASA' if abs(z) > 1.96 else 'no pasa'}   (umbral |z| > 1,96)")
        zc = (A.neta.mean() - D.neta.mean())/(A.neta.std(ddof=1)/sqrt(len(A)))
        print(f"\nSECUNDARIA · ¿bate a la regla a ciegas ({D.neta.mean():+.3f})?")
        print(f"  lo que toma {A.neta.mean():+.3f}   ·   z = {zc:+.2f}")
    print(f"\nLAS CUATRO PREDICCIONES FIRMADAS")
    tm = D.si.mean()
    r = A[A.mot.isin(["TP","SL"])]
    ac = (r.mot == "TP").mean() if len(r) else float("nan")
    dif = A.neta.mean() - B.neta.mean() if len(A) and len(B) else float("nan")
    se = sqrt(A.neta.var(ddof=1)/len(A) + B.neta.var(ddof=1)/len(B)) if len(A)>2 and len(B)>2 else 1
    z = dif/se
    for nom, ok in (("1 · toma entre el 40 % y el 70 %", 0.40 <= tm <= 0.70),
                    ("2 · diferencia entre -0,10 y +0,25 y NO significativa",
                     -0.10 <= dif <= 0.25 and abs(z) < 1.96),
                    ("3 · su acierto entre el 33 % y el 45 %", 0.33 <= ac <= 0.45),
                    ("4 · le cuesta más que el de roturas", None)):
        print(f"  {nom:56s} {'✓' if ok else ('—' if ok is None else '✗')}")
