"""Sostener la prima de riesgo con el apalancamiento ajustado a las barreras.

Preregistro sellado en docs/PREREGISTRO_prima.md.

Sin senal, sin entrada, sin stop: compra y manten. Lo unico que se ajusta es
el apalancamiento L. Por el teorema del muestreo opcional, superar el 37,0 %
exige deriva real, asi que esto es tambien una prueba de si la deriva existe.

  python3 bt/prima.py
"""
import os, numpy as np, pandas as pd

OBJ1, OBJ2   = 0.08, 0.05
LIM_DIA, LIM_TOT = 0.05, 0.10
DMAX, DMIN   = 60, 3
SIMS, BLOQ   = 20000, 20
LS   = (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0)
FIN  = (0.03, 0.06, 0.09)
rng  = np.random.default_rng(20260905)
TECHO = (LIM_TOT/(OBJ1+LIM_TOT))*(LIM_TOT/(OBJ2+LIM_TOT))

# --- rendimientos diarios del US100: cierre de sesion a cierre de sesion ----
d = pd.read_parquet("data/nsxusd_m1.parquet"); d["ts"] = pd.to_datetime(d["ts"])
ny = d.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
m  = ny.dt.hour*60 + ny.dt.minute
s  = d[(m >= 9*60+30) & (m <= 16*60) & (ny.dt.dayofweek < 5)].copy()
s["dia"] = ny[(m >= 9*60+30) & (m <= 16*60) & (ny.dt.dayofweek < 5)].dt.date
g = s.groupby("dia").agg(ap=("open","first"), hi=("high","max"),
                         lo=("low","min"), ci=("close","last"),
                         n=("close","size"))
g = g[g.n >= 120].reset_index()
g["r"]   = g.ci.pct_change()                       # cierre a cierre
g["mae"] = g.lo/g.ci.shift(1) - 1                  # peor punto del dia
g["gap"] = g.ap/g.ci.shift(1) - 1                  # hueco de apertura
g["anio"] = pd.to_datetime(g.dia).dt.year
g = g.dropna().reset_index(drop=True)
print(f"US100 · {len(g)} dias · {g.dia.min()} -> {g.dia.max()}")
print(f"  deriva diaria {g.r.mean()*100:+.4f} %   volatilidad {g.r.std()*100:.3f} %"
      f"   Sharpe anual {g.r.mean()/g.r.std()*np.sqrt(252):+.2f}")
print(f"  techo con ventaja CERO: fase1 {LIM_TOT/(OBJ1+LIM_TOT)*100:.1f} % · "
      f"fase2 {LIM_TOT/(OBJ2+LIM_TOT)*100:.1f} % · las dos {TECHO*100:.1f} %\n")

def fase(R, MAE, L, fin, obj):
    """R y MAE son matrices (sims, DMAX) de rendimientos diarios del indice."""
    cst = fin/360*L
    x   = R*L - cst                       # rendimiento diario de la cuenta
    peor= MAE*L - cst                     # peor punto del dia, para el limite
    eq  = np.cumprod(1+x, axis=1) - 1
    prev= np.concatenate([np.zeros((len(x),1)), eq[:, :-1]], axis=1)
    fldia = peor <= -LIM_DIA                       # limite diario, flotante
    fltot = (1+prev)*(1+peor) - 1 <= -LIM_TOT      # limite total, flotante
    fal = fldia | fltot
    idx = np.arange(DMAX)[None, :]
    pas = (eq >= obj) & (idx >= DMIN-1)
    ip = np.where(pas.any(1), pas.argmax(1), DMAX+9)
    if_= np.where(fal.any(1), fal.argmax(1), DMAX+9)
    ok = ip < if_
    return float(ok.mean()), (float(np.median(ip[ok])) if ok.any() else np.nan)

def caminos(sub, modo, sims=SIMS, con_gap=False):
    r, ma, gp = sub.r.to_numpy(), sub.mae.to_numpy(), sub.gap.to_numpy()
    if modo == "hist":                             # ventanas reales solapadas
        k = len(r) - DMAX
        i = np.arange(k)[:, None] + np.arange(DMAX)[None, :]
        return (r[i], ma[i], gp[i]) if con_gap else (r[i], ma[i])
    if modo == "bloque":                           # bootstrap por bloques
        nb = DMAX//BLOQ
        st = rng.integers(0, len(r)-BLOQ, size=(sims, nb))
        i  = (st[:, :, None] + np.arange(BLOQ)[None, None, :]).reshape(sims, -1)
        return (r[i], ma[i], gp[i]) if con_gap else (r[i], ma[i])
    i = rng.integers(0, len(r), size=(sims, DMAX))  # iid
    return (r[i], ma[i], gp[i]) if con_gap else (r[i], ma[i])

AJU, FUE = g[g.anio <= 2023], g[g.anio >= 2024]
for fin in FIN:
    print("=" * 76)
    print(f"FINANCIACION {fin*100:.0f} % ANUAL")
    print("=" * 76)
    print(f"  {'L':>5} | {'AJUSTE 2020-2023':^26} | {'FUERA 2024-2026':^26}")
    print(f"  {'':>5} | {'hist':>7} {'bloque':>7} {'iid':>7} {'2fases':>6} | "
          f"{'hist':>7} {'bloque':>7} {'iid':>7} {'2fases':>6}")
    for L in LS:
        fila = f"  {L:5.2f} |"
        for sub in (AJU, FUE):
            v = []
            for modo in ("hist", "bloque", "iid"):
                R, M = caminos(sub, modo)
                p1,_ = fase(R, M, L, fin, OBJ1); v.append(p1)
            R, M = caminos(sub, "bloque")
            p2,_ = fase(R, M, L, fin, OBJ2)
            fila += (f" {v[0]*100:6.1f}% {v[1]*100:6.1f}% {v[2]*100:6.1f}% "
                     f"{v[1]*p2*100:5.1f}% |")
        print(fila)
    print()

# --------------------------------------------------------------------------
# EXPLORATORIO (no preregistrado): un cortacircuitos justo por dentro del
# limite diario. Si el flotante cae al -X %, se cierra y no se vuelve a entrar
# hasta la apertura siguiente. Convierte una descalificacion en una perdida.
# --------------------------------------------------------------------------
def fase_corta(R, MAE, GAP, L, fin, obj, corte, desliz=0.0005):
    """Del hueco de apertura NO se escapa: si la sesion abre ya por debajo del
    corte, se sale en la apertura, no en el nivel del corte."""
    cst  = fin/360*L
    x    = R*L - cst; peor = MAE*L - cst; hueco = GAP*L - cst
    salta= peor <= -corte
    # precio de salida: el corte si se llega intradia, la apertura si ya abrio
    # por debajo. Mas deslizamiento en los dos casos.
    sale = np.where(hueco <= -corte, hueco, -corte) - desliz*L
    x    = np.where(salta, sale, x)
    peor = np.where(salta, sale, peor)
    eq   = np.cumprod(1+x,1)-1
    prev = np.concatenate([np.zeros((len(x),1)), eq[:,:-1]],1)
    fal  = (peor <= -LIM_DIA) | (((1+prev)*(1+peor)-1) <= -LIM_TOT)
    idx  = np.arange(DMAX)[None,:]
    pas  = (eq>=obj)&(idx>=DMIN-1)
    ip = np.where(pas.any(1), pas.argmax(1), DMAX+9)
    if_= np.where(fal.any(1), fal.argmax(1), DMAX+9)
    ok = ip<if_
    return float(ok.mean()), (float(np.median(ip[ok])) if ok.any() else np.nan)

print("=" * 76)
print("CORTACIRCUITOS · cerrar el dia si el flotante cae al -X %")
print("   financiacion 6 % · bootstrap por bloques · las DOS fases")
print("=" * 76)
print(f"  {'L':>5} {'corte':>7} | {'AJUSTE 2020-2023':>17} | {'FUERA 2024-2026':>16} "
      f"| {'dias':>5}")
mejor = None
for L in (1.0, 1.25, 1.5, 1.75, 2.0, 2.5):
    for corte in (0.025, 0.03, 0.035, 0.04, 0.045):
        v = []
        for sub in (AJU, FUE):
            R, M, G_ = caminos(sub, "bloque", con_gap=True)
            p1,d1 = fase_corta(R, M, G_, L, 0.06, OBJ1, corte)
            p2,d2 = fase_corta(R, M, G_, L, 0.06, OBJ2, corte)
            v.append((p1*p2, d1+d2))
        marca = ""
        if mejor is None or v[0][0] > mejor[0]:
            mejor = (v[0][0], L, corte, v[1][0]); marca = "  <-"
        print(f"  {L:5.2f} {corte*100:6.1f}% | {v[0][0]*100:16.1f}% "
              f"| {v[1][0]*100:15.1f}% | {v[0][1]:5.0f}{marca}")
print(f"\n  techo con ventaja CERO {TECHO*100:.1f} %")
print(f"  mejor en ajuste: L={mejor[1]:.2f} corte {mejor[2]*100:.1f} %  ->  "
      f"ajuste {mejor[0]*100:.1f} %   FUERA DE MUESTRA {mejor[3]*100:.1f} %")
