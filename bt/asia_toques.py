"""docs/PREREGISTRO_asia_toques.md · se ejecuta UNA vez.

Parte la muestra ya fijada de bt/asia_nivel.py por el numero de veces que el
nivel fue tocado ese dia antes del disparo. No genera operaciones nuevas.
"""
import numpy as np, pandas as pd

U, COSTE, TZ = 0.0001, 1.2, "Europe/Madrid"

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date.astype(str); v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
H, L = v.h.to_numpy(), v.l.to_numpy()

# nivel de Asia de cada dia
niveles = {}
for dia, g in v.groupby("dia"):
    a = g[g.hm < 800]
    if len(a) >= 60: niveles[dia] = (float(a.h.max()), float(a.l.min()))

t = pd.read_csv("data/asia_nivel.csv", parse_dates=["ts"])
t["dia"] = t.dia.astype(str)

# indice de la primera vela de cada dia a partir de las 08:00
ini = {d: int(g.index[0]) for d, g in v[v.hm >= 800].groupby("dia")}

toques = []
for r in t.itertuples():
    hi, lo = niveles[r.dia]
    niv = hi if r.nivel == "alto" else lo
    i0 = ini[r.dia]
    prev = slice(i0, r.i)                      # desde las 08:00 hasta la vela de entrada, excluida
    toques.append(int(((L[prev] <= niv) & (H[prev] >= niv)).sum()))
t["toques"] = toques
t["neto"] = t.R - COSTE / t.riesgo
t.to_csv("data/asia_toques.csv", index=False)

def dia(s): return s.groupby("dia").agg(R=("R","mean"), neto=("neto","mean"))

def contraste(nom, s):
    a, b = s[s.toques >= 1], s[s.toques == 0]
    da, db = dia(a), dia(b)
    ma, mb = da.neto.mean(), db.neto.mean()
    ea = da.neto.std(ddof=1)/np.sqrt(len(da)); eb = db.neto.std(ddof=1)/np.sqrt(len(db))
    dif = ma - mb; ee = np.sqrt(ea**2 + eb**2)
    print(f"\n{nom}")
    print(f"  {'':<22}{'n':>7}{'días':>7}{'%TP':>8}{'riesgo':>9}{'NETA/día':>11}{'z':>8}")
    for et, x, dd, m, e in (("nivel YA tocado", a, da, ma, ea), ("primera visita", b, db, mb, eb)):
        print(f"  {et:<22}{len(x):>7,}{len(dd):>7,}{100*(x.motivo=='TP').mean():>7.1f}%"
              f"{x.riesgo.median():>8.1f}p{m:>+11.3f}{m/e:>+8.2f}".replace(",", "."))
    print(f"  {'DIFERENCIA':<22}{'':>7}{'':>7}{'':>8}{'':>9}{dif:>+11.3f}{dif/ee:>+8.2f}"
          f"   {'predicha (positiva)' if dif > 0 else 'AL REVÉS de lo predicho'}")

print("=" * 92)
print("EL NIVEL YA TOCADO · docs/PREREGISTRO_asia_toques.md · una sola vez")
print("=" * 92)
contraste("PRINCIPAL · 2020-2025", t[t.ts < "2026-01-01"])
contraste("SECUNDARIA · enero-mayo 2026 (no lo ha visto)", t[(t.ts >= "2026-01-01") & (t.ts < "2026-06-01")])

print("\n\n--- exploratorio, no preregistrado ---")
s = t[t.ts < "2026-01-01"]
print(f"  {'toques':<12}{'n':>8}{'días':>7}{'%TP':>8}{'neta/día':>11}{'z':>8}")
for et, m in (("0", s.toques == 0), ("1-2", s.toques.between(1,2)), ("3-5", s.toques.between(3,5)),
              ("6+", s.toques >= 6)):
    x = s[m]
    if len(x) < 30: continue
    d = dia(x); e = d.neto.std(ddof=1)/np.sqrt(len(d))
    print(f"  {et:<12}{len(x):>8,}{len(d):>7,}{100*(x.motivo=='TP').mean():>7.1f}%"
          f"{d.neto.mean():>+11.3f}{d.neto.mean()/e:>+8.2f}".replace(",", "."))

# ---------------------------------------------------------------------------
# EXPLORATORIO, no preregistrado: cierres previos MÁS ALLÁ del nivel.
# Él describe una ruptura previa que pierde fuerza, no un simple toque.
# Es un segundo vistazo a los mismos datos: vale para orientar, no para probar.
# ---------------------------------------------------------------------------
C5 = v.c.to_numpy()
fuera = []
for r in t.itertuples():
    hi, lo = niveles[r.dia]
    niv = hi if r.nivel == "alto" else lo
    prev = slice(ini[r.dia], r.i)
    cc = C5[prev]
    fuera.append(int((cc > niv).sum() if r.lado > 0 else (cc < niv).sum()))
t["fuera"] = fuera
t.to_csv("data/asia_toques.csv", index=False)

print("\n\n--- EXPLORATORIO · cierres previos al otro lado del nivel (2020-2025) ---")
s = t[t.ts < "2026-01-01"]
print(f"  {'cierres fuera':<16}{'n':>8}{'días':>7}{'%TP':>8}{'riesgo':>9}{'neta/día':>11}{'z':>8}")
for et, m in (("0", s.fuera == 0), ("1-3", s.fuera.between(1,3)), ("4-9", s.fuera.between(4,9)),
              ("10+", s.fuera >= 10)):
    x = s[m]
    if len(x) < 30: continue
    d = dia(x); e = d.neto.std(ddof=1)/np.sqrt(len(d))
    print(f"  {et:<16}{len(x):>8,}{len(d):>7,}{100*(x.motivo=='TP').mean():>7.1f}%{x.riesgo.median():>8.1f}p"
          f"{d.neto.mean():>+11.3f}{d.neto.mean()/e:>+8.2f}".replace(",", "."))
a, b = s[s.fuera >= 1], s[s.fuera == 0]
da, db = dia(a), dia(b)
dif = da.neto.mean() - db.neto.mean()
ee = np.sqrt((da.neto.std(ddof=1)**2)/len(da) + (db.neto.std(ddof=1)**2)/len(db))
print(f"  diferencia (>=1 menos 0): {dif:+.3f}  z {dif/ee:+.2f}")
