"""Que se puede predecir del EURUSD y que no, sobre los datos del proyecto.

Dos preguntas separadas, que la gente confunde siempre:
  A) se puede predecir CUANTO se va a mover?      (volatilidad)
  B) se puede predecir HACIA DONDE?               (direccion)

  python3 bt/hay_patron.py
"""
import numpy as np, pandas as pd

U = 1e-4
m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
c = m1.close.to_numpy()
r = np.diff(np.log(c))                       # rendimiento por minuto
r = r[np.isfinite(r)]
print(f"{len(r):,} minutos de EURUSD  ·  {m1.ts.min().date()} a {m1.ts.max().date()}\n")

def ac(x, k):
    a, b = x[:-k], x[k:]
    return float(np.corrcoef(a, b)[0,1])

print("="*64)
print("A · SE PUEDE PREDECIR CUANTO SE MUEVE?   (autocorrelacion de |r|)")
print("="*64)
print(f"{'desfase':>10s} {'corr':>9s}")
for k in (1, 5, 15, 30, 60, 240, 1440):
    print(f"{k:8d} m {ac(np.abs(r), k):9.4f}")

print("\n" + "="*64)
print("B · SE PUEDE PREDECIR HACIA DONDE?   (autocorrelacion del signo)")
print("="*64)
print(f"{'desfase':>10s} {'corr':>9s}")
for k in (1, 5, 15, 30, 60, 240, 1440):
    print(f"{k:8d} m {ac(r, k):9.4f}")

# ---- R2 de una regresion honesta: 30 min pasados -> 30 min futuros
n = (len(r)//30)*30
b = r[:n].reshape(-1, 30)
vol  = np.abs(b).sum(axis=1)          # recorrido de cada bloque de 30 min
dire = b.sum(axis=1)                  # movimiento neto de cada bloque
def r2(x, y):
    x, y = x[:-1], y[1:]
    return float(np.corrcoef(x, y)[0,1])**2

print("\n" + "="*64)
print("CUANTO EXPLICA EL PASADO DEL FUTURO   (bloques de 30 minutos)")
print("="*64)
print(f"  recorrido de 30 min  ->  recorrido de los 30 siguientes   R2 = {r2(vol,vol):.4f}")
print(f"  recorrido de 30 min  ->  DIRECCION de los 30 siguientes   R2 = {r2(vol,dire):.4f}")
print(f"  direccion de 30 min  ->  DIRECCION de los 30 siguientes   R2 = {r2(dire,dire):.4f}")

# ---- cuanto vale la direccion en pips, si es que vale algo
s = np.sign(dire[:-1]); f = dire[1:]
seg = np.array([f[s>0].mean(), f[s<0].mean()])/U*1e4
print(f"\n  seguir la direccion de los 30 min previos, siguientes 30 min:")
print(f"    tras subida  {f[s>0].mean()/U:+.3f} pips   ·   tras bajada {f[s<0].mean()/U:+.3f} pips")
print(f"    ventaja direccional bruta: {abs(f[s>0].mean()-f[s<0].mean())/U/2:.3f} pips  "
      f"·  coste de ida y vuelta: 1,430 pips")
