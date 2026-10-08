"""Entrena y valida hacia delante. Pre-registro docs/PREREGISTRO_barrido_ml.md"""
import sys, time
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

D = pd.read_parquet("data/barrido_ml.parquet")
VARS = ["off","rgoP","costepc","prof","cuerpo","rango_vela","dist_niv","recorrido",
        "rango_ref","atr5","atr1h","londres","hora","dow","lado","r3","r6","r12",
        "previos","cerro_mas_alla"]
ANIOS = [2022, 2023, 2024, 2025, 2026]

# ── AUDITORIA DE FUGA · una a una, porque el nulo no la cubre ─────────────
if "--auditoria" in sys.argv:
    print("diferencia de R neta entre el quintil alto y el bajo de cada variable")
    print("(algo por encima de +-0,30 no lo puede saber esa variable: seria fuga)\n")
    for v in VARS:
        x = D[v]
        if x.nunique() < 5: 
            g = D.groupby(v).Rn.mean()
            print(f"{v:>16}  {g.min():+.4f} .. {g.max():+.4f}   dif {g.max()-g.min():+.4f}")
            continue
        q = pd.qcut(x.rank(method="first"), 5, labels=False)
        g = D.groupby(q).Rn.mean()
        print(f"{v:>16}  bajo {g.iloc[0]:+.4f}   alto {g.iloc[4]:+.4f}   dif {g.iloc[4]-g.iloc[0]:+.4f}")
    sys.exit()

def corre(D, col="Rn", semilla=0):
    """Validacion hacia delante: entrena con los anios anteriores, predice el siguiente."""
    pred = pd.Series(np.nan, index=D.index)
    for Y in ANIOS:
        tr = D.anio < Y
        te = D.anio == Y
        if tr.sum() < 5000 or te.sum() == 0: continue
        M = HistGradientBoostingRegressor(
            max_iter=220, learning_rate=0.06, max_depth=5,
            min_samples_leaf=200, l2_regularization=1.0, random_state=semilla)
        M.fit(D.loc[tr, VARS], D.loc[tr, col])
        pred[te] = M.predict(D.loc[te, VARS])
    return pred

t0 = time.time()
D["pred"] = corre(D)
F = D[D.pred.notna()].copy()
print(f"fuera de muestra: {len(F):,} filas, {F.anio.min()}-{F.anio.max()}  "
      f"({time.time()-t0:.0f} s)\n")

F["dec"] = pd.qcut(F.pred.rank(method="first"), 10, labels=False) + 1
F["Rb"] = 3 * F.gana - 1
print("de decil a decil, fuera de muestra")
print(f"{'decil':>6}{'n':>8}{'acierto':>9}{'riesgo':>9}{'coste':>8}{'BRUTA':>10}{'R neta':>10}{'IC95':>21}")
for d, S in F.groupby("dec"):
    m, s = S.Rn.mean(), S.Rn.std(ddof=1)
    ic = 1.96 * s / np.sqrt(len(S))
    print(f"{d:>6}{len(S):>8,}{100*S.gana.mean():>8.1f} %{S.rgoP.median():>8.1f} p"
          f"{S.costepc.median():>7.0f} %{S.Rb.mean():>+10.4f}{m:>+10.4f}   [{m-ic:+.4f}, {m+ic:+.4f}]")

S = F[F.dec == 10]
m, s = S.Rn.mean(), S.Rn.std(ddof=1)
ic = 1.96 * s / np.sqrt(len(S))
print(f"\nDECIL SUPERIOR  n {len(S):,}  R neta {m:+.4f}  IC95 [{m-ic:+.4f}, {m+ic:+.4f}]"
      f"  z {m/(s/np.sqrt(len(S))):+.2f}")
print(f"  frente a todas: {F.Rn.mean():+.4f}   mejora {m - F.Rn.mean():+.4f}")
zb = S.Rb.mean() / (S.Rb.std(ddof=1) / np.sqrt(len(S)))
print(f"  su BRUTA: {S.Rb.mean():+.4f} (z {zb:+.2f})   acierto {100*S.gana.mean():.1f} %"
      f"   el que necesita: {100*(1/3 + 1.43/(3*S.rgoP.median())):.1f} %")
print(f"  >> si la bruta es cero, el decil solo esta eligiendo stops anchos,"
      f" no operaciones buenas")
print("\npor anio, decil superior:")
for Y, G in S.groupby("anio"):
    print(f"  {Y}  n {len(G):5,}  acierto {100*G.gana.mean():5.1f} %  R neta {G.Rn.mean():+.4f}")

# ── NULOS ────────────────────────────────────────────────────────────────
print("\n20 nulos (misma tuberia, etiquetas barajadas dentro de cada mes)")
D["mes"] = pd.DatetimeIndex(D.t).to_period("M")
mejoras = []
for r in range(20):
    rng = np.random.default_rng(1000 + r)
    D["Rn_b"] = D.groupby("mes").Rn.transform(lambda x: rng.permutation(x.to_numpy()))
    p = corre(D, col="Rn_b", semilla=r)
    G = D[p.notna()].copy(); G["p"] = p[p.notna()]
    d10 = G[G.p >= G.p.quantile(0.9)]
    mejoras.append(d10.Rn_b.mean() - G.Rn_b.mean())
    print(f"  nulo {r+1:2d}  mejora {mejoras[-1]:+.4f}")
mejoras = np.array(mejoras)
print(f"\nnulos: de {mejoras.min():+.4f} a {mejoras.max():+.4f}  "
      f"(media {mejoras.mean():+.4f}, sd {mejoras.std():.4f})")
print(f"real:  {m - F.Rn.mean():+.4f}")
F.to_parquet("data/barrido_ml_pred.parquet", index=False)
