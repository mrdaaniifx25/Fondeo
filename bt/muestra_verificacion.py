"""Muestra estratificada para revision manual, con motivos de descarte."""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd, json
from crt_canonico import velas_ref, en_kz, KZ_FX
from crt_fib import setups

m1=pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
m5=m1.set_index("ts").resample("5min",label="left",closed="left").agg(
   open=("open","first"),high=("high","max"),low=("low","min"),close=("close","last")).dropna().reset_index()
U,C=0.0001,1.2
FIB,MINLEG,BUF=0.50,0.20,1.0
MINRR,MAXRR,MINRT,MINRR_=1.5,15.0,3.0,0.05
ref=velas_ref(m1,24,1); s=setups(ref)

T5=m5.ts.values;H5=m5.high.values;L5=m5.low.values;O5=m5.open.values
T=m1.ts.values;H=m1.high.values;L=m1.low.values;Cc=m1.close.values
ops=[];desc=[];libre=np.datetime64("1970-01-01");cuenta={}
for r in s.itertuples():
    i0=int(np.searchsorted(T5,np.datetime64(pd.Timestamp(r.ini3))))
    i1=int(np.searchsorted(T5,np.datetime64(pd.Timestamp(r.fin3))))+1
    if i0>=len(T5) or i1<=i0: desc.append((r,"sin datos M5")); continue
    if np.datetime64(pd.Timestamp(r.ini3))<libre: desc.append((r,"operacion anterior aun abierta")); continue
    A=r.A;B=None;hecho=False;motivo="el precio nunca volvio al nivel del 50%"
    for j in range(i0,min(i1,len(T5))):
        if B is not None:
            leg=(B-A) if r.largo else (A-B)
            if leg< MINLEG*r.rango:
                motivo="el rebote no llego al 20% del rango"
            else:
                niv=B-FIB*leg if r.largo else B+FIB*leg
                toca=(L5[j]<=niv) if r.largo else (H5[j]>=niv)
                if toca:
                    e=min(niv,O5[j]) if r.largo else max(niv,O5[j])
                    ts_e=T5[j]
                    if not en_kz(ts_e,KZ_FX):
                        motivo="toco el nivel fuera de killzone"
                        B=max(B,H5[j]) if r.largo else min(B,L5[j]); continue
                    dia=pd.Timestamp(ts_e).date()
                    if cuenta.get(dia,0)>=3:
                        motivo="ya habia 3 operaciones ese dia"
                        B=max(B,H5[j]) if r.largo else min(B,L5[j]); continue
                    sl=A-BUF*U if r.largo else A+BUF*U
                    tp=r.r_hi if r.largo else r.r_lo
                    rg=abs(e-sl);pr=abs(tp-e)
                    if rg<max(MINRT*U,MINRR_*r.rango): motivo="stop demasiado pegado";hecho=True;break
                    if pr<=0 or not (MINRR<=pr/rg<=MAXRR): motivo=f"R:R fuera de rango ({pr/rg:.1f})";hecho=True;break
                    if not ((e>sl and tp>e) if r.largo else (e<sl and tp<e)):
                        motivo="hueco: la entrada quedo al otro lado del stop";hecho=True;break
                    k0=int(np.searchsorted(T,np.datetime64(pd.Timestamp(ts_e))));k1=min(k0+48*60,len(T))
                    a_,b_=H[k0:k1],L[k0:k1]
                    gsl,gtp=((b_<=sl,a_>=tp) if r.largo else (a_>=sl,b_<=tp))
                    isl=int(np.argmax(gsl)) if gsl.any() else 10**9
                    itp=int(np.argmax(gtp)) if gtp.any() else 10**9
                    if isl==10**9 and itp==10**9: sal,mot,f=Cc[k1-1],"tiempo",(k1-k0)-1
                    elif isl<=itp: sal,mot,f=sl,"SL",isl
                    else: sal,mot,f=tp,"TP",itp
                    gan=(sal-e) if r.largo else (e-sal)
                    ops.append(dict(ts=ts_e,largo=bool(r.largo),motivo=mot,
                        v1l=r.r_lo,v1h=r.r_hi,A=A,B=B,entrada=e,sl=sl,tp=tp,
                        rr=pr/rg,riesgo_p=rg/U,bruto=gan/rg,ini3=r.ini3))
                    cuenta[dia]=cuenta.get(dia,0)+1
                    libre=T[min(k0+f,len(T)-1)];hecho=True;break
        v=H5[j] if r.largo else L5[j]
        B=v if B is None else (max(B,v) if r.largo else min(B,v))
    if not hecho: desc.append((r,motivo))

o=pd.DataFrame(ops); o["ts"]=pd.to_datetime(o.ts)
o["anio"]=o.ts.dt.year
print(f"operaciones {len(o)} | setups descartados {len(desc)}\n")
print("Motivos de descarte:")
md=pd.Series([d[1] for d in desc]).value_counts()
print(md.to_string(),"\n")

# muestra estratificada
rng=np.random.default_rng(4)
sel=[]
gan=o[o.motivo=="TP"]; per=o[o.motivo=="SL"]
for grupo,n,etq in ((gan,5,"GANADORA"),(per,5,"PERDEDORA")):
    idx=rng.choice(grupo.index,size=min(n,len(grupo)),replace=False)
    for i in idx: sel.append((o.loc[i],etq))
cortos=o[~o.largo]
extra=[i for i in rng.choice(cortos.index,size=min(3,len(cortos)),replace=False)
       if i not in [x[0].name for x in sel]]
for i in extra[:2]: sel.append((o.loc[i],"CORTO"))
sel.sort(key=lambda x: x[0].ts)

filas=[]
for r,etq in sel:
    tm=pd.Timestamp(r.ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    d3=pd.Timestamp(r.ini3).tz_localize("UTC").tz_convert("Europe/Madrid")
    filas.append(dict(etiqueta=etq, fecha=f"{tm:%d/%m/%Y}", hora=f"{tm:%H:%M}",
        dir="COMPRA" if r.largo else "VENTA", v1l=round(r.v1l,5), v1h=round(r.v1h,5),
        A=round(r.A,5), B=round(r.B,5), entrada=round(r.entrada,5),
        sl=round(r.sl,5), tp=round(r.tp,5), rr=round(r.rr,2),
        riesgo=round(r.riesgo_p,1), res=r.motivo, R=round(r.bruto,2),
        v3=f"{d3:%d/%m %H:%M}"))

# tres descartes representativos
dsc=[]
for mot in md.index[:3]:
    c=[d for d in desc if d[1]==mot]
    if not c: continue
    r=c[len(c)//2][0]
    d3=pd.Timestamp(r.ini3).tz_localize("UTC").tz_convert("Europe/Madrid")
    dsc.append(dict(motivo=mot, v3=f"{d3:%d/%m/%Y %H:%M}",
        dir="alcista" if r.largo else "bajista", v1l=round(r.r_lo,5),
        v1h=round(r.r_hi,5), A=round(r.A,5)))
json.dump(dict(ops=filas,desc=dsc,motivos=md.to_dict(),
               total_ops=len(o), total_desc=len(desc)),
          open("/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/muestra.json","w"), indent=1)
for f in filas: print(f"{f['etiqueta']:10s} {f['fecha']} {f['hora']} {f['dir']:6s} {f['res']:6s} {f['R']:+.2f}R")
print(f"\ndescartes de ejemplo: {len(dsc)}")
