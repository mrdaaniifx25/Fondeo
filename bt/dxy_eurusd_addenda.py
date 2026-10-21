"""Addenda de bt/dxy_eurusd.py: cuantas veces el filtro de confluencia cambia
algo, y por que la pendiente observada es -0,81 y no -0,576.

  python3 bt/dxy_eurusd_addenda.py
"""
import numpy as np, pandas as pd
from math import sqrt
src = open("bt/dxy_eurusd.py").read().split('print("="*96); print("1 ·')[0]
exec(compile(src, "d", "exec"))
print("8 · CUANTAS VECES EL FILTRO DE CONFLUENCIA CAMBIA ALGO")
mismo = np.sign(D.dE) == np.sign(D.dD)          # los dos al alza o los dos a la baja
print(f"  dias en que EURUSD y DXY se mueven en el MISMO sentido: "
      f"{100*mismo.mean():.2f} %  ({int(mismo.sum())} de {len(D)})")
print(f"  o sea: el filtro 'DXY a la baja Y EURUSD al alza' coincide con 'EURUSD")
print(f"  al alza' el {100*(1-mismo.mean()):.1f} % de los dias. Solo cambia algo en el "
      f"{100*mismo.mean():.1f} %.")
print("\n  Y en ESOS dias raros (los dos en el mismo sentido), que pasa despues?")
print(f"  {'caso':<40}{'n':>6}{'rend EURUSD 5d':>17}{'t':>8}")
fwd5 = D.lE.shift(-5) - D.lE
for et, m in (("los dos al alza", (D.dE>0)&(D.dD>0)),
              ("los dos a la baja", (D.dE<0)&(D.dD<0)),
              ("normal: euro arriba, DXY abajo", (D.dE>0)&(D.dD<0)),
              ("normal: euro abajo, DXY arriba", (D.dE<0)&(D.dD>0)),
              ("TODOS (control)", pd.Series(True, index=D.index))):
    f = fwd5[m].dropna().iloc[::5]
    if len(f) < 25: continue
    print(f"  {et:<40}{len(f):>6}{100*f.mean():>+16.4f}%"
          f"{f.mean()/(f.std(ddof=1)/sqrt(len(f))):>+8.2f}")

print("\n9 · LA PENDIENTE: por que -0,81 y no -0,576")
noe = D.noeur.diff()
print(f"  correlacion dEURUSD vs dNOEUR (cesta no-euro): {D.dE.corr(-noe):+.4f}")
print(f"  -> cuando el euro sube contra el dolar, las otras cinco divisas")
print(f"     tambien suben contra el dolar. La cesta no-euro NO diversifica:")
print(f"     amplifica. Por eso la pendiente observada (-0,81) es mayor que el")
print(f"     peso del euro (-0,576).")
r2n = D.dE.corr(-noe)**2
print(f"  R2 de la cesta no-euro contra EURUSD: {r2n:.4f}"
      f"  -> solo el {100*(1-r2n):.0f} % de la cesta es informacion nueva")
print(f"\n  INFORMACION REALMENTE INDEPENDIENTE en el DXY frente a EURUSD:")
print(f"    42,4 % de peso no-euro  x  {100*(1-r2n):.0f} % no explicado  = "
      f"{100*0.424*(1-r2n):.1f} % del DXY")
