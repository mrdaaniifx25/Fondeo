"""Diagnostico de bt/indicadores.py: que series mandan, si el relleno de
comillas lo explica, que queda en el universo liquido y si las once familias
son una sola apuesta.

  python3 bt/indicadores_diagnostico.py
"""
import numpy as np, pandas as pd
from math import sqrt
src=open("bt/indicadores.py").read()
exec(compile(src.split('print(f"{\'familia\'')[0],"ind","exec"))

print("=== 1. que series mandan (peso = 1/vol relativo) y cuanto aportan ===")
sig = SEN["Donchian 20"]
ap = (sig*Z).where(OK)
tot = ap.sum().sort_values(ascending=False)
print("  top 8 :", ", ".join(f"{k.replace('FX ','')} {v:.0f}" for k,v in tot.head(8).items()))
print("  cola 4:", ", ".join(f"{k.replace('FX ','')} {v:.0f}" for k,v in tot.tail(4).items()))
print("  las 25 aportan", f"{tot.sum():.0f}", "· las 5 primeras", f"{tot.head(5).sum():.0f}",
      f"({100*tot.head(5).sum()/tot.sum():.0f} %)")

print("\n=== 2. dias RELLENADOS por ffill (comilla repetida) ===")
raw = pd.DataFrame(S).sort_index(); raw = raw[raw.index>="1971-01-01"]
crudo = raw.resample("B").last()
rell = crudo.isna() & P.notna()
for a,b in (("1971","1999"),("2000","2012"),("2013","2026")):
    m=(P.index.year>=int(a))&(P.index.year<=int(b))
    print(f"  {a}-{b}: {100*rell[m].sum().sum()/max(P[m].notna().sum().sum(),1):.1f} % rellenados"
          f" · rendimiento exactamente CERO: {100*(R[m]==0).sum().sum()/max(R[m].notna().sum().sum(),1):.1f} %")

print("\n=== 3. la misma prueba SIN rellenar y SIN dias de rendimiento cero ===")
OK2 = OK & (R != 0) & crudo.notna()
Z2 = (R/VOL).where(OK2)
def men2(sig, ok, z, coste=COSTE):
    p=(sig*z).where(ok)
    f=(sig!=sig.shift(1))&ok&ok.shift(1).fillna(False)
    p=p-f.astype(float)*coste*sig.abs()
    n=p.notna().sum(axis=1); d=p.mean(axis=1)[n>=5].dropna()
    return d.resample("ME").sum()[d.resample("ME").count()>=10]
def tt(m): return (m.mean()/(m.std(ddof=1)/sqrt(len(m))), m.mean()/m.std(ddof=1)*sqrt(12)) if len(m)>=24 else (np.nan,np.nan)
print(f"{'familia':<20}{'meses':>7}{'NETO':>9}{'t':>7}{'Sharpe':>8}   |  1971-99   2000-12   2013-26")
for k in ("MM 50/200","MM 20/100","Donchian 20","Donchian 55","canal ATR 20/2","ROC 250","ROC 20","MACD 12/26/9","RSI 14 momento","RSI 14 reversion"):
    m=men2(SEN[k],OK2,Z2); t,sh=tt(m); out=""
    for a,b in (("1971","1999"),("2000","2012"),("2013","2026")):
        x=m[(m.index.year>=int(a))&(m.index.year<=int(b))]; t2,_=tt(x)
        out+=f"  t{t2:>+6.2f}" if len(x)>=24 else f"{'-':>9}"
    print(f"  {k:<18}{len(m):>7}{m.mean():>+9.4f}{t:>+7.2f}{sh:>+8.2f}   |{out}")

print("\n=== 4. solo G10 + materias primas (divisas flotantes y liquidas) ===")
G10=[c for c in P.columns if any(x in c for x in ("Euro","Japan","United Kingdom","Switzerland",
     "Canada","Australia","New Zealand","Sweden","Norway","Denmark"))]+["WTI","Brent","gas","S&P 500"]
G10=[c for c in G10 if c in P.columns]
print("  ", len(G10), "series:", ", ".join(c.replace("FX ","") for c in G10))
ok3=OK2[G10]; z3=Z2[G10]
print(f"{'familia':<20}{'meses':>7}{'NETO':>9}{'t':>7}{'Sharpe':>8}   |  1971-99   2000-12   2013-26")
for k in ("MM 50/200","MM 20/100","Donchian 20","Donchian 55","canal ATR 20/2","ROC 250","ROC 20","MACD 12/26/9","RSI 14 momento","RSI 14 reversion"):
    m=men2(SEN[k][G10],ok3,z3); t,sh=tt(m); out=""
    for a,b in (("1971","1999"),("2000","2012"),("2013","2026")):
        x=m[(m.index.year>=int(a))&(m.index.year<=int(b))]; t2,_=tt(x)
        out+=f"  t{t2:>+6.2f}" if len(x)>=24 else f"{'-':>9}"
    print(f"  {k:<18}{len(m):>7}{m.mean():>+9.4f}{t:>+7.2f}{sh:>+8.2f}   |{out}")

print("\n=== 5. son once estrategias o una? correlacion de los RENDIMIENTOS mensuales ===")
fams=["MM 50/200","MM 20/100","MM 10/50","MACD 12/26/9","MACD 12/26","RSI 14 momento",
      "Donchian 20","Donchian 55","canal ATR 20/2","ROC 250","ROC 20"]
M=pd.DataFrame({k: men2(SEN[k],OK2,Z2) for k in fams}).dropna()
C=M.corr()
iu=np.triu_indices(len(fams),1)
print(f"  correlacion media entre las once: {C.values[iu].mean():.2f}"
      f"   minima {C.values[iu].min():.2f}   maxima {C.values[iu].max():.2f}")
print(f"  meses en que TODAS van en el mismo sentido: {100*((M>0).all(axis=1)|(M<0).all(axis=1)).mean():.0f} %")
mix=M.mean(axis=1); t,sh=tt(mix)
print(f"  mezcla de las once: t {t:+.2f}  Sharpe {sh:+.2f}   ·  mejor individual Sharpe "
      f"{max(tt(M[k])[1] for k in fams):+.2f}")
print("\n=== 6. lo mismo, solo G10+materias, 2013-2026 ===")
MG=pd.DataFrame({k: men2(SEN[k][G10],ok3,z3) for k in fams}).dropna()
mg=MG[MG.index.year>=2013]; mx=mg.mean(axis=1); t,sh=tt(mx)
print(f"  mezcla de las once, 2013-2026: efecto {mx.mean():+.4f}  t {t:+.2f}  Sharpe {sh:+.2f}"
      f"  ·  meses {len(mx)}")
print(f"  familias positivas en ese tramo: {(mg.mean()>0).sum()} de 11")
print("\n=== 7. cuanto coste aguanta el tramo reciente en G10 ===")
for c in (0.0,0.02,0.05,0.10):
    m=men2(SEN["Donchian 55"][G10],ok3,z3,c); m=m[m.index.year>=2013]; t,_=tt(m)
    print(f"  Donchian 55 · coste {c:.2f}: efecto {m.mean():+.4f}  t {t:+.2f}")
