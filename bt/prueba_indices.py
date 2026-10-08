"""P1/P2 del pre-registro: CRT+DOL con parametros CONGELADOS desde EURUSD.

Unica adaptacion admitida y declarada: la unidad pasa de pip a punto del indice.
Ningun otro parametro se toca.
"""
import numpy as np, pandas as pd
from math import sqrt, erf

# ── parametros congelados desde EURUSD (pre-registro seccion 2) ─────────────
ANCLA_H4   = 1
USAR_OB    = True
USAR_H1    = True
DOL_K      = 0.5
TP_R       = 3.0
SL_BUFFER  = 1.0        # 1 unidad
HORA_INI   = 6.5
HORA_FIN   = 16.0
UNA_RANGO  = True
MAX_ESPERA = 16
MAX_HORAS  = 168

def niveles_dol(m1, unit):
    ts = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York")
    dia = pd.Index((ts+pd.Timedelta(hours=7)).date)
    d = m1.copy(); d["k"]=dia
    per={}
    per["D"]=d.groupby("k").agg(high=("high","max"),low=("low","min"),fin=("ts","max"))
    d["ks"]=pd.PeriodIndex(pd.to_datetime(dia),freq="W")
    per["W"]=d.groupby("ks").agg(high=("high","max"),low=("low","min"),fin=("ts","max"))
    d["km"]=pd.PeriodIndex(pd.to_datetime(dia),freq="M")
    per["M"]=d.groupby("km").agg(high=("high","max"),low=("low","min"),fin=("ts","max"))
    filas=[]
    for marco,g in per.items():
        g=g.sort_values("fin").reset_index(drop=True)
        for i in range(len(g)-1):
            nace=g.fin.iloc[i]+pd.Timedelta(minutes=1)
            filas.append((g.high.iloc[i],nace,True,marco))
            filas.append((g.low.iloc[i],nace,False,marco))
    lv=pd.DataFrame(filas,columns=["px","nace","arriba","marco"]).sort_values("nace")
    t=m1["ts"].to_numpy(); H=m1["high"].to_numpy(); L=m1["low"].to_numpy()
    muere=[]
    for px,nace,arriba,_ in lv.itertuples(index=False):
        i0=int(np.searchsorted(t,np.datetime64(nace)))
        if i0>=len(t): muere.append(pd.Timestamp("2100-01-01")); continue
        g=(H[i0:]>=px) if arriba else (L[i0:]<=px)
        muere.append(pd.Timestamp(t[i0+int(np.argmax(g))]) if g.any() else pd.Timestamp("2100-01-01"))
    lv["muere"]=muere
    return lv.reset_index(drop=True)

def prepara(m1, unit):
    ch = m1.set_index("ts").resample("15min",label="left",closed="left").agg(
        open=("open","first"),high=("high","max"),low=("low","min"),
        close=("close","last")).dropna().reset_index()
    org=pd.Timestamp("2020-01-01")+pd.Timedelta(hours=ANCLA_H4)
    h4=m1.set_index("ts").resample("4h",origin=org,label="left",closed="left").agg(
        high=("high","max"),low=("low","min")).dropna().reset_index()
    h4["r_hi"],h4["r_lo"]=h4.high.shift(1),h4.low.shift(1)
    ch["h4_id"]=(ch["ts"]-pd.Timedelta(hours=ANCLA_H4)).dt.floor("4h")+pd.Timedelta(hours=ANCLA_H4)
    ch=ch.merge(h4[["ts","r_hi","r_lo"]].rename(columns={"ts":"h4_id"}),on="h4_id",how="left")
    h1=m1.set_index("ts").resample("1h",label="left",closed="left").agg(
        high=("high","max"),low=("low","min")).dropna().reset_index()
    h1["p_hi"],h1["p_lo"]=h1.high.shift(1),h1.low.shift(1)
    ch["h1_id"]=ch["ts"].dt.floor("1h")
    ch=ch.merge(h1[["ts","p_hi","p_lo"]].rename(columns={"ts":"h1_id"}),on="h1_id",how="left")
    for pref,key in (("h4","h4_id"),("h1","h1_id")):
        ch[f"{pref}_run_hi"]=ch.groupby(key)["high"].cummax()
        ch[f"{pref}_run_lo"]=ch.groupby(key)["low"].cummin()
    # mapa DOL
    lv=niveles_dol(m1,unit)
    n=len(ch); up=np.full(n,np.nan); dn=np.full(n,np.nan)
    ev=[]
    for i,r in enumerate(lv.itertuples(index=False)):
        ev.append((r.nace,1,i)); ev.append((r.muere,-1,i))
    ev.sort(key=lambda x:x[0])
    px=lv.px.to_numpy(); arr=lv.arriba.to_numpy()
    vivos=set(); j=0; tsv=ch["ts"].to_numpy(); cl=ch["close"].to_numpy()
    for i in range(n):
        while j<len(ev) and np.datetime64(ev[j][0])<=tsv[i]:
            _,tp_,k=ev[j]
            vivos.add(k) if tp_==1 else vivos.discard(k)
            j+=1
        mu=md=None
        for k in vivos:
            if arr[k] and px[k]>cl[i]:
                if mu is None or px[k]<px[mu]: mu=k
            elif (not arr[k]) and px[k]<cl[i]:
                if md is None or px[k]>px[md]: md=k
        if mu is not None: up[i]=px[mu]
        if md is not None: dn[i]=px[md]
    ch["dol_up"],ch["dol_dn"]=up,dn
    return ch

def senales(ch, unit):
    op,hi,lo,cl=(ch[c].to_numpy() for c in ("open","high","low","close"))
    rhi,rlo=ch["r_hi"].to_numpy(),ch["r_lo"].to_numpy()
    p_hi,p_lo=ch["p_hi"].to_numpy(),ch["p_lo"].to_numpy()
    h4hi,h4lo=ch["h4_run_hi"].to_numpy(),ch["h4_run_lo"].to_numpy()
    h1hi,h1lo=ch["h1_run_hi"].to_numpy(),ch["h1_run_lo"].to_numpy()
    h4id=ch["h4_id"].to_numpy(); dup,ddn=ch["dol_up"].to_numpy(),ch["dol_dn"].to_numpy()
    ts=ch["ts"].to_numpy(); idx=pd.DatetimeIndex(ch["ts"])
    horas=idx.hour+idx.minute/60.0
    rb=np.full(len(ch),np.nan); rl=np.full(len(ch),np.nan); ub=un=np.nan
    for i in range(len(ch)):
        rb[i],rl[i]=ub,un
        if cl[i]<op[i]: ub=hi[i]
        elif cl[i]>op[i]: un=lo[i]
    ob_a=(cl>op)&~np.isnan(rb)&(cl>rb); ob_b=(cl<op)&~np.isnan(rl)&(cl<rl)
    out,hecho,espera=[],set(),{}
    emb=dict(ts_h4h1=0,con_ob=0,dol_ok=0,senales=0)
    for i in range(len(ch)-1):
        if np.isnan(rhi[i]) or np.isnan(p_hi[i]): continue
        if not (HORA_INI<=horas[i]<HORA_FIN): continue
        for largo in (True,False):
            if largo:
                t4=(h4lo[i]<rlo[i]) and (rlo[i]<cl[i]<=rhi[i])
                t1=(h1lo[i]<p_lo[i]) and (cl[i]>p_lo[i])
                obk=ob_a[i]
            else:
                t4=(h4hi[i]>rhi[i]) and (rlo[i]<=cl[i]<rhi[i])
                t1=(h1hi[i]>p_hi[i]) and (cl[i]<p_hi[i])
                obk=ob_b[i]
            if not (t4 and t1): continue
            emb["ts_h4h1"]+=1
            clave=(h4id[i],largo)
            if UNA_RANGO and clave in hecho: continue
            espera.setdefault(clave,i)
            if not obk or i-espera[clave]>MAX_ESPERA: continue
            emb["con_ob"]+=1
            obj=dup[i] if largo else ddn[i]; contr=ddn[i] if largo else dup[i]
            if np.isnan(obj): continue
            if not np.isnan(contr):
                if abs(obj-cl[i]) > DOL_K*abs(contr-cl[i]): continue
            emb["dol_ok"]+=1
            entrada=op[i+1]; swpx=h4lo[i] if largo else h4hi[i]
            sl=swpx-SL_BUFFER*unit if largo else swpx+SL_BUFFER*unit
            riesgo=abs(entrada-sl)
            if riesgo<=0: continue
            tp=entrada+TP_R*riesgo if largo else entrada-TP_R*riesgo
            if not ((entrada>sl and tp>entrada) if largo else (entrada<sl and tp<entrada)): continue
            emb["senales"]+=1; hecho.add(clave)
            out.append(dict(ts=ts[i],largo=largo,entrada=entrada,sl=sl,tp=tp,
                            riesgo_u=riesgo/unit))
            break
    return pd.DataFrame(out),emb

def simula(sig,m1,unit,coste):
    if sig.empty: return sig
    T=m1["ts"].to_numpy();H=m1["high"].to_numpy();L=m1["low"].to_numpy();C=m1["close"].to_numpy()
    out,libre=[],np.datetime64("1970-01-01")
    for r in sig.itertuples():
        ets=np.datetime64(pd.Timestamp(r.ts)+pd.Timedelta(minutes=15))
        if ets<libre: continue
        i0=int(np.searchsorted(T,ets)); i1=min(i0+MAX_HORAS*60,len(T))
        if i0>=len(T) or i1<=i0: continue
        a,b=H[i0:i1],L[i0:i1]
        gsl,gtp=((b<=r.sl,a>=r.tp) if r.largo else (a>=r.sl,b<=r.tp))
        isl=int(np.argmax(gsl)) if gsl.any() else 10**9
        itp=int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl==10**9 and itp==10**9: sal,mot,ifin=C[i1-1],"tiempo",(i1-i0)-1
        elif isl<=itp: sal,mot,ifin=r.sl,"SL",isl
        else: sal,mot,ifin=r.tp,"TP",itp
        br=(sal-r.entrada) if r.largo else (r.entrada-sal)
        bruto=(br/unit)/r.riesgo_u
        out.append(dict(ts=r.ts,dir="largo" if r.largo else "corto",riesgo_u=r.riesgo_u,
                        motivo=mot,bruto=bruto,R=(br/unit-coste)/r.riesgo_u))
        libre=T[i0+ifin]
    return pd.DataFrame(out)

def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z,2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
