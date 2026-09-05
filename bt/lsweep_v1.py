"""EUR/USD London Liquidity Sweep V1 · implementacion literal del protocolo.

Preregistro en docs/PREREGISTRO_lsweep_v1.md.

  SWEEP -> MSS -> DESPLAZAMIENTO -> FVG -> RETROCESO -> ENTRADA
  Si falta cualquiera: NO TRADE.

Todo causal: en cada instante solo se usa informacion cerrada hasta ese
instante (regla 29). Ejecucion minuto a minuto.

  VIDA=1030 python3 bt/lsweep_v1.py
"""
import os, numpy as np, pandas as pd

U, COSTE   = 1e-4, 1.43
RANGO_MIN, RANGO_MAX = 10.0, 35.0
DESPL      = 0.50
RR_MIN     = 2.0
BUFFER     = float(os.environ.get("BUF", 1.0))   # pips detras del sweep
V_INI, V_FIN = 7*60+30, 10*60+30      # ventana 07:30-10:30 Londres
VIDA       = int(os.environ.get("VIDA", V_FIN))   # hasta cuando puede llenarse
MAXOPS     = 2
PAR        = os.environ.get("PAR", "EURUSD")
RUTAS = {"EURUSD":"data/eurusd_m1.parquet", "GBPUSD":"data/gbpusd_m1.parquet"}

M = pd.read_parquet(RUTAS[PAR]); M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
lon = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/London").dt.tz_localize(None)
M["t"] = lon; M["d"] = lon.dt.date
M["m"] = lon.dt.hour*60 + lon.dt.minute
M = M[(lon.dt.dayofweek < 5).to_numpy()].reset_index(drop=True)
print(f"{PAR} · {len(M)} minutos · {M.d.min()} -> {M.d.max()} · hora de Londres")

def barras(g, k):
    h = g.set_index("t").resample(f"{k}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return h[h.n >= 1]

def swings(h, l):
    """Swing de 3 velas (regla 7). Confirmado en n+1, usable desde n+1."""
    n = len(h); sh = np.zeros(n, bool); sl = np.zeros(n, bool)
    if n < 3: return sh, sl
    sh[1:n-1] = (h[1:n-1] > h[0:n-2]) & (h[1:n-1] > h[2:n])
    sl[1:n-1] = (l[1:n-1] < l[0:n-2]) & (l[1:n-1] < l[2:n])
    return sh, sl

DIAS = sorted(M.d.unique())
G = {d: g for d, g in M.groupby("d")}
ops = []; motivos = {}
def no(m): motivos[m] = motivos.get(m, 0) + 1

for di in range(1, len(DIAS)):
    d, dprev = DIAS[di], DIAS[di-1]
    g, gp = G[d], G[dprev]
    # --- rango asiatico 00:00-06:00 Londres
    A = g[(g["m"] >= 0) & (g["m"] < 360)]
    if len(A) < 120: no("sin rango asiatico"); continue
    AH, AL = float(A.high.max()), float(A.low.min())
    rng_p = (AH-AL)/U
    if rng_p < RANGO_MIN: no("rango < 10 pips"); continue
    if rng_p > RANGO_MAX: no("rango > 35 pips"); continue
    PDH, PDL = float(gp.high.max()), float(gp.low.min())
    # --- swings de 15M y 1H disponibles ANTES de la ventana (causal)
    pre = g[g["m"] < V_INI]
    niv_sup, niv_inf = [AH, PDH], [AL, PDL]
    for k in (15, 60):
        b = barras(pre, k)
        if len(b) < 3: continue
        sh, sl = swings(b.h.to_numpy(), b.l.to_numpy())
        niv_sup += list(b.h.to_numpy()[sh]); niv_inf += list(b.l.to_numpy()[sl])
    # --- ventana de ejecucion en M5
    # La ventana 07:30-10:30 limita cuando se ABRE (regla 23). La posicion
    # corre hasta SL o TP con SL y TP fijos (regla 18). Cierre forzoso
    # declarado: 21:00 Londres del mismo dia.
    W = g[(g["m"] >= V_INI) & (g["m"] <= 21*60)]
    if len(W) < 60: no("ventana incompleta"); continue
    E = barras(W[W["m"] <= V_FIN], 5)
    if len(E) < 8: no("pocas velas M5"); continue
    o,h,l,c = E.o.to_numpy(), E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy()
    em = (E.index.hour*60 + E.index.minute).to_numpy()
    sh5, sl5 = swings(h, l)
    n5 = len(E)
    hechas = 0; parar = False
    for isw in range(n5):
        if parar or hechas >= MAXOPS: break
        # --- 1 · SWEEP (regla 6): mecha fuera, cierre dentro
        if   h[isw] > AH and c[isw] < AH: lado, ext = -1, h[isw]
        elif l[isw] < AL and c[isw] > AL: lado, ext = +1, l[isw]
        else: continue
        # --- 2 · MSS (regla 8) con DESPLAZAMIENTO (regla 9)
        mss = None
        for i in range(isw+1, n5):
            pj = [j for j in range(max(0, isw-12), i)
                  if (sl5[j] if lado < 0 else sh5[j]) and j+1 < i]
            if not pj: continue
            niv = l[pj[-1]] if lado < 0 else h[pj[-1]]
            roto = (c[i] < niv) if lado < 0 else (c[i] > niv)
            if not roto: continue
            rango = h[i]-l[i]
            if rango <= 0: continue
            if abs(c[i]-o[i])/rango < DESPL: no("desplazamiento < 0,50"); continue
            mss = i; break
        if mss is None: no("sin MSS"); continue
        # --- 3 · FVG del trio centrado en la vela del MSS (declarado)
        if mss+1 >= n5: no("sin vela posterior al MSS"); continue
        a1, a3 = mss-1, mss+1
        if a1 < 0: no("sin vela previa al MSS"); continue
        if lado < 0:
            if not (l[a1] > h[a3]): no("sin FVG"); continue
            fhi, flo = l[a1], h[a3]
        else:
            if not (h[a1] < l[a3]): no("sin FVG"); continue
            fhi, flo = l[a3], h[a1]
        ent = (fhi+flo)/2                     # 50 % de la FVG (regla 14)
        stop = ext + BUFFER*U if lado < 0 else ext - BUFFER*U
        rgo = abs(ent-stop)
        if rgo < 0.5*U: no("riesgo diminuto"); continue
        # --- 4 · TP: primera liquidez externa con RR >= 2 (reglas 16 y 17)
        cand = sorted([x for x in (niv_inf if lado < 0 else niv_sup)
                       if (ent-x)*(-lado) > 0], key=lambda x: abs(x-ent))
        tp = None
        for x in cand:
            if abs(x-ent)/rgo >= RR_MIN: tp = x; break
        if tp is None: no("RR < 2"); continue
        # --- 5 · RETROCESO y ENTRADA, minuto a minuto desde el cierre de MSS+1
        t0 = E.index[a3] + pd.Timedelta(minutes=5)
        P = W[(W["t"] >= t0)]
        if len(P) < 3: no("sin minutos tras el MSS"); continue
        pm = P["m"].to_numpy(); ph, pl = P.high.to_numpy(), P.low.to_numpy()
        lim = np.flatnonzero(pm > VIDA)
        fin = int(lim[0]) if len(lim) else len(P)
        if fin < 2: no("ventana agotada"); continue
        toca = (np.flatnonzero(ph[:fin] >= ent) if lado < 0
                else np.flatnonzero(pl[:fin] <= ent))
        if not len(toca): no("no vuelve al 50 % de la FVG"); continue
        k = int(toca[0])
        # el minuto que llena la orden no puede contar como objetivo
        aa = (np.flatnonzero(pl[k+1:] <= tp) if lado < 0
              else np.flatnonzero(ph[k+1:] >= tp))
        bb = (np.flatnonzero(ph[k:] >= stop) if lado < 0
              else np.flatnonzero(pl[k:] <= stop))
        ia = int(aa[0])+1 if len(aa) else 10**9
        ib = int(bb[0])   if len(bb) else 10**9
        rr = abs(tp-ent)/rgo
        if ia == ib == 10**9:
            R = (float(P.close.to_numpy()[-1])-ent)*lado/rgo; res = "abierta"
        elif ia < ib: R, res = rr, "TP"
        else:         R, res = -1.0, "SL"
        ops.append(dict(dia=d, hora=E.index[a3], lado=lado, rngA=rng_p,
                        ent=ent, stop=stop, tp=tp, rgo=rgo/U, rr=rr,
                        R=R, neta=R-COSTE/(rgo/U), res=res,
                        dow=pd.Timestamp(d).dayofweek))
        hechas += 1
        if R > 0: parar = True        # "+2R y se acaba el dia" (regla 20)

O = pd.DataFrame(ops)
O.to_csv(f"data/lsweep_v1_{PAR}_{VIDA}.csv", index=False)
print(f"\n=== POR QUE NO SE OPERA · dias descartados y en que paso ===")
for k, v in sorted(motivos.items(), key=lambda x: -x[1]):
    print(f"  {k:32s} {v:5d}")
print(f"\n=== RESULTADO · {len(O)} operaciones ===")
if len(O) < 10: raise SystemExit("muestra insuficiente")
z = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v))))
g_, p_ = O[O.neta > 0].neta, O[O.neta <= 0].neta
print(f"  periodo            {O.dia.min()} -> {O.dia.max()}")
print(f"  operaciones/mes    {len(O)/((pd.Timestamp(O.dia.max())-pd.Timestamp(O.dia.min())).days/30.44):.1f}")
print(f"  riesgo mediano     {O.rgo.median():.1f} pips  ·  coste/R "
      f"{(COSTE/O.rgo).mean()*100:.1f} %")
print(f"  RR mediano         {O.rr.median():.2f}")
print(f"  win rate           {(O.R>0).mean()*100:.1f} %")
print(f"  resultados         TP {int((O.res=='TP').sum())} · SL "
      f"{int((O.res=='SL').sum())} · abiertas {int((O.res=='abierta').sum())}")
print(f"\n  R BRUTA media      {O.R.mean():+.4f}   z {z(O.R):+.2f}")
print(f"  R NETA  media      {O.neta.mean():+.4f}   z {z(O.neta):+.2f}")
print(f"  profit factor neto {g_.sum()/abs(p_.sum()):.3f}")
eq = O.neta.cumsum()
print(f"  R acumulada        {eq.iloc[-1]:+.1f}   drawdown maximo "
      f"{(eq-eq.cummax()).min():.1f} R")
print(f"\n  {'anio':>6} {'ops':>5} {'winrate':>8} {'R neta':>9} {'acum':>8}")
for y, x in O.groupby(pd.to_datetime(O.dia).dt.year):
    print(f"  {y:>6} {len(x):>5} {(x.R>0).mean()*100:>7.1f}% {x.neta.mean():>+9.4f} "
          f"{x.neta.sum():>+8.1f}")
if os.environ.get("HIJO") == "si":
    print(f"RESUMEN{BUFFER:8.1f} {len(O):5d} {O.rgo.median():6.1f}p "
          f"{(COSTE/O.rgo).mean()*100:7.1f}% "
          f"{int((O.res=='TP').sum()):4d}/{int((O.res=='SL').sum()):<4d} "
          f"{O.R.mean():+9.4f} {z(O.R):+7.2f} {O.neta.mean():+9.4f} {z(O.neta):+7.2f}")
    raise SystemExit
print(f"\n  CRITERIO 1 (bruta z>2):     {'PASA' if z(O.R)>2 else 'FALLA'}")
print(f"  CRITERIO 2 (neta > 0):      {'PASA' if O.neta.mean()>0 else 'FALLA'}")
print(f"  CRITERIO 4 (>=250 ops):     {'PASA' if len(O)>=250 else 'FALLA'} ({len(O)})")
print(f"  CRITERIO 5 (PF neto>1,15):  "
      f"{'PASA' if g_.sum()/abs(p_.sum())>1.15 else 'FALLA'}")

# --------------------------------------------------------------------------
# DIAGNOSTICO · el stop mediano son 6,8 pips y el coste se lleva el 31,5 %.
# ¿Es la senal la que falla, o el stop de 1 pip detras del sweep?
# Se repite todo con buffers mas anchos. Todo lo demas identico.
# --------------------------------------------------------------------------
import subprocess, sys
if os.environ.get("HIJO") != "si":
    print(f"\n{'='*72}\nSENSIBILIDAD AL BUFFER DEL STOP\n{'='*72}")
    print(f"  {'buffer':>8} {'n':>5} {'stop':>7} {'coste/R':>8} {'TP/SL':>9} "
          f"{'BRUTA':>9} {'z':>7} {'NETA':>9} {'z':>7}")
    for b in (1.0, 3.0, 6.0, 10.0, 20.0):
        e = dict(os.environ); e["HIJO"] = "si"; e["BUF"] = str(b)
        r = subprocess.run([sys.executable, "bt/lsweep_v1.py"], capture_output=True,
                           text=True, env=e)
        ln = [x for x in r.stdout.split("\n") if x.startswith("RESUMEN")]
        print("  " + (ln[0][7:] if ln else f"{b:8.1f}  error"), flush=True)
