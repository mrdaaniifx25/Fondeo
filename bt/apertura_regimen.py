"""La afirmacion del video: una estrategia rinde distinto segun el REGIMEN de
volatilidad, y la de volatilidad MEDIA es la buena.

Se prueba sobre la estrategia de la vela de apertura, que es la unica del
proyecto que ha superado sus nulos.

El regimen se clasifica de forma CAUSAL: percentil del ATR(20) diario dentro
de los 250 dias ANTERIORES. Nada del futuro.

  python3 bt/apertura_regimen.py
"""
import os, numpy as np, pandas as pd
os.environ.setdefault("NULOS","0")
exec(open("bt/apertura_eurusd.py").read().split("D = rejilla(M)")[0])

# --- ATR diario y percentil movil, todo con datos anteriores ---------------
D1 = M.set_index("t").resample("1440min").agg(
    h=("high","max"), l=("low","min"), c=("close","last")).dropna()
tr = pd.concat([D1.h-D1.l, (D1.h-D1.c.shift()).abs(), (D1.l-D1.c.shift()).abs()],
               axis=1).max(axis=1)
atr = tr.rolling(20).mean()
pct = atr.rolling(250).apply(lambda x: (x[:-1] < x[-1]).mean(), raw=True)  # causal
REG = pd.Series(np.where(pct < 1/3, "BAJA", np.where(pct < 2/3, "MEDIA", "ALTA")),
                index=D1.index)
b1 = np.sign(D1.c.diff()).to_numpy()

G = {d: g for d, g in M.groupby("d")}
dias = sorted(G)
regd = {}
for i, ts in enumerate(D1.index):
    if not pd.isna(pct.iloc[i]): regd[ts.date()] = REG.iloc[i]

print("=== LA ESTRATEGIA DE LA VELA DE APERTURA, POR REGIMEN DE VOLATILIDAD ===")
print("   (08:00 Londres · buffer 3 pips · objetivo 3R · con bias diario)\n")
R = []
for k in range(1, len(dias)):
    d = dias[k]
    sg = int(b1[min(k, len(b1)-1)]) if not np.isnan(b1[min(k,len(b1)-1)]) else 0
    r = dia_estr(G[d], G[dias[k-1]], 480, 3.0, 3.0, True, sg)
    if r is None: continue
    # el regimen del dia ANTERIOR, para que sea utilizable en el momento
    rg = regd.get(dias[k-1])
    if rg is None: continue
    R.append((rg, r, d))
T = pd.DataFrame(R, columns=["reg","R","dia"])
z = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v)>2 else np.nan
print(f"  {'regimen':>10} {'n':>5} {'% del total':>12} {'R neta':>10} {'z':>8} "
      f"{'acierto':>9}")
for rg in ("BAJA","MEDIA","ALTA"):
    x = T[T.reg==rg]
    if not len(x): continue
    print(f"  {rg:>10} {len(x):>5} {len(x)/len(T)*100:>11.1f}% {x.R.mean():>+10.4f} "
          f"{z(x.R):>+8.2f} {(x.R>0).mean()*100:>8.1f}%")
print(f"  {'TODOS':>10} {len(T):>5} {100.0:>11.1f}% {T.R.mean():>+10.4f} "
      f"{z(T.R):>+8.2f} {(T.R>0).mean()*100:>8.1f}%")

print(f"\n  ¿se cumple lo del video (MEDIA mejor que BAJA y ALTA)? ", end="")
m = {rg: T[T.reg==rg].R.mean() for rg in ("BAJA","MEDIA","ALTA") if len(T[T.reg==rg])}
if len(m)==3:
    ok = m["MEDIA"] > m["BAJA"] and m["MEDIA"] > m["ALTA"]
    print("SI" if ok else "NO")
    print(f"     BAJA {m['BAJA']:+.4f}  ·  MEDIA {m['MEDIA']:+.4f}  ·  ALTA {m['ALTA']:+.4f}")
print(f"\n  Aviso: son 3 subgrupos = 3 comparaciones. Con ventaja igual en los")
print(f"  tres, la probabilidad de que uno destaque por azar no es pequena.")
