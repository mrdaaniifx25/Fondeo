"""Saca operaciones reales de las dos estrategias, con sus velas, para dibujarlas."""
import numpy as np, pandas as pd, json

TZ, U, COSTE = "Europe/Madrid", 1e-4, 1.43
m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
L = m1["loc"]; m1["dia"] = L.dt.normalize(); m1["hm"] = L.dt.hour*100 + L.dt.minute
MT = m1["loc"].to_numpy("datetime64[ns]")
MH, ML, MC = m1.high.to_numpy(), m1.low.to_numpy(), m1.close.to_numpy()
MDIA, MHM = m1.dia.to_numpy(), m1.hm.to_numpy()

def velas(mins):
    g = (m1.set_index("loc").resample(f"{mins}min", label="left", closed="left",
                                      origin="start_day")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    g = g[g.n >= max(1, mins*0.3)].reset_index().rename(columns={"loc":"t"})
    return g

V2, V5, V60 = velas(2), velas(5), velas(60)

def pivotes(d, tf, piv=3):
    h, l = d.h.to_numpy(), d.l.to_numpy(); t = d.t.to_numpy("datetime64[ns]")
    out = []
    for i in range(piv, len(d)-piv):
        if h[i] == h[i-piv:i+piv+1].max():
            out.append((t[i]+np.timedelta64(piv*tf, "m"), h[i], -1))
        if l[i] == l[i-piv:i+piv+1].min():
            out.append((t[i]+np.timedelta64(piv*tf, "m"), l[i], +1))
    out.sort(key=lambda x: x[0])
    return (np.array([x[0] for x in out], "datetime64[ns]"),
            np.array([x[1] for x in out]), np.array([x[2] for x in out], int))
NT, NP, NL = pivotes(V60, 60)

_dia = m1.groupby("dia").agg(hi=("high","max"), lo=("low","min"), n=("close","size"))
_dia = _dia[_dia.n > 200]
_asia = m1[m1.hm < 800].groupby("dia").agg(hi=("high","max"), lo=("low","min"), n=("close","size"))
_asia = _asia[_asia.n > 120]
_lon = m1[(m1.hm>=800)&(m1.hm<1400)].groupby("dia").agg(hi=("high","max"), lo=("low","min"), n=("close","size"))
_lon = _lon[_lon.n > 120]

def contexto(V, i_ent, antes=45, despues=55):
    a = max(0, i_ent-antes); b = min(len(V), i_ent+despues)
    s = V.iloc[a:b]
    velas_ = [dict(t=pd.Timestamp(r.t).strftime("%Y-%m-%d %H:%M"),
                   o=round(r.o,5), h=round(r.h,5), l=round(r.l,5), c=round(r.c,5))
              for r in s.itertuples()]
    # niveles del dia en que se entra
    d2 = pd.Timestamp(V.t.iloc[i_ent]).normalize()
    niv = {}
    if d2 in _asia.index:
        niv["asia_hi"] = round(float(_asia.hi[d2]),5); niv["asia_lo"] = round(float(_asia.lo[d2]),5)
    if d2 in _lon.index:
        niv["lon_hi"] = round(float(_lon.hi[d2]),5); niv["lon_lo"] = round(float(_lon.lo[d2]),5)
    if d2 in _dia.index:
        k = list(_dia.index).index(d2)
        if k > 0:
            niv["pdh"] = round(float(_dia.hi.iloc[k-1]),5)
            niv["pdl"] = round(float(_dia.lo.iloc[k-1]),5)
    return a, velas_, niv

# ================= ESTRATEGIA 1 · Benjamin (M2, nivel H1, 1:2) ================
def benjamin():
    d = V2; ts = d.t.to_numpy("datetime64[ns]")
    h, l, c = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    o = d.o.to_numpy(); N = len(d)
    al = np.zeros(N, bool); ba = np.zeros(N, bool)
    al[2:] = l[2:] > h[:-2]; ba[2:] = h[2:] < l[:-2]
    loc = pd.DatetimeIndex(ts); hm = loc.hour.to_numpy()+loc.minute.to_numpy()/60
    vent = ((hm >= 9)&(hm < 11))|((hm >= 14)&(hm < 16.5))
    dia = loc.normalize().to_numpy()
    ops, usado = [], set()
    for k in range(3, N-1):
        j = int(np.searchsorted(NT, ts[k], "right"))
        if j == 0: continue
        for q in range(max(0, j-40), j):
            lado, niv = NL[q], NP[q]
            if not ((h[k] > niv) if lado < 0 else (l[k] < niv)): continue
            clave = (dia[k], round(float(niv), 5))
            if clave in usado: continue
            kf = -1
            for z in range(k, min(k+30, N)):
                if (ba[z] if lado < 0 else al[z]): kf = z; break
            if kf < 0 or not vent[kf]: continue
            P = c[kf]; S = h[k:kf+1].max() if lado < 0 else l[k:kf+1].min()
            rgo = abs(S-P)
            if rgo <= 0: continue
            usado.add(clave)
            O = P - 2*rgo if lado < 0 else P + 2*rgo
            i0 = int(np.searchsorted(MT, ts[kf]+np.timedelta64(2,"m"), "left"))
            if i0 >= len(MT)-2: continue
            j1 = min(i0+24*60, len(MT))
            hh, ll = MH[i0:j1], ML[i0:j1]
            gt, gs = ((ll <= O, hh >= S) if lado < 0 else (hh >= O, ll <= S))
            it = int(np.argmax(gt)) if gt.any() else 10**9
            isl = int(np.argmax(gs)) if gs.any() else 10**9
            res = "TP" if it < isl else ("SL" if isl < 10**9 else "abierta")
            ops.append(dict(i_barrido=k, i_ent=kf, lado=int(lado), nivel=float(niv),
                            sesion="Londres" if hm[kf] < 12 else "NuevaYork",
                            entrada=float(P), sl=float(S), tp=float(O),
                            riesgo=round(rgo/U,1), res=res,
                            minutos=int(min(it,isl)) if res != "abierta" else None))
            break
    return ops

# ============ ESTRATEGIA 2 · Lozano (PDH/PDL/PSH/PSL + H4 + H1 + M5) =========
def lozano():
    d = V5; ts = d.t.to_numpy("datetime64[ns]")
    O5,H5,L5,C5 = (d[x].to_numpy() for x in ("o","h","l","c"))
    loc = pd.DatetimeIndex(ts); HM5 = loc.hour.to_numpy()*100+loc.minute.to_numpy()
    D5 = loc.normalize().to_numpy(); N = len(d)
    V240 = velas(240)
    F60 = (V60.t + pd.Timedelta(minutes=60)).to_numpy("datetime64[ns]")
    F240 = (V240.t + pd.Timedelta(minutes=240)).to_numpy("datetime64[ns]")
    H60,L60,C60 = V60.h.to_numpy(), V60.l.to_numpy(), V60.c.to_numpy()
    H240,L240,C240 = V240.h.to_numpy(), V240.l.to_numpy(), V240.c.to_numpy()
    dia_ = m1.groupby("dia").agg(hi=("high","max"), lo=("low","min"), n=("close","size"))
    dia_ = dia_[dia_.n > 200]
    asia = m1[m1.hm < 800].groupby("dia").agg(hi=("high","max"), lo=("low","min"), n=("close","size"))
    asia = asia[asia.n > 120]
    lon = m1[(m1.hm>=800)&(m1.hm<1400)].groupby("dia").agg(hi=("high","max"), lo=("low","min"), n=("close","size"))
    lon = lon[lon.n > 120]
    PD = {d2: (dia_.hi.iloc[i-1], dia_.lo.iloc[i-1]) for i, d2 in enumerate(dia_.index) if i > 0}
    def envolvente(i, lado):
        baj = C5[i] < O5[i]
        if (lado < 0) != baj: return False
        for j in range(i-1, max(i-13,-1), -1):
            if (C5[j] < O5[j]) == baj: continue
            a, b = min(O5[j],C5[j]), max(O5[j],C5[j])
            return (O5[i]>=b and C5[i]<=a) if lado<0 else (O5[i]<=a and C5[i]>=b)
        return False
    ops = []
    for dd in np.unique(D5):
        d2 = pd.Timestamp(dd)
        if d2 not in PD or d2 not in asia.index: continue
        pdh, pdl = PD[d2]
        for ses, (a,b) in (("Londres",(900,1100)), ("NuevaYork",(1400,1630))):
            S = asia if ses=="Londres" else lon
            if d2 not in S.index: continue
            NIV = [("PDH",pdh,-1),("PDL",pdl,+1),
                   ("PSH",float(S.hi[d2]),-1),("PSL",float(S.lo[d2]),+1)]
            idx = np.where((D5==dd)&(HM5>=a)&(HM5<b))[0]
            if len(idx) < 3: continue
            for nom, niv, lado in NIV:
                hecho = False
                for i in idx:
                    if hecho: break
                    if (lado<0 and C5[i]>niv) or (lado>0 and C5[i]<niv): break
                    barre = (H5[i]>niv and C5[i]<niv) if lado<0 else (L5[i]<niv and C5[i]>niv)
                    if not barre: continue
                    k4 = int(np.searchsorted(F240, ts[i], "right"))
                    if not any((H240[q]>niv and C240[q]<niv) if lado<0 else (L240[q]<niv and C240[q]>niv)
                               for q in range(max(0,k4-6),k4)): continue
                    k1 = int(np.searchsorted(F60, ts[i], "right"))
                    if not any((H60[q]>niv and C60[q]<niv) if lado<0 else (L60[q]<niv and C60[q]>niv)
                               for q in range(max(0,k1-6),k1)): continue
                    ext = H5[i] if lado<0 else L5[i]
                    for z in range(i, min(i+13,N)):
                        if D5[z]!=dd or HM5[z]>=b: break
                        ext = max(ext,H5[z]) if lado<0 else min(ext,L5[z])
                        if z==i or not envolvente(z,lado): continue
                        P = C5[z]; SL = ext + (1.0*U if lado<0 else -1.0*U)
                        rgo = abs(SL-P)
                        if rgo<=0: break
                        TP = P - 2*rgo if lado<0 else P + 2*rgo
                        i0 = int(np.searchsorted(MT, ts[z]+np.timedelta64(5,"m"), "left"))
                        kf = np.where((MDIA[i0:]!=dd)|(MHM[i0:]>=2300))[0]
                        j1 = max(i0+(int(kf[0]) if len(kf) else len(MT)-i0), i0+1)
                        hh, ll = MH[i0:j1], ML[i0:j1]
                        gt, gs = ((ll<=TP, hh>=SL) if lado<0 else (hh>=TP, ll<=SL))
                        it = int(np.argmax(gt)) if gt.any() else 10**9
                        isl = int(np.argmax(gs)) if gs.any() else 10**9
                        res = "TP" if it<isl else ("SL" if isl<10**9 else "cierre")
                        ops.append(dict(i_barrido=i, i_ent=z, lado=int(lado), nivel=float(niv),
                                        etiqueta=nom, sesion=ses, entrada=float(P),
                                        sl=float(SL), tp=float(TP), riesgo=round(rgo/U,1),
                                        res=res, minutos=int(min(it,isl)) if res!="cierre" else None))
                        hecho = True; break
    return ops

SALIDA = {}
for nombre, fn, V, tf in (("benjamin", benjamin, V2, 2), ("lozano", lozano, V5, 5)):
    ops = fn()
    g = [o for o in ops if o["res"]=="TP"]
    p = [o for o in ops if o["res"]=="SL"]
    print(f"{nombre}: {len(ops):,} operaciones · {len(g)} TP · {len(p)} SL "
          f"({100*len(g)/max(len(g)+len(p),1):.1f} % de acierto)")
    rng = np.random.default_rng(3)
    sel = []
    for ses in ("Londres", "NuevaYork"):
        for grupo, cuantas in ((g, 2), (p, 2)):
            cand = [o for o in grupo if o.get("sesion") == ses]
            if not cand: continue
            idx = rng.choice(len(cand), min(cuantas, len(cand)), replace=False)
            sel += [cand[k] for k in idx]
    print(f"  seleccion: " + ", ".join(
        f"{ses} {sum(1 for o in sel if o['sesion']==ses and o['res']==r)} {r}"
        for ses in ("Londres","NuevaYork") for r in ("TP","SL")))
    ejs = []
    for o in sel:
        base, velas_, niv = contexto(V, o["i_ent"])
        ejs.append(dict(**{k:v for k,v in o.items() if not k.startswith("i_")},
                        tf=tf, velas=velas_, niveles=niv,
                        i_barrido=o["i_barrido"]-base, i_ent=o["i_ent"]-base))
    SALIDA[nombre] = dict(n=len(ops), tp=len(g), sl=len(p), ejemplos=ejs)
def limpia(x):
    if isinstance(x, dict): return {k: limpia(v) for k, v in x.items()}
    if isinstance(x, list): return [limpia(v) for v in x]
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (np.floating,)): return float(x)
    return x
json.dump(limpia(SALIDA), open("data/ejemplos.json","w"))
print("\ndata/ejemplos.json escrito")
