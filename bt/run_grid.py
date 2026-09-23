import sys, pandas as pd
sys.path.insert(0, "bt")
from estrategia_ls import Config, construir_senales, simular, metricas

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])

variantes = [
    ("BASE (KZ, H4, 1R, coste 1.2)",      dict()),
    ("sin coste (spread = 0)",             dict(coste_pips=0.0)),
    ("coste 0.6 pips",                     dict(coste_pips=0.6)),
    ("sin filtro horario",                 dict(solo_kz=False)),
    ("sin confirmacion H4",                dict(exigir_h4=False)),
    ("solo niveles de DIA",                dict(usar_sesion=False)),
    ("solo niveles de SESION",             dict(usar_dia=False)),
    ("envolvente con cuerpo >=50%",        dict(min_body_ratio=0.5)),
    ("envolvente con cuerpo >=70%",        dict(min_body_ratio=0.7)),
    ("TP 2R",                              dict(rr=2.0)),
    ("TP 3R",                              dict(rr=3.0)),
    ("TP 0.5R",                            dict(rr=0.5)),
    ("SL buffer 3 pips",                   dict(sl_buffer_pips=3.0)),
    ("H4 anclado a las 17:00 NY",          dict(h4_anchor_hour=21)),
]

print(f"{'variante':32s} {'ops':>6s} {'WR%':>7s} {'R tot':>9s} "
      f"{'R/op':>8s} {'PF':>7s} {'riesgo':>8s} {'maxDD%':>8s}")
print("-" * 92)
filas = []
for nombre, kw in variantes:
    cfg = Config(**kw)
    m5, emb = construir_senales(m1, cfg)
    tr, _ = simular(m5, m1, cfg)
    met = metricas(tr)
    if met["operaciones"] == 0:
        print(f"{nombre:32s} {'0':>6s}")
        continue
    print(f"{nombre:32s} {met['operaciones']:>6d} {met['win rate %']:>7.2f} "
          f"{met['R total']:>9.2f} {met['R medio']:>8.4f} "
          f"{met['profit factor']:>7.3f} {met['riesgo medio (pips)']:>8.2f} "
          f"{met['max drawdown %']:>8.2f}")
    filas.append(dict(variante=nombre, **{k: v for k, v in met.items() if not k.startswith('_')}))

pd.DataFrame(filas).to_csv("data/sensibilidad_ls.csv", index=False)
print("\n-> data/sensibilidad_ls.csv")
