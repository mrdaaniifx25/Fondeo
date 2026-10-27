"""Carga GBPUSD y USDJPY con la MISMA conversion horaria validada para EURUSD:
reloj de Nueva York con horario de verano, no EST fijo."""
import glob, os, re, sys
import pandas as pd

def carga(par):
    fs = sorted(glob.glob(f"data/raw2/DAT_ASCII_{par}_M1_*.csv"))
    if not fs: return None
    fr = []
    for f in fs:
        df = pd.read_csv(f, sep=";", header=None,
                         names=["ts","open","high","low","close","vol"])
        df["ts"] = pd.to_datetime(df["ts"], format="%Y%m%d %H%M%S")
        fr.append(df.drop(columns=["vol"]))
    d = pd.concat(fr, ignore_index=True)
    idx = pd.DatetimeIndex(d["ts"])
    d["ts"] = idx.tz_localize("America/New_York", ambiguous="NaT",
                              nonexistent="NaT").tz_convert("UTC").tz_localize(None)
    d = d.dropna(subset=["ts"]).sort_values("ts").drop_duplicates("ts", keep="last")
    return d.reset_index(drop=True)

if __name__ == "__main__":
    for par in ("GBPUSD","USDJPY"):
        d = carga(par)
        if d is None: print(f"{par}: sin datos"); continue
        d.to_parquet(f"data/{par.lower()}_m1.parquet", index=False)
        bad = ((d.high<d.low)|(d.high<d.open)|(d.high<d.close)|
               (d.low>d.open)|(d.low>d.close)).sum()
        print(f"{par}: {len(d):,} velas | {d.ts.min()} -> {d.ts.max()} | OHLC malo: {bad}")
