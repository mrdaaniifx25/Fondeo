"""EMA50 + RSI14 · tendencia en H4, ejecucion en M15, solape Londres-Nueva York.

Reglas implementadas literalmente:
  1 H4: cierre por encima de la EMA50 = alcista, por debajo = bajista.
        Filtro de rango: si el precio cruza la EMA mas de MAX_CRUCES veces en las
        ultimas VENT_CRUCES velas H4, no se opera.
  2 M15: retroceso que TOCA la EMA50 (minimo <= EMA en largos) y RSI14 que toca
        30 (o 70 en cortos) dentro de las VENT_RSI velas previas.
  3 M15: gatillo = vela envolvente o martillo/estrella en la direccion.
        Entrada en la apertura de la vela siguiente.
  4 Horario: 08:00-17:00 hora de Europa central, con cambio de hora real.
No especificados por el usuario, declarados por mi y probados en sensibilidad:
  stop bajo el minimo del retroceso, objetivo en multiplo fijo de R.
"""
import numpy as np, pandas as pd
from math import sqrt, erf

VENT_CRUCES, MAX_CRUCES = 12, 2
VENT_RSI   = 10
SL_BUF     = 0.10      # fraccion del rango del retroceso anadida al stop
MAX_HORAS  = 48

def ema(s, n): return s.ewm(span=n, adjust=False).mean()

def rsi(s, n=14):
    d = s.diff()
    up = d.clip(lower=0); dn = -d.clip(upper=0)
    au = up.ewm(alpha=1/n, adjust=False).mean()
    ad = dn.ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100/(1 + au/ad.replace(0, np.nan))

def marcos(m1):
    m15 = m1.set_index("ts").resample("15min", label="left", closed="left").agg(
        open=("open","first"), high=("high","max"), low=("low","min"),
        close=("close","last")).dropna().reset_index()
    h4 = m1.set_index("ts").resample("4h", label="left", closed="left").agg(
        close=("close","last")).dropna().reset_index()
    h4["ema"] = ema(h4.close, 50)
    h4["arriba"] = h4.close > h4.ema
    cr = (h4.arriba != h4.arriba.shift(1)).astype(int)
    h4["cruces"] = cr.rolling(VENT_CRUCES).sum()
    # se usa la H4 YA CERRADA: desplazamiento de una vela
    h4["t_arriba"] = h4.arriba.shift(1); h4["t_cruces"] = h4.cruces.shift(1)
    h4["t_ema"] = h4.ema.shift(1)
    m15["h4_id"] = m15.ts.dt.floor("4h")
    m15 = m15.merge(h4[["ts","t_arriba","t_cruces"]].rename(columns={"ts":"h4_id"}),
                    on="h4_id", how="left")
    m15["ema"] = ema(m15.close, 50)
    m15["rsi"] = rsi(m15.close, 14)
    ce = pd.DatetimeIndex(m15.ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    m15["hora"] = ce.hour + ce.minute/60
    return m15

def patrones(d):
    o,h,l,c = (d[x].to_numpy() for x in ("open","high","low","close"))
    po,pc = np.roll(o,1), np.roll(c,1)
    cuerpo = np.abs(c-o); rango = np.maximum(h-l, 1e-12)
    env_a = (c>o) & (pc<po) & (o<=pc) & (c>=po)
    env_b = (c<o) & (pc>po) & (o>=pc) & (c<=po)
    mecha_i = np.minimum(o,c)-l; mecha_s = h-np.maximum(o,c)
    martillo = (mecha_i >= 2*cuerpo) & (mecha_s <= cuerpo) & (cuerpo/rango < 0.5)
    estrella = (mecha_s >= 2*cuerpo) & (mecha_i <= cuerpo) & (cuerpo/rango < 0.5)
    for v in (env_a,env_b,martillo,estrella): v[0]=False
    return (env_a|martillo), (env_b|estrella)

def senales(d, unit, tp_r, invertir=False):
    ga, gb = patrones(d)
    o,h,l,c = (d[x].to_numpy() for x in ("open","high","low","close"))
    em, rs = d.ema.to_numpy(), d.rsi.to_numpy()
    arr, crx, hora, ts = (d[x].to_numpy() for x in ("t_arriba","t_cruces","hora","ts"))
    toco30 = pd.Series(rs<=30).rolling(VENT_RSI).max().to_numpy()
    toco70 = pd.Series(rs>=70).rolling(VENT_RSI).max().to_numpy()
    out, emb = [], dict(tendencia=0, toque=0, rsi=0, patron=0, coherente=0)
    for i in range(60, len(d)-1):
        if np.isnan(em[i]) or np.isnan(rs[i]) or arr[i] is None: continue
        if not (8.0 <= hora[i] < 17.0): continue
        if np.isnan(crx[i]) or crx[i] > MAX_CRUCES: continue
        largo = bool(arr[i])
        emb["tendencia"] += 1
        if largo and not (l[i] <= em[i]): continue
        if (not largo) and not (h[i] >= em[i]): continue
        emb["toque"] += 1
        if largo and toco30[i] != 1: continue
        if (not largo) and toco70[i] != 1: continue
        emb["rsi"] += 1
        if largo and not ga[i]: continue
        if (not largo) and not gb[i]: continue
        emb["patron"] += 1
        j0 = max(0, i-VENT_RSI)
        piv_lo, piv_hi = l[j0:i+1].min(), h[j0:i+1].max()
        rg = max(piv_hi-piv_lo, unit)
        dire = (not largo) if invertir else largo
        e = o[i+1]
        sl = (piv_lo - SL_BUF*rg) if dire else (piv_hi + SL_BUF*rg)
        riesgo = abs(e-sl)
        if riesgo <= 0: continue
        tp = e + tp_r*riesgo if dire else e - tp_r*riesgo
        if not ((e>sl and tp>e) if dire else (e<sl and tp<e)): continue
        emb["coherente"] += 1
        out.append(dict(ts=ts[i+1], largo=dire, e=e, sl=sl, tp=tp, riesgo_u=riesgo/unit))
    return pd.DataFrame(out), emb

def simula(sig, m1, unit, coste):
    if sig.empty: return sig
    T,H,L,C = (m1[x].to_numpy() for x in ("ts","high","low","close"))
    out, libre = [], np.datetime64("1970-01-01")
    for r in sig.itertuples():
        t0 = np.datetime64(pd.Timestamp(r.ts))
        if t0 < libre: continue
        i0 = int(np.searchsorted(T, t0)); i1 = min(i0+MAX_HORAS*60, len(T))
        if i0 >= len(T) or i1 <= i0: continue
        a,b = H[i0:i1], L[i0:i1]
        gsl,gtp = ((b<=r.sl, a>=r.tp) if r.largo else (a>=r.sl, b<=r.tp))
        isl = int(np.argmax(gsl)) if gsl.any() else 10**9
        itp = int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl==10**9 and itp==10**9: sal,mot,f = C[i1-1],"tiempo",(i1-i0)-1
        elif isl<=itp: sal,mot,f = r.sl,"SL",isl
        else: sal,mot,f = r.tp,"TP",itp
        br = (sal-r.e) if r.largo else (r.e-sal)
        out.append(dict(ts=r.ts, motivo=mot, riesgo_u=r.riesgo_u,
                        bruto=(br/unit)/r.riesgo_u, R=(br/unit-coste)/r.riesgo_u))
        libre = T[i0+f]
    return pd.DataFrame(out)

def pz(x):
    n=len(x)
    if n<3: return 0.0,1.0
    se=x.std(ddof=1)/sqrt(n); z=x.mean()/se if se>0 else 0.0
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

def pf(R):
    g,p = R[R>0].sum(), -R[R<=0].sum()
    return g/p if p>0 else float("inf")
