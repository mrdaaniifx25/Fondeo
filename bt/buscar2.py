import sys, pandas as pd
sys.path.insert(0,"bt")
from laboratorio import Motor, resumen, TRAIN
import candidatas as K
m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
tr_m1 = m1[(m1.ts>=TRAIN[0])&(m1.ts<=TRAIN[1])].reset_index(drop=True)
mo = Motor(tr_m1)
P=[]
for rr in (1.0,2.0,3.0):
    for sl in ("mid","opuesto"):
        P.append((f"A · ruptura Asia rr{rr} sl{sl}", lambda m,rr=rr,sl=sl: K.asia(m,False,rr,sl)))
    for f in (0.25,0.5):
        P.append((f"B · fade Asia rr{rr} sl{f}", lambda m,rr=rr,f=f: K.asia_fade(m,rr,f)))
    for b in (1.0,3.0):
        P.append((f"C · barrido PDH/PDL rr{rr} buf{b}", lambda m,rr=rr,b=b: K.pdhl(m,rr,b)))
    for mn in (30,60):
        P.append((f"D · ORB Londres rr{rr} {mn}min", lambda m,rr=rr,mn=mn: K.orb(m,rr,mn)))
        P.append((f"G · ORB compresion rr{rr} {mn}min", lambda m,rr=rr,mn=mn: K.orb_compr(m,rr,mn)))
    for k in (0.8,1.2):
        P.append((f"F · fade extension rr{rr} k{k}", lambda m,rr=rr,k=k: K.ext_fade(m,k,rr)))
for h in (0,4,7,12,16):
    for lg in (True,False):
        P.append((f"E · deriva h{h} {'largo' if lg else 'corto'}",
                  lambda m,h=h,lg=lg: K.deriva(m,h,6,lg)))
print(f"{'candidata':38s} {'n':>5s} {'WR':>6s} {'bruto/op':>9s} {'p':>7s} {'1a':>7s} {'2a':>7s} {'Rneto':>8s} {'PF':>6s}")
print("-"*104)
res=[]
for nom,fn in P:
    sig=fn(tr_m1)
    if sig.empty: continue
    r=resumen(mo.resolver(sig), nom)
    if r is None: continue
    res.append(r)
    print(f"{nom:38s} {r['n']:>5d} {r['wr']:>5.1f}% {r['bruto']:>+9.4f} {r['p']:>7.3f} "
          f"{r['h1']:>+7.3f} {r['h2']:>+7.3f} {r['Rneto']:>+8.2f} {r['pf']:>6.3f}")
df=pd.DataFrame(res); df.to_csv("data/train_candidatas.csv",index=False)
print(f"\nCANDIDATAS PROBADAS: {len(res)}")
el=df[(df.n>=150)&(df.h1>0)&(df.h2>0)].sort_values("bruto",ascending=False)
print("\n=== REGLA: n>=150 y las dos mitades positivas ===")
print(el[["etiqueta","n","wr","bruto","p","h1","h2","Rneto","pf"]].head(8).to_string(index=False)
      if not el.empty else "  ninguna cumple")
if not el.empty:
    print(f"\nGANADORA: {el.iloc[0].etiqueta}  (p en entrenamiento = {el.iloc[0].p:.3f})")
