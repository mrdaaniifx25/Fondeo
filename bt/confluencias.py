"""H1-H5 del pre-registro. Filtros multiactivo sobre los setups CRT+DOL.
Se evaluan SOLO en entrenamiento 2020-2023. La reserva no se abre aqui."""
import numpy as np, pandas as pd
from math import sqrt, erf
import sys; sys.path.insert(0,"bt")

PIP=0.0001; COSTE=1.2
TR=("2020-01-01","2023-12-31"); TE=("2024-01-01","2026-07-31")

eur = pd.read_parquet("data/eurusd_m1.parquet"); eur["ts"]=pd.to_datetime(eur["ts"])
gbp = pd.read_parquet("data/gbpusd_m1.parquet"); gbp["ts"]=pd.to_datetime(gbp["ts"])
jpy = pd.read_parquet("data/usdjpy_m1.parquet"); jpy["ts"]=pd.to_datetime(jpy["ts"])

def rasgos(m1, pref, ancla=1):
    """Por cada vela M15: extremos acumulados de la vela H4 en curso y extremos
    de la H4 anterior, mas el retorno de las ultimas 24 h."""
    ch = m1.set_index("ts").resample("15min", label="left", closed="left").agg(
        high=("high","max"), low=("low","min"), close=("close","last")).dropna().reset_index()
    org = pd.Timestamp("2020-01-01")+pd.Timedelta(hours=ancla)
    h4 = m1.set_index("ts").resample("4h", origin=org, label="left", closed="left").agg(
        high=("high","max"), low=("low","min")).dropna().reset_index()
    h4["p_hi"], h4["p_lo"] = h4.high.shift(1), h4.low.shift(1)
    ch["h4_id"] = (ch["ts"]-pd.Timedelta(hours=ancla)).dt.floor("4h")+pd.Timedelta(hours=ancla)
    ch = ch.merge(h4[["ts","p_hi","p_lo"]].rename(columns={"ts":"h4_id"}), on="h4_id", how="left")
    ch["run_hi"] = ch.groupby("h4_id")["high"].cummax()
    ch["run_lo"] = ch.groupby("h4_id")["low"].cummin()
    ch["r24"] = ch["close"]/ch["close"].shift(96) - 1
    ch["atr_d"] = (ch["high"]-ch["low"]).rolling(96).mean()*4
    return ch[["ts","h4_id","close","p_hi","p_lo","run_hi","run_lo","r24","atr_d"]]\
             .rename(columns={c:f"{pref}_{c}" for c in
                     ("close","p_hi","p_lo","run_hi","run_lo","r24","atr_d")})

print("construyendo rasgos por par...")
fe = rasgos(eur,"e").merge(rasgos(gbp,"g").drop(columns=["h4_id"]), on="ts", how="inner")
fe = fe.merge(rasgos(jpy,"j").drop(columns=["h4_id"]), on="ts", how="inner")

# correlacion movil de 20 dias (solo dias cerrados)
de = np.log(eur.set_index("ts").close.resample("1D").last().dropna()).diff()
dg = np.log(gbp.set_index("ts").close.resample("1D").last().dropna()).diff()
cor = de.rolling(20).corr(dg).shift(1).rename("corr20").reset_index()
cor["dia"] = pd.DatetimeIndex(cor["ts"]).normalize()
fe["dia"] = pd.DatetimeIndex(fe["ts"]).normalize()
fe = fe.merge(cor[["dia","corr20"]], on="dia", how="left")
print(f"rasgos: {len(fe):,} velas M15\n")

# ── setups base: CRT + order block + DOL diario estricto ────────────────────
ch_dol = pd.read_parquet("data/ch_dol.parquet")
src = open("bt/estrategia_dol.py").read().replace("if d_fav > d_con: continue",
                                                  "if d_fav > 0.5*d_con: continue")
ns={}; exec(compile(src,"m","exec"), ns)
cfg = ns["C"](dol_filtro=True, tp_r=3.0)
sig,_ = ns["senales"](ch_dol, cfg)
sig = sig.merge(fe, on="ts", how="left")
print(f"setups base: {len(sig)}  (con rasgos: {sig.e_p_hi.notna().sum()})")

# ── definicion de las hipotesis ────────────────────────────────────────────
def cond(s, h):
    L = s.largo
    if h=="H1a":   # SMT estricto con GBPUSD
        return np.where(L, s.g_run_lo >= s.g_p_lo, s.g_run_hi <= s.g_p_hi)
    if h=="H1b":   # SMT laxo: el barrido de GBPUSD es mas superficial
        pe = np.where(L, (s.e_p_lo-s.e_run_lo), (s.e_run_hi-s.e_p_hi))/s.e_atr_d
        pg = np.where(L, (s.g_p_lo-s.g_run_lo), (s.g_run_hi-s.g_p_hi))/s.g_atr_d
        return pg < pe
    if h=="H2a":   # SMT con USDJPY invertido, estricto
        return np.where(L, s.j_run_hi <= s.j_p_hi, s.j_run_lo >= s.j_p_lo)
    if h=="H2b":   # laxo
        pe = np.where(L, (s.e_p_lo-s.e_run_lo), (s.e_run_hi-s.e_p_hi))/s.e_atr_d
        pj = np.where(L, (s.j_run_hi-s.j_p_hi), (s.j_p_lo-s.j_run_lo))/s.j_atr_d
        return pj < pe
    if h=="H3a":   # confluencia de barrido en la misma vela H4
        return np.where(L, s.g_run_lo < s.g_p_lo, s.g_run_hi > s.g_p_hi)
    if h=="H3b":   # confluencia en los dos pares Y en el yen
        c1 = np.where(L, s.g_run_lo < s.g_p_lo, s.g_run_hi > s.g_p_hi)
        c2 = np.where(L, s.j_run_hi > s.j_p_hi, s.j_run_lo < s.j_p_lo)
        return c1 & c2
    if h=="H4a":   # fuerza relativa del euro frente a la libra
        return np.where(L, s.e_r24 > s.g_r24, s.e_r24 < s.g_r24)
    if h=="H4b":   # con umbral
        d = (s.e_r24 - s.g_r24)
        u = 0.0025
        return np.where(L, d > u, d < -u)
    if h=="H5a":   # correlacion desacoplada (por debajo de la mediana)
        return s.corr20 < s.corr20.median()
    if h=="H5b":   # muy desacoplada (cuartil inferior)
        return s.corr20 < s.corr20.quantile(0.25)
    raise ValueError(h)

# ── motor ──────────────────────────────────────────────────────────────────
T=eur["ts"].to_numpy(); H=eur["high"].to_numpy(); L_=eur["low"].to_numpy(); C=eur["close"].to_numpy()
def simula(s):
    out, libre = [], np.datetime64("1970-01-01")
    for r in s.itertuples():
        ets=np.datetime64(pd.Timestamp(r.ts)+pd.Timedelta(minutes=15))
        if ets<libre: continue
        i0=int(np.searchsorted(T,ets)); i1=min(i0+168*60,len(T))
        if i0>=len(T) or i1<=i0: continue
        a,b=H[i0:i1],L_[i0:i1]
        gsl,gtp=((b<=r.sl,a>=r.tp) if r.largo else (a>=r.sl,b<=r.tp))
        isl=int(np.argmax(gsl)) if gsl.any() else 10**9
        itp=int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl==10**9 and itp==10**9: sal,ifin=C[i1-1],(i1-i0)-1
        elif isl<=itp: sal,ifin=r.sl,isl
        else: sal,ifin=r.tp,itp
        br=(sal-r.entrada) if r.largo else (r.entrada-sal)
        rp=r.riesgo_pips
        out.append(dict(ts=r.ts, R=(br/PIP-COSTE)/rp, bruto=(br/PIP)/rp))
        libre=T[i0+ifin]
    return pd.DataFrame(out)

def pz(x):
    n=len(x)
    if n<3: return 0,1
    se=x.std(ddof=1)/sqrt(n); z=x.mean()/se if se>0 else 0
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

def ev(s, nom):
    tr = simula(s)
    if tr.empty or len(tr)<20: return None
    z,p = pz(tr.bruto); h=len(tr)//2
    gan,per = tr[tr.R>0], tr[tr.R<=0]
    pf = gan.R.sum()/(-per.R.sum()) if per.R.sum()<0 else float("inf")
    return dict(h=nom, n=len(tr), bruto=float(tr.bruto.mean()), z=float(z), p=float(p),
                h1=float(tr.bruto.iloc[:h].mean()), h2=float(tr.bruto.iloc[h:].mean()),
                Rneto=float(tr.R.sum()), pf=float(pf))

s_tr = sig[(sig.ts>=TR[0])&(sig.ts<=TR[1])].copy()
print(f"setups en entrenamiento: {len(s_tr)}\n")
base = ev(s_tr, "SIN FILTRO (referencia)")
print(f"{'hipotesis':30s} {'n':>4s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'1a':>7s} {'2a':>7s} {'PF':>6s}")
print("-"*82)
def linea(r):
    if r is None: print("   (muestra insuficiente)"); return
    print(f"{r['h']:30s} {r['n']:>4d} {r['bruto']:>+9.4f} {r['z']:>+6.2f} {r['p']:>7.3f} "
          f"{r['h1']:>+7.3f} {r['h2']:>+7.3f} {r['pf']:>6.3f}")
linea(base)
print("-"*82)
res=[]
for h in ("H1a","H1b","H2a","H2b","H3a","H3b","H4a","H4b","H5a","H5b"):
    m = cond(s_tr, h)
    r = ev(s_tr[np.asarray(m, dtype=bool)], h)
    linea(r)
    if r: res.append(r)
pd.DataFrame(res).to_csv("data/h_train.csv", index=False)
print(f"\nCONTRASTES EJECUTADOS: {len(res)} + 1 (H6) = {len(res)+1}  (tope declarado: 12)")

print("\n=== REGLA DECLARADA ===")
print("   n>=150 | bruto > +0.2584 | ambas mitades positivas")
df = pd.DataFrame(res)
el = df[(df.n>=150)&(df.bruto>0.2584)&(df.h1>0)&(df.h2>0)].sort_values("bruto",ascending=False)
if el.empty:
    print("   NINGUNA hipotesis cumple la regla.")
    cerca = df[(df.n>=150)].sort_values("bruto",ascending=False).head(3)
    print("\n   las tres de mayor ventaja con n suficiente, para el registro:")
    print(cerca[["h","n","bruto","p","h1","h2"]].to_string(index=False))
else:
    print(el[["h","n","bruto","p","h1","h2","pf"]].to_string(index=False))
    print(f"\n   GANADORA: {el.iloc[0].h}")
