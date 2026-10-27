"""El motor supone que el stop se llena exactamente en su precio. ¿Cuanto miente?

En un stop de verdad la orden se dispara al tocar el nivel, pero si el precio
LLEGA POR UN SALTO -la vela de un minuto ya abre al otro lado- la ejecucion es
peor que el nivel. El motor no lo tiene en cuenta y por tanto es optimista.

Aqui se mide sobre las perdedoras reales: cuantas se llenaron por salto y cuanto
se pierde de mas cuando pasa.
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd

CELDA = "data/bc_Madrid_B.csv"
FUENTE = {"EURUSD": ("data/eurusd_m1.parquet", 0.0001),
          "GBPUSD": ("data/gbpusd_m1.parquet", 0.0001),
          "USDJPY": ("data/usdjpy_m1.parquet", 0.01),
          "NAS100": ("data/nsxusd_m1.parquet", 1.0),
          "SPX500": ("data/spxusd_m1.parquet", 1.0)}

d = pd.read_csv(CELDA); d["ts"] = pd.to_datetime(d.ts)
d = d[d.motivo == "SL"]
print("="*96)
print(f"DESLIZAMIENTO EN LAS PERDEDORAS   ·   {CELDA.split('/')[-1]}   n = {len(d):,}")
print("="*96)
print(f"{'instr':8s} {'perdedoras':>11s} {'por salto':>10s} {'%':>7s} "
      f"{'exceso medio (R)':>17s} {'peor':>8s}")

filas = []
for ins, g in d.groupby("ins"):
    ruta, u = FUENTE[ins]
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").reset_index(drop=True)
    t1 = m1.ts.to_numpy(); O = m1.open.to_numpy()
    H = m1.high.to_numpy(); L = m1.low.to_numpy()
    exceso, saltos = [], 0
    for r in g.itertuples():
        j0 = int(np.searchsorted(t1, np.datetime64(r.ts), side="right"))
        j1 = min(j0 + 3600, len(t1))
        if j0 >= len(t1): continue
        if r.lado > 0:
            hit = np.argmax(L[j0:j1] <= r.stop) if (L[j0:j1] <= r.stop).any() else None
        else:
            hit = np.argmax(H[j0:j1] >= r.stop) if (H[j0:j1] >= r.stop).any() else None
        if hit is None: continue
        j = j0 + int(hit)
        # ¿la vela ya ABRE al otro lado del stop? entonces se llena en la apertura
        peor = (O[j] < r.stop) if r.lado > 0 else (O[j] > r.stop)
        real = O[j] if peor else r.stop
        ex = (abs(real - r.stop) / abs(r.entrada - r.stop))    # en unidades de R
        exceso.append(ex)
        saltos += int(peor)
    if not exceso: continue
    e = np.array(exceso)
    print(f"{ins:8s} {len(e):>11,} {saltos:>10,} {100*saltos/len(e):>6.1f}% "
          f"{e.mean():>+17.4f} {e.max():>+8.3f}")
    filas.append((ins, len(e), saltos, e))

if filas:
    todo = np.concatenate([f[3] for f in filas])
    n = sum(f[1] for f in filas); s = sum(f[2] for f in filas)
    print("-"*96)
    print(f"{'TODOS':8s} {n:>11,} {s:>10,} {100*s/n:>6.1f}% {todo.mean():>+17.4f} {todo.max():>+8.3f}")
    print()
    print(f"Cada perdedora cuesta de media {todo.mean():.4f} R MAS de lo que dice el motor.")
    frac = len(pd.read_csv(CELDA))
    perd = n / frac
    print(f"Como el {100*perd:.0f} % de las operaciones son perdedoras, el sesgo sobre")
    print(f"la R media es de unos {todo.mean()*perd:+.4f} R por operación.")
