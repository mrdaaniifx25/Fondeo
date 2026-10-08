"""El motor, contra datos donde SE SABE que no hay nada que encontrar.

Un paseo aleatorio sin deriva es una martingala. Con un stop y un objetivo
fijos, el teorema del muestreo opcional dice que la esperanza en unidades de R
es CERO, valga lo que valga el R:R: si el premio es rr veces el riesgo, la
probabilidad de tocar antes el objetivo es 1/(1+rr), y rr/(1+rr) - rr/(1+rr) = 0.

Asi que si el motor mide una ventaja bruta distinta de cero sobre ruido, la
ventaja la esta fabricando el motor. Es la prueba que decide si el aparato de
medida vale para algo, y no depende de ninguna teoria sobre el mercado.

  python3 bc/prueba_ruido.py [replicas]
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd
import nucleo as N, motor as M

MIN = 1_500_000          # ~4 anos de minutos de mercado
SIGMA = 0.00013          # por minuto; da un rango diario del orden del 0,5 %
UNIDAD = 0.0001

def serie(semilla):
    rng = np.random.default_rng(semilla)
    p = 1.10 * np.exp(np.cumsum(rng.normal(0.0, SIGMA, MIN)))
    ts = pd.date_range("2016-01-04", periods=MIN, freq="min")
    # cada minuto necesita alto y bajo; se simulan con un puente sencillo
    ruido = np.abs(rng.normal(0.0, SIGMA * 0.6, MIN)) * p
    return pd.DataFrame({"ts": ts, "open": p, "close": p,
                         "high": p + ruido, "low": p - ruido})

reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
print("="*96)
print("EL MOTOR CONTRA RUIDO PURO   ·   la esperanza bruta verdadera es CERO")
print(f"{MIN:,} minutos por replica · {reps} replicas · sin coste, para no")
print("confundir 'el metodo no gana' con 'el metodo pierde por comisiones'")
print("="*96)
print(f"{'replica':9s} {'n':>7s} {'%TP':>7s} {'R:R med':>9s} "
      f"{'R bruta':>9s} {'IC95':>20s} {'z':>7s}")
print("-"*96)

tot = []
for k in range(reps):
    m1 = serie(20260827 + k)
    t = M.opera(m1, "UTC", "B", colchon=1.0, unidad=UNIDAD, coste=0.0,
                riesgo_min_x_coste=0.0, rr_min=3.0)
    if not len(t):
        print(f"{k:<9d} sin operaciones"); continue
    x = t.R.to_numpy()
    ee = x.std(ddof=1)/np.sqrt(len(x)); z = x.mean()/ee
    print(f"{k:<9d} {len(t):>7,} {100*(t.motivo=='TP').mean():>6.1f}% "
          f"{t.rr.median():>9.2f} {x.mean():>+9.3f} "
          f"[{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}] {z:>+7.2f}")
    tot.append(t)

if tot:
    T = pd.concat(tot, ignore_index=True)
    x = T.R.to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x)); z = x.mean()/ee
    print("-"*96)
    print(f"{'JUNTAS':9s} {len(T):>7,} {100*(T.motivo=='TP').mean():>6.1f}% "
          f"{T.rr.median():>9.2f} {x.mean():>+9.3f} "
          f"[{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}] {z:>+7.2f}")
    print()
    print("  salidas: " + "  ".join(f"{m} {100*(T.motivo==m).mean():.1f}%"
                                    for m in T.motivo.unique()))
    # la prediccion exacta de la teoria para el %TP observado
    rr = T.rr.median()
    print(f"  con R:R mediano {rr:.2f}, la teoria espera {100/(1+rr):.1f}% de aciertos")
    print()
    if abs(z) < 2:
        print("  VEREDICTO: el motor NO fabrica ventaja sobre ruido.")
    else:
        print(f"  VEREDICTO: el motor mide {x.mean():+.3f} R donde no hay nada. HAY UN FALLO.")
