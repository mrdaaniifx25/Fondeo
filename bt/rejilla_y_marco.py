"""Misma maquinaria canonica, dos rejillas: la del estudio (ancla NY) y la SUYA
(01/05/09/13/17/21 UTC, la de OANDA en TradingView)."""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,1.43),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.60),
       ("USDJPY","data/usdjpy_m1.parquet",0.01, 1.50)]

def ref_utc(m1, tfh):
    """Rejilla fija en UTC desplazada 1 h: 01,05,09,... para tf=4."""
    d = m1.copy()
    d["id"] = (pd.DatetimeIndex(d["ts"]) - pd.Timedelta(hours=1)).floor(f"{tfh}h") \
              + pd.Timedelta(hours=1)
    g = d.groupby("id").agg(open=("open","first"), high=("high","max"),
                            low=("low","min"), close=("close","last"),
                            ini=("ts","min"), fin=("ts","max"), n=("ts","size")).reset_index()
    return g[g.n >= tfh*60*0.5].reset_index(drop=True)

def mide(ref, m1, tfh, u, co):
    h,l,c = (ref[x].to_numpy() for x in ("high","low","close"))
    a = C.atr(h,l,c,20)
    s = LM.resuelve(LM.secuencias(ref, usar_cuerpo=False), ref, m1, tfh, a)
    s = s[s.k==1].dropna(subset=["nat","rr"]).copy()
    s["riesgo_u"] = (s.entrada-s.stop).abs()/u
    s = s[s.riesgo_u > 0]
    R = np.where(s.nat>0, s.rr, -1.0); cR = co/s.riesgo_u.to_numpy()
    net = R - cR
    return dict(n=len(R), acierto=100*(R>0).mean(), riesgo=s.riesgo_u.median(),
                costeR=100*np.median(cR), bruta=R.mean(),
                ee=R.std(ddof=1)/np.sqrt(len(R)), neta=net.mean(),
                zn=net.mean()/(net.std(ddof=1)/np.sqrt(len(net))))

for tfn, tfh in (("H4",4),("H8",8),("H12",12),("D1",24)):
    print(f"\n=== {tfn} " + "="*88)
    print(f"{'instrumento':<10} {'rejilla':<14} {'n':>6} {'acierto':>8} {'riesgo':>8} "
          f"{'coste%R':>8} {'BRUTA':>8} {'+-':>6} {'NETA':>8} {'z':>6}")
    for nom, ruta, u, co in INS:
        m1 = pd.read_parquet(ruta); m1["ts"]=pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").reset_index(drop=True)
        for eti, ref in (("estudio · NY", velas_ref(m1, tfh, ancla_ny=1)),
                         ("SUYA · UTC",   ref_utc(m1, tfh))):
            r = mide(ref, m1, tfh, u, co)
            print(f"{nom:<10} {eti:<14} {r['n']:>6} {r['acierto']:>7.1f}% "
                  f"{r['riesgo']:>8.1f} {r['costeR']:>7.1f}% {r['bruta']:>+8.3f} "
                  f"{1.96*r['ee']:>6.3f} {r['neta']:>+8.3f} {r['zn']:>+6.2f}")
