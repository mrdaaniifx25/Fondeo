"""¿La ventaja a R alto viene del ORDER BLOCK o es propia del barrido CRT?

Se aplica la MISMA escalera de objetivos a las tres variantes, sobre la misma
rejilla H4 y el mismo horario. Si la escalera solo aparece con order block,
el merito es suyo. Si aparece en las tres, es del barrido.
"""
import sys, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0, "bt")
from estrategia_ob import Config, preparar, senales, simular, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
ch = preparar(m1, Config())
def bruto(**kw):
    cfg = Config(**kw); sig,_ = senales(ch, cfg); tr,_ = simular(sig, m1, cfg)
    if tr.empty: return None
    tr["bruto"] = (tr.pips+cfg.coste_pips)/tr.riesgo_pips
    return tr
def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

variantes = [("sin OB, sin H1", dict(usar_ob=False, usar_h1=False)),
             ("sin OB, con H1", dict(usar_ob=False, usar_h1=True)),
             ("CON ORDER BLOCK", dict(usar_ob=True,  usar_h1=True))]
print(f"{'variante':18s} " + " ".join(f"{'TP '+str(r)+'R':>14s}" for r in (1,2,3,4)))
print("-"*76)
tabla = {}
for nom, kw in variantes:
    fila = []
    for r in (1.0, 2.0, 3.0, 4.0):
        tr = bruto(**kw, tp_modo="R", tp_r=float(r), min_rr=0.0, max_rr=99, max_trade_horas=168)
        z, p = pz(tr.bruto)
        fila.append((tr.bruto.mean(), p, len(tr)))
    tabla[nom] = fila
    print(f"{nom:18s} " + " ".join(f"{m:+7.4f} p{p:5.3f}" for m, p, _ in fila))
print("\n(n de operaciones)")
for nom, fila in tabla.items():
    print(f"{nom:18s} " + " ".join(f"{n:>14d}" for _, _, n in fila))

print("\n=== EL MISMO TEST SOBRE LA ESTRATEGIA 2 (CRT Trade Planner, rejilla 00 UTC) ===")
sys.path.insert(0, "bt")
from estrategia_crt import Config as C2, marcos, senales as sen2, simular as sim2
ch2 = marcos(m1, C2())
for r in (1.0, 2.0, 3.0, 4.0):
    c = C2(); c.max_trade_horas = 168
    sig, _ = sen2(ch2, c)
    if sig.empty: continue
    # sustituye el objetivo del rango por un multiplo R fijo
    sig = sig.copy()
    sig["tp"] = np.where(sig.largo, sig.entrada + r*(sig.entrada-sig.sl),
                                     sig.entrada - r*(sig.sl-sig.entrada))
    sig["rr"] = r
    tr, _ = sim2(sig, m1, c)
    b = (tr.pips + c.coste_pips)/tr.riesgo_pips
    z, p = pz(b)
    print(f"  TP {r:.0f}R | n {len(tr):>4} | WR {100*(tr.motivo=='TP').mean():5.2f}% "
          f"(equil {100/(1+r):5.2f}%) | bruto/op {b.mean():+.4f} | z {z:+5.2f} | p {p:.3f}")
