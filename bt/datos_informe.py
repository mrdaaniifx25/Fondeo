import sys, json, numpy as np, pandas as pd
sys.path.insert(0, "bt")
from estrategia_ls import Config, construir_senales, simular, metricas, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config()
m5, emb = construir_senales(m1, cfg)
tr, _ = simular(m5, m1, cfg)

# curvas de equity con y sin coste (1% de riesgo por operacion)
riesgo = tr.riesgo_pips.to_numpy()
R_con = tr.R.to_numpy()
R_sin = R_con + cfg.coste_pips / riesgo          # deshace el coste
def curva(Rs):
    eq, out = 10000.0, []
    for R in Rs:
        eq *= (1 + 0.01 * R); out.append(eq)
    return out
c_con, c_sin = curva(R_con), curva(R_sin)

paso = max(1, len(tr)//220)
idx = list(range(0, len(tr), paso)) + [len(tr)-1]
serie = [{"f": tr.ts.iloc[i].strftime("%Y-%m"), "n": i+1,
          "con": round(c_con[i], 1), "sin": round(c_sin[i], 1)} for i in idx]

# control de entradas aleatorias
t1 = m1["ts"].to_numpy(); HH, LL = m1["high"].to_numpy(), m1["low"].to_numpy()
CC = m1["close"].to_numpy()
pool = m5[m5.en_kz].reset_index(drop=True)
riesgos = riesgo * PIP
def resolver(ets, ent, corto, rg):
    sl = ent + rg if corto else ent - rg
    tp = ent - rg if corto else ent + rg
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
    return (bruto/PIP - cfg.coste_pips)/(rg/PIP), t1[i0+ifin]

azar = []
for semilla in range(30):
    rng = np.random.default_rng(semilla)
    sel = np.sort(rng.choice(len(pool), size=len(tr), replace=False))
    Rs, libre = [], np.datetime64("1970-01-01")
    for j, i in enumerate(sel):
        row = pool.iloc[i]; ets = np.datetime64(row.ts + pd.Timedelta(minutes=5))
        if ets < libre: continue
        R, fin = resolver(ets, row.close, rng.random() < 0.5, riesgos[j % len(riesgos)])
        if R is None: continue
        Rs.append(R); libre = fin
    Rs = np.array(Rs); azar.append(round(Rs.sum()/len(Rs)*len(tr), 1))

# espejo
Rs, libre = [], np.datetime64("1970-01-01")
for r in tr.itertuples():
    ets = np.datetime64(r.ts + pd.Timedelta(minutes=5))
    if ets < libre: continue
    R, fin = resolver(ets, r.entrada, r.dir == "largo", r.riesgo_pips*PIP)
    if R is None: continue
    Rs.append(R); libre = fin
espejo = round(float(np.sum(Rs)), 1)

datos = {
    "embudo": emb,
    "ops": int(len(tr)),
    "wr": round(100*float((tr.R>0).mean()), 2),
    "Rtot": round(float(tr.R.sum()), 2),
    "Rtot_sin": round(float(R_sin.sum()), 2),
    "eq_con": round(c_con[-1], 0), "eq_sin": round(c_sin[-1], 0),
    "serie": serie,
    "azar": azar, "azar_media": round(float(np.mean(azar)), 1),
    "azar_sd": round(float(np.std(azar, ddof=1)), 1),
    "espejo": espejo,
    "riesgo_med": round(float(tr.riesgo_pips.median()), 1),
    "por_ano": [{"a": int(a), "n": int(len(g)), "wr": round(100*float((g.R>0).mean()),1),
                 "R": round(float(g.R.sum()),1)} for a, g in tr.groupby(tr.ts.dt.year)],
}
json.dump(datos, open("data/informe_ls.json","w"), indent=1)
print(json.dumps({k:v for k,v in datos.items() if k not in ("serie","azar")}, indent=1))
print(f"\npuntos de curva: {len(serie)} | corridas azar: {len(azar)}")
