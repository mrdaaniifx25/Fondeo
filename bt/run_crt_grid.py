import sys, pandas as pd
sys.path.insert(0, "bt")
from estrategia_crt import Config, marcos, senales, simular, metricas

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cache = {}
def run(**kw):
    cfg = Config(**kw)
    key = (cfg.chart, cfg.htf_horas)
    if key not in cache:
        cache[key] = marcos(m1, cfg)
    sig, emb = senales(cache[key], cfg)
    tr, _ = simular(sig, m1, cfg)
    return metricas(tr), tr

variantes = [
    ("BASE M15 · KZ UTC · coste 1.2",  dict()),
    ("sin coste (spread = 0)",          dict(coste_pips=0.0)),
    ("coste 0.6 pips",                  dict(coste_pips=0.6)),
    ("sin filtro de kill zone",         dict(only_kz=False)),
    ("KZ en hora de Nueva York",        dict(kz_tz="America/New_York")),
    ("grafico M5",                      dict(chart="5min")),
    ("grafico M30",                     dict(chart="30min")),
    ("grafico H1",                      dict(chart="60min")),
    ("rango D1 (htf 24h), grafico H1",  dict(htf_horas=24, chart="60min")),
    ("R:R minimo 1.5",                  dict(min_rr=1.5)),
    ("R:R minimo 2.0",                  dict(min_rr=2.0)),
    ("colchon SL 0.25 ATR",             dict(sl_buffer_atr=0.25)),
    ("colchon SL 1.00 ATR",             dict(sl_buffer_atr=1.00)),
    ("rango minimo 0.8 ATR",            dict(min_range_atr=0.8)),
    ("sin tope diario",                 dict(daily_cap=0)),
    ("varias direcciones por rango",    dict(one_dir=False)),
]

print(f"{'variante':34s} {'ops':>5s} {'WR%':>7s} {'R tot':>8s} {'R/op':>8s} "
      f"{'PF':>7s} {'RR':>6s} {'riesgo':>7s} {'DD%':>7s}")
print("-"*96)
filas=[]
for nombre, kw in variantes:
    met, tr = run(**kw)
    if met["operaciones"] == 0:
        print(f"{nombre:34s} {'0':>5s}"); continue
    print(f"{nombre:34s} {met['operaciones']:>5d} {met['win rate %']:>7.2f} "
          f"{met['R total']:>8.2f} {met['R medio']:>8.4f} {met['profit factor']:>7.3f} "
          f"{met['R:R medio del plan']:>6.2f} {met['riesgo medio (pips)']:>7.2f} "
          f"{met['max drawdown %']:>7.2f}")
    filas.append(dict(variante=nombre, **{k:v for k,v in met.items() if not k.startswith('_')}))
pd.DataFrame(filas).to_csv("data/sensibilidad_crt.csv", index=False)
print("\n-> data/sensibilidad_crt.csv")
