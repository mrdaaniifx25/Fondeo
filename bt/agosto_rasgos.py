"""Construye 15 caracteristicas medibles en el momento de la entrada para las
operaciones de agosto que tienen datos M1, y comprueba si alguna explica el
resultado. Se usa para decidir si tiene sentido ajustar un indicador a agosto.
"""
import pandas as pd, numpy as np
U=0.0001
m1=pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
              pd.read_parquet("data/eurusd_m1_2026_08.parquet")],ignore_index=True)
m1["ts"]=pd.to_datetime(m1.ts); m1=m1.sort_values("ts").reset_index(drop=True)
m1["loc"]=pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert("Europe/Madrid").tz_localize(None)
m1["b5"]=m1["loc"].dt.floor("5min")
v=(m1.groupby("b5").agg(o=("open","first"),h=("high","max"),l=("low","min"),c=("close","last"),n=("ts","size")).reset_index())
v=v[v.n>=3].reset_index(drop=True); v["dia"]=v.b5.dt.date.astype(str); v["hm"]=v.b5.dt.strftime("%H:%M")
O,H,L,C=v.o.to_numpy(),v.h.to_numpy(),v.l.to_numpy(),v.c.to_numpy()
asia={d:(float(g[g.b5.dt.hour<8].h.max()),float(g[g.b5.dt.hour<8].l.min()))
      for d,g in v.groupby("dia") if len(g[g.b5.dt.hour<8])>=60}
h1=m1.set_index("ts").close.resample("1h").last().dropna()
m15=m1.set_index("ts").close.resample("15min").last().dropna()
def dirn(se,ts,k):
    i=se.index.searchsorted(ts,side="left")-1
    return 0 if i<k else int(np.sign(se.iloc[i]-se.iloc[i-k]))
o=pd.read_csv("data/agosto_operaciones.csv"); ver=pd.read_csv("data/agosto_verificacion.csv").set_index("id")
F=[]
for r in o[o.fecha<="2026-08-21"].itertuples():
    g=v[v.dia==r.fecha]; k=g.index[g.hm==r.hora]
    if not len(k): continue
    i=int(k[0]); rg=abs(r.entrada-r.stop); hi,lo=asia[r.fecha]
    niv=hi if abs(r.entrada-hi)<=abs(r.entrada-lo) else lo
    ini=int(v[(v.dia==r.fecha)&(v.hm>="08:00")].index[0]); prev=slice(ini,i)
    res=ver.loc[r.id,"mot"]; res=res if res in("TP","SL") else ver.loc[r.id,"suyo"]
    if res not in ("TP","SL"): continue
    rango=H[i]-L[i]
    tl=pd.Timestamp(v.b5[i]).tz_localize("Europe/Madrid").tz_convert("UTC").tz_localize(None)
    F.append(dict(id=r.id, y=1 if res=="TP" else 0, hora=int(r.hora[:2])*60+int(r.hora[3:]),
        riesgo=rg/U, dist=(r.entrada-niv)/U, lado=r.lado, alto=1 if niv==hi else 0,
        dirH1=dirn(h1,tl,4)*r.lado, dirM15=dirn(m15,tl,4)*r.lado,
        toques=int(((L[prev]<=niv)&(H[prev]>=niv)).sum()),
        fuera=int((C[prev]>niv).sum() if r.lado>0 else (C[prev]<niv).sum()),
        cuerpo=abs(C[i]-O[i])/U, rango=rango/U,
        mecha=(H[i]-max(O[i],C[i]))/U if r.lado>0 else (min(O[i],C[i])-L[i])/U,
        pos=np.nan if rango<=0 else ((r.entrada-L[i])/rango if r.lado>0 else (H[i]-r.entrada)/rango),
        dsem=pd.Timestamp(r.fecha).dayofweek, atr=np.nanmean(H[max(0,i-14):i]-L[max(0,i-14):i])/U))
d=pd.DataFrame(F).dropna(); d.to_csv("data/agosto_rasgos.csv", index=False)
y=d.y.to_numpy(); cols=[c for c in d.columns if c not in("id","y")]

def mejor(x, yv):
    """mejor acierto alcanzable con un solo umbral, en las dos direcciones"""
    b=0.0
    for th in np.unique(x):
        for s in (1,-1):
            p=(s*x>=s*th).astype(int)
            b=max(b,(p==yv).mean())
    return b

print(f"SUS {len(d)} OPERACIONES CON DATOS · {int(y.sum())} TP y {int((1-y).sum())} SL")
print(f"acertar siempre 'TP' ya da {100*max(y.mean(),1-y.mean()):.0f} %\n")
print(f"  {'característica':<14}{'mejor acierto con un umbral':>30}")
res=sorted(((c, mejor(d[c].to_numpy(), y)) for c in cols), key=lambda x:-x[1])
for c,a in res: print(f"  {c:<14}{100*a:>29.0f} %")

rng=np.random.default_rng(5); N=2000
maxs=[max(mejor(d[c].to_numpy(), rng.permutation(y)) for c in cols) for _ in range(N)]
obs=res[0][1]
print(f"\nPRUEBA DE PERMUTACIÓN ({N} barajadas de sus resultados)")
print(f"  el mejor de sus rasgos llega al {100*obs:.0f} %")
print(f"  con resultados al azar, el mejor rasgo llega de media al {100*np.mean(maxs):.0f} %")
print(f"  y alcanza o supera el {100*obs:.0f} % en el {100*np.mean(np.array(maxs)>=obs-1e-9):.0f} % de las barajadas")
