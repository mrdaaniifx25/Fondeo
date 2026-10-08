"""Abre los ficheros de reservado/ -2026 de oro y DAX, nunca tocados- en sus
propios parquet, sin mezclarlos con 2023-2025.  Misma conversion horaria que
bt/load_nuevos.py, ya validada en bt/check_tz.py.

  python3 bt/load_reservado.py
"""
import glob, io, os, sys, zipfile
import pandas as pd

DESTINO = {"XAUUSD": "data/xauusd_m1_2026.parquet",
           "GRXEUR": "data/grxeur_m1_2026.parquet"}

def lee_csv(buf):
    d = pd.read_csv(buf, sep=";", header=None, usecols=[0,1,2,3,4],
                    names=["ts","open","high","low","close"])
    d["ts"] = pd.to_datetime(d["ts"], format="%Y%m%d %H%M%S", errors="coerce")
    return d.dropna(subset=["ts"])

por_ins = {}
for f in sorted(glob.glob("reservado/*.zip")):
    base = os.path.basename(f).upper()
    ins = next((k for k in DESTINO if k in base), None)
    if ins is None: continue
    with zipfile.ZipFile(f) as z:
        for n in z.namelist():
            if n.lower().endswith(".csv"):
                por_ins.setdefault(ins, []).append(lee_csv(io.BytesIO(z.read(n))))

if not por_ins:
    sys.exit("no hay ZIP legibles en reservado/")

for ins, partes in por_ins.items():
    d = pd.concat(partes, ignore_index=True)
    idx = pd.DatetimeIndex(d["ts"])
    d["ts"] = idx.tz_localize("America/New_York", ambiguous="NaT",
                              nonexistent="NaT").tz_convert("UTC").tz_localize(None)
    d = (d.dropna(subset=["ts"]).sort_values("ts")
           .drop_duplicates("ts", keep="last").reset_index(drop=True))
    malo = ((d.high < d.low) | (d.high < d.open) | (d.high < d.close) |
            (d.low > d.open) | (d.low > d.close)).sum()
    nopos = (d[["open","high","low","close"]] <= 0).any(axis=1).sum()
    print(f"{ins}: {len(d):,} velas  {str(d.ts.min())[:16]} -> {str(d.ts.max())[:16]}  "
          f"OHLC imposible {malo}  precios<=0 {nopos}")
    if malo or nopos:
        print("   >> velas imposibles, no se escribe"); continue
    d.to_parquet(DESTINO[ins], index=False)
    print(f"   escrito {DESTINO[ins]}")
