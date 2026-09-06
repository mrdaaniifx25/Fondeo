"""Los secundarios declarados en el preregistro."""
import numpy as np, pandas as pd
from math import sqrt, erf
zf = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x))) if len(x) > 2 else np.nan
p1 = lambda z: 1-0.5*(1+erf(z/sqrt(2)))
t = pd.read_csv("data/escala_diaria.csv")
COSTE = {"EURUSD":1.43,"GBPUSD":1.80,"USDJPY":1.50,"XAUUSD":5.00,
         "NSXUSD":2.00,"SPXUSD":0.80,"GRXEUR":2.00}

print("="*88); print("1 · COMPOSICIÓN: ¿cuántas resuelven y cuántas mueren de viejas?")
print("="*88)
print(f"  {'':10s} {'n':>5s} {'TP':>7s} {'SL':>7s} {'cierre':>8s} {'días medianos':>14s}")
for regla in ("A","B","C"):
    for k in (1,2,3):
        s = t[(t.regla==regla)&(t.k==k)]
        if len(s) < 30: continue
        print(f"  {regla} k={k}     {len(s):5d} {100*(s.mot=='TP').mean():6.1f}% "
              f"{100*(s.mot=='SL').mean():6.1f}% {100*(s.mot=='cierre').mean():7.1f}% "
              f"{s.dias.median():13.0f}")

print("\n" + "="*88); print("2 · POR INSTRUMENTO · las celdas que importan"); print("="*88)
for regla, k in (("A",1), ("B",1), ("C",1)):
    s = t[(t.regla==regla)&(t.k==k)]
    print(f"\n  regla {regla}, k={k}   ({len(s)} operaciones)")
    print(f"    {'':9s} {'n':>5s} {'acierto':>9s} {'stop':>8s} {'c/s':>6s} {'R neta':>8s} {'z':>7s}")
    for ins, q in s.groupby("ins"):
        r = q[q.mot!="cierre"]
        print(f"    {ins:9s} {len(q):5d} {100*(r.mot=='TP').mean():8.1f}% {q.rgo_u.median():7.1f} "
              f"{100*COSTE[ins]/q.rgo_u.median():5.1f}% {q.neta.mean():+8.3f} "
              f"{zf(q.neta.to_numpy()):+7.2f}")

print("\n" + "="*88); print("3 · LA PEOR RACHA, EN R  (importa con el 10 % de tope)")
print("="*88)
for regla, k in (("A",1),("B",1),("C",1)):
    s = t[(t.regla==regla)&(t.k==k)].sort_values("dia")
    eq = s.neta.cumsum().to_numpy()
    dd = eq - np.maximum.accumulate(eq)
    print(f"  regla {regla} k={k}:  suma {s.neta.sum():+7.1f} R  ·  peor caída {dd.min():+6.1f} R"
          f"  ·  {len(s)/6.5:.0f} operaciones al año en los siete juntos")

print("\n" + "="*88)
print("4 · SI SE VA CON EL BARRIDO EN VEZ DE EN CONTRA  (regla A invertida)")
print("="*88)
print("""  Ojo: invertir no devuelve el signo cambiado, porque el coste se resta en las
  dos direcciones. La asimetría es 2*coste/stop.""")
for k in (1,):
    s = t[(t.regla=="A")&(t.k==k)]
    cs = np.array([COSTE[i] for i in s.ins])/s.rgo_u.to_numpy()
    bruta = s.R.to_numpy()
    inv = -bruta - cs                       # a 1:1 invertir es el espejo exacto
    print(f"  A k=1 tal cual   R neta {s.neta.mean():+.3f}  z {zf(s.neta.to_numpy()):+.2f}")
    print(f"  A k=1 invertida  R neta {inv.mean():+.3f}  z {zf(inv):+.2f}"
          f"   <- {'pasa' if zf(inv) > 2.77 else 'NO pasa el umbral'}")
    print(f"  la asimetría se come {2*cs.mean():.3f} R de los {abs(s.neta.mean()):.3f} disponibles")
