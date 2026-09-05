"""La pasada de docs/PREREGISTRO_asia_limpia.md.  Se ejecuta UNA vez.

El filtro de «vuelta limpia» sacado de EURUSD, aplicado a oro y DAX, donde esta
estrategia no se ha ejecutado nunca.  Umbrales fijados en el pre-registro y no
se tocan.
"""
import numpy as np, pandas as pd

TZ = "Europe/Madrid"
T_HORA, T_BARRIDO, T_RECHAZO = 10, 0.3314, 0.1322     # pre-registro, sin tocar

INS = [("XAUUSD 2023-2025", "data/xauusd_m1.parquet",      0.01, 35.0, 3, 60),
       ("XAUUSD 2026",      "data/xauusd_m1_2026.parquet", 0.01, 35.0, 3, 60),
       ("GRXEUR 2023-2025", "data/grxeur_m1.parquet",      1.00,  2.0, 2, 40),
       ("GRXEUR 2026",      "data/grxeur_m1_2026.parquet", 1.00,  2.0, 2, 40)]

def corre(ruta, U, minutos, min_asia):
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").reset_index(drop=True)
    m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    m1["b5"] = m1["loc"].dt.floor("5min")
    v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                              c=("close","last"), n=("ts","size")).reset_index())
    v = v[v.n >= minutos].reset_index(drop=True)
    v["dia"] = v.b5.dt.date; v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
    O,H,L,C = v.o.to_numpy(), v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()

    def env(i, alc):
        a0,a3,b0,b3 = O[i-1],C[i-1],O[i],C[i]
        if alc and not b3 > b0: return False
        if not alc and not b3 < b0: return False
        return min(b0,b3) <= min(a0,a3) and max(b0,b3) >= max(a0,a3)

    filas = []
    for dia, g in v.groupby("dia"):
        a = g[g.hm < 800]
        if len(a) < min_asia: continue
        hi, lo = float(a.h.max()), float(a.l.min())
        if hi <= lo: continue
        Lo = g[(g.hm >= 800) & (g.hm < 1400)]
        if Lo.empty: continue
        i0, i1 = Lo.index[0], Lo.index[-1]
        hecho = False
        for i in range(i0, i1+1):
            baja, alta = C[i] < lo, C[i] > hi
            if not (baja or alta): continue
            alc = baja; niv = lo if alc else hi
            for k in (1,2):
                j = i+k
                if j > i1 or not env(j, alc): continue
                ent = C[j]; sl = (L[j-1]-U) if alc else (H[j-1]+U)
                rgo = abs(ent-sl)
                if rgo <= 0: break
                tp = hi if alc else ent - 2*rgo
                if alc and tp <= ent: break
                rg = H[j]-L[j]
                if rg <= 0: break
                mecha_niv = (niv - L[i:j+1].min()) if alc else (H[i:j+1].max() - niv)
                mecha_rec = ((min(O[j],C[j])-L[j]) if alc else (H[j]-max(O[j],C[j])))/rg
                filas.append(dict(dia=dia, i=j, fin=i1, lado=1 if alc else -1,
                                  entrada=ent, stop=sl, obj=tp, riesgo=rgo/U,
                                  hora=v.hm.iloc[j]//100,
                                  dentro=1 if lo <= C[j] <= hi else 0,
                                  barrido_rel=mecha_niv/(hi-lo), rechazo=mecha_rec))
                hecho = True
                break
            if hecho: break
    t = pd.DataFrame(filas)
    if t.empty: return t

    ts1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
    TSV = m1.groupby("b5").ts.last().reindex(v.b5).to_numpy()
    R, mot = [], []
    for r in t.itertuples():
        j0 = int(np.searchsorted(ts1, TSV[int(r.i)], side="right"))
        j1 = min(max(int(np.searchsorted(ts1, TSV[int(r.fin)], side="right")), j0+1), len(ts1))
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
    t["F"] = ((t.hora < T_HORA) & (t.dentro == 1) &
              (t.barrido_rel <= T_BARRIDO) & (t.rechazo <= T_RECHAZO)).astype(int)
    return t

def linea(et, g, coste):
    if len(g) < 2:
        print(f"   {et:24s} n={len(g):>4}  n insuficiente"); return
    neto = (g.R - coste/g.riesgo).to_numpy()
    ee = neto.std(ddof=1)/np.sqrt(len(neto))
    inv = (1/g.riesgo).mean()
    print(f"   {et:24s} {len(g):>4} {100*(g.motivo=='TP').mean():>6.1f}% {100/(1+g.rr.median()):>8.1f}% "
          f"{100*coste/g.riesgo.median():>7.1f}% {g.R.mean():>+8.3f} {neto.mean():>+8.3f} "
          f"[{neto.mean()-1.96*ee:+.3f},{neto.mean()+1.96*ee:+.3f}] {neto.mean()/ee:>+6.2f} "
          f"{g.R.mean()/inv if inv>0 else float('nan'):>9.1f}")

print("="*128)
print("RÉPLICA DE «VUELTA LIMPIA» · docs/PREREGISTRO_asia_limpia.md · una sola vez")
print("  filtro: hora < 10 · el gatillo cierra dentro del rango · barrido/rango <= 0,3314 · rechazo <= 0,1322")
print("="*128)

todo = {}
for nom, ruta, U, coste, minutos, min_asia in INS:
    t = corre(ruta, U, minutos, min_asia)
    todo[nom] = (t, coste)
    print(f"\n{nom}   ({len(t)} operaciones)")
    if t.empty: continue
    print(f"   {'':24s} {'n':>4} {'%TP':>7} {'geometría':>9} {'coste/rgo':>8} {'R BRUTA':>8} "
          f"{'R NETA':>8} {'IC95 neta':>18} {'z':>6} {'c* equil.':>9}")
    linea("todas", t, coste)
    linea("cumple el filtro", t[t.F == 1], coste)
    linea("no cumple", t[t.F == 0], coste)
    a, b = t[t.F == 1], t[t.F == 0]
    if len(a) > 1 and len(b) > 1:
        d = a.R.mean()-b.R.mean(); e = np.sqrt(a.R.var(ddof=1)/len(a)+b.R.var(ddof=1)/len(b))
        print(f"   diferencia cumple - no cumple: {d:+.3f}  z {d/e:+.2f}")

print("\n" + "="*128)
print("PRUEBA PRINCIPAL · ORO, los dos periodos juntos")
oro = pd.concat([todo["XAUUSD 2023-2025"][0], todo["XAUUSD 2026"][0]], ignore_index=True)
if not oro.empty:
    print(f"   {'':24s} {'n':>4} {'%TP':>7} {'geometría':>9} {'coste/rgo':>8} {'R BRUTA':>8} "
          f"{'R NETA':>8} {'IC95 neta':>18} {'z':>6} {'c* equil.':>9}")
    linea("todas", oro, 35.0); linea("cumple el filtro", oro[oro.F==1], 35.0); linea("no cumple", oro[oro.F==0], 35.0)
    a,b = oro[oro.F==1], oro[oro.F==0]
    d = a.R.mean()-b.R.mean(); e = np.sqrt(a.R.var(ddof=1)/len(a)+b.R.var(ddof=1)/len(b))
    neto_f = (a.R - 35.0/a.riesgo).mean()
    print(f"\n   diferencia {d:+.3f}  z {d/e:+.2f}   ·   neta del filtro {neto_f:+.3f}")
    ok = (d >= 0.13) and (d/e >= 1.96) and (neto_f >= 0)
    print(f"   umbral: dif >= +0,13 · z >= 1,96 · neta >= 0   ->   {'REPLICA' if ok else 'NO REPLICA'}")
pd.concat([v[0].assign(bloque=k) for k,v in todo.items() if not v[0].empty]).to_csv("data/asia_limpia.csv", index=False)
