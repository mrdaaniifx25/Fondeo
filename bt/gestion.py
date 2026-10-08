"""¿Y si el problema no es la entrada sino como se gestiona la operacion?

Todo lo probado hasta ahora coloca SL y TP y no los toca. Aqui se toman los
MISMOS setups (CRT + order block + DOL diario, los unicos con senal medida) y
se les aplican reglas de gestion distintas, recorriendo vela a vela en M1.
"""
import numpy as np, pandas as pd
from math import sqrt, erf
import sys; sys.path.insert(0,"bt")

PIP=0.0001; COSTE=1.2
m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
ch = pd.read_parquet("data/ch_dol.parquet")
src = open("bt/estrategia_dol.py").read().replace("if d_fav > d_con: continue",
                                                  "if d_fav > 0.5*d_con: continue")
ns={}; exec(compile(src,"m","exec"), ns)
cfg = ns["C"](dol_filtro=True, tp_r=3.0)
sig,_ = ns["senales"](ch, cfg)
print(f"setups: {len(sig)}\n")

T=m1["ts"].to_numpy(); H=m1["high"].to_numpy(); L=m1["low"].to_numpy()
C=m1["close"].to_numpy(); O=m1["open"].to_numpy()

def gestiona(sig, modo, tp_r=3.0, be_en=1.0, parcial_en=1.0, frac=0.5,
             trail_r=1.0, horas=168):
    """Recorre M1 aplicando la regla de gestion. Devuelve R netos por operacion."""
    out, libre = [], np.datetime64("1970-01-01")
    for s in sig.itertuples():
        ets = np.datetime64(pd.Timestamp(s.ts)+pd.Timedelta(minutes=15))
        if ets < libre: continue
        i0=int(np.searchsorted(T,ets)); i1=min(i0+horas*60,len(T))
        if i0>=len(T) or i1<=i0: continue
        ent, sl0 = s.entrada, s.sl
        riesgo = abs(ent-sl0); largo = s.largo
        if riesgo<=0: continue
        R1 = riesgo
        tp = ent + tp_r*R1 if largo else ent - tp_r*R1
        sl = sl0
        cerrado = 0.0        # fraccion ya cerrada
        acum = 0.0           # R acumulado de los parciales
        mfe = 0.0            # maxima excursion favorable en R
        fin = i1-1; salida=None
        for i in range(i0, i1):
            hi, lo = H[i], L[i]
            fav = (hi-ent)/R1 if largo else (ent-lo)/R1
            mfe = max(mfe, fav)
            # --- parcial ---
            if modo in ("parcial","parcial_be","parcial_trail") and cerrado==0 and fav>=parcial_en:
                acum += frac*parcial_en; cerrado = frac
                if modo in ("parcial_be","parcial_trail"): sl = ent
            # --- break even ---
            if modo=="be" and fav>=be_en and ((largo and sl<ent) or (not largo and sl>ent)):
                sl = ent
            # --- trailing ---
            if modo in ("trail","parcial_trail") and fav>=trail_r:
                nuevo = (hi - trail_r*R1) if largo else (lo + trail_r*R1)
                sl = max(sl,nuevo) if largo else min(sl,nuevo)
            # --- salidas ---
            toca_sl = (lo<=sl) if largo else (hi>=sl)
            toca_tp = (hi>=tp) if largo else (lo<=tp)
            if toca_sl and (modo not in ("trail",) or True):
                r_sl = (sl-ent)/R1 if largo else (ent-sl)/R1
                acum += (1-cerrado)*r_sl; fin=i; salida="SL"; break
            if toca_tp and modo!="trail":
                acum += (1-cerrado)*tp_r; fin=i; salida="TP"; break
        if salida is None:
            px = C[fin]
            r = (px-ent)/R1 if largo else (ent-px)/R1
            acum += (1-cerrado)*r; salida="tiempo"
        neto = acum - COSTE/(R1/PIP)
        out.append(dict(ts=s.ts, R=neto, bruto=acum, mfe=mfe, salida=salida))
        libre = T[fin]
    return pd.DataFrame(out)

def resume(tr, nom):
    if tr.empty: return
    gan,per = tr[tr.R>0], tr[tr.R<=0]
    pf = gan.R.sum()/(-per.R.sum()) if per.R.sum()<0 else float("inf")
    eq,pico,dd = 10000.0,10000.0,0.0
    for R in tr.R:
        eq*=(1+0.01*R); pico=max(pico,eq); dd=max(dd,(pico-eq)/pico)
    z = tr.R.mean()/(tr.R.std()/sqrt(len(tr)))
    p = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
    print(f"  {nom:32s} n {len(tr):>4} | WR {100*(tr.R>0).mean():>5.1f}% | R/op {tr.R.mean():>+7.4f} "
          f"| R tot {tr.R.sum():>+7.1f} | PF {pf:>5.3f} | DD {100*dd:>4.1f}% | p {p:.3f}")

print("=== REGLAS DE GESTION SOBRE LOS MISMOS SETUPS ===")
resume(gestiona(sig,"fijo"),                          "fijo 3R (referencia)")
resume(gestiona(sig,"be", be_en=1.0),                 "break-even en +1R")
resume(gestiona(sig,"be", be_en=1.5),                 "break-even en +1.5R")
resume(gestiona(sig,"parcial", parcial_en=1.0),       "parcial 50% en +1R")
resume(gestiona(sig,"parcial_be", parcial_en=1.0),    "parcial 50% en +1R y BE")
resume(gestiona(sig,"parcial_be", parcial_en=1.5),    "parcial 50% en +1.5R y BE")
resume(gestiona(sig,"trail", trail_r=1.0),            "trailing de 1R tras +1R")
resume(gestiona(sig,"trail", trail_r=1.5),            "trailing de 1.5R tras +1.5R")
resume(gestiona(sig,"parcial_trail", parcial_en=1.0), "parcial 50% +1R y trailing 1R")
for r in (2.0, 4.0, 5.0, 6.0):
    resume(gestiona(sig,"fijo", tp_r=r),              f"fijo {r}R")

print("\n=== ¿HASTA DONDE LLEGAN LAS OPERACIONES? (excursion favorable maxima) ===")
tr = gestiona(sig,"fijo", tp_r=99)     # sin objetivo: deja correr
for q in (0.25,0.5,0.75,0.9):
    print(f"  percentil {int(q*100):>2}: MFE {tr.mfe.quantile(q):>5.2f} R")
print(f"  fraccion que alcanza +1R: {100*(tr.mfe>=1).mean():.1f}%")
print(f"  fraccion que alcanza +2R: {100*(tr.mfe>=2).mean():.1f}%")
print(f"  fraccion que alcanza +3R: {100*(tr.mfe>=3).mean():.1f}%")
print(f"  fraccion que alcanza +5R: {100*(tr.mfe>=5).mean():.1f}%")
