"""La regla, fijada en 2020-2023 y soltada en 2024-2026.
Pre-registro docs/PREREGISTRO_la_regla.md
"""
import numpy as np, pandas as pd
from math import sqrt

U, RR = 1e-4, 2.0
REJILLA = [10, 15, 20, 25, 30, 40]
COSTES = {"su cuenta de hoy (1,43 p)": 1.43, "spread crudo (0,90 p)": 0.90}

D = pd.read_csv("data/barrido_sesion_v2.csv")
D = D[D.conf == "C2"].copy()
D["t"] = pd.to_datetime(D.t)
D["anio"] = D.t.dt.year
D["Rb"] = np.where(D.gano == 1, RR, -1.0)
print(f"senales totales: {len(D):,}  ({D.anio.min()}-{D.anio.max()})\n")

DENTRO = D[D.anio <= 2023]
FUERA  = D[D.anio >= 2024]

def neta(S, c): return S.Rb - c / S.rgoP

# ── ELECCION, mirando SOLO 2020-2023 ─────────────────────────────────────
print("eleccion del filtro, mirando SOLO 2020-2023")
print(f"{'X':>5}{'n':>7}{'ops/mes':>9}{'acierto':>9}{'riesgo':>9}{'R neta':>10}")
mejor, mejorR = None, -9
for X in REJILLA:
    S = DENTRO[DENTRO.rgoP >= X]
    if len(S) < 50: continue
    r = neta(S, 1.43).mean()
    meses = (S.t.max() - S.t.min()).days / 30.44
    print(f"{X:>5}{len(S):>7}{len(S)/max(meses,1):>9.1f}{100*S.gano.mean():>8.1f} %"
          f"{S.rgoP.median():>8.1f} p{r:>+10.4f}")
    if r > mejorR: mejor, mejorR = X, r
print(f"\n>> elegido X = {mejor} pips, con R neta dentro de muestra {mejorR:+.4f}")
print("   (a partir de aqui no se vuelve a tocar nada)\n")

# ── EL NUMERO, 2024-2026 ─────────────────────────────────────────────────
S = FUERA[FUERA.rgoP >= mejor]
meses = (S.t.max() - S.t.min()).days / 30.44
print("=" * 96)
print(f"FUERA DE MUESTRA 2024-2026   ·   X = {mejor} pips")
print("=" * 96)
print(f"  n {len(S)}   {len(S)/meses:.1f} operaciones al mes   "
      f"acierto {100*S.gano.mean():.1f} %   riesgo mediano {S.rgoP.median():.1f} pips")
print(f"  bruta {S.Rb.mean():+.4f}\n")
for nom, c in COSTES.items():
    R = neta(S, c); m, sd = R.mean(), R.std(ddof=1)
    ic = 1.96 * sd / sqrt(len(S))
    cruza = "SI" if m - ic > 0 else "no"
    print(f"  {nom:<28} coste {100*c/S.rgoP.median():4.1f} % del riesgo   "
          f"NETA {m:+.4f}   IC95 [{m-ic:+.4f}, {m+ic:+.4f}]   z {m/(sd/sqrt(len(S))):+.2f}"
          f"   cruza cero: {cruza}")

print("\n  por año, a 0,90 pips:")
for y in sorted(S.anio.unique()):
    G = S[S.anio == y]; R = neta(G, 0.90)
    print(f"    {y}  n {len(G):4d}  acierto {100*G.gano.mean():5.1f} %  neta {R.mean():+.4f}")

print("\n  en dinero, a 0,90 pips y 150 EUR de riesgo por operacion:")
R = neta(S, 0.90)
print(f"    {R.mean()*150:+.2f} EUR por operacion  x  {len(S)/meses:.1f} al mes"
      f"  =  {R.mean()*150*len(S)/meses:+.2f} EUR al mes")
print(f"    vaiven de un mes (1 sigma): +-{150*R.std(ddof=1)*sqrt(len(S)/meses):.0f} EUR")
