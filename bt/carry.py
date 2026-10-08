"""Pre-registro docs/PREREGISTRO_carry.md

Carry en divisas con la inflacion del Banco Mundial como sustituto del
diferencial de tipos (Fisher). Senial del anio Y = inflacion del anio Y-2,
para que no quepa duda de que se sabia. Estadistico sobre los MESES.
"""
import numpy as np, pandas as pd
from math import sqrt

VENT_VOL, VOL_MIN, RET_MAX, COSTE_RUIDO, RECARGO = 36, 0.005, 0.50, 0.01, 1.5
rng = np.random.default_rng(20260922)

WB = {"Australia":"Australia","Brazil":"Brazil","Canada":"Canada","China":"China",
      "Denmark":"Denmark","Euro":"Euro area","Hong Kong":"Hong Kong SAR, China",
      "India":"India","Japan":"Japan","Malaysia":"Malaysia","Mexico":"Mexico",
      "New Zealand":"New Zealand","Norway":"Norway","Singapore":"Singapore",
      "South Africa":"South Africa","South Korea":"Korea, Rep.","Sweden":"Sweden",
      "Switzerland":"Switzerland","Thailand":"Thailand","United Kingdom":"United Kingdom"}

# ---------- tipos de cambio, normalizados a MONEDA POR DOLAR ----------
fx = pd.read_csv("data/ext/fx_daily.csv", parse_dates=["Date"])
S = {}
for pais, g in fx.groupby("Country"):
    if pais not in WB: continue
    s = g.set_index("Date")["Exchange rate"].sort_index()
    s = s[s > 0].resample("ME").last().dropna()
    # el Fed publica unas en dolares por unidad (GBP, EUR, AUD, NZD) y el resto
    # al reves. Se detecta por la mediana y se invierte para dejarlas todas
    # como MONEDA POR DOLAR: subir = la divisa se debilita.
    if s.median() < 1.2: s = 1.0/s
    if len(s) > 120: S[pais] = s
P = pd.DataFrame(S)
P = P[P.index >= "1971-01-01"]
print(f"divisas: {len(P.columns)}   meses: {len(P)}   "
      f"{P.index.min():%Y-%m} a {P.index.max():%Y-%m}")

# ---------- senial: inflacion del anio Y-2 menos la de EE.UU. ----------
inf = pd.read_csv("data/ext/inflacion.csv")
piv = inf.pivot_table(index="Year", columns="Country", values="Inflation")
us = piv["United States"]
C = pd.DataFrame(index=P.index, columns=P.columns, dtype=float)
for c in P.columns:
    col = piv.get(WB[c])
    if col is None: continue
    dif = (col - us).dropna()
    C[c] = [dif.get(a-2, np.nan) for a in P.index.year]
C = C.clip(-30, 60)                      # hiperinflaciones puntuales, declarado
print(f"senial disponible en {int(C.notna().sum().sum()):,} de {C.size:,} celdas")

R = np.log(P).diff()                     # subir = la divisa extranjera se debilita
VOL = R.rolling(VENT_VOL).std().shift(1)
OK = (VOL >= VOL_MIN) & R.abs().le(RET_MAX) & R.notna() & VOL.notna() & C.notna()
print(f"observaciones utiles: {int(OK.sum().sum()):,}\n")

def rend(recargo=0.0):
    """rendimiento mensual de estar LARGO en la divisa, financiado en dolares."""
    interes = (C - recargo).div(12) / 100.0        # en logaritmo aproximado
    return (interes - R).where(OK)                 # -R porque subir = debilitarse

def cartera(sig, recargo=0.0, con_coste=True):
    x = (rend(recargo) / VOL).where(OK)
    p = (sig * x).where(OK)
    if con_coste:
        flip = (sig != sig.shift(1)) & OK & OK.shift(1).fillna(False)
        p = p - flip.astype(float) * COSTE_RUIDO
    n = p.notna().sum(axis=1)
    return p.mean(axis=1)[n >= 6].dropna()

def tercios():
    """+1 al tercio de mayor carry, -1 al de menor, 0 al resto."""
    Cm = C.where(OK)
    r = Cm.rank(axis=1, pct=True)
    return (r > 2/3).astype(float) - (r < 1/3).astype(float)

def linea(et, m):
    if len(m) < 24: return print(f"  {et:<38} (pocos meses: {len(m)})")
    t = m.mean()/(m.std(ddof=1)/sqrt(len(m))); sh = m.mean()/m.std(ddof=1)*sqrt(12)
    ic = 1.96*m.std(ddof=1)/sqrt(len(m))
    print(f"  {et:<38} meses {len(m):>4}  efecto {m.mean():>+7.4f} "
          f"[{m.mean()-ic:>+.4f},{m.mean()+ic:>+.4f}]  t {t:>+6.2f}  Sharpe {sh:>+5.2f}"
          f"{'   *' if abs(t) > 2 else ''}")
    return m

T = tercios()
print("="*108)
print("PRINCIPAL declarado · carry transversal, tercio contra tercio, muestra completa")
print("="*108)
m = linea("sin recargo", cartera(T))
mr = linea(f"con recargo de {RECARGO} puntos/año", cartera(T, recargo=RECARGO))
linea("sin coste de operar", cartera(T, con_coste=False))

print("\n" + "="*108); print("SECUNDARIOS"); print("="*108)
linea("temporal · signo del carry", cartera(np.sign(C.where(OK))))
linea("tercios sin escalar por volatilidad",
      (T*rend()).where(OK).mean(axis=1)[(T*rend()).where(OK).notna().sum(axis=1) >= 6].dropna())

print("\n" + "="*108); print("PARTICION TEMPORAL declarada antes"); print("="*108)
for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026")):
    x = m[(m.index.year >= int(a)) & (m.index.year <= int(b))]
    linea(f"{a}-{b} · sin recargo", x)
    linea(f"{a}-{b} · con recargo", mr[(mr.index.year >= int(a)) & (mr.index.year <= int(b))])

print("\n" + "="*108); print("PLACEBOS"); print("="*108)
al = pd.DataFrame(rng.choice([-1.0, 0.0, 1.0], size=T.shape), index=T.index, columns=T.columns)
linea("1 · señales aleatorias", cartera(al))
linea("2 · señal invertida", cartera(-T))
bar = T.copy()
for i in bar.index:
    f = bar.loc[i].to_numpy(copy=True); rng.shuffle(f); bar.loc[i] = f
linea("3 · señales barajadas entre divisas", cartera(bar))

print("\n" + "="*108)
print("LA FORMA DEL RIESGO · lo que decide si le sirve")
print("="*108)
for et, x in (("sin recargo", m), ("con recargo", mr)):
    sd = x.std(ddof=1)
    cum = x.cumsum(); dd = (cum - cum.cummax())
    print(f"  {et:<14} asimetría {x.skew():>+6.2f}   peor mes {x.min():>+7.3f} "
          f"({x.min()/sd:>+5.1f} desviaciones)   peor caída {dd.min():>+7.3f} "
          f"unidades de ruido")

print("\n" + "="*108)
print("¿Y EN DINERO? · escalado para que la PEOR CAIDA HISTORICA sea del 10 %")
print("="*108)
for et, x in (("completa sin recargo", m), ("completa con recargo", mr),
              ("2013-2026 con recargo", mr[mr.index.year >= 2013])):
    if len(x) < 24: continue
    cum = x.cumsum(); dd = float((cum - cum.cummax()).min())
    if dd >= 0: continue
    k = 10.0/abs(dd)                      # escala que pone la peor caida en 10 %
    anual = x.mean()*12*k
    print(f"  {et:<24} escala {k:>5.1f}  ->  {anual:>+6.2f} %/año  "
          f"= {50000*anual/100/12:>+7.0f} €/mes sobre 50.000   (Sharpe "
          f"{x.mean()/x.std(ddof=1)*sqrt(12):+.2f})")

print("\n" + "="*108)
print("EL MES QUE LO DECIDE TODO")
print("="*108)
peor = mr.nsmallest(5)
print("  los cinco peores meses (con recargo):")
for f, v in peor.items():
    print(f"    {f:%Y-%m}   {v:>+7.3f} unidades de ruido  ({v/mr.std(ddof=1):>+5.1f} desviaciones)")
cum = mr.cumsum(); dd = cum - cum.cummax()
print(f"\n  peor caída acumulada: {dd.min():+.3f}, tocando fondo en {dd.idxmin():%Y-%m}")

rec = mr[mr.index.year >= 2013]
ddr = float((rec.cumsum() - rec.cumsum().cummax()).min())
k_rec = 10.0/abs(ddr)
print(f"\n  SI SE DIMENSIONA CON LOS ULTIMOS TRECE ANIOS (escala {k_rec:.1f}, porque en")
print(f"  ese tramo la peor caída fue de solo {abs(ddr):.2f} unidades)...")
print(f"    el peor mes de la historia completa, {peor.index[0]:%Y-%m}, habría costado "
      f"{peor.iloc[0]*k_rec:+.1f} % en UN mes")
print(f"    y la peor caída completa, {dd.min()*k_rec:+.1f} %")
print(f"\n  a la escala prudente (peor caída histórica = 10 %):")
k = 10.0/abs(float(dd.min()))
print(f"    el peor mes cuesta {peor.iloc[0]*k:+.1f} % y se ganan "
      f"{50000*mr.mean()*12*k/100/12:+.0f} €/mes")

print("\n" + "="*108)
print("POSTERIOR AL PRE-REGISTRO · solo el G10, que es lo unico que el puede operar")
print("="*108)
print("  NO estaba declarado. Se marca como exploratorio. El motivo: el peor mes de")
print("  arriba es la devaluacion administrada del yuan de enero de 1994, y ni el yuan")
print("  ni el rupia ni el baht eran operables por un minorista en aquella epoca.")
G10 = ["Australia","Canada","Switzerland","Denmark","Euro","United Kingdom",
       "Japan","Norway","New Zealand","Sweden"]
g = [c for c in P.columns if c in G10]
OKg = OK[g]; Cg = C[g]; Rg = R[g]; VOLg = VOL[g]
def cartera_g(sig, recargo=0.0):
    interes = (Cg - recargo).div(12)/100.0
    x = ((interes - Rg)/VOLg).where(OKg)
    p = (sig*x).where(OKg)
    flip = (sig != sig.shift(1)) & OKg & OKg.shift(1).fillna(False)
    p = p - flip.astype(float)*COSTE_RUIDO
    n = p.notna().sum(axis=1)
    return p.mean(axis=1)[n >= 5].dropna()
r_ = Cg.where(OKg).rank(axis=1, pct=True)
Tg = (r_ > 2/3).astype(float) - (r_ < 1/3).astype(float)
print(f"\n  divisas: {len(g)}  ({', '.join(g)})")
mg = linea("G10 · completa, con recargo", cartera_g(Tg, RECARGO))
for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026")):
    linea(f"G10 · {a}-{b}", mg[(mg.index.year >= int(a)) & (mg.index.year <= int(b))])
linea("G10 · placebo barajado", cartera_g(
      pd.DataFrame(rng.permutation(Tg.to_numpy().T).T, index=Tg.index, columns=Tg.columns), RECARGO))
sd = mg.std(ddof=1); cumg = mg.cumsum(); ddg = cumg - cumg.cummax()
print(f"\n  asimetría {mg.skew():+.2f}   peor mes {mg.min():+.3f} ({mg.min()/sd:+.1f} desv.)"
      f"   peor caída {ddg.min():+.3f} en {ddg.idxmin():%Y-%m}")
print("  los cinco peores meses:")
for f_, v in mg.nsmallest(5).items():
    print(f"    {f_:%Y-%m}   {v:>+7.3f}  ({v/sd:>+5.1f} desviaciones)")
k = 10.0/abs(float(ddg.min()))
print(f"\n  a la escala prudente (peor caída histórica = 10 %, escala {k:.1f}):")
print(f"    {mg.mean()*12*k:+.2f} %/año = {50000*mg.mean()*12*k/100/12:+.0f} €/mes sobre 50.000")
print(f"    el peor mes cuesta {mg.min()*k:+.1f} %")

mg.to_csv("data/ext/serie_carry_g10.csv")

mr.to_csv("data/ext/serie_carry_todas.csv")
