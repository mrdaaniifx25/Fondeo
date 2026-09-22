"""Pre-registro docs/PREREGISTRO_momento_largo.md

Momento de series temporales, mensual, sobre 27 series y hasta 55 anios.
Lo que decide si esto vale algo: cada mes se promedia en UN numero de
cartera y el estadistico va sobre los MESES, no sobre las filas, porque
las 22 divisas son todas contra el dolar y estan correlacionadas.
"""
import numpy as np, pandas as pd
from math import sqrt

KS = [1, 3, 6, 12]
VENT_VOL, VOL_MIN, RET_MAX, COSTE_RUIDO = 36, 0.005, 0.50, 0.01
rng = np.random.default_rng(20260922)

# ---------------- las 27 series, a cierre mensual ----------------
S = {}
fx = pd.read_csv("data/ext/fx_daily.csv", parse_dates=["Date"])
fx = fx[fx.Country != "Venezuela"]
for pais, g in fx.groupby("Country"):
    s = g.set_index("Date")["Exchange rate"].sort_index()
    s = s[s > 0].resample("ME").last().dropna()
    if len(s) > 120: S["FX " + pais] = s

def carga(ruta, col, fecha="Date", mens=False):
    d = pd.read_csv(ruta)
    d[fecha] = pd.to_datetime(d[fecha], format="%Y-%m" if mens else None)
    s = d.set_index(fecha)[col].sort_index()
    s = pd.to_numeric(s, errors="coerce").dropna()
    return s[s > 0].resample("ME").last().dropna()

S["oro"]     = carga("data/ext/gold-prices_monthly.csv", "Price", mens=True)
S["WTI"]     = carga("data/ext/oil-prices_wti-daily.csv", "Price")
S["Brent"]   = carga("data/ext/oil-prices_brent-daily.csv", "Price")
S["gas"]     = carga("data/ext/natural-gas_daily.csv", "Price")
S["S&P 500"] = carga("data/ext/s-and-p-500_data.csv", "SP500")
print(f"series: {len(S)}   meses totales: {sum(len(v) for v in S.values()):,}")
print(f"rango: {min(v.index.min() for v in S.values()):%Y-%m} a "
      f"{max(v.index.max() for v in S.values()):%Y-%m}\n")

# ---------------- rendimientos, volatilidad ex-ante, exclusiones -------------
R = pd.DataFrame({k: np.log(v).diff() for k, v in S.items()})
R = R[R.index >= "1971-01-01"]
VOL = R.rolling(VENT_VOL).std().shift(1)          # SOLO pasado
OK = (VOL >= VOL_MIN) & R.abs().le(RET_MAX) & R.notna() & VOL.notna()
print(f"observaciones utiles: {int(OK.sum().sum()):,} de {int(R.notna().sum().sum()):,}")

def cartera(sig, quita_dolar=False, con_coste=True):
    """sig: DataFrame de signos, ya desplazado (conocido al inicio del mes)."""
    z = (R / VOL).where(OK)                        # rendimiento en unidades de ruido
    if quita_dolar:
        esfx = [c for c in z.columns if c.startswith("FX ")]
        z[esfx] = z[esfx].sub(z[esfx].mean(axis=1), axis=0)
    p = (sig * z).where(OK)
    if con_coste:
        flip = (sig != sig.shift(1)) & OK & OK.shift(1).fillna(False)
        p = p - flip.astype(float) * COSTE_RUIDO
    n = p.notna().sum(axis=1)
    m = p.mean(axis=1)[n >= 5]                     # al menos 5 series vivas
    return m.dropna()

def linea(et, m, ind=""):
    if len(m) < 24: return print(f"  {ind}{et:<34} (pocos meses: {len(m)})")
    t = m.mean()/(m.std(ddof=1)/sqrt(len(m)))
    sh = m.mean()/m.std(ddof=1)*sqrt(12)
    ic = 1.96*m.std(ddof=1)/sqrt(len(m))
    print(f"  {ind}{et:<34} meses {len(m):>4}  efecto {m.mean():>+7.4f} "
          f"[{m.mean()-ic:>+.4f},{m.mean()+ic:>+.4f}]  t {t:>+6.2f}  Sharpe {sh:>+5.2f}"
          f"{'   *' if abs(t) > 2 else ''}")
    return t

def senal(K):
    return np.sign(np.log(pd.DataFrame(S)).diff(K)).shift(1).reindex_like(R)

print("\n" + "="*104)
print("PRINCIPAL declarado en el pre-registro · K = 12, las 27 series, muestra completa")
print("="*104)
m12 = cartera(senal(12))
linea("K=12 · con coste", m12)
linea("K=12 · sin coste", cartera(senal(12), con_coste=False))
linea("K=12 · sin factor dolar", cartera(senal(12), quita_dolar=True))

print("\n" + "="*104); print("SECUNDARIOS · los otros K"); print("="*104)
MS = {}
for K in KS:
    MS[K] = cartera(senal(K)); linea(f"K={K}", MS[K])

print("\n" + "="*104)
print("PARTICION TEMPORAL declarada antes · K = 12")
print("="*104)
for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026")):
    linea(f"{a}-{b}", m12[(m12.index.year >= int(a)) & (m12.index.year <= int(b))])

print("\n" + "="*104); print("PLACEBOS · K = 12"); print("="*104)
s12 = senal(12)
al = pd.DataFrame(rng.choice([-1.0, 1.0], size=s12.shape), index=s12.index, columns=s12.columns)
linea("1 · signos aleatorios", cartera(al))
linea("2 · senal invertida", cartera(-s12))
bar = s12.copy()
for i in bar.index:
    f = bar.loc[i].to_numpy(copy=True); rng.shuffle(f); bar.loc[i] = f
linea("3 · signos barajados entre series", cartera(bar))

print("\n" + "="*104)
print("POR SERIE · K = 12, cuantas van en el mismo sentido")
print("="*104)
z = (R/VOL).where(OK); p12 = (s12*z).where(OK)
pos = 0
for c in sorted(p12.columns):
    x = p12[c].dropna()
    if len(x) < 60: continue
    t = x.mean()/(x.std(ddof=1)/sqrt(len(x))); pos += t > 0
    print(f"  {c:<22} meses {len(x):>4}  efecto {x.mean():>+7.4f}  t {t:>+6.2f}")
print(f"\n  positivas: {pos} de {sum(1 for c in p12.columns if p12[c].dropna().size >= 60)}")

print("\n" + "="*104)
print("¿Y EN DINERO? · riesgo 0,25 % por posicion, 10 posiciones a la vez")
print("="*104)
for et, m in (("K=12 completa", m12), ("K=12 2013-2026", m12[m12.index.year >= 2013])):
    if len(m) < 24: continue
    anual = m.mean()*12; vol = m.std(ddof=1)*sqrt(12)
    # la cartera de 10 posiciones a 0,25 % cada una: escala 10 x 0,25 % de riesgo mensual
    pct = anual*0.25*10
    print(f"  {et:<18} {anual:>+7.3f} unidades de ruido/anio  ->  {pct:>+6.2f} %/anio  "
          f"= {50000*pct/100/12:>+7.0f} €/mes sobre 50.000   (Sharpe {anual/vol:+.2f})")

print("\n" + "="*104)
print("¿EL DETERIORO ES REAL O ES QUE EL TRAMO RECIENTE NO TIENE POTENCIA?")
print("="*104)
a = m12[m12.index.year <= 1999]; b = m12[m12.index.year >= 2013]
ea = a.std(ddof=1)/sqrt(len(a)); eb = b.std(ddof=1)/sqrt(len(b))
dif = a.mean()-b.mean(); ee = sqrt(ea**2+eb**2)
print(f"  1971-1999 {a.mean():+.4f}   2013-2026 {b.mean():+.4f}   "
      f"diferencia {dif:+.4f}  t {dif/ee:+.2f}")
need = (2*b.std(ddof=1)/b.mean())**2
print(f"  para que el tramo reciente llegase a t=2 con su efecto actual "
      f"harian falta {need:,.0f} meses ({need/12:,.0f} anios)")
print(f"  hay {len(b)}")

print("\n  por decada:")
for d in range(1970, 2030, 10):
    x = m12[(m12.index.year >= d) & (m12.index.year < d+10)]
    if len(x) < 24: continue
    t = x.mean()/(x.std(ddof=1)/sqrt(len(x)))
    print(f"    {d}s  meses {len(x):>4}  efecto {x.mean():>+7.4f}  t {t:>+6.2f}  "
          f"Sharpe {x.mean()/x.std(ddof=1)*sqrt(12):>+5.2f}")

print("\n  solo las 21 divisas (sin materias primas ni bolsa), 2013-2026:")
sfx = senal(12)[[c for c in R.columns if c.startswith("FX ")]]
Rg, VOLg, OKg = R, VOL, OK
zfx = (R/VOL).where(OK)[sfx.columns]
p = (sfx*zfx)
flip = (sfx != sfx.shift(1))
p = p - flip.astype(float)*COSTE_RUIDO
mfx = p.mean(axis=1).dropna()
linea("FX solo · completa", mfx)
linea("FX solo · 2013-2026", mfx[mfx.index.year >= 2013])
