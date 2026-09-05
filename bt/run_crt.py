import sys, pandas as pd
sys.path.insert(0, "bt")
from estrategia_crt import Config, marcos, senales, simular, metricas

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config()
ch = marcos(m1, cfg)
print(f"Grafico {cfg.chart}: {len(ch):,} velas | rango H4 ya cerrado\n")

sig, emb = senales(ch, cfg)
print("=== EMBUDO ===")
for k, v in emb.items():
    print(f"  {k:18s} {v:>10,}")

tr, amb = simular(sig, m1, cfg)
print(f"\nSenales {len(sig):,} -> operaciones {len(tr):,} "
      f"(velas M1 con SL y TP a la vez: {amb})")

met = metricas(tr)
print("\n=== RESULTADO BASE (M15, rango H4, KZ UTC, coste 1.2 pips) ===")
for k, v in met.items():
    if not k.startswith("_"):
        print(f"  {k:22s} {v}")

if not tr.empty:
    tr.to_csv("data/trades_crt_base.csv", index=False)
    print("\n--- distribucion del R:R planificado ---")
    for q in (.1,.25,.5,.75,.9):
        print(f"  p{int(q*100):>2} {tr.rr.quantile(q):6.2f}", end="")
    print(f"   max {tr.rr.max():.2f}")
    print("\n--- por ano ---")
    tr["ano"] = tr.ts.dt.year
    for a, g in tr.groupby("ano"):
        print(f"  {a}: {len(g):>4} ops | WR {100*(g.R>0).mean():5.1f}% "
              f"| R total {g.R.sum():+7.2f} | RR medio {g.rr.mean():5.2f}")
