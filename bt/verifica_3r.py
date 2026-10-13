"""La unica configuracion en positivo: TP fijo 3R. ¿Sobrevive?"""
import sys, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0, "bt")
from estrategia_ob import Config, preparar, senales, simular, metricas, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
ch = preparar(m1, Config())
def corre(**kw):
    cfg = Config(**kw); sig,_ = senales(ch, cfg); tr,_ = simular(sig, m1, cfg); return cfg, tr
def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

cfg, tr = corre(tp_modo="R", tp_r=3.0)
tr["bruto"] = (tr.pips + cfg.coste_pips)/tr.riesgo_pips
z, p = pz(tr.bruto)
print("=== 1. SIGNIFICACION DEL BRUTO ===")
print(f"  n={len(tr)} | bruto/op {tr.bruto.mean():+.4f} | z {z:+.2f} | p {p:.4f}")
print(f"  umbral con correccion de Bonferroni para 14 variantes: p < {0.05/14:.4f}")
print(f"  -> {'SUPERA' if p < 0.05/14 else 'NO supera'} la correccion por comparaciones multiples")

print("\n=== 2. MISMOS SETUPS, DISTINTOS OBJETIVOS (muestra comparable) ===")
# fija la muestra con min_rr=0 para que el objetivo no cambie quien entra
base = dict(tp_modo="R", min_rr=0.0, max_rr=99)
for r in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0):
    c2, t2 = corre(**base, tp_r=r)
    b = (t2.pips + c2.coste_pips)/t2.riesgo_pips
    equil = 1/(1+r)
    wr = (t2.motivo=="TP").mean()
    zz, pp = pz(b)
    print(f"  TP {r:.1f}R | n {len(t2):>4} | WR {100*wr:5.2f}% (equilibrio {100*equil:5.2f}%) "
          f"| bruto/op {b.mean():+.4f} | z {zz:+5.2f} | p {pp:.3f}")

print("\n=== 3. PARTICION TEMPORAL (fuera de muestra) ===")
mid = tr.ts.quantile(0.5)
for nom, sub in (("2020 - mediados 2023", tr[tr.ts <= mid]), ("mediados 2023 - 2026", tr[tr.ts > mid])):
    zz, pp = pz(sub.bruto)
    gan, per = sub[sub.R>0], sub[sub.R<=0]
    pf = gan.R.sum()/(-per.R.sum())
    print(f"  {nom:24s} n {len(sub):>4} | WR {100*(sub.R>0).mean():5.2f}% "
          f"| R neto {sub.R.sum():+7.2f} | PF {pf:.3f} | bruto/op {sub.bruto.mean():+.4f} | p {pp:.3f}")

print("\n=== 4. POR ANO ===")
for a, g in tr.groupby(tr.ts.dt.year):
    print(f"  {a}: n {len(g):>4} | WR {100*(g.R>0).mean():5.2f}% | R neto {g.R.sum():+7.2f} "
          f"| bruto/op {g.bruto.mean():+.4f}")

print("\n=== 5. CONTROLES ===")
t1 = m1["ts"].to_numpy(); HH=m1["high"].to_numpy(); LL=m1["low"].to_numpy(); CC=m1["close"].to_numpy()
def resolver(ets, ent, largo, riesgo, rr):
    sl = ent-riesgo if largo else ent+riesgo
    tp = ent+rr*riesgo if largo else ent-rr*riesgo
    i0=int(np.searchsorted(t1,ets)); i1=min(i0+cfg.max_trade_horas*60,len(t1))
    if i0>=len(t1) or i1<=i0: return None,None
    a,b=HH[i0:i1],LL[i0:i1]
    gsl,gtp=((b<=sl,a>=tp) if largo else (a>=sl,b<=tp))
    isl=int(np.argmax(gsl)) if gsl.any() else 10**9
    itp=int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl==10**9 and itp==10**9: sal,ifin=CC[i1-1],(i1-i0)-1
    elif isl<=itp: sal,ifin=sl,isl
    else: sal,ifin=tp,itp
    br=(sal-ent) if largo else (ent-sal)
    return (br/PIP-cfg.coste_pips)/(riesgo/PIP), t1[i0+ifin]

Rs, libre = [], np.datetime64("1970-01-01")
for r in tr.itertuples():
    ets=np.datetime64(pd.Timestamp(r.ts)+pd.Timedelta(minutes=15))
    if ets<libre: continue
    R,fin=resolver(ets,r.entrada,r.dir=="corto",r.riesgo_pips*PIP,r.rr)
    if R is None: continue
    Rs.append(R); libre=fin
print(f"  espejo : {len(Rs):>4} ops | R total {np.sum(Rs):+8.2f}   (real {tr.R.sum():+8.2f})")

horas = pd.DatetimeIndex(ch["ts"]).hour + pd.DatetimeIndex(ch["ts"]).minute/60
pool = ch[(horas>=cfg.hora_ini)&(horas<cfg.hora_fin)&ch["r_hi"].notna()].reset_index(drop=True)
riesgos = tr.riesgo_pips.to_numpy()*PIP
tot=[]
for s in range(30):
    rng=np.random.default_rng(s); sel=np.sort(rng.choice(len(pool),size=len(tr),replace=False))
    Rs2,libre=[],np.datetime64("1970-01-01")
    for j,i in enumerate(sel):
        row=pool.iloc[i]; ets=np.datetime64(pd.Timestamp(row.ts)+pd.Timedelta(minutes=15))
        if ets<libre: continue
        R,fin=resolver(ets,row.close,rng.random()<0.5,riesgos[j%len(riesgos)],3.0)
        if R is None: continue
        Rs2.append(R); libre=fin
    Rs2=np.array(Rs2); tot.append(Rs2.sum()/len(Rs2)*len(tr))
tot=np.array(tot)
print(f"  azar   : media {tot.mean():+8.2f} (sd {tot.std(ddof=1):.2f}) "
      f"-> real a {(tr.R.sum()-tot.mean())/tot.std(ddof=1):+.2f} sigmas")
tr.to_csv("data/trades_ob_3r.csv", index=False)
