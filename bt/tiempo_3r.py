"""¿De donde sale el bruto positivo? ¿Del objetivo o de la salida por tiempo?"""
import sys, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0, "bt")
from estrategia_ob import Config, preparar, senales, simular, metricas, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
ch = preparar(m1, Config())
def corre(**kw):
    cfg = Config(**kw); sig,_ = senales(ch, cfg); tr,_ = simular(sig, m1, cfg)
    if not tr.empty: tr["bruto"] = (tr.pips+cfg.coste_pips)/tr.riesgo_pips
    return tr
def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

print("=== DESCOMPOSICION POR MOTIVO DE SALIDA (TP 3R, tope 48 h) ===")
tr = corre(tp_modo="R", tp_r=3.0, min_rr=0.0, max_rr=99)
g = tr.groupby("motivo").agg(ops=("bruto","size"), bruto_total=("bruto","sum"),
                             bruto_op=("bruto","mean"))
print(g.round(3).to_string())
print(f"\n  total bruto {tr.bruto.sum():+.2f}R de {len(tr)} operaciones")
pct = 100*g.loc["tiempo","bruto_total"]/tr.bruto.sum() if "tiempo" in g.index else 0
print(f"  las salidas por TIEMPO aportan {g.loc['tiempo','bruto_total']:+.2f}R "
      f"= {pct:.0f}% del total, con solo {int(g.loc['tiempo','ops'])} operaciones")

print("\n=== MISMO TEST CAMBIANDO EL TOPE TEMPORAL ===")
print(f"{'tope':>8s} {'ops':>5s} {'%tiempo':>8s} {'WR%':>7s} {'bruto/op':>10s} {'z':>6s} {'p':>7s} {'R neto':>8s}")
for h in (8, 12, 24, 48, 96, 168):
    t = corre(tp_modo="R", tp_r=3.0, min_rr=0.0, max_rr=99, max_trade_horas=h)
    z, p = pz(t.bruto)
    pt = 100*(t.motivo=="tiempo").mean()
    print(f"{h:>6d} h {len(t):>5d} {pt:>7.1f}% {100*(t.R>0).mean():>6.2f}% "
          f"{t.bruto.mean():>+10.4f} {z:>+6.2f} {p:>7.3f} {t.R.sum():>+8.2f}")

print("\n=== SOLO OPERACIONES RESUELTAS POR SL O TP (sin salidas por tiempo) ===")
print(f"{'TP':>5s} {'n':>5s} {'WR%':>7s} {'equil%':>7s} {'bruto/op':>10s} {'z':>6s} {'p':>7s}")
for r in (1.0, 2.0, 3.0, 4.0, 5.0):
    t = corre(tp_modo="R", tp_r=r, min_rr=0.0, max_rr=99, max_trade_horas=168)
    d = t[t.motivo.isin(["TP","SL"])]
    wr = (d.motivo=="TP").mean(); eq = 1/(1+r)
    z, p = pz(d.bruto)
    print(f"{r:>5.1f} {len(d):>5d} {100*wr:>6.2f}% {100*eq:>6.2f}% "
          f"{d.bruto.mean():>+10.4f} {z:>+6.2f} {p:>7.3f}")
