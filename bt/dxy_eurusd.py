"""Pre-registro docs/PREREGISTRO_dxy.md  ·  EURUSD y DXY, exhaustivo.

Se reconstruye el DXY con sus pesos oficiales a partir de las seis series
diarias de la Reserva Federal, 1999-2026, y se descompone:

    dlog DXY = -0,576 * dlog EURUSD + 0,424 * dNOEUR

La unica parte NO tautologica es NOEUR (yen, libra, CAD, SEK, CHF).

Rendimientos futuros a k dias SIN SOLAPE (un dia de cada k).

  python3 bt/dxy_eurusd.py
"""
import numpy as np, pandas as pd
from math import sqrt
rng = np.random.default_rng(20261013)

W = {"Euro": 0.576, "Japan": 0.136, "United Kingdom": 0.119,
     "Canada": 0.091, "Sweden": 0.042, "Switzerland": 0.036}

fx = pd.read_csv("data/ext/fx_daily.csv", parse_dates=["Date"])
S = {}
for p in W:
    s = fx[fx.Country == p].set_index("Date")["Exchange rate"].sort_index()
    s = s[s > 0]; S[p] = s[~s.index.duplicated()]
P = pd.DataFrame(S).dropna()
P = P[P.index >= "1999-01-01"]
# todas vienen como DIVISA POR DOLAR -> log DXY = suma ponderada de sus logs
lD = sum(W[p]*np.log(P[p]) for p in W)
lE = -np.log(P["Euro"])                      # log EURUSD = -log(EUR por USD)
D = pd.DataFrame({"lE": lE, "lD": lD}).dropna()
D["dE"], D["dD"] = D.lE.diff(), D.lD.diff()
# residuo: la parte de DXY que NO explica el euro  = 0,424 * dNOEUR
D["res"] = D.dD + W["Euro"]*D.dE
D["noeur"] = (sum(W[p]*np.log(P[p]) for p in W if p != "Euro")/(1-W["Euro"]))
D = D.dropna()
print(f"dias {len(D):,}  ·  {D.index.min():%Y-%m-%d} a {D.index.max():%Y-%m-%d}")
print(f"DXY reconstruido: nivel medio {np.exp(D.lD.mean())*50.14348112/np.exp(D.lD.mean()):.0f}"
      f" (escala irrelevante, se trabaja en logaritmos)\n")


def t_sin_solape(sig, fut_k, et, pasos=None):
    """t de corr(signo de sig, rendimiento futuro a k dias) SIN SOLAPE."""
    k = fut_k
    fwd = D.lE.shift(-k) - D.lE
    x = pd.DataFrame({"s": sig, "y": fwd}).dropna()
    paso = pasos or k
    x = x.iloc[::paso]
    if len(x) < 30: return None
    s = np.sign(x.s)
    r = (s*x.y).replace(0, np.nan).dropna()
    t = r.mean()/(r.std(ddof=1)/sqrt(len(r)))
    # placebo: signos barajados
    pl = [float((pd.Series(rng.permutation(s.to_numpy()), index=s.index)*x.y)
                .mean()) for _ in range(200)]
    return len(r), r.mean(), t, np.mean(pl), np.std(pl)


print("="*96); print("1 · LA IDENTIDAD MECANICA"); print("="*96)
c = D.dE.corr(D.dD)
b = np.polyfit(D.dE, D.dD, 1)
r2 = c**2
print(f"  correlacion diaria dEURUSD vs dDXY : {c:+.4f}")
print(f"  R2                                 : {r2:.4f}  -> el {100*r2:.1f} % de DXY ES EURUSD")
print(f"  pendiente                          : {b[0]:+.4f}  (teorica -0,576)")
print(f"  correlacion de NIVELES (log)       : {D.lE.corr(D.lD):+.4f}")
print(f"  desv. de dEURUSD {D.dE.std()*100:.3f} %  ·  del residuo {D.res.std()*100:.3f} %"
      f"  -> el residuo es el {100*D.res.std()/D.dD.std():.0f} % de la varianza de DXY")

print("\n" + "="*96); print("2 · ADELANTO Y RETRASO (correlacion cruzada)"); print("="*96)
print(f"  {'k':>4}{'corr(dE[t+k], dD[t])':>24}{'t':>9}   interpretacion")
for k in range(-5, 6):
    a = D.dE.shift(-k); x = pd.DataFrame({"a": a, "b": D.dD}).dropna()
    cc = x.a.corr(x.b); tt = cc*sqrt(len(x)-2)/sqrt(max(1-cc**2, 1e-12))
    et = "DXY adelanta" if k > 0 else ("simultaneo" if k == 0 else "EURUSD adelanta")
    print(f"  {k:>4}{cc:>24.4f}{tt:>9.1f}   {et}")

print("\n" + "="*96)
print("3 · PRINCIPAL · el RESIDUO de DXY (la parte no-euro) prediciendo EURUSD")
print("="*96)
print(f"  {'plazo':>7}{'n':>7}{'rend medio':>13}{'t':>8}{'placebo':>11}{'desv pl':>9}")
for k in (1, 5, 20):
    r = t_sin_solape(-D.res, k, f"res {k}d")     # residuo DXY arriba -> euro abajo
    if r: print(f"  {k:>6}d{r[0]:>7}{100*r[1]:>+12.4f}%{r[2]:>+8.2f}{100*r[3]:>+10.4f}%{100*r[4]:>8.4f}%")
print("  (signo invertido: DXY no-euro al alza deberia implicar EURUSD a la baja)")

print("\n" + "="*96); print("4 · MOMENTO DE LA CESTA NO-EURO prediciendo EURUSD"); print("="*96)
print(f"  {'momento':>9}{'plazo':>7}{'n':>7}{'rend medio':>13}{'t':>8}{'placebo':>11}")
for m in (1, 5, 20, 60):
    for k in (5, 20):
        sig = -(D.noeur - D.noeur.shift(m))
        r = t_sin_solape(sig, k, "")
        if r: print(f"  {m:>8}d{k:>6}d{r[0]:>7}{100*r[1]:>+12.4f}%{r[2]:>+8.2f}{100*r[3]:>+10.4f}%")

print("\n" + "="*96); print("5 · DIVERGENCIA SMT en diario"); print("="*96)
N = 20
maxE = D.lE.rolling(N).max().shift(1); minE = D.lE.rolling(N).min().shift(1)
minDx = D.lD.rolling(N).min().shift(1); maxDx = D.lD.rolling(N).max().shift(1)
altoE = D.lE > maxE; bajoDx = D.lD < minDx
bajoE = D.lE < minE; altoDx = D.lD > maxDx
div_baj = altoE & ~bajoDx     # euro rompe arriba y DXY NO rompe abajo -> bajista
con_baj = altoE & bajoDx      # los dos confirman
div_alc = bajoE & ~altoDx
con_alc = bajoE & altoDx
print(f"  {'caso':<34}{'n':>6}{'rend 5d sig.':>15}{'t':>8}")
for et, m, sg in (("euro rompe arriba, DXY NO abajo (div)", div_baj, -1),
                  ("euro rompe arriba, DXY sI abajo (conf)", con_baj, +1),
                  ("euro rompe abajo, DXY NO arriba (div)", div_alc, +1),
                  ("euro rompe abajo, DXY sI arriba (conf)", con_alc, -1),
                  ("TODOS los dias (control)", pd.Series(True, index=D.index), +1)):
    fwd = (D.lE.shift(-5) - D.lE)[m.fillna(False)].dropna()
    if len(fwd) < 30: continue
    r = sg*fwd
    print(f"  {et:<34}{len(r):>6}{100*r.mean():>+14.4f}%"
          f"{r.mean()/(r.std(ddof=1)/sqrt(len(r))):>+8.2f}")
print("  (el signo de cada caso es el que la teoria SMT predice)")

print("\n" + "="*96); print("6 · REVERSION DEL DIFERENCIAL ACUMULADO"); print("="*96)
acum = D.res.cumsum()
zsc = ((acum - acum.rolling(60).mean())/acum.rolling(60).std()).shift(1)
print(f"  {'z del residuo':>16}{'n':>7}{'rend 5d de EURUSD':>20}{'t':>8}")
for lo, hi, et in ((-99,-1.5,"z < -1,5"), (-1.5,-0.5,"-1,5 a -0,5"),
                   (-0.5,0.5,"-0,5 a +0,5"), (0.5,1.5,"+0,5 a +1,5"), (1.5,99,"z > +1,5")):
    m = (zsc > lo) & (zsc <= hi)
    fwd = (D.lE.shift(-5) - D.lE)[m].dropna().iloc[::5]
    if len(fwd) < 30: continue
    print(f"  {et:>16}{len(fwd):>7}{100*fwd.mean():>+19.4f}%"
          f"{fwd.mean()/(fwd.std(ddof=1)/sqrt(len(fwd))):>+8.2f}")

print("\n" + "="*96); print("7 · PARTICION TEMPORAL del principal (residuo, 5 dias)"); print("="*96)
for a, b2 in (("1999","2012"), ("2013","2026")):
    sub = D[(D.index.year >= int(a)) & (D.index.year <= int(b2))]
    fwd = sub.lE.shift(-5) - sub.lE
    x = pd.DataFrame({"s": -sub.res, "y": fwd}).dropna().iloc[::5]
    r = (np.sign(x.s)*x.y).dropna()
    print(f"  {a}-{b2}: n {len(r):>5}  rend {100*r.mean():>+8.4f}%  "
          f"t {r.mean()/(r.std(ddof=1)/sqrt(len(r))):>+6.2f}")
print(f"\n  MURO de coste en EURUSD diario: 0,0226 en unidades de ruido diario.")
print(f"  Desv. diaria de EURUSD: {100*D.dE.std():.3f} %  -> el coste equivale a "
      f"{100*0.0226*D.dE.std():.4f} % por operacion.")
