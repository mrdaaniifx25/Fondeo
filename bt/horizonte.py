"""¿Y si el problema no es el patron sino el horizonte?

Todo lo probado hasta ahora opera en minutos: stops de 10-20 pips y un coste de
1.2 pips, o sea entre el 6% y el 12% del riesgo en CADA operacion. A ese peaje
hace falta una ventaja enorme solo para empatar.

Aqui se prueba lo contrario: seguimiento de tendencia en diario, posicion
continua, sin stops, con muy poca rotacion. El coste deja de ser el problema.
"""
import numpy as np, pandas as pd
from math import sqrt, erf

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
d = m1.set_index("ts").resample("1D").agg(
    open=("open","first"), high=("high","max"), low=("low","min"),
    close=("close","last")).dropna().reset_index()
d["ret"] = d.close.pct_change()
print(f"EURUSD diario: {len(d)} sesiones | {d.ts.min().date()} a {d.ts.max().date()}")
print(f"Comprar y mantener: {100*(d.close.iloc[-1]/d.close.iloc[0]-1):+.1f}% en el periodo")
print(f"Volatilidad anualizada: {100*d.ret.std()*sqrt(252):.1f}%\n")

COSTE_REL = 1.2*0.0001/1.10   # 1,2 pips sobre un precio de ~1,10

def evalua(pos, nombre):
    """pos: serie de -1/0/+1 aplicada al retorno del dia SIGUIENTE."""
    pos = pd.Series(pos, index=d.index).shift(1).fillna(0)
    giros = (pos.diff().abs()/2).fillna(0)
    bruto = pos * d.ret.fillna(0)
    neto = bruto - giros*COSTE_REL
    n = int(giros.sum())
    eq = float((1+neto).prod())
    curva = (1+neto).cumprod()
    dd = float((1 - curva/curva.cummax()).max())
    ann = eq**(252/len(d)) - 1
    sharpe = neto.mean()/neto.std()*sqrt(252) if neto.std()>0 else 0
    z = neto.mean()/(neto.std()/sqrt(len(neto)))
    p = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
    print(f"  {nombre:34s} giros {n:>4} | anual {100*ann:>+6.2f}% | Sharpe {sharpe:>+5.2f} "
          f"| maxDD {100*dd:>5.1f}% | p {p:.3f}")
    return dict(nombre=nombre, ann=ann, sharpe=sharpe, dd=dd, p=p, giros=n)

print("=== A · TENDENCIA: precio frente a su media movil ===")
res=[]
for n in (20, 50, 100, 200):
    sma = d.close.rolling(n).mean()
    res.append(evalua(np.sign(d.close - sma).fillna(0), f"precio vs SMA {n}"))

print("\n=== B · TENDENCIA: signo del retorno de N dias ===")
for n in (20, 60, 120, 250):
    res.append(evalua(np.sign(d.close/d.close.shift(n) - 1).fillna(0), f"momento {n} dias"))

print("\n=== C · CRUCE DE MEDIAS ===")
for a,b in ((20,100),(50,200),(10,50)):
    res.append(evalua(np.sign(d.close.rolling(a).mean()-d.close.rolling(b).mean()).fillna(0),
                      f"cruce SMA {a}/{b}"))

print("\n=== D · CONTROL: lo contrario (reversion) ===")
for n in (20, 100):
    sma = d.close.rolling(n).mean()
    res.append(evalua(-np.sign(d.close - sma).fillna(0), f"reversion vs SMA {n}"))

print("\n=== E · CONTROL: posicion aleatoria con la misma rotacion ===")
rng = np.random.default_rng(0); ann=[]
for s in range(200):
    r2 = np.random.default_rng(s)
    p = pd.Series(np.where(r2.random(len(d))<0.5,-1,1)).rolling(50).apply(lambda x: np.sign(x.mean()) or 1).fillna(0)
    pos = p.shift(1).fillna(0); giros=(pos.diff().abs()/2).fillna(0)
    neto = pos*d.ret.fillna(0) - giros*COSTE_REL
    ann.append(float((1+neto).prod())**(252/len(d))-1)
ann=np.array(ann)
print(f"  200 corridas aleatorias: anual medio {100*ann.mean():+.2f}% (sd {100*ann.std():.2f}pp)")
mejor = max([r for r in res if 'reversion' not in r['nombre']], key=lambda r: r['sharpe'])
print(f"  mejor tendencia: {mejor['nombre']} anual {100*mejor['ann']:+.2f}% "
      f"-> {(mejor['ann']-ann.mean())/ann.std():+.2f} sigmas")

print("\n=== F · CUANTO PESA EL COSTE AQUI ===")
sma = d.close.rolling(100).mean(); pos = pd.Series(np.sign(d.close-sma).fillna(0)).shift(1).fillna(0)
giros = int((pos.diff().abs()/2).fillna(0).sum())
bruto = float((1+pos*d.ret.fillna(0)).prod())**(252/len(d))-1
neto  = float((1+pos*d.ret.fillna(0)-(pos.diff().abs()/2).fillna(0)*COSTE_REL).prod())**(252/len(d))-1
print(f"  SMA 100: {giros} giros en {len(d)} sesiones")
print(f"  bruto {100*bruto:+.2f}% anual | neto {100*neto:+.2f}% anual "
      f"| el coste se lleva {100*(bruto-neto)/abs(bruto) if bruto else 0:.1f}% del bruto")
print("  (recuerda: en el CRT intradia el coste se llevaba el 34%)")
