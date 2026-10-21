"""¿Que distingue un rango CRT que se completa de uno que no?

No anade indicadores: mide propiedades del PROPIO setup.

  1 tamano del rango en unidades de ATR
  2 profundidad del barrido mas alla del extremo
  3 posicion del cierre dentro del rango tras barrer
  4 hora del barrido

H4, cinco instrumentos, 2020-2026. Declarado antes de mirar: son 4
dimensiones = 4 comparaciones; lo que aparezca necesita nulo.

  python3 bt/crt_anatomia.py
"""
import numpy as np, pandas as pd
TF = 240
INSTR = {"EURUSD":("data/eurusd_m1.parquet",1e-4,1.43),
         "GBPUSD":("data/gbpusd_m1.parquet",1e-4,1.60),
         "USDJPY":("data/usdjpy_m1.parquet",1e-2,1.50),
         "NAS100":("data/nsxusd_m1.parquet",1e-0,1.50),
         "SPX500":("data/spxusd_m1.parquet",1e-0,0.60)}

filas=[]
for par,(ruta,U,COSTE) in INSTR.items():
    M=pd.read_parquet(ruta); M["ts"]=pd.to_datetime(M["ts"])
    M=M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    B=M.set_index("ts").resample(f"{TF}min",label="left",closed="left").agg(
        o=("open","first"),h=("high","max"),l=("low","min"),
        c=("close","last"),n=("close","size")).dropna()
    B=B[B.n>=TF*0.3]
    tr=pd.concat([B.h-B.l,(B.h-B.c.shift()).abs(),(B.l-B.c.shift()).abs()],axis=1).max(axis=1)
    atr=tr.rolling(20).mean().to_numpy()
    h,l,c,o=B.h.to_numpy(),B.l.to_numpy(),B.c.to_numpy(),B.o.to_numpy()
    ti=B.index.to_numpy()
    mh,ml,mt=M.high.to_numpy(),M.low.to_numpy(),M.ts.to_numpy()
    for i in range(21,len(B)-1):
        if np.isnan(atr[i]) or atr[i]<=0: continue
        rng=h[i-1]-l[i-1]
        if rng<=0: continue
        if   h[i]>h[i-1] and c[i]<h[i-1]: lado,ext,obj=-1,h[i],l[i-1]
        elif l[i]<l[i-1] and c[i]>l[i-1]: lado,ext,obj=+1,l[i],h[i-1]
        else: continue
        ent=c[i]; rgo=abs(ent-ext)
        if rgo<2*U or (obj-ent)*lado<=0: continue
        j0=int(np.searchsorted(mt,ti[i]+np.timedelta64(TF,"m")))
        j1=min(j0+TF*12,len(mt))
        if j1<=j0+5: continue
        hh,ll=mh[j0:j1],ml[j0:j1]
        a=np.flatnonzero(hh>=obj) if lado>0 else np.flatnonzero(ll<=obj)
        b=np.flatnonzero(ll<=ext) if lado>0 else np.flatnonzero(hh>=ext)
        ia=int(a[0]) if len(a) else 10**9
        ib=int(b[0]) if len(b) else 10**9
        if ia==ib==10**9: continue
        rr=abs(obj-ent)/rgo
        R=(rr if ia<ib else -1.0)
        filas.append(dict(par=par, lado=lado, R=R, neta=R-COSTE*U/rgo,
            tam=rng/atr[i],                                  # 1 tamano
            prof=abs(ext-(h[i-1] if lado<0 else l[i-1]))/rng, # 2 profundidad
            cierre=(c[i]-l[i-1])/rng if lado>0 else (h[i-1]-c[i])/rng,  # 3 cierre
            hora=pd.Timestamp(ti[i]).hour, rr=rr))
D=pd.DataFrame(filas); D.to_csv("data/crt_anatomia.csv",index=False)
z=lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v)>5 else np.nan
print(f"=== ANATOMIA DEL CRT EN H4 · {len(D)} setups, 5 instrumentos ===\n")
print(f"  R bruta global {D.R.mean():+.4f} (z {z(D.R):+.2f})  ·  "
      f"neta {D.neta.mean():+.4f} (z {z(D.neta):+.2f})\n")
for col,et,cortes in (("tam","1 · TAMANO del rango (x ATR)",[0,.6,.9,1.3,99]),
                      ("prof","2 · PROFUNDIDAD del barrido (x rango)",[0,.05,.12,.25,99]),
                      ("cierre","3 · CIERRE dentro del rango (0=barrido, 1=opuesto)",[0,.3,.5,.7,1.01]),
                      ("hora","4 · HORA del barrido (UTC)",[-1,3,7,11,15,19,24])):
    D["g"]=pd.cut(D[col],cortes)
    print(f"  {et}")
    print(f"    {'grupo':>16} {'n':>6} {'R:R':>6} {'BRUTA':>9} {'z':>7} {'NETA':>9}")
    for k,g in D.groupby("g",observed=True):
        print(f"    {str(k):>16} {len(g):>6} {g.rr.mean():>6.2f} {g.R.mean():>+9.4f} "
              f"{z(g.R):>+7.2f} {g.neta.mean():>+9.4f}")
    print()
