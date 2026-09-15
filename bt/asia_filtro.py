"""El filtro que el usuario aplica sin saber que lo aplica.

De las 60 cartas de la baraja ciega salieron tres rasgos que separan lo que
elige de lo que pasa.  Aqui se convierten en regla y se prueban sobre los
candidatos que NO vio.

  python3 bt/asia_filtro.py            solo cuenta candidatos (no resuelve)
  python3 bt/asia_filtro.py --resolver cuenta y resuelve
"""
import sys
import numpy as np
import pandas as pd

RESOLVER = "--resolver" in sys.argv
UNIDAD, COSTE, TZ = 0.0001, 1.2, "Europe/Madrid"
# umbrales fijados en docs/PREREGISTRO_asia_filtro.md, punto medio de las
# medianas de los 26 operados y los 34 pasados.  No se tocan.
T_EXCESO, T_CUERPO = 1.7, 3.7

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), ts=("ts","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date
v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute

O,H,L,C = v.o.to_numpy(), v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()

def envuelve(i, alc):
    a0,a3,b0,b3 = O[i-1],C[i-1],O[i],C[i]
    if alc and not b3 > b0: return False
    if not alc and not b3 < b0: return False
    return min(b0,b3) <= min(a0,a3) and max(b0,b3) >= max(a0,a3)

filas = []
for dia, g in v.groupby("dia"):
    a = g[g.hm < 800]
    if len(a) < 60: continue
    hi, lo = float(a.h.max()), float(a.l.min())
    Lo = g[(g.hm >= 800) & (g.hm < 1400)]
    if Lo.empty: continue
    i0, i1 = Lo.index[0], Lo.index[-1]
    for i in range(i0, i1+1):
        baja, alta = C[i] < lo, C[i] > hi
        if not (baja or alta): continue
        alc = baja; niv = lo if alc else hi
        for k in (1,2):
            j = i+k
            if j > i1 or not envuelve(j, alc): continue
            ent = C[j]; sl = (L[j-1]-UNIDAD) if alc else (H[j-1]+UNIDAD)
            rgo = abs(ent-sl)
            if rgo <= 0: break
            tp = hi if alc else ent - 2*rgo
            if alc and tp <= ent: break
            mecha = (niv - L[i:j+1].min()) if alc else (H[i:j+1].max() - niv)
            filas.append(dict(dia=dia, ts=v.ts.iloc[j], i=j, fin=i1, lado=1 if alc else -1,
                              entrada=ent, stop=sl, obj=tp, riesgo=rgo/UNIDAD,
                              exceso=abs(C[i]-niv)/UNIDAD, mecha=mecha/UNIDAD,
                              cuerpo=abs(C[j]-O[j])/UNIDAD))
            break
        break                                    # solo el primer barrido del dia

t = pd.DataFrame(filas)
t["ts"] = pd.to_datetime(t.ts)
vistos = set(pd.read_csv("data/etiquetado_asia_verdad.csv").ts.astype(str))
t["visto"] = t.ts.astype(str).isin(vistos)
t["A"] = (t.exceso <= T_EXCESO) & (t.cuerpo >= T_CUERPO)
t["B"] = t.exceso <= T_EXCESO
t["C"] = t.cuerpo >= T_CUERPO

def bloque(nom, s):
    print(f"\n{nom}  ({len(s)} candidatos)")
    for et, m in (("todos", np.ones(len(s), bool)), ("A estricto", s.A.to_numpy()),
                  ("B barrido limpio", s.B.to_numpy()), ("C envolvente fuerte", s.C.to_numpy())):
        print(f"   {et:22s} {int(m.sum()):>4}  ({100*m.mean():>4.0f} %)")

print("=== CANDIDATOS Y CUÁNTOS PASAN CADA FILTRO ===")
bloque("2020-2025 · los 60 que vio", t[t.visto])
bloque("2020-2025 · los que NO vio", t[(~t.visto) & (t.ts < "2026-01-01")])
bloque("2026 ene-jul · reservado",  t[t.ts >= "2026-01-01"])

if not RESOLVER:
    t.to_csv("data/asia_filtro_candidatos.csv", index=False)
    sys.exit("\n(sin resolver; pasa --resolver cuando el pre-registro esté escrito)")

# ------------------------------------------------------------------ resolver
t1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
finLon = v.ts.to_numpy()
R, mot = [], []
for r in t.itertuples():
    j0 = int(np.searchsorted(t1, np.datetime64(r.ts), side="right"))
    j1 = min(max(int(np.searchsorted(t1, finLon[r.fin], side="right")), j0+1), len(t1))
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

def linea(et, s):
    if len(s) < 2:
        print(f"   {et:22s} {len(s):>4}  n insuficiente"); return
    x = s.neto.to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x))
    print(f"   {et:22s} {len(s):>4} {s.riesgo.median():>7.1f}p {s.rr.median():>5.2f} "
          f"{100*(s.motivo=='TP').mean():>6.1f}% {100/(1+s.rr.median()):>8.1f}% "
          f"{s.R.mean():>+9.3f} {x.mean():>+9.3f} [{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}] {x.mean()/ee:>+6.2f}")

print("\n\n=== RESULTADO ===")
for nom, s in (("2020-2025 · NO vistos (prueba principal)", t[(~t.visto) & (t.ts < "2026-01-01")]),
               ("2026 ene-jul · reservado", t[t.ts >= "2026-01-01"]),
               ("2020-2025 · los 60 vistos (referencia)", t[t.visto])):
    print(f"\n{nom}")
    print(f"   {'':22s} {'n':>4} {'riesgo':>8} {'R:R':>5} {'%TP':>7} {'geometría':>9} "
          f"{'R BRUTA':>9} {'R NETA':>9} {'IC95 neta':>18} {'z':>6}")
    linea("todos", s)
    linea("A estricto", s[s.A]); linea("B barrido limpio", s[s.B]); linea("C envolvente fuerte", s[s.C])
t.to_csv("data/asia_filtro.csv", index=False)
