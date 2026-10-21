"""Gestion de riesgo: el tope de operaciones al dia.

El P&L diario de esta estrategia tiene una cola izquierda gorda: el peor dia
observado es -6,53 R. Motivo: en un dia de tendencia el RSI se queda clavado
bajo 30 y cada vela de rechazo falla, encadenando perdidas. Eso es el modo de
fallo clasico de la reversion a la media.

Aqui se mide el tope de operaciones al dia y la regla de parar tras N perdidas
seguidas, que es lo unico que controla esa cola.

Objetivo = EMA20 CONGELADA en la senial (mide mejor que la dinamica cuando el
stop es fijo; ver docs/RESULTADOS_mr_reglas.md).

  python3 bt/mr_tope_dia.py
"""
import numpy as np, pandas as pd, sys

PIP, COSTE_P = 1e-4, 0.7
K, STOP_P = 1.5, 15.0
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
H1=M.high.to_numpy(); L1=M.low.to_numpy(); C1=M.close.to_numpy()
M["b15"] = M.index // 15
V = M.groupby("b15").agg(ts=("loc","first"), o=("open","first"), h=("high","max"),
                         l=("low","min"), c=("close","last"))
V["i1"] = M.groupby("b15").apply(lambda g: g.index[-1], include_groups=False).to_numpy()
V = V.reset_index(drop=True)
o=V.o.to_numpy(); h=V.h.to_numpy(); l=V.l.to_numpy(); c=V.c.to_numpy(); I1=V.i1.to_numpy()
TS=V.ts.to_numpy()
ema20 = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
d = np.diff(c, prepend=c[0])
up = pd.Series(np.where(d>0,d,0.0)).ewm(alpha=1/14, adjust=False).mean()
dn = pd.Series(np.where(d<0,-d,0.0)).ewm(alpha=1/14, adjust=False).mean()
rsi14 = (100-100/(1+up/dn.replace(0,np.nan))).fillna(50).to_numpy()
sd = pd.Series(c).rolling(20).std().to_numpy()
mdd = (h+l)/2
bl = ema20 - K*sd; bu = ema20 + K*sd
rl = (l < bl) & (c > mdd) & (c > o) & (rsi14 < 30)
rs = (h > bu) & (c < mdd) & (c < o) & (rsi14 > 70)
dia15 = pd.Series(V.ts).dt.normalize().to_numpy()

def corre(tope_dia=None, parar_tras=None, hor=64):
    idx = np.nonzero(rl | rs)[0]; idx = idx[(idx>40) & (idx<len(V)-2)]
    out=[]; ult=-1; dia_act=None; n_dia=0; perd_seg=0
    for p in idx:
        if p <= ult: continue
        if dia15[p] != dia_act:
            dia_act, n_dia, perd_seg = dia15[p], 0, 0
        if tope_dia is not None and n_dia >= tope_dia: continue
        if parar_tras is not None and perd_seg >= parar_tras: continue
        lado = 1 if rl[p] else -1
        ent = o[p+1]; rgo = STOP_P*PIP; sl = ent - lado*rgo
        ob = ema20[p]
        if (ob-ent)*lado <= 1*PIP: continue
        a = I1[p]+1; b = min(a+hor*15, len(C1))
        if b <= a: continue
        hi=H1[a:b]; lo=L1[a:b]
        gs = (lo<=sl) if lado>0 else (hi>=sl)
        gt = (hi>=ob) if lado>0 else (lo<=ob)
        ks = int(np.argmax(gs)) if gs.any() else 10**9
        kt = int(np.argmax(gt)) if gt.any() else 10**9
        if ks==kt==10**9: pips, kf = (C1[b-1]-ent)*lado/PIP, hor*15
        elif ks<=kt:      pips, kf = -STOP_P, ks
        else:             pips, kf = (ob-ent)*lado/PIP, kt
        n_dia += 1
        perd_seg = perd_seg+1 if pips-COSTE_P <= 0 else 0
        out.append((TS[p], dia15[p], pips, kf))
        ult = p + max(1, kf//15)
    R = pd.DataFrame(out, columns=["ts","dia","pips","min"])
    R["neto"] = R.pips - COSTE_P
    return R

F1_,F2_,DIA_,TOT_ = 0.08,0.05,0.03,0.10
def examen(v, rg, n=20000, tope=300, semilla=5):
    v = v - v.mean(); N=len(v); rng=np.random.default_rng(semilla)
    p1=p2=mdia=0; dur=[]
    for _ in range(n):
        a=rng.integers(0,max(N-tope,1)); dd=v[a:a+tope]*rg
        s=0.0; fase=0; meta=F1_
        for t_ in range(len(dd)):
            s+=dd[t_]
            if dd[t_] <= -DIA_: mdia+=1; break
            if s <= -TOT_: break
            if s >= meta:
                if fase==0: fase,s,meta=1,0.0,F2_
                else: fase=2; dur.append(t_); break
        if fase>=1: p1+=1
        if fase==2: p2+=1
    return p1/n,p2/n,(np.median(dur) if dur else float("nan")),mdia/n

print(f"GESTION DE RIESGO · k {K} · stop {STOP_P:.0f} pips · objetivo EMA20 congelada")
print(f"coste {COSTE_P} pips ida y vuelta\n")
print(f"  {'regla del dia':<28}{'n':>6}{'ops/dia':>9}{'neto pips':>11}"
      f"{'PEOR DIA':>10}{'riesgo max':>12}{'fase1':>8}{'LAS DOS':>9}{'muere dia':>11}")
for nom, td, pt in (("sin tope", None, None), ("tope 1 al dia", 1, None),
                    ("tope 2 al dia", 2, None), ("tope 3 al dia", 3, None),
                    ("parar tras 2 perdidas", None, 2),
                    ("parar tras 1 perdida", None, 1)):
    R = corre(td, pt)
    if len(R) < 80: continue
    dR = (R.groupby("dia").neto.sum())/STOP_P
    peor = dR.min()
    rmax = 0.03/abs(peor) if peor < 0 else 0.03
    rmax = np.floor(rmax*400)/400.0            # redondeo a 0,25 %
    v = dR.to_numpy().astype(float)
    p1,p2,md,mdia = examen(v, max(rmax, 0.0025))
    print(f"  {nom:<28}{len(R):>6}{len(R)/len(dR):>9.2f}{R.neto.mean():>11.3f}"
          f"{peor:>10.2f}{100*rmax:>11.2f}%{100*p1:>7.1f}%{100*p2:>8.1f}%{100*mdia:>10.1f}%")
    sys.stdout.flush()

print("\n  'riesgo max' = el que hace que el PEOR DIA observado no toque el -3 %.")
print("  El examen se simula con ESE riesgo, no con uno elegido a conveniencia.\n")

R = corre(2, None)
dR = (R.groupby("dia").neto.sum())/STOP_P
print(f"DETALLE DE LA CELDA RECOMENDADA · tope 2 al dia")
print(f"  n {len(R)} · {len(R)/5.66:.0f} ops/anio · {len(R)/len(dR):.2f} ops en dias con señal")
print(f"  dias con operacion {len(dR)} de {5.66*252:.0f} ({100*len(dR)/(5.66*252):.0f} %)")
print(f"  acierto {100*(R.neto>0).mean():.1f} % · duracion mediana {R['min'].median():.0f} min")
print(f"  neto {R.neto.mean():+.3f} pips/op · peor dia {dR.min():+.2f} R · mejor {dR.max():+.2f} R")
gp=(R.neto>0).to_numpy(); rr=[];cc=0
for x in gp:
    if x:
        if cc: rr.append(cc)
        cc=0
    else: cc+=1
if cc: rr.append(cc)
rr=np.array(rr)
print(f"  racha de perdidas: mediana {np.median(rr):.0f} · p90 {np.percentile(rr,90):.0f}"
      f" · PEOR {rr.max():.0f}")
print(f"\n  SENSIBILIDAD AL COSTE:")
for cp in (0.3,0.5,0.7,1.0,1.4):
    nt = R.pips.mean()-cp
    eur = nt*(0.005*10000.0/STOP_P)*(len(R)/5.66/12)
    print(f"    coste {cp:.1f} pips -> {nt:+.3f} pips/op -> {eur:+.0f} EUR/mes (riesgo 0,50 %)")
