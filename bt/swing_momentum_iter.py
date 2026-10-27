"""Iteraciones 1 y 2 sobre bt/swing_momentum_eurusd.py.

El problema de la base no son los parametros: son 29 operaciones en 5,7 anios.
  ITER 1  quitar el filtro EMA (momentum puro de ruptura) -> mas operaciones
  ITER 2  mismas reglas sobre 27 ANIOS de EURUSD (serie diaria de la Reserva
          Federal, 1999-2026). Solo cierres, asi que el stop y el objetivo se
          resuelven con el CIERRE del dia: menos fiel, pero 5 veces mas muestra.

  python3 bt/swing_momentum_iter.py
"""
import numpy as np, pandas as pd
from math import sqrt
RIESGO, COSTE, RR, KSTOP, TOPE, CAP0 = 0.005, 0.0004, 2.0, 2.0, 20, 10000.0

# ═══════════ ITERACION 1 · sin filtro EMA, sobre el M1 2021-2026 ═══════════
M = pd.read_parquet("data/eurusd_m1.parquet"); M["ts"]=pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")
g = M.groupby("dfx", sort=True)
D = g.agg(o=("open","first"),h=("high","max"),l=("low","min"),c=("close","last"),
          ini=("open",lambda x:x.index[0]), fin=("close",lambda x:x.index[-1]))
D = D[D.index.notna()]; D = D[g.size()>=300]
tr = pd.concat([D.h-D.l,(D.h-D.c.shift(1)).abs(),(D.l-D.c.shift(1)).abs()],axis=1).max(axis=1)
D["atr"]=tr.rolling(14).mean()
HH,LL,CC = M.high.to_numpy(), M.low.to_numpy(), M.close.to_numpy()
INI,FIN = D.ini.to_numpy().astype(int), D.fin.to_numpy().astype(int)
C,H,L,O,ATR = (D[k].to_numpy() for k in ("c","h","l","o","atr"))
FE = D.index

def iter1(canal=20, kstop=KSTOP, rr=RR, filtro=False, tope=TOPE):
    mx=pd.Series(H).rolling(canal).max().to_numpy(); mn=pd.Series(L).rolling(canal).min().to_numpy()
    e50=pd.Series(C).ewm(span=50,adjust=False).mean().to_numpy()
    e200=pd.Series(C).ewm(span=200,adjust=False).mean().to_numpy()
    ops=[]; i=max(canal,200)+1; n=len(D)
    while i < n-1:
        if not np.isfinite(ATR[i]) or ATR[i]<=0: i+=1; continue
        lar = C[i]>mx[i-1]; cor = C[i]<mn[i-1]
        if filtro: lar = lar and e50[i]>e200[i]; cor = cor and e50[i]<e200[i]
        if not(lar or cor): i+=1; continue
        lado=1 if lar else -1; e=i+1; ent=O[e]; rgo=kstop*ATR[i]
        sl=ent-lado*rgo; tp=ent+lado*rr*rgo
        a,b=INI[e],FIN[min(e+tope-1,n-1)]; hh,ll=HH[a:b+1],LL[a:b+1]
        if lado>0: ks=np.nonzero(ll<=sl)[0]; kt=np.nonzero(hh>=tp)[0]
        else:      ks=np.nonzero(hh>=sl)[0]; kt=np.nonzero(ll<=tp)[0]
        fs=ks[0] if len(ks) else 10**9; ft=kt[0] if len(kt) else 10**9
        sal = tp if ft<fs else (sl if fs<10**9 else CC[b])
        R=(sal-ent)*lado/rgo - (2*COSTE*ent)/rgo
        dsal=min(e+tope-1,n-1)
        ops.append((FE[e],lado,R)); i=dsal+1
    return pd.DataFrame(ops, columns="fecha lado Rn".split())

# ITERACION 2 IMPOSIBLE: data/ext/fx_daily.csv (serie de la Fed, 1999-2026) se
# perdio al reciclarse el contenedor y la politica de red solo permite GitHub.
# Queda declarado: no se puede ampliar la muestra mas alla de 2021-2026.

def mide(T, et):
    if len(T)<8: return print(f"  {et:<34} (pocas: {len(T)})")
    gp,pp = T.Rn[T.Rn>0].sum(), -T.Rn[T.Rn<0].sum()
    eq=CAP0*(1+RIESGO*T.Rn).cumprod(); dd=float(((eq-eq.cummax())/eq.cummax()).min())
    sd=T.Rn.std(ddof=1); t=T.Rn.mean()/(sd/sqrt(len(T))) if sd>0 else np.nan
    print(f"  {et:<34}{len(T):>5}{100*(T.Rn>0).mean():>9.1f}%{T.Rn.mean():>+9.3f}"
          f"{t:>+7.2f}{(gp/pp if pp>0 else np.inf):>7.2f}{100*dd:>9.1f}%"
          f"{100*(eq.iloc[-1]/CAP0-1):>9.1f}%")
    return T.Rn.mean()

CAB=f"  {'':<34}{'n':>5}{'win rate':>10}{'exp R':>9}{'t':>7}{'PF':>7}{'maxDD':>10}{'ret':>10}"
print("\n"+"="*104); print("ITERACIÓN 1 · sin filtro EMA (momentum de ruptura puro), 2021-2026")
print("="*104); print(CAB)
for ca in (10,20,55):
    T=iter1(canal=ca, filtro=False)
    if len(T)<8: continue
    co=T.fecha.iloc[int(len(T)*.70)]
    mide(T, f"canal {ca} · completa")
    mide(T[T.fecha<co],  f"   canal {ca} · dentro 70 %")
    mide(T[T.fecha>=co], f"   canal {ca} · FUERA 30 %")

print("\n  ITERACIÓN 2 (27 años) NO EJECUTADA: data/ext/fx_daily.csv no está en el")
print("  contenedor y la red sólo permite GitHub. La muestra se queda en 2021-2026.")
