"""La deriva de la finta, medida en unidades de su propio ruido (sigma de la
hora), para poder comparar instrumentos y compararla contra el coste.

La pregunta ya no es 'cuantos pips'. Es: el coste, en sigmas, es mayor o menor
que la senal, en sigmas. Eso decide si hay negocio en ALGUN instrumento.
"""
import numpy as np, pandas as pd
exec(open("bt/deriva.py").read().split("for ins, (ruta, U, coste) in INS.items():")[0])

# costes realistas de minorista, en unidades del instrumento.
# EURUSD: 0,85 de horquilla + 5 EUR/lote (~0,58 pips) = 1,43 pips
# oro:    ~25 centavos de horquilla + comision ~ 0,35 unidades
# DAX:    ~1,2 puntos de horquilla + comision ~ 1,6 puntos
COSTES = {"EURUSD": 1.43e-4, "oro": 0.35, "DAX": 1.6}
HH = [1]

print(f"{'instrumento':<10} {'n':>6} {'sigma 1h':>10} {'deriva':>9} {'IC95':>20} "
      f"{'deriva/sigma':>13} {'coste/sigma':>12} {'detectable':>11}")
print("-"*100)
for ins, (ruta, U, _) in INS.items():
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    mts = m1.ts.to_numpy("datetime64[ns]"); mc = m1.close.to_numpy()
    ev = sucesos(velas(m1, 60), 8)["finta"]
    R, mes = mide(ev, mts, mc, U)
    if R is None: continue
    r = R[:, 0]                              # h = 1 hora, en unidades/U
    sig = r.std(ddof=1)                      # ruido de una hora, en las mismas
    med, lo, hi = bloques(R[:, :1], mes)
    cs = COSTES[ins] / U                     # coste en las mismas unidades
    # menor efecto que esta muestra podria distinguir del cero (semiancho del IC)
    mde = (hi[0] - lo[0]) / 2
    print(f"{ins:<10} {len(r):>6,} {sig:>10.1f} {med[0]:>+9.2f} "
          f"[{lo[0]:>+7.2f},{hi[0]:>+7.2f}] {med[0]/sig:>+13.4f} {cs/sig:>12.4f} "
          f"{mde/sig:>11.4f}")

print("""
  deriva/sigma  = lo que gana la senal, en ruido de una hora
  coste/sigma   = lo que cuesta entrar, en ruido de una hora
  detectable    = el efecto mas pequenio que esta muestra distingue del cero

  Si 'detectable' es mayor que la deriva/sigma de EURUSD, ese instrumento NO
  dice que no haya efecto: dice que no tiene potencia para verlo.""")
