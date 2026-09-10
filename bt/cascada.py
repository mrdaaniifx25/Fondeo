"""docs/PREREGISTRO_cascada.md · una sola vez.

Cada sesion cerrada deja su maximo y su minimo como niveles pendientes. Un
nivel muere cuando el precio lo toca. Se opera el BARRIDO: la vela atraviesa
el nivel con la mecha y cierra de vuelta al lado de origen.
"""
import numpy as np, pandas as pd, sys
U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"
ATRAS, FIN = 10, 2300          # sesiones cuyos niveles se conservan

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)

def marco(regla):
    g = (m1.set_index("loc").resample(regla)
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), ts=("ts","last"), n=("close","size")))
    g = g[g.n >= 1].reset_index()
    g["dia"] = g["loc"].dt.date
    g["hm"]  = g["loc"].dt.hour*100 + g["loc"].dt.minute
    g["dsem"] = g["loc"].dt.dayofweek
    return g[g.dsem < 5].reset_index(drop=True)

def sesion(hm):
    if hm < 800:  return "Asia"
    if hm < 1400: return "Londres"
    return "NY"

ts1 = m1.ts.to_numpy(); Hm = m1.high.to_numpy(); Lm = m1.low.to_numpy(); Cm = m1.close.to_numpy()
fD = m1["loc"].dt.date.to_numpy(); fH = (m1["loc"].dt.hour*100 + m1["loc"].dt.minute).to_numpy()

def corre(regla, unaPorDia=True):
    v = marco(regla)
    v["ses"] = v.hm.map(sesion)
    v["clave"] = v.dia.astype(str) + "|" + v.ses
    H, L, C = v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()
    claves = v.clave.to_numpy()

    pend = []          # [(precio, tipo, clave_sesion_origen)]
    cerradas = []
    filas = []
    ultimo = None
    hechoDia, hechoSes = set(), set()
    acc_h, acc_l = -1e9, 1e9

    for i in range(len(v)):
        k = claves[i]
        if ultimo is not None and k != ultimo:
            cerradas.append((acc_h, acc_l, ultimo))
            pend.append([acc_h, "alto", ultimo]); pend.append([acc_l, "bajo", ultimo])
            if len(cerradas) > ATRAS:
                viejas = {c[2] for c in cerradas[:-ATRAS]}
                pend = [p for p in pend if p[2] not in viejas]
            acc_h, acc_l = H[i], L[i]
        else:
            acc_h = max(acc_h, H[i]); acc_l = min(acc_l, L[i])
        ultimo = k
        dia = v.dia.iloc[i]

        vivos = []
        for p in pend:
            niv, tipo, orig = p
            tocado = L[i] <= niv <= H[i]
            if not tocado: vivos.append(p); continue
            # el nivel muere al ser tocado; si ademas cierra de vuelta, es barrido
            barre = (H[i] > niv and C[i] < niv) if tipo == "alto" else (L[i] < niv and C[i] > niv)
            if not barre: continue
            libre = (dia not in hechoDia) if unaPorDia else (k not in hechoSes)
            if not libre: continue
            lado = -1 if tipo == "alto" else 1
            ent = C[i]; stp = (H[i] + U) if lado < 0 else (L[i] - U)
            rgo = abs(ent - stp)
            if rgo <= 0: continue
            hechoDia.add(dia); hechoSes.add(k)
            filas.append(dict(dia=dia, ses=v.ses.iloc[i], hm=int(v.hm.iloc[i]), lado=lado,
                              tipo=tipo, entrada=ent, stop=stp, riesgo=rgo/U,
                              edad=len(cerradas) - [c[2] for c in cerradas].index(orig),
                              ts=v.ts.iloc[i]))
        pend = vivos

    t = pd.DataFrame(filas)
    if not len(t): return t
    t["ts"] = pd.to_datetime(t.ts)
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
    t["R"] = R; t["motivo"] = mot; t = t.dropna(subset=["R"])
    t["neto"] = t.R - COSTE/t.riesgo
    return t

def linea(et, s):
    if len(s) < 30: print(f"  {et:<34} n insuficiente ({len(s)})"); return
    sn = s.groupby("dia").neto.sum(); sb = s.groupby("dia").R.sum()
    e1 = sb.std(ddof=1)/np.sqrt(len(sb)); e2 = sn.std(ddof=1)/np.sqrt(len(sn))
    pm = len(sn)/((pd.to_datetime(s.ts.max())-pd.to_datetime(s.ts.min())).days/30.44)
    g, p = s.neto[s.neto > 0].sum(), -s.neto[s.neto < 0].sum()
    print(f"  {et:<34}{len(s):>6,}{s.riesgo.median():>7.1f}p{100*(s.motivo=='TP').mean():>7.1f}%"
          f"{s.R.mean():>+9.3f}{sb.mean():>+9.3f}{sb.mean()/e1:>+7.2f}{sn.mean():>+10.3f}"
          f"{sn.mean()/e2:>+7.2f}{g/p:>7.2f}{sn.mean()*100*pm:>+8.0f}€".replace(",","."))

CAB = f"  {'':<34}{'n':>6}{'stop':>8}{'%TP':>8}{'R/op':>9}{'bruta/d':>9}{'z':>7}{'NETA/d':>10}{'z':>7}{'PF':>7}{'€/mes':>9}"
for regla, et in (("15min","M15 · CONTRASTE PRINCIPAL"), ("30min","M30 · secundario")):
    t = corre(regla)
    print("\n" + "="*118); print(et); print("="*118); print(CAB)
    linea("2020-2025", t[t.ts < "2026-01-01"])
    linea("2026 ene-jul", t[t.ts >= "2026-01-01"])
    if regla == "15min":
        s = t[t.ts < "2026-01-01"]
        print("\n  por sesión en la que se opera")
        for x in ("Asia","Londres","NY"): linea(f"    {x}", s[s.ses == x])
        print("\n  por antigüedad del nivel barrido")
        for et2, m in (("    de la sesión anterior", s.edad <= 1), ("    2 a 4 sesiones", s.edad.between(2,4)),
                       ("    5 o más", s.edad >= 5)): linea(et2, s[m])
        t2 = corre("15min", unaPorDia=False)
        print("\n  una por sesión en vez de una por día")
        linea("    2020-2025", t2[t2.ts < "2026-01-01"])
