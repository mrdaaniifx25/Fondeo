"""La regla que sale de sus 150: BARRIDO Y RECHAZO del nivel de Asia.

De la ingenieria inversa salio que sus entradas no van con la rotura -solo el
6,7 %, igual que el azar- sino sobre velas que PINCHAN el nivel con la mecha y
cierran de vuelta dentro: el 23,3 % de las suyas contra el 8,1 % de base
(z +6,45). Y de esas, 30 de 35 van contra el nivel: venden el rechazo del alto y
compran el rechazo del bajo. Aciertan el 73-78 %.

Es la primera regla del proyecto escrita desde lo que hizo y no desde una guia.

  python3 bt/regla_rechazo.py [ventana_fin]        (por defecto 1130)
"""
import json, sys
import numpy as np, pandas as pd
from math import sqrt, erf

U, COSTE, TZ = 1e-4, 1.43, "Europe/Madrid"
INI = 480
FINV = int(sys.argv[1]) if len(sys.argv) > 1 else 1130
FIN_MIN = (FINV//100)*60 + FINV % 100
MAX_TOQUE = 1                       # primer o segundo toque del nivel
CORTE = 690                         # se cierra a mercado a las 11:30
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
zf = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x)))

DIAS_EX = set()
for dj in ("data/examen_dias.json", "data/examen_dias2.json",
           "data/examen_dias3.json", "data/examen_dias4.json"):
    DIAS_EX |= {pd.Timestamp(v).date() for v in json.load(open(dj)).values()}

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date
m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
T1 = m1["loc"].to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()

v = m1.assign(b=(m1["min"]//5)*5).groupby(["dia","b"]).agg(
        o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
        n=("close","size")).reset_index()
v = v[v.n >= 3].reset_index(drop=True)
v["cierre_min"] = v.b + 5

filas = []
for dia, d1 in m1.groupby("dia"):
    a = d1[d1["min"] < INI]
    if len(a) < 300: continue
    hi, lo = float(a.high.max()), float(a.low.min())
    g = v[(v.dia == dia) & (v.cierre_min >= INI) & (v.cierre_min <= FIN_MIN)]
    if len(g) < 5: continue
    toques = {True: 0, False: 0}
    for r in g.itertuples():
        for arriba, L in ((True, hi), (False, lo)):
            if not (r.l <= L <= r.h): continue          # la mecha no llega al nivel
            n_toque = toques[arriba]; toques[arriba] += 1
            dentro = (r.c < L) if arriba else (r.c > L)
            if not dentro: continue                     # cerro fuera: es rotura, no rechazo
            if n_toque > MAX_TOQUE: continue
            lado = -1 if arriba else 1                  # contra el nivel
            ent = r.c
            stp = r.h if arriba else r.l                # el extremo de la mecha
            rgo = abs(ent - stp)/U
            if rgo < 1.0: continue                      # demasiado pegado, el coste manda
            filas.append(dict(dia=dia, cierre_min=int(r.cierre_min), lado=lado, ent=ent,
                              sl=stp, tp=ent + lado*2*rgo*U, rgo=rgo, toque=n_toque,
                              arriba=arriba))
t = pd.DataFrame(filas)

out = []
for r in t.itertuples():
    ini = np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(minutes=int(r.cierre_min)))
    fin = np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(minutes=CORTE))
    k = int(np.searchsorted(T1, ini)); j = int(np.searchsorted(T1, fin))
    j = min(max(j, k+1), len(T1))
    hh, ll = H1[k:j], L1[k:j]
    largo = r.lado > 0
    gs, gt = ((ll <= r.sl, hh >= r.tp) if largo else (hh >= r.sl, ll <= r.tp))
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    itp = int(np.argmax(gt)) if gt.any() else 10**9
    if isl == 10**9 and itp == 10**9:
        sal = C1[j-1]; R = ((sal-r.ent) if largo else (r.ent-sal))/U/r.rgo; mot = "cierre"
    elif isl <= itp: R, mot = -1.0, "SL"
    else:            R, mot = 2.0, "TP"
    out.append((R, mot))
t["R"] = [o[0] for o in out]; t["mot"] = [o[1] for o in out]
t["neta"] = t.R - COSTE/t.rgo
t["examen"] = t.dia.isin(DIAS_EX)

def informe(nom, d):
    if len(d) < 10: print(f"\n{nom}: solo {len(d)} disparos"); return
    res = d[d.mot != "cierre"]
    ac = (res.mot == "TP").mean()
    se = sqrt((1/3)*(2/3)/len(res))
    zn = zf(d.neta.to_numpy())
    print(f"\n{nom}")
    print(f"  disparos {len(d)}  en {d.dia.nunique()} días  ·  {len(d)/d.dia.nunique():.2f} por día")
    print(f"  acierto {100*ac:.1f} %  (geométrico 33,3 %)   z = {(ac-1/3)/se:+.2f}")
    print(f"  stop mediano {d.rgo.median():.1f} p   ·   coste sobre riesgo "
          f"{100*(COSTE/d.rgo).mean():.1f} %")
    print(f"  R bruta {d.R.mean():+.3f}   ·   R NETA {d.neta.mean():+.3f}   z = {zn:+.2f}"
          f"   (p={p2(zn):.6f})")
    print(f"  suma neta {d.neta.sum():+.1f} R")

print("="*74)
print(f"REGLA DE BARRIDO Y RECHAZO · ventana 08:00-{FINV//100:02d}:{FINV%100:02d}"
      f" · hasta el toque nº {MAX_TOQUE+1}")
print("="*74)
informe("EN LOS 114 DÍAS DEL EXAMEN  (de donde salió: descriptivo)", t[t.examen])
informe("FUERA DE MUESTRA · todos los demás días 2020-2026  (CONFIRMATORIO)",
        t[~t.examen])
d = t[~t.examen]
print("\n  por año, fuera de muestra:")
d = d.assign(ano=pd.to_datetime(d.dia).dt.year)
for y, s in d.groupby("ano"):
    r = s[s.mot != "cierre"]
    print(f"    {y}  n={len(s):4d}  acierto {100*(r.mot=='TP').mean():5.1f} %  "
          f"neta {s.neta.mean():+.3f}  suma {s.neta.sum():+7.1f} R")
print("\n  por lado y por toque, fuera de muestra:")
for nom, m in (("rechazo del ALTO (venta)", d.arriba), ("rechazo del BAJO (compra)", ~d.arriba),
               ("primer toque", d.toque == 0), ("segundo toque", d.toque == 1)):
    s = d[m]; r = s[s.mot != "cierre"]
    print(f"    {nom:26s} n={len(s):4d}  acierto {100*(r.mot=='TP').mean():5.1f} %  "
          f"neta {s.neta.mean():+.3f}")
t.to_csv("data/regla_rechazo.csv", index=False)

print("\n" + "="*74); print("DOS COMPROBACIONES MÁS  (secundarias, exploratorias)"); print("="*74)
# 1 · ¿es el stop de 3 pips lo que la mata? Se ensancha al suyo.
print("\n  a · con el stop ensanchado hasta la anchura que pone él:")
print(f"    {'stop mínimo':>12s} {'n':>6s} {'stop med':>9s} {'coste/riesgo':>13s} "
      f"{'acierto':>8s} {'R neta':>8s} {'z':>7s}")
d0 = t[~t.examen]
for smin in (0, 4, 6, 8, 10):
    s = d0.copy()
    rgo = np.maximum(s.rgo, smin)
    # se rehace el desenlace solo cuando el stop cambia: se recalcula entero
    R, mot = [], []
    for r, g in zip(s.itertuples(), rgo):
        largo = r.lado > 0
        stp = r.ent - r.lado*g*U
        tp  = r.ent + r.lado*2*g*U
        ini = np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(minutes=int(r.cierre_min)))
        fin = np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(minutes=CORTE))
        k = int(np.searchsorted(T1, ini)); j = min(max(int(np.searchsorted(T1, fin)), k+1), len(T1))
        hh, ll = H1[k:j], L1[k:j]
        gs, gt = ((ll <= stp, hh >= tp) if largo else (hh >= stp, ll <= tp))
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        itp = int(np.argmax(gt)) if gt.any() else 10**9
        if isl == 10**9 and itp == 10**9:
            sal = C1[j-1]; R.append(((sal-r.ent) if largo else (r.ent-sal))/U/g); mot.append("cierre")
        elif isl <= itp: R.append(-1.0); mot.append("SL")
        else:            R.append(2.0);  mot.append("TP")
    R = np.array(R); mot = np.array(mot)
    neta = R - COSTE/rgo.to_numpy()
    res = mot != "cierre"
    print(f"    {smin:10d} p {len(s):6d} {np.median(rgo):8.1f}p "
          f"{100*np.mean(COSTE/rgo):12.1f}% {100*np.mean(mot[res]=='TP'):7.1f}% "
          f"{neta.mean():+8.3f} {zf(neta):+7.2f}")

# 2 · ¿coincide la regla con sus operaciones?
print("\n  b · ¿elige la regla las mismas operaciones que él?")
s150 = pd.read_csv("data/contexto_suyas.csv")
s150["dia"] = pd.to_datetime(s150.dia).dt.date
disp = {(r.dia, r.cierre_min) for r in t[t.examen].itertuples()}
cerca = 0
for r in s150.itertuples():
    if any((r.dia, m) in disp for m in range(r.ent_min-15, r.ent_min+20)): cerca += 1
print(f"    de sus 150, coinciden con un disparo de la regla (±15 min): {cerca} "
      f"({100*cerca/len(s150):.0f} %)")
print(f"    la regla dispara {len(t[t.examen])} veces en esos días y él entra {len(s150)}")

print("\n  c · en los MISMOS disparos, ¿qué saca él y qué saca la regla?")
par = []
for r in s150.itertuples():
    cand = [x for x in t[t.examen].itertuples()
            if x.dia == r.dia and r.ent_min-15 <= x.cierre_min <= r.ent_min+19]
    if not cand: continue
    x = min(cand, key=lambda x: abs(x.cierre_min - r.ent_min))
    par.append(dict(dia=r.dia, suyo_R=r.R, suyo_mot=r.mot, suyo_rgo=r.rgo, suyo_lado=r.lado,
                    regla_R=x.R, regla_mot=x.mot, regla_rgo=x.rgo, regla_lado=x.lado,
                    mismo_lado=(r.lado == x.lado)))
P = pd.DataFrame(par)
print(f"    {len(P)} parejas (su entrada y el disparo de la regla, a menos de 15 min)")
print(f"    van en la misma dirección: {int(P.mismo_lado.sum())} de {len(P)}")
for nom, col, rg in (("él   ", "suyo", "suyo_rgo"), ("regla", "regla", "regla_rgo")):
    m = P[f"{col}_mot"]; R = P[f"{col}_R"]
    res = m != "cierre"
    neta = R - COSTE/P[rg]
    print(f"    {nom}  acierto {100*(m[res]=='TP').mean():5.1f} %  stop {P[rg].median():.1f}p  "
          f"R bruta {R.mean():+.3f}  R neta {neta.mean():+.3f}")
dif = (P.suyo_R - COSTE/P.suyo_rgo) - (P.regla_R - COSTE/P.regla_rgo)
print(f"    diferencia emparejada  {dif.mean():+.3f} R por disparo   z = {zf(dif.to_numpy()):+.2f}")
