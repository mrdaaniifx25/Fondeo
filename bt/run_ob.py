import sys, pandas as pd
sys.path.insert(0, "bt")
from estrategia_ob import Config, preparar, senales, simular, metricas

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cache = {}
def run(**kw):
    cfg = Config(**kw)
    if cfg.ancla_h4 not in cache: cache[cfg.ancla_h4] = preparar(m1, cfg)
    sig, emb = senales(cache[cfg.ancla_h4], cfg)
    tr, _ = simular(sig, m1, cfg)
    return metricas(tr), emb, tr

print("=== EL EXPERIMENTO: ¿aporta algo el order block de M15? ===")
print("Mismas reglas, mismo horario, misma rejilla H4. Solo cambia el filtro.\n")
print(f"{'configuracion':40s} {'ops':>5s} {'WR%':>7s} {'R tot':>8s} {'R/op':>8s} {'PF':>7s} {'RR':>6s} {'riesgo':>7s}")
print("-"*94)
res = {}
for nombre, kw in [
    ("CRT solo (sin OB, sin H1)",      dict(usar_ob=False, usar_h1=False)),
    ("CRT + confirmacion H1",          dict(usar_ob=False, usar_h1=True)),
    ("CRT + H1 + ORDER BLOCK M15",     dict(usar_ob=True,  usar_h1=True)),
    ("CRT + ORDER BLOCK, sin H1",      dict(usar_ob=True,  usar_h1=False)),
]:
    met, emb, tr = run(**kw)
    res[nombre] = (met, emb, tr)
    if met["operaciones"] == 0: print(f"{nombre:40s} 0"); continue
    print(f"{nombre:40s} {met['operaciones']:>5d} {met['win rate %']:>7.2f} "
          f"{met['R total']:>8.2f} {met['R medio']:>8.4f} {met['profit factor']:>7.3f} "
          f"{met['R:R medio']:>6.2f} {met['riesgo medio']:>7.2f}")

print("\n=== EMBUDO de la version completa ===")
for k, v in res["CRT + H1 + ORDER BLOCK M15"][1].items():
    print(f"  {k:14s} {v:>10,}")

print("\n=== SIN COSTE (aisla la ventaja bruta) ===")
for nombre, kw in [("CRT solo", dict(usar_ob=False, usar_h1=False, coste_pips=0.0)),
                   ("CRT + H1 + OB M15", dict(usar_ob=True, usar_h1=True, coste_pips=0.0))]:
    met, _, _ = run(**kw)
    print(f"  {nombre:22s} ops {met['operaciones']:>5d} | R total {met['R total']:>8.2f} "
          f"| PF {met['profit factor']:.3f}")
