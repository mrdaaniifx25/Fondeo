"""EL SISTEMA PEDIDO: day trading EURUSD, ventana de 4 horas, 100 % mecanico.

Diseniado con las UNICAS tres cosas que han medido positivo en este proyecto:
  1 la direccion sale del horizonte largo (momento diario), no del intradia
    -> RESULTADOS_momento_largo.md, RESULTADOS_indicadores.md
  2 la entrada espera un RETROCESO, no una ruptura
    -> RESULTADOS_timing_crt.md: +3 pp de exceso con la direccion dada
  3 el objetivo CERCANO convierte mejor la misma ventaja que el lejano
    -> RESULTADOS_timing_crt.md: R:R 9,8 bate a 15,5 en neta/dia

Se miden Londres y Nueva York por separado, tres R:R y con/sin trailing.
Coste ECN corregido: 0,70 pips (ver RESULTADOS_potencia_operaciones.md).

  python3 bt/sistema_eurusd_intradia.py
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE = 1e-4, 0.70
SES = {"Londres 08-12": ("Europe/London", 8, 12),
       "NuevaYork 08-12": ("America/New_York", 8, 12),
       "NuevaYork 09:30-13:30": ("America/New_York", 9.5, 13.5)}

M = pd.read_parquet("data/eurusd_m1.parquet")
M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
HH, LL, OO, CC = (M[k].to_numpy() for k in ("high","low","open","close"))
utc = M.ts.dt.tz_localize("UTC")

# ---------- contexto D1: direccion por momento (EMA 20 sobre cierres diarios)
d = M.assign(k=M.ts.dt.floor("1440min")).groupby("k").agg(c=("close","last"))
ema20 = d.c.ewm(span=20, adjust=False).mean()
dirD = np.sign(d.c - ema20).shift(1)            # conocida al abrir el dia
mapD = M.ts.dt.floor("1440min").map(dirD).to_numpy()

# ---------- contexto H1: posicion del precio en el rango de las ultimas 6 H1
h = M.assign(k=M.ts.dt.floor("60min")).groupby("k").agg(
    h=("high","max"), l=("low","min"), c=("close","last"))
hh6 = h.h.rolling(6).max().shift(1)
ll6 = h.l.rolling(6).min().shift(1)
pos6 = ((h.c.shift(1) - ll6) / (hh6 - ll6))
mapP = M.ts.dt.floor("60min").map(pos6).to_numpy()

# ---------- M15: velas y ATR(14)
q15 = M.assign(k=M.ts.dt.floor("15min")).groupby("k", sort=True)
b = q15.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"))
b["fin"] = q15.apply(lambda x: x.index[-1], include_groups=False).reindex(b.index)
b = b[b.index.notna()]
tr = pd.concat([b.h-b.l, (b.h-b.c.shift(1)).abs(), (b.l-b.c.shift(1)).abs()], axis=1).max(axis=1)
b["atr"] = tr.rolling(14).mean().shift(1)
O15,H15,L15,C15,A15 = (b[k].to_numpy() for k in ("o","h","l","c","atr"))
FIN = b.fin.to_numpy().astype(int)
BI = b.index


def senales(tz, h0, h1):
    loc = BI.tz_localize("UTC").tz_convert(tz).tz_localize(None)
    hor = loc.hour + loc.minute/60.0
    dentro = (hor >= h0) & (hor < h1)
    out = []
    for i in range(20, len(b)-1):
        if not dentro[i]: continue
        j = FIN[i]
        if not np.isfinite(A15[i]) or A15[i] <= 0: continue
        lado = mapD[j]
        if not np.isfinite(lado) or lado == 0: continue
        lado = int(lado)
        p = mapP[j]
        if not np.isfinite(p): continue
        # RETROCESO a favor del sesgo + vela M15 que confirma el giro
        retro = (p < 1/3) if lado > 0 else (p > 2/3)
        conf = (C15[i] > O15[i]) if lado > 0 else (C15[i] < O15[i])
        if not (retro and conf): continue
        e = j + 1
        if e >= len(M): continue
        out.append((BI[i], e, lado, 1.5*A15[i]/U))     # riesgo = 1,5 x ATR(14) M15
    return pd.DataFrame(out, columns="ts e lado rgo".split())


def resuelve(e, lado, rgo, rr, trail, tope):
    ent = OO[e]
    r = rgo*U
    sl = ent - lado*r
    tp = ent + lado*r*rr
    mejor = ent
    for k in range(e, min(e+tope, len(M))):
        hi, lo = HH[k], LL[k]
        # el valor del stop se calcula con UNA sola expresion para los dos
        # lados: (sl-ent)*lado/r. Escribirla dos veces con los operandos
        # espejados y conservar el *lado la doble-niega en los cortos, que es
        # el fallo que inflo este backtest a PF 2,61 (ver RESULTADOS).
        if lado > 0:
            if lo <= sl: return (sl-ent)*lado/r
            if hi >= tp: return rr
            if trail:
                mejor = max(mejor, hi)
                sl = max(sl, mejor - r)
        else:
            if hi >= sl: return (sl-ent)*lado/r
            if lo <= tp: return rr
            if trail:
                mejor = min(mejor, lo)
                sl = min(sl, mejor + r)
    k = min(e+tope, len(M))-1
    return (CC[k]-ent)*lado/r


def z(x, gr):
    m = x.mean()
    su = pd.DataFrame({"x":x.to_numpy(),"g":gr.to_numpy()}).groupby("g").x.apply(
        lambda v: (v-m).sum())
    s2 = float((su**2).sum())
    return m*len(x)/sqrt(s2) if s2>0 else float("nan")


print(f"{'sesion':<24}{'R:R':>5}{'trail':>7}{'n':>6}{'riesgo':>8}{'coste':>7}"
      f"{'acierto':>9}{'geom':>7}{'PF bru':>8}{'PF neto':>8}{'R neta':>9}{'z':>7}")
RES = {}
for et, (tz, h0, h1) in SES.items():
    S = senales(tz, h0, h1)
    if not len(S): continue
    S["dia"] = pd.to_datetime(S.ts).dt.floor("D")
    for rr in (1.0, 1.5, 2.0):
        for trail in (False, True):
            R = np.array([resuelve(int(r.e), r.lado, r.rgo, rr, trail, 4*60)
                          for _, r in S.iterrows()])
            cr = COSTE/S.rgo.to_numpy()
            n = pd.Series(R - cr)
            g, p = R[R>0].sum(), -R[R<0].sum()
            gn, pn = (R-cr)[(R-cr)>0].sum(), -(R-cr)[(R-cr)<0].sum()
            geo = (S.rgo/(S.rgo + rr*S.rgo)).mean()
            print(f"  {et:<22}{rr:>5.1f}{('si' if trail else 'no'):>7}{len(S):>6}"
                  f"{S.rgo.median():>8.1f}{100*cr.mean():>6.1f}%{100*(R>0).mean():>8.1f}%"
                  f"{100*geo:>6.1f}%{(g/p if p>0 else np.inf):>8.2f}"
                  f"{(gn/pn if pn>0 else np.inf):>8.2f}{n.mean():>+9.4f}"
                  f"{z(n, S.dia.astype(str)):>+7.2f}")
            RES[(et,rr,trail)] = (len(S), (R>0).mean(), gn/pn if pn>0 else np.inf,
                                  n.mean(), S.dia.nunique())

print("\nLA CELDA PEDIDA  ·  Londres 08-12, R:R 1,5, sin trailing")
k = ("Londres 08-12", 1.5, False)
if k in RES:
    n, ac, pf, rn, nd = RES[k]
    print(f"  operaciones {n}   dias {nd}   {n/nd:.2f} por dia")
    print(f"  ACIERTO {100*ac:.1f} %   ·   PROFIT FACTOR NETO {pf:.2f}   ·   R neta {rn:+.4f}")
    # dinero: 1 % de riesgo por operacion sobre 10.000 EUR
    print(f"  a 1 % de riesgo sobre 10.000 EUR: {100*rn:+.2f} EUR por operacion, "
          f"{100*rn*n/nd*21:+.0f} EUR/mes")
