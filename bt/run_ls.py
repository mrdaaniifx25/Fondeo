import sys, pandas as pd
sys.path.insert(0, "bt")
from estrategia_ls import Config, construir_senales, simular, metricas

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
print(f"M1: {len(m1):,} velas | {m1.ts.min()} -> {m1.ts.max()}\n")

cfg = Config()
m5, emb = construir_senales(m1, cfg)
print("=== EMBUDO DE CONFIRMACIONES ===")
for k, v in emb.items():
    print(f"  {k:26s} {v:>10,}")

tr, amb = simular(m5, m1, cfg)
print(f"\nOperaciones tras 'una a la vez': {len(tr):,}   "
      f"(velas M1 con SL y TP simultaneos: {amb})")

met = metricas(tr)
print("\n=== RESULTADO (config base: KZ activa, TP 1R, coste 1.2 pips) ===")
for k, v in met.items():
    if not k.startswith("_"):
        print(f"  {k:26s} {v}")

if not tr.empty:
    tr.to_csv("data/trades_ls_base.csv", index=False)
    print("\n--- por ano ---")
    tr["ano"] = tr.ts.dt.year
    for a, g in tr.groupby("ano"):
        wr = 100 * (g.R > 0).mean()
        print(f"  {a}:  {len(g):>4} ops | WR {wr:5.1f}% | R total {g.R.sum():+7.2f} "
              f"| riesgo medio {g.riesgo_pips.mean():5.1f} pips")
