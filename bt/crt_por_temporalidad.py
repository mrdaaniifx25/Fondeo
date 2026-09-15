"""El CRT desnudo en cada temporalidad, y donde la aritmetica del coste duele menos.

Es la cuenta que decide una estrategia "master": el patron tiene ventaja bruta
medida (+0,085 R en H4) pero el coste se lleva el 7 % del riesgo. Si el mismo
patron aguanta en temporalidades mayores, el stop es mas ancho, el coste pesa
menos, y la misma ventaja bruta podria cruzar.
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
TFS = [("H1",1),("H2",2),("H4",4),("H6",6),("H8",8),("H12",12),("D1",24)]

print("="*116)
print("EL CRT DESNUDO POR TEMPORALIDAD · liquidez simple · 2020-2026 · cinco instrumentos")
print("  la pregunta: ¿donde deja de comerse el coste la ventaja?")
print("="*116)
print(f"{'TF':5s} {'n':>7s} {'al año':>7s} {'acierto':>8s} {'R:R med':>8s} "
      f"{'riesgo med':>11s} {'coste %R':>9s} {'R BRUTA':>9s} {'IC95':>18s} {'R NETA':>9s}")
print("-"*116)

filas=[]
for tfn, tfh in TFS:
    tot=[]
    for nom, ruta, u, co in INS:
        m1 = pd.read_parquet(ruta); m1["ts"]=pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").reset_index(drop=True)
        ref = velas_ref(m1, tfh, ancla_ny=1)
        h,l,c = (ref[x].to_numpy() for x in ("high","low","close"))
        a = C.atr(h,l,c,20)
        seq = LM.secuencias(ref, usar_cuerpo=False)
        if seq.empty: continue
        seq = LM.resuelve(seq, ref, m1, tfh, a)
        seq = seq[seq.k==1].dropna(subset=["nat","rr"]).copy()
        if seq.empty: continue
        seq["riesgo_u"] = (seq.entrada-seq.stop).abs()/u
        seq["R"] = np.where(seq.nat>0, seq.rr, -1.0)
        seq["coste_R"] = co/seq.riesgo_u
        seq["R_neto"] = seq.R - seq.coste_R
        tot.append(seq.assign(ins=nom))
    if not tot: continue
    T = pd.concat(tot, ignore_index=True)
    T = T[T.riesgo_u > 0]
    x = T.R.to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x))
    anos = 6.6
    print(f"{tfn:5s} {len(T):>7,} {len(T)/anos:>7.0f} {100*(T.R>0).mean():>7.1f}% "
          f"{T.rr.median():>8.2f} {T.riesgo_u.median():>11.1f} "
          f"{100*T.coste_R.median():>8.1f}% {x.mean():>+9.3f} "
          f"[{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}] {T.R_neto.mean():>+9.3f}")
    filas.append(dict(tf=tfn, n=len(T), bruta=x.mean(), lo=x.mean()-1.96*ee,
                      neta=T.R_neto.mean(), coste=100*T.coste_R.median(),
                      riesgo=T.riesgo_u.median()))

R = pd.DataFrame(filas)
R.to_csv("data/crt_por_tf.csv", index=False)
print("\n" + "="*116)
print("LECTURA")
print(f"  ventaja bruta: ¿sube, baja o se mantiene al subir de temporalidad?")
print("  " + "  ".join(f"{r.tf} {r.bruta:+.3f}" for r in R.itertuples()))
print(f"\n  coste como % del riesgo:")
print("  " + "  ".join(f"{r.tf} {r.coste:.1f}%" for r in R.itertuples()))
pos = R[R.neta > 0]
print(f"\n  temporalidades con NETA positiva: {len(pos)} de {len(R)}"
      + (f"  ->  {', '.join(pos.tf)}" if len(pos) else ""))
