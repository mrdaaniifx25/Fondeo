"""Pre-registro docs/PREREGISTRO_indicadores.md

Las familias clasicas de indicadores -medias, MACD, RSI, Donchian, canal ATR-
en DIARIO sobre el panel de 26 series y 55 anios, que es donde el muro de
coste baja de 0,1076 a 0,0226 (RESULTADOS_muro_horizonte.md).

El estadistico va sobre los MESES, no sobre los dias.

  python3 bt/indicadores.py
"""
import numpy as np, pandas as pd
from math import sqrt

VENT_VOL, VOL_MIN, RET_MAX = 36, 0.0008, 0.25
COSTE = 0.02                       # muro diario de EURUSD, en unidades de ruido
rng = np.random.default_rng(20260923)

# ---------------- el panel, a cierre DIARIO ----------------
S = {}
fx = pd.read_csv("data/ext/fx_daily.csv", parse_dates=["Date"])
fx = fx[fx.Country != "Venezuela"]
for pais, g in fx.groupby("Country"):
    s = g.set_index("Date")["Exchange rate"].sort_index()
    s = s[s > 0]
    s = s[~s.index.duplicated()]
    if len(s) > 1500: S["FX " + pais] = s

def carga(ruta, col, fecha="Date"):
    d = pd.read_csv(ruta); d[fecha] = pd.to_datetime(d[fecha])
    s = d.set_index(fecha)[col].sort_index()
    s = pd.to_numeric(s, errors="coerce").dropna()
    s = s[s > 0]
    return s[~s.index.duplicated()]

S["WTI"]     = carga("data/ext/oil-prices_wti-daily.csv", "Price")
S["Brent"]   = carga("data/ext/oil-prices_brent-daily.csv", "Price")
S["gas"]     = carga("data/ext/natural-gas_daily.csv", "Price")
S["S&P 500"] = carga("data/ext/s-and-p-500_data.csv", "SP500")

P = pd.DataFrame(S).sort_index()
P = P[P.index >= "1971-01-01"]
P = P.resample("B").last().ffill(limit=5)
R = np.log(P).diff()
VOL = R.rolling(VENT_VOL).std().shift(1)
OK = (VOL >= VOL_MIN) & R.abs().le(RET_MAX) & R.notna() & VOL.notna()
print(f"series {P.shape[1]}   dias {P.shape[0]:,}   rango {P.index.min():%Y-%m} a "
      f"{P.index.max():%Y-%m}   observaciones utiles {int(OK.sum().sum()):,}\n")

Z = (R / VOL).where(OK)

# ---------------- los indicadores ----------------
def sma(n): return P.rolling(n).mean()
def ema(n): return P.ewm(span=n, adjust=False).mean()

def rsi(n=14):
    d = P.diff()
    up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100/(1 + up/dn.replace(0, np.nan))

def atr(n=20):
    pc = P.shift(1)
    return (P - pc).abs().rolling(n).mean()     # sin high/low: |cierre a cierre|

def persiste(x):
    """+1/-1 que se mantiene hasta que aparece el signo contrario."""
    return x.replace(0, np.nan).ffill().fillna(0)

def rsi_reversion():
    r = rsi(14)
    s = pd.DataFrame(np.nan, index=r.index, columns=r.columns)
    s = s.mask(r < 30, 1.0).mask(r > 70, -1.0)
    s = s.mask((r > 50) & (s.ffill() > 0) & s.isna(), 0.0)   # cierra el largo
    s = s.mask((r < 50) & (s.ffill() < 0) & s.isna(), 0.0)   # cierra el corto
    return s.ffill().fillna(0)

def canal_atr():
    m, a = ema(20), atr(20)
    return persiste(np.sign((P > m + 2*a).astype(float) - (P < m - 2*a).astype(float)))

SEN = {
 "MM 50/200":        np.sign(sma(50) - sma(200)),
 "MM 20/100":        np.sign(sma(20) - sma(100)),
 "MM 10/50":         np.sign(sma(10) - sma(50)),
 "MACD 12/26/9":     np.sign((ema(12)-ema(26)) - (ema(12)-ema(26)).ewm(span=9, adjust=False).mean()),
 "MACD 12/26":       np.sign(ema(12) - ema(26)),
 "RSI 14 reversion": rsi_reversion(),
 "RSI 14 momento":   np.sign(rsi(14) - 50),
 "Donchian 20":      persiste(np.sign((P >= P.rolling(20).max().shift(1)).astype(float)
                                     -(P <= P.rolling(20).min().shift(1)).astype(float))),
 "Donchian 55":      persiste(np.sign((P >= P.rolling(55).max().shift(1)).astype(float)
                                     -(P <= P.rolling(55).min().shift(1)).astype(float))),
 "canal ATR 20/2":   canal_atr(),
 "ROC 250":          np.sign(np.log(P).diff(250)),
 "ROC 20":           np.sign(np.log(P).diff(20)),
}
SEN = {k: v.shift(1).reindex_like(R) for k, v in SEN.items()}   # SOLO pasado

# ---------------- cartera y estadistico ----------------
def mensual(sig, coste=COSTE):
    p = (sig * Z).where(OK)
    if coste:
        flip = (sig != sig.shift(1)) & OK & OK.shift(1).fillna(False)
        p = p - flip.astype(float) * coste * sig.abs()
    n = p.notna().sum(axis=1)
    d = p.mean(axis=1)[n >= 5].dropna()
    return d.resample("ME").sum()[d.resample("ME").count() >= 10]

def rot(sig):
    f = (sig != sig.shift(1)) & OK & OK.shift(1).fillna(False)
    return 252.0 * f.sum().sum() / max(OK.sum().sum(), 1)

def t_sh(m):
    if len(m) < 24: return np.nan, np.nan
    return m.mean()/(m.std(ddof=1)/sqrt(len(m))), m.mean()/m.std(ddof=1)*sqrt(12)

ref = SEN["ROC 250"]
def corr_ref(sig):
    a, b = sig.where(OK), ref.where(OK)
    v = pd.concat([a.stack(), b.stack()], axis=1).dropna()
    return v.corr().iloc[0, 1] if len(v) > 100 else np.nan

print(f"{'familia':<20}{'rot/ano':>8}{'corrROC':>9}{'meses':>7}"
      f"{'BRUTO':>9}{'t':>7}{'NETO':>9}{'t':>7}{'Sharpe':>8}")
res = {}
for k, s in SEN.items():
    mb, mn = mensual(s, 0), mensual(s)
    tb, _ = t_sh(mb); tn, shn = t_sh(mn)
    res[k] = (mb, mn)
    mark = "  <--" if k == "ROC 250" else ""
    print(f"  {k:<18}{rot(s):>8.1f}{corr_ref(s):>9.2f}{len(mn):>7}"
          f"{mb.mean():>+9.4f}{tb:>+7.2f}{mn.mean():>+9.4f}{tn:>+7.2f}{shn:>+8.2f}{mark}")

print("\nCONTROLES")
largo = pd.DataFrame(1.0, index=R.index, columns=R.columns)
mb, mn = mensual(largo, 0), mensual(largo)
tb, _ = t_sh(mb); tn, shn = t_sh(mn)
print(f"  {'comprar y mantener':<18}{rot(largo):>8.1f}{corr_ref(largo):>9.2f}{len(mn):>7}"
      f"{mb.mean():>+9.4f}{tb:>+7.2f}{mn.mean():>+9.4f}{tn:>+7.2f}{shn:>+8.2f}")
for et, base in (("placebo lento", "MM 50/200"), ("placebo rapido", "MACD 12/26/9")):
    b = SEN[base]
    al = pd.DataFrame(rng.choice([-1.0, 1.0], size=b.shape), index=b.index, columns=b.columns)
    bl = (rng.random(b.shape) < (rot(b)/252.0)).cumsum(axis=0)     # cambia al mismo ritmo
    al = pd.DataFrame(np.where(bl % 2 == 0, al, -al), index=b.index, columns=b.columns)
    al = al.where(OK)
    mb, mn = mensual(al, 0), mensual(al)
    tb, _ = t_sh(mb); tn, shn = t_sh(mn)
    print(f"  {et:<18}{rot(al):>8.1f}{corr_ref(al):>9.2f}{len(mn):>7}"
          f"{mb.mean():>+9.4f}{tb:>+7.2f}{mn.mean():>+9.4f}{tn:>+7.2f}{shn:>+8.2f}")

print("\nSENSIBILIDAD AL COSTE (efecto neto mensual)")
print(f"{'familia':<20}{'c=0,00':>9}{'c=0,01':>9}{'c=0,02':>9}{'c=0,04':>9}")
for k in SEN:
    v = [mensual(SEN[k], c).mean() for c in (0.0, 0.01, 0.02, 0.04)]
    print(f"  {k:<18}" + "".join(f"{x:>+9.4f}" for x in v))

print("\nPARTICION TEMPORAL (neto)")
print(f"{'familia':<20}{'1971-1999':>20}{'2000-2012':>20}{'2013-2026':>20}")
for k in SEN:
    m = res[k][1]; out = ""
    for a, b in (("1971","1999"), ("2000","2012"), ("2013","2026")):
        x = m[(m.index.year >= int(a)) & (m.index.year <= int(b))]
        t, _ = t_sh(x)
        out += f"{x.mean():>+13.4f} t{t:>+6.2f}" if len(x) >= 24 else f"{'-':>20}"
    print(f"  {k:<18}{out}")
