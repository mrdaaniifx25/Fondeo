"""Genera la muestra ciega para que el usuario etiquete su criterio.

REGLAS DEL EXPERIMENTO, para que valga algo:
  - muestra ALEATORIA de la poblacion, no elegida. La tasa base es la natural.
  - se dibujan las velas SOLO hasta la de entrada. Ni una vela posterior.
  - el resultado no viaja al fichero de la pagina. Se guarda aparte.
  - los identificadores son opacos y el orden va barajado.
"""
import sys; sys.path.insert(0,"bt")
import json
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,1.2,5),
       ("NAS100","data/nsxusd_m1.parquet",1.0,1.5,1)]
N_POR_INS = 150
VELAS_ATRAS = 16          # contexto visible antes de la vela de entrada
SEMILLA = 20260825

rng = np.random.default_rng(SEMILLA)
casos, verdad = [], []

for nom, ruta, U, CO, dec in INS:
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").reset_index(drop=True)
    ref = velas_ref(m1, 4, ancla_ny=1)
    h,l,o,c = (ref[x].to_numpy() for x in ("high","low","open","close"))
    a4 = C.atr(h,l,c,20)
    seq = LM.secuencias(ref, usar_cuerpo=False)
    seq = LM.resuelve(seq, ref, m1, 4, a4)
    seq = seq[(seq.k == 1)].dropna(subset=["nat","rr"])
    seq = seq[seq.i_base >= VELAS_ATRAS].reset_index(drop=True)

    # contexto diario, siempre de la diaria YA CERRADA
    D = velas_ref(m1, 24, ancla_ny=17)
    dh, dl, dc = D.high.to_numpy(), D.low.to_numpy(), D.close.to_numpy()
    dph, dpl = np.roll(dh,1), np.roll(dl,1)
    dcrt = np.where((dl<dpl)&(dh<=dph)&(dc>=dpl)&(dc<=dph), +1,
            np.where((dh>dph)&(dl>=dpl)&(dc>=dpl)&(dc<=dph), -1, 0))
    tD = D["fin"].to_numpy()

    pick = rng.choice(len(seq), size=min(N_POR_INS, len(seq)), replace=False)
    for z in pick:
        r = seq.iloc[z]
        ie, ib = int(r.i_ent), int(r.i_base)
        j0 = ib - VELAS_ATRAS
        vs = []
        for j in range(j0, ie+1):                       # NUNCA pasa de ie
            vs.append([int(pd.Timestamp(ref["id"].iloc[j]).timestamp()),
                       round(float(o[j]),dec), round(float(h[j]),dec),
                       round(float(l[j]),dec), round(float(c[j]),dec)])
        k = int(np.searchsorted(tD, ref["fin"].to_numpy()[ie], side="left")) - 1
        if k < 1: continue
        casos.append(dict(
            id=f"{nom[:3]}{z:05d}", ins=nom, dec=dec,
            velas=vs, i_base=ib-j0, i_ent=ie-j0,
            largo=bool(r.alcista),
            entrada=round(float(r.entrada),dec), stop=round(float(r.stop),dec),
            objetivo=round(float(r.objetivo),dec),
            rr=round(float(r.rr),2),
            riesgo=round(abs(float(r.entrada)-float(r.stop))/U,1),
            coste_pct=round(100*CO/(abs(float(r.entrada)-float(r.stop))/U),1),
            dia_hi=round(float(dh[k]),dec), dia_lo=round(float(dl[k]),dec),
            dia_crt=int(dcrt[k]),
            hora=pd.Timestamp(ref["id"].iloc[ie]).strftime("%Y-%m-%d %H:%M")))
        verdad.append(dict(id=casos[-1]["id"], gano=int(r.nat), R=float(r.rr if r.nat>0 else -1.0),
                           ts=casos[-1]["hora"], ins=nom))

orden = rng.permutation(len(casos))
casos = [casos[i] for i in orden]
for n, ca in enumerate(casos): ca["n"] = n+1

json.dump(casos, open("data/etiquetas_casos.json","w"), separators=(",",":"))
pd.DataFrame(verdad).to_csv("data/etiquetas_verdad.csv", index=False)

v = pd.DataFrame(verdad)
print(f"casos generados: {len(casos)}")
print(v.groupby("ins").agg(n=("gano","size"), aciertos=("gano","mean"), R=("R","mean")).round(4).to_string())
print(f"\nTASA BASE del conjunto: {100*v.gano.mean():.1f} % de acierto, R media {v.R.mean():+.3f}")
print(f"desviación típica de R: {v.R.std():.3f}  ->  con 150 vs 150 el error típico "
      f"de la diferencia es {v.R.std()*np.sqrt(2/150):.3f} R")
print(f"tamaño del fichero de la página: {len(open('data/etiquetas_casos.json').read())/1024:.0f} KB")
