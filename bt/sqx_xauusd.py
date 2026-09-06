"""Strategy 4.3.23 - Improved 5.1.20 · XAUUSD H1 · solo largos.

Implementada LITERALMENTE segun la especificacion, sin anadir nada.

  filtro      GannHiLo(5) en la vela H1 ANTERIOR
  gatillo     Buy Stop en el maximo de las ultimas 51 velas H1 CERRADAS
  validez     10 barras; si no se ejecuta, se cancela
  stop        1 x ATR(95) de H1, fijado en la entrada
  objetivo    no hay
  tiempo      cierre a las 5 barras H1 desde la apertura, al precio que haya
  posiciones  1 como maximo; con posicion abierta no se generan senales
  horario     senales solo entre 01:30 y 23:30 hora del CSV
  riesgo      1 % del capital del momento
  costes      comision 6 $/lote ida y vuelta · spread 0,2 en cada ejecucion
              swap 35 $/lote por noche en largos

Ejecucion MINUTO A MINUTO dentro de cada vela H1: nada se aproxima.

  python3 bt/sqx_xauusd.py
"""
import os, numpy as np, pandas as pd

CAP0, RIESGO      = 100_000.0, 0.01
GANN, NBAR, ATRN  = 5, 51, 95
VALIDEZ, NSAL     = 10, 5
H_INI, H_FIN      = 1*60+30, 23*60+30
COM_LOTE, SPREAD, SWAP = 6.0, 0.2, 35.0
ONZAS             = 100.0            # 1 lote de XAUUSD = 100 onzas -> 100 $/punto

M = pd.concat([pd.read_parquet("data/xauusd_m1.parquet"),
               pd.read_parquet("data/xauusd_m1_2026.parquet")], ignore_index=True)
M["ts"] = pd.to_datetime(M["ts"]); M = M.sort_values("ts").drop_duplicates("ts")
M = M.reset_index(drop=True)
print(f"CSV M1 · {len(M)} minutos · {M.ts.min()} -> {M.ts.max()}")
d = M.ts.diff().dt.total_seconds()/60
print(f"  huecos > 60 min: {int((d > 60).sum())}   ·   mayor hueco "
      f"{d.max()/60/24:.1f} dias (fines de semana)")
print(f"  duplicados: {int(M.ts.duplicated().sum())}   ·   minutos sin dato dentro "
      f"de la semana: {int(((d > 1) & (d <= 60*24)).sum())}\n")

H = M.set_index("ts").resample("60min", label="left", closed="left").agg(
    o=("open","first"), h=("high","max"), l=("low","min"),
    c=("close","last"), n=("close","size")).dropna()
H = H[H.n >= 10]
print(f"H1 agregadas: {len(H)} velas")

# --- GannHiLo Activator, periodo 5 -----------------------------------------
sh = H.h.rolling(GANN).mean(); sl = H.l.rolling(GANN).mean()
est = np.zeros(len(H)); cur = 0
hv, shv, slv = H.c.to_numpy(), sh.to_numpy(), sl.to_numpy()
for i in range(len(H)):
    if not np.isnan(shv[i]):
        if   hv[i] > shv[i]: cur = +1
        elif hv[i] < slv[i]: cur = -1
    est[i] = cur
H["gann"] = est

# --- ATR(95) y maximo de 51 velas CERRADAS ---------------------------------
tr = pd.concat([H.h-H.l, (H.h-H.c.shift()).abs(), (H.l-H.c.shift()).abs()],
               axis=1).max(axis=1)
H["atr"] = tr.rolling(ATRN).mean()
H["max51"] = H.h.rolling(NBAR).max()          # incluye la vela k, ya cerrada
H["hm"] = H.index.hour*60 + H.index.minute

# --- indice de minutos por vela H1 -----------------------------------------
M["hb"] = M.ts.dt.floor("60min")
ini = M.groupby("hb").apply(lambda g: g.index[0], include_groups=False)
fin = M.groupby("hb").apply(lambda g: g.index[-1], include_groups=False)
IDX = pd.DataFrame(dict(i0=ini, i1=fin)).reindex(H.index)

mh, ml, mo, mc, mt = (M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy(),
                      M.close.to_numpy(), M.ts.to_numpy())
h_o = H.o.to_numpy(); h_at = H.atr.to_numpy(); h_mx = H.max51.to_numpy()
h_gn = H.gann.to_numpy(); h_hm = H.hm.to_numpy()
i0 = IDX.i0.to_numpy(); i1 = IDX.i1.to_numpy()
n = len(H)

cap, ops = CAP0, []
k = NBAR + ATRN + 2
while k < n - NSAL - 1:
    # senal evaluada al CIERRE de la vela k: filtro en la vela ANTERIOR
    if (np.isnan(h_at[k]) or np.isnan(h_mx[k]) or h_gn[k] != +1
            or not (H_INI <= h_hm[k] <= H_FIN)):
        k += 1; continue
    niv = h_mx[k]
    # orden pendiente viva en las velas k+1 .. k+VALIDEZ
    ent = None
    for j in range(k+1, min(k+1+VALIDEZ, n)):
        if np.isnan(i0[j]): continue
        a, b = int(i0[j]), int(i1[j])
        t = np.flatnonzero(mh[a:b+1] >= niv)
        if len(t):
            m = a + int(t[0])
            ent = (j, m, max(niv, mo[m]) + SPREAD)   # hueco al alza: al precio real
            break
    if ent is None:
        k += 1; continue
    jent, ment, px = ent
    atr = h_at[k]
    stop = px - atr
    lotes = RIESGO*cap/(atr*ONZAS)
    jsal = jent + NSAL
    if jsal >= n or np.isnan(i0[jsal]): break
    msal = int(i0[jsal])
    # recorrido MINUTO A MINUTO desde la entrada hasta el cierre por tiempo
    st = np.flatnonzero(ml[ment:msal+1] <= stop)
    if len(st):
        mfin = ment + int(st[0]); sale = stop - SPREAD; motivo = "stop"
    else:
        mfin = msal; sale = mo[msal] - SPREAD; motivo = "tiempo"
    noches = len(pd.date_range(pd.Timestamp(mt[ment]).ceil("D"),
                               pd.Timestamp(mt[mfin]), freq="D"))
    bruto = (sale - px)*ONZAS*lotes
    coste = COM_LOTE*lotes + SWAP*lotes*noches
    cap  += bruto - coste
    ops.append(dict(entrada=pd.Timestamp(mt[ment]), salida=pd.Timestamp(mt[mfin]),
                    px_ent=px, px_sal=sale, lotes=lotes, atr=atr, motivo=motivo,
                    noches=noches, bruto=bruto, coste=coste, neto=bruto-coste,
                    capital=cap))
    # con posicion abierta no se generan senales: se reanuda tras la salida
    k = max(k+1, jsal)

O = pd.DataFrame(ops); O.to_csv("data/sqx_xauusd_operaciones.csv", index=False)
print(f"\n{'='*70}\nRESULTADO\n{'='*70}")
if not len(O): raise SystemExit("sin operaciones")
ret = cap/CAP0 - 1
anios = (O.salida.max()-O.entrada.min()).days/365.25
gan = O[O.neto > 0].neto; per = O[O.neto <= 0].neto
eq = CAP0 + O.neto.cumsum(); dd = (eq/eq.cummax() - 1).min()
rach = (O.neto <= 0).astype(int)
mx = 0; c = 0
for v in rach:
    c = c+1 if v else 0; mx = max(mx, c)
print(f"  operaciones          {len(O)}")
print(f"  periodo              {O.entrada.min().date()} -> {O.salida.max().date()}"
      f"  ({anios:.2f} anios)")
print(f"  capital final        {cap:,.0f} $   ({ret*100:+.1f} %)")
print(f"  CAGR                 {((cap/CAP0)**(1/anios)-1)*100:+.2f} %")
print(f"  acierto              {len(gan)/len(O)*100:.1f} %")
print(f"  profit factor        {gan.sum()/abs(per.sum()):.3f}")
print(f"  payoff (media G/P)   {gan.mean()/abs(per.mean()):.3f}")
print(f"  drawdown maximo      {dd*100:.1f} %")
print(f"  racha maxima de perdidas  {mx}")
print(f"  salidas por stop {int((O.motivo=='stop').sum())} · "
      f"por tiempo {int((O.motivo=='tiempo').sum())}")
print(f"  coste total          {O.coste.sum():,.0f} $   "
      f"({O.coste.sum()/abs(O.bruto).sum()*100:.1f} % del bruto movido)")
print(f"  BRUTO total {O.bruto.sum():+,.0f} $   ->   NETO {O.neto.sum():+,.0f} $")
print(f"\n  {'anio':>6} {'ops':>5} {'neto':>12} {'acierto':>9} {'capital fin':>13}")
for y, g in O.groupby(O.entrada.dt.year):
    print(f"  {y:>6} {len(g):>5} {g.neto.sum():>+12,.0f} "
          f"{(g.neto>0).mean()*100:>8.1f}% {g.capital.iloc[-1]:>13,.0f}")
