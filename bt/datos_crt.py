import sys, json, numpy as np, pandas as pd
sys.path.insert(0, "bt")
from estrategia_crt import Config, marcos, senales, simular, metricas, PIP, _en_kz

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config(); ch = marcos(m1, cfg)
sig, emb = senales(ch, cfg); tr, _ = simular(sig, m1, cfg)

R_con = tr.R.to_numpy(); R_sin = R_con + cfg.coste_pips/tr.riesgo_pips.to_numpy()
def curva(Rs):
    eq, out = 10000.0, []
    for R in Rs: eq *= (1+0.01*R); out.append(eq)
    return out
c_con, c_sin = curva(R_con), curva(R_sin)
paso = max(1, len(tr)//220); idx = list(range(0, len(tr), paso)) + [len(tr)-1]
serie = [{"f": tr.ts.iloc[i].strftime("%Y-%m"), "n": i+1,
          "con": round(c_con[i],1), "sin": round(c_sin[i],1)} for i in idx]

# tramos de riesgo
tr2 = tr.copy(); tr2["R_bruto"] = (tr2.pips + cfg.coste_pips)/tr2.riesgo_pips
tr2["tramo"] = pd.cut(tr2.riesgo_pips, [0,12,18,25,35,1000],
                      labels=["<12","12-18","18-25","25-35",">35"])
g = tr2.groupby("tramo", observed=True).agg(ops=("R","size"), neto=("R","sum"), bruto=("R_bruto","sum"))
tramos = [{"t": str(i), "ops": int(r.ops), "neto": round(r.neto,1), "bruto": round(r.bruto,1)}
          for i, r in g.iterrows()]

# controles
t1 = m1["ts"].to_numpy(); HH=m1["high"].to_numpy(); LL=m1["low"].to_numpy(); CC=m1["close"].to_numpy()
pas = pd.Timedelta(cfg.chart)
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
    bruto=(sal-ent) if largo else (ent-sal)
    return (bruto/PIP-cfg.coste_pips)/(riesgo/PIP), t1[i0+ifin]

pool = ch[_en_kz(ch["ts"], cfg) & ch["r_hi"].notna()].reset_index(drop=True)
riesgos = tr.riesgo_pips.to_numpy()*PIP; rrs = tr.rr.to_numpy()
azar=[]
for s in range(30):
    rng=np.random.default_rng(s); sel=np.sort(rng.choice(len(pool),size=len(tr),replace=False))
    Rs,libre=[],np.datetime64("1970-01-01")
    for j,i in enumerate(sel):
        row=pool.iloc[i]; ets=np.datetime64(pd.Timestamp(row.ts)+pas)
        if ets<libre: continue
        R,fin=resolver(ets,row.close,rng.random()<0.5,riesgos[j%len(riesgos)],rrs[j%len(rrs)])
        if R is None: continue
        Rs.append(R); libre=fin
    Rs=np.array(Rs); azar.append(round(Rs.sum()/len(Rs)*len(tr),1))
Rs,libre=[],np.datetime64("1970-01-01")
for r in tr.itertuples():
    ets=np.datetime64(pd.Timestamp(r.ts)+pas)
    if ets<libre: continue
    R,fin=resolver(ets,r.entrada,r.dir=="corto",r.riesgo_pips*PIP,r.rr)
    if R is None: continue
    Rs.append(R); libre=fin
espejo=round(float(np.sum(Rs)),1)

d = {"embudo": emb, "ops": int(len(tr)), "wr": round(100*float((tr.R>0).mean()),2),
 "Rtot": round(float(tr.R.sum()),2), "Rtot_sin": round(float(R_sin.sum()),2),
 "eq_con": round(c_con[-1],0), "eq_sin": round(c_sin[-1],0), "serie": serie,
 "azar": azar, "azar_media": round(float(np.mean(azar)),1), "azar_sd": round(float(np.std(azar,ddof=1)),1),
 "espejo": espejo, "tramos": tramos,
 "rr_med": round(float(tr.rr.mean()),2), "rr_p50": round(float(tr.rr.median()),2),
 "riesgo_med": round(float(tr.riesgo_pips.mean()),1),
 "equilibrio": round(100*float((1/(1+tr[tr.motivo.isin(['TP','SL'])].rr)).mean()),2),
 "por_ano": [{"a":int(a),"n":int(len(x)),"wr":round(100*float((x.R>0).mean()),1),
              "R":round(float(x.R.sum()),1)} for a,x in tr.groupby(tr.ts.dt.year)]}
json.dump(d, open("data/informe_crt.json","w"), indent=1)
print(json.dumps({k:v for k,v in d.items() if k not in ("serie","azar")}, indent=1)[:1400])
