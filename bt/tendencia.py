"""T1/T2 del pre-registro: seguimiento de tendencia con parametros Turtle canonicos.

Complemento mecanico exacto de todo lo refutado: operar A FAVOR de la rotura.
"""
import numpy as np, pandas as pd
from math import sqrt, erf

ATR_N   = 20
ATR_K   = 2.0
MAX_DIAS= 120
MIN_M1  = 60          # higiene: un dia con menos velas M1 no se considera dia de mercado

INSTR = {  # nombre: (fichero, unidad, coste ida y vuelta)
  "EURUSD": ("data/eurusd_m1.parquet", 0.0001, 1.2),
  "GBPUSD": ("data/gbpusd_m1.parquet", 0.0001, 1.5),
  "USDJPY": ("data/usdjpy_m1.parquet", 0.01,   1.2),
  "NAS100": ("data/nsxusd_m1.parquet", 1.0,    1.5),
  "SP500":  ("data/spxusd_m1.parquet", 1.0,    0.6),
}
FX  = ["EURUSD","GBPUSD","USDJPY"]
IDX = ["NAS100","SP500"]

def dias(m1):
    """Velas diarias con cierre a las 17:00 de Nueva York, el cierre real del mercado."""
    ts = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert("America/New_York")
    d = m1.copy(); d["k"] = pd.Index((ts + pd.Timedelta(hours=7)).date)
    g = d.groupby("k").agg(open=("open","first"), high=("high","max"),
                           low=("low","min"), close=("close","last"),
                           ini=("ts","min"), fin=("ts","max"), n=("ts","size"))
    g = g[g.n >= MIN_M1].reset_index(drop=True)
    pc = g.close.shift(1)
    tr = pd.concat([g.high-g.low, (g.high-pc).abs(), (g.low-pc).abs()], axis=1).max(axis=1)
    g["atr"] = tr.rolling(ATR_N).mean()
    return g

def marca(g, N):
    g = g.copy()
    g["dhi"] = g.high.rolling(N).max().shift(1)
    g["dlo"] = g.low.rolling(N).min().shift(1)
    g["tlo"] = g.low.rolling(max(N//2,1)).min().shift(1)    # trailing de un largo
    g["thi"] = g.high.rolling(max(N//2,1)).max().shift(1)   # trailing de un corto
    return g

def _m1_ordena(m1, ini, fin, largo, sl, tp):
    """Cual de los dos niveles se toca primero dentro de un dia concreto."""
    s = m1[(m1.ts>=ini)&(m1.ts<=fin)]
    H,L = s.high.to_numpy(), s.low.to_numpy()
    gsl,gtp = ((L<=sl, H>=tp) if largo else (H>=sl, L<=tp))
    isl = int(np.argmax(gsl)) if gsl.any() else 10**9
    itp = int(np.argmax(gtp)) if gtp.any() else 10**9
    return "SL" if isl<=itp else "TP"

def opera(g, m1, N, salida, unit, coste, invertir=False, dias_azar=None, semilla=0):
    """salida: 'turtle' (Donchian opuesto de N/2) o '3R' (objetivo fijo)."""
    g = marca(g, N)
    op,hi,lo,cl = (g[c].to_numpy() for c in ("open","high","low","close"))
    dhi,dlo,tlo,thi,atr = (g[c].to_numpy() for c in ("dhi","dlo","tlo","thi","atr"))
    ini,fin = g.ini.to_numpy(), g.fin.to_numpy()
    n = len(g)

    if dias_azar is None:
        senal = np.full(n, 0, dtype=int)
        senal[(~np.isnan(dhi)) & (cl > dhi)] =  1
        senal[(~np.isnan(dlo)) & (cl < dlo)] = -1
    else:                                   # control de entrada aleatoria
        rng = np.random.default_rng(semilla)
        senal = np.zeros(n, dtype=int)
        val = np.where(~np.isnan(atr))[0]
        val = val[(val>N) & (val<n-MAX_DIAS-2)]
        pick = rng.choice(val, size=min(dias_azar, len(val)), replace=False)
        senal[pick] = rng.choice([-1,1], size=len(pick))

    out, libre = [], -1
    for i in range(n-1):
        if senal[i]==0 or i<=libre or np.isnan(atr[i]): continue
        largo = senal[i]>0
        if invertir: largo = not largo
        e   = op[i+1]
        sl0 = e - ATR_K*atr[i] if largo else e + ATR_K*atr[i]
        # el 1R es la distancia al stop REALMENTE vigente el primer dia. Con salida
        # turtle el Donchian opuesto puede estar mas cerca que el 2xATR; normalizar
        # siempre por 2xATR inflaria la R al medir perdidas menores que 1R contra un
        # denominador mayor. Lo detecto el control de entrada aleatoria.
        s_ini = sl0
        if salida=="turtle":
            t0 = tlo[i+1] if largo else thi[i+1]
            if not np.isnan(t0): s_ini = max(sl0,t0) if largo else min(sl0,t0)
        riesgo = abs(e-s_ini)
        if riesgo<=0: continue
        tp = e + 3*riesgo if largo else e - 3*riesgo
        sal=mot=None; jfin=min(i+1+MAX_DIAS, n)
        for j in range(i+1, jfin):
            s = sl0
            if salida=="turtle":
                t = tlo[j] if largo else thi[j]
                if not np.isnan(t): s = max(sl0,t) if largo else min(sl0,t)
            toca_sl = (lo[j]<=s) if largo else (hi[j]>=s)
            toca_tp = ((hi[j]>=tp) if largo else (lo[j]<=tp)) if salida=="3R" else False
            if toca_sl and toca_tp:
                mot = _m1_ordena(m1, ini[j], fin[j], largo, s, tp)
                sal = (min(op[j],s) if largo else max(op[j],s)) if mot=="SL" else tp
            elif toca_sl:
                mot="SL"; sal = min(op[j],s) if largo else max(op[j],s)
            elif toca_tp:
                mot="TP"; sal = tp
            if mot: libre=j; break
        if mot is None:
            j=jfin-1; sal,mot,libre = cl[j],"tiempo",j
        br = (sal-e) if largo else (e-sal)
        out.append(dict(dia=g.ini.iloc[i+1], largo=largo, riesgo_u=riesgo/unit,
                        motivo=mot, dias=libre-i,
                        bruto=br/riesgo, R=(br/unit-coste)/(riesgo/unit)))
    return pd.DataFrame(out)

def pz(x):
    n=len(x)
    if n<3: return 0.0,1.0
    se=x.std(ddof=1)/sqrt(n)
    z=x.mean()/se if se>0 else 0.0
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

def pf(R):
    g,p = R[R>0].sum(), -R[R<=0].sum()
    return g/p if p>0 else float("inf")

def linea(nom, tr):
    if tr is None or len(tr)<3:
        print(f"{nom:34s}      (muestra insuficiente)"); return None
    z,p = pz(tr.bruto); h=len(tr)//2
    print(f"{nom:34s} {len(tr):>5d} {tr.bruto.mean():>+9.4f} {z:>+6.2f} {p:>7.4f} "
          f"{(tr.motivo=='TP').mean()*100 if 'TP' in set(tr.motivo) else np.nan:>6.1f} "
          f"{tr.dias.mean():>6.1f} {pf(tr.R):>6.3f} {tr.R.sum():>+8.1f}")
    return dict(n=len(tr), bruto=float(tr.bruto.mean()), z=float(z), p=float(p),
                pf=float(pf(tr.R)), Rneto=float(tr.R.sum()),
                h1=float(tr.bruto.iloc[:h].mean()), h2=float(tr.bruto.iloc[h:].mean()))

CAB = f"{'':34s} {'n':>5s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'%TP':>6s} {'dias':>6s} {'PF':>6s} {'R neto':>8s}"
