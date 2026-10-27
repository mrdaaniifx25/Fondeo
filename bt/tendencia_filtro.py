"""Pre-registro docs/PREREGISTRO_tendencia_filtro.md

Su estrategia (barrido del rango de Asia en Londres) filtrada por SIETE
medidas de tendencia causales, con el oraculo al lado como techo.

  python3 bt/tendencia_filtro.py
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, KATR, RR, HOR = 1e-4, 0.70, 1.5, 2.0, 6*60
M = pd.read_parquet("data/eurusd_m1.parquet")
M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
loc = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
M["dia"] = loc.dt.floor("D"); M["h"] = loc.dt.hour + loc.dt.minute/60.0
HH, LL, OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()

# ---- velas diarias y H4 para los filtros ----
d = M.groupby("dia").agg(o=("open","first"), c=("close","last"))
d["ema20"] = d.c.ewm(span=20, adjust=False).mean()
d["ema50"] = d.c.ewm(span=50, adjust=False).mean()
FIL = {}
FIL["EMA(20) diaria"]      = np.sign(d.c - d.ema20).shift(1)
FIL["EMA(50) diaria"]      = np.sign(d.c - d.ema50).shift(1)
FIL["ROC 5 días"]          = np.sign(d.c.diff(5)).shift(1)
FIL["ROC 20 días"]         = np.sign(d.c.diff(20)).shift(1)
FIL["día anterior"]        = np.sign(d.c - d.o).shift(1)
sem = d.assign(s=pd.PeriodIndex(d.index, freq="W")).groupby("s").c.agg(["first","last"])
FIL["semana anterior"]     = pd.Series(pd.PeriodIndex(d.index, freq="W")).map(
    np.sign(sem["last"]-sem["first"]).shift(1)).set_axis(d.index)
h4 = M.assign(k=loc.dt.floor("240min")).groupby("k").c4 if False else None
q4 = M.assign(k=loc.dt.floor("240min")).groupby("k").agg(c=("close","last"))
q4["e"] = q4.c.ewm(span=50, adjust=False).mean()
s4 = np.sign(q4.c - q4.e).shift(1)
# oraculo: direccion REAL de la semana (mira al futuro a proposito)
FIL["ORÁCULO (futuro)"]    = pd.Series(pd.PeriodIndex(d.index, freq="W")).map(
    np.sign(sem["last"]-sem["first"])).set_axis(d.index)

# ---- velas M15 y la senal ----
g = M.assign(k=loc.dt.floor("15min")).groupby("k", sort=True)
b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
          fin=("high", lambda x: x.index[-1]))
b = b[b.index.notna()]
tr = pd.concat([b.h-b.l,(b.h-b.c.shift(1)).abs(),(b.l-b.c.shift(1)).abs()],axis=1).max(axis=1)
b["atr"] = tr.rolling(14).mean().shift(1)
B = b.index; hb = B.hour + B.minute/60.0
O15,H15,L15,C15,A15 = (b[k].to_numpy() for k in ("o","h","l","c","atr"))
FIN = b.fin.to_numpy().astype(int)
dib = pd.Series(B).dt.floor("D")
asia = M[(M.h>=0)&(M.h<8)].groupby("dia").agg(ah=("high","max"), al=("low","min"))
AH = dib.map(asia.ah).to_numpy(); AL = dib.map(asia.al).to_numpy()
k4 = pd.Series(B).dt.floor("240min")
S4 = k4.map(s4).to_numpy()

ops, vistos = [], set()
for i in range(20, len(b)-1):
    if not (8 <= hb[i] < 11): continue
    if not np.isfinite(A15[i]) or A15[i] <= 0: continue
    if not (np.isfinite(AH[i]) and np.isfinite(AL[i])): continue
    lado = 0
    if H15[i] >= AH[i] and C15[i] < AH[i] and L15[i] > AL[i]: lado = -1
    elif L15[i] <= AL[i] and C15[i] > AL[i] and H15[i] < AH[i]: lado = 1
    if lado == 0: continue
    key = (B[i].date(), lado)
    if key in vistos: continue
    vistos.add(key)
    e = FIN[i]+1
    if e >= len(M): continue
    ent = OO[e]; rgo = KATR*A15[i]; rec = RR*rgo
    sl = ent-lado*rgo; tp = ent+lado*rec
    a,z2 = e, min(e+HOR, len(M)); hh,ll = HH[a:z2], LL[a:z2]
    if lado>0: ks=np.nonzero(ll<=sl)[0]; kt=np.nonzero(hh>=tp)[0]
    else:      ks=np.nonzero(hh>=sl)[0]; kt=np.nonzero(ll<=tp)[0]
    fs=ks[0] if len(ks) else 10**9; ft=kt[0] if len(kt) else 10**9
    R = RR if ft<fs else (-1.0 if fs<10**9 else 0.0)
    ops.append((B[i], dib[i], lado, rgo/U, R, S4[i]))
D = pd.DataFrame(ops, columns="ts dia lado rgo R s4".split())
D["cr"] = COSTE/D.rgo; D["n"] = D.R - D.cr
for k, v in FIL.items(): D[k] = D.dia.map(v)
D["EMA(50) de H4"] = D.s4
print(f"operaciones: {len(D):,}   días: {D.dia.nunique():,}\n")

def z(x, gr):
    m=x.mean(); su=pd.DataFrame({"x":x.to_numpy(),"g":gr.to_numpy()}).groupby("g").x.apply(lambda v:(v-m).sum())
    s2=float((su**2).sum()); return m*len(x)/sqrt(s2) if s2>0 else np.nan
def ficha(et, S, ind="  "):
    if len(S)<40: return print(f"{ind}{et:<26} (pocas: {len(S)})")
    print(f"{ind}{et:<26}{len(S):>6}{100*(S.R>0).mean():>9.1f}%{100*S.cr.mean():>7.1f}%"
          f"{S.R.mean():>+9.4f}{S.n.mean():>+9.4f}{z(S.n,S.dia.astype(str)):>+7.2f}")

CAB = f"  {'':<26}{'n':>6}{'acierto':>10}{'coste':>7}{'bruta':>9}{'NETA':>9}{'z':>7}"
print("="*88); print("SIN FILTRO (su estrategia tal cual)"); print("="*88)
print(CAB); ficha("todas", D)
print(f"\n  (nulo geométrico con R:R 2: 33,3 %)")

orden = ["EMA(20) diaria","EMA(50) diaria","ROC 5 días","ROC 20 días",
         "día anterior","semana anterior","EMA(50) de H4","ORÁCULO (futuro)"]
print("\n" + "="*88); print("CON FILTRO DE TENDENCIA"); print("="*88)
for k in orden:
    S = D[D[k].notna() & (D[k] != 0)]
    if len(S) < 80: continue
    af = S[S.lado == S[k]]; ct = S[S.lado == -S[k]]
    print(f"\n  {k}"); print(CAB)
    ficha("a favor", af, "    ")
    ficha("en contra", ct, "    ")
    if len(af) >= 40 and len(ct) >= 40:
        print(f"    {'diferencia a favor-contra':<26}{'':>6}"
              f"{100*((af.R>0).mean()-(ct.R>0).mean()):>+8.1f}pp{'':>7}"
              f"{af.R.mean()-ct.R.mean():>+9.4f}{af.n.mean()-ct.n.mean():>+9.4f}")

print("\n" + "="*88); print("RESUMEN · brazo «a favor» de cada filtro"); print("="*88)
print(f"  {'filtro':<26}{'n':>6}{'acierto':>10}{'NETA':>10}{'vs sin filtro':>15}")
base = D.n.mean()
for k in orden:
    S = D[D[k].notna() & (D[k]!=0)]; af = S[S.lado == S[k]]
    if len(af) < 40: continue
    print(f"  {k:<26}{len(af):>6}{100*(af.R>0).mean():>9.1f}%{af.n.mean():>+10.4f}"
          f"{af.n.mean()-base:>+15.4f}")
print(f"  {'SIN FILTRO':<26}{len(D):>6}{100*(D.R>0).mean():>9.1f}%{base:>+10.4f}{0.0:>+15.4f}")
