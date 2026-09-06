"""¿El order block aporta ventaja real, o solo ensancha el stop?"""
import sys, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0, "bt")
from estrategia_ob import Config, preparar, senales, simular, metricas, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
ch = preparar(m1, Config())

def corre(**kw):
    cfg = Config(**kw); sig, emb = senales(ch, cfg); tr, _ = simular(sig, m1, cfg)
    return cfg, tr

def bruto(tr, coste=1.2):
    return (tr.pips + coste)/tr.riesgo_pips

def resumen(nombre, tr):
    b = bruto(tr); n = len(b)
    se = b.std(ddof=1)/sqrt(n)
    z = b.mean()/se
    p = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
    print(f"  {nombre:26s} n={n:>5d} | bruto/op {b.mean():+.4f} "
          f"(ee {se:.4f}) | z {z:+5.2f} | p {p:.3f} | R bruto {b.sum():+8.2f}")
    return b

print("=== VENTAJA BRUTA POR OPERACION (sin coste), con su error estandar ===")
_, tr_sin = corre(usar_ob=False, usar_h1=True)
_, tr_con = corre(usar_ob=True,  usar_h1=True)
b_sin = resumen("sin order block", tr_sin)
b_con = resumen("con order block", tr_con)
dif = b_con.mean() - b_sin.mean()
se_d = sqrt(b_con.var(ddof=1)/len(b_con) + b_sin.var(ddof=1)/len(b_sin))
z = dif/se_d; p = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
print(f"\n  diferencia (con - sin) = {dif:+.4f} R/op | ee {se_d:.4f} | z {z:+.2f} | p {p:.3f}")

# --- controles sobre la version con order block -----------------------------
cfg = Config()
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

print("\n=== ESPEJO (misma senal, direccion invertida) ===")
Rs, libre = [], np.datetime64("1970-01-01")
for r in tr_con.itertuples():
    ets = np.datetime64(pd.Timestamp(r.ts)+pd.Timedelta(minutes=15))
    if ets < libre: continue
    R, fin = resolver(ets, r.entrada, r.dir=="corto", r.riesgo_pips*PIP, r.rr)
    if R is None: continue
    Rs.append(R); libre = fin
print(f"  real   {len(tr_con):>5} ops | WR {100*(tr_con.R>0).mean():5.2f}% | R total {tr_con.R.sum():+8.2f}")
print(f"  espejo {len(Rs):>5} ops | WR {100*(np.array(Rs)>0).mean():5.2f}% | R total {np.sum(Rs):+8.2f}")

print("\n=== ENTRADAS ALEATORIAS (mismo horario, mismo riesgo, mismo R:R) ===")
horas = pd.DatetimeIndex(ch["ts"]).hour + pd.DatetimeIndex(ch["ts"]).minute/60
pool = ch[(horas>=cfg.hora_ini)&(horas<cfg.hora_fin)&ch["r_hi"].notna()].reset_index(drop=True)
riesgos = tr_con.riesgo_pips.to_numpy()*PIP; rrs = tr_con.rr.to_numpy()
tot=[]
for s in range(30):
    rng=np.random.default_rng(s); sel=np.sort(rng.choice(len(pool),size=len(tr_con),replace=False))
    Rs,libre=[],np.datetime64("1970-01-01")
    for j,i in enumerate(sel):
        row=pool.iloc[i]; ets=np.datetime64(pd.Timestamp(row.ts)+pd.Timedelta(minutes=15))
        if ets<libre: continue
        R,fin=resolver(ets,row.close,rng.random()<0.5,riesgos[j%len(riesgos)],rrs[j%len(rrs)])
        if R is None: continue
        Rs.append(R); libre=fin
    Rs=np.array(Rs); tot.append(Rs.sum()/len(Rs)*len(tr_con))
tot=np.array(tot)
print(f"  30 corridas | R total medio {tot.mean():+8.2f} (sd {tot.std(ddof=1):.2f})")
print(f"  real        | R total {tr_con.R.sum():+8.2f}  -> {(tr_con.R.sum()-tot.mean())/tot.std(ddof=1):+.2f} sigmas")

print("\n=== ¿ES SOLO EL STOP MAS ANCHO? bruto por tramo de riesgo ===")
for nom, tr in (("sin OB", tr_sin), ("con OB", tr_con)):
    t = tr.copy(); t["b"] = bruto(t)
    t["tr"] = pd.cut(t.riesgo_pips, [0,8,12,18,30,1000], labels=["<8","8-12","12-18","18-30",">30"])
    g = t.groupby("tr", observed=True).agg(ops=("b","size"), bruto_op=("b","mean"))
    print(f"  {nom}: " + " | ".join(f"{i} {r.bruto_op:+.3f} ({int(r.ops)})" for i, r in g.iterrows()))
