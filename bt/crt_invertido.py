"""docs/PREREGISTRO_crt_invertido.md · una sola vez."""
import numpy as np, pandas as pd
U, COSTE = 0.0001, 1.43

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
ts1 = m1.ts.to_numpy(); Hm = m1.high.to_numpy(); Lm = m1.low.to_numpy(); Cm = m1.close.to_numpy()

d = pd.read_csv("data/trades_crt_base.csv", parse_dates=["ts"])
d["lado"] = np.where(d.dir == "largo", 1, -1)
d["dia"] = d.ts.dt.date

R, mot = [], []
for r in d.itertuples():
    lado = -r.lado
    rgo = abs(r.entrada - r.sl)                 # misma distancia en pips
    obj = abs(r.tp - r.entrada)
    stp = r.entrada - rgo*lado
    tp  = r.entrada + obj*lado
    j0 = int(np.searchsorted(ts1, np.datetime64(r.ts), side="right"))
    j1 = int(np.searchsorted(ts1, np.datetime64(r.ts + pd.Timedelta(days=5)), side="right"))
    j1 = min(max(j1, j0+1), len(Cm))
    if j0 >= len(Cm): R.append(np.nan); mot.append("x"); continue
    hh, ll = Hm[j0:j1], Lm[j0:j1]
    gt, gs = ((hh >= tp, ll <= stp) if lado > 0 else (ll <= tp, hh >= stp))
    it  = int(np.argmax(gt)) if gt.any() else 10**9
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    if it == 10**9 and isl == 10**9:
        sal = Cm[j1-1]
        R.append(((sal-r.entrada) if lado > 0 else (r.entrada-sal))/rgo); mot.append("tiempo")
    elif isl <= it: R.append(-1.0); mot.append("SL")
    else: R.append(obj/rgo); mot.append("TP")
d["Rinv"] = R; d["motInv"] = mot
d = d.dropna(subset=["Rinv"])
d["neto"]    = d.R    - COSTE/d.riesgo_pips
d["netoInv"] = d.Rinv - COSTE/d.riesgo_pips
d.to_csv("data/crt_invertido.csv", index=False)

def linea(et, s, rc, nc, mc):
    sn = s.groupby("dia")[nc].sum(); sb = s.groupby("dia")[rc].sum()
    e1 = sb.std(ddof=1)/np.sqrt(len(sb)); e2 = sn.std(ddof=1)/np.sqrt(len(sn))
    g, p = s[nc][s[nc] > 0].sum(), -s[nc][s[nc] < 0].sum()
    pm = len(sn)/((s.ts.max()-s.ts.min()).days/30.44)
    print(f"  {et:<26}{len(s):>6,}{100*(s[mc].astype(str).str.upper()=='TP').mean():>7.1f}%"
          f"{s[rc].mean():>+9.3f}{sb.mean():>+9.3f}{sb.mean()/e1:>+7.2f}{sn.mean():>+10.3f}"
          f"{sn.mean()/e2:>+7.2f}{g/p:>7.2f}{sn.mean()*100*pm:>+8.0f}€".replace(",","."))

CAB = f"  {'':<26}{'n':>6}{'%TP':>8}{'R/op':>9}{'bruta/d':>9}{'z':>7}{'NETA/d':>10}{'z':>7}{'PF':>7}{'€/mes':>9}"
for et, a, b in (("2020-2025 · CONTRASTE PRINCIPAL","2000-01-01","2026-01-01"),
                 ("2026 ene-jul · secundaria","2026-01-01","2027-01-01")):
    s = d[(d.ts >= a) & (d.ts < b)]
    print("\n" + "="*106); print(et); print("="*106); print(CAB)
    linea("el CRT como está", s, "R", "neto", "motivo")
    linea("el CRT al revés",  s, "Rinv", "netoInv", "motInv")
    print(f"  sin resolver al revés: {100*(s.motInv=='tiempo').mean():.1f} %")
