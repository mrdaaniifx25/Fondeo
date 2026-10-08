"""Muestra de CRT PURO: sin Fibonacci, exactamente como lo describe la guia.
   Vela 1 rango | Vela 2 barre y cierra dentro | orden stop en el extremo de la
   Vela 2 durante la Vela 3 | SL tras la mecha | TP en el extremo opuesto."""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd, json
from crt_canonico import velas_ref, senales, en_kz, KZ_FX

m1=pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
U,C=0.0001,1.2
CFG=dict(entrada="v2", cierre_estricto=True, killzone=True, min_rr=1.5,
         buffer=1.0, tope_dia=3, max_horas=48)
ref=velas_ref(m1,4,1)          # rejilla H4 anclada a la 01:00 de Nueva York
sig=senales(ref,CFG)
print(f"setups de CRT puro detectados en EURUSD: {len(sig)}")

T=m1.ts.values;H=m1.high.values;L=m1.low.values;Cc=m1.close.values;O=m1.open.values
ops=[];libre=np.datetime64("1970-01-01");cuenta={}
for r in sig.itertuples():
    i0=int(np.searchsorted(T,np.datetime64(pd.Timestamp(r.ini3))))
    i1=int(np.searchsorted(T,np.datetime64(pd.Timestamp(r.fin3))))+1
    if i0>=len(T) or i1<=i0 or np.datetime64(pd.Timestamp(r.ini3))<libre: continue
    niv = r.v2_hi if r.largo else r.v2_lo          # el disparo: extremo de la Vela 2
    g=(H[i0:i1]>=niv) if r.largo else (L[i0:i1]<=niv)
    if not g.any(): continue
    it=i0+int(np.argmax(g))
    e=max(niv,O[it]) if r.largo else min(niv,O[it])
    ts_e=T[it]
    if not en_kz(ts_e,KZ_FX): continue
    dia=pd.Timestamp(ts_e).date()
    if cuenta.get(dia,0)>=3: continue
    sl=r.sweep-U if r.largo else r.sweep+U
    tp=r.r_hi if r.largo else r.r_lo
    rg=abs(e-sl); pr=abs(tp-e)
    if rg<=0 or pr<=0 or pr/rg<1.5: continue
    if not ((e>sl and tp>e) if r.largo else (e<sl and tp<e)): continue
    i2=min(it+48*60,len(T)); a_,b_=H[it:i2],L[it:i2]
    gsl,gtp=((b_<=sl,a_>=tp) if r.largo else (a_>=sl,b_<=tp))
    isl=int(np.argmax(gsl)) if gsl.any() else 10**9
    itp=int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl==10**9 and itp==10**9: sal,mot,f=Cc[i2-1],"tiempo",(i2-it)-1
    elif isl<=itp: sal,mot,f=sl,"SL",isl
    else: sal,mot,f=tp,"TP",itp
    gan=(sal-e) if r.largo else (e-sal)
    ops.append(dict(ts=ts_e,largo=bool(r.largo),motivo=mot,v1l=r.r_lo,v1h=r.r_hi,
        A=r.sweep,v2hi=r.v2_hi,v2lo=r.v2_lo,entrada=e,sl=sl,tp=tp,rr=pr/rg,
        riesgo=rg/U,bruto=gan/rg,ini3=r.ini3))
    cuenta[dia]=cuenta.get(dia,0)+1
    libre=T[min(it+f,len(T)-1)]

o=pd.DataFrame(ops); o["ts"]=pd.to_datetime(o.ts)
print(f"operaciones ejecutadas: {len(o)}  |  aciertos {(o.motivo=='TP').mean()*100:.0f}%")
print(f"ventaja bruta {o.bruto.mean():+.4f} R/op\n")

rng=np.random.default_rng(9); sel=[]
gan_=o[o.motivo=="TP"]; per_=o[o.motivo=="SL"]
for grupo,n in ((gan_,5),(per_,5)):
    if len(grupo): sel += list(rng.choice(grupo.index,size=min(n,len(grupo)),replace=False))
resto=[i for i in o.index if i not in sel]
sel += list(rng.choice(resto,size=min(2,len(resto)),replace=False))
sub=o.loc[sorted(sel)].sort_values("ts")

filas=[]
for r in sub.itertuples():
    tm=pd.Timestamp(r.ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    d3=pd.Timestamp(r.ini3).tz_localize("UTC").tz_convert("Europe/Madrid")
    filas.append(dict(fecha=f"{tm:%d/%m/%Y}",hora=f"{tm:%H:%M}",
        dir="COMPRA" if r.largo else "VENTA",v1l=round(r.v1l,5),v1h=round(r.v1h,5),
        A=round(r.A,5),v2ext=round(r.v2hi if r.largo else r.v2lo,5),
        entrada=round(r.entrada,5),sl=round(r.sl,5),tp=round(r.tp,5),
        rr=round(r.rr,2),riesgo=round(r.riesgo,1),res=r.motivo,R=round(r.bruto,2),
        v3=f"{d3:%d/%m %H:%M}"))
json.dump(filas,open("/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/puro.json","w"),indent=1)
for f in filas: print(f"  {f['fecha']} {f['hora']} {f['dir']:6s} {f['res']:6s} {f['R']:+.2f}R  entrada {f['entrada']}")
