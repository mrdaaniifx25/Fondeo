"""El modelo congelado, operando. Elige las K mejores velas de cada dia y entra
con SU stop medido -el extremo de las dos ultimas velas de M5- y 1:2.

Se prueba en los 114 dias del examen con probabilidades validadas por dias no
vistos, y luego en los 1.032 dias que el modelo no ha tocado nunca.

  python3 bt/regla_modelo.py
"""
import json, numpy as np, pandas as pd
from math import sqrt, erf
U, COSTE, TZ, INI, CORTE = 1e-4, 1.43, "Europe/Madrid", 480, 690
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
zf = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x))) if len(x) > 2 else float("nan")

X = pd.read_csv("data/modelo_pares.csv.gz"); X["dia"] = pd.to_datetime(X.dia).dt.date
w = np.load("data/modelo_w.npy")
esc = pd.read_csv("data/modelo_escala.csv", index_col=0).iloc[:, 0]
VAR = ["cerca_asia","hacia_asia","rechazo","rotura","d_ext","d_ext_contra","toque",
       "hora","rango","h4_al","m15_al","dia_al","imp_al","imp_abs","cuerpo_al","dentro_asia"]
mu = np.array([esc["mu_"+k] for k in VAR]); sd = np.array([esc["sd_"+k] for k in VAR])
A = np.column_stack([np.ones(len(X)), (X[VAR].to_numpy()-mu)/sd])
X["p"] = 1/(1+np.exp(-A@w))

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
T1 = m1["loc"].to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
v5 = m1.assign(b=(m1["min"]//5)*5).groupby(["dia","b"]).agg(
       h=("high","max"), l=("low","min"), n=("close","size")).reset_index()
v5 = v5[v5.n >= 3]; v5["cierre_min"] = v5.b + 5
V = {(r.dia, r.cierre_min): (r.h, r.l) for r in v5.itertuples()}

def opera(sel):
    """Su stop medido: extremo de las dos ultimas velas de M5. 1:2. Corte 11:30."""
    out = []
    for r in sel.itertuples():
        xs = [V[(r.dia, r.cierre_min-5*i)] for i in (0, 1) if (r.dia, r.cierre_min-5*i) in V]
        if not xs: continue
        ext = min(x[1] for x in xs) if r.lado > 0 else max(x[0] for x in xs)
        rgo = abs(r.c - ext)/U
        if rgo < 1.5: continue
        sl, tp = ext, r.c + r.lado*2*rgo*U
        ini = np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(minutes=int(r.cierre_min)))
        fin = np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(minutes=CORTE))
        k = int(np.searchsorted(T1, ini)); j = min(max(int(np.searchsorted(T1, fin)), k+1), len(T1))
        hh, ll = H1[k:j], L1[k:j]
        largo = r.lado > 0
        gs, gt = ((ll <= sl, hh >= tp) if largo else (hh >= sl, ll <= tp))
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        itp = int(np.argmax(gt)) if gt.any() else 10**9
        if isl == 10**9 and itp == 10**9:
            sal = C1[j-1]; R = ((sal-r.c) if largo else (r.c-sal))/U/rgo; mot = "cierre"
        elif isl <= itp: R, mot = -1.0, "SL"
        else:            R, mot = 2.0, "TP"
        out.append(dict(dia=r.dia, cierre_min=r.cierre_min, lado=r.lado, p=r.p,
                        rgo=rgo, R=R, mot=mot, neta=R-COSTE/rgo))
    return pd.DataFrame(out)

def informe(nom, d, ndias):
    if len(d) < 10: print(f"\n{nom}: {len(d)} operaciones, muy pocas"); return
    res = d[d.mot != "cierre"]; ac = (res.mot == "TP").mean()
    se = sqrt((1/3)*(2/3)/len(res)); zn = zf(d.neta.to_numpy())
    print(f"\n{nom}")
    print(f"  {len(d)} operaciones en {d.dia.nunique()} días de {ndias}  ·  "
          f"{len(d)/ndias:.2f} por sesión")
    print(f"  acierto {100*ac:.1f} %   z contra 33,3 % = {(ac-1/3)/se:+.2f}")
    print(f"  stop mediano {d.rgo.median():.1f} p  ·  coste/riesgo {100*(COSTE/d.rgo).mean():.1f} %")
    print(f"  R bruta {d.R.mean():+.3f}  ·  R NETA {d.neta.mean():+.3f}  z = {zn:+.2f}"
          f"  (p={p2(zn):.5f})  ·  suma {d.neta.sum():+.1f} R")

print("="*74); print("EL MODELO CONGELADO, OPERANDO"); print("="*74)
for K in (1, 2, 3):
    for et, sub in (("114 días del examen", X[X.examen]),
                    ("1.032 días NUEVOS", X[~X.examen])):
        sel = sub.sort_values("p", ascending=False).groupby("dia").head(K)
        informe(f"K={K} mejores por día · {et}", opera(sel), sub.dia.nunique())
print("\n" + "="*74)
print("Y SI SOLO SE OPERA CUANDO EL MODELO ESTÁ MUY SEGURO (umbral de probabilidad)")
print("="*74)
nue = X[~X.examen]
for u in (0.05, 0.10, 0.20, 0.30):
    sel = nue[nue.p >= u]
    d = opera(sel)
    if len(d) < 10: print(f"  p >= {u:.2f}: {len(d)} operaciones"); continue
    res = d[d.mot != "cierre"]
    print(f"  p >= {u:.2f}   n={len(d):5d}  acierto {100*(res.mot=='TP').mean():5.1f} %  "
          f"stop {d.rgo.median():4.1f}p  R neta {d.neta.mean():+.3f}  z {zf(d.neta.to_numpy()):+6.2f}")
