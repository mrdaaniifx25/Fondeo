"""Carga los CSV M1 de HistData y los normaliza a un unico parquet en UTC.

HistData DOCUMENTA que sus timestamps son EST fijo sin horario de verano, pero
la verificacion empirica (bt/check_dst.py) demuestra lo contrario: el perfil de
volatilidad no se desplaza entre estaciones, lo que solo ocurre si los sellos de
tiempo siguen el reloj de Nueva York CON horario de verano. Por eso convertimos
con la zona America/New_York y no con un desplazamiento fijo.
"""
import glob, os
import pandas as pd

RAW = "data/raw"
OUT = "data/eurusd_m1.parquet"

def main():
    files = sorted(glob.glob(os.path.join(RAW, "DAT_ASCII_EURUSD_M1_*.csv")))
    frames = []
    for f in files:
        df = pd.read_csv(f, sep=";", header=None,
                         names=["ts", "open", "high", "low", "close", "vol"])
        df["ts"] = pd.to_datetime(df["ts"], format="%Y%m%d %H%M%S")
        frames.append(df.drop(columns=["vol"]))
    m1 = pd.concat(frames, ignore_index=True)
    n0 = len(m1)

    # Hora local de Nueva York (con DST) -> UTC.
    idx = pd.DatetimeIndex(m1["ts"])
    utc = idx.tz_localize("America/New_York", ambiguous="NaT",
                          nonexistent="NaT").tz_convert("UTC").tz_localize(None)
    m1["ts"] = utc
    perdidas = m1["ts"].isna().sum()
    m1 = m1.dropna(subset=["ts"])

    m1 = m1.sort_values("ts").drop_duplicates(subset="ts", keep="last")
    m1 = m1.reset_index(drop=True)

    print(f"{len(files)} ficheros | {n0:,} filas leidas")
    print(f"Descartadas por transicion de horario de verano: {perdidas}")
    print(f"TOTAL {len(m1):,} velas M1")
    print(f"Rango UTC: {m1.ts.min()} -> {m1.ts.max()}")
    bad = ((m1.high < m1.low) | (m1.high < m1.open) | (m1.high < m1.close)
           | (m1.low > m1.open) | (m1.low > m1.close)).sum()
    print(f"Velas con OHLC incoherente: {bad}")

    os.makedirs("data", exist_ok=True)
    m1.to_parquet(OUT, index=False)
    print(f"Guardado -> {OUT}")

if __name__ == "__main__":
    main()
