"""Los dos bloques juntos: 53 operaciones, 40 sesiones.

Dos preguntas:
  1  ¿aguanta la ventaja si el coste real es peor de lo que suponemos?
  2  con 53 en vez de 23, ¿hay ya algo que separe sus ganadoras de sus perdedoras?

La 2 es EXPLORATORIA. Se marca como tal.

  python3 bt/examen_juntos.py
"""
import json, re, numpy as np, pandas as pd
from math import sqrt, erf
TZ, GEO = "Europe/Madrid", 1/3
z  = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x)))
p2 = lambda zz: 2*(1-0.5*(1+erf(abs(zz)/sqrt(2))))

def lee(f, dj, bloque):
    dias = {int(k): pd.Timestamp(v).date() for k,v in json.load(open(dj)).items()}
    out=[]
    for l in open(f):
        m = re.match(r"S(\d+) · (\d\d):(\d\d) (COMPRA|VENTA) ent ([\d.]+) sl \S+ \(([\d.]+)p\) "
                     r"tp \S+ -> (\S+) ([+-][\d.]+) R a las (\d\d):(\d\d)", l.strip())
        if not m: continue
        out.append(dict(bloque=bloque, s=int(m.group(1)), dia=dias[int(m.group(1))],
                        n=len(out)+1, min=int(m.group(2))*60+int(m.group(3)),
                        lado=1 if m.group(4)=="COMPRA" else -1, ent=float(m.group(5)),
                        rgo=float(m.group(6)), mot=m.group(7), R=float(m.group(8)),
                        dura=int(m.group(9))*60+int(m.group(10)) - (int(m.group(2))*60+int(m.group(3)))))
    return pd.DataFrame(out), sorted(dias.values())

a, i1 = lee("data/examen_respuestas_1.txt", "data/examen_dias.json", 1)
b, i2 = lee("data/examen_respuestas_2.txt", "data/examen_dias2.json", 2)
t = pd.concat([a, b], ignore_index=True)
idx = i1 + i2
print(f"{len(t)} operaciones · {len(idx)} sesiones\n")

print("="*72); print("1 · ¿AGUANTA SI EL COSTE ES PEOR?"); print("="*72)
print(f"  {'coste':>7s} {'neta/op':>9s} {'z':>7s} {'suma':>8s} {'por sesión':>11s} {'z sesión':>9s}")
print("  " + "-"*56)
for c in (1.28, 1.43, 1.58, 2.00, 2.50, 3.00):
    n = t.R - c/t.rgo
    por = pd.Series(n.values, index=t.dia).groupby(level=0).sum().reindex(idx).fillna(0)
    print(f"  {c:6.2f}p {n.mean():+9.3f} {z(n.to_numpy()):+7.2f} {n.sum():+8.2f} "
          f"{por.mean():+11.3f} {z(por.to_numpy()):+9.2f}")
be = np.polyfit([1.28,3.0], [ (t.R-1.28/t.rgo).mean(), (t.R-3.0/t.rgo).mean() ], 1)
print(f"\n  el coste al que su neta llegaría a cero: "
      f"{t.R.mean()/ (1/t.rgo).mean():.2f} pips por operación redonda")

print("\n" + "="*72); print("2 · GANADORAS CONTRA PERDEDORAS, CON LAS 53  (EXPLORATORIO)"); print("="*72)
t["gana"] = t.R > 0
G, P = t[t.gana], t[~t.gana]
print(f"  {len(G)} ganadoras · {len(P)} perdedoras")
print(f"  {'':22s} {'gana':>9s} {'pierde':>9s} {'dif':>9s} {'t':>7s} {'p':>8s}")
print("  " + "-"*68)
for c, nom in (("min","hora de entrada"), ("rgo","stop en pips"),
               ("dura","minutos hasta salir"), ("n","nº dentro del bloque"),
               ("s","nº de sesión")):
    g, p = G[c].astype(float), P[c].astype(float)
    ee = sqrt(g.var(ddof=1)/len(g) + p.var(ddof=1)/len(p))
    tt = (g.mean()-p.mean())/ee if ee>0 else 0
    print(f"  {nom:22s} {g.median():9.1f} {p.median():9.1f} {g.mean()-p.mean():+9.1f} "
          f"{tt:+7.2f} {p2(tt):8.4f}")
print("\n  por dirección:")
for lado, nom in ((1,"compras"), (-1,"ventas")):
    s = t[t.lado==lado]; r = s[s.mot.isin(["TP","SL"])]
    print(f"    {nom:9s} n={len(s):2d}  acierto {100*(r.mot=='TP').mean():5.1f} %  "
          f"neta {(s.R-1.43/s.rgo).mean():+.3f}")
print("\n  por bloque y mitad:")
for bl in (1,2):
    s = t[t.bloque==bl].sort_values("n")
    mitad = len(s)//2
    for nom, sub in (("1ª mitad", s.iloc[:mitad]), ("2ª mitad", s.iloc[mitad:])):
        r = sub[sub.mot.isin(["TP","SL"])]
        print(f"    bloque {bl} · {nom}  n={len(sub):2d}  acierto {100*(r.mot=='TP').mean():5.1f} %  "
              f"neta {(sub.R-1.43/sub.rgo).mean():+.3f}")
t.to_csv("data/examen_juntos.csv", index=False)
