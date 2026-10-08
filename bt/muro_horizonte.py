"""El muro no es una constante: baja con el horizonte.

El coste es FIJO por operacion. El ruido crece con la raiz del tiempo. Asi que
la ventaja que hace falta para empatar, medida en ruido, se hace pequeña sola
segun alargas el horizonte. Esto sale de los mismos datos, no es una opinion.
"""
import numpy as np, pandas as pd

COSTES = {"EURUSD": (1.43e-4, "data/eurusd_m1.parquet", 1e-4, "pips"),
          "oro":    (0.35,    "data/xauusd_m1.parquet", 0.01, "unid."),
          "DAX":    (1.6,     "data/grxeur_m1.parquet", 1.0,  "puntos")}
H = [("1 hora",1), ("4 horas",4), ("1 dia",24), ("1 semana",120),
     ("1 mes",480), ("3 meses",1440), ("1 anio",5760)]   # horas DE MERCADO

print(f"{'':<9}{'horizonte':>11} {'ruido (sigma)':>16} {'coste/sigma':>13}  "
      f"{'ventaja necesaria para empatar':<32}")
print("-"*92)
for ins, (coste, ruta, U, un) in COSTES.items():
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    c = m1.close.to_numpy(); M = len(c)
    print(f"{ins}")
    for nom, hh in H:
        n = hh*60
        if M < n*3: print(f"{'':<9}{nom:>11}   (no hay histórico)"); continue
        paso = max(1, n//4)
        r = (c[n::paso] - c[:-n:paso]) / U
        sig = r.std(ddof=1)
        cs = (coste/U)/sig
        barra = "#" * max(1, int(round(cs*100)))
        print(f"{'':<9}{nom:>11} {sig:>12,.1f} {un:<4} {cs:>12.4f}  {barra[:32]}")
    print()
print("""  coste/sigma = que parte del ruido se lleva el coste de entrar UNA vez.
  Es la ventaja minima que necesitas para no perder dinero.
  La senal mas fuerte medida en el proyecto vale 0,060 de ruido.""")
