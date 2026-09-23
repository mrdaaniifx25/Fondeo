"""La regla del usuario, escrita por el. docs/PREREGISTRO_asia_nivel.md

Se ejecuta UNA vez. Nada de lo de aqui se toca despues de ver el resultado.
"""
import numpy as np, pandas as pd

U, COSTE, TZ = 0.0001, 1.2, "Europe/Madrid"
VENTANA = (800, 1130)          # Londres, hora de Madrid
REARME  = 10.0                 # pips de alejamiento para rearmar el nivel
ATRAS   = 10                   # velas hacia atras para buscar la contraria
FIN     = 2200                 # horizonte maximo: cierre de NY

m1 = pd.read_parquet("data/eurusd_m1.parquet")
ago = pd.read_parquet("data/eurusd_m1_2026_08.parquet")
m1 = pd.concat([m1, ago], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["b5"] = m1["loc"].dt.floor("5min")
v = (m1.groupby("b5").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                          c=("close","last"), ts=("ts","last"), n=("ts","size")).reset_index())
v = v[v.n >= 3].reset_index(drop=True)
v["dia"] = v.b5.dt.date; v["hm"] = v.b5.dt.hour*100 + v.b5.dt.minute
O,H,L,C = v.o.to_numpy(), v.h.to_numpy(), v.l.to_numpy(), v.c.to_numpy()

def gatillo(i, niv, lado):
    """A: el cuerpo entero a un lado del nivel. B: cierra pasado el cuerpo de
    la ultima vela contraria. En los dos casos la vela va en ese sentido."""
    o, c = O[i], C[i]
    misma = (c > o) if lado > 0 else (c < o)
    if not misma: return None
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
            if not toca and min(abs(H[i]-niv), abs(L[i]-niv))/U > REARME:
                armado = True
            if not (armado and toca): continue
            for lado in (1, -1):
                g_ = gatillo(i, niv, lado)
                if g_ is None: continue
                ent = C[i]
                stp = L[i-1] if lado > 0 else H[i-1]
                rgo = abs(ent - stp)
                if rgo <= 0: break
                tp = ent + 2*rgo*lado
                filas.append(dict(dia=dia, i=int(i), lado=lado, tipo=g_, nivel="alto" if niv==hi else "mínimo",
                                  entrada=ent, stop=stp, obj=tp, riesgo=rgo/U, hora=int(v.hm.iloc[i])//100))
                armado = False
                break

t = pd.DataFrame(filas)
t["ts"] = v.ts.to_numpy()[t.i]; t["ts"] = pd.to_datetime(t.ts)

# resolucion en M1, hasta las 22:00 del mismo dia
ts1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy(); C1 = m1.close.to_numpy()
finHM = m1.loc[:, "loc"].dt.hour*100 + m1.loc[:, "loc"].dt.minute
finDia = m1.loc[:, "loc"].dt.date.to_numpy(); finHM = finHM.to_numpy()
R, mot = [], []
for r in t.itertuples():
    j0 = int(np.searchsorted(ts1, np.datetime64(r.ts), side="right"))
    fin = np.where((finDia[j0:] != r.dia) | (finHM[j0:] >= FIN))[0]
    j1 = j0 + (int(fin[0]) if len(fin) else len(ts1)-j0)
    j1 = max(j1, j0+1)
    hh, ll = H1[j0:j1], L1[j0:j1]
    gt, gs = ((hh >= r.obj, ll <= r.stop) if r.lado > 0 else (ll <= r.obj, hh >= r.stop))
    it = int(np.argmax(gt)) if gt.any() else 10**9
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    if it == 10**9 and isl == 10**9:
        sal = C1[j1-1]
        R.append(((sal-r.entrada) if r.lado>0 else (r.entrada-sal))/abs(r.entrada-r.stop)); mot.append("cierre")
    elif isl <= it: R.append(-1.0); mot.append("SL")
    else: R.append(2.0); mot.append("TP")
t["R"] = R; t["motivo"] = mot
t["neto"] = t.R - COSTE/t.riesgo
t.to_csv("data/asia_nivel.csv", index=False)

def bloque(nom, s):
    if len(s) < 5: print(f"\n{nom}: n insuficiente ({len(s)})"); return
    dia = s.groupby("dia").agg(R=("R","mean"), neto=("neto","mean"))
    ee = dia.R.std(ddof=1)/np.sqrt(len(dia)); een = dia.neto.std(ddof=1)/np.sqrt(len(dia))
    anos = (s.ts.max()-s.ts.min()).days/365.25
    print(f"\n{nom}")
    print(f"  {len(s):,} disparos en {len(dia):,} días  ·  {len(s)/max(anos,.01):.0f} al año  ·  "
          f"{len(s)/len(dia):.2f} por día")
    print(f"  riesgo mediano {s.riesgo.median():.1f} p  ·  el spread es el {100*COSTE/s.riesgo.median():.0f} % del riesgo")
    print(f"  %TP {100*(s.motivo=='TP').mean():.1f} %   (geometría de un 1:2 = 33,3 %)")
    print(f"  por operación: bruta {s.R.mean():+.3f} · neta {s.neto.mean():+.3f}")
    print(f"  POR DÍA:  bruta {dia.R.mean():+.3f} ± {ee:.3f} (z {dia.R.mean()/ee:+.2f})  ·  "
          f"neta {dia.neto.mean():+.3f} ± {een:.3f} (z {dia.neto.mean()/een:+.2f})")
    inv = (1/s.riesgo).mean()
    print(f"  coste de equilibrio c* = {s.R.mean()/inv if inv>0 else float('nan'):.2f} pips")

print("="*100)
print("LA REGLA DEL USUARIO · docs/PREREGISTRO_asia_nivel.md · una sola vez")
print("="*100)
bloque("PRINCIPAL · 2020-2025", t[t.ts < "2026-01-01"])
bloque("secundaria · 2026 ene-jul", t[(t.ts >= "2026-01-01") & (t.ts < "2026-08-01")])
bloque("su mes (de donde sale la regla, NO cuenta)", t[t.ts >= "2026-08-01"])
s = t[t.ts < "2026-01-01"]
print("\n\nreparto en 2020-2025:")
for k in ("tipo","nivel","lado"):
    print(f"  por {k}:")
    for x,gg in s.groupby(k):
        et = {1:"compra",-1:"venta"}.get(x,x)
        print(f"    {str(et):>8}  n={len(gg):>5}  %TP {100*(gg.motivo=='TP').mean():>5.1f} %  "
              f"bruta {gg.R.mean():>+7.3f}  neta {gg.neto.mean():>+7.3f}")
