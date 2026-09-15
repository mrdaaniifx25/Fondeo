import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from efectos import pz, ny, sesiones

IDX={"NAS100":"data/nsxusd_m1.parquet","SP500":"data/spxusd_m1.parquet"}
FX ={"EURUSD":"data/eurusd_m1.parquet","GBPUSD":"data/gbpusd_m1.parquet",
     "USDJPY":"data/usdjpy_m1.parquet"}
M={k:pd.read_parquet(v).assign(ts=lambda d: pd.to_datetime(d.ts)) for k,v in {**IDX,**FX}.items()}

print("="*92); print("E1 · NOCTURNO FRENTE A DIURNO EN INDICES"); print("="*92)
S={}
for k in IDX:
    g=sesiones(M[k]); S[k]=g
    zf,pf_=pz(g.fuera.to_numpy()); zd,pd_=pz(g.dentro.to_numpy())
    cf=float(np.prod(1+g.fuera)); cd=float(np.prod(1+g.dentro))
    print(f"\n{k}  ({len(g)} sesiones, {g.index.min()} -> {g.index.max()})")
    print(f"   NOCTURNO 16:00->09:30  media {g.fuera.mean()*100:+.4f}%/dia  z {zf:+5.2f}  "
          f"p {pf_:.5f}  acumulado x{cf:.3f} ({(cf-1)*100:+.1f}%)")
    print(f"   DIURNO   09:30->16:00  media {g.dentro.mean()*100:+.4f}%/dia  z {zd:+5.2f}  "
          f"p {pd_:.5f}  acumulado x{cd:.3f} ({(cd-1)*100:+.1f}%)")
    dif=g.fuera-g.dentro; zz,pp=pz(dif.to_numpy())
    print(f"   DIFERENCIA nocturno-diurno {dif.mean()*100:+.4f}%/dia  z {zz:+5.2f}  p {pp:.5f}")
    print(f"   comprar y mantener la sesion completa: x{cf*cd:.3f} ({(cf*cd-1)*100:+.1f}%)")
    print("   coste de financiacion nocturna (CFD largo), efecto sobre el acumulado:")
    for tasa in (0.00, 0.02, 0.03, 0.04, 0.05):
        neto=float(np.prod(1+g.fuera-tasa/252))
        print(f"      {tasa*100:>4.1f}%/año -> x{neto:.3f} ({(neto-1)*100:+7.1f}%)"
              f"{'   <- deja de compensar' if neto<1 else ''}")

print("\n"+"="*92); print("E2 · CALENDARIO"); print("="*92)
filas=[]
for k in {**IDX,**FX}:
    d=ny(M[k]); d["dia"]=d.ny.dt.date
    g=d.groupby("dia").agg(ci=("close","last"))
    g["r"]=g.ci.pct_change(); g=g.dropna()
    idx=pd.DatetimeIndex(pd.to_datetime(g.index))
    g["dow"]=idx.dayofweek; g["dom"]=idx.day
    g["mes"]=idx.to_period("M")
    ult=g.groupby("mes").apply(lambda x: x.index[-1], include_groups=False)
    g["cambio"]=[ (i in set(ult)) or (dd<=3) for i,dd in zip(g.index,g.dom) ]
    for nom,serie in [(f"lunes",g[g.dow==0].r),(f"martes",g[g.dow==1].r),
                      (f"miercoles",g[g.dow==2].r),(f"jueves",g[g.dow==3].r),
                      (f"viernes",g[g.dow==4].r),
                      (f"cambio de mes",g[g.cambio].r),(f"resto del mes",g[~g.cambio].r)]:
        z,p=pz(serie.to_numpy())
        filas.append(dict(instr=k,casilla=nom,n=len(serie),media=serie.mean()*100,z=z,p=p))
t=pd.DataFrame(filas)
print(f"casillas probadas: {len(t)}  ->  umbral Bonferroni p < {0.05/len(t):.5f}\n")
print(t.sort_values("p").head(12).to_string(index=False,
      formatters={"media":"{:+.4f}".format,"z":"{:+.2f}".format,"p":"{:.5f}".format}))
sig=t[t.p<0.05/len(t)]
print(f"\ncasillas que superan Bonferroni: {len(sig)}" + ("  -> NINGUNA" if sig.empty else ""))

print("\n"+"="*92); print("E3 · FILTRO LENTO COMO CONTROL DE CAIDA SOBRE EXPOSICION LARGA"); print("="*92)
def metricas(r):
    eq=np.cumprod(1+r); dd=1-eq/np.maximum.accumulate(eq)
    ann=eq[-1]**(252/len(r))-1
    return eq[-1], ann, dd.max(), ann/dd.max() if dd.max()>0 else np.inf
print(f"{'':34s} {'x final':>8s} {'anual':>8s} {'caida max':>10s} {'anual/caida':>12s}")
for k in IDX:
    d=ny(M[k]); d["dia"]=d.ny.dt.date
    g=d.groupby("dia").agg(ci=("close","last")); g["r"]=g.ci.pct_change()
    g=g.dropna(); r=g.r.to_numpy()
    print(f"\n{k}")
    e,a,dd,ra=metricas(r); print(f"  {'comprar y mantener':32s} {e:>8.3f} {a*100:>7.1f}% {dd*100:>9.1f}% {ra:>12.2f}")
    for N in (100,150,200):
        ma=g.ci.rolling(N).mean().shift(1)
        dentro=(g.ci.shift(1)>ma).to_numpy()
        rf=np.where(dentro, r, 0.0)
        e,a,dd,ra=metricas(rf)
        exp=dentro.mean()*100
        print(f"  {f'largo solo si precio > media {N}':32s} {e:>8.3f} {a*100:>7.1f}% {dd*100:>9.1f}% {ra:>12.2f}"
              f"   (expuesto {exp:.0f}% del tiempo)")
