"""docs/PREREGISTRO_trendline.md · rotura de linea de tendencia en M5.

Una linea de tendencia son dos pivotes unidos y prolongados. Nada se usa antes
de estar confirmado: un pivote en j no existe hasta la vela j+w.

  python3 bt/trendline.py [instrumento]
"""
import sys
import numpy as np, pandas as pd
from math import sqrt, erf

TZ, W, SEP, VIDA = "Europe/Madrid", 2, 3, 60
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
zf = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x))) if len(x) > 2 else np.nan

INS = {
 "EURUSD": (["data/eurusd_m1.parquet","data/eurusd_m1_2026_08.parquet"], 1e-4, 1.43),
 "GBPUSD": (["data/gbpusd_m1.parquet"],                                   1e-4, 1.80),
 "USDJPY": (["data/usdjpy_m1.parquet"],                                   1e-2, 1.50),
 "XAUUSD": (["data/xauusd_m1.parquet","data/xauusd_m1_2026.parquet"],     0.10, 5.00),
 "NSXUSD": (["data/nsxusd_m1.parquet"],                                   1.00, 2.00),
 "SPXUSD": (["data/spxusd_m1.parquet"],                                   1.00, 0.80),
 "GRXEUR": (["data/grxeur_m1.parquet","data/grxeur_m1_2026.parquet"],     1.00, 2.00),
}

def carga(fs):
    d = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)
    d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").reset_index(drop=True)
    d["loc"] = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    d["dia"] = d["loc"].dt.date
    d["min"] = d["loc"].dt.hour*60 + d["loc"].dt.minute
    return d

def m5(d):
    g = d.assign(b=(d["min"]//5)*5).groupby(["dia","b"]).agg(
        o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
        n=("close","size"), t=("loc","first")).reset_index()
    g = g[g.n >= 3].reset_index(drop=True)
    g["cierre"] = g.t + pd.Timedelta(minutes=5)
    return g

def pivotes(H, L, w):
    """Indices de pivote. Cada uno se confirma w velas despues."""
    n = len(H)
    pa = np.zeros(n, bool); pb = np.zeros(n, bool)
    for j in range(w, n-w):
        if H[j] == H[j-w:j+w+1].max() and H[j] > H[j-w:j].max(): pa[j] = True
        if L[j] == L[j-w:j+w+1].min() and L[j] < L[j-w:j].min(): pb[j] = True
    return pa, pb

def roturas(V):
    """Devuelve (i, lado, stopA, stopB) de cada rotura de linea."""
    H, L, C = V.h.to_numpy(), V.l.to_numpy(), V.c.to_numpy()
    pa, pb = pivotes(H, L, W)
    altos, bajos = [], []            # pivotes ya confirmados
    out = []
    lineaR = lineaS = None           # (p1, y1, pendiente)
    for i in range(W, len(V)):
        j = i - W                    # el pivote de j se confirma ahora
        if pa[j]:
            for p1 in reversed(altos):
                if j - p1 >= SEP and H[p1] > H[j]:
                    lineaR = (p1, H[p1], (H[j]-H[p1])/(j-p1), j); break
            altos.append(j)
        if pb[j]:
            for p1 in reversed(bajos):
                if j - p1 >= SEP and L[p1] < L[j]:
                    lineaS = (p1, L[p1], (L[j]-L[p1])/(j-p1), j); break
            bajos.append(j)
        for lin, lado in ((lineaR, 1), (lineaS, -1)):
            if lin is None: continue
            p1, y1, m, p2 = lin
            if i - p2 > VIDA:
                if lado > 0: lineaR = None
                else: lineaS = None
                continue
            y  = y1 + m*(i - p1)
            yp = y1 + m*(i-1 - p1)
            cruza = (C[i] > y and C[i-1] <= yp) if lado > 0 else (C[i] < y and C[i-1] >= yp)
            if not cruza: continue
            stopA = L[i] if lado > 0 else H[i]
            k = [q for q in (bajos if lado > 0 else altos) if q < i]
            stopB = (L[k[-1]] if lado > 0 else H[k[-1]]) if k else stopA
            out.append((i, lado, stopA, stopB))
            if lado > 0: lineaR = None
            else: lineaS = None
    return out

def corre(nom, ventana):
    fs, U, COSTE = INS[nom]
    d = carga(fs); V = m5(d)
    if ventana == "londres":
        ini, fin = 480, 690
        V = V[(V.b >= ini) & (V.b < fin)].reset_index(drop=True)
        cierre_dia = 690
    else:
        cierre_dia = 22*60
    R = roturas(V)
    T = d["loc"].to_numpy(); Hm = d.high.to_numpy(); Lm = d.low.to_numpy(); Cm = d.close.to_numpy()
    filas = []
    for stopq in ("A", "B"):
        for k in (1, 2, 3):
            libre = pd.Timestamp("1900-01-01")
            for i, lado, sA, sB in R:
                ts = V.cierre.iloc[i]
                if ts <= libre: continue
                if ventana == "londres" and i > 0 and V.dia.iloc[i] != V.dia.iloc[i-1]:
                    pass
                ent = float(V.c.iloc[i]); stp = float(sA if stopq == "A" else sB)
                rgo = abs(ent - stp)
                if rgo < 1.5*U: continue
                tp = ent + lado*k*rgo
                fin_ts = pd.Timestamp(V.dia.iloc[i]) + pd.Timedelta(minutes=cierre_dia)
                if fin_ts <= ts: continue
                a = int(np.searchsorted(T, np.datetime64(ts)))
                b = int(np.searchsorted(T, np.datetime64(fin_ts)))
                b = min(max(b, a+1), len(T))
                hh, ll = Hm[a:b], Lm[a:b]
                largo = lado > 0
                gs, gt = ((ll <= stp, hh >= tp) if largo else (hh >= stp, ll <= tp))
                isl = int(np.argmax(gs)) if gs.any() else 10**9
                itp = int(np.argmax(gt)) if gt.any() else 10**9
                if isl == 10**9 and itp == 10**9:
                    sal = Cm[b-1]; Rr = ((sal-ent) if largo else (ent-sal))/rgo; mot = "cierre"
                    libre = fin_ts
                else:
                    Rr, mot = (-1.0, "SL") if isl <= itp else (float(k), "TP")
                    libre = pd.Timestamp(T[a + min(isl, itp)])
                filas.append(dict(ins=nom, ventana=ventana, stop=stopq, k=k,
                                  ts=ts, lado=lado, rgo=rgo/U, R=Rr, mot=mot,
                                  neta=Rr - COSTE/(rgo/U)))
    return pd.DataFrame(filas), len(R)

if __name__ == "__main__":
    nom = sys.argv[1] if len(sys.argv) > 1 else "EURUSD"
    todo = []
    for v in ("londres", "dia"):
        t, nr = corre(nom, v)
        todo.append(t)
        print(f"{nom} · {v}: {nr} roturas detectadas", flush=True)
    t = pd.concat(todo, ignore_index=True)
    t.to_csv(f"data/trendline_{nom}.csv", index=False)
    print(f"\n{'ventana':>9s} {'stop':>5s} {'k':>2s} {'n':>6s} {'acierto':>9s} {'geom':>7s} "
          f"{'dif':>7s} {'stop p':>7s} {'c/s':>6s} {'R neta':>8s} {'z':>7s} {'c*':>7s}")
    print("-"*92)
    for v in ("londres", "dia"):
        for sq in ("A","B"):
            for k in (1,2,3):
                s = t[(t.ventana==v)&(t.stop==sq)&(t.k==k)]
                if len(s) < 30: continue
                r = s[s.mot != "cierre"]; ac = (r.mot=="TP").mean(); geo = 1/(1+k)
                z = zf(s.neta.to_numpy())
                cst = s.R.mean()/(1/s.rgo).mean()
                print(f"{v:>9s} {sq:>5s} {k:2d} {len(s):6d} {100*ac:8.1f}% {100*geo:6.1f}% "
                      f"{100*(ac-geo):+6.1f}pt {s.rgo.median():6.1f} "
                      f"{100*(INS[nom][2]/s.rgo.median()):5.1f}% {s.neta.mean():+8.3f} "
                      f"{z:+7.2f} {cst:7.2f}" + ("  *" if abs(z) > 2.87 else ""))
