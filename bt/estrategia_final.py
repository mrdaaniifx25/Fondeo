"""Pre-registro docs/PREREGISTRO_estrategia_final.md  ·  LA ESTRATEGIA ENSAMBLADA

Tres bloques a peso igual, sin elegir nada:
  A momento    media de signos de ROC 21/63/126/252 dias
  B tendencia  media de signos de MM 20/100, Donchian 55, canal ATR 20/2
  C carry      diferencial de inflacion frente a EEUU, por tercios (solo divisas)

Reequilibrio MENSUAL: la posicion se fija el primer dia habil del mes.
El titular es el universo OPERABLE (G10 + materias + S&P) en 2013-2026.

  python3 bt/estrategia_final.py
"""
import numpy as np, pandas as pd
from math import sqrt

VENT_VOL, VOL_MIN, RET_MAX, COSTE = 36, 0.0008, 0.25, 0.02
rng = np.random.default_rng(20260923)
WB = {"Australia":"Australia","Brazil":"Brazil","Canada":"Canada","China":"China",
      "Denmark":"Denmark","Euro":"Euro area","Hong Kong":"Hong Kong SAR, China",
      "India":"India","Japan":"Japan","Malaysia":"Malaysia","Mexico":"Mexico",
      "New Zealand":"New Zealand","Norway":"Norway","Singapore":"Singapore",
      "South Africa":"South Africa","South Korea":"Korea, Rep.","Sweden":"Sweden",
      "Switzerland":"Switzerland","Thailand":"Thailand","United Kingdom":"United Kingdom"}

# ---------------- panel diario ----------------
S = {}
fx = pd.read_csv("data/ext/fx_daily.csv", parse_dates=["Date"])
fx = fx[fx.Country != "Venezuela"]
for pais, g in fx.groupby("Country"):
    s = g.set_index("Date")["Exchange rate"].sort_index()
    s = s[s > 0]; s = s[~s.index.duplicated()]
    if len(s) > 1500: S["FX " + pais] = s
def carga(ruta, col):
    d = pd.read_csv(ruta); d["Date"] = pd.to_datetime(d["Date"])
    s = pd.to_numeric(d.set_index("Date")[col].sort_index(), errors="coerce").dropna()
    s = s[s > 0]; return s[~s.index.duplicated()]
S["WTI"]     = carga("data/ext/oil-prices_wti-daily.csv", "Price")
S["Brent"]   = carga("data/ext/oil-prices_brent-daily.csv", "Price")
S["gas"]     = carga("data/ext/natural-gas_daily.csv", "Price")
S["S&P 500"] = carga("data/ext/s-and-p-500_data.csv", "SP500")

P = pd.DataFrame(S).sort_index()
P = P[P.index >= "1971-01-01"].resample("B").last().ffill(limit=5)
R = np.log(P).diff()
VOL = R.rolling(VENT_VOL).std().shift(1)
OK = (VOL >= VOL_MIN) & R.abs().le(RET_MAX) & R.notna() & VOL.notna()
Z = (R / VOL).where(OK)

OPER = [c for c in P.columns if any(x in c for x in ("Euro","Japan","United Kingdom",
        "Switzerland","Canada","Australia","New Zealand","Sweden","Norway","Denmark"))] \
       + ["WTI","Brent","gas","S&P 500"]
OPER = [c for c in OPER if c in P.columns]

# ---------------- los tres bloques ----------------
def sma(n): return P.rolling(n).mean()
def ema(n): return P.ewm(span=n, adjust=False).mean()
def persiste(x): return x.replace(0, np.nan).ffill().fillna(0)

A = sum(np.sign(np.log(P).diff(K)) for K in (21, 63, 126, 252)) / 4.0

don55 = persiste(np.sign((P >= P.rolling(55).max().shift(1)).astype(float)
                        -(P <= P.rolling(55).min().shift(1)).astype(float)))
atr20 = (P - P.shift(1)).abs().rolling(20).mean()
canal = persiste(np.sign((P > ema(20)+2*atr20).astype(float)
                        -(P < ema(20)-2*atr20).astype(float)))
B = (np.sign(sma(20) - sma(100)) + don55 + canal) / 3.0

# carry: diferencial de inflacion frente a EEUU, con dos anios de retardo
inf = pd.read_csv("data/ext/inflacion.csv")
piv = inf.pivot_table(index="Year", columns="Country", values="Inflation")
us = piv["United States"]
Cd = pd.DataFrame(np.nan, index=P.index, columns=P.columns)
for c in P.columns:
    pais = c.replace("FX ", "")
    col = piv.get(WB.get(pais, ""))
    if col is None: continue
    d = (col - us).dropna()
    v = pd.Series([d.get(a-2, np.nan) for a in P.index.year], index=P.index)
    # las divisas de la Fed vienen en dos convenciones; el carry se define
    # sobre MONEDA POR DOLAR, igual que en bt/carry.py
    if P[c].median() < 1.2: v = -v
    Cd[c] = v
Cd = Cd.clip(-30, 60).ffill()
r = Cd.where(OK).rank(axis=1, pct=True)
C = (r > 2/3).astype(float) - (r < 1/3).astype(float)
C = C.where(Cd.notna())

def mezcla(cols):
    b = [x[cols].where(OK[cols]) for x in (A, B, C)]
    n = sum(x.notna().astype(float) for x in b)
    return (sum(x.fillna(0) for x in b) / n.replace(0, np.nan)).clip(-1, 1)

def mensualiza(sig):
    """posicion fijada el primer dia habil del mes y mantenida."""
    return sig.shift(1).groupby(sig.index.to_period("M")).transform("first")

def serie(sig, cols, coste=COSTE):
    s = mensualiza(sig)
    p = (s * Z[cols]).where(OK[cols])
    f = (s != s.shift(1)) & OK[cols] & OK[cols].shift(1).fillna(False)
    p = p - f.astype(float) * coste * s.abs()
    n = p.notna().sum(axis=1)
    d = p.mean(axis=1)[n >= 5].dropna()
    return d.resample("ME").sum()[d.resample("ME").count() >= 10]

def tt(m):
    if len(m) < 24: return (np.nan,)*5
    t = m.mean()/(m.std(ddof=1)/sqrt(len(m)))
    sh = m.mean()/m.std(ddof=1)*sqrt(12)
    eq = m.cumsum(); dd = (eq - eq.cummax()).min()
    peor = min(m.rolling(12).sum().min(), 0)
    return t, sh, 100*(m > 0).mean(), dd, peor

def linea(et, m, ind="  "):
    if len(m) < 24: return print(f"{ind}{et:<30} (pocos meses: {len(m)})")
    t, sh, pc, dd, peor = tt(m)
    print(f"{ind}{et:<30}{len(m):>6}{m.mean():>+9.4f}{t:>+7.2f}{sh:>+8.2f}"
          f"{pc:>8.0f}%{dd:>9.2f}{peor:>9.2f}")

CAB = f"{'':<32}{'meses':>6}{'efecto':>9}{'t':>7}{'Sharpe':>8}{'+meses':>9}{'caida':>9}{'peor12':>9}"

print("="*90); print("PRINCIPAL declarado  ·  universo OPERABLE (14 series)"); print("="*90)
mo = serie(mezcla(OPER), OPER)
print(CAB)
linea("2013-2026  <-- EL NUMERO", mo[mo.index.year >= 2013])
linea("muestra completa", mo)
for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026"), ("2020","2026")):
    linea(f"{a}-{b}", mo[(mo.index.year >= int(a)) & (mo.index.year <= int(b))], "    ")

print("\n" + "="*90); print("Universo COMPLETO (25 series)"); print("="*90)
mc = serie(mezcla(list(P.columns)), list(P.columns))
print(CAB)
linea("muestra completa", mc)
for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026"), ("2020","2026")):
    linea(f"{a}-{b}", mc[(mc.index.year >= int(a)) & (mc.index.year <= int(b))], "    ")

print("\n" + "="*90); print("CADA BLOQUE POR SEPARADO  ·  universo operable"); print("="*90)
print(CAB)
BL = {}
for et, X in (("A momento", A), ("B tendencia", B), ("C carry", C)):
    s = X[OPER].where(OK[OPER]).clip(-1, 1)
    BL[et] = serie(s, OPER)
    linea(et + " · completa", BL[et])
    linea(et + " · 2013-2026", BL[et][BL[et].index.year >= 2013], "    ")

M3 = pd.DataFrame(BL).dropna()
print("\n  correlacion entre bloques (rendimientos mensuales):")
print("   ", M3.corr().round(2).to_string().replace("\n", "\n    "))

print("\n" + "="*90); print("CONTROLES  ·  universo operable"); print("="*90)
print(CAB)
linea("comprar y mantener", serie(pd.DataFrame(1.0, index=P.index, columns=P.columns)[OPER], OPER))
sm = mensualiza(mezcla(OPER))
rot = float(((sm != sm.shift(1)) & OK[OPER]).sum().sum()) / max(OK[OPER].sum().sum(), 1)
al = pd.DataFrame(rng.choice([-1.0, 1.0], size=(len(P.index.to_period("M").unique()), len(OPER))),
                  index=pd.PeriodIndex(P.index.to_period("M").unique(), freq="M"), columns=OPER)
alz = al.reindex(P.index.to_period("M")).set_axis(P.index)
linea("placebo (azar, misma rotacion)", serie(alz.where(OK[OPER]), OPER))
print(f"\n  rotacion real del sistema: {252*rot:.1f} cambios por instrumento y anio")

print("\n" + "="*90); print("EN DINERO  ·  limite de caida del 10 %"); print("="*90)
for et, m in (("muestra completa", mo), ("2013-2026", mo[mo.index.year >= 2013]),
              ("2020-2026", mo[mo.index.year >= 2020])):
    if len(m) < 24: continue
    sh = m.mean()/m.std(ddof=1)*sqrt(12)
    # se escala la cartera para que la caida maxima HISTORICA sea el 10 %
    eq = m.cumsum(); dd = abs((eq - eq.cummax()).min())
    k = 0.10/dd if dd > 0 else 0
    anual = 12*m.mean()*k
    print(f"  {et:<20} Sharpe {sh:>+5.2f}   vol {100*k*m.std(ddof=1)*sqrt(12):>5.2f} %/ano"
          f"   rend {100*anual:>+6.2f} %/ano   " +
          "   ".join(f"{cap//1000}k: {anual*cap/12:>+6.0f} EUR/mes" for cap in (10000, 50000, 100000)))
