"""Por que unas van al stop y otras al objetivo.

Tres hipotesis del usuario -la hora, entrar lejos del nivel, y la liquidez de
otras sesiones que el precio va a buscar- mas la tipologia de vela de la
documentacion.  Se calculan sobre TODA la poblacion de la regla laxa, un setup
por dia, 2020-2026, que es donde hay potencia; sus 37 solo sirven para saber
que mirar.

  python3 bt/asia_anatomia.py
"""
import numpy as np
import pandas as pd

U, COSTE, TZ = 0.0001, 1.2, "Europe/Madrid"

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date
v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
O,H,L,C = v.o.to_numpy(), v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()
HM = v.hm.to_numpy()

# ---- niveles de sesion del dia anterior, y maximo/minimo de la semana
dias = sorted(v.dia.unique())
ses = {}
for d, g in v.groupby("dia"):
    a  = g[g.hm < 800]; lo_ = g[(g.hm >= 800) & (g.hm < 1400)]; ny = g[g.hm >= 1400]
    ses[d] = dict(dia_hi=g.h.max(), dia_lo=g.l.min(),
                  lon_hi=lo_.h.max() if len(lo_) else np.nan,
                  lon_lo=lo_.l.min() if len(lo_) else np.nan,
                  ny_hi=ny.h.max() if len(ny) else np.nan,
                  ny_lo=ny.l.min() if len(ny) else np.nan)
prev = {d: ses[dias[i-1]] for i, d in enumerate(dias) if i > 0}

def envuelve(i, alc):
    a0,a3,b0,b3 = O[i-1],C[i-1],O[i],C[i]
    if alc and not b3 > b0: return False
    if not alc and not b3 < b0: return False
    return min(b0,b3) <= min(a0,a3) and max(b0,b3) >= max(a0,a3)

filas = []
for dia, g in v.groupby("dia"):
    if dia not in prev: continue
    a = g[g.hm < 800]
    if len(a) < 60: continue
    hi, lo = float(a.h.max()), float(a.l.min())
    Lo = g[(g.hm >= 800) & (g.hm < 1400)]
    if Lo.empty: continue
    i0, i1 = Lo.index[0], Lo.index[-1]
    hallado = False
    for i in range(i0, i1+1):
        baja, alta = C[i] < lo, C[i] > hi
        if not (baja or alta): continue
        alc = baja; niv = lo if alc else hi
        for k in (1,2):
            j = i+k
            if j > i1 or not envuelve(j, alc): continue
            ent = C[j]; sl = (L[j-1]-U) if alc else (H[j-1]+U)
            rgo = abs(ent-sl)
            if rgo <= 0: break
            tp = hi if alc else ent - 2*rgo
            if alc and tp <= ent: break

            rango_g = H[j]-L[j]
            cuerpo  = abs(C[j]-O[j])
            mecha_a = H[j]-max(O[j],C[j])
            mecha_b = min(O[j],C[j])-L[j]
            # la mecha del barrido que se lleva el nivel
            mecha_niv = (niv - L[i:j+1].min()) if alc else (H[i:j+1].max() - niv)

            # atractores: niveles de ayer y de la semana
            p = prev[dia]
            sem = g.index[0]
            niveles = [p["dia_hi"], p["dia_lo"], p["lon_hi"], p["lon_lo"], p["ny_hi"], p["ny_lo"]]
            niveles = [x for x in niveles if not np.isnan(x)]
            contra = [x for x in niveles if (x < ent if alc else x > ent)]
            favor  = [x for x in niveles if (x > ent if alc else x < ent)]
            d_contra = (min(abs(ent-x) for x in contra)/rgo) if contra else np.inf
            d_favor  = (min(abs(ent-x) for x in favor)/rgo) if favor else np.inf

            filas.append(dict(
                dia=dia, i=j, fin=i1, lado=1 if alc else -1, entrada=ent, stop=sl, obj=tp,
                riesgo=rgo/U, hora=HM[j]//100,
                # A · la hora ya esta; B · lejos del nivel
                dist_niv=abs(ent-niv)/U, dist_niv_R=abs(ent-niv)/rgo,
                sitio=(ent-lo)/(hi-lo) if hi > lo else np.nan,
                dist_obj=abs(tp-ent)/U,
                # C · liquidez de otras sesiones
                atrae_contra=d_contra, atrae_favor=d_favor,
                # D · tipologia de la vela gatillo
                cuerpo=cuerpo/U, cuerpo_pct=cuerpo/rango_g if rango_g > 0 else np.nan,
                mecha_arriba=mecha_a/rango_g if rango_g > 0 else np.nan,
                mecha_abajo=mecha_b/rango_g if rango_g > 0 else np.nan,
                mecha_niv=mecha_niv/U, mecha_niv_R=mecha_niv/rgo,
                dentro=1 if (lo <= C[j] <= hi) else 0,
                exceso=abs(C[i]-niv)/U,
                # E · volatilidad y rango
                rango_asia=(hi-lo)/U,
                atr=float(np.mean(H[max(0,j-24):j] - L[max(0,j-24):j]))/U,
                dsem=pd.Timestamp(dia).dayofweek,
            ))
            hallado = True
            break
        if hallado: break

t = pd.DataFrame(filas)

# ---- resolucion hasta el cierre de Londres
ts1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
tsv = m1.groupby("b5").ts.last().reindex(v.b5).to_numpy()
R, mot = [], []
for r in t.itertuples():
    j0 = int(np.searchsorted(ts1, tsv[r.i], side="right"))
    j1 = min(max(int(np.searchsorted(ts1, tsv[r.fin], side="right")), j0+1), len(ts1))
    hh, ll = H1[j0:j1], L1[j0:j1]
    gt, gs = ((hh >= r.obj, ll <= r.stop) if r.lado > 0 else (ll <= r.obj, hh >= r.stop))
    it = int(np.argmax(gt)) if gt.any() else 10**9
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    rr = abs(r.obj-r.entrada)/abs(r.entrada-r.stop)
    if it == 10**9 and isl == 10**9:
        sal = C1[j1-1]
        R.append(((sal-r.entrada) if r.lado>0 else (r.entrada-sal))/abs(r.entrada-r.stop)); mot.append("cierre")
    elif isl <= it: R.append(-1.0); mot.append("SL")
    else: R.append(float(rr)); mot.append("TP")
t["R"] = R; t["motivo"] = mot
t["rr"] = (t.obj-t.entrada).abs()/(t.entrada-t.stop).abs()
t["neto"] = t.R - COSTE/t.riesgo
t["ts"] = pd.to_datetime(t.dia)
t.to_csv("data/asia_anatomia.csv", index=False)
print(f"poblacion: {len(t):,} operaciones · {t.ts.min():%Y-%m} a {t.ts.max():%Y-%m} · "
      f"%TP {100*(t.motivo=='TP').mean():.1f}% · bruta {t.R.mean():+.3f} · neta {t.neto.mean():+.3f}")
