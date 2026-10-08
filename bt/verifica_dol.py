"""Verificacion exhaustiva del filtro DOL. Es el momento de intentar tumbarlo."""
import sys, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0,"bt")
from estrategia_dol import C, senales, simular, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
ch = pd.read_parquet("data/ch_dol.parquet")
def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
def corre(chx=None, **kw):
    cfg=C(**kw); sig,_=senales(chx if chx is not None else ch, cfg); tr=simular(sig,m1,cfg)
    if not tr.empty: tr["b"]=(tr.pips+cfg.coste_pips)/tr.riesgo_pips
    return cfg, tr

cfg, tr = corre(dol_filtro=True, tp_r=3.0)
z,p = pz(tr.b)
print(f"BASE: {len(tr)} ops | bruto/op {tr.b.mean():+.4f} | z {z:+.2f} | p {p:.4f} "
      f"| R neto {tr.R.sum():+.2f}")

print("\n=== 1. FUERA DE MUESTRA ===")
mid = tr.ts.quantile(0.5)
for nom, sub in (("primera mitad", tr[tr.ts<=mid]), ("segunda mitad", tr[tr.ts>mid])):
    zz,pp = pz(sub.b)
    print(f"  {nom:16s} n {len(sub):>4} | bruto/op {sub.b.mean():+.4f} | z {zz:+.2f} "
          f"| p {pp:.3f} | R neto {sub.R.sum():+7.2f}")
print("\n  por ano:")
for a,g in tr.groupby(tr.ts.dt.year):
    print(f"    {a}: n {len(g):>3} | bruto/op {g.b.mean():+.4f} | R neto {g.R.sum():+7.2f}")

print("\n=== 2. PRUEBA DE FUGA TEMPORAL: retrasar el mapa DOL ===")
print("  Si la ventaja viene de informacion filtrada del futuro, retrasar el mapa la destruye.")
for lag in (0, 1, 4, 16, 96):
    c2 = ch.copy()
    for col in ("dol_up","dol_dn","dol_up_tf","dol_dn_tf"):
        c2[col] = c2[col].shift(lag)
    _, t2 = corre(chx=c2, dol_filtro=True, tp_r=3.0)
    if t2.empty or len(t2)<30: print(f"  lag {lag:>3}: pocas ops"); continue
    zz,pp = pz(t2.b)
    print(f"  retraso {lag:>3} velas M15 ({lag*15:>5} min): n {len(t2):>4} | "
          f"bruto/op {t2.b.mean():+.4f} | z {zz:+.2f} | p {pp:.3f}")

print("\n=== 3. CONTROL: DOL BARAJADO (rompe la relacion, conserva la distribucion) ===")
tots=[]
for s in range(20):
    rng = np.random.default_rng(s)
    c3 = ch.copy()
    perm = rng.permutation(len(c3))
    for col in ("dol_up","dol_dn","dol_up_tf","dol_dn_tf"):
        c3[col] = c3[col].to_numpy()[perm]
    _, t3 = corre(chx=c3, dol_filtro=True, tp_r=3.0)
    if t3.empty: continue
    tots.append(t3.b.mean())
tots=np.array(tots)
print(f"  20 barajados | bruto/op medio {tots.mean():+.4f} (sd {tots.std(ddof=1):.4f})")
print(f"  real         | bruto/op {tr.b.mean():+.4f} -> {(tr.b.mean()-tots.mean())/tots.std(ddof=1):+.2f} sigmas")

print("\n=== 4. ESPEJO Y ENTRADAS ALEATORIAS ===")
t1=m1["ts"].to_numpy(); HH=m1["high"].to_numpy(); LL=m1["low"].to_numpy(); CC=m1["close"].to_numpy()
def resolver(ets, ent, largo, riesgo, rr=3.0):
    sl=ent-riesgo if largo else ent+riesgo
    tp=ent+rr*riesgo if largo else ent-rr*riesgo
    i0=int(np.searchsorted(t1,ets)); i1=min(i0+168*60,len(t1))
    if i0>=len(t1) or i1<=i0: return None,None
    a,b=HH[i0:i1],LL[i0:i1]
    gsl,gtp=((b<=sl,a>=tp) if largo else (a>=sl,b<=tp))
    isl=int(np.argmax(gsl)) if gsl.any() else 10**9
    itp=int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl==10**9 and itp==10**9: sal,ifin=CC[i1-1],(i1-i0)-1
    elif isl<=itp: sal,ifin=sl,isl
    else: sal,ifin=tp,itp
    br=(sal-ent) if largo else (ent-sal)
    return (br/PIP-1.2)/(riesgo/PIP), t1[i0+ifin]
Rs,libre=[],np.datetime64("1970-01-01")
for r in tr.itertuples():
    ets=np.datetime64(pd.Timestamp(r.ts)+pd.Timedelta(minutes=15))
    if ets<libre: continue
    R,fin=resolver(ets,r.entrada,r.dir=="corto",r.riesgo_pips*PIP)
    if R is None: continue
    Rs.append(R); libre=fin
print(f"  espejo : {len(Rs)} ops | R total {np.sum(Rs):+8.2f}  (real {tr.R.sum():+.2f})")
horas = pd.DatetimeIndex(ch["ts"]).hour + pd.DatetimeIndex(ch["ts"]).minute/60
pool = ch[(horas>=6.5)&(horas<16)&ch["r_hi"].notna()].reset_index(drop=True)
riesgos = tr.riesgo_pips.to_numpy()*PIP
az=[]
for s in range(30):
    rng=np.random.default_rng(s); sel=np.sort(rng.choice(len(pool),size=len(tr),replace=False))
    R2,lb=[],np.datetime64("1970-01-01")
    for j,i in enumerate(sel):
        row=pool.iloc[i]; ets=np.datetime64(pd.Timestamp(row.ts)+pd.Timedelta(minutes=15))
        if ets<lb: continue
        R,fin=resolver(ets,row.close,rng.random()<0.5,riesgos[j%len(riesgos)])
        if R is None: continue
        R2.append(R); lb=fin
    R2=np.array(R2); az.append(R2.sum()/len(R2)*len(tr))
az=np.array(az)
print(f"  azar   : media {az.mean():+8.2f} (sd {az.std(ddof=1):.2f}) -> real a "
      f"{(tr.R.sum()-az.mean())/az.std(ddof=1):+.2f} sigmas")
tr.to_csv("data/trades_dol.csv", index=False)
