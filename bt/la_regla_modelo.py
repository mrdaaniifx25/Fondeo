"""Ultima prueba limpia: el modelo, con 2026 reservado de verdad.

Entrena con <=2024, elige el umbral de stop minimo mirando SOLO 2025, y da el
numero de 2026 sin tocar nada. Es el unico tramo que queda sin usar.
"""
import numpy as np, pandas as pd
from math import sqrt
from sklearn.ensemble import HistGradientBoostingRegressor

D = pd.read_parquet("data/barrido_ml.parquet")
VARS = ["off","rgoP","costepc","prof","cuerpo","rango_vela","dist_niv","recorrido",
        "rango_ref","atr5","atr1h","londres","hora","dow","lado","r3","r6","r12",
        "previos","cerro_mas_alla"]
REJILLA = [0, 10, 20, 30]
D["Rb"] = 3 * D.gana - 1

M = HistGradientBoostingRegressor(max_iter=220, learning_rate=0.06, max_depth=5,
        min_samples_leaf=200, l2_regularization=1.0, random_state=0)
M.fit(D[D.anio <= 2024][VARS], D[D.anio <= 2024].Rn)

V = D[D.anio == 2025].copy(); V["p"] = M.predict(V[VARS])
T = D[D.anio == 2026].copy(); T["p"] = M.predict(T[VARS])
corte = V.p.quantile(0.9)                     # decil superior, fijado en 2025

print("eleccion del umbral, mirando SOLO 2025")
print(f"{'X':>5}{'n':>7}{'acierto':>9}{'bruta':>9}{'neta':>9}")
mejor, mejorR = None, -9
for X in REJILLA:
    S = V[(V.p >= corte) & (V.rgoP >= X)]
    if len(S) < 100: continue
    print(f"{X:>5}{len(S):>7}{100*S.gana.mean():>8.1f} %{S.Rb.mean():>+9.4f}{S.Rn.mean():>+9.4f}")
    if S.Rn.mean() > mejorR: mejor, mejorR = X, S.Rn.mean()
print(f"\n>> elegido X = {mejor} pips (neta en 2025: {mejorR:+.4f})\n")

S = T[(T.p >= corte) & (T.rgoP >= mejor)]
# una operacion por barrido: la primera vela que el modelo aprueba
S = S.sort_values("t").drop_duplicates(subset=["t"], keep="first")
print("=" * 92)
print(f"2026, RESERVADO DE VERDAD   ·   decil del modelo, stop >= {mejor} p")
print("=" * 92)
if len(S) < 30:
    print(f"  solo {len(S)} operaciones: muestra insuficiente")
else:
    meses = (pd.DatetimeIndex(S.t).max() - pd.DatetimeIndex(S.t).min()).days / 30.44
    print(f"  n {len(S)}   {len(S)/meses:.1f} al mes   acierto {100*S.gana.mean():.1f} %   "
          f"riesgo {S.rgoP.median():.1f} p   bruta {S.Rb.mean():+.4f}")
    for nom, c in (("su cuenta (1,43 p)", 1.43), ("spread crudo (0,90 p)", 0.90)):
        R = S.Rb - c / S.rgoP
        m, sd = R.mean(), R.std(ddof=1); ic = 1.96 * sd / sqrt(len(S))
        print(f"  {nom:<24} NETA {m:+.4f}  IC95 [{m-ic:+.4f}, {m+ic:+.4f}]  "
              f"z {m/(sd/sqrt(len(S))):+.2f}  cruza cero: {'SI' if m-ic>0 else 'no'}")
        print(f"  {'':24}   = {m*150:+.2f} EUR/op  x {len(S)/meses:.1f} al mes"
              f"  = {m*150*len(S)/meses:+.0f} EUR/mes")
