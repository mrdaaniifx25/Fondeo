"""Carga NSXUSD y SPXUSD con la misma conversion horaria validada."""
import glob, pandas as pd
def carga(sym):
    fs = sorted(glob.glob(f"data/raw3/DAT_ASCII_{sym}_M1_*.csv"))
    if not fs: return None
    fr=[]
    for f in fs:
        df = pd.read_csv(f, sep=";", header=None,
                         names=["ts","open","high","low","close","vol"])
        df["ts"] = pd.to_datetime(df["ts"], format="%Y%m%d %H%M%S")
        fr.append(df.drop(columns=["vol"]))
    d = pd.concat(fr, ignore_index=True)
    idx = pd.DatetimeIndex(d["ts"])
    d["ts"] = idx.tz_localize("America/New_York", ambiguous="NaT",
                              nonexistent="NaT").tz_convert("UTC").tz_localize(None)
    return d.dropna(subset=["ts"]).sort_values("ts").drop_duplicates("ts",keep="last").reset_index(drop=True)

if __name__=="__main__":
    import numpy as np
    for s in ("NSXUSD","SPXUSD"):
        d = carga(s)
        if d is None: continue
        d.to_parquet(f"data/{s.lower()}_m1.parquet", index=False)
        bad=((d.high<d.low)|(d.high<d.open)|(d.high<d.close)|(d.low>d.open)|(d.low>d.close)).sum()
        print(f"{s}: {len(d):,} velas | {d.ts.min()} -> {d.ts.max()} | OHLC malo {bad}")
        # huecos: diferencia entre velas consecutivas
        dif = d.ts.diff().dt.total_seconds()/60
        print(f"   huecos >5 min: {int((dif>5).sum()):,} | >60 min: {int((dif>60).sum()):,} "
              f"| mediana del hueco largo: {dif[dif>60].median():.0f} min")
        # perfil por hora UTC
        idx = pd.DatetimeIndex(d["ts"])
        ny = idx.tz_localize("UTC").tz_convert("America/New_York")
        dst = np.array([t.dst().total_seconds()!=0 for t in ny])
        r = (d["high"]-d["low"]).to_numpy(); h = idx.hour
        inv = pd.Series(r[~dst]).groupby(h[~dst]).mean()
        ver = pd.Series(r[dst]).groupby(h[dst]).mean()
        print(f"   pico invierno {inv.idxmax():02d}h UTC | pico verano {ver.idxmax():02d}h UTC "
              f"-> {'OK (apertura EEUU se desplaza 1h)' if inv.idxmax()-ver.idxmax()==1 else 'REVISAR'}")
        print(f"   rango medio de la vela M1: {r.mean():.2f} puntos | precio medio {d.close.mean():.0f}")
