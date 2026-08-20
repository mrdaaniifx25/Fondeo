import sys, numpy as np, pandas as pd
sys.path.insert(0, "bt")
from estrategia_ls import Config, construir_senales, simular, metricas

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config()
m5, emb = construir_senales(m1, cfg)
tr, _ = simular(m5, m1, cfg)
met = metricas(tr)

tr["ano"] = tr.ts.dt.year
tsu = pd.DatetimeIndex(tr.ts).tz_localize("UTC")
hl = tsu.tz_convert("Europe/London").hour
tr["plaza"] = np.where((hl >= cfg.kz_londres[0]) & (hl < cfg.kz_londres[1]), "Londres", "NY")

print("=== POR PLAZA ===")
for p, g in tr.groupby("plaza"):
    print(f"  {p:8s} {len(g):>5} ops | WR {100*(g.R>0).mean():5.2f}% | R total {g.R.sum():+8.2f}")

print("\n=== DISTRIBUCION DEL RIESGO (pips) ===")
print(f"  p10 {tr.riesgo_pips.quantile(.10):5.1f} | mediana {tr.riesgo_pips.median():5.1f} "
      f"| p90 {tr.riesgo_pips.quantile(.90):5.1f} | max {tr.riesgo_pips.max():5.1f}")
print(f"  coste 1.2 pips = {100*1.2/tr.riesgo_pips.median():.1f}% del riesgo mediano")

print("\n=== LA SEMANA DEL VIDEO: 7 ACIERTOS DE 8 ===")
from math import comb
p = (comb(8,7)+comb(8,8))/2**8
print(f"  Probabilidad de >=7/8 con una moneda: {100*p:.2f}%")
print(f"  Semanas esperadas asi al ano lanzando monedas: {52*p:.1f}")

eq = met["_curva"]
pd.DataFrame({"ts": tr.ts, "R": tr.R, "equity": eq, "ano": tr.ano,
              "plaza": tr.plaza, "riesgo_pips": tr.riesgo_pips,
              "motivo": tr.motivo, "dir": tr["dir"]}).to_csv("data/curva_ls.csv", index=False)
print(f"\nequity final {eq[-1]:.2f} desde 10000 | maxDD {met['max drawdown %']}%")
print("-> data/curva_ls.csv")
