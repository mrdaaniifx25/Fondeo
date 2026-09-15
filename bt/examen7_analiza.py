"""docs/PREREGISTRO_examen7.md · el analisis, escrito ANTES del volcado.

  python3 bt/examen7_analiza.py [fichero]
"""
import json, sys
from math import sqrt, erf
import numpy as np, pandas as pd
import importlib.util
spec = importlib.util.spec_from_file_location("lee7", "bt/examen7_lee.py")
lee7 = importlib.util.module_from_spec(spec); spec.loader.exec_module(lee7)

GEO, COSTE, NSES, CERCA = 1/3, 1.43, 40, 3
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
IND = json.load(open("data/examen7_ind.json"))
CON = {int(k) for k, v in IND["con"].items() if v}
CAND = {int(k): v for k, v in IND["cand"].items()}

o, des, cta, vac = lee7.lee(sys.argv[1] if len(sys.argv) > 1 else "data/examen7_respuestas.txt")
_, malas = lee7.comprueba(o, des)
o["con"] = o.ses.isin(CON)

print("="*74); print("BLOQUE 7 · 40 SESIONES · A/B DEL INDICADOR"); print("="*74)
print(f"  {len(o)} operaciones en {o.ses.nunique()} sesiones "
      f"· {len(vac)} sin operar · {len(des)} descartes")
print(f"  marca [ind] contra el sorteo: "
      f"{'coincide' if not malas else str(len(malas)) + ' DESCUADRES'}")

# ─── principal: operaciones por sesion ──────────────────────────────────────
por = pd.Series(0, index=range(1, NSES+1), dtype=float)
por.update(o.groupby("ses").size())
a, b = por[por.index.isin(CON)].to_numpy(), por[~por.index.isin(CON)].to_numpy()
dif = a.mean() - b.mean()
se = sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
z1 = dif/se if se else 0.0
print("\n" + "="*74); print("PRINCIPAL · operaciones por sesión"); print("="*74)
print(f"  con indicador  {a.mean():.2f}   ({int(a.sum())} en {len(a)} sesiones)")
print(f"  sin indicador  {b.mean():.2f}   ({int(b.sum())} en {len(b)} sesiones)")
print(f"  DIFERENCIA     {dif:+.2f}   ·   z = {z1:+.2f}   ·   p = {p2(z1):.3f}"
      f"   ·   {'PASA' if abs(z1) > 1.96 else 'no pasa'}")

# ─── secundaria: coincidencia con las flechas ───────────────────────────────
def coincide(r):
    fl = [c for c in CAND.get(r.ses, []) if c["pasa"]]
    return any(abs(c["m"] + 480 - r.min) <= CERCA and c["lado"] == r.lado for c in fl)
o["coin"] = [coincide(r) for r in o.itertuples()] if len(o) else []
ca, cb = o[o.con].coin, o[~o.con].coin
if len(ca) and len(cb):
    pa, pb = ca.mean(), cb.mean(); pp = o.coin.mean()
    z2 = (pa-pb)/sqrt(pp*(1-pp)*(1/len(ca)+1/len(cb))) if 0 < pp < 1 else 0.0
else: pa = pb = z2 = float("nan")
print("\n" + "="*74); print(f"SECUNDARIA · sus entradas que caen sobre una flecha (±{CERCA} min)")
print("="*74)
print(f"  con indicador  {100*pa:.1f} %   ({int(ca.sum())} de {len(ca)})")
print(f"  sin indicador  {100*pb:.1f} %   ({int(cb.sum())} de {len(cb)})")
print(f"  DIFERENCIA     {100*(pa-pb):+.1f} pt   ·   z = {z2:+.2f}"
      f"   ·   {'PASA' if abs(z2) > 1.96 else 'no pasa'}")

# ─── descriptivas, que NO deciden ───────────────────────────────────────────
print("\n" + "="*74); print("DESCRIPTIVAS · sin potencia, no deciden nada"); print("="*74)
print(f"{'':>16s} {'n':>4s} {'acierto':>9s} {'R neta':>9s} {'stop':>7s}")
for nom, g in (("con indicador", o[o.con]), ("sin indicador", o[~o.con])):
    r = g[g.mot.isin(["TP","SL"])]
    ac = 100*(r.mot == "TP").mean() if len(r) else float("nan")
    print(f"{nom:>16s} {len(g):4d} {ac:8.1f} % {g.neta.mean():+9.3f} {g.rgo.median():6.1f} p")
if len(o):
    vc = [s for s in vac if s in CON]; vs = [s for s in vac if s not in CON]
    print(f"  sesiones sin operar: {len(vc)} con indicador · {len(vs)} sin")

# ─── replicacion del 64,8 % ─────────────────────────────────────────────────
r = o[o.mot.isin(["TP","SL"])]
ac = (r.mot == "TP").mean() if len(r) else float("nan")
zr = (ac-GEO)/sqrt(GEO*(1-GEO)/len(r)) if len(r) else 0.0
zn = o.neta.mean()/(o.neta.std(ddof=1)/sqrt(len(o))) if len(o) > 1 else 0.0
print("\n" + "="*74); print("REPLICACIÓN · las 40 juntas"); print("="*74)
print(f"  acierto {100*ac:.1f} % sobre {len(r)} resueltas · z contra 33,3 % = {zr:+.2f}"
      f"   {'PASA' if zr > 1.64 else 'NO PASA'}")
print(f"  R neta/op {o.neta.mean():+.3f} · z = {zn:+.2f} · suma {o.neta.sum():+.1f} R")
if len(cta):
    print(f"  cuentas: {(cta.estado=='PASA').sum()} superadas · "
          f"{(cta.estado=='REVIENTA').sum()} reventadas")

# ─── las sentadas ───────────────────────────────────────────────────────────
if len(o) and o.tanda.notna().any():
    t = o.groupby("tanda").ses.nunique()
    print(f"\n  sentadas: {len(t)} · sesiones por sentada {dict(t)}")

print("\n" + "="*74); print("LAS CINCO PREDICCIONES FIRMADAS"); print("="*74)
pred = [
 ("1 · más operaciones con indicador, +0,3 a +1,2/sesión", 0.3 <= dif <= 1.2),
 ("2 · coincidencia >60 % con y ~35 % sin", pa > 0.60 and pb < 0.45),
 ("3 · su acierto baja con indicador, 0-12 pt, sin significar", None),
 ("4 · acierto de las 40 entre 55 % y 68 %", 0.55 <= ac <= 0.68),
 ("5 · menos de cuatro sentadas", (o.tanda.nunique() < 4) if o.tanda.notna().any() else None)]
for nom, v in pred:
    print(f"  {nom:56s} {'✓' if v else ('—' if v is None else '✗')}")
