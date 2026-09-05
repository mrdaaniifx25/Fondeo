import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("EURUSD","data/eurusd_m1.parquet"), ("NAS100","data/nsxusd_m1.parquet"),
       ("GBPUSD","data/gbpusd_m1.parquet"), ("USDJPY","data/usdjpy_m1.parquet")]

print("="*112)
print("LIQUIDEZ SIMPLE, DOBLE Y TRIPLE  ·  «la doble y la triple aumentan la probabilidad»")
print("  (a) NATURAL   objetivo en el extremo opuesto, stop en el barrido -> el stop se aleja solo")
print("  (b) SIMÉTRICA ±1 ATR, MISMA distancia para k=1, 2 y 3 -> aquí el gradiente no puede ser geometría")
print("="*112)

todo = []
for cuerpo in (False, True):
    et = "cierre dentro del CUERPO de la vela base" if cuerpo else "cierre dentro del RANGO de la vela base"
    print(f"\n{'█'*112}\n{et.upper()}\n{'█'*112}")
    acum = []
    for nom, ruta in INS:
        m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").reset_index(drop=True)
        for tfn, tfh in (("H4",4), ("D1",24)):
            ref = velas_ref(m1, tfh, ancla_ny=1)
            h,l,c = (ref[x].to_numpy() for x in ("high","low","close"))
            a = C.atr(h,l,c,20)
            seq = LM.secuencias(ref, usar_cuerpo=cuerpo)
            if seq.empty: continue
            seq = LM.resuelve(seq, ref, m1, tfh, a)
            LM.tabla(seq, f"{nom} · {tfn}")
            acum.append(seq.assign(ins=nom, tf=tfn, cuerpo=cuerpo))
    if acum:
        A = pd.concat(acum, ignore_index=True)
        for tfn in ("H4","D1"):
            LM.tabla(A[A.tf==tfn], f"▶ LOS CUATRO INSTRUMENTOS JUNTOS · {tfn}")
        todo.append(A)
pd.concat(todo, ignore_index=True).to_csv("data/liquidez_multiple.csv", index=False)
