"""docs/PREREGISTRO_barrido.md · una sola vez."""
import numpy as np, pandas as pd
U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"
VENTANA, FIN = (800, 1130), 2200

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), ts=("ts","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date; v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
O,H,L,C = v.o.to_numpy(), v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()

# --- niveles ---------------------------------------------------------------
asia, londres = {}, {}
for dia, g in v.groupby("dia"):
    a = g[g.hm < 800]
    if len(a) >= 60: asia[dia] = (float(a.h.max()), float(a.l.min()))
    lo_ = g[(g.hm >= 900) & (g.hm < 1730)]
    if len(lo_) >= 60: londres[dia] = (float(lo_.h.max()), float(lo_.l.min()))
dias = sorted(londres)
prevL = {d: londres[dias[i-1]] for i, d in enumerate(dias) if i > 0}

ts1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
finDia = m1["loc"].dt.date.to_numpy(); finHM = (m1["loc"].dt.hour*100 + m1["loc"].dt.minute).to_numpy()

def busca(niveles, nom):
    filas = []
    for dia, g in v.groupby("dia"):
        if dia not in niveles: continue
        hi, lo = niveles[dia]
        if not (hi > lo): continue
        W = g[(g.hm >= VENTANA[0]) & (g.hm < VENTANA[1])]
        for i in W.index:
            for niv, lado in ((hi, -1), (lo, 1)):
                pincha = (H[i] > niv) if lado < 0 else (L[i] < niv)
                vuelve = (C[i] < niv) if lado < 0 else (C[i] > niv)
                if not (pincha and vuelve): continue
                ent = C[i]
                stp = (H[i] + U) if lado < 0 else (L[i] - U)
                rgo = abs(ent - stp)
                if rgo <= 0: continue
                filas.append(dict(dia=dia, i=int(i), lado=lado, nivel=("alto" if lado < 0 else "mínimo"),
                                  entrada=ent, stop=stp, riesgo=rgo/U, mecha=abs(H[i]-niv if lado<0 else niv-L[i])/U))
                break
            else: continue
            break                                        # una por dia: la primera
    t = pd.DataFrame(filas)
    t["ts"] = pd.to_datetime(v.ts.to_numpy()[t.i])
    return t

def resuelve(t, ancho=0.0, k=2.0):
    R, mot = [], []
    for r in t.itertuples():
        rgo = max(r.riesgo, ancho) * U
        stp = r.entrada - rgo*r.lado; tp = r.entrada + k*rgo*r.lado
        j0 = int(np.searchsorted(ts1, np.datetime64(r.ts), side="right"))
        f = np.where((finDia[j0:] != r.dia) | (finHM[j0:] >= FIN))[0]
        j1 = min(max(j0 + (int(f[0]) if len(f) else len(ts1)-j0), j0+1), len(C1))
        hh, ll = H1[j0:j1], L1[j0:j1]
        gt, gs = ((hh >= tp, ll <= stp) if r.lado > 0 else (ll <= tp, hh >= stp))
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = C1[j1-1]
            R.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/rgo); mot.append("cierre")
        elif isl <= it: R.append(-1.0); mot.append("SL")
        else: R.append(float(k)); mot.append("TP")
    d = t.assign(R=R, motivo=mot, rgoP=np.maximum(t.riesgo, ancho))
    d["neto"] = d.R - COSTE/d.rgoP
    return d

def linea(et, d, ini, fin):
    s = d[(d.ts >= ini) & (d.ts < fin)]
    if len(s) < 30: print(f"  {et:<32} n insuficiente ({len(s)})"); return
    sn = s.groupby("dia").neto.sum(); sb = s.groupby("dia").R.sum()
    e1 = sb.std(ddof=1)/np.sqrt(len(sb)); e2 = sn.std(ddof=1)/np.sqrt(len(sn))
    pm = len(sn)/((pd.to_datetime(s.ts.max())-pd.to_datetime(s.ts.min())).days/30.44)
    g, p = s.neto[s.neto > 0].sum(), -s.neto[s.neto < 0].sum()
    print(f"  {et:<32}{len(s):>6,}{s.rgoP.median():>7.1f}p{100*(s.motivo=='TP').mean():>7.1f}%"
          f"{s.R.mean():>+9.3f}{sb.mean():>+9.3f}{sb.mean()/e1:>+7.2f}{sn.mean():>+10.3f}"
          f"{sn.mean()/e2:>+7.2f}{g/p:>7.2f}{sn.mean()*100*pm:>+8.0f}€".replace(",","."))

for nom, niveles in (("ASIA (contraste principal)", asia), ("LONDRES DEL DÍA ANTERIOR", prevL)):
    t = busca(niveles, nom)
    print("\n" + "="*118); print(nom + f"   ·   {len(t):,} barridos encontrados".replace(",",".")); print("="*118)
    print(f"  {'':<32}{'n':>6}{'stop':>8}{'%TP':>8}{'R/op':>9}{'bruta/d':>9}{'z':>7}{'NETA/d':>10}{'z':>7}{'PF':>7}{'€/mes':>9}")
    for et, ini, fin in (("2020-2025", "2000-01-01", "2026-01-01"), ("2026 ene-jul", "2026-01-01", "2026-08-01")):
        linea(f"{et} · stop de la mecha", resuelve(t), ini, fin)
        linea(f"{et} · stop mín 10p (descriptivo)", resuelve(t, 10.0), ini, fin)
