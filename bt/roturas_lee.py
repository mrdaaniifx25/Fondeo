"""Analizador del volcado de «Entro / No entro».

Se escribe y se prueba ANTES de que lo haga, como en el bloque 4.

  python3 bt/roturas_lee.py [fichero]
"""
import json, re, sys
import numpy as np, pandas as pd
from math import sqrt, erf, comb

COSTE = 1.43
LIN = re.compile(r"^S(?P<ses>\d+) · (?P<h>\d\d):(?P<m>\d\d) (?P<lado>COMPRA|VENTA)\s+"
                 r"\((?P<rgo>[\d.]+)p\)\s+(?P<dec>ENTRO|no entro)\s+-> (?P<mot>\S+) "
                 r"(?P<R>[+-][\d.]+) R\s*$")
p1 = lambda z: 1-0.5*(1+erf(z/sqrt(2)))
def fisher(a,b,c,d):
    n,r1,c1 = a+b+c+d, a+b, a+c
    if min(a,b,c,d) < 0 or n == 0: return 1.0
    D = lambda k: comb(r1,k)*comb(n-r1,c1-k)/comb(n,c1)
    p0 = D(a)*(1+1e-9)
    return sum(D(k) for k in range(max(0,c1-(n-r1)), min(r1,c1)+1) if D(k) <= p0)

def lee(ruta):
    out = []
    for l in open(ruta, encoding="utf-8"):
        m = LIN.match(l.rstrip("\n"))
        if not m: continue
        d = m.groupdict()
        rgo = float(d["rgo"]); R = float(d["R"])
        out.append(dict(ses=int(d["ses"]), min=int(d["h"])*60+int(d["m"])-480,
                        lado=1 if d["lado"].strip()=="COMPRA" else -1, rgo=rgo,
                        si=d["dec"]=="ENTRO", mot=d["mot"], R=R, neta=R-COSTE/rgo))
    return pd.DataFrame(out)

if __name__ == "__main__":
    t = lee(sys.argv[1] if len(sys.argv) > 1 else "data/roturas_prueba.txt")
    print(f"{len(t)} decisiones leídas · {t.ses.nunique()} sesiones")
    if not len(t): sys.exit(1)
    t["res"] = t.mot.isin(["TP","SL"])
    ac = lambda s: 100*(s[s.res].mot=="TP").mean() if s.res.any() else float("nan")
    A, B = t[t.si], t[~t.si]
    print("\n" + "="*70); print("CONTRASTE PRINCIPAL"); print("="*70)
    print(f"  {'':22s} {'n':>5s} {'acierto':>9s} {'R neta':>9s} {'stop':>7s}")
    for nom, s in (("las que TOMA", A), ("las que DEJA pasar", B), ("todas", t)):
        print(f"  {nom:22s} {len(s):5d} {ac(s):8.1f}% {s.neta.mean():+9.3f} "
              f"{s.rgo.median():6.1f}p")
    ra, rb = A[A.res], B[B.res]
    if len(ra) >= 5:
        pa, pb = (ra.mot=="TP").mean(), (rb.mot=="TP").mean()
        ee = sqrt(pa*(1-pa)/len(ra) + pb*(1-pb)/len(rb))
        z = (pa-pb)/ee if ee > 0 else 0
        print(f"\n  diferencia {100*(pa-pb):+.1f} puntos   ·   z = {z:+.2f}   ·   "
              f"p = {p1(z):.5f}   ·   umbral z > +1,96")
        print(f"  Fisher exacto: p = {fisher(int((ra.mot=='TP').sum()), int((ra.mot=='SL').sum()), int((rb.mot=='TP').sum()), int((rb.mot=='SL').sum())):.5f}")
        print(f"  {'PASA' if z > 1.96 else 'NO PASA'} el umbral firmado")
    print("\n" + "="*70); print("QUÉ DISTINGUE A LAS QUE TOMA"); print("="*70)
    print(f"  {'':26s} {'toma':>9s} {'deja':>9s} {'dif':>8s}")
    for nom, col in (("stop en pips", "rgo"), ("minutos desde las 08:00", "min")):
        print(f"  {nom:26s} {A[col].median():8.1f} {B[col].median():8.1f} "
              f"{A[col].median()-B[col].median():+8.1f}")
    print(f"  {'compras':26s} {100*(A.lado>0).mean():8.1f}% {100*(B.lado>0).mean():8.1f}%")
    print(f"\n  acepta el {100*len(A)/len(t):.1f} % de las roturas (predije 20-45 de 250)")
    print(f"  por sesión: {A.groupby('ses').size().reindex(range(1,11)).fillna(0).astype(int).tolist()}")
