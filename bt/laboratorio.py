"""Laboratorio con reserva ciega.

TRAIN  2020-01-01 .. 2023-12-31   -> aqui se busca
TEST   2024-01-01 .. 2026-07-31   -> un solo disparo al final

Familias simples, pocos parametros cada una. Todas comparten el mismo motor de
resolucion sobre velas M1 y el mismo coste de 1,2 pips.
"""
import numpy as np, pandas as pd
from math import sqrt, erf

PIP = 0.0001
COSTE = 1.2
TRAIN = ("2020-01-01", "2023-12-31")
TEST  = ("2024-01-01", "2026-07-31")

def pz(x):
    n=len(x)
    if n < 2: return 0.0, 1.0
    se=x.std(ddof=1)/sqrt(n); z=x.mean()/se if se>0 else 0.0
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

class Motor:
    def __init__(self, m1):
        self.t = m1["ts"].to_numpy()
        self.H = m1["high"].to_numpy(); self.L = m1["low"].to_numpy()
        self.C = m1["close"].to_numpy()
    def resolver(self, sig, horas=72):
        """sig: DataFrame con ts (cierre de la vela de senal), largo, entrada, sl, rr"""
        out, libre = [], np.datetime64("1970-01-01")
        for r in sig.itertuples():
            ets = np.datetime64(pd.Timestamp(r.ts))
            if ets < libre: continue
            riesgo = abs(r.entrada - r.sl)
            if riesgo <= 0: continue
            tp = r.entrada + r.rr*riesgo if r.largo else r.entrada - r.rr*riesgo
            i0 = int(np.searchsorted(self.t, ets)); i1 = min(i0+horas*60, len(self.t))
            if i0 >= len(self.t) or i1 <= i0: continue
            a, b = self.H[i0:i1], self.L[i0:i1]
            gsl, gtp = ((b<=r.sl, a>=tp) if r.largo else (a>=r.sl, b<=tp))
            isl = int(np.argmax(gsl)) if gsl.any() else 10**9
            itp = int(np.argmax(gtp)) if gtp.any() else 10**9
            if isl==10**9 and itp==10**9: sal, ifin = self.C[i1-1], (i1-i0)-1
            elif isl <= itp: sal, ifin = r.sl, isl
            else: sal, ifin = tp, itp
            br = (sal-r.entrada) if r.largo else (r.entrada-sal)
            neto = br/PIP - COSTE
            out.append(dict(ts=pd.Timestamp(ets), largo=r.largo, riesgo_pips=riesgo/PIP,
                            R=neto/(riesgo/PIP), bruto=(br/PIP)/(riesgo/PIP)))
            libre = self.t[i0+ifin]
        return pd.DataFrame(out)

def resumen(tr, etiqueta=""):
    if tr.empty or len(tr) < 10: return None
    z, p = pz(tr.bruto)
    gan, per = tr[tr.R>0], tr[tr.R<=0]
    pf = gan.R.sum()/(-per.R.sum()) if per.R.sum() < 0 else float("inf")
    eq, pico, dd = 10000.0, 10000.0, 0.0
    for R in tr.R:
        eq *= (1+0.01*R); pico = max(pico, eq); dd = max(dd, (pico-eq)/pico)
    h = len(tr)//2
    return dict(etiqueta=etiqueta, n=len(tr), wr=100*float((tr.R>0).mean()),
                bruto=float(tr.bruto.mean()), z=float(z), p=float(p),
                Rneto=float(tr.R.sum()), pf=float(pf), dd=100*dd, eq=eq,
                h1=float(tr.bruto.iloc[:h].mean()), h2=float(tr.bruto.iloc[h:].mean()),
                riesgo=float(tr.riesgo_pips.mean()))

def barras(m1, regla, origin=None):
    r = m1.set_index("ts").resample(regla, label="left", closed="left",
                                    **({"origin": origin} if origin else {}))
    return r.agg(open=("open","first"), high=("high","max"),
                 low=("low","min"), close=("close","last")).dropna().reset_index()
