"""El hallazgo por temporalidad, partido en dos mitades de tiempo.

AVISO SOBRE LO QUE ESTO ES Y NO ES. El estudio original (RESULTADOS_crt_
temporalidad.md) corrio sobre 2020-2026 ENTERO, asi que quemo el conjunto que
BC_00 §a reservaba. Esto NO es una confirmacion limpia: el hallazgo ya vio estos
datos. Es una comprobacion de estabilidad -si el neto positivo de H12 y D1 vive
en las dos mitades o sale de una sola-, y como tal se reporta.

Un hallazgo que solo aparece en una mitad es ruido con buena presentacion.
"""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,1.2),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.5),
       ("USDJPY","data/usdjpy_m1.parquet",0.01, 1.3),
       ("NAS100","data/nsxusd_m1.parquet",1.0,  1.5),
       ("SPX500","data/spxusd_m1.parquet",1.0,  0.6)]
TFS   = [("H1",1),("H2",2),("H4",4),("H8",8),("H12",12),("D1",24)]
CORTE = pd.Timestamp("2024-01-01")

cache = {}
def carga(ruta):
    if ruta not in cache:
        m1 = pd.read_parquet(ruta); m1["ts"]=pd.to_datetime(m1["ts"])
        cache[ruta] = m1.sort_values("ts").reset_index(drop=True)
    return cache[ruta]

def mide(T):
    x = T.R.to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x))
    return dict(n=len(T), bruta=x.mean(), ee=ee, neta=T.R_neto.mean(),
                coste=100*T.coste_R.median(), riesgo=T.riesgo_u.median(),
                ac=100*(T.R>0).mean())

print("="*122)
print("EL CRT POR TEMPORALIDAD, PARTIDO EN DOS MITADES")
print("  2020-2023 (4 años, desarrollo)   vs   2024-2026 (2,6 años)")
print("  NO es confirmación: el hallazgo original ya vio las dos. Es estabilidad.")
print("="*122)
print(f"{'TF':5s} │ {'n':>6s} {'coste':>6s} {'BRUTA':>8s} {'NETA':>8s} │ "
      f"{'n':>6s} {'coste':>6s} {'BRUTA':>8s} {'NETA':>8s} │ {'dif bruta':>10s} {'z dif':>7s}")
print(f"{'':5s} │ {'──── 2020-2023 ────':^32s} │ {'──── 2024-2026 ────':^32s} │")
print("-"*122)

filas=[]
for tfn, tfh in TFS:
    tot=[]
    for nom, ruta, u, co in INS:
        m1 = carga(ruta)
        ref = velas_ref(m1, tfh, ancla_ny=1)
        h,l,c = (ref[x].to_numpy() for x in ("high","low","close"))
        a = C.atr(h,l,c,20)
        seq = LM.secuencias(ref, usar_cuerpo=False)
        if seq.empty: continue
        seq = LM.resuelve(seq, ref, m1, tfh, a)
        seq = seq[seq.k==1].dropna(subset=["nat","rr"]).copy()
        if seq.empty: continue
        # secuencias() solo devuelve indices; la fecha hay que traerla de ref
        seq["ts"] = ref["fin"].to_numpy()[seq.i_ent.to_numpy().astype(int)]
        seq["riesgo_u"] = (seq.entrada-seq.stop).abs()/u
        seq["R"] = np.where(seq.nat>0, seq.rr, -1.0)
        seq["coste_R"] = co/seq.riesgo_u
        seq["R_neto"] = seq.R - seq.coste_R
        tot.append(seq.assign(ins=nom))
    if not tot: continue
    T = pd.concat(tot, ignore_index=True)
    T = T[T.riesgo_u > 0]
    fecha = pd.to_datetime(T["ts"])
    assert fecha.notna().all() and fecha.max() > CORTE, "el corte temporal no separa nada"
    A, B = mide(T[fecha < CORTE]), mide(T[fecha >= CORTE])
    dif = B["bruta"] - A["bruta"]
    z   = dif / np.sqrt(A["ee"]**2 + B["ee"]**2)
    print(f"{tfn:5s} │ {A['n']:>6,} {A['coste']:>5.1f}% {A['bruta']:>+8.3f} {A['neta']:>+8.3f} │ "
          f"{B['n']:>6,} {B['coste']:>5.1f}% {B['bruta']:>+8.3f} {B['neta']:>+8.3f} │ "
          f"{dif:>+10.3f} {z:>+7.2f}")
    filas.append(dict(tf=tfn, nA=A["n"], brutaA=A["bruta"], netaA=A["neta"],
                      nB=B["n"], brutaB=B["bruta"], netaB=B["neta"], dif=dif, z=z))

R = pd.DataFrame(filas)
R.to_csv("data/crt_tf_partido.csv", index=False)
print("\n" + "="*122)
print("LECTURA")
p1 = R[R.netaA > 0].tf.tolist(); p2 = R[R.netaB > 0].tf.tolist()
print(f"  neta positiva en 2020-2023 : {', '.join(p1) if p1 else 'ninguna'}")
print(f"  neta positiva en 2024-2026 : {', '.join(p2) if p2 else 'ninguna'}")
amb = [t for t in p1 if t in p2]
print(f"  positiva en LAS DOS        : {', '.join(amb) if amb else 'NINGUNA'}")
print()
if amb:
    print(f"  {len(amb)} temporalidad(es) aguantan el corte. Es lo mínimo exigible para")
    print("  seguir mirando ahí, y sigue sin ser una confirmación limpia.")
else:
    print("  Ninguna temporalidad tiene el neto positivo en las dos mitades.")
    print("  El hallazgo de RESULTADOS_crt_temporalidad no sobrevive al corte temporal:")
    print("  el neto positivo de H12 y D1 salía de una sola mitad de los datos.")
