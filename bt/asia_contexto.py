"""docs/PREREGISTRO_asia_contexto.md · una sola vez."""
import numpy as np, pandas as pd
COSTE, TZ = 1.43, "Europe/Madrid"

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1 = m1.set_index("ts")

def marco(regla):
    g = m1.close.resample(regla).last().dropna()
    return g

h1  = marco("1h")
m15 = marco("15min")

def direccion(serie, ts, atras, minutos):
    """signo de las ultimas `atras` barras REALMENTE CERRADAS antes de ts.

    El indice de `serie` son horas de APERTURA, asi que una barra solo esta
    cerrada si su apertura + su duracion es menor o igual que ts. Restar la
    duracion antes de buscar es lo que evita leer una vela en formacion.
    """
    lim = ts - np.timedelta64(minutos, "m")
    idx = serie.index.searchsorted(lim, side="right") - 1
    out = np.zeros(len(ts), dtype=int)
    ok = idx >= atras
    a = serie.to_numpy()
    out[ok] = np.sign(a[idx[ok]] - a[idx[ok] - atras])
    return out

t = pd.read_csv("data/asia_nivel.csv", parse_dates=["ts"])
ts = t.ts.to_numpy()
t["dirH1"]  = direccion(h1,  ts, 4, 60)
t["dirM15"] = direccion(m15, ts, 4, 15)
t["favH1"]  = t.dirH1  == t.lado
t["favM15"] = t.dirM15 == t.lado
t["neto"]   = t.R - COSTE / t.riesgo
t.to_csv("data/asia_contexto.csv", index=False)

def dia(s): return s.groupby("dia").agg(R=("R","mean"), neto=("neto","mean"))

def contraste(nom, s, mask, etA, etB):
    a, b = s[mask], s[~mask]
    da, db = dia(a), dia(b)
    ma, mb = da.neto.mean(), db.neto.mean()
    ea = da.neto.std(ddof=1)/np.sqrt(len(da)); eb = db.neto.std(ddof=1)/np.sqrt(len(db))
    dif = ma - mb; ee = np.sqrt(ea**2 + eb**2)
    print(f"\n  {nom}")
    for et, x, d, m, e in ((etA, a, da, ma, ea), (etB, b, db, mb, eb)):
        print(f"    {et:<22}{len(x):>7,}{len(d):>7,}{100*(x.motivo=='TP').mean():>7.1f}%"
              f"{x.R.mean():>+9.3f}{m:>+10.3f}{m/e:>+8.2f}".replace(",", "."))
    marca = "SÍ" if (dif > 0 and abs(dif/ee) >= 2.39) else ("signo bien, sin fuerza" if dif > 0 else "AL REVÉS")
    print(f"    {'DIFERENCIA':<22}{'':>7}{'':>7}{'':>8}{'':>9}{dif:>+10.3f}{dif/ee:>+8.2f}   {marca}")

for et, s in (("PRINCIPAL · 2020-2025", t[t.ts < "2026-01-01"]),
              ("SECUNDARIA · enero-mayo 2026", t[(t.ts >= "2026-01-01") & (t.ts < "2026-06-01")])):
    print("\n" + "=" * 88); print(et); print("=" * 88)
    print(f"  {'':<22}{'n':>7}{'días':>7}{'%TP':>8}{'R/op':>9}{'neta/d':>10}{'z':>8}")
    contraste("1 · contexto de M15", s, s.favM15, "M15 a favor", "M15 en contra")
    contraste("2 · contexto de H1",  s, s.favH1,  "H1 a favor",  "H1 en contra")
    contraste("3 · las dos a favor", s, s.favM15 & s.favH1, "M15 y H1 a favor", "el resto")
