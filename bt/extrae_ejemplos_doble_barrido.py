"""Saca ejemplos reales de la celda principal, con todo lo que hay que dibujar."""
import json, numpy as np, pandas as pd
U, COSTE, RR, HOR = 1e-4, 1.43, 2.0, 2880
ANTES, DESPUES = 56, 72          # velas de M15 alrededor

M = pd.read_parquet("data/eurusd_m1.parquet"); M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)

def velas(mins):
    g = M.set_index("ts").resample(f"{mins}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return g[g.n >= mins*0.3]

def barrido(V):
    ph, pl = V.h.shift(1), V.l.shift(1)
    bl = (V.l < pl) & (V.c > pl) & (V.c < ph)
    bh = (V.h > ph) & (V.c < ph) & (V.c > pl)
    lado = np.where(bl & ~bh, 1, np.where(bh & ~bl, -1, 0)).astype(np.int8)
    ext = np.where(lado > 0, V.l.to_numpy(), np.where(lado < 0, V.h.to_numpy(), np.nan))
    return lado, ext, ph.to_numpy(), pl.to_numpy()

V12, V4, E = velas(720), velas(240), velas(15)
l12, _, ph12, pl12 = barrido(V12)
l4, e4, ph4, pl4 = barrido(V4)
eo,eh,el,ec = (E[x].to_numpy() for x in "ohlc"); et = E.index.to_numpy()
i12 = np.searchsorted(V12.index.to_numpy(), et, "right") - 1
i4  = np.searchsorted(V4.index.to_numpy(),  et, "right") - 1
ok = (i12 >= 0) & (i4 >= 0)
c12 = np.clip(i12,0,None); c4 = np.clip(i4,0,None)
L12 = np.where(ok, l12[c12], 0); L4 = np.where(ok, l4[c4], 0)
doble = np.where((L12 == L4) & (L12 != 0), L12, 0)
cA, cB = np.minimum(eo,ec), np.maximum(eo,ec)
env = np.r_[False, (cB[:-1] <= cB[1:]) & (cA[:-1] >= cA[1:])]
mh, ml, mt = M.high.to_numpy(), M.low.to_numpy(), M.ts.to_numpy()

ej, ult = [], -10**9
for k in range(1, len(E)-1):
    lado = int(doble[k])
    if lado == 0 or k <= ult: continue
    if not ((ec[k] > eo[k]) if lado > 0 else (ec[k] < eo[k])) or not env[k]: continue
    stop = e4[c4[k]]
    if not np.isfinite(stop): continue
    ent = ec[k]
    if (stop >= ent) if lado > 0 else (stop <= ent): continue
    rgo = abs(ent-stop)
    if rgo < 0.5*U: continue
    tp = ent + lado*RR*rgo
    j0 = int(np.searchsorted(mt, et[k] + np.timedelta64(15,"m"))); j1 = min(j0+HOR, len(mt))
    if j1 <= j0+3: continue
    hh, ll = mh[j0:j1], ml[j0:j1]
    a = np.flatnonzero(hh >= tp) if lado > 0 else np.flatnonzero(ll <= tp)
    b = np.flatnonzero(ll <= stop) if lado > 0 else np.flatnonzero(hh >= stop)
    ia, ib = (int(a[0]) if len(a) else 10**9), (int(b[0]) if len(b) else 10**9)
    if ia == ib == 10**9: continue
    gana = ia < ib
    ult = k
    k0, k1 = max(0,k-ANTES), min(len(E), k+DESPUES)
    # la vela de M15 donde se resuelve
    tfin = mt[j0 + min(ia,ib)]
    kfin = int(np.searchsorted(et, tfin, "right")) - 1
    ej.append(dict(
        t=pd.Timestamp(et[k]).strftime("%d/%m/%Y %H:%M"), lado=lado, gana=int(gana),
        i=k-k0, ifin=max(0, min(k1-k0-1, kfin-k0)),
        ent=round(float(ent),5), stop=round(float(stop),5), tp=round(float(tp),5),
        rgo=round(rgo/U,1), coste=round(100*COSTE/(rgo/U),1),
        h12=round(float(ph12[c12[k]]),5), l12=round(float(pl12[c12[k]]),5),
        h4=round(float(ph4[c4[k]]),5),  l4=round(float(pl4[c4[k]]),5),
        o=[round(x,5) for x in eo[k0:k1]], h=[round(x,5) for x in eh[k0:k1]],
        l=[round(x,5) for x in el[k0:k1]], c=[round(x,5) for x in ec[k0:k1]],
        hm=[pd.Timestamp(x).strftime("%H:%M") for x in et[k0:k1]]))

rng = np.random.default_rng(7)
G = [x for x in ej if x["gana"]]; P = [x for x in ej if not x["gana"]]
sel = list(rng.choice(G, 12, replace=False)) + list(rng.choice(P, 12, replace=False))
sel.sort(key=lambda x: x["t"][6:10]+x["t"][3:5]+x["t"][:2]+x["t"][11:])
P_ = "/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/art/ejemplos.json"
json.dump(sel, open(P_,"w"), separators=(",",":"))
import os
print(f"{len(ej)} señales en EURUSD · {len(G)} ganan, {len(P)} pierden "
      f"({100*len(G)/len(ej):.1f} %)")
print(f"{len(sel)} ejemplos guardados · {os.path.getsize(P_)/1024:.0f} KB")
