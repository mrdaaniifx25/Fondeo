"""Cerrar las reglas: objetivo EMA20 DINAMICO con stop fijo, medido en pips.

El objetivo dinamico (bt/mean_reversion_video.py) y el stop fijo
(bt/mean_reversion_pips.py) se midieron por separado. La combinacion de los
dos no la ha medido nadie, asi que se mide aqui antes de entregarla.

  python3 bt/mr_reglas.py
"""
import numpy as np, pandas as pd, sys

PIP = 1e-4
COSTE_P = 0.7
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
H1 = M.high.to_numpy(); L1 = M.low.to_numpy(); C1 = M.close.to_numpy()
M["b15"] = M.index // 15
V = M.groupby("b15").agg(ts=("loc","first"), o=("open","first"), h=("high","max"),
                         l=("low","min"), c=("close","last"))
V["i1"] = M.groupby("b15").apply(lambda g: g.index[-1], include_groups=False).to_numpy()
V = V.reset_index(drop=True)
o=V.o.to_numpy(); h=V.h.to_numpy(); l=V.l.to_numpy(); c=V.c.to_numpy(); I1=V.i1.to_numpy()
TS = V.ts.to_numpy()
ema20 = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
d = np.diff(c, prepend=c[0])
up = pd.Series(np.where(d>0,d,0.0)).ewm(alpha=1/14, adjust=False).mean()
dn = pd.Series(np.where(d<0,-d,0.0)).ewm(alpha=1/14, adjust=False).mean()
rsi14 = (100-100/(1+up/dn.replace(0,np.nan))).fillna(50).to_numpy()
sd = pd.Series(c).rolling(20).std().to_numpy()
med = (h+l)/2
corte = V.ts.iloc[int(0.70*len(V))]

def corre(k, stop_p, hor=64, tope_h=None):
    """Objetivo = EMA20 de la vela anterior, recalculada cada vela. Stop fijo."""
    bl = ema20 - k*sd; bu = ema20 + k*sd
    rl = (l < bl) & (c > med) & (c > o) & (rsi14 < 30)
    rs = (h > bu) & (c < med) & (c < o) & (rsi14 > 70)
    idx = np.nonzero(rl | rs)[0]; idx = idx[(idx > 40) & (idx < len(V)-2)]
    out = []; ult = -1
    for p in idx:
        if p <= ult: continue
        lado = 1 if rl[p] else -1
        ent = o[p+1]; rgo = stop_p*PIP; sl = ent - lado*rgo
        a = I1[p]+1
        pips = None; kf = None
        for q in range(p+1, min(p+1+hor, len(V))):
            aq = I1[q-1]+1; bq = I1[q]+1
            if bq > len(C1): break
            e = ema20[q-1]                       # EMA conocida al abrir la vela q
            sh = H1[aq:bq]; sl_ = L1[aq:bq]
            if len(sh) == 0: break
            gs = (sl_ <= sl) if lado > 0 else (sh >= sl)
            gt = (sh >= e) if lado > 0 else (sl_ <= e)
            ks = int(np.argmax(gs)) if gs.any() else 10**9
            kt = int(np.argmax(gt)) if gt.any() else 10**9
            if ks == kt == 10**9: continue
            if ks <= kt:
                pips, kf = -stop_p, (aq-a)+ks
            else:
                pips, kf = (e-ent)*lado/PIP, (aq-a)+kt
            break
        if pips is None:
            b = min(a+hor*15, len(C1))
            if b <= a: continue
            pips, kf = (C1[b-1]-ent)*lado/PIP, hor*15
        out.append((TS[p], pips, kf))
        ult = p + max(1, kf//15)
    return pd.DataFrame(out, columns=["ts","pips","min"])

print("REGLAS DEL VIDEO, CERRADAS · objetivo EMA20 DINAMICO + stop FIJO")
print(f"EUR/USD M15 · RSI(14) 30/70 · vela de rechazo · coste {COSTE_P} pips\n")
print(f"  {'k':>4}{'stop':>6}{'n':>6}{'ops/anio':>10}{'acierto':>9}{'min med':>9}"
      f"{'BRUTO':>9}{'t':>7}{'NETO':>8}{'dentro':>9}{'fuera':>9}")
res = []
for k in (1.5, 2.0):
    for stop_p in (8.0, 10.0, 12.0, 15.0, 18.0, 22.0):
        R = corre(k, stop_p)
        if len(R) < 80: continue
        t = R.pips.mean()/(R.pips.std(ddof=1)/np.sqrt(len(R)))
        dd = (R.ts < corte).to_numpy()
        print(f"  {k:>4.1f}{stop_p:>6.0f}{len(R):>6}{len(R)/5.66:>10.0f}"
              f"{100*(R.pips>COSTE_P).mean():>8.1f}%{R['min'].median():>9.0f}"
              f"{R.pips.mean():>9.3f}{t:>7.2f}{R.pips.mean()-COSTE_P:>8.3f}"
              f"{R.pips[dd].mean()-COSTE_P:>9.3f}{R.pips[~dd].mean()-COSTE_P:>9.3f}")
        res.append({"k":k,"stop":stop_p,"n":len(R),"bruto":R.pips.mean(),"t":t,
                    "neto":R.pips.mean()-COSTE_P,
                    "dentro":R.pips[dd].mean()-COSTE_P,
                    "fuera":R.pips[~dd].mean()-COSTE_P,"R":R})
        sys.stdout.flush()
    print()

F = pd.DataFrame([{a:b for a,b in r.items() if a!="R"} for r in res])
g = F[(F.dentro > 0) & (F.fuera > 0)]
print("  Celdas con NETO > 0 en los dos tramos:")
print("    ninguna" if g.empty else g.to_string(index=False))
print(f"\n  liston por seleccion con {len(F)} celdas: E[max|t|] ~ {np.sqrt(2*np.log(len(F))):.2f}")

# ---- la celda para operar: la de mejor neto que ademas tenga muestra
best = max(res, key=lambda r: r["neto"])
print(f"\n  CELDA ELEGIDA: k {best['k']} · stop {best['stop']:.0f} pips · "
      f"n {best['n']} · neto {best['neto']:+.3f} pips/op")
R = best["R"]; stop_p = best["stop"]

# ---- riesgo: del peor dia observado
R["dia"] = pd.to_datetime(R.ts).dt.normalize()
dpips = R.groupby("dia").pips.sum() - COSTE_P*R.groupby("dia").size()
dR = dpips/stop_p
print(f"\n  P&L DIARIO (en R, una posicion a la vez):")
print(f"    dias con operacion {len(dR)} · ops/dia {len(R)/len(dR):.2f} · "
      f"media {dR.mean():+.4f} R · sigma {dR.std():.3f}")
print(f"    PEOR DIA {dR.min():+.2f} R · mejor {dR.max():+.2f} R")
for rg in (0.0025, 0.005, 0.0075, 0.010, 0.015):
    print(f"    riesgo {100*rg:.2f} % -> peor dia observado {100*rg*dR.min():+.2f} % "
          f"(limite -3,00 %)" + ("   ELIMINADO" if 100*rg*dR.min() <= -3.0 else "   ok"))

# ---- el examen, con los dias reales y la deriva quitada
v = dR.to_numpy().astype(float); v = v - v.mean()
F1_, F2_, DIA_, TOT_ = 0.08, 0.05, 0.03, 0.10
def examen(rg, n=20000, tope=300, semilla=5):
    N=len(v); rng=np.random.default_rng(semilla); p1=p2=mdia=0; dur=[]
    for _ in range(n):
        a = rng.integers(0, max(N-tope,1)); dd = v[a:a+tope]*rg
        s=0.0; fase=0; meta=F1_
        for t_ in range(len(dd)):
            s += dd[t_]
            if dd[t_] <= -DIA_: mdia += 1; break
            if s <= -TOT_: break
            if s >= meta:
                if fase==0: fase,s,meta = 1,0.0,F2_
                else: fase=2; dur.append(t_); break
        if fase>=1: p1+=1
        if fase==2: p2+=1
    return p1/n, p2/n, (np.median(dur) if dur else float("nan")), mdia/n
print(f"\n  EL EXAMEN (deriva quitada, bloques moviles sobre {len(dR)} dias reales):")
print(f"    {'riesgo':>8}{'fase 1':>9}{'LAS DOS':>10}{'dias med':>10}{'muere dia':>11}")
for rg in (0.005, 0.0075, 0.010, 0.015):
    p1,p2,md,mdia = examen(rg)
    print(f"    {100*rg:>7.2f}%{100*p1:>8.1f}%{100*p2:>9.1f}%{md:>10.0f}{100*mdia:>10.1f}%")
    sys.stdout.flush()

# ---- rachas
gv = (dR > 0).to_numpy(); rr=[]; cc=0
for x in gv:
    if x:
        if cc: rr.append(cc)
        cc=0
    else: cc+=1
if cc: rr.append(cc)
rr=np.array(rr)
print(f"\n  RACHAS: dias en verde {100*gv.mean():.0f} % · racha roja mediana "
      f"{np.median(rr):.0f} · p90 {np.percentile(rr,90):.0f} · peor {rr.max():.0f}")
op = R.pips.to_numpy() - COSTE_P
gp = (op > 0); rr2=[]; cc=0
for x in gp:
    if x:
        if cc: rr2.append(cc)
        cc=0
    else: cc+=1
if cc: rr2.append(cc)
rr2=np.array(rr2)
print(f"  por OPERACION: acierto {100*gp.mean():.1f} % · racha de perdidas mediana "
      f"{np.median(rr2):.0f} · p90 {np.percentile(rr2,90):.0f} · peor {rr2.max():.0f}")
print(f"\n  SENSIBILIDAD AL COSTE (celda elegida, {best['n']} ops):")
for cp in (0.3, 0.5, 0.7, 1.0, 1.4):
    nt = R.pips.mean() - cp
    eur = nt * (0.005*10000.0/stop_p) * (len(R)/5.66/12)
    print(f"    coste {cp:.1f} pips -> neto {nt:+.3f} pips/op -> {eur:+.0f} EUR/mes")
