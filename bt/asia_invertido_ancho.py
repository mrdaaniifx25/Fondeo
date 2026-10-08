"""EXPLORATORIO. El invertido con stops mas anchos.

El contraste preregistrado (bt/asia_invertido.py) fallo en neto: z -1.10.
Esto es una especificacion nueva sobre datos ya vistos y se informa como tal.
"""
import numpy as np, pandas as pd
U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"
m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
ts1 = m1.ts.to_numpy(); Hm = m1.high.to_numpy(); Lm = m1.low.to_numpy(); Cm = m1.close.to_numpy()
loc1 = m1["loc"].to_numpy(); N = len(Cm)

t = pd.read_csv("data/asia_contexto.csv", parse_dates=["ts"])
t = t[~(t.favM15 & t.favH1) & (t.ts < "2026-06-01")].reset_index(drop=True)
t["diaD"] = pd.to_datetime(t.dia)
J0 = np.searchsorted(ts1, t.ts.to_numpy(), side="right")
FIN = np.searchsorted(loc1, (t.diaD + pd.Timedelta(hours=22)).to_numpy())

def corre(ancho, k):
    R, mot = [], []
    for n, r in enumerate(t.itertuples()):
        lado = -r.lado
        rgo = max(r.riesgo, ancho) * U
        stp = r.entrada - rgo*lado; tp = r.entrada + k*rgo*lado
        j0 = int(J0[n]); j1 = min(max(int(FIN[n]), j0+1), N)
        if j0 >= N: R.append(np.nan); mot.append("x"); continue
        hh, ll = Hm[j0:j1], Lm[j0:j1]
        gt, gs = ((hh >= tp, ll <= stp) if lado > 0 else (ll <= tp, hh >= stp))
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = Cm[j1-1]
            R.append(((sal-r.entrada) if lado > 0 else (r.entrada-sal))/rgo); mot.append("cierre")
        elif isl <= it: R.append(-1.0); mot.append("SL")
        else: R.append(float(k)); mot.append("TP")
    d = t.assign(R=R, motivo=mot, rgoP=np.maximum(t.riesgo, ancho)).dropna(subset=["R"])
    d["neto"] = d.R - COSTE/d.rgoP
    return d

print("EL INVERTIDO CON STOPS ANCHOS · EXPLORATORIO, especificación nueva sobre datos ya vistos")
print(f"\n{'stop':>7}{'ratio':>7}{'obj':>7}{'n':>6}{'días':>6}{'%TP':>7}{'sin res':>9}"
      f"{'R/op':>9}{'suma bruta/d':>14}{'z':>7}{'SUMA NETA/d':>13}{'z':>7}{'€/mes':>9}")
for ancho in (0, 8, 10, 12, 15, 20):
    for k in (1.5, 2.0):
        d = corre(ancho, k)
        for et, ini, fin in (("", "2000-01-01", "2026-01-01"),):
            s = d[(d.ts >= ini) & (d.ts < fin)]
            sb = s.groupby("dia").R.sum(); sn = s.groupby("dia").neto.sum()
            e1 = sb.std(ddof=1)/np.sqrt(len(sb)); e2 = sn.std(ddof=1)/np.sqrt(len(sn))
            pm = len(sn)/((pd.to_datetime(s.ts.max())-pd.to_datetime(s.ts.min())).days/30.44)
            print(f"{('nat' if not ancho else str(ancho)+'p'):>7}{k:>7.1f}{(max(ancho,5)*k):>6.0f}p"
                  f"{len(s):>6}{len(sn):>6}{100*(s.motivo=='TP').mean():>6.1f}%"
                  f"{100*(s.motivo=='cierre').mean():>8.1f}%{s.R.mean():>+9.3f}"
                  f"{sb.mean():>+14.3f}{sb.mean()/e1:>+7.2f}{sn.mean():>+13.3f}{sn.mean()/e2:>+7.2f}"
                  f"{sn.mean()*100*pm:>+8.0f}€")
    print()
