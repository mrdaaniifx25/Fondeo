import sys, pandas as pd
sys.path.insert(0, "bt")
from estrategia_ob import Config, preparar, senales, simular, metricas

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cache = {}
def run(**kw):
    cfg = Config(**kw)
    if cfg.ancla_h4 not in cache: cache[cfg.ancla_h4] = preparar(m1, cfg)
    sig,_ = senales(cache[cfg.ancla_h4], cfg); tr,_ = simular(sig, m1, cfg)
    m = metricas(tr)
    if not tr.empty:
        m["R bruto"] = round(float(((tr.pips+cfg.coste_pips)/tr.riesgo_pips).sum()), 2)
    return m

vs = [
 ("BASE (ancla 01 UTC, TP rango, 06:30-16)", dict()),
 ("TP fijo 2R",                    dict(tp_modo="R", tp_r=2.0)),
 ("TP fijo 3R",                    dict(tp_modo="R", tp_r=3.0)),
 ("rejilla H4 estandar (00 UTC)",  dict(ancla_h4=0)),
 ("sin filtro horario",            dict(hora_ini=0, hora_fin=24)),
 ("solo Londres (06:30-11)",       dict(hora_ini=6.5, hora_fin=11)),
 ("solo Nueva York (12-16)",       dict(hora_ini=12, hora_fin=16)),
 ("OB medido contra la apertura",  dict(ob_ref="open")),
 ("margen OB 4 velas",             dict(max_espera=4)),
 ("margen OB 32 velas",            dict(max_espera=32)),
 ("rango minimo 0.5 ATR",          dict(min_range_atr=0.5)),
 ("R:R minimo 2",                  dict(min_rr=2.0)),
 ("colchon SL 3 pips",             dict(sl_buffer_pips=3.0)),
 ("varias por rango",              dict(una_por_rango=False)),
]
print(f"{'variante':42s} {'ops':>5s} {'WR%':>7s} {'R neto':>8s} {'R bruto':>8s} {'PF':>7s} {'riesgo':>7s}")
print("-"*90)
filas=[]
for n, kw in vs:
    m = run(**kw)
    if m["operaciones"]==0: print(f"{n:42s} 0"); continue
    print(f"{n:42s} {m['operaciones']:>5d} {m['win rate %']:>7.2f} {m['R total']:>8.2f} "
          f"{m.get('R bruto',0):>8.2f} {m['profit factor']:>7.3f} {m['riesgo medio']:>7.2f}")
    filas.append(dict(variante=n, **m))
pd.DataFrame(filas).to_csv("data/sensibilidad_ob.csv", index=False)
