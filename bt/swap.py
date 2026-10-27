"""CASILLA 4 · el swap: cuanto aguanta el carry el recargo REAL de un broker.

Y una CORRECCION de bt/carry.py. Alli el recargo se restaba al diferencial:

    rend = ((C - recargo)/1200 - R)      y luego   p = sig * rend

Para las posiciones LARGAS (sig=+1) eso resta el recargo, correcto. Pero para
las CORTAS (sig=-1) lo SUMA: el recargo sale como un ingreso. Media cartera
recibia un abono donde deberia pagar una comision.

Lo correcto es que el recargo cueste SIEMPRE:

    p = (sig*(interes - R) - |sig|*recargo) / VOL

  python3 bt/swap.py
"""
import numpy as np, pandas as pd
from math import sqrt

VENT_VOL, VOL_MIN, RET_MAX, COSTE_RUIDO = 36, 0.005, 0.50, 0.01
rng = np.random.default_rng(20261013)
WB = {"Australia":"Australia","Brazil":"Brazil","Canada":"Canada","China":"China",
      "Denmark":"Denmark","Euro":"Euro area","Hong Kong":"Hong Kong SAR, China",
      "India":"India","Japan":"Japan","Malaysia":"Malaysia","Mexico":"Mexico",
      "New Zealand":"New Zealand","Norway":"Norway","Singapore":"Singapore",
      "South Africa":"South Africa","South Korea":"Korea, Rep.","Sweden":"Sweden",
      "Switzerland":"Switzerland","Thailand":"Thailand","United Kingdom":"United Kingdom"}
G10 = ["Australia","Canada","Denmark","Euro","Japan","New Zealand","Norway",
       "Sweden","Switzerland","United Kingdom"]

fx = pd.read_csv("data/ext/fx_daily.csv", parse_dates=["Date"])
S = {}
for pais, g in fx.groupby("Country"):
    if pais not in WB: continue
    s = g.set_index("Date")["Exchange rate"].sort_index()
    s = s[s > 0].resample("ME").last().dropna()
    if s.median() < 1.2: s = 1.0/s          # todas a MONEDA POR DOLAR
    if len(s) > 120: S[pais] = s
P = pd.DataFrame(S); P = P[P.index >= "1971-01-01"]
inf = pd.read_csv("data/ext/inflacion.csv")
piv = inf.pivot_table(index="Year", columns="Country", values="Inflation")
us = piv["United States"]

def difer(retraso):
    C = pd.DataFrame(index=P.index, columns=P.columns, dtype=float)
    for c in P.columns:
        col = piv.get(WB[c])
        if col is None: continue
        d = (col - us).dropna()
        C[c] = [d.get(a-retraso, np.nan) for a in P.index.year]
    return C.clip(-30, 60)

R = np.log(P).diff()
VOL = R.rolling(VENT_VOL).std().shift(1)

def monta(C):
    OK = (VOL >= VOL_MIN) & R.abs().le(RET_MAX) & R.notna() & VOL.notna() & C.notna()
    r = C.where(OK).rank(axis=1, pct=True)
    sig = ((r > 2/3).astype(float) - (r < 1/3).astype(float)).where(OK)
    return OK, sig

def serie(C, OK, sig, recargo=0.0, modo="correcto", cols=None, coste=True):
    """modo: 'correcto' (cuesta en los dos lados) · 'antiguo' (el bug) ·
    'sin_swap' (el broker se queda TODO el interes: solo queda el movimiento)"""
    if cols is not None:
        C, OK2, sig2, R2, V2 = C[cols], OK[cols], sig[cols], R[cols], VOL[cols]
    else:
        OK2, sig2, R2, V2 = OK, sig, R, VOL
    intr = C.div(1200.0)
    m = recargo/1200.0
    if modo == "correcto":   bruto = sig2*(intr - R2) - sig2.abs()*m
    elif modo == "antiguo":  bruto = sig2*((C - recargo).div(1200.0) - R2)
    elif modo == "sin_swap": bruto = sig2*(-R2)
    elif modo == "solo_int": bruto = sig2*intr - sig2.abs()*m
    p = (bruto/V2).where(OK2)
    if coste:
        flip = (sig2 != sig2.shift(1)) & OK2 & OK2.shift(1).fillna(False)
        p = p - flip.astype(float)*COSTE_RUIDO
    n = p.notna().sum(axis=1)
    return p.mean(axis=1)[n >= 6].dropna()

def tt(x):
    if len(x) < 24: return (np.nan,)*3
    return (x.mean(), x.mean()/(x.std(ddof=1)/sqrt(len(x))),
            x.mean()/x.std(ddof=1)*sqrt(12))

def linea(et, x, ind="  "):
    e, t, sh = tt(x)
    if not np.isfinite(t): return print(f"{ind}{et:<40} (pocos meses)")
    print(f"{ind}{et:<40}{len(x):>6}{e:>+10.4f}{t:>+8.2f}{sh:>+8.2f}")

C2 = difer(2); OK, sig = monta(C2)
CAB = f"  {'':<40}{'meses':>6}{'efecto':>10}{'t':>8}{'Sharpe':>8}"

print("="*78); print("1 · EL ERROR DEL RECARGO, y cuanto costaba"); print("="*78)
print(CAB)
for m in (0.0, 1.5, 3.0):
    linea(f"recargo {m:.1f} pp/año · modelo ANTIGUO (bug)", serie(C2,OK,sig,m,"antiguo"))
    linea(f"recargo {m:.1f} pp/año · modelo CORRECTO",      serie(C2,OK,sig,m,"correcto"))
    print()

print("="*78); print("2 · CUANTO RECARGO AGUANTA  ·  20 divisas y solo G10"); print("="*78)
print(f"  {'recargo':>9}{'20 divisas t':>15}{'Sharpe':>9}   {'G10 t':>8}{'Sharpe':>9}")
for m in (0, 1, 2, 3, 4, 5, 6, 8, 10):
    a = serie(C2, OK, sig, m, "correcto")
    b = serie(C2, OK, sig, m, "correcto", cols=G10)
    _, ta, sa = tt(a); _, tb, sb = tt(b)
    print(f"  {m:>7} pp{ta:>15.2f}{sa:>9.2f}   {tb:>8.2f}{sb:>9.2f}")

print("\n" + "="*78); print("3 · DE DONDE SALE EL RENDIMIENTO"); print("="*78)
print(CAB)
linea("completo (interes + movimiento)", serie(C2,OK,sig,0,"correcto"))
linea("SOLO el interes (el swap)",       serie(C2,OK,sig,0,"solo_int"))
linea("SOLO el movimiento (sin swap)",   serie(C2,OK,sig,0,"sin_swap"))
print("\n  'sin_swap' = el broker se queda TODO el interes. Es el caso de una")
print("  cuenta sin swap o de una prop que cobra financiacion. Si eso da cero,")
print("  la estrategia ES el swap y el recargo lo decide todo.")

print("\n" + "="*78); print("4 · LO QUE CUESTA QUE LA SEÑAL ESTE VIEJA"); print("="*78)
print(CAB)
for L, et in ((2, "inflacion de Y-2 (lo que uso)"), (1, "inflacion de Y-1"),
              (0, "inflacion de Y (mira al futuro, cota superior)")):
    Cx = difer(L); OKx, sx = monta(Cx)
    linea(et, serie(Cx, OKx, sx, 2.0, "correcto"))
print("\n  Con tipos de interes REALES el retraso es cero: la cota de arriba es")
print("  lo que podria ganarse usando la tabla de swap del broker en vivo.")

print("\n" + "="*78); print("5 · TRAMO RECIENTE, con recargo correcto de 2 pp"); print("="*78)
print(CAB)
x = serie(C2, OK, sig, 2.0, "correcto")
for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026")):
    linea(f"{a}-{b}", x[(x.index.year >= int(a)) & (x.index.year <= int(b))])
g = serie(C2, OK, sig, 2.0, "correcto", cols=G10)
linea("G10 2013-2026", g[g.index.year >= 2013])

print("\n" + "="*78); print("6 · EN DINERO, con limite de caida del 10 %"); print("="*78)
for et, s in (("completa, recargo 2 pp", x), ("2013-2026, recargo 2 pp",
               x[x.index.year >= 2013]), ("G10 2013-2026, recargo 2 pp",
               g[g.index.year >= 2013])):
    if len(s) < 24: continue
    eq = s.cumsum(); dd = abs((eq-eq.cummax()).min())
    k = 0.10/dd if dd > 0 else 0
    an = 12*s.mean()*k
    print(f"  {et:<30} vol {100*k*s.std(ddof=1)*sqrt(12):>5.1f} %/año  "
          f"rend {100*an:>+6.2f} %/año   " +
          "  ".join(f"{c//1000}k: {an*c/12:>+5.0f} €/mes" for c in (10000, 50000)))
