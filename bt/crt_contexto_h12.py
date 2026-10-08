"""¿Aporta el contexto superior al CRT de H12?

Tres filtros, todos causales, sobre las mismas senales del simulador:

  objetivo pendiente  la idea del usuario: si el CRT falla es porque hay OTRO
                      rango superior sin cumplir tirando del precio. Un CRT
                      diario ya formado cuyo objetivo aun no se ha alcanzado.
  sesgo diario     la direccion de los dos ultimos dias cerrados
  sesgo semanal    igual con semanas cerradas
  rango diario     el dia en curso ya se llevo el extremo del dia anterior
                   en el mismo sentido que la senal (la cascada de la clase)

  python3 bt/crt_contexto_h12.py
"""
import json, numpy as np, pandas as pd

D = json.load(open("data/crt_simulador.json"))
FIL = {
    "sin filtro":            lambda s: True,
    "sesgo diario a favor":  lambda s: s["bd"] == s["d"],
    "sesgo diario en contra":lambda s: s["bd"] == -s["d"],
    "sesgo semanal a favor": lambda s: s["bs"] == s["d"],
    "rango diario a favor":  lambda s: s["cd"] == s["d"],
    "rango diario en contra":lambda s: s["cd"] == -s["d"],
    "diario + semanal":      lambda s: s["bd"] == s["d"] and s["bs"] == s["d"],
    "rango + sesgo diario":  lambda s: s["cd"] == s["d"] and s["bd"] == s["d"],
    "OBJ diario pendiente a favor":   lambda s: s["po"] ==  s["d"],
    "OBJ diario pendiente en contra": lambda s: s["po"] == -s["d"],
    "OBJ diario sin pendiente":       lambda s: s["po"] == 0,
    "OBJ semanal pendiente a favor":  lambda s: s["pw"] ==  s["d"],
    "OBJ semanal pendiente en contra":lambda s: s["pw"] == -s["d"],
    "OBJ diario y semanal a favor":   lambda s: s["po"] == s["d"] and s["pw"] == s["d"],
}

filas = []
for par, P in D.items():
    cost = P["coste"]
    for s in P["senales"]:
        r = s["res"].get("ext150")
        if not r: continue
        cR = cost / s["rp"]
        filas.append(dict(par=par, t=P["velas"][s["i"]][0], d=s["d"], bd=s["bd"],
                          bs=s["bs"], cd=s["cd"], po=s["po"], pw=s["pw"],
                          rr=r["rr"], R=r["R"],
                          tp=1 if r["q"]=="objetivo" else 0, neta=r["R"]-cR))
T = pd.DataFrame(filas)
T["ano"] = pd.to_datetime(T.t, unit="s").dt.year
z = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v) > 5 else np.nan

print(f"=== ¿APORTA EL CONTEXTO SUPERIOR AL CRT DE H12? · {len(T)} senales · "
      f"3 pares · 2020-2026 ===\n")
print(f"  {'filtro':>24} {'n':>5} {'R:R':>5} {'acierto':>8} {'azar':>7} "
      f"{'R BRUTA':>9} {'z':>7} {'R NETA':>9} {'z':>7}")
for nom, f in FIL.items():
    g = T[[f(dict(d=r.d, bd=r.bd, bs=r.bs, cd=r.cd, po=r.po, pw=r.pw)) for r in T.itertuples()]]
    if len(g) < 20: continue
    print(f"  {nom:>24} {len(g):>5} {g.rr.mean():>5.2f} {g.tp.mean():>7.1%} "
          f"{(1/(1+g.rr)).mean():>6.1%} {g.R.mean():>+9.4f} {z(g.R):>+7.2f} "
          f"{g.neta.mean():>+9.4f} {z(g.neta):>+7.2f}")

print("\n  el mejor filtro, por par y por ano\n")
best = "OBJ diario pendiente en contra"
g = T[[FIL[best](dict(d=r.d, bd=r.bd, bs=r.bs, cd=r.cd, po=r.po, pw=r.pw)) for r in T.itertuples()]]
print(f"  ({best})")
print(f"  {'':>8} {'n':>5} {'acierto':>8} {'azar':>7} {'R BRUTA':>9} {'z':>7} {'R NETA':>9}")
for k, x in list(g.groupby("par")) + list(g.groupby("ano")):
    print(f"  {str(k):>8} {len(x):>5} {x.tp.mean():>7.1%} {(1/(1+x.rr)).mean():>6.1%} "
          f"{x.R.mean():>+9.4f} {z(x.R):>+7.2f} {x.neta.mean():>+9.4f}")
