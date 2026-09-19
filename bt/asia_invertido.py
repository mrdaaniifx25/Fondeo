"""docs/PREREGISTRO_asia_invertido.md · una sola vez."""
import numpy as np, pandas as pd
U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
ts1 = m1.ts.to_numpy(); Hm = m1.high.to_numpy(); Lm = m1.low.to_numpy(); Cm = m1.close.to_numpy()
loc1 = m1["loc"].to_numpy()

t = pd.read_csv("data/asia_contexto.csv", parse_dates=["ts"])
t = t[~(t.favM15 & t.favH1)].reset_index(drop=True)
t["diaD"] = pd.to_datetime(t.dia)
j0v = np.searchsorted(ts1, t.ts.to_numpy(), side="right")
finv = np.searchsorted(loc1, (t.diaD + pd.Timedelta(hours=22)).to_numpy())

R, mot = [], []
for n, r in enumerate(t.itertuples()):
    lado = -r.lado                                   # al reves
    rgo = r.riesgo * U
    stp = r.entrada - rgo*lado
    tp  = r.entrada + 2*rgo*lado
    j0 = int(j0v[n]); j1 = min(max(int(finv[n]), j0+1), len(Cm))
    if j0 >= len(Cm): R.append(np.nan); mot.append('sin datos'); continue
    hh, ll = Hm[j0:j1], Lm[j0:j1]
    gt, gs = ((hh >= tp, ll <= stp) if lado > 0 else (ll <= tp, hh >= stp))
    it  = int(np.argmax(gt)) if gt.any() else 10**9
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    if it == 10**9 and isl == 10**9:
        sal = Cm[j1-1]
        R.append(((sal-r.entrada) if lado > 0 else (r.entrada-sal))/rgo); mot.append("cierre")
    elif isl <= it: R.append(-1.0); mot.append("SL")
    else: R.append(2.0); mot.append("TP")
t["Rinv"] = R; t["motInv"] = mot; t["netoInv"] = t.Rinv - COSTE/t.riesgo
t.to_csv("data/asia_invertido.csv", index=False)

def bloque(nom, s):
    if len(s) < 30: print(f"\n{nom}: n insuficiente"); return
    sm = s.groupby("dia").netoInv.sum(); md = s.groupby("dia").netoInv.mean()
    bs = s.groupby("dia").Rinv.sum()
    e1 = sm.std(ddof=1)/np.sqrt(len(sm)); e2 = md.std(ddof=1)/np.sqrt(len(md))
    e3 = bs.std(ddof=1)/np.sqrt(len(bs))
    g, p = s.netoInv[s.netoInv > 0].sum(), -s.netoInv[s.netoInv < 0].sum()
    pm = len(sm)/((pd.to_datetime(s.ts.max())-pd.to_datetime(s.ts.min())).days/30.44)
    print(f"\n{nom}")
    print(f"  {len(s):,} disparos en {len(sm):,} días  ·  {pm:.1f} días con señal al mes".replace(",","."))
    print(f"  acierto invertido {100*(s.motInv=='TP').mean():.1f} %   (el original hacía "
          f"{100*(s.motivo=='TP').mean():.1f} %; la geometría da 33,3 %)")
    print(f"  R bruta/op {s.Rinv.mean():+.3f}  ·  R neta/op {s.netoInv.mean():+.3f}")
    print(f"  SUMA por día:  bruta {bs.mean():+.3f} (z {bs.mean()/e3:+.2f})  ·  "
          f"NETA {sm.mean():+.3f} (z {sm.mean()/e1:+.2f})   <- el contraste firmado")
    print(f"  media por día: neta {md.mean():+.3f} (z {md.mean()/e2:+.2f})")
    print(f"  profit factor neto {g/p:.2f}  ·  con 100 € de riesgo: {sm.mean()*100*pm:+.0f} €/mes")

print("=" * 90)
print("INVERTIR LOS DISPAROS CON EL CONTEXTO EN CONTRA · una sola vez")
print("=" * 90)
bloque("PRINCIPAL · 2020-2025", t[t.ts < "2026-01-01"])
bloque("SECUNDARIA · enero-mayo 2026", t[(t.ts >= "2026-01-01") & (t.ts < "2026-06-01")])
