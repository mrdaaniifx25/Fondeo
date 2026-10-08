"""¿Aporta algo exigir que H1 acompañe a H4?  Aportacion del usuario.

PREDICCION ESCRITA ANTES DE CORRER: no aporta. Reducira las operaciones a la
mitad y la ventaja por operacion se quedara donde esta. Todos los filtros de
alineacion probados hasta ahora han salido planos.

Especificacion, de las respuestas del usuario:
  estructura en H4 · objetivo = extremo opuesto de la vela base
  stop pegado a la mecha del barrido · entrada al cierre de la vela
  horizonte 10 velas, sin resolver -> cerrar a mercado
"""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS=[("EURUSD","data/eurusd_m1.parquet",0.0001,1.2),("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.5),
     ("USDJPY","data/usdjpy_m1.parquet",0.01,1.3),("NAS100","data/nsxusd_m1.parquet",1.0,1.5),
     ("SPX500","data/spxusd_m1.parquet",1.0,0.6),
     ("XAUUSD","data/xauusd_m1.parquet",0.01,35.0),("GRXEUR","data/grxeur_m1.parquet",1.0,2.0)]
TF, HZ = 4, 10
rng=np.random.default_rng(20260827)

def ee_bloq(x,largo=20,reps=3000):
    n=len(x)
    if n<largo*3: return x.std(ddof=1)/np.sqrt(n)
    nb=int(np.ceil(n/largo)); ini=rng.integers(0,n-largo+1,size=(reps,nb))
    idx=(ini[:,:,None]+np.arange(largo)[None,None,:]).reshape(reps,-1)[:,:n]
    return float(x[idx].mean(axis=1).std(ddof=1))

def h1_alineado(m1, fin_h4, alcista):
    """En el momento en que cierra la vela de H4, ¿hay un rango vivo de H1 en la
    misma direccion? Se usa la ULTIMA vela de H1 cerrada, nunca la siguiente."""
    r1=velas_ref(m1,1,ancla_ny=1)
    h,l,o,c=(r1[x].to_numpy() for x in ("high","low","open","close"))
    ph,pl,po,pc=(np.roll(v,1) for v in (h,l,o,c))
    ph[0]=pl[0]=po[0]=pc[0]=np.nan
    ca,cb=np.maximum(po,pc),np.minimum(po,pc)
    dentro=(c>=cb)&(c<=ca)
    lado=np.where((l<pl)&dentro,1,np.where((h>ph)&dentro,-1,0))
    fin1=r1["fin"].to_numpy()
    viva=pd.DataFrame({"ts":fin1,"lado":lado})
    viva=viva[viva.lado!=0]
    m=pd.merge_asof(pd.DataFrame({"ts":fin_h4}).sort_values("ts"),
                    viva.sort_values("ts"), on="ts", direction="backward")
    L=m["lado"].to_numpy()
    return np.where(np.isnan(L),0,L)==np.where(alcista,1,-1)

def corre(m1,ref,ie,ent,stp,obj,alc):
    t1=m1.ts.to_numpy();H=m1.high.to_numpy();L=m1.low.to_numpy();C1=m1.close.to_numpy()
    fin=ref["fin"].to_numpy(); barras=int(HZ*TF*60)
    R=np.full(len(ent),np.nan); mot=np.array([""]*len(ent),dtype=object)
    for k in range(len(ent)):
        j0=int(np.searchsorted(t1,fin[ie[k]],side="right")); j1=min(j0+barras,len(t1))
        if j0>=len(t1): continue
        hh,ll=H[j0:j1],L[j0:j1]
        if alc[k]: ga,gb=hh>=obj[k],ll<=stp[k]
        else:      ga,gb=ll<=obj[k],hh>=stp[k]
        ia=int(np.argmax(ga)) if ga.any() else 10**9
        ib=int(np.argmax(gb)) if gb.any() else 10**9
        rr=abs(obj[k]-ent[k])/abs(ent[k]-stp[k])
        if ia==10**9 and ib==10**9:
            sal=C1[j1-1]
            R[k]=((sal-ent[k]) if alc[k] else (ent[k]-sal))/abs(ent[k]-stp[k]); mot[k]="tiempo"
        elif ib<=ia: R[k]=-1.0; mot[k]="SL"
        else: R[k]=rr; mot[k]="TP"
    return R,mot

tot=[]
for nom,ruta,u,co in INS:
    m1=pd.read_parquet(ruta); m1["ts"]=pd.to_datetime(m1["ts"])
    m1=m1.sort_values("ts").reset_index(drop=True)
    ref=velas_ref(m1,TF,ancla_ny=1)
    h,l=(ref[x].to_numpy() for x in ("high","low"))
    s=LM.secuencias(ref,usar_cuerpo=False); s=s[s.k==1].copy()
    ib=s.i_base.to_numpy().astype(int); ie=s.i_ent.to_numpy().astype(int)
    ent=s.entrada.to_numpy(); alc=s.alcista.to_numpy().astype(bool)
    obj=np.where(alc,h[ib],l[ib]); stp=np.where(alc,l[ie],h[ie])
    riesgo=np.abs(ent-stp)/u
    ok=np.isfinite(riesgo)&(riesgo>0)&np.isfinite(obj)
    ie,ent,stp,obj,alc,riesgo=ie[ok],ent[ok],stp[ok],obj[ok],alc[ok],riesgo[ok]
    ali=h1_alineado(m1, ref["fin"].to_numpy()[ie], alc)
    R,mot=corre(m1,ref,ie,ent,stp,obj,alc)
    d=pd.DataFrame(dict(R=R,mot=mot,riesgo=riesgo,ali=ali)).dropna(subset=["R"])
    d["neto"]=d.R-co/d.riesgo
    tot.append(d.assign(ins=nom))
D=pd.concat(tot,ignore_index=True)

print("="*104)
print("¿APORTA EXIGIR QUE H1 ACOMPAÑE A H4?   siete instrumentos, stop en la mecha, H4")
print("="*104)
print(f"{'grupo':22s} {'n':>7s} {'%TP':>7s} {'R:R':>6s} {'R BRUTA':>9s} {'IC95 bruta':>19s} {'R NETA':>9s}")
print("-"*104)
for nom,g in (("H1 acompaña",D[D.ali]),("H1 NO acompaña",D[~D.ali]),("todas, sin filtro",D)):
    x=g.R.to_numpy(); ee=ee_bloq(x)
    print(f"{nom:22s} {len(g):>7,} {100*(g.mot=='TP').mean():>6.1f}% "
          f"{'':>6s} {x.mean():>+9.3f} [{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}] "
          f"{g.neto.mean():>+9.3f}")
a=D[D.ali].R.to_numpy(); b=D[~D.ali].R.to_numpy()
dif=a.mean()-b.mean(); ee=np.sqrt(ee_bloq(a)**2+ee_bloq(b)**2)
print("-"*104)
print(f"  diferencia acompaña − no acompaña: {dif:+.4f} R   z {dif/ee:+.2f}   "
      f"{'aporta' if abs(dif/ee)>2 else 'NO aporta'}")
print(f"  el filtro se queda con el {100*D.ali.mean():.0f} % de las operaciones")
print("\n  por instrumento (neta, con y sin el filtro):")
for ins,g in D.groupby("ins"):
    print(f"    {ins:8s} con filtro {g[g.ali].neto.mean():>+7.3f} (n={g.ali.sum():>5,})   "
          f"sin filtro {g.neto.mean():>+7.3f} (n={len(g):>5,})")
D.to_csv("data/h4_h1.csv", index=False)
