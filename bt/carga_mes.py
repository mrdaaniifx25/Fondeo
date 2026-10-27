"""Ingesta de un mes suelto de HistData (ZIP o CSV) al parquet mensual.

HistData publica el mes EN CURSO como instantanea parcial y solo cierra el mes
completo unos dias despues de acabar. Por eso este script avisa siempre de hasta
donde llega el fichero: si el corte no ha avanzado, la descarga no ha traido
nada nuevo y no merece la pena rehacer los calculos de aguas abajo.

Conversion horaria: hora de Nueva York CON horario de verano, no EST fijo.
Es la misma de bt/load_data.py y esta comprobada en bt/check_tz.py.

  python3 bt/carga_mes.py <fichero.zip|fichero.csv> [destino.parquet]
"""
import io, os, sys, zipfile
import pandas as pd

DESTINO = "data/eurusd_m1_2026_08.parquet"

def lee(buf, nombre):
    d = pd.read_csv(buf, sep=";", header=None, usecols=[0, 1, 2, 3, 4],
                    names=["ts", "open", "high", "low", "close"])
    d["ts"] = pd.to_datetime(d["ts"], format="%Y%m%d %H%M%S", errors="coerce")
    n0 = len(d)
    d = d.dropna(subset=["ts"])
    if len(d) < n0:
        print(f"   {n0-len(d)} filas con fecha ilegible descartadas en {nombre}")
    return d

def main(origen, destino=DESTINO):
    if origen.lower().endswith(".zip"):
        with zipfile.ZipFile(origen) as z:
            csvs = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not csvs:
                sys.exit(f"{origen} no contiene ningun CSV")
            print(f"   {os.path.basename(origen)} -> {csvs[0]}")
            d = lee(io.BytesIO(z.read(csvs[0])), csvs[0])
    else:
        d = lee(origen, os.path.basename(origen))

    idx = pd.DatetimeIndex(d["ts"])
    d["ts"] = (idx.tz_localize("America/New_York", ambiguous="NaT",
                               nonexistent="NaT")
                  .tz_convert("UTC").tz_localize(None))
    perdidas = d["ts"].isna().sum()
    d = (d.dropna(subset=["ts"]).sort_values("ts")
          .drop_duplicates("ts", keep="last").reset_index(drop=True))
    if perdidas:
        print(f"   {perdidas} filas descartadas por el cambio de horario")

    mal = ((d.high < d.low) | (d.high < d.open) | (d.high < d.close)
           | (d.low > d.open) | (d.low > d.close)).sum()
    print(f"   {len(d):,} velas M1 | OHLC incoherente: {mal}")
    print(f"   rango UTC: {d.ts.min()} -> {d.ts.max()}")

    if os.path.exists(destino):
        v = pd.read_parquet(destino)
        antes = pd.to_datetime(v.ts).max()
        print(f"   el parquet actual llegaba a {antes}")
        if d.ts.max() <= antes:
            print("   AVISO: el fichero NO amplia la cobertura. HistData aun no")
            print("          ha cerrado el mes. No se reescribe nada.")
            return 1
        print(f"   gana {(d.ts.max()-antes).days} dias de cobertura")

    d.to_parquet(destino, index=False)
    print(f"   guardado -> {destino}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:3]))
