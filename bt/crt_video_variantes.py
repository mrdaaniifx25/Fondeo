"""Exploratorio (post hoc): variantes de objetivo y de stop del video CRT.

Las tres dianas que el video menciona (extremo opuesto de H4, 50 % del rango
diario, extremo completo del rango diario) por tres anchos de stop.
NO estaba preregistrado: se publica marcado como exploratorio.

  python3 bt/crt_video_variantes.py
"""
import numpy as np, pandas as pd
from math import sqrt
import sys; sys.path.insert(0,"bt")
import importlib.util as _i
_sp=_i.spec_from_file_location("_cv","bt/crt_video.py")
_m=_i.module_from_spec(_sp)
_src=open("bt/crt_video.py").read().split("T = pd.concat")[0]
exec(compile(_src,"cv","exec"),_m.__dict__)
lado_activado=_m.lado_activado; z=_m.z

INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 1.43),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 35.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  1.6)]
HOR = 2*1440

def corre(nom, ruta, U, coste):
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    t = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    M["kD"]=t.dt.floor("1440min"); M["kH4"]=t.dt.floor("240min")
    M["kH1"]=t.dt.floor("60min");  M["k15"]=t.dt.floor("15min")
    lD,dh,dl = lado_activado(M,"kD"); lH4,h4h,h4l = lado_activado(M,"kH4")
    lH1,_,_  = lado_activado(M,"kH1")
    q = M.groupby("k15",sort=False).agg(o=("open","first"),h=("high","max"),
                                        l=("low","min"),c=("close","last"))
    q = q[q.index.notna()]
    ph15,pl15 = q.h.shift(1).to_numpy(), q.l.shift(1).to_numpy()
    O,H,L,C = (q[k].to_numpy() for k in "ohlc")
    up = (L<=pl15)&(C>pl15)&(C<ph15)&(H<ph15)
    dn = (H>=ph15)&(C<ph15)&(C>pl15)&(L>pl15)
    sig = np.where(up,1,np.where(dn,-1,0)).astype(np.int8)
    fin = M.groupby("k15",sort=False).apply(lambda d: d.index[-1]).reindex(q.index).to_numpy()
    HH,LL,OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()
    ts = M.ts.to_numpy()
    out=[]
    for i in np.nonzero(sig)[0]:
        if i+1>=len(q): continue
        j=int(fin[i]); e=j+1
        if e>=len(M): continue
        s=int(sig[i])
        if not (lD[j]==s and lH4[j]==s and lH1[j]==s): continue
        ent=OO[e]; mecha = L[i] if s>0 else H[i]
        if not (np.isfinite(h4h[j]) and np.isfinite(dh[j])): continue
        med = (dh[j]+dl[j])/2.0
        tg = {"H4": h4h[j] if s>0 else h4l[j],
              "D50": med,
              "D": dh[j] if s>0 else dl[j]}
        base=(ent-mecha)*s
        if base<=0: continue
        out.append((nom,ts[e],s,ent,base,tg["H4"],tg["D50"],tg["D"],e,U,coste))
    D=pd.DataFrame(out,columns="ins ts lado ent base tH4 tD50 tD e U coste".split())
    D["dia"]=pd.to_datetime(D.ts).dt.floor("D")
    return D,HH,LL

Q={}; T=[]
for a in INS:
    D,HH,LL=corre(*a); Q[a[0]]=(HH,LL); T.append(D)
T=pd.concat(T,ignore_index=True)
T=T.sort_values("ts").drop_duplicates(["ins","dia"]).reset_index(drop=True)
print(f"{'objetivo':<7}{'stop':>6}{'n':>6}{'R:R':>7}{'acierto':>9}{'geom':>8}{'coste':>8}{'BRUTA':>9}{'z':>7}{'NETA':>9}{'z':>7}")
for tg in ("tH4","tD50","tD"):
    for mult in (1.0,2.0,4.0):
        R=[];RG=[];RC=[];CR=[];GR=[]
        for _,r in T.iterrows():
            s=r.lado; ent=r.ent; rgo=r.base*mult; rec=(r[tg]-ent)*s
            if rec<=0 or rgo<=0: continue
            HHx,LLx=Q[r.ins]; a=int(r.e); b=min(a+HOR,len(HHx))
            hh,ll=HHx[a:b],LLx[a:b]
            if s>0: ks=np.nonzero(ll<=ent-rgo)[0]; kt=np.nonzero(hh>=ent+rec)[0]
            else:   ks=np.nonzero(hh>=ent+rgo)[0]; kt=np.nonzero(ll<=ent-rec)[0]
            fs=ks[0] if len(ks) else 10**9; ft=kt[0] if len(kt) else 10**9
            R.append(rec/rgo if ft<fs else (-1.0 if fs<10**9 else 0.0))
            RG.append(rgo/r.U); RC.append(rec/r.U); CR.append(r.coste/(rgo/r.U))
            GR.append(r.ins+str(r.dia))
        R=pd.Series(R); CR=pd.Series(CR); GR=pd.Series(GR)
        rr=(pd.Series(RC)/pd.Series(RG)).mean()
        geo=(pd.Series(RG)/(pd.Series(RG)+pd.Series(RC))).mean()
        N=R-CR
        print(f"{tg:<7}{mult:>5.0f}x{len(R):>6}{rr:>7.2f}{100*(R>0).mean():>8.1f}%"
              f"{100*geo:>7.1f}%{100*CR.mean():>7.1f}%{R.mean():>+9.4f}{z(R,GR):>+7.2f}"
              f"{N.mean():>+9.4f}{z(N,GR):>+7.2f}")
