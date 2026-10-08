"""Doble barrido anidado + envolvente de entrada.
Especificacion cerrada en docs/PREREGISTRO_doble_barrido.md antes de medir.

  barrido en TF = la vela en curso se lleva UN extremo de la anterior cerrada
                  y cierra de vuelta dentro de su rango
  doble         = las dos TF del par, barrido activo del MISMO lado
  disparo       = primera envolvente de M15/M5 a favor del giro
  stop          = extremo de la envolvente     objetivo = 1:2

  python3 bt/doble_barrido.py
"""
import numpy as np, pandas as pd

INS = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
       "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
       "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
       "NAS100": ("data/nsxusd_m1.parquet", 1e0,  1.50),
       "SPX500": ("data/spxusd_m1.parquet", 1e0,  0.60)}
PARES = [(720,240,"12h+4h"), (480,240,"8h+4h"), (240,120,"4h+2h")]
ENTRADAS = [(15,"M15"), (5,"M5")]
RR, HOR = 2.0, 2880          # objetivo 1:2 · tope de 2 dias de M1

def velas(M, mins):
    """Velas de mins minutos, ancladas a medianoche UTC."""
    g = M.set_index("ts").resample(f"{mins}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return g[g.n >= mins*0.3]

def lado_barrido(V):
    """+1 barrio el minimo (busca compras), -1 barrio el maximo. 0 si nada o ambos."""
    ph, pl = V.h.shift(1), V.l.shift(1)
    bl = (V.l < pl) & (V.c > pl) & (V.c < ph)
    bh = (V.h > ph) & (V.c < ph) & (V.c > pl)
    return pd.Series(np.where(bl & ~bh, 1, np.where(bh & ~bl, -1, 0)),
                     index=V.index, dtype=np.int8)

def corre(par, ent_min, nom_par, nom_ent):
    tf_alta, tf_baja, _ = par
    filas = []
    for nom, (ruta, U, COSTE) in INS.items():
        M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
        M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
        VA, VB = velas(M, tf_alta), velas(M, tf_baja)
        la, lb = lado_barrido(VA), lado_barrido(VB)
        E = velas(M, ent_min)
        eo,eh,el,ec = (E[x].to_numpy() for x in "ohlc"); et = E.index.to_numpy()
        # lado vigente de cada TF en el instante de cada vela de entrada,
        # leyendo SOLO velas ya cerradas (shift de una vela)
        ia = np.searchsorted(VA.index.to_numpy(), et, "right") - 1
        ib = np.searchsorted(VB.index.to_numpy(), et, "right") - 1
        ok = (ia >= 0) & (ib >= 0)
        La = np.where(ok, la.to_numpy()[np.clip(ia,0,None)], 0)
        Lb = np.where(ok, lb.to_numpy()[np.clip(ib,0,None)], 0)
        doble = np.where((La == Lb) & (La != 0), La, 0)
        # envolvente: el cuerpo contiene por completo al anterior, a favor del giro
        cA, cB = np.minimum(eo,ec), np.maximum(eo,ec)
        env_alc = (ec > eo) & (np.r_[False, cB[:-1] <= cB[1:]][:len(ec)]) & \
                  (np.r_[False, cA[:-1] >= cA[1:]][:len(ec)])
        env_baj = (ec < eo) & (np.r_[False, cB[:-1] <= cB[1:]][:len(ec)]) & \
                  (np.r_[False, cA[:-1] >= cA[1:]][:len(ec)])
        mh, ml, mt = M.high.to_numpy(), M.low.to_numpy(), M.ts.to_numpy()
        ult = -10**9
        for k in range(1, len(E)-1):
            lado = int(doble[k])
            if lado == 0: continue
            if not (env_alc[k] if lado > 0 else env_baj[k]): continue
            if k <= ult: continue
            ent = ec[k]; stop = el[k] if lado > 0 else eh[k]
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
            R = RR if ia_ < ib_ else -1.0
            filas.append(dict(ins=nom, dia=pd.Timestamp(et[k]).date(),
                              R=R, rgo=rgo/U, coste=COSTE/(rgo/U)))
            ult = k
    D = pd.DataFrame(filas)
    if D.empty: return None
    D["neta"] = D.R - D.coste
    cl = D.ins + "|" + D.dia.astype(str)
    x = D.neta.to_numpy(); mu = x.mean()
    r = (D.neta - mu).groupby(cl).sum()
    ee = np.sqrt((r**2).sum())/len(x)
    return dict(par=nom_par, ent=nom_ent, n=len(D), acierto=(D.R>0).mean(),
                rgo=D.rgo.median(), coste=D.coste.median(),
                bruta=D.R.mean(), neta=mu, ee=ee, z=mu/ee if ee>0 else np.nan)

print("DOBLE BARRIDO ANIDADO + ENVOLVENTE · pre-registro 2db0010\n")
print(f"{'par':>8}{'entra':>7}{'n':>7}{'acierto':>9}{'riesgo':>9}{'coste %R':>10}"
      f"{'R BRUTA':>10}{'R NETA':>10}{'IC95':>20}{'z':>7}")
print("-"*97)
res = []
for par in PARES:
    for em, en in ENTRADAS:
        r = corre(par, em, par[2], en)
        if r is None:
            print(f"{par[2]:>8}{en:>7}{'sin disparos':>20}"); continue
        res.append(r)
        pri = "  <<<" if (par[2]=="12h+4h" and en=="M15") else ""
        print(f"{r['par']:>8}{r['ent']:>7}{r['n']:>7,}{r['acierto']:>8.1%}"
              f"{r['rgo']:>9.1f}{100*r['coste']:>9.1f}%{r['bruta']:>+10.4f}"
              f"{r['neta']:>+10.4f}"
              f"  [{r['neta']-1.96*r['ee']:+.3f},{r['neta']+1.96*r['ee']:+.3f}]"
              f"{r['z']:>7.2f}{pri}")
R = pd.DataFrame(res); R.to_csv("data/doble_barrido.csv", index=False)

P = R[(R.par=="12h+4h") & (R.ent=="M15")]
if len(P):
    p = P.iloc[0]; lo, hi = p.neta-1.96*p.ee, p.neta+1.96*p.ee
    print(f"\nCELDA PRINCIPAL declarada: 12h+4h · M15")
    print(f"  n {p.n:,}   bruta {p.bruta:+.4f}   neta {p.neta:+.4f}   "
          f"IC95 [{lo:+.3f}, {hi:+.3f}]   z {p.z:+.2f}")
    mde = 2*1.3/np.sqrt(p.n)
    print(f"  efecto mínimo detectable con esta n: {mde:+.3f} R "
          f"(el esperado era +0,05)")
    if lo > 0:
        msg = "SE CUMPLE: la neta excluye el cero por arriba."
    elif hi < 0:
        msg = "NO SE CUMPLE: la neta excluye el cero por ABAJO — negativa con holgura."
    else:
        msg = "NO SE CUMPLE: el intervalo incluye el cero."
    print("\n  >> " + msg)
print("\nLAS TRES PREDICCIONES")
if len(R):
    b = R.bruta.mean()
    print(f"  1 · bruta entre +0,05 y +0,15 ........ "
          f"{'SÍ' if 0.05 <= b <= 0.15 else 'NO'}  (media {b:+.4f})")
    print(f"  2 · coste > 20 % del riesgo ......... "
          f"{'SÍ' if R.coste.median() > 0.20 else 'NO'}  "
          f"({100*R.coste.median():.1f} %)")
    print(f"  3 · neta negativa en las 6 celdas ... "
          f"{'SÍ' if (R.neta < 0).all() else 'NO'}  "
          f"({int((R.neta<0).sum())} de {len(R)})")
