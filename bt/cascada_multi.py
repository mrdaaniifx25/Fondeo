"""docs/PREREGISTRO_cascada_instrumentos.md · una sola vez.

Mismo motor que bt/cascada.py, cambiando solo el fichero de precios.
Todo en BRUTO: el coste real de cada instrumento lo pone el usuario.
"""
import numpy as np, pandas as pd
TZ, ATRAS, FIN = "Europe/Madrid", 10, 2300

def carga(fich):
    m = pd.read_parquet(fich)
    m["ts"] = pd.to_datetime(m["ts"]); m = m.sort_values("ts").reset_index(drop=True)
    m["loc"] = pd.DatetimeIndex(m.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    return m

def sesion(hm): return "Asia" if hm < 800 else ("Londres" if hm < 1400 else "NY")

def corre(m, paso):
    g = (m.set_index("loc").resample("15min")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), ts=("ts","last"), n=("close","size")))
    v = g[g.n >= 1].reset_index()
    v["dia"] = v["loc"].dt.date
    v["hm"] = v["loc"].dt.hour*100 + v["loc"].dt.minute
    v = v[v["loc"].dt.dayofweek < 5].reset_index(drop=True)
    v["clave"] = v.dia.astype(str) + "|" + v.hm.map(sesion)
    H, L, C = v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()
    claves = v.clave.to_numpy()

    pend, cerradas, filas = [], [], []
    ultimo, hecho = None, set()
    acc_h, acc_l = -1e18, 1e18
    for i in range(len(v)):
        k = claves[i]
        if ultimo is not None and k != ultimo:
            cerradas.append(ultimo)
            pend.append([acc_h, "alto", ultimo]); pend.append([acc_l, "bajo", ultimo])
            if len(cerradas) > ATRAS:
                viejas = set(cerradas[:-ATRAS])
                pend = [p for p in pend if p[2] not in viejas]
            acc_h, acc_l = H[i], L[i]
        else:
            acc_h = max(acc_h, H[i]); acc_l = min(acc_l, L[i])
        ultimo = k
        dia = v.dia.iloc[i]
        vivos = []
        for p in pend:
            niv, tipo, orig = p
            if not (L[i] <= niv <= H[i]): vivos.append(p); continue
            barre = (H[i] > niv and C[i] < niv) if tipo == "alto" else (L[i] < niv and C[i] > niv)
            if not barre or dia in hecho: continue
            lado = -1 if tipo == "alto" else 1
            ent = C[i]; stp = (H[i] + paso) if lado < 0 else (L[i] - paso)
            rgo = abs(ent - stp)
            if rgo <= 0: continue
            hecho.add(dia)
            filas.append(dict(dia=dia, lado=lado, entrada=ent, stop=stp, riesgo=rgo,
                              edad=len(cerradas) - cerradas.index(orig), ts=v.ts.iloc[i]))
        pend = vivos
    t = pd.DataFrame(filas)
    if not len(t): return t
    t["ts"] = pd.to_datetime(t.ts)
    ts1 = m.ts.to_numpy(); Hm = m.high.to_numpy(); Lm = m.low.to_numpy(); Cm = m.close.to_numpy()
    fD = m["loc"].dt.date.to_numpy(); fH = (m["loc"].dt.hour*100 + m["loc"].dt.minute).to_numpy()
    R, mot = [], []
    for r in t.itertuples():
        rgo = abs(r.entrada - r.stop); tp = r.entrada + 2*rgo*r.lado
        j0 = int(np.searchsorted(ts1, np.datetime64(r.ts), side="right"))
        f = np.where((fD[j0:] != r.dia) | (fH[j0:] >= FIN))[0]
        j1 = min(max(j0 + (int(f[0]) if len(f) else len(ts1)-j0), j0+1), len(Cm))
        if j0 >= len(Cm): R.append(np.nan); mot.append("x"); continue
        hh, ll = Hm[j0:j1], Lm[j0:j1]
        gt, gs = ((hh >= tp, ll <= r.stop) if r.lado > 0 else (ll <= tp, hh >= r.stop))
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = Cm[j1-1]; R.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/rgo); mot.append("cierre")
        elif isl <= it: R.append(-1.0); mot.append("SL")
        else: R.append(2.0); mot.append("TP")
    t["R"] = R; t["motivo"] = mot
    return t.dropna(subset=["R"])

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,"pips"),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,"pips"),
       ("USDJPY","data/usdjpy_m1.parquet",0.01,  "pips"),
       ("XAUUSD","data/xauusd_m1.parquet",0.01,  "centavos"),
       ("DAX",   "data/grxeur_m1.parquet",1.0,   "puntos"),
       ("NAS100","data/nsxusd_m1.parquet",1.0,   "puntos"),
       ("SP500", "data/spxusd_m1.parquet",1.0,   "puntos")]

print("LA CASCADA EN SIETE INSTRUMENTOS · TODO EN BRUTO, sin suponer ningún coste")
print(f"  {'':<9}{'n':>6}{'desde':>8}{'%TP':>8}{'R/op':>9}{'bruta/d':>9}{'z':>7}"
      f"{'stop mediano':>16}{'c* (equilibrio)':>18}")
for nom, fich, u, unid in INS:
    m = carga(fich)
    t = corre(m, u)
    if len(t) < 60: print(f"  {nom:<9} n insuficiente"); continue
    d = t.groupby("dia").R.sum(); e = d.std(ddof=1)/np.sqrt(len(d))
    cs = t.R.mean()/(1/(t.riesgo/u)).mean()
    print(f"  {nom:<9}{len(t):>6,}{str(t.ts.min().year):>8}{100*(t.motivo=='TP').mean():>7.1f}%"
          f"{t.R.mean():>+9.3f}{d.mean():>+9.3f}{d.mean()/e:>+7.2f}"
          f"{t.riesgo.median()/u:>11.1f} {unid:<4}{cs:>13.2f} {unid}".replace(",","."))
