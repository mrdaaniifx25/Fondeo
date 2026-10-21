import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd, json
from ema_rsi import marcos, senales, simula, pz, pf

INSTR = {
 "EURUSD": ("data/eurusd_m1.parquet", 0.0001, 1.2),
 "GBPUSD": ("data/gbpusd_m1.parquet", 0.0001, 1.5),
 "USDJPY": ("data/usdjpy_m1.parquet", 0.01,   1.2),
 "NAS100": ("data/nsxusd_m1.parquet", 1.0,    1.5),
 "SP500":  ("data/spxusd_m1.parquet", 1.0,    0.6),
}
CAB=f"{'':30s} {'n':>5s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'%TP':>6s} {'PF neto':>8s} {'R neto':>8s}"
def linea(nom,tr):
    if tr is None or len(tr)<3:
        print(f"{nom:30s} {0 if tr is None else len(tr):>5d}      (muestra insuficiente)"); return None
    z,p=pz(tr.bruto)
    print(f"{nom:30s} {len(tr):>5d} {tr.bruto.mean():>+9.4f} {z:>+6.2f} {p:>7.4f} "
          f"{(tr.motivo=='TP').mean()*100:>5.1f}% {pf(tr.R):>8.3f} {tr.R.sum():>+8.1f}")
    return dict(n=len(tr), bruto=float(tr.bruto.mean()), z=float(z), p=float(p),
                pf=float(pf(tr.R)), Rneto=float(tr.R.sum()))

D={}
print("preparando marcos temporales...")
for k,(f,u,c) in INSTR.items():
    m1=pd.read_parquet(f); m1["ts"]=pd.to_datetime(m1["ts"])
    D[k]=(m1, marcos(m1)); print(f"  {k:7s} {len(D[k][1]):>7,} velas M15")

res={}
for tp_r in (1.0,1.5,2.0,3.0):
    print(f"\n{'='*88}\nOBJETIVO {tp_r:.1f}R\n{'='*88}\n{CAB}")
    tot=[]
    for k,(f,u,c) in INSTR.items():
        m1,d = D[k]
        sig,emb = senales(d,u,tp_r)
        tr = simula(sig,m1,u,c)
        r = linea(f"   {k}", tr)
        if r: r["emb"]=emb; res[f"{k}_{tp_r}"]=r
        if tr is not None and not tr.empty: tot.append(tr)
        if tp_r==2.0:
            print(f"        embudo: tendencia {emb['tendencia']:,} -> toca EMA {emb['toque']:,} "
                  f"-> RSI {emb['rsi']:,} -> patron {emb['patron']:,} -> operables {emb['coherente']:,}")
    if tot:
        a=pd.concat(tot,ignore_index=True)
        print("   "+"-"*85)
        res[f"TODOS_{tp_r}"]=linea("   LOS CINCO JUNTOS", a)

print(f"\n{'='*88}\nCONTROLES sobre el objetivo 2R\n{'='*88}\n{CAB}")
esp=[]
for k,(f,u,c) in INSTR.items():
    m1,d=D[k]; sig,_=senales(d,u,2.0,invertir=True)
    tr=simula(sig,m1,u,c)
    if tr is not None and not tr.empty: esp.append(tr)
res["espejo"]=linea("   ESPEJO (direccion contraria)", pd.concat(esp,ignore_index=True))

az=[]
rng=np.random.default_rng(7)
for k,(f,u,c) in INSTR.items():
    m1,d=D[k]; sig,_=senales(d,u,2.0)
    n=len(sig)
    if n==0: continue
    val=d[(d.hora>=8)&(d.hora<17)].index.to_numpy(); val=val[(val>60)&(val<len(d)-200)]
    for s in range(5):
        pick=np.sort(rng.choice(val,size=min(n,len(val)),replace=False))
        o,h,l = (d[x].to_numpy() for x in ("open","high","low"))
        ts=d["ts"].to_numpy()
        filas=[]
        for i in pick:
            largo=bool(rng.integers(0,2))
            j0=max(0,i-10); piv_lo,piv_hi=l[j0:i+1].min(),h[j0:i+1].max()
            rg=max(piv_hi-piv_lo,u); e=o[i+1]
            sl=(piv_lo-0.10*rg) if largo else (piv_hi+0.10*rg)
            riesgo=abs(e-sl)
            if riesgo<=0: continue
            tp=e+2.0*riesgo if largo else e-2.0*riesgo
            filas.append(dict(ts=ts[i+1],largo=largo,e=e,sl=sl,tp=tp,riesgo_u=riesgo/u))
        tr=simula(pd.DataFrame(filas),m1,u,c)
        if tr is not None and not tr.empty: az.append(tr)
res["azar"]=linea("   ENTRADA AL AZAR (5 rep)", pd.concat(az,ignore_index=True))
json.dump({k:v for k,v in res.items()}, open("data/informe_ema_rsi.json","w"), indent=1, default=str)
