import sys, itertools, numpy as np, pandas as pd
sys.path.insert(0,"bt")
from laboratorio import Motor, resumen, TRAIN, TEST
import candidatas as K

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
tr_m1 = m1[(m1.ts>=TRAIN[0]) & (m1.ts<=TRAIN[1])].reset_index(drop=True)
motor_tr = Motor(tr_m1)

print(f"ENTRENAMIENTO {TRAIN[0]} .. {TRAIN[1]}  ({len(tr_m1):,} velas M1)")
print("La reserva no se toca todavia.\n")

pruebas = []
for rr in (1.0, 2.0, 3.0):
    for sl in ("mid","opuesto"):
        pruebas.append((f"A · ruptura Asia rr{rr} sl{sl}", lambda mm,rr=rr,sl=sl: K.asia(mm, False, rr, sl)))
        pruebas.append((f"B · fade Asia rr{rr} sl{sl}",    lambda mm,rr=rr,sl=sl: K.asia(mm, True, rr, sl)))
for rr in (1.0, 2.0, 3.0):
    for buf in (1.0, 3.0):
        pruebas.append((f"C · barrido PDH/PDL rr{rr} buf{buf}", lambda mm,rr=rr,b=buf: K.pdhl(mm, rr, b)))
for rr in (1.0, 2.0, 3.0):
    for mins in (30, 60):
        pruebas.append((f"D · ORB Londres rr{rr} {mins}min", lambda mm,rr=rr,m=mins: K.orb(mm, rr, m)))

print(f"{'candidata':38s} {'n':>5s} {'WR':>6s} {'bruto/op':>9s} {'p':>7s} "
      f"{'1a mit':>7s} {'2a mit':>7s} {'R neto':>8s} {'PF':>6s}")
print("-"*104)
res = []
for nom, fn in pruebas:
    sig = fn(tr_m1)
    if sig.empty: print(f"{nom:38s} sin senales"); continue
    tr = motor_tr.resolver(sig)
    r = resumen(tr, nom)
    if r is None: print(f"{nom:38s} pocas ops"); continue
    res.append(r)
    print(f"{nom:38s} {r['n']:>5d} {r['wr']:>5.1f}% {r['bruto']:>+9.4f} {r['p']:>7.3f} "
          f"{r['h1']:>+7.3f} {r['h2']:>+7.3f} {r['Rneto']:>+8.2f} {r['pf']:>6.3f}")

print(f"\nTOTAL CANDIDATAS PROBADAS EN ENTRENAMIENTO: {len(res)}")
df = pd.DataFrame(res)
df.to_csv("data/train_candidatas.csv", index=False)
elegibles = df[(df.n>=150) & (df.h1>0) & (df.h2>0)].sort_values("bruto", ascending=False)
print(f"\n=== REGLA DECLARADA: n>=150 y las dos mitades positivas en bruto ===")
if elegibles.empty:
    print("  NINGUNA candidata cumple la regla.")
else:
    print(elegibles[["etiqueta","n","wr","bruto","p","h1","h2","Rneto","pf"]].to_string(index=False))
    print(f"\n  GANADORA: {elegibles.iloc[0].etiqueta}")
