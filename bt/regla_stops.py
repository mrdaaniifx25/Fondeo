"""La misma señal de bt/asia_nivel.py, con ocho stops distintos.

Preregistrado en docs/PREREGISTRO_regla_stops.md. Un solo pase.

La señal no se toca: niveles de Asia, ventana de Londres, gatillos A y B,
armado y rearme, entrada al cierre de la vela de M5. Lo unico que cambia es
donde va el stop, porque el suyo real va sobre M1 y el del pase original iba
sobre M5.

  python3 bt/regla_stops.py
"""
import numpy as np, pandas as pd
from math import sqrt, erf

U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"
VENTANA = (800, 1130)
REARME, ATRAS, FIN = 10.0, 10, 2200
GEO = 100/3                      # acierto de un 1:2 sin coste

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), ts=("ts","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date; v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
O,H,L,C = v.o.to_numpy(), v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()

# M1 en arrays, para poder mirar la estructura fina justo antes de la entrada
T1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy()

def gatillo(i, niv, lado):
    o, c = O[i], C[i]
    if not ((c > o) if lado > 0 else (c < o)): return None
    if (min(o,c) >= niv) if lado > 0 else (max(o,c) <= niv): return "A"
    for j in range(i-1, max(i-1-ATRAS, -1), -1):
        if (lado > 0) == (C[j] >= O[j]): continue
        ref = max(O[j], C[j]) if lado > 0 else min(O[j], C[j])
        return "B" if ((c > ref) if lado > 0 else (c < ref)) else None
    return None

filas = []
for dia, g in v.groupby("dia"):
    a = g[g.hm < 800]
    if len(a) < 60: continue
    hi, lo = float(a.h.max()), float(a.l.min())
    if hi <= lo: continue
    W = g[(g.hm >= VENTANA[0]) & (g.hm < VENTANA[1])]
    if len(W) < 5: continue
    i0, i1 = W.index[0], W.index[-1]
    for niv in (hi, lo):
        armado = True
        for i in range(i0, i1 + 1):
            toca = L[i] <= niv <= H[i]
            if not toca and min(abs(H[i]-niv), abs(L[i]-niv))/U > REARME: armado = True
            if not (armado and toca): continue
            for lado in (1, -1):
                if gatillo(i, niv, lado) is None: continue
                filas.append(dict(dia=dia, i=int(i), lado=lado, entrada=C[i]))
                armado = False
                break

s = pd.DataFrame(filas)
s["ts"] = pd.to_datetime(v.ts.to_numpy()[s.i])
# indice del minuto de entrada: la vela M5 cierra en ese sello, se entra ahi
s["k"] = np.searchsorted(T1, s.ts.to_numpy())
print(f"{len(s):,} señales en {s.dia.nunique():,} días")

def stop_de(nombre, r):
    """Devuelve el precio del stop para una señal, segun la variante."""
    i, k, lado, ent = r.i, r.k, r.lado, r.entrada
    if nombre == "M5 anterior":
        return L[i-1] if lado > 0 else H[i-1]
    if nombre == "M5 señal":
        return L[i] if lado > 0 else H[i]
    if nombre.startswith("M1 x"):
        n = int(nombre[4:]); j0 = max(0, k - n + 1)
        return (L1[j0:k+1].min() if lado > 0 else H1[j0:k+1].max())
    p = float(nombre.split()[1].rstrip("p"))
    return ent - lado*p*U

VARIANTES = ["M5 anterior", "M5 señal", "M1 x1", "M1 x3",
             "fijo 3p", "fijo 5p", "fijo 8p", "fijo 20p"]

def resuelve(sub):
    """Camina M1 desde el minuto SIGUIENTE al de la entrada hasta las 22:00.

    Se entra al CIERRE de la vela de M5, y `k` es su ultimo minuto. Resolver
    desde `k` metia la propia vela de entrada en la busqueda, asi que un stop
    pegado saltaba siempre en el mismo minuto en que se entraba: M1 x1 daba
    0,0 % de acierto sobre 1.951 operaciones. Se empieza en k+1.
    """
    out = []
    for r in sub.itertuples():
        k = r.k + 1
        fin = np.searchsorted(T1, np.datetime64(pd.Timestamp(r.dia)) +
                              np.timedelta64(FIN//100, "h"))
        fin = min(max(fin, k+1), len(T1))
        hh, ll = H1[k:fin], L1[k:fin]
        gt, gs = ((hh >= r.obj, ll <= r.stop) if r.lado > 0
                  else (ll <= r.obj, hh >= r.stop))
        itp = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if itp == 10**9 and isl == 10**9: R, mot = 0.0, "sin resolver"
        elif isl <= itp: R, mot = -1.0, "SL"
        else: R, mot = 2.0, "TP"
        out.append((R, mot))
    return pd.DataFrame(out, columns=["R", "motivo"], index=sub.index)

print(f"\n{'variante':13s} {'n':>6s} {'abierta':>8s} {'stop':>6s} {'cost%':>6s} "
      f"{'acierto':>8s} {'vs 33,3%':>9s} {'z ac.':>6s} {'R bruta':>8s} {'R neta':>8s} "
      f"{'z neta':>7s} {'suma':>9s}")
print("-"*114)
for nom in VARIANTES:
    d = s.copy()
    d["stop"] = [stop_de(nom, r) for r in d.itertuples()]
    d["riesgo"] = (d.entrada - d.stop).abs()/U
    d = d[d.riesgo > 0.2].copy()                 # un stop de dos decimas no existe
    d["obj"] = d.entrada + 2*d.lado*(d.riesgo*U)
    d[["R","motivo"]] = resuelve(d)
    d["neta"] = d.R - COSTE/d.riesgo
    res = d[d.motivo != "sin resolver"]
    ac = 100*(res.motivo == "TP").mean()
    ee_ac = 100*sqrt((GEO/100)*(1-GEO/100)/len(res))
    x = d.neta.to_numpy(); z = x.mean()/(x.std(ddof=1)/sqrt(len(x)))
    print(f"{nom:13s} {len(d):6d} {100*(1-len(res)/len(d)):7.1f}% {d.riesgo.median():5.1f}p "
          f"{100*(COSTE/d.riesgo).median():5.0f}% {ac:7.1f}% {ac-GEO:+8.1f}pp "
          f"{(ac-GEO)/ee_ac:+6.2f} {d.R.mean():+8.3f} {d.neta.mean():+8.3f} "
          f"{z:+7.2f} {d.neta.sum():+9.1f}")
print("\numbral Bonferroni para ocho variantes: |z| > 2,73")
