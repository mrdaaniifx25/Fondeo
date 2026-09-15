"""Las tres piezas que faltaban de la lectura del usuario."""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from math import sqrt, erf
from liquidez_sesiones import sesiones, niveles, pz, pf

U, COSTE, BUF = 0.0001, 1.2, 2.0
m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
ch = m1.set_index("ts").resample("15min",label="left",closed="left").agg(
     open=("open","first"),high=("high","max"),low=("low","min"),
     close=("close","last")).dropna().reset_index()
T=m1.ts.values; H=m1.high.values; L=m1.low.values; C=m1.close.values

ny=pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert("America/New_York").tz_localize(None)
m1n=m1.assign(ny=ny)
m1n["dia"]=m1n.ny.dt.date
d=m1n.groupby("dia").agg(hi=("high","max"),lo=("low","min"),fin=("ts","max"))
d["pdh"],d["pdl"]=d.hi.shift(1),d.lo.shift(1)
d=d.dropna()

chn=ch.assign(ny=pd.DatetimeIndex(ch.ts).tz_localize("UTC").tz_convert("America/New_York").tz_localize(None))
chn["dia"]=chn.ny.dt.date
chn=chn.merge(d[["pdh","pdl"]],left_on="dia",right_index=True,how="left")
tc=ch.ts.values; oc=ch.open.values; cc=ch.close.values; hc=ch.high.values; lc=ch.low.values

CAB=f"{'':44s} {'n':>5s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'%TP':>6s} {'RR':>5s} {'PF neto':>8s}"
def linea(nom,tr):
    if tr is None or len(tr)<3:
        print(f"{nom:44s} {0 if tr is None else len(tr):>5d}  (muestra insuficiente)"); return None
    z,p=pz(tr.bruto)
    print(f"{nom:44s} {len(tr):>5d} {tr.bruto.mean():>+9.4f} {z:>+6.2f} {p:>7.4f} "
          f"{(tr.motivo=='TP').mean()*100:>5.1f}% {tr.rr.mean():>5.2f} {pf(tr.R):>8.3f}")
    return tr.bruto.mean()

def resuelve(e, sl, tp, largo, i0, maxh=24):
    i1=min(i0+maxh*60,len(T))
    if i0>=len(T) or i1<=i0: return None
    a,b=H[i0:i1],L[i0:i1]
    gsl,gtp=((b<=sl,a>=tp) if largo else (a>=sl,b<=tp))
    isl=int(np.argmax(gsl)) if gsl.any() else 10**9
    itp=int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl==10**9 and itp==10**9: sal,mot,f=C[i1-1],"tiempo",(i1-i0)-1
    elif isl<=itp: sal,mot,f=sl,"SL",isl
    else: sal,mot,f=tp,"TP",itp
    gan=(sal-e) if largo else (e-sal)
    return sal,mot,f,gan

# ═══════════════════════════════════════════════════════════════════════════
print("="*104)
print("1 · PDH y PDL COMO OBJETIVO  ·  contra un nivel placebo a distancia parecida")
print("="*104)
ses=sesiones(m1); lv=niveles(ses,m1)
rng=np.random.default_rng(31)
def prueba_pdh(desplaza=0.0):
    out=[]; libre=np.datetime64("1970-01-01")
    for r in lv[lv.imuere<10**9].sort_values("muere").itertuples():
        tb=np.datetime64(pd.Timestamp(r.muere))
        if tb<libre: continue
        largo = not r.arriba
        j0=int(np.searchsorted(tc,tb))
        jj=None
        for j in range(j0,min(j0+8,len(tc))):
            if (cc[j]<r.px) if r.arriba else (cc[j]>r.px): jj=j; break
        if jj is None or jj+1>=len(tc): continue
        pdh,pdl=chn.pdh.values[jj],chn.pdl.values[jj]
        if np.isnan(pdh) or np.isnan(pdl): continue
        e=oc[jj+1]
        i0=int(np.searchsorted(T,np.datetime64(pd.Timestamp(tc[jj]))+np.timedelta64(15,"m")))
        if i0>=len(T): continue
        k0=int(np.searchsorted(T,tb))
        ext=H[k0:i0].max() if r.arriba else L[k0:i0].min()
        sl=ext+BUF*U if r.arriba else ext-BUF*U
        base = pdh if largo else pdl
        off = desplaza*U*(1 if rng.integers(0,2) else -1) if desplaza>0 else 0.0
        tp = base + off
        riesgo=abs(e-sl); premio=abs(tp-e)
        if riesgo<=0 or premio<=0: continue
        if not ((e>sl and tp>e) if largo else (e<sl and tp<e)): continue
        rr=premio/riesgo
        if rr<0.5 or rr>20 or riesgo<5*U: continue
        rs=resuelve(e,sl,tp,largo,i0)
        if rs is None: continue
        sal,mot,f,gan=rs
        out.append(dict(motivo=mot,rr=rr,riesgo_p=riesgo/U,bruto=gan/riesgo,
                        R=(gan/U-COSTE)/(riesgo/U)))
        libre=T[min(i0+f,len(T)-1)]
    return pd.DataFrame(out)
print(CAB)
a=linea("   objetivo en el PDH/PDL de verdad", prueba_pdh(0))
b=linea("   objetivo desplazado 15 pips (placebo)", prueba_pdh(15))
c=linea("   objetivo desplazado 30 pips (placebo)", prueba_pdh(30))

# ═══════════════════════════════════════════════════════════════════════════
print("\n"+"="*104)
print("2 · FVG DE VERDAD EN M15 como entrada tras el barrido de H4")
print("="*104)
from crt_canonico import velas_ref, senales, en_kz, KZ_FX
CFG=dict(entrada="v2",cierre_estricto=True,killzone=True,min_rr=1.5,
         buffer=1.0,tope_dia=3,max_horas=48)
ref=velas_ref(m1,4,1); sig=senales(ref,CFG)
Ho,Lo=hc,lc
def fvg_en(j, largo):
    """FVG con las tres velas M15 cerradas terminando en j-1."""
    if j<4: return None
    A_h,A_l = Ho[j-4],Lo[j-4]
    C_h,C_l = Ho[j-2],Lo[j-2]
    if largo and C_l>A_h: return (A_h,C_l)
    if (not largo) and C_h<A_l: return (C_h,A_l)
    return None
def prueba_fvg(donde):
    out=[]; libre=np.datetime64("1970-01-01")
    for r in sig.itertuples():
        j0=int(np.searchsorted(tc,np.datetime64(pd.Timestamp(r.ini3))))
        j1=int(np.searchsorted(tc,np.datetime64(pd.Timestamp(r.fin3))))+1
        if j0>=len(tc) or j1<=j0 or np.datetime64(pd.Timestamp(r.ini3))<libre: continue
        hecho=False
        for j in range(j0,min(j1,len(tc))):
            g=fvg_en(j,r.largo)
            if g is None: continue
            bajo,alto=g
            niv = (alto if donde=="cerca" else (bajo if donde=="lejos" else (alto+bajo)/2)) if r.largo \
                  else (bajo if donde=="cerca" else (alto if donde=="lejos" else (alto+bajo)/2))
            toca=(lc[j]<=niv) if r.largo else (hc[j]>=niv)
            if not toca: continue
            e=min(niv,oc[j]) if r.largo else max(niv,oc[j])
            ts_e=tc[j]
            if not en_kz(ts_e,KZ_FX): continue
            sl=r.sweep-1*U if r.largo else r.sweep+1*U
            tp=r.r_hi if r.largo else r.r_lo
            riesgo=abs(e-sl); premio=abs(tp-e)
            if riesgo<max(3*U,0.05*r.rango) or premio<=0: hecho=True; break
            rr=premio/riesgo
            if rr<1.5 or rr>15: hecho=True; break
            if not ((e>sl and tp>e) if r.largo else (e<sl and tp<e)): hecho=True; break
            i0=int(np.searchsorted(T,np.datetime64(pd.Timestamp(ts_e))))
            rs=resuelve(e,sl,tp,r.largo,i0,48)
            if rs is None: hecho=True; break
            sal,mot,f,gan=rs
            out.append(dict(motivo=mot,rr=rr,riesgo_p=riesgo/U,bruto=gan/riesgo,
                            R=(gan/U-COSTE)/(riesgo/U)))
            libre=T[min(i0+f,len(T)-1)]; hecho=True; break
    return pd.DataFrame(out)
print(CAB)
for w,nom in (("cerca","borde cercano"),("medio","50 % del hueco"),("lejos","borde lejano")):
    linea(f"   entrada en el {nom}", prueba_fvg(w))

# ═══════════════════════════════════════════════════════════════════════════
print("\n"+"="*104)
print("3 · TU LECTURA COMPLETA, capa a capa")
print("="*104)
# rango de Asia por dia de sesion
m1n["h"]=m1n.ny.dt.hour
asia=m1n[(m1n.h>=18)|(m1n.h<1)].copy()
asia["ds"]=(asia.ny+pd.Timedelta(hours=6)).dt.date
ar=asia.groupby("ds").agg(ahi=("high","max"),alo=("low","min"))
chn["ds"]=(chn.ny+pd.Timedelta(hours=6)).dt.date
chn=chn.merge(ar,left_on="ds",right_index=True,how="left")
ahi_v,alo_v=chn.ahi.values,chn.alo.values
pdh_v,pdl_v=chn.pdh.values,chn.pdl.values

# H1 previo por vela M15
m1n["id1"]=m1n.ny.dt.floor("1h")
h1=m1n.groupby("id1").agg(hi=("high","max"),lo=("low","min"),n=("ts","size"))
h1=h1[h1.n>=30].reset_index()
h1["p_hi"],h1["p_lo"]=h1.hi.shift(1),h1.lo.shift(1)
chn["id1"]=chn.ny.dt.floor("1h")
chn=chn.merge(h1[["id1","p_hi","p_lo"]],on="id1",how="left")
chn["r1hi"]=chn.groupby("id1").high.cummax(); chn["r1lo"]=chn.groupby("id1").low.cummin()
p1hi,p1lo=chn.p_hi.values,chn.p_lo.values
r1hi,r1lo=chn.r1hi.values,chn.r1lo.values

def stack(usaH1, usaKZ, usaFVG, usaPD, usaAsia, donde="lejos"):
    out=[]; libre=np.datetime64("1970-01-01")
    for r in sig.itertuples():
        j0=int(np.searchsorted(tc,np.datetime64(pd.Timestamp(r.ini3))))
        j1=int(np.searchsorted(tc,np.datetime64(pd.Timestamp(r.fin3))))+1
        if j0>=len(tc) or j1<=j0 or np.datetime64(pd.Timestamp(r.ini3))<libre: continue
        if usaPD:
            k=min(j0,len(tc)-1)
            ref_pd = pdl_v[k] if r.largo else pdh_v[k]
            if np.isnan(ref_pd) or abs(r.sweep-ref_pd) > 15*U: continue
        if usaAsia:
            k=min(j0,len(tc)-1)
            if np.isnan(ahi_v[k]) or not ((r.sweep<alo_v[k]) if r.largo else (r.sweep>ahi_v[k])): continue
        for j in range(j0,min(j1,len(tc))):
            if usaH1:
                ok1 = (r1lo[j]<p1lo[j] and cc[j]>p1lo[j]) if r.largo else (r1hi[j]>p1hi[j] and cc[j]<p1hi[j])
                if not ok1 or np.isnan(p1hi[j]): continue
            if usaKZ and not en_kz(tc[j],KZ_FX): continue
            if usaFVG:
                g=fvg_en(j,r.largo)
                if g is None: continue
                bajo,alto=g
                niv=(bajo if donde=="lejos" else alto) if r.largo else (alto if donde=="lejos" else bajo)
                if not ((lc[j]<=niv) if r.largo else (hc[j]>=niv)): continue
                e=min(niv,oc[j]) if r.largo else max(niv,oc[j])
            else:
                if j+1>=len(tc): continue
                e=oc[j+1]
            sl=r.sweep-1*U if r.largo else r.sweep+1*U
            tp=r.r_hi if r.largo else r.r_lo
            riesgo=abs(e-sl); premio=abs(tp-e)
            if riesgo<max(3*U,0.05*r.rango) or premio<=0: break
            rr=premio/riesgo
            if rr<1.5 or rr>15: break
            if not ((e>sl and tp>e) if r.largo else (e<sl and tp<e)): break
            i0=int(np.searchsorted(T,np.datetime64(pd.Timestamp(tc[j]))))
            rs=resuelve(e,sl,tp,r.largo,i0,48)
            if rs is None: break
            sal,mot,f,gan=rs
            out.append(dict(motivo=mot,rr=rr,riesgo_p=riesgo/U,bruto=gan/riesgo,
                            R=(gan/U-COSTE)/(riesgo/U)))
            libre=T[min(i0+f,len(T)-1)]; break
    return pd.DataFrame(out)

print(CAB)
linea("   1. solo turtle soup H4",                     stack(0,0,0,0,0))
linea("   2. + turtle soup H1",                        stack(1,0,0,0,0))
linea("   3. + killzone",                              stack(1,1,0,0,0))
linea("   4. + entrada en FVG de M15 (borde lejano)",  stack(1,1,1,0,0))
linea("   5. + el barrido toca PDH/PDL",               stack(1,1,1,1,0))
linea("   6. + Londres barrio el rango de Asia",       stack(1,1,1,1,1))

print("\n"+"="*104)
print("VERIFICACION: si la killzone resta, ¿que pasa FUERA de ella?")
print("="*104)
def stack_kz(dentro):
    out=[]; libre=np.datetime64("1970-01-01")
    for r in sig.itertuples():
        j0=int(np.searchsorted(tc,np.datetime64(pd.Timestamp(r.ini3))))
        j1=int(np.searchsorted(tc,np.datetime64(pd.Timestamp(r.fin3))))+1
        if j0>=len(tc) or j1<=j0 or np.datetime64(pd.Timestamp(r.ini3))<libre: continue
        for j in range(j0,min(j1,len(tc))):
            ok1=(r1lo[j]<p1lo[j] and cc[j]>p1lo[j]) if r.largo else (r1hi[j]>p1hi[j] and cc[j]<p1hi[j])
            if not ok1 or np.isnan(p1hi[j]): continue
            if en_kz(tc[j],KZ_FX) != dentro: continue
            if j+1>=len(tc): continue
            e=oc[j+1]
            sl=r.sweep-1*U if r.largo else r.sweep+1*U
            tp=r.r_hi if r.largo else r.r_lo
            riesgo=abs(e-sl); premio=abs(tp-e)
            if riesgo<max(3*U,0.05*r.rango) or premio<=0: break
            rr=premio/riesgo
            if rr<1.5 or rr>15: break
            if not ((e>sl and tp>e) if r.largo else (e<sl and tp<e)): break
            i0=int(np.searchsorted(T,np.datetime64(pd.Timestamp(tc[j]))))
            rs=resuelve(e,sl,tp,r.largo,i0,48)
            if rs is None: break
            sal,mot,f,gan=rs
            out.append(dict(motivo=mot,rr=rr,riesgo_p=riesgo/U,bruto=gan/riesgo,
                            R=(gan/U-COSTE)/(riesgo/U)))
            libre=T[min(i0+f,len(T)-1)]; break
    return pd.DataFrame(out)
print(CAB)
A=stack_kz(True); B=stack_kz(False)
linea("   DENTRO de killzone", A)
linea("   FUERA de killzone",  B)
if A is not None and B is not None and len(A)>3 and len(B)>3:
    dif=A.bruto.mean()-B.bruto.mean()
    se=sqrt(A.bruto.var(ddof=1)/len(A)+B.bruto.var(ddof=1)/len(B))
    z=dif/se; p=2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
    print(f"\n   diferencia dentro menos fuera: {dif:+.4f} R/op | z {z:+.2f} | p {p:.4f}")
