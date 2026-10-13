import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from estrategia_benjamin import *

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
T=m1.ts.values; H=m1.high.values; L=m1.low.values; C=m1.close.values
MARCOS = {}
for tf in ("H1","H4"):
    g = marcos(m1, tf)
    MARCOS[tf] = niveles_vivos(g, m1)
    print(f"{tf}: {len(g):,} velas -> {len(MARCOS[tf]):,} pivotes barridos")

ENT = {}
for tf,mins in (("M1",1),("M2",2),("M5",5)):
    ENT[tf] = m1.set_index("ts").resample(f"{mins}min",label="left",closed="left").agg(
        open=("open","first"),high=("high","max"),low=("low","min"),
        close=("close","last")).dropna().reset_index()
print()

def opera(tf_niv, tf_ent, rr_obj=2.0, buf=1.0, max_espera=60, invertir=False, azar=False, semilla=0):
    e_df = ENT[tf_ent]
    te=e_df.ts.values; oe=e_df.open.values; he=e_df.high.values; le=e_df.low.values
    lv = MARCOS[tf_niv]
    rng = np.random.default_rng(semilla)
    out=[]; libre=np.datetime64("1970-01-01")
    for r in lv.itertuples():
        tb = np.datetime64(pd.Timestamp(r.tbarr))
        if tb < libre: continue
        largo = not r.arriba
        if invertir: largo = not largo
        if azar: largo = bool(rng.integers(0,2))
        j0 = int(np.searchsorted(te, tb))
        if j0 >= len(te)-4: continue
        # buscar el imbalance en las siguientes velas del marco de entrada
        for j in range(j0+3, min(j0+max_espera, len(te)-1)):
            if not en_sesion(te[j]): continue
            A_h,A_l = he[j-3], le[j-3]
            C_h,C_l = he[j-1], le[j-1]
            if largo:
                if not (C_l > A_h): continue
                niv = C_l                       # borde superior del hueco alcista
                toca = le[j] <= niv
            else:
                if not (C_h < A_l): continue
                niv = C_h
                toca = he[j] >= niv
            if not toca: continue
            e = min(niv, oe[j]) if largo else max(niv, oe[j])
            k0 = int(np.searchsorted(T, np.datetime64(pd.Timestamp(te[j]))))
            kb = int(np.searchsorted(T, tb))
            if k0 >= len(T) or k0 <= kb: break
            ext = H[kb:k0].max() if not largo else L[kb:k0].min()
            sl = ext + buf*U if not largo else ext - buf*U
            riesgo = abs(e-sl)
            if riesgo < 3*U or riesgo > 60*U: break
            tp = e + rr_obj*riesgo if largo else e - rr_obj*riesgo
            if not ((e>sl and tp>e) if largo else (e<sl and tp<e)): break
            k1 = min(k0+24*60, len(T))
            a,b = H[k0:k1], L[k0:k1]
            gsl,gtp = ((b<=sl,a>=tp) if largo else (a>=sl,b<=tp))
            isl = int(np.argmax(gsl)) if gsl.any() else 10**9
            itp = int(np.argmax(gtp)) if gtp.any() else 10**9
            if isl==10**9 and itp==10**9: sal,mot,f = C[k1-1],"tiempo",(k1-k0)-1
            elif isl<=itp: sal,mot,f = sl,"SL",isl
            else: sal,mot,f = tp,"TP",itp
            gan = (sal-e) if largo else (e-sal)
            out.append(dict(ts=te[j], largo=largo, motivo=mot, riesgo_p=riesgo/U,
                            bruto=gan/riesgo, R=(gan/U-COSTE)/(riesgo/U)))
            libre = T[min(k0+f, len(T)-1)]
            break
    return pd.DataFrame(out)

CAB=f"{'':42s} {'n':>5s} {'al año':>7s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'%TP':>6s} {'PF neto':>8s}"
def linea(nom,tr):
    if tr is None or len(tr)<3:
        print(f"{nom:42s} {0 if tr is None else len(tr):>5d}  (muestra insuficiente)"); return
    z,p=pz(tr.bruto)
    print(f"{nom:42s} {len(tr):>5d} {len(tr)/6.6:>7.0f} {tr.bruto.mean():>+9.4f} {z:>+6.2f} "
          f"{p:>7.4f} {(tr.motivo=='TP').mean()*100:>5.1f}% {pf(tr.R):>8.3f}")

print("="*104)
print("LA ESTRATEGIA TAL COMO LA DESCRIBE  ·  EURUSD 2020-2026  ·  objetivo 1:2")
print("="*104); print(CAB)
res={}
for tn in ("H1","H4"):
    for te_ in ("M1","M2","M5"):
        tr=opera(tn,te_); res[(tn,te_)]=tr
        linea(f"   niveles {tn} · entrada {te_}", tr)

print("\n"+"="*104)
print("¿DE QUE VIVE LA CELDA QUE PARECE BUENA?  (H1 + M1)")
print("="*104)
tr=res[("H1","M1")]
c=COSTE/tr.riesgo_p
print(f"  riesgo mediano {tr.riesgo_p.median():.1f} pips | percentil 10 {tr.riesgo_p.quantile(.10):.1f}")
print(f"  el coste de 1.2 pips es el {c.mean()*100:.1f}% del riesgo medio")
for umbral in (5,8,12):
    g=tr[tr.riesgo_p>=umbral]
    if len(g)>3:
        z,p=pz(g.bruto)
        print(f"  exigiendo stop >= {umbral:>2} pips: n {len(g):>4} | bruto {g.bruto.mean():+.4f} "
              f"| p {p:.4f} | PF neto {pf(g.R):.3f}")

print("\n"+"="*104)
print("CONTROLES sobre la configuracion del video (H1 + M1)")
print("="*104); print(CAB)
linea("   la estrategia", tr)
linea("   ESPEJO: la direccion contraria", opera("H1","M1",invertir=True))
az=[opera("H1","M1",azar=True,semilla=s) for s in range(5)]
az=[x for x in az if x is not None and len(x)>0]
linea("   DIRECCION AL AZAR (5 rep)", pd.concat(az,ignore_index=True) if az else None)

print("\n"+"="*104)
print("SENSIBILIDAD AL OBJETIVO  (el video usa 1:2)")
print("="*104); print(CAB)
for rr in (1.0,1.5,2.0,3.0):
    linea(f"   objetivo 1:{rr:g}", opera("H1","M1",rr_obj=rr))

print("\n"+"="*104)
print("LAS DOS SESIONES POR SEPARADO")
print("="*104); print(CAB)
import estrategia_benjamin as EB
orig=EB.SES
for nom,ven in (("Londres 09:00-11:00",[(9.0,11.0)]),
                ("Nueva York 14:00-16:30",[(14.0,16.5)]),
                ("fuera de las dos",[(0.0,9.0),(11.0,14.0),(16.5,24.0)])):
    EB.SES=ven
    import importlib
    linea(f"   {nom}", opera("H1","M1"))
EB.SES=orig
