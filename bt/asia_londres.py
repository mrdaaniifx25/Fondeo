"""El barrido de Asia en la apertura de Londres.  Pre-registro: docs/PREREGISTRO_asia_londres.md

Regla del usuario, sin retocar:
  Asia 00:00-08:00 deja maximo y minimo. En Londres 08:00-14:00, todo en M5:
  una vela CIERRA mas alla del nivel; la siguiente o la de despues tiene que ser
  una ENVOLVENTE; se entra a su cierre; el stop va al otro lado de la vela
  anterior a la envolvente. Rompe el minimo -> compra al maximo de Asia.
  Rompe el maximo -> venta a 1:2.
"""
import sys; sys.path.insert(0, "bt")
import numpy as np, pandas as pd

RUTA, UNIDAD, COSTE = "data/eurusd_m1.parquet", 0.0001, 1.2
TZ = "Europe/Madrid"
rng = np.random.default_rng(20260827)

def ee_bloq(x, largo=20, reps=4000):
    n = len(x)
    if n < largo * 3:
        return x.std(ddof=1) / np.sqrt(n)
    nb = int(np.ceil(n / largo))
    ini = rng.integers(0, n - largo + 1, size=(reps, nb))
    idx = (ini[:, :, None] + np.arange(largo)[None, None, :]).reshape(reps, -1)[:, :n]
    return float(x[idx].mean(axis=1).std(ddof=1))

m1 = pd.read_parquet(RUTA); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").reset_index(drop=True)
loc = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["loc"] = loc

# velas de M5 en hora local
m1["b5"] = m1["loc"].dt.floor("5min")
v = m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                         c=("close","last"), ts=("ts","last"), n=("ts","size")).reset_index()
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date
v["hm"] = v.b5.dt.hour * 100 + v.b5.dt.minute
v["asia"] = v.hm < 800
v["lon"]  = (v.hm >= 800) & (v.hm < 1400)

def envuelve(i, alcista, cuerpo=True):
    """la vela i envuelve a la i-1 y va en direccion contraria"""
    if i < 1: return False
    a, b = v.iloc[i-1], v.iloc[i]
    if alcista and not (b.c > b.o): return False
    if not alcista and not (b.c < b.o): return False
    if cuerpo:
        return min(b.o,b.c) <= min(a.o,a.c) and max(b.o,b.c) >= max(a.o,a.c)
    return b.l <= a.l and b.h >= a.h

def corre(cuerpo=True):
    filas = []
    for dia, g in v.groupby("dia"):
        a = g[g.asia]
        if len(a) < 60: continue                 # necesita una sesion de Asia completa
        hi, lo = a.h.max(), a.l.min()
        L = g[g.lon]
        if L.empty: continue
        i0, i1 = L.index[0], L.index[-1]
        hecho = False
        for i in range(i0, i1 + 1):
            if hecho: break
            r = v.iloc[i]
            rompe_bajo = r.c < lo
            rompe_alto = r.c > hi
            if not (rompe_bajo or rompe_alto): continue
            alc = rompe_bajo
            # la envolvente: la siguiente o la de despues
            for k in (1, 2):
                j = i + k
                if j > i1: break
                if not envuelve(j, alc, cuerpo): continue
                ent = v.iloc[j].c
                prev = v.iloc[j-1]
                stp = prev.l - UNIDAD if alc else prev.h + UNIDAD
                rgo = abs(ent - stp)
                if rgo <= 0: break
                obj = hi if alc else ent - 2*rgo
                if alc and obj <= ent: break
                filas.append(dict(dia=dia, ts=v.iloc[j].ts, i=j, fin=i1, lado=1 if alc else -1,
                                  rama="mínimo" if alc else "máximo", entrada=ent,
                                  stop=stp, obj=obj, riesgo=rgo/UNIDAD))
                hecho = True
                break
    t = pd.DataFrame(filas)
    if t.empty: return t
    # resolucion en M1 hasta el cierre de Londres
    t1 = m1.ts.to_numpy(); H = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
    finLon = v.ts.to_numpy()
    R, mot = [], []
    for r in t.itertuples():
        j0 = int(np.searchsorted(t1, np.datetime64(r.ts), side="right"))
        j1 = int(np.searchsorted(t1, finLon[r.fin], side="right"))
        j1 = max(j1, j0 + 1); j1 = min(j1, len(t1))
        if j0 >= len(t1): R.append(np.nan); mot.append("sin datos"); continue
        hh, ll = H[j0:j1], L1[j0:j1]
        gt, gs = ((hh >= r.obj, ll <= r.stop) if r.lado > 0 else (ll <= r.obj, hh >= r.stop))
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        rr = abs(r.obj - r.entrada) / abs(r.entrada - r.stop)
        if it == 10**9 and isl == 10**9:
            sal = C1[j1-1]
            R.append(((sal-r.entrada) if r.lado>0 else (r.entrada-sal))/abs(r.entrada-r.stop))
            mot.append("cierre Londres")
        elif isl <= it: R.append(-1.0); mot.append("SL")
        else: R.append(float(rr)); mot.append("TP")
    t["R"] = R; t["motivo"] = mot
    t["rr"] = (t.obj - t.entrada).abs() / (t.entrada - t.stop).abs()
    t["coste_R"] = COSTE / t.riesgo
    t["neto"] = t.R - t.coste_R
    return t.dropna(subset=["R"]).reset_index(drop=True)

print("="*110)
print("BARRIDO DE ASIA EN LA APERTURA DE LONDRES · EURUSD M5 · pre-registro fijado")
print("="*110)

for nom, cuerpo in (("envolvente por CUERPO (principal)", True),
                    ("envolvente por RANGO (secundaria)", False)):
    t = corre(cuerpo)
    if t.empty:
        print(f"\n{nom}: sin operaciones"); continue
    t["ts"] = pd.to_datetime(t.ts)
    print(f"\n### {nom}")
    print(f"{'periodo':16s} {'rama':9s} {'n':>6s} {'/año':>6s} {'riesgo':>8s} {'R:R':>6s} "
          f"{'%TP':>6s} {'coste':>7s} {'R BRUTA':>9s} {'R NETA':>9s} {'IC95 neta':>20s} {'z':>7s}")
    for per, lo_, hi_ in (("2020-2025 CIEGO","2020-01-01","2026-01-01"),
                          ("2026 ene-jun","2026-01-01","2026-07-01"),
                          ("2026 julio (suyo)","2026-07-01","2026-08-01")):
        s = t[(t.ts >= lo_) & (t.ts < hi_)]
        for rama in ("todas", "mínimo", "máximo"):
            g = s if rama == "todas" else s[s.rama == rama]
            if len(g) < 2: continue
            x = g.neto.to_numpy(); eb = ee_bloq(x)
            anos = (pd.Timestamp(hi_) - pd.Timestamp(lo_)).days / 365.25
            marca = "  <<<" if rama == "todas" and per.startswith("2020") else ""
            print(f"{per if rama=='todas' else '':16s} {rama:9s} {len(g):>6,} {len(g)/anos:>6.0f} "
                  f"{g.riesgo.median():>7.1f}p {g.rr.median():>6.2f} {100*(g.motivo=='TP').mean():>5.1f}% "
                  f"{100*g.coste_R.median():>6.1f}% {g.R.mean():>+9.3f} {x.mean():>+9.3f} "
                  f"[{x.mean()-1.96*eb:+.3f},{x.mean()+1.96*eb:+.3f}] {x.mean()/eb:>+7.2f}{marca}")
    if cuerpo:
        t.to_csv("data/asia_londres.csv", index=False)
        dias = t[(t.ts>="2020-01-01")&(t.ts<"2026-01-01")].dia.nunique()
        tot = v[(v.b5>="2020-01-01")&(v.b5<"2026-01-01")].dia.nunique()
        print(f"\n  aparece en {dias:,} de {tot:,} días  ({100*dias/tot:.0f} %)")
