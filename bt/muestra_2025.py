import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd, json
from crt_canonico import velas_ref, senales, en_kz, KZ_FX
from crt_fib import setups, ejecuta_fib

m1=pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
m5=m1.set_index("ts").resample("5min",label="left",closed="left").agg(
   open=("open","first"),high=("high","max"),low=("low","min"),close=("close","last")).dropna().reset_index()
U=0.0001
def mad(t): return pd.Timestamp(t).tz_localize("UTC").tz_convert("Europe/Madrid")

# ---------- CRT PURO ----------
CFG=dict(entrada="v2",cierre_estricto=True,killzone=True,min_rr=1.5,
         buffer=1.0,tope_dia=3,max_horas=48)
ref=velas_ref(m1,4,1); sig=senales(ref,CFG)
INI=ref["ini"].to_numpy(); FIN=ref["fin"].to_numpy()
T=m1.ts.values;H=m1.high.values;L=m1.low.values;Cc=m1.close.values;O=m1.open.values
puro=[];libre=np.datetime64("1970-01-01");cuenta={}
for r in sig.itertuples():
    i0=int(np.searchsorted(T,np.datetime64(pd.Timestamp(r.ini3))))
    i1=int(np.searchsorted(T,np.datetime64(pd.Timestamp(r.fin3))))+1
    if i0>=len(T) or i1<=i0 or np.datetime64(pd.Timestamp(r.ini3))<libre: continue
    niv=r.v2_hi if r.largo else r.v2_lo
    g=(H[i0:i1]>=niv) if r.largo else (L[i0:i1]<=niv)
    if not g.any(): continue
    it=i0+int(np.argmax(g)); e=max(niv,O[it]) if r.largo else min(niv,O[it]); ts_e=T[it]
    if not en_kz(ts_e,KZ_FX): continue
    d=pd.Timestamp(ts_e).date()
    if cuenta.get(d,0)>=3: continue
    sl=r.sweep-U if r.largo else r.sweep+U; tp=r.r_hi if r.largo else r.r_lo
    rg=abs(e-sl);pr=abs(tp-e)
    if rg<=0 or pr<=0 or pr/rg<1.5: continue
    if not ((e>sl and tp>e) if r.largo else (e<sl and tp<e)): continue
    i2=min(it+48*60,len(T));a_,b_=H[it:i2],L[it:i2]
    gsl,gtp=((b_<=sl,a_>=tp) if r.largo else (a_>=sl,b_<=tp))
    isl=int(np.argmax(gsl)) if gsl.any() else 10**9
    itp=int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl==10**9 and itp==10**9: sal,mot,f=Cc[i2-1],"tiempo",(i2-it)-1
    elif isl<=itp: sal,mot,f=sl,"SL",isl
    else: sal,mot,f=tp,"TP",itp
    gan=(sal-e) if r.largo else (e-sal); k=int(r.k)
    puro.append(dict(ts=ts_e,largo=bool(r.largo),motivo=mot,
        v1i=INI[k-1],v1f=FIN[k-1],v2i=INI[k],v2f=FIN[k],v3i=INI[k+1],v3f=FIN[k+1],
        v1l=r.r_lo,v1h=r.r_hi,A=r.sweep,v2ext=r.v2_hi if r.largo else r.v2_lo,
        entrada=e,sl=sl,tp=tp,rr=pr/rg,riesgo=rg/U,bruto=gan/rg))
    cuenta[d]=cuenta.get(d,0)+1; libre=T[min(it+f,len(T)-1)]
P=pd.DataFrame(puro); P["ts"]=pd.to_datetime(P.ts)

# ---------- FIB ----------
cfgF=dict(fib=0.50,min_leg=0.20,killzone=True,min_rr=1.5,max_rr=15.0,
          min_riesgo_u=3.0,buffer=1.0,tope_dia=3,max_horas=48)
sF=setups(velas_ref(m1,24,1))
F=ejecuta_fib(sF,m5,m1,cfgF,U,1.2,KZ_FX); F["ts"]=pd.to_datetime(F.ts)

for nom,df in (("CRT PURO (H4)",P),("FIBONACCI (D1 + fib 50% M5)",F)):
    tot=len(df); d25=df[df.ts>="2025-01-01"]; d24h=df[df.ts>="2024-07-01"]
    print(f"{nom:32s} total {tot:>4}  |  desde 2025 {len(d25):>3}  |  desde jul-2024 {len(d24h):>3}")
json.dump({"ok":1},open("/dev/null","w"))
P.to_pickle("/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/P.pkl")
F.to_pickle("/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/F.pkl")
print("\nCRT PURO desde 2025:")
for r in P[P.ts>="2025-01-01"].itertuples():
    print(f"   {mad(r.ts):%d/%m/%Y %H:%M}  {'COMPRA' if r.largo else 'VENTA':6s}  {r.motivo:6s} {r.bruto:+.2f}R")
