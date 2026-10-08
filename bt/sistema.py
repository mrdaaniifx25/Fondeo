"""EL SISTEMA. Momento (los cuatro horizontes juntos) + carry.

No es una prueba nueva: son las mismas seniales ya medidas y publicadas,
combinadas a peso igual. Juntar K=1,3,6,12 es lo contrario de elegir el
mejor: es no elegir.
"""
import numpy as np, pandas as pd
from math import sqrt

VENT_VOL, VOL_MIN, RET_MAX, COSTE_RUIDO, RECARGO = 36, 0.005, 0.50, 0.01, 1.5
KS = [1, 3, 6, 12]
WB = {"Australia":"Australia","Brazil":"Brazil","Canada":"Canada","China":"China",
      "Denmark":"Denmark","Euro":"Euro area","Hong Kong":"Hong Kong SAR, China",
      "India":"India","Japan":"Japan","Malaysia":"Malaysia","Mexico":"Mexico",
      "New Zealand":"New Zealand","Norway":"Norway","Singapore":"Singapore",
      "South Africa":"South Africa","South Korea":"Korea, Rep.","Sweden":"Sweden",
      "Switzerland":"Switzerland","Thailand":"Thailand","United Kingdom":"United Kingdom"}

fx = pd.read_csv("data/ext/fx_daily.csv", parse_dates=["Date"])
S, INV = {}, {}
for pais, g in fx.groupby("Country"):
    if pais not in WB: continue
    s = g.set_index("Date")["Exchange rate"].sort_index()
    s = s[s > 0].resample("ME").last().dropna()
    inv = s.median() < 1.2
    if inv: s = 1.0/s                      # todas a MONEDA POR DOLAR
    if len(s) > 120: S[pais] = s; INV[pais] = inv
P = pd.DataFrame(S); P = P[P.index >= "1971-01-01"]

inf = pd.read_csv("data/ext/inflacion.csv")
piv = inf.pivot_table(index="Year", columns="Country", values="Inflation")
us = piv["United States"]
C = pd.DataFrame(index=P.index, columns=P.columns, dtype=float)
for c in P.columns:
    col = piv.get(WB[c])
    if col is not None:
        d = (col - us).dropna(); C[c] = [d.get(a-2, np.nan) for a in P.index.year]
C = C.clip(-30, 60)
# la inflacion del Banco Mundial acaba en 2023: para los meses posteriores se
# arrastra el ultimo dato conocido, que es lo que se podria hacer en vivo
C = C.ffill()

R = np.log(P).diff()
VOL = R.rolling(VENT_VOL).std().shift(1)
OKm = (VOL >= VOL_MIN) & R.abs().le(RET_MAX) & R.notna() & VOL.notna()
OKc = OKm & C.notna()

def sig_mom():
    """media de los signos de los cuatro horizontes: -1 .. +1"""
    s = sum(np.sign(np.log(P).diff(K)) for K in KS)/len(KS)
    return s.shift(1).reindex_like(R)

def sig_carry():
    r = C.where(OKc).rank(axis=1, pct=True)
    return (r > 2/3).astype(float) - (r < 1/3).astype(float)

def serie(sig, ok, rend, coste=True):
    x = (rend/VOL).where(ok)
    p = (sig*x).where(ok)
    if coste:
        flip = (np.sign(sig) != np.sign(sig).shift(1)) & ok & ok.shift(1).fillna(False)
        p = p - flip.astype(float)*COSTE_RUIDO
    n = p.notna().sum(axis=1)
    return p.mean(axis=1)[n >= 6].dropna()

rend_mom = -R                                    # largo = apostar a que sube el dolar? no:
rend_mom = R.copy()                              # el signo lo pone la senial sobre la serie
rend_car = ((C - RECARGO).div(12)/100.0 - R)

M = serie(sig_mom(), OKm, rend_mom)
K = serie(sig_carry(), OKc, rend_car)

def ficha(et, x):
    t = x.mean()/(x.std(ddof=1)/sqrt(len(x))); sh = x.mean()/x.std(ddof=1)*sqrt(12)
    dd = float((x.cumsum() - x.cumsum().cummax()).min())
    k = 10.0/abs(dd)
    print(f"  {et:<30} meses {len(x):>4}  t {t:>+6.2f}  Sharpe {sh:>+5.2f}  "
          f"asim {x.skew():>+5.2f}  peor caída {dd:>+6.2f}  ->{50000*x.mean()*12*k/100/12:>+6.0f} €/mes")
    return x

print("="*112); print("EL SISTEMA"); print("="*112)
j = pd.concat([M.rename("m"), K.rename("k")], axis=1).dropna()
print(f"  correlación momento/carry: {j.m.corr(j.k):+.3f}\n")
ficha("momento (1 solo horizonte, K=12)", serie(np.sign(np.log(P).diff(12)).shift(1).reindex_like(R), OKm, rend_mom))
ficha("momento (los CUATRO juntos)", j.m)
ficha("carry", j.k)
MIX = ficha("MEZCLA 50/50", 0.5*j.m + 0.5*j.k)
print()
for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026")):
    ficha(f"  mezcla {a}-{b}", MIX[(MIX.index.year >= int(a)) & (MIX.index.year <= int(b))])

# ---------------- LA SEÑAL DE HOY ----------------
print("\n" + "="*112); print("LA SEÑAL DE HOY"); print("="*112)
sm, sk = sig_mom(), sig_carry()
ult = P.index[-1]
print(f"  último dato: {ult:%Y-%m-%d}\n")
print(f"  {'divisa':<18} {'par como se opera':<20} {'momento':>9} {'carry':>7} {'SEÑAL':>8}  {'dirección del par':<22}")
print("  " + "-"*100)
filas = []
for c in sorted(P.columns):
    if not OKm.loc[ult, c]: continue
    m_ = sm.loc[ult, c] if pd.notna(sm.loc[ult, c]) else 0.0
    k_ = sk.loc[ult, c] if c in sk.columns and pd.notna(sk.loc[ult, c]) else 0.0
    tot = 0.5*m_ + 0.5*k_
    if abs(tot) < 0.25: continue
    # la serie es MONEDA POR DOLAR: senial +1 = apostar a que la moneda SUBE
    # contra el dolar. El par como lo cotiza el broker puede estar invertido.
    par = {"Euro":"EURUSD","United Kingdom":"GBPUSD","Australia":"AUDUSD",
           "New Zealand":"NZDUSD","Canada":"USDCAD","Japan":"USDJPY",
           "Switzerland":"USDCHF","Norway":"USDNOK","Sweden":"USDSEK",
           "Denmark":"USDDKK","Mexico":"USDMXN","South Africa":"USDZAR",
           "Singapore":"USDSGD","India":"USDINR","Brazil":"USDBRL",
           "South Korea":"USDKRW","China":"USDCNH","Thailand":"USDTHB",
           "Hong Kong":"USDHKD","Malaysia":"USDMYR"}.get(c, "?")
    base_es_moneda = par.startswith(("EUR","GBP","AUD","NZD"))
    # tot>0 = la moneda extranjera se fortalece
    if base_es_moneda: dirn = "COMPRAR" if tot > 0 else "VENDER"
    else:              dirn = "VENDER" if tot > 0 else "COMPRAR"
    filas.append((c, par, m_, k_, tot, dirn))
filas.sort(key=lambda r: -abs(r[4]))
for c, par, m_, k_, tot, dirn in filas:
    print(f"  {c:<18} {par:<20} {m_:>+9.2f} {k_:>+7.0f} {tot:>+8.2f}  {dirn} {par}")
print(f"\n  {len(filas)} posiciones. A 0,25 % de riesgo cada una = {0.25*len(filas):.2f} % de riesgo total.")
pd.DataFrame(filas, columns=["divisa","par","momento","carry","senal","direccion"]).to_csv(
    "data/senal_actual.csv", index=False)
