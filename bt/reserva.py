"""EL DISPARO. Se abre la reserva 2024-2026 por primera y unica vez."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,"bt")
from laboratorio import Motor, resumen, TRAIN, TEST
import candidatas as K

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
te = m1[(m1.ts>=TEST[0])&(m1.ts<=TEST[1])].reset_index(drop=True)
mo = Motor(te)
print(f"RESERVA {TEST[0]} .. {TEST[1]}  ({len(te):,} velas M1)\n")

print("=== PRUEBA PREDECLARADA (una sola) ===")
sig = K.asia(te, False, 3.0, "opuesto")
r = resumen(mo.resolver(sig), "A · ruptura Asia rr3.0 slopuesto")
if r:
    print(f"  {r['etiqueta']}")
    print(f"    n {r['n']} | WR {r['wr']:.1f}% | bruto/op {r['bruto']:+.4f} | p {r['p']:.3f}")
    print(f"    R neto {r['Rneto']:+.2f} | profit factor {r['pf']:.3f} | maxDD {r['dd']:.1f}%")
    print(f"    equity al 1%: {r['eq']:,.0f} EUR desde 10.000")
    print(f"    entrenamiento decia: bruto +0.0826, p 0.234, PF 1.050")

print("\n=== CONTEXTO (no predeclarado): las otras del podio ===")
for nom, fn in [("B · fade Asia rr3.0 sl0.25", lambda m: K.asia_fade(m,3.0,0.25)),
                ("A · ruptura Asia rr2.0 slopuesto", lambda m: K.asia(m,False,2.0,"opuesto")),
                ("E · deriva h7 corto", lambda m: K.deriva(m,7,6,False)),
                ("F · fade extension rr3.0 k0.8", lambda m: K.ext_fade(m,0.8,3.0))]:
    s = fn(te)
    if s.empty: continue
    rr = resumen(mo.resolver(s), nom)
    if rr: print(f"  {nom:36s} n {rr['n']:>4} | bruto/op {rr['bruto']:+.4f} | p {rr['p']:.3f} "
                 f"| R neto {rr['Rneto']:+7.2f} | PF {rr['pf']:.3f}")

print("\n=== CUANTO SOBRESALE LA MEJOR DE 46 SI NO HUBIERA NADA ===")
import pandas as _pd
df = _pd.read_csv("data/train_candidatas.csv")
pmin = df.p.min()
n = len(df)
print(f"  candidatas: {n} | p minima observada en entrenamiento: {pmin:.3f}")
print(f"  con {n} monedas independientes, la p minima esperada seria ~{1/(n+1):.3f}")
print(f"  observada {pmin:.3f} -> las candidatas no destacan ni lo que destacaria el ruido")
