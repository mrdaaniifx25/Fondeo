"""Controles de la estrategia 2, identicos en metodo a los de la estrategia 1."""
import sys, numpy as np, pandas as pd
from math import erf, sqrt
sys.path.insert(0, "bt")
from estrategia_crt import Config, marcos, senales, simular, metricas, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config()
ch = marcos(m1, cfg)
sig, _ = senales(ch, cfg)
tr, _ = simular(sig, m1, cfg)

t1 = m1["ts"].to_numpy(); HH = m1["high"].to_numpy()
LL = m1["low"].to_numpy(); CC = m1["close"].to_numpy()
paso = pd.Timedelta(cfg.chart)

def resolver(ets, ent, largo, riesgo, rr):
    sl = ent - riesgo if largo else ent + riesgo
    tp = ent + rr*riesgo if largo else ent - rr*riesgo
    i0 = int(np.searchsorted(t1, ets)); i1 = min(i0+cfg.max_trade_horas*60, len(t1))
    if i0 >= len(t1) or i1 <= i0: return None, None
    a, b = HH[i0:i1], LL[i0:i1]
    gsl, gtp = ((b<=sl, a>=tp) if largo else (a>=sl, b<=tp))
    isl = int(np.argmax(gsl)) if gsl.any() else 10**9
    itp = int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl==10**9 and itp==10**9: sal, ifin = CC[i1-1], (i1-i0)-1
    elif isl <= itp: sal, ifin = sl, isl
    else: sal, ifin = tp, itp
    bruto = (sal-ent) if largo else (ent-sal)
    return (bruto/PIP - cfg.coste_pips)/(riesgo/PIP), t1[i0+ifin]

# ── espejo ──────────────────────────────────────────────────────────────────
print("=== ESPEJO (misma senal, direccion invertida, mismo riesgo y mismo R:R) ===")
Rs, libre = [], np.datetime64("1970-01-01")
for r in tr.itertuples():
    ets = np.datetime64(pd.Timestamp(r.ts) + paso)
    if ets < libre: continue
    R, fin = resolver(ets, r.entrada, r.dir == "corto", r.riesgo_pips*PIP, r.rr)
    if R is None: continue
    Rs.append(R); libre = fin
esp = np.array(Rs)
print(f"  real   : {len(tr):>5} ops | WR {100*(tr.R>0).mean():5.2f}% | R total {tr.R.sum():+8.2f}")
print(f"  espejo : {len(esp):>5} ops | WR {100*(esp>0).mean():5.2f}% | R total {esp.sum():+8.2f}")

# ── entradas aleatorias en la misma ventana horaria ─────────────────────────
print("\n=== ENTRADAS ALEATORIAS (misma ventana, mismo riesgo, mismo R:R) ===")
from estrategia_crt import _en_kz
pool = ch[_en_kz(ch["ts"], cfg) & ch["r_hi"].notna()].reset_index(drop=True)
riesgos = tr.riesgo_pips.to_numpy()*PIP; rrs = tr.rr.to_numpy()
tot, wrs = [], []
for semilla in range(30):
    rng = np.random.default_rng(semilla)
    idx = np.sort(rng.choice(len(pool), size=len(tr), replace=False))
    Rs, libre = [], np.datetime64("1970-01-01")
    for j, i in enumerate(idx):
        row = pool.iloc[i]
        ets = np.datetime64(pd.Timestamp(row.ts) + paso)
        if ets < libre: continue
        R, fin = resolver(ets, row.close, rng.random() < 0.5,
                          riesgos[j % len(riesgos)], rrs[j % len(rrs)])
        if R is None: continue
        Rs.append(R); libre = fin
    Rs = np.array(Rs); tot.append(Rs.sum()/len(Rs)*len(tr)); wrs.append(100*(Rs>0).mean())
tot, wrs = np.array(tot), np.array(wrs)
print(f"  30 corridas | WR medio {wrs.mean():5.2f}% | R total medio {tot.mean():+8.2f} (sd {tot.std(ddof=1):.2f})")
print(f"  real        | WR {100*(tr.R>0).mean():5.2f}% | R total {tr.R.sum():+8.2f}")
z = (tr.R.sum()-tot.mean())/tot.std(ddof=1)
print(f"  -> la real esta a {z:+.2f} sigmas del azar")

# ── win rate frente al equilibrio del R:R real de cada plan ────────────────
print("\n=== WIN RATE FRENTE AL EQUILIBRIO ===")
d = tr[tr.motivo.isin(["TP","SL"])]
p0 = (1/(1+d.rr)).mean()          # equilibrio medio ponderado por el R:R de cada plan
n, k = len(d), int((d.motivo=="TP").sum())
z = (k - n*p0)/sqrt(n*p0*(1-p0))
pv = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
print(f"  {k}/{n} = {100*k/n:.2f}% | equilibrio medio {100*p0:.2f}% | z = {z:+.2f} | p = {pv:.3f}")

# ── bruto por tramo de riesgo: aisla el efecto del coste ───────────────────
print("\n=== BRUTO (sin coste) POR TRAMO DE RIESGO ===")
tr2 = tr.copy()
tr2["R_bruto"] = (tr2.pips + cfg.coste_pips)/tr2.riesgo_pips
tr2["tramo"] = pd.cut(tr2.riesgo_pips, [0,12,18,25,35,1000],
                      labels=["<12","12-18","18-25","25-35",">35"])
g = tr2.groupby("tramo", observed=True).agg(ops=("R","size"), wr=("R", lambda s: 100*(s>0).mean()),
    R_neto=("R","sum"), R_bruto=("R_bruto","sum"))
print(g.round(2).to_string())
print("\n  Si el bruto ronda 0 en todos los tramos, la unica variable es el coste.")
