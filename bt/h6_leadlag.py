"""H6 · Adelanto-retraso EURUSD <-> GBPUSD.

Prueba puramente estadistica, declarada en el pre-registro. Si uno de los dos
pares adelanta al otro de forma explotable, aparece como correlacion cruzada
significativa a desfase distinto de cero.

Expectativa registrada de antemano: dara cero. Si existiera arbitraje entre los
dos pares mas liquidos del mundo, ya estaria explotado.
"""
import numpy as np, pandas as pd
from math import sqrt, erf

TR = ("2020-01-01","2023-12-31")
eur = pd.read_parquet("data/eurusd_m1.parquet"); eur["ts"]=pd.to_datetime(eur["ts"])
gbp = pd.read_parquet("data/gbpusd_m1.parquet"); gbp["ts"]=pd.to_datetime(gbp["ts"])
for d in (eur,gbp): d.query("@TR[0] <= ts <= @TR[1]", inplace=True)

j = pd.merge(eur[["ts","close"]].rename(columns={"close":"e"}),
             gbp[["ts","close"]].rename(columns={"close":"g"}), on="ts", how="inner")
print(f"minutos solapados en entrenamiento: {len(j):,}")
re_ = np.log(j.e).diff(); rg = np.log(j.g).diff()
d = pd.DataFrame({"e":re_,"g":rg}).dropna()
n = len(d)
ee = 1/sqrt(n)

print(f"\n=== CORRELACION CRUZADA (n = {n:,}, error estandar {ee:.5f}) ===")
print("   desfase>0: GBPUSD adelantado (EURUSD de hoy vs GBPUSD de hace k minutos)")
print(f"{'desfase':>9s} {'corr':>10s} {'z':>8s} {'lectura':>26s}")
sig = []
for k in list(range(-15,0)) + [0] + list(range(1,16)):
    if k == 0:
        c = float(d.e.corr(d.g))
    elif k > 0:
        c = float(d.e.corr(d.g.shift(k)))
    else:
        c = float(d.e.shift(-k).corr(d.g))
    z = c/ee
    if k == 0: lec = "contemporanea (esperada alta)"
    elif abs(z) < 3: lec = "ruido"
    else: lec = "SIGNIFICATIVA"; sig.append((k,c,z))
    if abs(k) <= 5 or k == 0 or abs(z) >= 3:
        print(f"{k:>+9d} {c:>+10.5f} {z:>+8.1f} {lec:>26s}")

print(f"\n   desfases significativos (|z|>3, sin contar el 0): {len(sig)}")
if sig:
    for k,c,z in sig:
        pips_por_pip = c   # correlacion ~ elasticidad para retornos pequenos
        print(f"     desfase {k:+d} min: corr {c:+.5f} -> por cada pip de movimiento")
        print(f"       en el par adelantado, {abs(c):.5f} pips predecibles en el otro")
        print(f"       ({abs(c)*10:.3f} pips por cada 10 de movimiento; coste 1,2 pips)")
else:
    print("     ninguno. No hay adelanto-retraso explotable.")

print("\n=== ¿CUANTO VALDRIA EL MEJOR DESFASE EN PIPS? ===")
mejor = max([(abs(d.e.corr(d.g.shift(k))), k) for k in range(1,16)])
c, k = mejor
mov = (j.g.diff().abs()/0.0001).mean()
print(f"   mejor desfase positivo: {k} min con |corr| {c:.5f}")
print(f"   movimiento medio de GBPUSD en 1 min: {mov:.2f} pips")
print(f"   movimiento predecible en EURUSD: {c*mov:.4f} pips")
print(f"   coste de operarlo: 1,2 pips  ->  {'RENTABLE' if c*mov>1.2 else 'NO LLEGA, por un factor de %.0f' % (1.2/(c*mov))}")
