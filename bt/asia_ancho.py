"""docs/PREREGISTRO_asia_ancho.md · una sola vez."""
import numpy as np, pandas as pd
U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
ts1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
loc1 = m1["loc"].to_numpy()          # para cortar el horizonte con searchsorted

t = pd.read_csv("data/asia_contexto.csv", parse_dates=["ts"])
t = t[t.favM15 & t.favH1 & (t.ts < "2026-06-01")].reset_index(drop=True)
t["diaD"] = pd.to_datetime(t.dia)
t["j0"] = np.searchsorted(ts1, t.ts.to_numpy(), side="right")
# fin del horizonte, calculado una sola vez
FIN = {0: np.searchsorted(loc1, (t.diaD + pd.Timedelta(hours=22)).to_numpy()),
       3: np.searchsorted(loc1, (t.diaD + pd.Timedelta(days=4)).to_numpy())}

def resuelve(ancho, dias):
    fin = FIN[dias]
    R, mot = [], []
    for r in t.itertuples():
        rgo = max(r.riesgo, ancho) * U
        stp = r.entrada - rgo*r.lado
        tp  = r.entrada + 2*rgo*r.lado
        j0 = int(r.j0); j1 = max(int(fin[r.Index]), j0+1)
        hh, ll = H1[j0:j1], L1[j0:j1]
        gt, gs = ((hh >= tp, ll <= stp) if r.lado > 0 else (ll <= tp, hh >= stp))
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = C1[j1-1]
            R.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/rgo); mot.append("cierre")
        elif isl <= it: R.append(-1.0); mot.append("SL")
        else: R.append(2.0); mot.append("TP")
    d = t.assign(R=R, motivo=mot, rgoP=np.maximum(t.riesgo, ancho))
    d["neto"] = d.R - COSTE/d.rgoP
    return d

def linea(et, d, ini, fin):
    s = d[(d.ts >= ini) & (d.ts < fin)]
    if len(s) < 30: return
    g = s.groupby("dia").agg(R=("R","mean"), neto=("neto","mean"))
    eb = g.R.std(ddof=1)/np.sqrt(len(g)); en = g.neto.std(ddof=1)/np.sqrt(len(g))
    print(f"  {et:<12}{len(s):>7,}{len(g):>7,}{s.rgoP.median():>8.1f}p"
          f"{100*(s.motivo=='TP').mean():>7.1f}%{100*(s.motivo=='cierre').mean():>9.1f}%"
          f"{s.R.mean():>+9.3f}{g.R.mean()/eb:>+7.2f}{g.neto.mean():>+10.3f}{g.neto.mean()/en:>+7.2f}"
          .replace(",", "."))

for dias, et in ((0, "HORIZONTE PRINCIPAL · hasta las 22:00 del mismo día"),
                 (3, "HORIZONTE SECUNDARIO · 3 días naturales")):
    print("\n" + "=" * 100); print(et); print("=" * 100)
    for ini, fin, nom in (("2000-01-01", "2026-01-01", "PRINCIPAL · 2020-2025"),
                          ("2026-01-01", "2026-06-01", "SECUNDARIA · enero-mayo 2026")):
        print(f"\n{nom}")
        print(f"  {'stop mín':<12}{'n':>7}{'días':>7}{'stop':>9}{'%TP':>8}{'sin resolver':>10}"
              f"{'R/op':>9}{'z br':>7}{'neta/d':>10}{'z':>7}")
        for ancho in (0, 10, 15, 20, 25, 30):
            linea(f"{ancho} p" if ancho else "natural", resuelve(ancho, dias), ini, fin)
