"""Ingesta de los instrumentos ciegos, con la conversion horaria ya validada.

Lee lo que haya en material/ -ZIP o CSV de HistData- y escribe los parquet.
Misma conversion que bt/load_pares.py: hora de Nueva York CON horario de verano,
no EST fijo, comprobado empiricamente en bt/check_tz.py.

  python3 bt/load_nuevos.py
"""
import glob, io, os, re, sys, zipfile
import numpy as np, pandas as pd

DESTINO = {"XAUUSD": "data/xauusd_m1.parquet", "GRXEUR": "data/grxeur_m1.parquet"}

def lee_csv(buf, nombre):
    d = pd.read_csv(buf, sep=";", header=None, usecols=[0,1,2,3,4],
                    names=["ts","open","high","low","close"])
    d["ts"] = pd.to_datetime(d["ts"], format="%Y%m%d %H%M%S", errors="coerce")
    n0 = len(d); d = d.dropna(subset=["ts"])
    if len(d) < n0:
        print(f"      {n0-len(d)} filas con fecha ilegible descartadas en {nombre}")
    return d

def trozos():
    """Devuelve (instrumento, DataFrame) por cada fichero encontrado."""
    for f in sorted(glob.glob("material/**/*", recursive=True)):
        if os.path.isdir(f): continue
        base = os.path.basename(f).upper()
        ins = next((k for k in DESTINO if k in base), None)
        if ins is None: continue
        if f.lower().endswith(".zip"):
            with zipfile.ZipFile(f) as z:
                for n in z.namelist():
                    if n.lower().endswith(".csv"):
                        print(f"   {os.path.basename(f)} -> {n}")
                        yield ins, lee_csv(io.BytesIO(z.read(n)), n)
        elif f.lower().endswith(".csv"):
            print(f"   {os.path.basename(f)}")
            yield ins, lee_csv(f, base)

def hueco_semanal(d):
    """El mercado cierra el viernes y abre el domingo. Si la conversion es
    correcta, la hora UTC de la apertura se desplaza una hora entre invierno y
    verano. Si no se desplaza, los datos venian en EST fijo y hay que revisarlo."""
    dif = d.ts.diff()
    ap = d.loc[dif > pd.Timedelta(hours=12), "ts"]
    if len(ap) < 10: return None
    inv = ap.dt.month.isin([12,1,2,11])
    return ap[inv].dt.hour.mode(), ap[~inv].dt.hour.mode(), len(ap)

por_ins = {}
print("Buscando ficheros de HistData en material/ ...")
for ins, d in trozos():
    por_ins.setdefault(ins, []).append(d)

if not por_ins:
    print("\nNo hay nada que leer. Sube los ZIP a material/ y vuelve a ejecutar.")
    print("Se esperan ficheros cuyo nombre contenga XAUUSD o GRXEUR.")
    sys.exit(0)

print()
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
    print(f"{ins}")
    print(f"   {len(d):,} velas   {str(d.ts.min())[:16]} -> {str(d.ts.max())[:16]}")
    print(f"   años presentes: {sorted(d.ts.dt.year.unique().tolist())}")
    print(f"   OHLC imposible: {malo}   precios <= 0: {nopos}   duplicados: 0")
    h = hueco_semanal(d)
    if h is None:
        print("   hueco semanal: no hay suficientes semanas para comprobarlo")
    else:
        inv, ver, n = h
        i = inv.iloc[0] if len(inv) else -1; v = ver.iloc[0] if len(ver) else -1
        ok = (i != v)
        print(f"   apertura semanal UTC: invierno {i:02d}h · verano {v:02d}h "
              f"({n} semanas)   {'OK, se desplaza con el horario de verano' if ok else 'NO SE DESPLAZA -> revisar el huso'}")
    if malo or nopos:
        print("   >> hay velas imposibles: NO se escribe el parquet"); continue
    d.to_parquet(DESTINO[ins], index=False)
    print(f"   escrito {DESTINO[ins]}\n")
