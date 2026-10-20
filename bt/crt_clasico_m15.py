"""El CRT CLASICO en M15 con stop ancho. Sin sesiones, sin filtros.

  rango         la vela M15 ANTERIOR ya cerrada
  manipulacion  la vela actual barre un extremo y CIERRA de vuelta dentro
  entrada       apertura de la vela siguiente
  stop          k x ATR(14)   <- el cambio: no la mecha del barrido
  objetivo      R:R fijo, o el extremo opuesto del rango

  python3 bt/crt_clasico_m15.py
"""
import numpy as np, pandas as pd
from math import sqrt

INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 0.70),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 12.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  0.8)]
HOR = 6*60

def corre(nom, ruta, U, coste, kATR, RR, soloLondres=False, unaPorDia=False):
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    loc = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
    g = M.assign(k=loc.dt.floor("15min")).groupby("k", sort=True)
    b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
              fin=("high", lambda x: x.index[-1]))
    b = b[b.index.notna()]
    tr = pd.concat([b.h-b.l,(b.h-b.c.shift(1)).abs(),(b.l-b.c.shift(1)).abs()],axis=1).max(axis=1)
    b["atr"] = tr.rolling(14).mean().shift(1)
    B = b.index; hb = B.hour + B.minute/60.0
    O,H,L,C,A = (b[k].to_numpy() for k in ("o","h","l","c","atr"))
    FIN = b.fin.to_numpy().astype(int)
    ph, pl = np.r_[np.nan,H[:-1]], np.r_[np.nan,L[:-1]]
    # EL PATRON CLASICO: barre un extremo de la vela anterior y cierra dentro
    up = (L<=pl)&(C>pl)&(C<ph)&(H<ph)
    dn = (H>=ph)&(C<ph)&(C>pl)&(L>pl)
    s = np.where(up,1,np.where(dn,-1,0)).astype(np.int8)
    HH,LL,OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()
    ops=[]; vistos=set()
    for i in np.nonzero(s)[0]:
        if i<20 or i>=len(b)-1: continue
        if soloLondres and not (8<=hb[i]<11): continue
        if not np.isfinite(A[i]) or A[i]<=0: continue
        d=B[i].date()
        if unaPorDia and d in vistos: continue
        e=FIN[i]+1
        if e>=len(M): continue
        lado=int(s[i]); ent=OO[e]; rgo=kATR*A[i]
        rec = RR*rgo if RR>0 else abs((ph[i] if lado>0 else pl[i])-ent)
        if rec<=0: continue
        sl=ent-lado*rgo; tp=ent+lado*rec
        a,z2=e,min(e+HOR,len(M)); hh,ll=HH[a:z2],LL[a:z2]
        if lado>0: ks=np.nonzero(ll<=sl)[0]; kt=np.nonzero(hh>=tp)[0]
        else:      ks=np.nonzero(hh>=sl)[0]; kt=np.nonzero(ll<=tp)[0]
        fs=ks[0] if len(ks) else 10**9; ft=kt[0] if len(kt) else 10**9
        R=(rec/rgo) if ft<fs else (-1.0 if fs<10**9 else 0.0)
        ops.append((B[i], lado, rgo/U, rec/rgo, R)); vistos.add(d)
    D=pd.DataFrame(ops, columns="ts lado rgo rr R".split())
    if len(D): D["cr"]=coste/D.rgo; D["n"]=D.R-D.cr; D["dia"]=pd.to_datetime(D.ts).dt.floor("D")
    return D

def z(x,gr):
    m=x.mean(); su=pd.DataFrame({"x":x.to_numpy(),"g":gr.to_numpy()}).groupby("g").x.apply(lambda v:(v-m).sum())
    s2=float((su**2).sum()); return m*len(x)/sqrt(s2) if s2>0 else np.nan

print(f"{'':<40}{'n':>7}{'ops/día':>9}{'riesgo':>8}{'coste':>7}{'acierto':>9}{'geom':>7}"
      f"{'bruta':>9}{'NETA':>9}{'z':>7}")
def ficha(et,D,RR):
    if D is None or len(D)<30: return print(f"  {et:<38} (pocas)")
    geo=(D.rgo/(D.rgo+D.rr*D.rgo)).mean(); nd=D.dia.nunique()
    print(f"  {et:<38}{len(D):>7}{len(D)/nd:>9.1f}{D.rgo.median():>8.1f}{100*D.cr.mean():>6.1f}%"
          f"{100*(D.R>0).mean():>8.1f}%{100*geo:>6.1f}%{D.R.mean():>+9.4f}{D.n.mean():>+9.4f}"
          f"{z(D.n,D.dia.astype(str)):>+7.2f}")

for nom,ruta,U,coste in INS:
    print(f"\n=== {nom} ===")
    for k in (1.0, 1.5, 2.0):
        ficha(f"stop {k}xATR · R:R 2 · todas", corre(nom,ruta,U,coste,k,2.0), 2.0)
    print("  " + "-"*110)
    ficha("stop 1,5xATR · R:R 2 · UNA por día",  corre(nom,ruta,U,coste,1.5,2.0,False,True), 2.0)
    ficha("stop 1,5xATR · R:R 2 · solo Londres", corre(nom,ruta,U,coste,1.5,2.0,True,False), 2.0)
    ficha("stop 1,5xATR · R:R 2 · Londres+1/día",corre(nom,ruta,U,coste,1.5,2.0,True,True), 2.0)
    ficha("stop 1,5xATR · objetivo extremo opuesto", corre(nom,ruta,U,coste,1.5,-1,False,False), 2.0)
