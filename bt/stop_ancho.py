"""¿Ensanchar el stop conserva la ventaja, o solo cambia la geometria?

El coste en R baja al ensanchar el stop -es una division-. Pero el objetivo del
CRT es estructural: el extremo opuesto de la vela base, y NO se ensancha con el
stop. Asi que el R:R cae. La pregunta es si la tasa de aciertos sube lo bastante
para compensar, y eso no se razona: se mide.
"""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS=[("EURUSD","data/eurusd_m1.parquet",0.0001,1.2),("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.5),
     ("USDJPY","data/usdjpy_m1.parquet",0.01,1.3),("NAS100","data/nsxusd_m1.parquet",1.0,1.5),
     ("SPX500","data/spxusd_m1.parquet",1.0,0.6)]
TF = 4

def resuelve(m1, ref, ent_i, entrada, stop, objetivo, alcista, tope_velas=5):
    """Resolucion en M1, identica al motor auditado: empate -> stop."""
    t1=m1.ts.to_numpy(); H=m1.high.to_numpy(); L=m1.low.to_numpy(); C1=m1.close.to_numpy()
    fin=ref["fin"].to_numpy()
    tope=int(tope_velas*TF*60)
    R=np.full(len(entrada), np.nan); mot=np.array([""]*len(entrada), dtype=object)
    for k in range(len(entrada)):
        j0=int(np.searchsorted(t1, fin[ent_i[k]], side="right")); j1=min(j0+tope,len(t1))
        if j0>=len(t1): continue
        hh,ll=H[j0:j1],L[j0:j1]
        if alcista[k]: gt,gs = hh>=objetivo[k], ll<=stop[k]
        else:          gt,gs = ll<=objetivo[k], hh>=stop[k]
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        rr = abs(objetivo[k]-entrada[k])/abs(entrada[k]-stop[k])
        if it==10**9 and isl==10**9:
            sal=C1[j1-1]
            R[k]=((sal-entrada[k]) if alcista[k] else (entrada[k]-sal))/abs(entrada[k]-stop[k])
            mot[k]="tiempo"
        elif isl<=it: R[k]=-1.0; mot[k]="SL"
        else:         R[k]=rr;   mot[k]="TP"
    return R, mot

print("="*112)
print("CRT en H4 · mismo setup, misma entrada, mismo objetivo · SOLO cambia dónde va el stop")
print("  cinco instrumentos, 2020-2026 · objetivo = extremo opuesto de la vela base")
print("="*112)
print(f"{'referencia del stop':26s} {'n':>6s} {'stop med':>9s} {'R:R':>6s} {'%TP':>7s} "
      f"{'coste %R':>9s} {'R BRUTA':>9s} {'IC95 bruta':>19s} {'R NETA':>9s}")
print("-"*112)

acum={}
for nom,ruta,u,co in INS:
    m1=pd.read_parquet(ruta); m1["ts"]=pd.to_datetime(m1["ts"])
    m1=m1.sort_values("ts").reset_index(drop=True)
    ref=velas_ref(m1,TF,ancla_ny=1)
    h,l,c=(ref[x].to_numpy() for x in ("high","low","close")); a=C.atr(h,l,c,20)
    s=LM.secuencias(ref, usar_cuerpo=False)
    s=s[s.k==1].copy()
    ib=s.i_base.to_numpy().astype(int); ie=s.i_ent.to_numpy().astype(int)
    ent=s.entrada.to_numpy(); alc=s.alcista.to_numpy().astype(bool)
    obj=np.where(alc, h[ib], l[ib])
    d3 = np.where(alc, np.minimum.reduce([l[ie],l[ib],l[np.maximum(ib-1,0)]]),
                       np.maximum.reduce([h[ie],h[ib],h[np.maximum(ib-1,0)]]))
    refs={
      "mecha del barrido"    : np.where(alc, l[ie], h[ie]),
      "extremo de 3 velas"   : d3,
      "0,5 x ATR"            : np.where(alc, ent-0.5*a[ie], ent+0.5*a[ie]),
      "1,0 x ATR  (el tuyo)" : np.where(alc, ent-1.0*a[ie], ent+1.0*a[ie]),
      "2,0 x ATR"            : np.where(alc, ent-2.0*a[ie], ent+2.0*a[ie]),
    }
    for k,stp in refs.items():
        riesgo=np.abs(ent-stp)/u
        ok=np.isfinite(riesgo)&(riesgo>0)&np.isfinite(obj)
        R,mot=resuelve(m1,ref,ie[ok],ent[ok],stp[ok],obj[ok],alc[ok])
        d=pd.DataFrame(dict(R=R,mot=mot,riesgo=riesgo[ok],
                            rr=np.abs(obj[ok]-ent[ok])/np.abs(ent[ok]-stp[ok]))).dropna()
        d["neto"]=d.R-co/d.riesgo
        acum.setdefault(k,[]).append(d)

for k,ds in acum.items():
    D=pd.concat(ds,ignore_index=True)
    x=D.R.to_numpy(); ee=x.std(ddof=1)/np.sqrt(len(x))
    print(f"{k:26s} {len(D):>6,} {D.riesgo.median():>8.1f}u {D.rr.median():>6.2f} "
          f"{100*(D.mot=='TP').mean():>6.1f}% {100*(1.2/D.riesgo).median():>8.1f}% "
          f"{x.mean():>+9.3f} [{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}] "
          f"{D.neto.mean():>+9.3f}")

print("\n" + "="*112)
print("La geometría pura predice %TP = 1/(1+R:R). Si la ventaja fuera información")
print("real y no geometría, el %TP observado tendría que superar ese número:")
for k,ds in acum.items():
    D=pd.concat(ds,ignore_index=True)
    rr=D.rr.median(); esp=100/(1+rr); obs=100*(D.mot=='TP').mean()
    print(f"   {k:26s} espera {esp:>5.1f}%   observa {obs:>5.1f}%   "
          f"{obs-esp:>+5.1f} puntos")
