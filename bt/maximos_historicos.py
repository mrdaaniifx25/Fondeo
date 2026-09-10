"""¿Es cierto que en maximos historicos hay que buscar siempre compras?

Afirmacion de la transcripcion nº24. Preregistro sellado en 02570ea.

  python3 bt/maximos_historicos.py
"""
import numpy as np, pandas as pd

INSTR = {"NASDAQ":("data/nsxusd_m1.parquet",1.50),
         "SP500": ("data/spxusd_m1.parquet",0.50),
         "GER40": ("data/grxeur_m1.parquet",1.50)}
TF, VIDA, CERCA = 30, 96, 0.01     # 96 velas de vida · a menos del 1 % del max

def corre(nom, ruta, coste):
    d = pd.read_parquet(ruta); d["ts"]=pd.to_datetime(d.ts)
    d = d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    d = d.rename(columns={"open":"o","high":"h","low":"l","close":"c"})
    g = (d.set_index("ts").resample(f"{TF}min",label="left",closed="left")
         .agg(h=("h","max"),l=("l","min"),c=("c","last"),n=("c","size"))
         .dropna())
    g = g[g.n >= TF*0.4].reset_index()
    h,l,c = g.h.to_numpy(), g.l.to_numpy(), g.c.to_numpy()
    n=len(g)
    maxh = np.maximum.accumulate(h)
    # EN MAXIMOS: el cierre esta a menos del 1 % del maximo historico previo
    enmax = np.zeros(n,bool)
    enmax[1:] = c[1:] >= maxh[:-1]*(1-CERCA)
    out=[]
    for stop in (20,40,80):
        for lado,et in ((+1,"COMPRA"),(-1,"VENTA")):
            for zona,mz in (("EN MAXIMOS",enmax),("fuera",~enmax)):
                idx = np.where(mz)[0]
                idx = idx[(idx>200)&(idx<n-VIDA-1)]
                if len(idx)<200: continue
                idx = idx[::3]                     # submuestreo: menos solape
                Rs=[]
                for i in idx:
                    ent=c[i]; sl=ent-lado*stop; tp=ent+lado*stop
                    H,L=h[i+1:i+1+VIDA], l[i+1:i+1+VIDA]
                    ms=(L<=sl) if lado>0 else (H>=sl)
                    mt=(H>=tp) if lado>0 else (L<=tp)
                    iS=int(np.argmax(ms)) if ms.any() else 10**9
                    iT=int(np.argmax(mt)) if mt.any() else 10**9
                    if iS==10**9 and iT==10**9:
                        sal=c[min(i+VIDA,n-1)]
                        Rs.append(((sal-ent)*lado)/stop)
                    else:
                        Rs.append(-1.0 if iS<=iT else 1.0)
                R=np.array(Rs)
                out.append(dict(instr=nom, stop=stop, lado=et, zona=zona,
                                n=len(R), acierto=100*(R>0).mean(),
                                R=R.mean(), z=R.mean()/(R.std(ddof=1)/np.sqrt(len(R))),
                                Rn=R.mean()-coste/stop))
    return pd.DataFrame(out)

if __name__=="__main__":
    T=pd.concat([corre(k,*v) for k,v in INSTR.items()], ignore_index=True)
    T.to_csv("data/maximos_historicos.csv", index=False)
    print("El azar a 1:1 es el 50,0 % de acierto y R = 0.\n")
    print(f"{'instr':>7s} {'stop':>5s} {'lado':>7s} {'zona':>11s} {'n':>6s} "
          f"{'acierto':>9s} {'R':>8s} {'z':>7s} {'R NETA':>8s}")
    print("-"*76)
    for r in T.itertuples():
        print(f"{r.instr:>7s} {r.stop:5d} {r.lado:>7s} {r.zona:>11s} {r.n:6d} "
              f"{r.acierto:8.1f} % {r.R:+8.3f} {r.z:+7.2f} {r.Rn:+8.3f}")
    print("\n" + "="*76)
    print("COMPRAS: en maximos contra fuera de maximos")
    for st,g in T[T.lado=="COMPRA"].groupby("stop"):
        a=g[g.zona=="EN MAXIMOS"]; b=g[g.zona=="fuera"]
        if not len(a) or not len(b): continue
        print(f"  stop {st:3d}:  en maximos {a.acierto.mean():.1f} %  ·  "
              f"fuera {b.acierto.mean():.1f} %  ·  diferencia "
              f"{a.acierto.mean()-b.acierto.mean():+.1f} puntos")
    print("\nCOMPRAS contra VENTAS, solo EN MAXIMOS")
    for st,g in T[T.zona=="EN MAXIMOS"].groupby("stop"):
        cc=g[g.lado=="COMPRA"]; vv=g[g.lado=="VENTA"]
        if not len(cc) or not len(vv): continue
        print(f"  stop {st:3d}:  compras {cc.acierto.mean():.1f} %  ·  "
              f"ventas {vv.acierto.mean():.1f} %  ·  R compras {cc.R.mean():+.3f}  "
              f"NETA {cc.Rn.mean():+.3f}")
