"""Configuracion mas defendible: DOL diario estricto (k=0.5), TP 3R."""
import sys, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0,"bt")
m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
ch = pd.read_parquet("data/ch_dol.parquet")
src = open("bt/estrategia_dol.py").read().replace("if d_fav > d_con: continue",
                                                  "if d_fav > 0.5*d_con: continue")
ns = {}; exec(compile(src,"m","exec"), ns)
C, senales, simular, PIP = ns["C"], ns["senales"], ns["simular"], ns["PIP"]
def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

cfg = C(dol_filtro=True, tp_r=3.0, dol_marcos=("D","W","M"))
sig,emb = senales(ch,cfg); tr = simular(sig,m1,cfg)
tr["b"]=(tr.pips+cfg.coste_pips)/tr.riesgo_pips
z,p = pz(tr.b)
gan,per = tr[tr.R>0], tr[tr.R<=0]
eq,pico,dd = 10000.0,10000.0,0.0
for R in tr.R:
    eq*=(1+0.01*R); pico=max(pico,eq); dd=max(dd,(pico-eq)/pico)
print("=== CONFIGURACION FINAL: CRT + order block M15 + DOL diario estricto, TP 3R ===")
print(f"  operaciones      {len(tr)}   (unas {len(tr)/6.6:.0f} al ano)")
print(f"  win rate         {100*(tr.R>0).mean():.2f}%   (equilibrio a 3R: 25.00%)")
print(f"  riesgo medio     {tr.riesgo_pips.mean():.1f} pips")
print(f"  ventaja bruta    {tr.b.mean():+.4f} R/op | z {z:+.2f} | p {p:.4f}")
print(f"  R neto           {tr.R.sum():+.2f}   | profit factor {gan.R.sum()/(-per.R.sum()):.3f}")
print(f"  equity al 1%     {eq:,.0f} EUR desde 10.000  ({100*(eq/10000-1):+.1f}%)")
print(f"  max drawdown     {100*dd:.1f}%")
print(f"  coste / riesgo   {100*1.2/tr.riesgo_pips.mean():.1f}% de cada operacion")

print("\n  por mitad:")
h=len(tr)//2
for nom,s in (("1a",tr.iloc[:h]),("2a",tr.iloc[h:])):
    zz,pp=pz(s.b)
    print(f"    {nom} mitad: n {len(s):>3} | bruto/op {s.b.mean():+.4f} | p {pp:.3f} | R neto {s.R.sum():+7.2f}")
print("\n  por ano:")
for a,g in tr.groupby(tr.ts.dt.year):
    print(f"    {a}: n {len(g):>3} | WR {100*(g.R>0).mean():5.1f}% | bruto/op {g.b.mean():+.4f} | R neto {g.R.sum():+7.2f}")

t1=m1["ts"].to_numpy(); HH=m1["high"].to_numpy(); LL=m1["low"].to_numpy(); CC=m1["close"].to_numpy()
def res(ets,ent,largo,riesgo,rr=3.0):
    sl=ent-riesgo if largo else ent+riesgo; tp=ent+rr*riesgo if largo else ent-rr*riesgo
    i0=int(np.searchsorted(t1,ets)); i1=min(i0+168*60,len(t1))
    if i0>=len(t1) or i1<=i0: return None,None
    a,b=HH[i0:i1],LL[i0:i1]
    gsl,gtp=((b<=sl,a>=tp) if largo else (a>=sl,b<=tp))
    isl=int(np.argmax(gsl)) if gsl.any() else 10**9
    itp=int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl==10**9 and itp==10**9: sal,ifin=CC[i1-1],(i1-i0)-1
    elif isl<=itp: sal,ifin=sl,isl
    else: sal,ifin=tp,itp
    br=(sal-ent) if largo else (ent-sal)
    return (br/PIP-1.2)/(riesgo/PIP), t1[i0+ifin]
Rs,lb=[],np.datetime64("1970-01-01")
for r in tr.itertuples():
    ets=np.datetime64(pd.Timestamp(r.ts)+pd.Timedelta(minutes=15))
    if ets<lb: continue
    R,f=res(ets,r.entrada,r.dir=="corto",r.riesgo_pips*PIP)
    if R is None: continue
    Rs.append(R); lb=f
horas=pd.DatetimeIndex(ch["ts"]).hour+pd.DatetimeIndex(ch["ts"]).minute/60
pool=ch[(horas>=6.5)&(horas<16)&ch["r_hi"].notna()].reset_index(drop=True)
rg=tr.riesgo_pips.to_numpy()*PIP; az=[]
for s in range(30):
    rng=np.random.default_rng(s); sel=np.sort(rng.choice(len(pool),size=len(tr),replace=False))
    R2,lb2=[],np.datetime64("1970-01-01")
    for j,i in enumerate(sel):
        row=pool.iloc[i]; ets=np.datetime64(pd.Timestamp(row.ts)+pd.Timedelta(minutes=15))
        if ets<lb2: continue
        R,f=res(ets,row.close,rng.random()<0.5,rg[j%len(rg)])
        if R is None: continue
        R2.append(R); lb2=f
    R2=np.array(R2); az.append(R2.sum()/len(R2)*len(tr))
az=np.array(az)
print(f"\n  espejo: {np.sum(Rs):+.2f} R   |   azar: media {az.mean():+.2f} (sd {az.std(ddof=1):.1f}) "
      f"-> real a {(tr.R.sum()-az.mean())/az.std(ddof=1):+.2f} sigmas")
tr.to_csv("data/trades_final.csv", index=False)
