import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from liquidez_sesiones import sesiones, niveles, pz, pf

U, COSTE = 0.0001, 1.2
BUF, MAXH = 2.0, 24
m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
ch = m1.set_index("ts").resample("15min",label="left",closed="left").agg(
     open=("open","first"),high=("high","max"),low=("low","min"),
     close=("close","last")).dropna().reset_index()

print("construyendo sesiones y niveles...")
ses = sesiones(m1); lv = niveles(ses, m1)
print(f"  sesiones cerradas: {len(ses):,}  |  niveles: {len(lv):,}")
print(f"  niveles que llegaron a barrerse: {(lv.imuere<10**9).sum():,} "
      f"({(lv.imuere<10**9).mean()*100:.1f}%)\n")

T=m1.ts.values; H=m1.high.values; L=m1.low.values; C=m1.close.values
tc=ch.ts.values; hc=ch.high.values; lc=ch.low.values; cc=ch.close.values

def opera(objetivo, confirmar=True):
    """objetivo: 'opuesto' = el otro extremo de la misma sesion
                 'vivo'    = el nivel de sesion vivo mas cercano del lado contrario"""
    out=[]; libre=np.datetime64("1970-01-01")
    vivos = lv.sort_values("nace")
    for r in lv[lv.imuere < 10**9].sort_values("muere").itertuples():
        tb = np.datetime64(pd.Timestamp(r.muere))          # instante del barrido
        if tb < libre: continue
        largo = not r.arriba                                # barre maximo -> corto
        j0 = int(np.searchsorted(tc, tb))
        if j0 >= len(tc)-1: continue
        # confirmacion: cierre M15 de vuelta dentro del rango de la sesion
        jj = None
        for j in range(j0, min(j0+8, len(tc))):
            dentro = (cc[j] < r.px) if r.arriba else (cc[j] > r.px)
            if not confirmar or dentro:
                jj = j; break
        if jj is None: continue
        e = ch.open.values[jj+1] if jj+1 < len(ch) else cc[jj]
        i0 = int(np.searchsorted(T, np.datetime64(pd.Timestamp(tc[jj]))+np.timedelta64(15,"m")))
        if i0 >= len(T): continue
        # extremo real del barrido hasta la entrada
        k0 = int(np.searchsorted(T, tb))
        ext = H[k0:i0].max() if r.arriba else L[k0:i0].min()
        sl = ext + BUF*U if r.arriba else ext - BUF*U
        if objetivo == "opuesto":
            tp = r.otro
        else:
            cand = lv[(lv.nace <= pd.Timestamp(tb)) & (lv.muere > pd.Timestamp(tb))]
            cand = cand[cand.arriba != r.arriba] if False else cand[cand.arriba == (not r.arriba)]
            if cand.empty: continue
            tp = cand.px.max() if not r.arriba else cand.px.min()
            tp = cand.px.iloc[(cand.px - e).abs().argsort().iloc[0]]
        riesgo = abs(e-sl); premio = abs(tp-e)
        if riesgo <= 0 or premio <= 0: continue
        if not ((e<sl and tp<e) if r.arriba else (e>sl and tp>e)): continue
        rr = premio/riesgo
        if rr < 0.5 or rr > 20: continue
        i1 = min(i0 + MAXH*60, len(T))
        a,b = H[i0:i1], L[i0:i1]
        gsl,gtp = ((a>=sl, b<=tp) if r.arriba else (b<=sl, a>=tp))
        isl = int(np.argmax(gsl)) if gsl.any() else 10**9
        itp = int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl==10**9 and itp==10**9: sal,mot,f = C[i1-1],"tiempo",(i1-i0)-1
        elif isl<=itp: sal,mot,f = sl,"SL",isl
        else: sal,mot,f = tp,"TP",itp
        gan = (e-sal) if r.arriba else (sal-e)
        out.append(dict(ts=tc[jj], ses=r.ses, arriba=bool(r.arriba), motivo=mot, rr=rr,
                        riesgo_p=riesgo/U, bruto=gan/riesgo,
                        R=(gan/U - COSTE)/(riesgo/U)))
        libre = T[min(i0+f, len(T)-1)]
    return pd.DataFrame(out)

CAB=f"{'':40s} {'n':>5s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'%TP':>6s} {'RR':>5s} {'PF neto':>8s}"
def linea(nom,tr):
    if tr is None or len(tr)<3:
        print(f"{nom:40s} {0 if tr is None else len(tr):>5d}   (muestra insuficiente)"); return
    z,p=pz(tr.bruto)
    print(f"{nom:40s} {len(tr):>5d} {tr.bruto.mean():>+9.4f} {z:>+6.2f} {p:>7.4f} "
          f"{(tr.motivo=='TP').mean()*100:>5.1f}% {tr.rr.mean():>5.2f} {pf(tr.R):>8.3f}")

print("="*100)
print("LA TEORIA, MEDIDA COMO OPERACION")
print("="*100); print(CAB)
A=opera("opuesto",True);  linea("   objetivo: extremo opuesto de la sesion", A)
B=opera("vivo",True);     linea("   objetivo: liquidez viva mas cercana",    B)
A0=opera("opuesto",False); linea("   idem, SIN esperar cierre de vuelta",    A0)

print("\n" + "="*100)
print("POR SESION BARRIDA  (objetivo: extremo opuesto)")
print("="*100); print(CAB)
for s in ("Asia","Londres","NuevaYork"):
    linea(f"   se barrio el nivel de {s}", A[A.ses==s])
linea("   barrido de un MAXIMO (vamos cortos)", A[A.arriba])
linea("   barrido de un MINIMO (vamos largos)", A[~A.arriba])
A.to_csv("data/trades_liquidez.csv", index=False)

print("\n" + "="*100)
print("SOSPECHA: ¿el caso 'sin confirmar' vive de stops diminutos?")
print("="*100)
for nom,df in (("con confirmacion",A),("SIN confirmacion",A0)):
    c = COSTE/df.riesgo_p
    print(f"  {nom:18s} riesgo mediano {df.riesgo_p.median():>6.1f} pips | "
          f"percentil 10 {df.riesgo_p.quantile(.10):>5.1f} | "
          f"coste = {c.mean()*100:>5.1f}% del riesgo")
    chico = df[df.riesgo_p < 5]
    print(f"{'':20s} operaciones con stop < 5 pips: {len(chico):>4} "
          f"({len(chico)/len(df)*100:.1f}%) y su R bruta media {chico.bruto.mean():+.3f}")

print("\n  Repitiendo 'sin confirmar' exigiendo stop de al menos 8 pips:")
g = A0[A0.riesgo_p >= 8]
z,p = pz(g.bruto)
print(f"     n {len(g)} | bruto {g.bruto.mean():+.4f} | z {z:+.2f} | p {p:.4f} | "
      f"PF neto {pf(g.R):.3f}")

print("\n" + "="*100)
print("CONTROL: misma mecanica, DIRECCION AL AZAR")
print("="*100); print(CAB)
rng = np.random.default_rng(19)
def azar(n_rep=5):
    tot=[]
    for rep in range(n_rep):
        out=[]
        libre=np.datetime64("1970-01-01")
        for r in lv[lv.imuere < 10**9].sort_values("muere").itertuples():
            tb=np.datetime64(pd.Timestamp(r.muere))
            if tb<libre: continue
            arriba = bool(rng.integers(0,2))      # sentido sorteado
            j0=int(np.searchsorted(tc,tb))
            if j0>=len(tc)-1: continue
            jj=None
            for j in range(j0,min(j0+8,len(tc))):
                dentro=(cc[j]<r.px) if r.arriba else (cc[j]>r.px)
                if dentro: jj=j; break
            if jj is None: continue
            e=ch.open.values[jj+1] if jj+1<len(ch) else cc[jj]
            i0=int(np.searchsorted(T,np.datetime64(pd.Timestamp(tc[jj]))+np.timedelta64(15,"m")))
            if i0>=len(T): continue
            k0=int(np.searchsorted(T,tb))
            ext=H[k0:i0].max() if arriba else L[k0:i0].min()
            sl=ext+BUF*U if arriba else ext-BUF*U
            tp=r.otro if not arriba else r.otro
            riesgo=abs(e-sl); premio=abs(tp-e)
            if riesgo<=0 or premio<=0: continue
            if not ((e<sl and tp<e) if arriba else (e>sl and tp>e)): continue
            rr=premio/riesgo
            if rr<0.5 or rr>20: continue
            i1=min(i0+MAXH*60,len(T)); a_,b_=H[i0:i1],L[i0:i1]
            gsl,gtp=((a_>=sl,b_<=tp) if arriba else (b_<=sl,a_>=tp))
            isl=int(np.argmax(gsl)) if gsl.any() else 10**9
            itp=int(np.argmax(gtp)) if gtp.any() else 10**9
            if isl==10**9 and itp==10**9: sal,mot,f=C[i1-1],"tiempo",(i1-i0)-1
            elif isl<=itp: sal,mot,f=sl,"SL",isl
            else: sal,mot,f=tp,"TP",itp
            gan=(e-sal) if arriba else (sal-e)
            out.append(dict(motivo=mot,rr=rr,riesgo_p=riesgo/U,bruto=gan/riesgo,
                            R=(gan/U-COSTE)/(riesgo/U)))
            libre=T[min(i0+f,len(T)-1)]
        if out: tot.append(pd.DataFrame(out))
    return pd.concat(tot,ignore_index=True) if tot else None
linea("   direccion al azar (5 rep)", azar())

print("\n" + "="*100)
print("LA TEORIA EN CRUDO: ¿llega al lado opuesto antes de seguir?")
print("="*100)
llega=0; falla=0
for r in lv[lv.imuere < 10**9].sort_values("muere").itertuples():
    i0=int(r.imuere); i1=min(i0+MAXH*60,len(T))
    if i1<=i0: continue
    if r.arriba:
        ext=r.px+ (H[i0:i1].max()-r.px)*0   # referencia
        gsl=H[i0:i1] >= r.px + 15*U         # sigue subiendo 15 pips mas
        gtp=L[i0:i1] <= r.otro
    else:
        gsl=L[i0:i1] <= r.px - 15*U
        gtp=H[i0:i1] >= r.otro
    isl=int(np.argmax(gsl)) if gsl.any() else 10**9
    itp=int(np.argmax(gtp)) if gtp.any() else 10**9
    if itp<isl: llega+=1
    elif isl<10**9: falla+=1
tot=llega+falla
print(f"  Tras barrer un nivel de sesion, en 24 h:")
print(f"     alcanza el extremo opuesto ANTES de seguir 15 pips mas: {llega:,} de {tot:,} "
      f"= {llega/tot*100:.1f}%")
print(f"     sigue en la direccion del barrido: {falla:,} = {falla/tot*100:.1f}%")
