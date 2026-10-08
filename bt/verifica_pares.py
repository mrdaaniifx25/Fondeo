"""Seccion 2 del pre-registro: verificacion previa a cualquier contraste."""
import numpy as np, pandas as pd
from math import sqrt

eur = pd.read_parquet("data/eurusd_m1.parquet"); eur["ts"]=pd.to_datetime(eur["ts"])
res = {"EURUSD": eur}
for p in ("gbpusd","usdjpy"):
    try:
        d = pd.read_parquet(f"data/{p}_m1.parquet"); d["ts"]=pd.to_datetime(d["ts"])
        res[p.upper()] = d
    except Exception: pass

print("=== 2.1 · VERIFICACION DEL HUSO (perfil de volatilidad por estacion) ===")
print("   Los picos deben DESPLAZARSE una hora entre invierno y verano.")
for nom, d in res.items():
    idx = pd.DatetimeIndex(d["ts"])
    ny = idx.tz_localize("UTC").tz_convert("America/New_York")
    dst = np.array([t.dst().total_seconds()!=0 for t in ny])
    r = (d["high"]-d["low"]).to_numpy()
    h = idx.hour
    inv = pd.Series(r[~dst]).groupby(h[~dst]).mean()
    ver = pd.Series(r[dst]).groupby(h[dst]).mean()
    pm_i, pm_v = inv.loc[5:11].idxmax(), ver.loc[5:11].idxmax()
    pt_i, pt_v = inv.loc[12:18].idxmax(), ver.loc[12:18].idxmax()
    ok = (pm_i-pm_v==1) and (pt_i-pt_v==1)
    print(f"   {nom:7s} manana inv {pm_i:02d}h / ver {pm_v:02d}h | "
          f"tarde inv {pt_i:02d}h / ver {pt_v:02d}h  -> {'OK' if ok else 'REVISAR'}")

print("\n=== 2.2 · CORRELACIONES DE RETORNOS DIARIOS ===")
print("   Esperado: EURUSD-GBPUSD ~ +0,85 | EURUSD-USDJPY ~ -0,5")
diarios = {}
for nom, d in res.items():
    s = d.set_index("ts").close.resample("1D").last().dropna()
    diarios[nom] = np.log(s).diff().dropna()
base = diarios["EURUSD"]
for nom, s in diarios.items():
    if nom=="EURUSD": continue
    j = pd.concat([base, s], axis=1, join="inner").dropna()
    c = float(j.corr().iloc[0,1])
    print(f"   EURUSD vs {nom}: {c:+.3f}  sobre {len(j):,} dias  "
          f"-> info independiente {100*(1-c*c):.0f}%")

print("\n=== 2.3 · SOLAPE UTIL POR PERIODO ===")
for nom, d in res.items():
    e = d.set_index("ts").close.resample("1D").last().dropna()
    tr = e[(e.index>='2020-01-01')&(e.index<='2023-12-31')]
    te = e[(e.index>='2024-01-01')&(e.index<='2026-07-31')]
    print(f"   {nom:7s} entrenamiento {len(tr):>4} dias | reserva {len(te):>4} dias")
