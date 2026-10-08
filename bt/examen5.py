"""docs/PREREGISTRO_examen5.md · el quinto bloque.

  python3 bt/examen5.py
"""
import json, numpy as np, pandas as pd
from math import sqrt, erf, comb
import importlib.util
spec = importlib.util.spec_from_file_location("lee5", "bt/examen5_lee.py")
lee5 = importlib.util.module_from_spec(spec); spec.loader.exec_module(lee5)

TZ, U, COSTE, GEO, INI, FIN = "Europe/Madrid", 1e-4, 1.43, 1/3, 480, 690
z  = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x)))
p1 = lambda zz: 1-0.5*(1+erf(zz/sqrt(2)))
def fisher(a,b,c,d):
    n,r1,c1 = a+b+c+d, a+b, a+c
    if min(a,b,c,d) < 0 or n == 0: return 1.0
    D = lambda k: comb(r1,k)*comb(n-r1,c1-k)/comb(n,c1)
    p0 = D(a)*(1+1e-9)
    return sum(D(k) for k in range(max(0,c1-(n-r1)), min(r1,c1)+1) if D(k) <= p0)

o, des, cta, vac = lee5.lee("data/examen_respuestas_5.txt")
DIAS = {int(k): pd.Timestamp(v).date() for k, v in json.load(open("data/examen_dias5.json")).items()}
o["dia"] = o.ses.map(DIAS)
idx = sorted(DIAS.values())
res = o[o.mot.isin(["TP","SL"])]
ac = (res.mot == "TP").mean()
zac = (ac-GEO)/sqrt(GEO*(1-GEO)/len(res))
zn = z(o.neta.to_numpy())
suyo = o.groupby("dia").neta.sum().reindex(idx).fillna(0)

print("="*74); print("BLOQUE 5 · 50 SESIONES"); print("="*74)
print(f"  operaciones            {len(o)}   en {o.ses.nunique()} sesiones ({vac} sin operar)"
      f"  ·  {len(o)/50:.2f} por sesión")
print(f"  desenlaces             TP {(o.mot=='TP').sum()} · SL {(o.mot=='SL').sum()} · "
      f"cierre {(o.mot=='cierre').sum()}")
print(f"  ACIERTO                {100*ac:.1f} %  sobre {len(res)}   ·   z = {zac:+.2f}")
print(f"  stop mediano           {o.rgo.median():.1f} p  ·  coste/riesgo "
      f"{100*(COSTE/o.rgo).mean():.1f} %")
print(f"  R BRUTA / op           {o.R.mean():+.3f}   ·   suma {o.R.sum():+.2f} R")
print(f"  R NETA  / op           {o.neta.mean():+.3f}   ·   z = {zn:+.2f}   ·   "
      f"suma {o.neta.sum():+.2f} R")
print(f"  por sesión             {suyo.mean():+.3f}   ·   z = {z(suyo.to_numpy()):+.2f}")

g = pd.read_csv("data/examen_regla5.csv"); g["dia"] = pd.to_datetime(g.dia).dt.date
regla = g.groupby("dia").neta.sum().reindex(idx).fillna(0)
dif = suyo - regla
zd = z(dif.to_numpy())
print(f"\n  la regla mecánica     {regla.mean():+.3f} R/sesión")
print(f"  DIFERENCIA emparejada {dif.mean():+.3f} R/sesión   ·   z = {zd:+.2f}")

print("\n" + "="*74); print("LOS TRES UMBRALES  (z > +1,64)"); print("="*74)
for nom, v in (("acierto sobre 33,3 %", zac), ("R neta por operación", zn),
               ("diferencia contra la regla", zd)):
    print(f"  {nom:32s} z = {v:+6.2f}   {'PASA' if v > 1.64 else 'NO PASA'}")

print("\n" + "="*74); print("EL CONTRASTE PRINCIPAL: SUS DESCARTES"); print("="*74)
print(f"  descartes registrados: {len(des)}  (predije entre 25 y 75)")
if len(des) < 10:
    print("  NO SE PUEDE CORRER. Con tres descartes -y dos de ellos duplicados-")
    print("  no hay grupo de control. El contraste principal del bloque queda vacío.")
    print(f"  {des[['ses','min','lado','rgo','motivo']].to_string(index=False)}")

print("\n" + "="*74); print("SECUNDARIO 1 · LA CONFIANZA"); print("="*74)
for c in ("claro", "normal", "dudando"):
    s = o[o.conf == c]
    if not len(s): continue
    r = s[s.mot.isin(["TP","SL"])]
    print(f"  {c:9s} n={len(s):3d} ({100*len(s)/len(o):4.1f} %)  acierto "
          f"{100*(r.mot=='TP').mean() if len(r) else float('nan'):5.1f} %  "
          f"R neta {s.neta.mean():+.3f}")
a, b = o[o.conf=="claro"], o[o.conf=="normal"]
ra, rb = a[a.mot.isin(["TP","SL"])], b[b.mot.isin(["TP","SL"])]
print(f"  claro contra normal: Fisher p = "
      f"{fisher(int((ra.mot=='TP').sum()), int((ra.mot=='SL').sum()), int((rb.mot=='TP').sum()), int((rb.mot=='SL').sum())):.3f}")

print("\n" + "="*74); print("SECUNDARIO 2 · EL INDICADOR (sorteado, 25 sesiones cada rama)")
print("="*74)
for v, nom in ((True, "con indicador"), (False, "sin indicador")):
    s = o[o.ind == v]
    r = s[s.mot.isin(["TP","SL"])]
    ses = s.ses.nunique()
    print(f"  {nom:15s} {len(s):3d} ops en {ses} sesiones ({len(s)/25:.2f} por sesión)  "
          f"acierto {100*(r.mot=='TP').mean():5.1f} %  R neta {s.neta.mean():+.3f}  "
          f"stop {s.rgo.median():.1f}p")
a, b = o[o.ind], o[~o.ind]
ra, rb = a[a.mot.isin(["TP","SL"])], b[b.mot.isin(["TP","SL"])]
print(f"  Fisher p = {fisher(int((ra.mot=='TP').sum()), int((ra.mot=='SL').sum()), int((rb.mot=='TP').sum()), int((rb.mot=='SL').sum())):.3f}")
o.to_csv("data/examen5_ops.csv", index=False)
