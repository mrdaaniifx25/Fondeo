"""Doble barrido anidado, stop en el extremo del barrido de 4h.
Pre-registro cd653c2. Identico a bt/doble_barrido.py salvo el stop.
Reporta SIEMPRE los cinco instrumentos, declarado de antemano.
"""
import numpy as np, pandas as pd

INS = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
       "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
       "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
       "NAS100": ("data/nsxusd_m1.parquet", 1e0,  1.50),
       "SPX500": ("data/spxusd_m1.parquet", 1e0,  0.60)}
PARES = [(720,240,"12h+4h"), (480,240,"8h+4h"), (240,120,"4h+2h")]
ENTRADAS = [(15,"M15"), (5,"M5")]
RR, HOR = 2.0, 2880

def velas(M, mins):
    g = M.set_index("ts").resample(f"{mins}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return g[g.n >= mins*0.3]

def barrido(V):
    """lado (+1 barrio el minimo) y el EXTREMO que dejo el barrido."""
    ph, pl = V.h.shift(1), V.l.shift(1)
    bl = (V.l < pl) & (V.c > pl) & (V.c < ph)
    bh = (V.h > ph) & (V.c < ph) & (V.c > pl)
    lado = np.where(bl & ~bh, 1, np.where(bh & ~bl, -1, 0)).astype(np.int8)
    ext = np.where(lado > 0, V.l.to_numpy(), np.where(lado < 0, V.h.to_numpy(), np.nan))
    return pd.Series(lado, index=V.index), pd.Series(ext, index=V.index)

def corre(par, ent_min):
    tf_alta, tf_baja, _ = par
    filas = []
    for nom, (ruta, U, COSTE) in INS.items():
        M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
        M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
        VA, VB = velas(M, tf_alta), velas(M, tf_baja)
        la, _ = barrido(VA)
        lb, eb = barrido(VB)                      # el extremo del barrido de la TF baja
        E = velas(M, ent_min)
        eo,eh,el,ec = (E[x].to_numpy() for x in "ohlc"); et = E.index.to_numpy()
        ia = np.searchsorted(VA.index.to_numpy(), et, "right") - 1
        ib = np.searchsorted(VB.index.to_numpy(), et, "right") - 1
        ok = (ia >= 0) & (ib >= 0)
        La = np.where(ok, la.to_numpy()[np.clip(ia,0,None)], 0)
        Lb = np.where(ok, lb.to_numpy()[np.clip(ib,0,None)], 0)
        Eb = np.where(ok, eb.to_numpy()[np.clip(ib,0,None)], np.nan)
        doble = np.where((La == Lb) & (La != 0), La, 0)
        cA, cB = np.minimum(eo,ec), np.maximum(eo,ec)
        env = np.r_[False, (cB[:-1] <= cB[1:]) & (cA[:-1] >= cA[1:])]
        env_alc = (ec > eo) & env
        env_baj = (ec < eo) & env
        mh, ml, mt = M.high.to_numpy(), M.low.to_numpy(), M.ts.to_numpy()
        ult = -10**9
        for k in range(1, len(E)-1):
            lado = int(doble[k])
            if lado == 0 or k <= ult: continue
            if not (env_alc[k] if lado > 0 else env_baj[k]): continue
            stop = Eb[k]                          # <- EL UNICO CAMBIO
            if not np.isfinite(stop): continue
            ent = ec[k]
            if (stop >= ent) if lado > 0 else (stop <= ent): continue
            rgo = abs(ent-stop)
            if rgo < 0.5*U: continue
            tp = ent + lado*RR*rgo
            j0 = int(np.searchsorted(mt, et[k] + np.timedelta64(ent_min,"m")))
            j1 = min(j0+HOR, len(mt))
            if j1 <= j0+3: continue
            hh, ll = mh[j0:j1], ml[j0:j1]
            a = np.flatnonzero(hh >= tp) if lado > 0 else np.flatnonzero(ll <= tp)
            b = np.flatnonzero(ll <= stop) if lado > 0 else np.flatnonzero(hh >= stop)
            ia_, ib_ = (int(a[0]) if len(a) else 10**9), (int(b[0]) if len(b) else 10**9)
            if ia_ == ib_ == 10**9: continue
            filas.append(dict(ins=nom, dia=pd.Timestamp(et[k]).date(),
                              R=RR if ia_ < ib_ else -1.0,
                              rgo=rgo/U, coste=COSTE/(rgo/U)))
            ult = k
    return pd.DataFrame(filas)

def resume(D):
    D = D.copy(); D["neta"] = D.R - D.coste
    cl = D.ins + "|" + D.dia.astype(str)
    mu = D.neta.mean(); r = (D.neta - mu).groupby(cl).sum()
    ee = np.sqrt((r**2).sum())/len(D)
    return dict(n=len(D), acierto=(D.R>0).mean(), rgo=D.rgo.median(),
                coste=D.coste.median(), bruta=D.R.mean(), neta=mu, ee=ee,
                z=mu/ee if ee>0 else np.nan)

print("DOBLE BARRIDO · STOP EN EL BARRIDO DE 4h · pre-registro cd653c2\n")
print(f"{'par':>8}{'entra':>7}{'n':>7}{'acierto':>9}{'riesgo':>9}{'coste %R':>10}"
      f"{'R BRUTA':>10}{'R NETA':>10}{'IC95':>20}{'z':>7}")
print("-"*97)
guarda = {}
for par in PARES:
    for em, en in ENTRADAS:
        D = corre(par, em)
        if D.empty: continue
        guarda[(par[2], en)] = D
        r = resume(D)
        pri = "  <<<" if (par[2]=="12h+4h" and en=="M15") else ""
        print(f"{par[2]:>8}{en:>7}{r['n']:>7,}{r['acierto']:>8.1%}{r['rgo']:>9.1f}"
              f"{100*r['coste']:>9.1f}%{r['bruta']:>+10.4f}{r['neta']:>+10.4f}"
              f"  [{r['neta']-1.96*r['ee']:+.3f},{r['neta']+1.96*r['ee']:+.3f}]"
              f"{r['z']:>7.2f}{pri}")

D = guarda.get(("12h+4h","M15"))
if D is not None:
    r = resume(D); lo, hi = r['neta']-1.96*r['ee'], r['neta']+1.96*r['ee']
    print(f"\nCELDA PRINCIPAL · 12h+4h · M15")
    print(f"  n {r['n']:,}   riesgo {r['rgo']:.1f} p   coste {100*r['coste']:.1f} %"
          f"   bruta {r['bruta']:+.4f}   neta {r['neta']:+.4f}")
    print(f"  IC95 [{lo:+.3f}, {hi:+.3f}]   z {r['z']:+.2f}")
    mde = 2*1.3/np.sqrt(r['n'])
    print(f"  efecto mínimo detectable: {mde:+.3f} R")
    print("\n  >> " + ("SE CUMPLE: excluye el cero por arriba." if lo > 0
          else ("NO SE CUMPLE: excluye el cero por ABAJO." if hi < 0
                else "NO SE CUMPLE: el intervalo incluye el cero.")))
    print(f"\nPOR INSTRUMENTO (declarado de antemano · ninguno cuenta como éxito)\n")
    print(f"{'instrumento':<12}{'n':>7}{'acierto':>9}{'riesgo':>9}{'coste %R':>10}"
          f"{'R BRUTA':>10}{'R NETA':>10}")
    print("-"*67)
    for ins, g in D.groupby("ins"):
        q = resume(g)
        marca = "   <- EURUSD" if ins == "EURUSD" else ""
        print(f"{ins:<12}{q['n']:>7,}{q['acierto']:>8.1%}{q['rgo']:>9.1f}"
              f"{100*q['coste']:>9.1f}%{q['bruta']:>+10.4f}{q['neta']:>+10.4f}{marca}")
