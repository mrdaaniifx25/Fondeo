"""Mide la afirmacion fundacional en varios instrumentos y temporalidades."""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C

INS = [("EURUSD","data/eurusd_m1.parquet"), ("NAS100","data/nsxusd_m1.parquet"),
       ("GBPUSD","data/gbpusd_m1.parquet"), ("USDJPY","data/usdjpy_m1.parquet")]
TF  = [("H1",1), ("H4",4), ("D1",24)]

print("="*104)
print("¿SE SEPARAN LAS DOS CELDAS?  ·  retorno de la vela SIGUIENTE en unidades de ATR(20)")
print("  su afirmación:  cierra FUERA -> continúa   |   cierra DENTRO -> se da la vuelta")
print("  sin coste, sin entrada, sin stop: estadística condicionada pura")
print("="*104)

todo = []
for nom, ruta in INS:
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    print(f"\n{'─'*104}\n{nom}")
    for tfn, tfh in TF:
        ref = velas_ref(m1, tfh, ancla_ny=1)
        t = C.clasifica(ref)
        C.resumen(t, f"{nom} · {tfn}  ({len(ref):,} velas de referencia)")
        t = t.assign(ins=nom, tf=tfn); todo.append(t)

T = pd.concat(todo, ignore_index=True)
print("\n" + "="*104)
print("TODOS LOS INSTRUMENTOS JUNTOS")
print("="*104)
for tfn, _ in TF:
    C.resumen(T[T.tf == tfn], f"las cuatro piezas · {tfn}")
T.to_csv("data/cierres.csv", index=False)
