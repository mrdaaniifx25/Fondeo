"""Prueba decisiva del huso: el perfil de volatilidad debe DESPLAZARSE entre
verano e invierno si la conversion (+5h fija) es correcta.

  Caso A - los datos son EST fijo y +5h da UTC real:
      Londres abre 08:00 UTC en invierno y 07:00 UTC en verano (BST).
      -> el pico se mueve una hora entre estaciones.

  Caso B - los datos son hora local de Nueva York CON horario de verano:
      en verano habria que sumar +4h, no +5h, asi que nuestra serie va
      una hora adelantada y el pico de Londres aparece a las 08:00 SIEMPRE.
      -> el pico NO se mueve.
"""
import pandas as pd

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1["rango"] = (m1["high"] - m1["low"]) * 10000
m1["hora"] = m1["ts"].dt.hour

# Periodo de horario de verano de EEUU: 2o domingo de marzo -> 1er domingo nov.
idx = pd.DatetimeIndex(m1["ts"])
ny = idx.tz_localize("UTC").tz_convert("America/New_York")
m1["dst"] = (ny.map(lambda t: t.dst().total_seconds() != 0)).astype(bool)

print("Velas en horario de verano :", f"{m1.dst.sum():,}")
print("Velas en horario de invierno:", f"{(~m1.dst).sum():,}\n")

inv = m1[~m1.dst].groupby("hora")["rango"].mean()
ver = m1[m1.dst].groupby("hora")["rango"].mean()

print("hora UTC | invierno | verano  |  (barra = invierno / verano)")
for h in range(24):
    a, b = inv.get(h, 0), ver.get(h, 0)
    print(f"  {h:02d}:00  |  {a:5.2f}   |  {b:5.2f}  | "
          f"{'#' * int(a/inv.max()*26):26s} {'*' * int(b/ver.max()*26)}")

print(f"\nPico de la manana (05-11 UTC):")
print(f"  invierno -> {inv.loc[5:11].idxmax():02d}:00")
print(f"  verano   -> {ver.loc[5:11].idxmax():02d}:00")
print(f"\nPico de la tarde (12-18 UTC):")
print(f"  invierno -> {inv.loc[12:18].idxmax():02d}:00")
print(f"  verano   -> {ver.loc[12:18].idxmax():02d}:00")

print("\nSi los picos NO se mueven entre estaciones -> CASO B: hay que")
print("reconvertir con America/New_York (DST) en vez de +5h fijo.")
