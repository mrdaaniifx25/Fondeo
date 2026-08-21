import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd, json
from tendencia import *

D, M = {}, {}
print("cargando y construyendo velas diarias...")
for k,(f,u,c) in INSTR.items():
    m1 = pd.read_parquet(f); m1["ts"]=pd.to_datetime(m1["ts"])
    M[k]=m1; D[k]=dias(m1)
    print(f"  {k:7s} {len(m1):>9,} velas M1 -> {len(D[k]):>4} dias  "
          f"({D[k].ini.min().date()} -> {D[k].ini.max().date()})")

todo={}
def corre(N, salida, **kw):
    r={}
    for k in INSTR:
        u,c = INSTR[k][1], INSTR[k][2]
        r[k]=opera(D[k],M[k],N,salida,u,c,**kw)
    return r

print("\n" + "="*104)
print("LAS OCHO CELDAS   (T1 y T2 son N=55 + turtle, agregados por clase)")
print("="*104); print(CAB)
res={}
for N in (55,20):
    for salida in ("turtle","3R"):
        r = corre(N,salida); todo[(N,salida)]=r
        fx  = pd.concat([r[k] for k in FX],  ignore_index=True).sort_values("dia")
        idx = pd.concat([r[k] for k in IDX], ignore_index=True).sort_values("dia")
        et = "  <<< PRIMARIO" if (N==55 and salida=="turtle") else ""
        print(f"-- N={N} salida={salida}")
        res[f"FX_{N}_{salida}"]  = linea(f"   divisas (3 pares){et}", fx)
        res[f"IDX_{N}_{salida}"] = linea(f"   indices (2){et}",       idx)
        for k in INSTR: linea(f"      {k}", r[k])

print("\n" + "="*104)
print("CONTROLES")
print("="*104); print(CAB)

# -- espejo. Con stop dinamico (turtle) el espejo es DEGENERADO: al invertir un
#    breakout el Donchian opuesto queda pegado a la entrada, el 1R tiende a cero y
#    la R estalla. Se reporta, se marca como no informativo, y el control valido
#    es el del brazo 3R, donde el stop es fijo y el espejo si esta bien planteado.
for salida in ("turtle","3R"):
    esp = corre(55, salida, invertir=True)
    for nom,cls in (("divisas",FX),("indices",IDX)):
        e = pd.concat([esp[k] for k in cls], ignore_index=True)
        et = "  (DEGENERADO, no informativo)" if salida=="turtle" else "  (valido)"
        res[f"espejo_{salida}_{nom}"] = linea(f"   ESPEJO {salida} {nom}{et}", e)

# -- entrada aleatoria. 20 repeticiones NO son independientes entre si: solapan
#    en el mismo periodo y el mismo instrumento. Agrupar las 1195 operaciones y
#    sacar un z de ahi infla el estadistico. Se resume por repeticion.
print("\n" + "="*104)
print("CONTROL 2 bien planteado: media por repeticion, no operaciones agrupadas")
print("="*104)
NREP=20
azm={"divisas":[], "indices":[]}
for s_ in range(NREP):
    az = {k: opera(D[k],M[k],55,"turtle",INSTR[k][1],INSTR[k][2],
                   dias_azar=len(todo[(55,"turtle")][k]), semilla=s_) for k in INSTR}
    for nom,cls in (("divisas",FX),("indices",IDX)):
        a = pd.concat([az[k] for k in cls], ignore_index=True)
        azm[nom].append(a.bruto.mean())
for nom,real in (("divisas", res["FX_55_turtle"]["bruto"]),
                 ("indices", res["IDX_55_turtle"]["bruto"])):
    v = np.array(azm[nom]); pct = (v < real).mean()*100
    print(f"  {nom:8s} azar {v.mean():+.4f} +- {v.std(ddof=1):.4f}  "
          f"(rango {v.min():+.4f} a {v.max():+.4f})")
    print(f"           estrategia {real:+.4f}  ->  percentil {pct:.0f} de la distribucion "
          f"al azar  ->  {'SUPERA' if pct>=95 else 'NO supera'}")
    res[f"azar_{nom}"]=dict(media=float(v.mean()), sd=float(v.std(ddof=1)),
                            real=float(real), percentil=float(pct))

print("\n" + "="*104)
print("CONTROL 3: comprar y mantener  (solo indices, riesgo 1% por operacion, compuesto)")
print("="*104)
for k in IDX:
    tr = todo[(55,"turtle")][k]
    eq = float(np.prod(1+0.01*tr.R.to_numpy()))
    byh = D[k].close.iloc[-1]/D[k].close.iloc[0]
    print(f"  {k:7s} estrategia x{eq:.3f} ({(eq-1)*100:+.1f}%)   |   "
          f"comprar y mantener x{byh:.3f} ({(byh-1)*100:+.1f}%)   |   "
          f"{'SUPERA' if eq>byh else 'NO supera'}")
    res[f"byh_{k}"]=dict(estrategia=eq, comprar=float(byh))

json.dump(res, open("data/informe_tendencia.json","w"), indent=1)
pd.concat([todo[(55,"turtle")][k].assign(instr=k) for k in INSTR],
          ignore_index=True).to_csv("data/trades_tendencia.csv", index=False)
