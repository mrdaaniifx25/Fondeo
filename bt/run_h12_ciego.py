"""La pasada ciega de docs/PREREGISTRO_h12_ciego.md. Se ejecuta UNA vez.

Mismo codigo que produjo RESULTADOS_crt_temporalidad.md, sin tocar: CRT desnudo,
liquidez simple, objetivo en el extremo opuesto, ancla_ny = 1.
"""
import sys; sys.path.insert(0,"bt")
import os
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

# costes declarados en la enmienda del pre-registro, antes de tener los datos
INS = [("XAUUSD","data/xauusd_m1.parquet", 0.01, 35.0, "u"),
       ("GRXEUR","data/grxeur_m1.parquet", 1.0,   2.0, "p")]
TFS = [("H1",1),("H2",2),("H4",4),("H8",8),("H12",12),("D1",24)]
DESDE, HASTA = "2023-01-01", "2026-01-01"
PRINCIPAL = "H12"
rng = np.random.default_rng(20260827)

falta = [r for _,r,_,_,_ in INS if not os.path.exists(r)]
if falta:
    print("Faltan los parquet:", ", ".join(falta))
    print("Ejecuta antes:  python3 bt/load_nuevos.py")
    sys.exit(1)

def ee_bloq(x, largo=20, reps=4000):
    n = len(x)
    if n < largo*3: return x.std(ddof=1)/np.sqrt(n)
    nb = int(np.ceil(n/largo))
    ini = rng.integers(0, n-largo+1, size=(reps, nb))
    idx = (ini[:,:,None]+np.arange(largo)[None,None,:]).reshape(reps,-1)[:,:n]
    return float(x[idx].mean(axis=1).std(ddof=1))

def cero(T):
    inv = (1/T.riesgo_u).mean()
    return T.R.mean()/inv if inv > 0 else np.nan

datos = {}
for nom, ruta, u, co, un in INS:
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    datos[nom] = m1.sort_values("ts").reset_index(drop=True)

print("="*118)
print("PASADA CIEGA · docs/PREREGISTRO_h12_ciego.md · una sola vez")
print(f"  {DESDE[:4]}-{int(HASTA[:4])-1} · XAUUSD (coste 0,35 USD) · GRXEUR (coste 2,0 puntos)")
print(f"  celda principal declarada de antemano: {PRINCIPAL}")
print("="*118)

filas = []
for tfn, tfh in TFS:
    tot = []
    for nom, ruta, u, co, un in INS:
        m1 = datos[nom]
        ref = velas_ref(m1, tfh, ancla_ny=1)
        h,l,c = (ref[x].to_numpy() for x in ("high","low","close"))
        a = C.atr(h,l,c,20)
        s = LM.resuelve(LM.secuencias(ref, usar_cuerpo=False), ref, m1, tfh, a)
        s = s[s.k==1].dropna(subset=["nat","rr"]).copy()
        if s.empty: continue
        s["ts"] = ref["fin"].to_numpy()[s.i_ent.to_numpy().astype(int)]
        s = s[(pd.to_datetime(s.ts) >= DESDE) & (pd.to_datetime(s.ts) < HASTA)]
        if s.empty: continue
        s["riesgo_u"] = (s.entrada - s.stop).abs()/u
        s = s[s.riesgo_u > 0]
        s["R"] = np.where(s.nat > 0, s.rr, -1.0)
        s["coste_R"] = co/s.riesgo_u
        s["R_neto"] = s.R - s.coste_R
        tot.append(s.assign(ins=nom, coste=co, uni=un))
    if not tot: continue
    T = pd.concat(tot, ignore_index=True).sort_values("ts")
    filas.append((tfn, T))

print(f"\n{'TF':5s} {'n':>6s} {'acierto':>8s} {'R:R':>7s} {'riesgo':>8s} {'coste %R':>9s} "
      f"{'R BRUTA':>9s} {'R NETA':>9s} {'IC95 neta (bloques)':>22s} {'z':>7s}")
print("-"*118)
res = []
for tfn, T in filas:
    x = T.R_neto.to_numpy(); eb = ee_bloq(x); z = x.mean()/eb
    marca = "  <<< PRINCIPAL" if tfn == PRINCIPAL else ""
    print(f"{tfn:5s} {len(T):>6,} {100*(T.R>0).mean():>7.1f}% {T.rr.median():>7.2f} "
          f"{T.riesgo_u.median():>8.1f} {100*T.coste_R.median():>8.1f}% "
          f"{T.R.mean():>+9.3f} {x.mean():>+9.3f} "
          f"[{x.mean()-1.96*eb:+.3f},{x.mean()+1.96*eb:+.3f}] {z:>+7.2f}{marca}")
    res.append(dict(tf=tfn, n=len(T), bruta=T.R.mean(), neta=x.mean(), ee=eb, z=z,
                    coste=100*T.coste_R.median(), riesgo=T.riesgo_u.median()))

print(f"\n{'TF':5s} {'instrumento':12s} {'n':>6s} {'R bruta':>9s} {'R neta':>9s} "
      f"{'coste cero':>12s} {'pagas':>8s}")
print("-"*118)
for tfn, T in filas:
    for ins, g in T.groupby("ins"):
        c0 = cero(g); co = g.coste.iloc[0]; un = g.uni.iloc[0]
        print(f"{tfn:5s} {ins:12s} {len(g):>6,} {g.R.mean():>+9.3f} {g.R_neto.mean():>+9.3f} "
              f"{c0:>11.2f}{un} {co:>7.1f}{un}" + ("   margen" if c0 > co else ""))

R = pd.DataFrame(res); R.to_csv("data/h12_ciego.csv", index=False)
for tfn, T in filas: T.to_csv(f"data/h12_ciego_{tfn}.csv", index=False)

print("\n" + "="*118)
print("LAS CINCO PREDICCIONES DEL PRE-REGISTRO")
P = R[R.tf == PRINCIPAL]
if P.empty:
    print("  sin operaciones en la celda principal"); sys.exit(0)
p = P.iloc[0]
lo, hi = p.neta - 1.96*p.ee, p.neta + 1.96*p.ee
h1 = R[R.tf=="H1"].iloc[0]
print(f"  1 · bruta de H12 entre +0,05 y +0,15 ......... "
      f"{'SÍ' if 0.05 <= p.bruta <= 0.15 else 'NO'}   ({p.bruta:+.3f})")
print(f"  2 · coste de H12 por debajo del 4 % .......... "
      f"{'SÍ' if p.coste < 4 else 'NO'}   ({p.coste:.1f} %)")
print(f"  3 · neta de H12 positiva ..................... "
      f"{'SÍ' if p.neta > 0 else 'NO'}   ({p.neta:+.3f})")
brutas = R.bruta.to_numpy()
print(f"  4 · bruta plana entre H1 y D1 ................ "
      f"rango {brutas.min():+.3f} a {brutas.max():+.3f}")
print(f"  5 · neta de H1 negativa ...................... "
      f"{'SÍ' if h1.neta < 0 else 'NO'}   ({h1.neta:+.3f})")
print()
print(f"  CRITERIO DECLARADO: el IC95 de la neta de H12 excluye el cero por arriba")
print(f"     IC95 = [{lo:+.3f}, {hi:+.3f}]    z = {p.z:+.2f}    n = {p.n:,}")
if lo > 0:
    print("\n  >> SE CUMPLE. El mecanismo del coste aguanta en instrumentos ciegos.")
elif p.z > 1.5:
    print("\n  >> NO CONCLUYENTE. Positivo pero el intervalo toca el cero; estaba")
    print("     previsto que esto se reportara como no concluyente, no como éxito.")
else:
    print("\n  >> NO SE CUMPLE. Según el pre-registro, el CRT se cierra aquí.")
