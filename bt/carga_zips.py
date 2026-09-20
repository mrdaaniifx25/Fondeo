"""Reconstruye los parquet M1 desde los ZIP de HistData que hay en el repo.

Hizo falta el 19-09-2026: el contenedor se reinicio, el clon vino limpio y los
parquet nunca estuvieron versionados (eran demasiado grandes). Los ZIP si.

HistData da la marca de tiempo en hora de Nueva York CON horario de verano,
no EST fijo. Misma conversion que bt/load_data.py.
"""
import glob, io, os, re, sys, zipfile
import pandas as pd

def lee_zip(ruta):
    z = zipfile.ZipFile(ruta)
    n = [x for x in z.namelist() if x.lower().endswith(".csv")][0]
    d = pd.read_csv(io.BytesIO(z.read(n)), sep=";", header=None,
                    usecols=[0, 1, 2, 3, 4],
                    names=["ts", "open", "high", "low", "close"])
    t = pd.to_datetime(d.ts, format="%Y%m%d %H%M%S")
    d["ts"] = (t.dt.tz_localize("America/New_York", ambiguous="NaT",
                                nonexistent="shift_forward")
                .dt.tz_convert("UTC").dt.tz_localize(None))
    return d.dropna(subset=["ts"])

def junta(patrones, salida):
    fich = []
    for p in patrones: fich.extend(sorted(glob.glob(p)))
    if not fich:
        print(f"  sin ficheros para {salida}"); return None
    D = pd.concat([lee_zip(f) for f in fich], ignore_index=True)
    D = D.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    D.to_parquet(salida, index=False)
    print(f"  {salida}: {len(D):,} minutos   "
          f"{D.ts.min():%Y-%m-%d} a {D.ts.max():%Y-%m-%d}   "
          f"({len(fich)} ficheros)")
    return D

os.makedirs("data", exist_ok=True)
print("reconstruyendo desde los ZIP del repositorio:")
# 20-09-2026: los patrones de ???? solo cogian los ZIP anuales y se dejaban
# fuera los mensuales (XAUUSD_M1202601_1.zip). Ahora entra todo.
junta(["material/*XAUUSD_M1*.zip", "reservado/*XAUUSD_M1*.zip"], "data/xauusd_m1.parquet")
junta(["material/*GRXEUR_M1*.zip", "reservado/*GRXEUR_M1*.zip"], "data/grxeur_m1.parquet")
junta(["material/*EURUSD_M1*.zip"], "data/eurusd_m1.parquet")
