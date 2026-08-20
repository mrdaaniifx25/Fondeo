"""Controles limpios:
  B1) ESPEJO: mismas velas, direccion siempre invertida.
  B2) BARRAS ALEATORIAS: entradas al azar dentro de la misma ventana horaria,
      con la misma distribucion de distancias de stop.  Aisla si el momento
      elegido aporta algo.
  C ) Prueba binomial (aproximacion normal) del win rate frente al equilibrio.
"""
import sys, numpy as np, pandas as pd
from math import erf, sqrt
sys.path.insert(0, "bt")
from estrategia_ls import Config, construir_senales, simular, metricas, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config()
m5, _ = construir_senales(m1, cfg)
tr, _ = simular(m5, m1, cfg)

t1 = m1["ts"].to_numpy(); HH, LL = m1["high"].to_numpy(), m1["low"].to_numpy()
CC = m1["close"].to_numpy()

def resolver(ets, ent, corto, riesgo, coste=cfg.coste_pips, rr=cfg.rr):
    sl = ent + riesgo if corto else ent - riesgo
    tp = ent - rr*riesgo if corto else ent + rr*riesgo
    i0 = int(np.searchsorted(t1, ets)); i1 = min(i0+cfg.max_trade_horas*60, len(t1))
    if i0 >= len(t1) or i1 <= i0: return None, None
    a, b = HH[i0:i1], LL[i0:i1]
    gsl, gtp = (a>=sl, b<=tp) if corto else (b<=sl, a>=tp)
    isl = int(np.argmax(gsl)) if gsl.any() else 10**9
    itp = int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl==10**9 and itp==10**9: sal, ifin = CC[i1-1], (i1-i0)-1
    elif isl <= itp: sal, ifin = sl, isl
    else: sal, ifin = tp, itp
    bruto = (ent-sal) if corto else (sal-ent)
    return (bruto/PIP - coste)/(riesgo/PIP), t1[i0+ifin]

# ── B1) espejo ──────────────────────────────────────────────────────────────
print("=== B1) ESTRATEGIA ESPEJO (misma senal, direccion invertida) ===")
Rs, libre = [], np.datetime64("1970-01-01")
for r in tr.itertuples():
    ets = np.datetime64(r.ts + pd.Timedelta(minutes=5))
    if ets < libre: continue
    R, fin = resolver(ets, r.entrada, r.dir == "largo", r.riesgo_pips*PIP)
    if R is None: continue
    Rs.append(R); libre = fin
esp = np.array(Rs)
print(f"  real   : {len(tr):>5} ops | WR {100*(tr.R>0).mean():5.2f}% | R total {tr.R.sum():+8.2f}")
print(f"  espejo : {len(esp):>5} ops | WR {100*(esp>0).mean():5.2f}% | R total {esp.sum():+8.2f}")
print(f"  suma de ambos = {tr.R.sum()+esp.sum():+.2f}R  (si no hubiera ventaja")
print(f"     seria aprox. -2 x coste/riesgo x N = {-2*cfg.coste_pips/tr.riesgo_pips.mean()*len(tr):+.2f}R)")

# ── B2) barras aleatorias en la misma ventana horaria ───────────────────────
print("\n=== B2) ENTRADAS ALEATORIAS EN LA MISMA VENTANA HORARIA ===")
pool = m5[m5.en_kz].reset_index(drop=True) if cfg.solo_kz else m5.reset_index(drop=True)
riesgos = tr.riesgo_pips.to_numpy()*PIP
tot, wrs = [], []
for semilla in range(30):
    rng = np.random.default_rng(semilla)
    idx = rng.choice(len(pool), size=len(tr), replace=False)
    idx.sort()
    Rs, libre = [], np.datetime64("1970-01-01")
    for j, i in enumerate(idx):
        row = pool.iloc[i]
        ets = np.datetime64(row.ts + pd.Timedelta(minutes=5))
        if ets < libre: continue
        R, fin = resolver(ets, row.close, rng.random() < 0.5, riesgos[j % len(riesgos)])
        if R is None: continue
        Rs.append(R); libre = fin
    Rs = np.array(Rs); tot.append(Rs.sum()/len(Rs)*len(tr)); wrs.append(100*(Rs>0).mean())
tot, wrs = np.array(tot), np.array(wrs)
print(f"  30 corridas | WR medio {wrs.mean():5.2f}% (sd {wrs.std():.2f})")
print(f"              | R total medio {tot.mean():+8.2f} (sd {tot.std():.2f})")
print(f"  real        | WR {100*(tr.R>0).mean():5.2f}%   R total {tr.R.sum():+8.2f}")
print(f"  -> la real esta a {(tr.R.sum()-tot.mean())/tot.std(ddof=1):+.2f} sigmas del azar")

# ── C) binomial ─────────────────────────────────────────────────────────────
print("\n=== C) PRUEBA BINOMIAL DEL WIN RATE ===")
for rr, nombre in ((1.0,"1R"), (2.0,"2R"), (3.0,"3R")):
    c2 = Config(rr=rr); m5b,_ = construir_senales(m1,c2); trb,_ = simular(m5b,m1,c2)
    d = trb[trb.motivo.isin(["TP","SL"])]
    n, k = len(d), int((d.motivo=="TP").sum())
    p0 = 1/(1+rr)
    z = (k - n*p0)/sqrt(n*p0*(1-p0))
    pv = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
    print(f"  TP {nombre}: {k}/{n} = {100*k/n:5.2f}% | equilibrio {100*p0:5.2f}% "
          f"| z = {z:+5.2f} | p = {pv:.3f}")
print("  p alto = el win rate es indistinguible del punto de equilibrio.")
