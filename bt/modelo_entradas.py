"""Multivariante: sus 150 entradas contra TODOS los pares (vela, direccion) que
tenia disponibles esos dias. Una variable cada vez no vale; el patron, si esta,
es una combinacion.

Se modela el par (vela de M5, comprar o vender), asi la direccion entra en el
modelo en vez de decidirse a mano. Regresion logistica con L2, ajustada solo en
los 114 dias del examen y validada por dias que el modelo no ha visto.

  python3 bt/modelo_entradas.py
"""
import json, sys
import numpy as np, pandas as pd
from math import sqrt, erf

U, COSTE, TZ = 1e-4, 1.43, "Europe/Madrid"
INI, FIN, CORTE = 480, 690, 690
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
zf = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x)))

DIAS_EX = set()
for dj in ("data/examen_dias.json", "data/examen_dias2.json",
           "data/examen_dias3.json", "data/examen_dias4.json"):
    DIAS_EX |= {pd.Timestamp(v).date() for v in json.load(open(dj)).values()}

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
T1 = m1["loc"].to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()

v = m1.assign(b=(m1["min"]//5)*5).groupby(["dia","b"]).agg(
      o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
      n=("close","size")).reset_index()
v = v[v.n >= 3].reset_index(drop=True); v["cierre_min"] = v.b + 5

print("construyendo pares (vela, dirección)...", flush=True)
filas = []
for dia, d1 in m1.groupby("dia"):
    a = d1[d1["min"] < INI]
    if len(a) < 300: continue
    hi, lo = float(a.high.max()), float(a.low.min())
    h4 = d1[(d1["min"] >= 240) & (d1["min"] < INI)]
    if h4.empty: continue
    h4d = float(np.sign(float(h4.close.iloc[-1]) - float(h4.open.iloc[0])))
    g = v[(v.dia == dia) & (v.cierre_min >= INI) & (v.cierre_min <= FIN)].reset_index(drop=True)
    if len(g) < 10: continue
    ap0 = float(g.o.iloc[0])
    H, L, C, O = g.h.to_numpy(), g.l.to_numpy(), g.c.to_numpy(), g.o.to_numpy()
    smax = np.maximum.accumulate(H); smin = np.minimum.accumulate(L)
    toques = {True: 0, False: 0}
    for i, r in enumerate(g.itertuples()):
        arriba = abs(r.c-hi) <= abs(r.c-lo)
        L0 = hi if arriba else lo
        toca = r.l <= L0 <= r.h
        n_toque = toques[arriba]
        if toca: toques[arriba] += 1
        dentro = (r.c < L0) if arriba else (r.c > L0)
        # impulso de las 3 velas anteriores y de la propia
        imp = (r.c - C[max(i-3,0)])/U
        cuerpo = np.sign(r.c - r.o)
        m15 = np.sign(C[i] - C[max(i-3,0)])
        dia_d = np.sign(r.c - ap0)
        for lado in (1, -1):
            hacia = 1.0 if ((lado > 0) == arriba) else -1.0
            filas.append((dia, int(r.cierre_min), lado, r.c,
                float(min(abs(r.c-hi), abs(r.c-lo))/U),        # cerca_asia
                hacia,                                          # hacia_asia
                float(toca and dentro and hacia < 0),           # rechazo
                float(toca and not dentro and hacia > 0),       # rotura
                float(((smax[i]-r.c) if lado > 0 else (r.c-smin[i]))/U),   # d_ext (a favor)
                float(((r.c-smin[i]) if lado > 0 else (smax[i]-r.c))/U),   # d_ext_contra
                float(n_toque), float(r.cierre_min-INI), float((r.h-r.l)/U),
                float(lado == h4d), float(lado == m15), float(lado == dia_d),
                float(np.sign(imp) == lado), float(abs(imp)),
                float(cuerpo == lado), float(lo <= r.c <= hi)))
COLS = ["dia","cierre_min","lado","c","cerca_asia","hacia_asia","rechazo","rotura",
        "d_ext","d_ext_contra","toque","hora","rango","h4_al","m15_al","dia_al",
        "imp_al","imp_abs","cuerpo_al","dentro_asia"]
X = pd.DataFrame(filas, columns=COLS)
X["examen"] = X.dia.isin(DIAS_EX)
print(f"{len(X):,} pares · {X.examen.sum():,} en los 114 días del examen")

# marcar los suyos
t = pd.read_csv("data/operaciones_150.csv"); t["dia"] = pd.to_datetime(t.dia).dt.date
X["suya"] = False; X["ocupada"] = False
idx = {(r.dia, r.cierre_min, r.lado): i for i, r in enumerate(X.itertuples())}
n_ok = 0
for r in t.itertuples():
    cm = r.ent_min - (r.ent_min % 5)
    if cm < INI: cm = INI
    k = idx.get((r.dia, cm, r.lado))
    if k is not None: X.loc[k, "suya"] = True; n_ok += 1
X.loc[X.suya, "ocupada"] = False
for r in t.itertuples():
    X.loc[(X.dia == r.dia) & (X.cierre_min > r.ent_min) & (X.cierre_min <= r.sal_min)
          & ~X.suya, "ocupada"] = True
print(f"marcadas {n_ok} de {len(t)} entradas suyas sobre su par exacto")

VAR = ["cerca_asia","hacia_asia","rechazo","rotura","d_ext","d_ext_contra","toque",
       "hora","rango","h4_al","m15_al","dia_al","imp_al","imp_abs","cuerpo_al","dentro_asia"]
E = X[X.examen & ~X.ocupada].reset_index(drop=True)
print(f"ajuste sobre {len(E):,} pares ({int(E.suya.sum())} suyos)\n")

def logit(A, y, lam=1.0, it=200):
    """Newton-Raphson con L2. A ya lleva la columna de unos."""
    w = np.zeros(A.shape[1])
    P = np.eye(A.shape[1])*lam; P[0,0] = 0
    for _ in range(it):
        p = 1/(1+np.exp(-A@w)); p = np.clip(p, 1e-9, 1-1e-9)
        g = A.T@(y-p) - P@w
        Hs = -(A.T*(p*(1-p)))@A - P
        try: d = np.linalg.solve(Hs, -g)
        except np.linalg.LinAlgError: break
        w = w + d
        if np.max(np.abs(d)) < 1e-9: break
    return w

mu, sd = E[VAR].mean(), E[VAR].std().replace(0, 1)
def dis(d): return np.column_stack([np.ones(len(d)), ((d[VAR]-mu)/sd).to_numpy()])
w = logit(dis(E), E.suya.to_numpy().astype(float))
print("="*74); print("QUÉ PESA EN SU DECISIÓN  (coeficientes estandarizados)"); print("="*74)
ord_ = np.argsort(-np.abs(w[1:]))
for j in ord_:
    print(f"  {VAR[j]:16s} {w[j+1]:+7.3f}")

# validacion por dias que el modelo no ha visto
dias = sorted(set(E.dia)); rng = np.random.default_rng(7)
perm = rng.permutation(len(dias)); pl = np.zeros(len(E))
for f in range(5):
    fuera = {dias[i] for i in perm[f::5]}
    tr = E[~E.dia.isin(fuera)]; te = E.dia.isin(fuera).to_numpy()
    wf = logit(dis(tr), tr.suya.to_numpy().astype(float))
    pl[te] = 1/(1+np.exp(-dis(E[te])@wf))
E["p"] = pl
pos, neg = E[E.suya].p.to_numpy(), E[~E.suya].p.to_numpy()
auc = (np.mean(rng.choice(pos, 200000) > rng.choice(neg, 200000))
       + 0.5*np.mean(rng.choice(pos, 200000) == rng.choice(neg, 200000)))
print(f"\n  AUC validada por días no vistos: {auc:.3f}   (0,5 = azar)")
top = E.nlargest(len(E)//100, "p")
print(f"  del 1 % mejor puntuado ({len(top)} pares), son suyos {int(top.suya.sum())} "
      f"({100*top.suya.mean():.1f} %; la base es {100*E.suya.mean():.2f} %)")
np.save("data/modelo_w.npy", w)
pd.Series({**{"mu_"+k: v for k, v in mu.items()}, **{"sd_"+k: v for k, v in sd.items()}}
          ).to_csv("data/modelo_escala.csv")
X.to_csv("data/modelo_pares.csv.gz", index=False, compression="gzip")
print("\nguardado el modelo y los pares")
