"""Se puede aprender SU criterio? Las 250 roturas del bloque 6, con lo que el
decidio en cada una, contra todo lo que se ve en la pantalla en ese minuto.

Post hoc y declarado como tal: los datos ya estaban recogidos. La proteccion no
es el preregistro sino la validacion fuera de muestra, agrupada POR SESION, para
que ninguna rotura entrene con otra del mismo dia.

Tres preguntas, en este orden:
  1. Se puede predecir su SI/NO desde el grafico?      -> AUC sobre 'si'
  2. Se puede predecir el DESENLACE desde el grafico?  -> AUC sobre 'res'
  3. Si copio su criterio aprendido, gano dinero?      -> R neta fuera de muestra

  python3 bt/aprende_su_criterio.py
"""
import json
import numpy as np, pandas as pd

TZ, U, INI, FIN, SEP = "Europe/Madrid", 1e-4, 480, 690, 4
POR_SESION, COSTE = 25, 1.43

# ---------------------------------------------------------------- los datos
DIAS = {int(k): pd.Timestamp(v).date()
        for k, v in json.load(open("data/examen_dias6.json")).items()}
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date
m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(set(DIAS.values()))].reset_index(drop=True)

filas = []
for n, dia in DIAS.items():
    d = m1[m1.dia == dia].sort_values("min").reset_index(drop=True)
    O,H,L,C,M = (d.open.to_numpy(), d.high.to_numpy(), d.low.to_numpy(),
                 d.close.to_numpy(), d["min"].to_numpy())
    b5 = {}
    for i in range(len(d)):
        g = M[i]//5
        if g not in b5: b5[g] = [O[i], H[i], L[i], C[i]]
        else:
            b5[g][1] = max(b5[g][1], H[i]); b5[g][2] = min(b5[g][2], L[i]); b5[g][3] = C[i]
    asia = (M >= 0) & (M < INI)
    aHi = float(H[asia].max()) if asia.any() else np.nan
    aLo = float(L[asia].min()) if asia.any() else np.nan
    rot, ultimo, ultLado = [], -99, 0
    for i in range(len(d)):
        m = int(M[i])
        if not (INI <= m <= FIN): continue
        g = m//5 - 1
        if g not in b5: continue
        o5,h5,l5,c5 = b5[g]
        cA, cB = min(o5,c5), max(o5,c5)
        lado = 1 if C[i] > cB else (-1 if C[i] < cA else 0)
        if lado == 0: continue
        if m - ultimo < SEP and lado == ultLado: continue
        prev = ultimo
        ultimo, ultLado = m, lado
        k0 = max(0, i-9)
        ent = float(C[i])
        stp = float(L[k0:i+1].min()) if lado > 0 else float(H[k0:i+1].max())
        rgo = abs(ent-stp)
        if rgo < 1.5*U: continue
        tp = ent + lado*2*rgo
        fin = int(np.searchsorted(M, FIN))
        hh, ll = H[i+1:fin], L[i+1:fin]
        if not len(hh): continue
        largo = lado > 0
        gs, gt = ((ll <= stp, hh >= tp) if largo else (hh >= stp, ll <= tp))
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        itp = int(np.argmax(gt)) if gt.any() else 10**9
        if isl == 10**9 and itp == 10**9:
            sal = float(C[fin-1]); R = ((sal-ent) if largo else (ent-sal))/rgo
            mot = "cierre"
        else:
            R, mot = (-1.0, "SL") if isl <= itp else (2.0, "TP")

        # ---- lo que se ve en la pantalla en ese minuto, y nada mas
        def mom(k):
            j = max(0, i-k)
            return lado*(C[i]-C[j])/U
        j30 = max(0, i-29)
        rango30 = (H[j30:i+1].max() - L[j30:i+1].min())/U
        dHi = (H[:i+1].max() - C[i])/U
        dLo = (C[i] - L[:i+1].min())/U
        rgoDia = dHi + dLo
        # M15 y H1 ya CERRADAS, sin mirar al futuro
        g15 = m//15
        c15 = [b for b in [(k, v) for k, v in b5.items()] if False]
        def cierra_tf(paso, atras):
            gg = m//paso - atras
            sel = (M >= gg*paso) & (M < (gg+1)*paso) & (M <= m)
            return float(C[sel][-1]) if sel.any() else np.nan
        t15 = cierra_tf(15,0) - cierra_tf(15,1)
        t60 = cierra_tf(60,0) - cierra_tf(60,1)
        cuerpo5 = abs(c5-o5)/max(h5-l5, 1e-9)
        filas.append(dict(
            ses=n, min=m-INI, lado=lado, rgo=round(rgo/U,1), mot=mot, R=R,
            hora=m, cuerpo5=cuerpo5, rango5=(h5-l5)/U,
            mom10=mom(10), mom30=mom(30), mom60=mom(60),
            rango30=rango30, dAsiaHi=(aHi-C[i])/U, dAsiaLo=(C[i]-aLo)/U,
            anchoAsia=(aHi-aLo)/U,
            posDia=dLo/max(rgoDia,1e-9), rgoDia=rgoDia,
            t15=lado*t15/U, t60=lado*t60/U,
            desdeAnt=min(m-prev, 60) if prev > 0 else 60,
            largo=1.0 if largo else 0.0))
    ses = [f for f in filas if f["ses"] == n]
    if len(ses) > POR_SESION:
        rng = np.random.default_rng(20260904 + n)
        idx = set(sorted(rng.choice(len(ses), POR_SESION, replace=False)))
        keep = {id(ses[k]) for k in idx}
        filas = [f for f in filas if f["ses"] != n or id(f) in keep]

X = pd.DataFrame(filas)
sus = pd.read_csv("data/roturas_ops.csv")
X = X.merge(sus[["ses","min","lado","rgo","si"]], on=["ses","min","lado","rgo"], how="inner")
X["res"] = (X.mot == "TP").astype(float)
X["neta"] = X.R - COSTE/X.rgo
print(f"{len(X)} roturas emparejadas con sus decisiones "
      f"· toma {int(X.si.sum())} · acierto global {100*X.res.mean():.1f} %\n")

VARS = ["cuerpo5","rango5","mom10","mom30","mom60","rango30","dAsiaHi","dAsiaLo",
        "anchoAsia","posDia","rgoDia","t15","t60","rgo","hora","desdeAnt","largo"]

# ---------------------------------------------------------------- el motor
def auc(y, p):
    o = np.argsort(p); r = np.empty(len(p)); r[o] = np.arange(1, len(p)+1)
    # empates al rango medio
    s = pd.Series(p); r = s.rank().to_numpy()
    n1 = y.sum(); n0 = len(y)-n1
    if n1 == 0 or n0 == 0: return np.nan
    return (r[y == 1].sum() - n1*(n1+1)/2) / (n1*n0)

def logit(Xtr, ytr, lam=1.0, it=400):
    n, k = Xtr.shape
    A = np.hstack([np.ones((n,1)), Xtr]); w = np.zeros(k+1)
    for _ in range(it):
        z = A @ w; p = 1/(1+np.exp(-np.clip(z,-30,30)))
        g = A.T @ (p-ytr) + lam*np.r_[0, w[1:]]
        W = p*(1-p) + 1e-6
        Hm = A.T @ (A*W[:,None]) + lam*np.diag(np.r_[0, np.ones(k)])
        try: paso = np.linalg.solve(Hm, g)
        except np.linalg.LinAlgError: break
        w -= paso
        if np.max(np.abs(paso)) < 1e-8: break
    return w

def predice(w, Xte):
    A = np.hstack([np.ones((len(Xte),1)), Xte])
    return 1/(1+np.exp(-np.clip(A @ w,-30,30)))

def cv(objetivo, lam=1.0):
    """Validacion dejando fuera una SESION entera cada vez."""
    y = X[objetivo].to_numpy().astype(float)
    P = np.full(len(X), np.nan)
    for s in sorted(X.ses.unique()):
        tr, te = (X.ses != s).to_numpy(), (X.ses == s).to_numpy()
        mu, sd = X.loc[tr, VARS].mean(), X.loc[tr, VARS].std().replace(0,1)
        Xtr = ((X.loc[tr, VARS]-mu)/sd).to_numpy()
        Xte = ((X.loc[te, VARS]-mu)/sd).to_numpy()
        P[te] = predice(logit(Xtr, y[tr], lam), Xte)
    return y, P

print("="*66)
print("1 · SE PUEDE PREDECIR SU SI/NO DESDE EL GRAFICO?")
print("="*66)
for lam in (0.3, 1.0, 3.0, 10.0):
    y, P = cv("si", lam)
    yd, Pd = cv("si", lam)          # dentro de muestra, para comparar
    mu, sd = X[VARS].mean(), X[VARS].std().replace(0,1)
    Z = ((X[VARS]-mu)/sd).to_numpy()
    w = logit(Z, y, lam); Pin = predice(w, Z)
    print(f"  lambda {lam:5.1f}   AUC dentro {auc(y,Pin):.3f}   "
          f"AUC FUERA de muestra {auc(y,P):.3f}")
y, Psi = cv("si", 1.0)
print(f"\n  0,50 = no aprende nada · 1,00 = lo clona")

print("\n" + "="*66)
print("2 · SE PUEDE PREDECIR EL DESENLACE DESDE EL GRAFICO?")
print("="*66)
for lam in (0.3, 1.0, 3.0, 10.0):
    yr, Pr = cv("res", lam)
    mu, sd = X[VARS].mean(), X[VARS].std().replace(0,1)
    Z = ((X[VARS]-mu)/sd).to_numpy()
    w = logit(Z, yr, lam)
    print(f"  lambda {lam:5.1f}   AUC dentro {auc(yr,predice(w,Z)):.3f}   "
          f"AUC FUERA de muestra {auc(yr,Pr):.3f}")
yr, Pres = cv("res", 1.0)

print("\n" + "="*66)
print("3 · SI COPIO EL CRITERIO APRENDIDO, GANO DINERO?")
print("="*66)
print(f"{'quien elige':>28s} {'n':>5s} {'acierto':>9s} {'R neta':>9s}")
print("-"*56)
def linea(nom, sel):
    sel = np.asarray(sel)
    if sel.sum() == 0: print(f"{nom:>28s}   ninguna"); return
    print(f"{nom:>28s} {int(sel.sum()):5d} {100*X.res[sel].mean():8.1f} % "
          f"{X.neta[sel].mean():+9.3f}")
linea("todas (la regla a ciegas)", np.ones(len(X), bool))
linea("EL", X.si.to_numpy().astype(bool))
for q in (0.5, 0.4, 0.3, 0.2):
    u = np.quantile(Psi, 1-q)
    linea(f"copia de su criterio ({int(q*100)} %)", Psi >= u)
for q in (0.5, 0.4, 0.3, 0.2):
    u = np.quantile(Pres, 1-q)
    linea(f"modelo del desenlace ({int(q*100)} %)", Pres >= u)

print("\n" + "="*66)
print("QUE VARIABLES PESAN EN SU DECISION (todo el conjunto, estandarizado)")
print("="*66)
mu, sd = X[VARS].mean(), X[VARS].std().replace(0,1)
Z = ((X[VARS]-mu)/sd).to_numpy()
w = logit(Z, X.si.to_numpy().astype(float), 1.0)
ord_ = np.argsort(-np.abs(w[1:]))
for k in ord_[:10]:
    print(f"  {VARS[k]:>10s}  {w[1+k]:+.3f}")
