import sys, json, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0, "bt")
from estrategia_ob import Config, preparar, senales, simular, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
ch = preparar(m1, Config())
def corre(**kw):
    cfg = Config(**kw); sig, emb = senales(ch, cfg); tr,_ = simular(sig, m1, cfg)
    if not tr.empty: tr["bruto"] = (tr.pips+cfg.coste_pips)/tr.riesgo_pips
    return cfg, tr, emb
def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

# --- escalera de objetivos, 3 niveles de filtro -----------------------------
niveles = [("CRT desnudo", dict(usar_ob=False, usar_h1=False)),
           ("+ confirmacion H1", dict(usar_ob=False, usar_h1=True)),
           ("+ order block M15", dict(usar_ob=True, usar_h1=True))]
esc = []
for nom, kw in niveles:
    pts = []
    for r in (1.0, 2.0, 3.0, 4.0):
        _, tr, _ = corre(**kw, tp_modo="R", tp_r=r, min_rr=0.0, max_rr=99, max_trade_horas=168)
        z, p = pz(tr.bruto)
        pts.append({"r": r, "b": round(float(tr.bruto.mean()), 4),
                    "p": round(float(p), 3), "n": int(len(tr))})
    esc.append({"nom": nom, "pts": pts})

# estrategia 2 como referencia
from estrategia_crt import Config as C2, marcos, senales as sen2, simular as sim2
ch2 = marcos(m1, C2()); c2 = C2(); c2.max_trade_horas = 168
sig2, _ = sen2(ch2, c2)
pts = []
for r in (1.0, 2.0, 3.0, 4.0):
    s = sig2.copy()
    s["tp"] = np.where(s.largo, s.entrada + r*(s.entrada-s.sl), s.entrada - r*(s.sl-s.entrada))
    s["rr"] = r
    t, _ = sim2(s, m1, c2)
    b = (t.pips + c2.coste_pips)/t.riesgo_pips
    z, p = pz(b)
    pts.append({"r": r, "b": round(float(b.mean()),4), "p": round(float(p),3), "n": int(len(t))})
esc.append({"nom": "Estrategia 2 (CRT Planner)", "pts": pts, "ref": True})

# --- mejor configuracion: TP 3R, tope 168 h ---------------------------------
cfg, tr, emb = corre(tp_modo="R", tp_r=3.0, min_rr=0.0, max_rr=99, max_trade_horas=168)
R_con = tr.R.to_numpy(); R_sin = tr.bruto.to_numpy()
def curva(Rs):
    eq, out = 10000.0, []
    for R in Rs: eq *= (1+0.01*R); out.append(eq)
    return out
c_con, c_sin = curva(R_con), curva(R_sin)
paso = max(1, len(tr)//220); idx = list(range(0, len(tr), paso)) + [len(tr)-1]
serie = [{"f": tr.ts.iloc[i].strftime("%Y-%m"), "n": i+1,
          "con": round(c_con[i],1), "sin": round(c_sin[i],1)} for i in idx]
z, p = pz(tr.bruto)
mid = tr.ts.quantile(0.5)
mit = []
for nom, sub in (("Primera mitad", tr[tr.ts<=mid]), ("Segunda mitad", tr[tr.ts>mid])):
    zz, pp = pz(sub.bruto)
    mit.append({"nom": nom, "n": int(len(sub)), "wr": round(100*float((sub.R>0).mean()),2),
                "R": round(float(sub.R.sum()),2), "b": round(float(sub.bruto.mean()),4),
                "p": round(float(pp),3)})

# controles
t1=m1["ts"].to_numpy(); HH=m1["high"].to_numpy(); LL=m1["low"].to_numpy(); CC=m1["close"].to_numpy()
def resolver(ets, ent, largo, riesgo, rr=3.0):
    sl = ent-riesgo if largo else ent+riesgo
    tp = ent+rr*riesgo if largo else ent-rr*riesgo
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
espejo = round(float(np.sum(Rs)),1)
horas = pd.DatetimeIndex(ch["ts"]).hour + pd.DatetimeIndex(ch["ts"]).minute/60
pool = ch[(horas>=cfg.hora_ini)&(horas<cfg.hora_fin)&ch["r_hi"].notna()].reset_index(drop=True)
riesgos = tr.riesgo_pips.to_numpy()*PIP
azar=[]
for s in range(30):
    rng=np.random.default_rng(s); sel=np.sort(rng.choice(len(pool),size=len(tr),replace=False))
    R2,libre=[],np.datetime64("1970-01-01")
    for j,i in enumerate(sel):
        row=pool.iloc[i]; ets=np.datetime64(pd.Timestamp(row.ts)+pd.Timedelta(minutes=15))
        if ets<libre: continue
        R,fin=resolver(ets,row.close,rng.random()<0.5,riesgos[j%len(riesgos)])
        if R is None: continue
        R2.append(R); libre=fin
    R2=np.array(R2); azar.append(round(float(R2.sum()/len(R2)*len(tr)),1))

d = {"escalera": esc, "serie": serie,
 "ops": int(len(tr)), "wr": round(100*float((tr.R>0).mean()),2),
 "Rtot": round(float(tr.R.sum()),2), "Rbruto": round(float(tr.bruto.sum()),2),
 "b_op": round(float(tr.bruto.mean()),4), "z": round(float(z),2), "p": round(float(p),4),
 "eq_con": round(c_con[-1],0), "eq_sin": round(c_sin[-1],0),
 "riesgo": round(float(tr.riesgo_pips.mean()),1),
 "mitades": mit, "espejo": espejo, "azar": azar,
 "azar_media": round(float(np.mean(azar)),1), "azar_sd": round(float(np.std(azar,ddof=1)),1),
 "embudo": emb,
 "por_ano": [{"a":int(a),"n":int(len(g)),"wr":round(100*float((g.R>0).mean()),1),
              "R":round(float(g.R.sum()),1),"b":round(float(g.bruto.mean()),3)}
             for a,g in tr.groupby(tr.ts.dt.year)]}
json.dump(d, open("data/informe_ob.json","w"), indent=1)
print(json.dumps({k:v for k,v in d.items() if k not in ("serie","azar","escalera")}, indent=1))
