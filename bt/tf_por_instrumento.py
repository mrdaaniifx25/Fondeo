"""El estudio canonico de temporalidad, pero desglosado por instrumento."""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,1.2),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.5),
       ("USDJPY","data/usdjpy_m1.parquet",0.01, 1.3),
       ("NAS100","data/nsxusd_m1.parquet",1.0,  1.5),
       ("SPX500","data/spxusd_m1.parquet",1.0,  0.6)]
TFS = [("H4",4),("H6",6),("H8",8),("H12",12),("D1",24)]
ANOS = 6.6

filas=[]
for tfn, tfh in TFS:
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
        seq = seq[seq.riesgo_u > 0]
        R  = np.where(seq.nat>0, seq.rr, -1.0)
        cR = co/seq.riesgo_u.to_numpy()
        net = R - cR
        ee = R.std(ddof=1)/np.sqrt(len(R))
        een = net.std(ddof=1)/np.sqrt(len(net))
        filas.append(dict(tf=tfn, ins=nom, n=len(R), ano=len(R)/ANOS,
            acierto=100*(R>0).mean(), riesgo=seq.riesgo_u.median(),
            costeR=100*np.median(cR), bruta=R.mean(), ee=ee,
            neta=net.mean(), z=net.mean()/een))
D = pd.DataFrame(filas)
D.to_csv("data/tf_por_instrumento.csv", index=False)

for tfn,_ in TFS:
    S = D[D.tf==tfn]
    print(f"\n--- {tfn} " + "-"*74)
    print(f"{'instrumento':<11} {'n':>6} {'ops/ano':>8} {'acierto':>8} {'riesgo':>8} "
          f"{'coste%R':>8} {'BRUTA':>8} {'+-':>6} {'NETA':>8} {'z':>6}")
    for r in S.itertuples():
        print(f"{r.ins:<11} {r.n:>6} {r.ano:>8.0f} {r.acierto:>7.1f}% {r.riesgo:>8.1f} "
              f"{r.costeR:>7.1f}% {r.bruta:>+8.3f} {1.96*r.ee:>6.3f} {r.neta:>+8.3f} {r.z:>+6.2f}")
    x = S.bruta.to_numpy()
    print(f"{'--> media':<11} {S.n.sum():>6} {S.ano.sum():>8.0f} {'':>8} {'':>8} {'':>8} "
          f"{np.average(x, weights=S.n):>+8.3f} {'':>6} "
          f"{np.average(S.neta, weights=S.n):>+8.3f}   {(S.neta>0).sum()}/5 positivos")
