"""Pre-registro docs/PREREGISTRO_reloj.md

La pregunta simple que nunca se hizo: que hace el precio, de media, en cada
hora del dia. Sin patron, sin nivel, sin barrido.
"""
import numpy as np, pandas as pd
from math import sqrt

TZ = "Europe/Madrid"
INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 1.43),
       ("oro",    "data/xauusd_m1.parquet", 0.01, 35.0),
       ("DAX",    "data/grxeur_m1.parquet", 1.0,   1.6)]
SES = {"Asia 00-08": (0, 8), "Londres 08-14": (8, 14), "NuevaYork 14-23": (14, 23)}

def carga(ruta):
    d = pd.read_parquet(ruta); d["ts"] = pd.to_datetime(d["ts"])
    d = d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    d["loc"] = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    return d.set_index("loc")

def barras(d, regla):
    g = (d.resample(regla).agg(o=("open","first"), c=("close","last"),
                               n=("close","size")).dropna())
    return g[g.n > 0]

def ficha(et, r, coste_ruido, ind="  ", n_min=100):
    r = r.dropna()
    if len(r) < n_min: return print(f"{ind}{et:<22} (pocas: {len(r)})")
    m, s = r.mean(), r.std(ddof=1)
    if s <= 0: return
    ef = m/s                                  # en unidades de ruido de esa barra
    ee = 1/sqrt(len(r))
    neto = ef - coste_ruido
    print(f"{ind}{et:<22} n {len(r):>6,}  bruto {ef:>+7.4f} [{ef-1.96*ee:>+.4f},{ef+1.96*ee:>+.4f}]"
          f"  muro {coste_ruido:>6.4f}  NETO {neto:>+8.4f}"
          f"{'   CRUZA' if ef-1.96*ee > coste_ruido else ''}")
    return ef, ee, neto

DAT = {}
for nom, ruta, U, co in INS:
    d = carga(ruta); DAT[nom] = (d, U, co)
    print(f"{nom}: {len(d):,} minutos, {d.index.min():%Y-%m-%d} a {d.index.max():%Y-%m-%d}")

print("\n" + "="*112)
print("PRINCIPAL declarado · la sesión de LONDRES completa (08:00-14:00) en EURUSD, comprada siempre")
print("="*112)
d, U, co = DAT["EURUSD"]
h1 = barras(d, "1h"); h1["h"] = h1.index.hour; h1["dia"] = h1.index.normalize()
lon = h1[(h1.h >= 8) & (h1.h < 14)].groupby("dia").agg(o=("o","first"), c=("c","last"),
                                                        n=("n","sum"))
lon = lon[lon.n > 250]
r = np.log(lon.c/lon.o)
muro = co*U/ (r.std()*lon.o.mean())          # coste en unidades del ruido de la sesion
ficha("Londres · EURUSD", r, muro)
print(f"\n  ruido de la sesion: {100*r.std():.3f} %  ·  coste {co*U/lon.o.mean()*100:.4f} %"
      f"  ·  muro {muro:.4f}")
print("\n  por año:")
for a, g in r.groupby(r.index.year):
    ficha(f"{a}", g, muro, ind="    ", n_min=60)

print("\n" + "="*112); print("LAS TRES SESIONES, EN LOS TRES INSTRUMENTOS"); print("="*112)
for nom, (d, U, co) in DAT.items():
    print(f"\n  {nom}")
    h1 = barras(d, "1h"); h1["h"] = h1.index.hour; h1["dia"] = h1.index.normalize()
    for et, (a, b) in SES.items():
        s = h1[(h1.h >= a) & (h1.h < b)].groupby("dia").agg(o=("o","first"), c=("c","last"),
                                                            n=("n","sum"))
        s = s[s.n > (b-a)*40]
        if len(s) < 100: continue
        rr = np.log(s.c/s.o)
        mu = co*U/(rr.std()*s.o.mean())
        ficha(et, rr, mu, ind="    ")

print("\n" + "="*112); print("EL RELOJ · las 24 horas (EXPLORATORIO, 72 celdas)"); print("="*112)
mejor = {}
for nom, (d, U, co) in DAT.items():
    h1 = barras(d, "1h"); h1["h"] = h1.index.hour
    rr = np.log(h1.c/h1.o)
    print(f"\n  {nom}   (muro de una hora: ", end="")
    mu = co*U/(rr.std()*h1.o.mean()); print(f"{mu:.4f})")
    fila = ""
    best = (0.0, None)
    for hh in range(24):
        x = rr[h1.h == hh].dropna()
        if len(x) < 200: continue
        ef = x.mean()/x.std(ddof=1); ee = 1/sqrt(len(x))
        if abs(ef) > abs(best[0]): best = (ef, hh)
        marca = "*" if abs(ef) > 1.96*ee else " "
        fila += f"{hh:02d}h {ef:>+7.4f}{marca}  "
        if (hh+1) % 4 == 0: print("    " + fila); fila = ""
    if fila: print("    " + fila)
    mejor[nom] = best
    if best[1] is not None:
        print(f"    mejor hora: {best[1]:02d}h con {best[0]:+.4f}   "
              f"(muro {mu:.4f} · sesgo de seleccion +0,065)")

print("\n" + "="*112); print("LA NOCHE CONTRA EL DIA"); print("="*112)
for nom, (d, U, co) in DAT.items():
    dd = barras(d, "1D"); dd = dd[dd.n > 200]
    noche = np.log(dd.o/dd.c.shift(1)).dropna()      # cierre -> apertura siguiente
    diurno = np.log(dd.c/dd.o).dropna()
    mu = co*U/(noche.std()*dd.o.mean())
    print(f"\n  {nom}")
    ficha("noche (cierre->apertura)", noche, mu, ind="    ")
    ficha("dia (apertura->cierre)", diurno, co*U/(diurno.std()*dd.o.mean()), ind="    ")

print("\n" + "="*112); print("EL DIA DE LA SEMANA · EURUSD"); print("="*112)
d, U, co = DAT["EURUSD"]
dd = barras(d, "1D"); dd = dd[dd.n > 200]
r = np.log(dd.c/dd.o)
mu = co*U/(r.std()*dd.o.mean())
for i, et in enumerate(["lunes","martes","miércoles","jueves","viernes"]):
    ficha(et, r[r.index.dayofweek == i], mu, ind="  ", n_min=60)


print("\n" + "="*112)
print("EL CONTROL QUE DECIDE · ¿la sesión aporta algo, o es sólo la deriva del instrumento?")
print("="*112)
print("  El oro sube un 40 % en 2023-2026. Cualquier trozo del día suyo sale positivo.")
print("  La pregunta correcta: ¿rinde esa sesión MÁS de lo que le toca por horas?\n")
print(f"{'instrumento':<10}{'sesión':<18}{'horas':>7}{'su parte':>10}{'deriva real':>13}"
      f"{'lo que le toca':>16}{'EXCESO':>12}{'t':>8}")
print("-"*96)
for nom, (d, U, co) in DAT.items():
    dd = barras(d, "1D"); dd = dd[dd.n > 200]
    dia_r = np.log(dd.c/dd.o).dropna()
    dia_m = dia_r.mean()                       # deriva media de un dia entero
    h1 = barras(d, "1h"); h1["h"] = h1.index.hour; h1["dia"] = h1.index.normalize()
    horas_dia = h1.groupby("dia").size()
    horas_dia = horas_dia[horas_dia > 8].mean()
    for et, (a, b) in SES.items():
        s_ = h1[(h1.h >= a) & (h1.h < b)].groupby("dia").agg(o=("o","first"), c=("c","last"),
                                                             n=("n","sum"))
        s_ = s_[s_.n > (b-a)*40]
        if len(s_) < 100: continue
        rr = np.log(s_.c/s_.o).dropna()
        parte = (b-a)/horas_dia
        toca = dia_m*parte
        exc = rr.mean() - toca
        t = exc/(rr.std(ddof=1)/sqrt(len(rr)))
        print(f"{nom:<10}{et:<18}{b-a:>7}{100*parte:>9.0f}%{100*rr.mean():>12.4f}%"
              f"{100*toca:>15.4f}%{100*exc:>+11.4f}%{t:>+8.2f}")
    print()
print("  'lo que le toca' = deriva del dia entero x (horas de la sesion / horas del dia)")
print("  Si el exceso no se distingue de cero, la sesion no aporta nada: es el instrumento.")
