"""Los 16 patrones contra sus 94 ganadoras, sus 48 perdedoras y los controles.

  python3 bt/patrones_informe.py
"""
import numpy as np, pandas as pd
from math import sqrt, erf, comb
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
def fisher(a,b,c,d):
    n,r1,c1 = a+b+c+d, a+b, a+c
    D = lambda k: comb(r1,k)*comb(n-r1,c1-k)/comb(n,c1)
    p0 = D(a)*(1+1e-9)
    return sum(D(k) for k in range(max(0,c1-(n-r1)), min(r1,c1)+1) if D(k) <= p0)

B = pd.read_csv("data/patrones_velas.csv")
B["dia"] = pd.to_datetime(B.dia).dt.date
S   = B[B.suya]
TP  = S[S.mot == "TP"]; SL = S[S.mot == "SL"]
CTL = B[~B.suya & ~B.ocupada]
print(f"{len(TP)} ganadoras · {len(SL)} perdedoras · {len(S)-len(TP)-len(SL)} cerradas a las 11:30")
print(f"{len(CTL):,} velas de control\n")

TODOS = ["martillo","martillo invertido","envolvente alcista","penetrante",
         "estrella de la mañana","tres soldados blancos","triple formación alcista",
         "hombre colgado","estrella fugaz","envolvente bajista",
         "cubierta de nube oscura","estrella del atardecer","tres cuervos negros",
         "triple formación bajista","doji","trompo"]
tiene = lambda d, p: d.patrones.fillna("").str.split("+").apply(lambda x: p in x)

print("="*92)
print("LOS 16 PATRONES · en la vela de M5 en la que entra")
print("="*92)
print(f"  {'patrón':26s} {'TP':>7s} {'SL':>7s} {'control':>8s}   {'TP vs SL':>9s}  {'suyas vs control':>17s}")
print("  " + "-"*88)
for p in TODOS:
    a, b = int(tiene(TP,p).sum()), int(tiene(SL,p).sum())
    ctl = tiene(CTL,p).mean()
    su  = tiene(S,p).mean()
    pf  = fisher(a, len(TP)-a, b, len(SL)-b) if (a+b) else 1.0
    pp  = (tiene(S,p).sum()+tiene(CTL,p).sum())/(len(S)+len(CTL))
    ee  = sqrt(pp*(1-pp)*(1/len(S)+1/len(CTL))) if pp > 0 else 1
    zz  = (su-ctl)/ee if ee > 0 else 0
    print(f"  {p:26s} {a:3d} {100*a/len(TP):4.0f}% {b:3d} {100*b/len(SL):4.0f}% "
          f"{100*ctl:7.1f}%   p={pf:7.3f}  {100*(su-ctl):+7.1f}pt z={zz:+5.2f}"
          + ("  *" if pf < 0.05/16 or abs(zz) > 3.2 else ""))

print("\n" + "="*92)
print("¿EL PATRÓN VA EN SU MISMA DIRECCIÓN?")
print("="*92)
for nom, d in (("ganadoras", TP), ("perdedoras", SL), ("todas las suyas", S)):
    af = ((d.alcista & (d.lado > 0)) | (d.bajista & (d.lado < 0))).sum()
    en = ((d.alcista & (d.lado < 0)) | (d.bajista & (d.lado > 0))).sum()
    nin = (~d.alcista & ~d.bajista).sum()
    print(f"  {nom:16s} a favor {af:3d} ({100*af/len(d):4.1f} %) · "
          f"en contra {en:3d} ({100*en/len(d):4.1f} %) · sin patrón direccional "
          f"{nin:3d} ({100*nin/len(d):4.1f} %)")

print("\n" + "="*92); print("EL TIPO DE CIERRE DE LA VELA"); print("="*92)
print(f"  {'':22s} {'TP':>8s} {'SL':>8s} {'control':>9s}   {'TP vs SL':>10s}")
print("  " + "-"*66)
for col, vals in (("cierre", ["cierra arriba","cierra en medio","cierra abajo"]),
                  ("cuerpo", ["cuerpo lleno","cuerpo medio","cuerpo pequeño"])):
    for v in vals:
        a, b = int((TP[col]==v).sum()), int((SL[col]==v).sum())
        pf = fisher(a, len(TP)-a, b, len(SL)-b)
        print(f"  {v:22s} {100*a/len(TP):7.1f}% {100*b/len(SL):7.1f}% "
              f"{100*(CTL[col]==v).mean():8.1f}%   p={pf:8.3f}")

print("\n  el cierre VISTO DESDE SU DIRECCIÓN (a favor = cierra en su extremo):")
for nom, d in (("ganadoras", TP), ("perdedoras", SL), ("control (compras)", None)):
    if d is None: continue
    pos = np.where(d.lado > 0, d.pos_cierre, 1-d.pos_cierre)
    print(f"    {nom:20s} mediana {np.median(pos):.2f}  ·  "
          f"cierra en el tercio a su favor: {100*np.mean(pos >= 2/3):.0f} %")
posS = np.where(S.lado > 0, S.pos_cierre, 1-S.pos_cierre)
print(f"    {'control':20s} mediana 0.50 por construcción (la vela no tiene dirección elegida)")
print(f"    todas las suyas      mediana {np.median(posS):.2f}  ·  "
      f"tercio a favor {100*np.mean(posS >= 2/3):.0f} %")
print(f"    la vela va en su misma dirección (verde y compra, roja y venta): "
      f"{100*np.mean((S.verde & (S.lado>0)) | (~S.verde & (S.lado<0))):.0f} % de las suyas · "
      f"TP {100*np.mean((TP.verde & (TP.lado>0)) | (~TP.verde & (TP.lado<0))):.0f} % · "
      f"SL {100*np.mean((SL.verde & (SL.lado>0)) | (~SL.verde & (SL.lado<0))):.0f} %")

print("\n" + "="*92); print("EL CONTEXTO: M15 Y M5 EN EL MOMENTO DE LA ENTRADA"); print("="*92)
print(f"  {'':34s} {'TP':>8s} {'SL':>8s}   {'p':>8s}")
print("  " + "-"*62)
for nom, f in (("la última M15 cerrada va con él", lambda d: d.m15dir == d.lado),
               ("la tendencia de M15 va con él",   lambda d: d.m15tend == d.lado),
               ("la tendencia de M5 va con él",    lambda d: d.m5tend == d.lado),
               ("la vela de M5 va con él",         lambda d: (d.verde) == (d.lado > 0)),
               ("está en el tercio alto de la M15",lambda d: d.m15pos >= 2/3),
               ("está en el tercio bajo de la M15", lambda d: d.m15pos <= 1/3)):
    a, b = int(f(TP).sum()), int(f(SL).sum())
    print(f"  {nom:34s} {100*a/len(TP):7.1f}% {100*b/len(SL):7.1f}%   "
          f"p={fisher(a, len(TP)-a, b, len(SL)-b):8.3f}")
print("\n  donde queda el precio dentro de la vela de M15 en curso, desde su dirección:")
for nom, d in (("ganadoras", TP), ("perdedoras", SL)):
    q = np.where(d.lado > 0, d.m15pos, 1-d.m15pos)
    print(f"    {nom:12s} mediana {np.median(q):.2f}  ·  en el tercio a su favor "
          f"{100*np.mean(q >= 2/3):.0f} %  ·  en contra {100*np.mean(q <= 1/3):.0f} %")

print("\n" + "="*92)
print("EL ÚNICO HALLAZGO: EL TAMAÑO DEL CUERPO DE LA VELA EN LA QUE ENTRA")
print("="*92)
t = pd.read_csv("data/operaciones_150.csv"); t["dia"] = pd.to_datetime(t.dia).dt.date
S2 = S.merge(t[["dia","ent_min","rgo","R","mot"]].rename(columns={"R":"R2","mot":"mot2"}),
             on="dia", how="left")
S2 = S2[(S2.ent_min >= S2.cierre_min) & (S2.ent_min < S2.cierre_min+5)].drop_duplicates(
        subset=["dia","cierre_min"])
S2["neta"] = S2.R2 - 1.43/S2.rgo
print(f"  emparejadas {len(S2)} de {len(S)} con su stop real\n")
print(f"  {'cuerpo de la vela':22s} {'n':>4s} {'acierto':>9s} {'R neta':>9s} "
      f"{'stop':>7s} {'bloque 1-2-3-4'}")
print("  " + "-"*76)
bl = pd.read_csv("data/contexto_suyas.csv")
for v in ("cuerpo lleno","cuerpo medio","cuerpo pequeño"):
    s = S2[S2.cuerpo == v]; r = s[s.mot2.isin(["TP","SL"])]
    print(f"  {v:22s} {len(s):4d} {100*(r.mot2=='TP').mean():8.1f}% {s.neta.mean():+9.3f} "
          f"{s.rgo.median():6.1f}p")
lleno = S2.cuerpo == "cuerpo lleno"
a = S2[lleno]; b = S2[~lleno]
ra, rb = a[a.mot2.isin(["TP","SL"])], b[b.mot2.isin(["TP","SL"])]
print(f"\n  {'CUERPO LLENO':22s} {len(a):4d} {100*(ra.mot2=='TP').mean():8.1f}% {a.neta.mean():+9.3f}")
print(f"  {'todo lo demás':22s} {len(b):4d} {100*(rb.mot2=='TP').mean():8.1f}% {b.neta.mean():+9.3f}")
print(f"  Fisher: p = {fisher(int((ra.mot2=='TP').sum()), int((ra.mot2=='SL').sum()), int((rb.mot2=='TP').sum()), int((rb.mot2=='SL').sum())):.4f}"
      f"   (28 contrastes en este informe · Bonferroni pide p < 0,0018)")

print("\n  ¿aguanta en los cuatro bloques por separado?")
D2 = {d: i for i, d in enumerate(sorted(set(bl.dia)))}
bl["dia"] = pd.to_datetime(bl.dia).dt.date
mapb = dict(zip(zip(bl.dia, bl.ent_min), bl.ses*0))   # no hay columna de bloque: se deduce
import json
for nb, dj in enumerate(["data/examen_dias.json","data/examen_dias2.json",
                         "data/examen_dias3.json","data/examen_dias4.json"], 1):
    dd = {pd.Timestamp(v).date() for v in json.load(open(dj)).values()}
    s = S2[S2.dia.isin(dd)]
    if not len(s): continue
    al, ao = s[s.cuerpo=="cuerpo lleno"], s[s.cuerpo!="cuerpo lleno"]
    f = lambda x: (100*(x[x.mot2.isin(['TP','SL'])].mot2=='TP').mean()) if len(x) else float('nan')
    print(f"    bloque {nb}:  cuerpo lleno {len(al):2d} ops {f(al):5.1f} %   ·   "
          f"resto {len(ao):2d} ops {f(ao):5.1f} %")

print("\n  ¿es solo que el stop cambia? (si el cuerpo es grande, el stop se aleja)")
for v in ("cuerpo lleno","cuerpo medio","cuerpo pequeño"):
    s = S2[S2.cuerpo == v]
    print(f"    {v:16s} stop mediano {s.rgo.median():4.1f} p  ·  coste sobre riesgo "
          f"{100*(1.43/s.rgo).mean():4.1f} %  ·  R bruta {s.R2.mean():+.3f}")
