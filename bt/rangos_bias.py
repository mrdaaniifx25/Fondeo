"""Rangos por temporalidad (D1, H4, H1, M15) y bias diario.

Pre-registro: docs/PREREGISTRO_rangos_bias.md

1 · tamaño real de cada rango, en pips
2 · que hace la vela siguiente con el rango de la anterior, y con que frecuencia
    barre y cierra otra vez dentro (el montaje del CRT)
3 · cinco definiciones de bias diario, contrastadas contra el movimiento del dia

  python3 bt/rangos_bias.py
"""
import numpy as np, pandas as pd, sys

PIP = 1e-4
M = pd.read_parquet("data/eurusd_m1.parquet")
M["utc"] = M.ts
ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")        # dia FX, cierre 17:00 NY
print(f"M1: {len(M)} velas · {M.ts.iloc[0]} -> {M.ts.iloc[-1]} (UTC)")

def agrega(clave):
    g = M.groupby(clave)
    V = g.agg(o=("open","first"), h=("high","max"), l=("low","min"),
              c=("close","last"), n=("close","size"))
    return V[V.n >= 3]                     # descarta velas mutiladas por huecos

TF = {}
TF["D1"]  = agrega("dfx")
TF["H4"]  = agrega(M.utc.dt.floor("4h"))   # alineado a 00/04/08/12/16/20 UTC
TF["H1"]  = agrega(M.utc.dt.floor("1h"))
TF["M15"] = agrega(M.utc.dt.floor("15min"))

print("\n" + "="*74)
print("1 · TAMAÑO DEL RANGO (alto - bajo), en pips")
print("="*74)
print(f"  {'tf':<5}{'n':>8}{'p25':>9}{'MEDIANA':>10}{'p75':>9}{'p95':>9}{'media':>9}")
for k in ("D1","H4","H1","M15"):
    r = ((TF[k].h - TF[k].l) / PIP).to_numpy()
    print(f"  {k:<5}{len(r):>8}{np.percentile(r,25):>9.1f}{np.median(r):>10.1f}"
          f"{np.percentile(r,75):>9.1f}{np.percentile(r,95):>9.1f}{r.mean():>9.1f}")

print("\n" + "="*74)
print("2 · QUE HACE LA VELA SIGUIENTE CON EL RANGO DE LA ANTERIOR")
print("="*74)
print(f"  {'tf':<5}{'n':>7}{'solo alto':>11}{'solo bajo':>11}{'los dos':>10}"
      f"{'interior':>10}")
EST = {}
for k in ("D1","H4","H1","M15"):
    V = TF[k]
    ph = V.h.shift(1).to_numpy(); pl = V.l.shift(1).to_numpy()
    h = V.h.to_numpy(); l = V.l.to_numpy(); c = V.c.to_numpy()
    ok = np.isfinite(ph)
    sa = (h > ph) & ok; sb = (l < pl) & ok
    dos = sa & sb; solo_a = sa & ~sb; solo_b = sb & ~sa
    dentro = (~sa) & (~sb) & ok
    n = ok.sum()
    EST[k] = dict(ph=ph, pl=pl, h=h, l=l, c=c, ok=ok, sa=sa, sb=sb)
    print(f"  {k:<5}{n:>7}{100*solo_a.sum()/n:>10.1f}%{100*solo_b.sum()/n:>10.1f}%"
          f"{100*dos.sum()/n:>9.1f}%{100*dentro.sum()/n:>9.1f}%")

print("\n  BARRE Y CIERRA OTRA VEZ DENTRO (el montaje del CRT):")
print(f"  {'tf':<5}{'barre alto':>12}{'y cierra dentro':>18}{'barre bajo':>13}"
      f"{'y cierra dentro':>18}")
for k in ("D1","H4","H1","M15"):
    e = EST[k]; n = e["ok"].sum()
    ra = e["sa"] & (e["c"] < e["ph"])
    rb = e["sb"] & (e["c"] > e["pl"])
    print(f"  {k:<5}{100*e['sa'].sum()/n:>11.1f}%{100*ra.sum()/e['sa'].sum():>17.1f}%"
          f"{100*e['sb'].sum()/n:>12.1f}%{100*rb.sum()/e['sb'].sum():>17.1f}%")

print("\n  Y DESPUES DE BARRER Y CERRAR DENTRO, ¿QUE HACE LA VELA SIGUIENTE?")
print("  (movimiento de la vela siguiente, en pips, en la direccion que predice el CRT)")
print(f"  {'tf':<5}{'n':>7}{'media pips':>12}{'t':>8}{'acierto':>10}{'ciego':>9}")
for k in ("D1","H4","H1","M15"):
    V = TF[k]; e = EST[k]
    o2 = V.o.shift(-1).to_numpy(); c2 = V.c.shift(-1).to_numpy()
    ra = e["sa"] & (e["c"] < e["ph"]) & np.isfinite(c2)      # -> predice bajada
    rb = e["sb"] & (e["c"] > e["pl"]) & np.isfinite(c2)      # -> predice subida
    mv = np.concatenate([-(c2[ra]-o2[ra])/PIP, (c2[rb]-o2[rb])/PIP])
    base = np.abs(np.concatenate([(c2[e["ok"]]-o2[e["ok"]])/PIP]))
    if len(mv) < 50: continue
    t = mv.mean()/(mv.std(ddof=1)/np.sqrt(len(mv)))
    todos = (c2[e["ok"]]-o2[e["ok"]])/PIP
    todos = todos[np.isfinite(todos)]
    print(f"  {k:<5}{len(mv):>7}{mv.mean():>12.3f}{t:>8.2f}{100*(mv>0).mean():>9.1f}%"
          f"{100*(todos>0).mean():>8.1f}%")
    sys.stdout.flush()

print("\n" + "="*74)
print("3 · EL BIAS DIARIO · cinco definiciones, todas causales")
print("="*74)
D = TF["D1"].copy()
o=D.o.to_numpy(); h=D.h.to_numpy(); l=D.l.to_numpy(); c=D.c.to_numpy()
tr = np.maximum.reduce([h-l, np.abs(h-np.roll(c,1)), np.abs(l-np.roll(c,1))])
tr[0] = h[0]-l[0]
atr = pd.Series(tr).rolling(14).mean().shift(1).to_numpy()   # ATR hasta AYER
mov = (c - o) / atr                                           # movimiento del dia, en ATR
ema20 = pd.Series(c).ewm(span=20, adjust=False).mean().shift(1).to_numpy()
ph, pl, pc, po = (np.roll(x,1) for x in (h,l,c,o))
pph, ppl = np.roll(h,2), np.roll(l,2)
med_ayer = (ph + pl) / 2

A = np.sign(pc - po)                                          # vela de ayer
B = np.where(o > ph, 1.0, np.where(o < pl, -1.0, 0.0))        # apertura vs rango de ayer
C = np.sign(pc - med_ayer)                                    # cierre vs punto medio
Dd = np.where((pl < ppl) & (pc > ppl), 1.0,
     np.where((ph > pph) & (pc < pph), -1.0, 0.0))            # barrido CRT
E = np.sign(pc - ema20)                                       # cierre vs EMA20

val = np.isfinite(mov) & np.isfinite(atr)
val[:260] = False
print(f"  dias validos: {val.sum()}")
print(f"  {'bias':<42}{'n':>7}{'media ATR':>11}{'t':>8}{'acierto':>10}")
res = []
for nom, s in (("A · direccion de la vela de ayer", A),
               ("B · apertura de hoy vs rango de ayer", B),
               ("C · cierre de ayer vs punto medio", C),
               ("D · barrido CRT de ayer", Dd),
               ("E · cierre de ayer vs EMA20 diaria", E)):
    m = val & np.isin(s, (1.0, -1.0))
    x = s[m] * mov[m]
    t = x.mean()/(x.std(ddof=1)/np.sqrt(len(x)))
    print(f"  {nom:<42}{len(x):>7}{x.mean():>11.4f}{t:>8.2f}{100*(x>0).mean():>9.1f}%")
    res.append((nom, len(x), x.mean(), t))
    sys.stdout.flush()
mm = val
print(f"  {'(control) comprar siempre':<42}{mm.sum():>7}{mov[mm].mean():>11.4f}"
      f"{mov[mm].mean()/(mov[mm].std(ddof=1)/np.sqrt(mm.sum())):>8.2f}"
      f"{100*(mov[mm]>0).mean():>9.1f}%")
se = mov[val].std(ddof=1)/np.sqrt(val.sum())
print(f"\n  error estandar con n={val.sum()}: {se:.4f} ATR -> detecta {2*se:+.4f} a t=2")
print(f"  liston con 5 definiciones: E[max|t|] ~ {np.sqrt(2*np.log(5)):.2f}; exijo 2,33")
mejor = max(res, key=lambda r: abs(r[3]))
print(f"  MEJOR: {mejor[0]} con t {mejor[3]:+.2f}" +
      ("  -> PASA" if abs(mejor[3]) >= 2.33 else "  -> no pasa"))

print("\n  ¿Y si el bias sirve sólo para FILTRAR, no para predecir?")
print("  (movimiento del dia cuando el bias coincide con la vela de ayer)")
m2 = val & (A != 0) & (E != 0) & (A == E)
x2 = A[m2]*mov[m2]
print(f"    A y E de acuerdo        n {m2.sum():>5}  media {x2.mean():+.4f}  "
      f"t {x2.mean()/(x2.std(ddof=1)/np.sqrt(len(x2))):+.2f}")
m3 = val & (A != 0) & (E != 0) & (A != E)
x3 = A[m3]*mov[m3]
print(f"    A y E en desacuerdo     n {m3.sum():>5}  media {x3.mean():+.4f}  "
      f"t {x3.mean()/(x3.std(ddof=1)/np.sqrt(len(x3))):+.2f}")
