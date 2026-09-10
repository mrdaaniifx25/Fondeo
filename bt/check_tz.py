"""Verifica empiricamente el huso horario de los datos ya convertidos a 'UTC'.

Dos pruebas independientes:
  1. El hueco semanal. El mercado FX cierra viernes 17:00 ET y abre domingo
     17:00 ET. Si HistData usa EST fijo, en nuestra serie deberia aparecer
     siempre a las 22:00 UTC, en invierno y en verano. Si se desplaza a 21:00
     en verano, es que aplican horario de verano y la conversion fija esta mal.
  2. El perfil de volatilidad por hora. El rango medio de la vela M1 tiene que
     dispararse en la apertura de Londres (08:00 UTC) y de Nueva York
     (13:30 UTC). Si los picos no caen ahi, hay desfase.
"""
import pandas as pd

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])

# ---- 1. hueco semanal -------------------------------------------------------
d = m1["ts"].diff()
big = m1.loc[d > pd.Timedelta(hours=12), "ts"]          # aperturas de semana
prev = m1["ts"].shift(1).loc[big.index]                  # cierres de semana
wk = pd.DataFrame({"cierre": prev.values, "apertura": big.values})
wk["mes"] = wk["apertura"].dt.month
wk["h_cierre"] = wk["cierre"].dt.hour
wk["h_apertura"] = wk["apertura"].dt.hour
wk["invierno"] = wk["mes"].isin([12, 1, 2, 11])

print("=== 1. HUECO SEMANAL (hora UTC de la apertura del domingo) ===")
print(wk.groupby(["invierno", "h_apertura"]).size().rename("semanas").to_frame())
print()
print("Cierres de viernes por hora UTC:")
print(wk.groupby(["invierno", "h_cierre"]).size().rename("semanas").to_frame())

# ---- 2. perfil de volatilidad por hora --------------------------------------
m1["rango_pips"] = (m1["high"] - m1["low"]) * 10000
m1["hora"] = m1["ts"].dt.hour
perfil = m1.groupby("hora")["rango_pips"].mean()
print("\n=== 2. RANGO MEDIO DE LA VELA M1 POR HORA UTC (pips) ===")
mx = perfil.max()
for h, v in perfil.items():
    barra = "#" * int(round(v / mx * 55))
    print(f"  {h:02d}:00  {v:5.2f}  {barra}")
print(f"\nTop 4 horas: {list(perfil.nlargest(4).index)}")

# ---- 3. estructura por ano (los ficheros de 2026 venian distinto) -----------
print("\n=== 3. PRIMERA Y ULTIMA HORA UTC OBSERVADA POR ANO ===")
m1["ano"] = m1["ts"].dt.year
for a, g in m1.groupby("ano"):
    horas = sorted(g["hora"].unique())
    print(f"  {a}: {len(g):>9,} velas | horas presentes: {len(horas)}/24 "
          f"| min={g.ts.min()} max={g.ts.max()}")
