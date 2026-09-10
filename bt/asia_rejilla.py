"""EXPLORATORIO. Rejilla de ancho de stop x ratio objetivo, sobre las senales
filtradas por contexto y tomando solo la primera del dia.

No es una prueba: es elegir el punto de trabajo. Se informa como tal.
"""
import numpy as np, pandas as pd
U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
ts1 = m1.ts.to_numpy(); Hm = m1.high.to_numpy(); Lm = m1.low.to_numpy(); Cm = m1.close.to_numpy()
loc1 = m1["loc"].to_numpy()

t = pd.read_csv("data/asia_contexto.csv", parse_dates=["ts"])
t = t[t.favM15 & t.favH1 & (t.ts < "2026-06-01")].sort_values("ts")
t = t.groupby("dia").head(1).reset_index(drop=True)          # solo la primera del dia
t["diaD"] = pd.to_datetime(t.dia)
t["j0"] = np.searchsorted(ts1, t.ts.to_numpy(), side="right")
FIN = np.searchsorted(loc1, (t.diaD + pd.Timedelta(hours=22)).to_numpy())

def corre(ancho, k):
    R, mot = [], []
    for n, r in enumerate(t.itertuples()):
        rgo = max(r.riesgo, ancho) * U
        stp = r.entrada - rgo*r.lado
        tp  = r.entrada + k*rgo*r.lado
        j0 = int(r.j0); j1 = max(int(FIN[n]), j0+1)
        hh, ll = Hm[j0:j1], Lm[j0:j1]
        gt, gs = ((hh >= tp, ll <= stp) if r.lado > 0 else (ll <= tp, hh >= stp))
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = Cm[j1-1]
            R.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/rgo); mot.append("cierre")
        elif isl <= it: R.append(-1.0); mot.append("SL")
        else: R.append(float(k)); mot.append("TP")
    d = t.assign(R=R, motivo=mot, rgoP=np.maximum(t.riesgo, ancho))
    d["neto"] = d.R - COSTE/d.rgoP
    return d

print("REJILLA · ancho de stop x ratio · senales filtradas por contexto, la primera del dia")
print("EXPLORATORIO: se prueban muchas combinaciones sobre datos ya vistos.\n")
print(f"  {'stop':>6}{'ratio':>7}{'objetivo':>10}{'winrate':>9}{'sin resolver':>14}"
      f"{'PF bruto':>10}{'PF neto':>9}{'€/mes':>9}{'z':>7}")
for ancho in (8, 10, 12, 15, 20):
    for k in (1.0, 1.5, 2.0, 2.5):
        d = corre(ancho, k)
        s = d[d.ts < "2026-01-01"]
        n = s.neto; g, p = n[n > 0].sum(), -n[n < 0].sum()
        b = s.R; gb, pb = b[b > 0].sum(), -b[b < 0].sum()
        dd = n.groupby(s.dia).sum(); e = dd.std(ddof=1)/np.sqrt(len(dd))
        pm = len(dd)/((pd.to_datetime(s.ts.max())-pd.to_datetime(s.ts.min())).days/30.44)
        print(f"  {ancho:>5}p{k:>7.1f}{ancho*k:>9.0f}p{100*(s.motivo=='TP').mean():>8.1f}%"
              f"{100*(s.motivo=='cierre').mean():>13.1f}%{gb/pb:>10.2f}{g/p:>9.2f}"
              f"{dd.mean()*150*pm:>+8.0f}€{dd.mean()/e:>+7.2f}")
    print()
