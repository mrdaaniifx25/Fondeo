"""La rejilla completa: cada indicador clasico x cada temporalidad, en SUS datos.

Sin pre-registro porque no hay hipotesis que firmar: es un censo. Se publican
las 96 celdas, salgan como salgan, para que el usuario mire el grid entero en
vez de fiarse de un resumen.

Instrumentos suyos (M1): EURUSD 2021-2026, oro y DAX 2023-2026.
Temporalidades: M15, H1, H4, D1.
El estadistico va sobre los MESES.

  python3 bt/rejilla_indicadores.py
"""
import numpy as np, pandas as pd
from math import sqrt

INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 1.43),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 35.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  1.6)]
TF = [("M15", 15), ("H1", 60), ("H4", 240), ("D1", 1440)]
VENT = 36

def barras(M, minutos):
    k = M.ts.dt.floor(f"{minutos}min")
    g = M.groupby(k, sort=True)
    b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"))
    return b[b.index.notna()]

def sen(b):
    P = b.c
    sma = lambda n: P.rolling(n).mean()
    ema = lambda n: P.ewm(span=n, adjust=False).mean()
    d = P.diff()
    up = d.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rsi = 100 - 100/(1 + up/dn.replace(0, np.nan))
    macd = ema(12) - ema(26)
    tr = pd.concat([b.h-b.l, (b.h-P.shift(1)).abs(), (b.l-P.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.rolling(20).mean()
    per = lambda x: x.replace(0, np.nan).ffill().fillna(0)
    rev = pd.Series(np.nan, index=P.index)
    rev[rsi < 30] = 1.0; rev[rsi > 70] = -1.0
    rev = rev.ffill().fillna(0)
    return {
      "RSI 14 momento":   np.sign(rsi - 50),
      "RSI 14 reversion": rev,
      "MACD 12/26/9":     np.sign(macd - macd.ewm(span=9, adjust=False).mean()),
      "MACD 12/26":       np.sign(macd),
      "MM 20/100":        np.sign(sma(20) - sma(100)),
      "MM 50/200":        np.sign(sma(50) - sma(200)),
      "Donchian 20":      per(np.sign((P >= b.h.rolling(20).max().shift(1)).astype(float)
                                     -(P <= b.l.rolling(20).min().shift(1)).astype(float))),
      "Donchian 55":      per(np.sign((P >= b.h.rolling(55).max().shift(1)).astype(float)
                                     -(P <= b.l.rolling(55).min().shift(1)).astype(float))),
      "canal ATR 20/2":   per(np.sign((P > ema(20)+2*atr).astype(float)
                                     -(P < ema(20)-2*atr).astype(float))),
    }

def tt(m):
    if len(m) < 12 or m.std(ddof=1) == 0: return np.nan, np.nan
    return m.mean()/(m.std(ddof=1)/sqrt(len(m))), m.mean()/m.std(ddof=1)*sqrt(12)

FIL = {}
for nom, ruta, U, coste in INS:
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts")
    for et, mi in TF:
        b = barras(M, mi)
        r = np.log(b.c).diff()
        vol = r.rolling(VENT).std().shift(1)
        ok = (vol > 0) & r.notna() & vol.notna()
        z = (r/vol).where(ok)
        # coste por cambio, en unidades del ruido de ESA temporalidad
        cr = (coste*U/b.c) / vol
        for k, s in sen(b).items():
            s = s.shift(1).where(ok)
            p = (s*z)
            f = (s != s.shift(1)) & ok
            pb = p.dropna()
            pn = (p - f.astype(float)*cr*s.abs()).dropna()
            mb = pb.resample("ME").sum(); mn = pn.resample("ME").sum()
            mb = mb[pb.resample("ME").count() >= 5]; mn = mn[pn.resample("ME").count() >= 5]
            tb, _ = tt(mb); tn, shn = tt(mn)
            rot = float(f.sum())/max(float(ok.sum()), 1)
            FIL[(nom, et, k)] = (len(mn), 100*cr[ok].mean(), rot, mb.mean(), tb, mn.mean(), tn, shn)

ORD = ["RSI 14 momento","RSI 14 reversion","MACD 12/26/9","MACD 12/26","MM 20/100",
       "MM 50/200","Donchian 20","Donchian 55","canal ATR 20/2"]
for nom, _, _, _ in INS:
    print("\n" + "="*104); print(f"{nom}"); print("="*104)
    print(f"{'indicador':<20}" + "".join(f"{et:>20}" for et, _ in TF))
    print(f"{'':<20}" + "".join(f"{'BRUTO   t':>20}" for _ in TF))
    for k in ORD:
        fila = f"  {k:<18}"
        for et, _ in TF:
            v = FIL.get((nom, et, k))
            fila += f"{v[3]:>+13.4f}{v[4]:>+7.2f}" if v and np.isfinite(v[4]) else f"{'-':>20}"
        print(fila)
    print(f"{'':<20}" + "".join(f"{'NETO   t':>20}" for _ in TF))
    for k in ORD:
        fila = f"  {k:<18}"
        for et, _ in TF:
            v = FIL.get((nom, et, k))
            fila += f"{v[5]:>+13.4f}{v[6]:>+7.2f}" if v and np.isfinite(v[6]) else f"{'-':>20}"
        print(fila)
    print(f"  {'coste medio por cambio (% del ruido de la barra)':<50}" +
          "".join(f"{FIL[(nom,et,'MM 20/100')][1]:>10.1f}%" for et, _ in TF))

print("\n" + "="*104); print("RESUMEN: las 108 celdas"); print("="*104)
tb = [v[4] for v in FIL.values() if np.isfinite(v[4])]
tn = [v[6] for v in FIL.values() if np.isfinite(v[6])]
print(f"  celdas con dato: {len(tb)}")
print(f"  BRUTO  t mediano {np.median(tb):+.2f}   con t>+2: {sum(t>2 for t in tb)}   con t<-2: {sum(t<-2 for t in tb)}")
print(f"  NETO   t mediano {np.median(tn):+.2f}   con t>+2: {sum(t>2 for t in tn)}   con t<-2: {sum(t<-2 for t in tn)}")
print(f"  esperado por azar con 108 celdas al 5 %: 2,7 por cola")
print("\n  t NETO mediano por temporalidad:")
for et, _ in TF:
    v = [FIL[k][6] for k in FIL if k[1] == et and np.isfinite(FIL[k][6])]
    c = [FIL[k][1] for k in FIL if k[1] == et]
    print(f"    {et:<4} t mediano {np.median(v):>+6.2f}   coste medio {np.mean(c):>6.1f} % del ruido de la barra")
