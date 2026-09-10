"""docs/PREREGISTRO_mixto.md · una sola vez.

Barrido de niveles de sesion, pero sobre velas de H4 (la escala del CRT).
Siete instrumentos desde el principio. Todo en bruto.
"""
import numpy as np, pandas as pd, sys
TZ, ATRAS = "Europe/Madrid", 10
TF = sys.argv[1] if len(sys.argv) > 1 else "4h"

def sesion(hm): return "Asia" if hm < 800 else ("Londres" if hm < 1400 else "NY")

def corre(m, paso, tf):
    g = (m.set_index("loc").resample(tf)
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), ts=("ts","last"), n=("close","size")))
    v = g[g.n >= 1].reset_index()
    v["dia"] = v["loc"].dt.date
    v["hm"] = v["loc"].dt.hour*100 + v["loc"].dt.minute
    v = v[v["loc"].dt.dayofweek < 5].reset_index(drop=True)
    H, L, C = v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()

    # los niveles se acumulan por SESION, aunque operemos en H4
    s5 = (m.set_index("loc").resample("15min")
            .agg(h=("high","max"), l=("low","min"), n=("close","size")))
    s5 = s5[s5.n >= 1].reset_index()
    s5["dia"] = s5["loc"].dt.date
    s5["ses"] = (s5["loc"].dt.hour*100 + s5["loc"].dt.minute).map(sesion)
    s5["clave"] = s5.dia.astype(str) + "|" + s5.ses
    ses = (s5.groupby("clave", sort=False)
              .agg(hi=("h","max"), lo=("l","min"), fin=("loc","max")).reset_index())
    ses = ses.sort_values("fin").reset_index(drop=True)
    finSes = ses.fin.to_numpy()

    filas, hecho = [], set()
    for i in range(len(v)):
        ahora = np.datetime64(v["loc"].iloc[i])
        k = int(np.searchsorted(finSes, ahora, side="left"))    # sesiones ya cerradas
        if k < 2: continue
        dis = ses.iloc[max(0, k-ATRAS):k]
        dia = v.dia.iloc[i]
        if dia in hecho: continue
        for j in range(len(dis)-1, -1, -1):                     # de la mas reciente hacia atras
            for niv, tipo in ((dis.hi.iloc[j], "alto"), (dis.lo.iloc[j], "bajo")):
                if not (L[i] <= niv <= H[i]): continue
                barre = (H[i] > niv and C[i] < niv) if tipo == "alto" else (L[i] < niv and C[i] > niv)
                if not barre: continue
                lado = -1 if tipo == "alto" else 1
                ent = C[i]; stp = (H[i] + paso) if lado < 0 else (L[i] - paso)
                rgo = abs(ent - stp)
                if rgo <= 0: continue
                hecho.add(dia)
                filas.append(dict(dia=dia, ses=sesion(int(v.hm.iloc[i])), lado=lado,
                                  entrada=ent, stop=stp, riesgo=rgo,
                                  edad=len(dis)-j, ts=v.ts.iloc[i]))
                break
            if dia in hecho: break
    t = pd.DataFrame(filas)
    if not len(t): return t
    t["ts"] = pd.to_datetime(t.ts)
    ts1 = m.ts.to_numpy(); Hm = m.high.to_numpy(); Lm = m.low.to_numpy(); Cm = m.close.to_numpy()
    R, mot = [], []
    for r in t.itertuples():
        rgo = abs(r.entrada - r.stop); tp = r.entrada + 2*rgo*r.lado
        j0 = int(np.searchsorted(ts1, np.datetime64(r.ts), side="right"))
        j1 = int(np.searchsorted(ts1, np.datetime64(pd.Timestamp(r.ts) + pd.Timedelta(days=3)), side="right"))
        j1 = min(max(j1, j0+1), len(Cm))
        if j0 >= len(Cm): R.append(np.nan); mot.append("x"); continue
        hh, ll = Hm[j0:j1], Lm[j0:j1]
        gt, gs = ((hh >= tp, ll <= r.stop) if r.lado > 0 else (ll <= tp, hh >= r.stop))
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = Cm[j1-1]; R.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/rgo); mot.append("tiempo")
        elif isl <= it: R.append(-1.0); mot.append("SL")
        else: R.append(2.0); mot.append("TP")
    t["R"] = R; t["motivo"] = mot
    return t.dropna(subset=["R"])

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,"pips"),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,"pips"),
       ("USDJPY","data/usdjpy_m1.parquet",0.01,  "pips"),
       ("XAUUSD","data/xauusd_m1.parquet",0.01,  "cent"),
       ("DAX",   "data/grxeur_m1.parquet",1.0,   "pts"),
       ("NAS100","data/nsxusd_m1.parquet",1.0,   "pts"),
       ("SP500", "data/spxusd_m1.parquet",1.0,   "pts")]

print(f"MIX CRT + SESIONES · barrido de niveles de sesion en {TF.upper()} · TODO EN BRUTO")
print(f"  {'':<9}{'n':>6}{'%TP':>8}{'R/op':>9}{'bruta/d':>9}{'z':>7}{'sin res':>9}{'stop mediano':>16}{'c*':>14}")
todo = []
for nom, fich, u, unid in INS:
    m = pd.read_parquet(fich)
    m["ts"] = pd.to_datetime(m["ts"]); m = m.sort_values("ts").reset_index(drop=True)
    m["loc"] = pd.DatetimeIndex(m.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    t = corre(m, u, TF)
    if len(t) < 60: print(f"  {nom:<9} n insuficiente ({len(t)})"); continue
    d = t.groupby("dia").R.sum(); e = d.std(ddof=1)/np.sqrt(len(d))
    cs = t.R.mean()/(1/(t.riesgo/u)).mean()
    print(f"  {nom:<9}{len(t):>6,}{100*(t.motivo=='TP').mean():>7.1f}%{t.R.mean():>+9.3f}"
          f"{d.mean():>+9.3f}{d.mean()/e:>+7.2f}{100*(t.motivo=='tiempo').mean():>8.1f}%"
          f"{t.riesgo.median()/u:>11.1f} {unid:<4}{cs:>9.2f} {unid}".replace(",","."))
    t2 = t.assign(ins=nom); todo.append(t2)
    t2.to_csv(f"data/mixto_{nom}_{TF}.csv", index=False)

if todo:
    A = pd.concat(todo)
    d = A.groupby(["ins","dia"]).R.sum(); e = d.std(ddof=1)/np.sqrt(len(d))
    print("\n" + "="*100)
    print(f"  CONTRASTE PRINCIPAL · los siete agrupados · {len(A):,} operaciones en {len(d):,} días-instrumento".replace(",","."))
    print(f"  acierto {100*(A.motivo=='TP').mean():.1f} %  ·  R/op {A.R.mean():+.4f}  ·  "
          f"BRUTA POR DÍA {d.mean():+.4f}  ·  z {d.mean()/e:+.2f}")
    print(f"  -> {'POSITIVA, como se predijo' if d.mean()>0 else 'NEGATIVA, al reves de lo predicho'}")
    print("="*100)
    print("\n  por sesión operada")
    for x in ("Asia","Londres","NY"):
        s = A[A.ses == x]
        if len(s) < 40: continue
        dd = s.groupby(["ins","dia"]).R.sum(); ee = dd.std(ddof=1)/np.sqrt(len(dd))
        print(f"    {x:<10}{len(s):>6,}{100*(s.motivo=='TP').mean():>7.1f}%{s.R.mean():>+9.3f}{dd.mean()/ee:>+8.2f}".replace(",","."))
    print("\n  por antigüedad del nivel")
    for et, msk in (("de la sesión anterior", A.edad <= 1), ("2 a 4 sesiones", A.edad.between(2,4)), ("5 o más", A.edad >= 5)):
        s = A[msk]
        if len(s) < 40: continue
        dd = s.groupby(["ins","dia"]).R.sum(); ee = dd.std(ddof=1)/np.sqrt(len(dd))
        print(f"    {et:<24}{len(s):>6,}{100*(s.motivo=='TP').mean():>7.1f}%{s.R.mean():>+9.3f}{dd.mean()/ee:>+8.2f}".replace(",","."))
