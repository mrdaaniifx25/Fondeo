"""EXPLORATORIO. Variantes de la regla del usuario sobre 2020-2025.

NO es una prueba limpia: son especificaciones nuevas sobre datos que ya se han
mirado. Solo sirve para saber si los dos matices que el anadio despues de ver
el resultado (empezar a las 09:00, y poner el stop al otro lado del nivel
cuando la entrada esta pegada al nivel) mueven algo. La prueba pre-registrada
es bt/asia_nivel.py y ya esta cerrada.
"""
import numpy as np, pandas as pd

U, COSTE, TZ = 0.0001, 1.2, "Europe/Madrid"
REARME, ATRAS, FIN = 10.0, 10, 2200

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), ts=("ts","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date; v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
O,H,L,C = v.o.to_numpy(), v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()

ts1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
finHM = (m1["loc"].dt.hour*100 + m1["loc"].dt.minute).to_numpy()
finDia = m1["loc"].dt.date.to_numpy()

def gatillo(i, niv, lado):
    o, c = O[i], C[i]
    if not ((c > o) if lado > 0 else (c < o)): return None
    if (min(o,c) >= niv) if lado > 0 else (max(o,c) <= niv): return "A"
    for j in range(i-1, max(i-1-ATRAS, -1), -1):
        if (lado > 0) == (C[j] >= O[j]): continue
        ref = max(O[j], C[j]) if lado > 0 else min(O[j], C[j])
        return "B" if ((c > ref) if lado > 0 else (c < ref)) else None
    return None

def corre(inicio, cerca):
    """inicio = hora minima de entrada (hhmm). cerca = pips; si la entrada esta
    a menos de esa distancia del nivel, el stop se pone al otro lado del nivel."""
    filas = []
    for dia, g in v.groupby("dia"):
        a = g[g.hm < 800]
        if len(a) < 60: continue
        hi, lo = float(a.h.max()), float(a.l.min())
        if hi <= lo: continue
        W = g[(g.hm >= inicio) & (g.hm < 1130)]
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
                    ent = C[i]; ext = L[i-1] if lado > 0 else H[i-1]
                    if cerca is not None and abs(ent-niv)/U <= cerca:
                        stp = (niv-U) if lado > 0 else (niv+U)
                        stp = min(stp, ext) if lado > 0 else max(stp, ext)
                    else: stp = ext
                    rgo = abs(ent - stp)
                    if rgo <= 0: break
                    filas.append(dict(dia=dia, i=int(i), lado=lado, entrada=ent, stop=stp,
                                      obj=ent + 2*rgo*lado, riesgo=rgo/U))
                    armado = False
                    break
    t = pd.DataFrame(filas)
    t["ts"] = pd.to_datetime(v.ts.to_numpy()[t.i])
    R, mot = [], []
    for r in t.itertuples():
        j0 = int(np.searchsorted(ts1, np.datetime64(r.ts), side="right"))
        fin = np.where((finDia[j0:] != r.dia) | (finHM[j0:] >= FIN))[0]
        j1 = max(j0 + (int(fin[0]) if len(fin) else len(ts1)-j0), j0+1)
        hh, ll = H1[j0:j1], L1[j0:j1]
        gt, gs = ((hh >= r.obj, ll <= r.stop) if r.lado > 0 else (ll <= r.obj, hh >= r.stop))
        it  = int(np.argmax(gt)) if gt.any() else 10**9
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        if it == 10**9 and isl == 10**9:
            sal = C1[j1-1]
            R.append(((sal-r.entrada) if r.lado>0 else (r.entrada-sal))/abs(r.entrada-r.stop)); mot.append("cierre")
        elif isl <= it: R.append(-1.0); mot.append("SL")
        else: R.append(2.0); mot.append("TP")
    t["R"] = R; t["motivo"] = mot; t["neto"] = t.R - COSTE/t.riesgo
    return t[t.ts < "2026-01-01"]

print("2020-2025 · UNIDAD: EL DIA         (exploratorio: son especificaciones nuevas sobre datos ya vistos)")
print(f"{'':<38}{'n':>6}{'riesgo':>8}{'%TP':>8}{'BRUTA/d':>9}{'z':>7}{'NETA/d':>9}{'z':>7}")
for nom, ini, cer in [("pre-registrada (08:00, stop vela)", 800, None),
                      ("desde las 09:00 (lo que el dice)", 900, None),
                      ("09:00 + stop al nivel si <5p",     900, 5.0),
                      ("09:00 + stop al nivel si <8p",     900, 8.0)]:
    s = corre(ini, cer)
    d = s.groupby("dia").agg(R=("R","mean"), neto=("neto","mean"))
    eb = d.R.std(ddof=1)/np.sqrt(len(d)); en = d.neto.std(ddof=1)/np.sqrt(len(d))
    print(f"{nom:<38}{len(d):>6}{s.riesgo.median():>7.1f}p{100*(s.motivo=='TP').mean():>7.1f}%"
          f"{d.R.mean():>+9.3f}{d.R.mean()/eb:>+7.2f}{d.neto.mean():>+9.3f}{d.neto.mean()/en:>+7.2f}")
