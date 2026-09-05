"""La familia "alta tasa de acierto / cola catastrofica", medida.

Preregistro sellado en docs/PREREGISTRO_alto_winrate.md (commit a9b6fe8).

No busca senal. Mide GEOMETRIA: que pasa cuando el TP es diminuto y el
stop enorme, y sobre todo si eso cambia la probabilidad de pasar una
evaluacion de fondeo -que es un problema de barreras, no de acierto-.

  python3 bt/alto_winrate.py
"""
import os, sys, itertools
import numpy as np, pandas as pd

# ---------------------------------------------------------------- ajustes
SIMS   = int(os.environ.get("SIMS", 10000))
NMAX   = 200                       # dias maximos de evaluacion
OBJ    = 3000.0                    # objetivo de beneficio, $
DD     = 2000.0                    # drawdown maximo, $
DIAMIN = 5                         # dias minimos de operativa
CONSIS = 0.40                      # ningun dia > 40 % del beneficio
SIZS   = (0.20, 0.50, 1.00)        # el stop vale esta fraccion del drawdown
CUOTA  = 80.0                      # cuota de la evaluacion, EUR
PAGO   = 1823.0                    # ganancia media por cuenta pasada, EUR
FCOSTE = float(os.environ.get("FCOSTE", 1.0))   # sensibilidad al coste

INSTR = {                          # ruta, $/punto del micro, coste ida+vuelta pts
 "NASDAQ": ("data/nsxusd_m1.parquet", 2.0, 1.20),
 "SP500":  ("data/spxusd_m1.parquet", 5.0, 0.80),
}
SLF  = (0.25, 0.50, 1.00)                    # stop, en rangos diarios
RATS = ((1,1), (1,3), (1,10), (1,30))        # TP:SL
rng  = np.random.default_rng(20260905)

# ---------------------------------------------------------------- datos
def sesiones(ruta):
    """Devuelve una lista de dias: (fecha, ts, o, h, l, c) del cash de NY."""
    d = pd.read_parquet(ruta)
    d["ts"] = pd.to_datetime(d["ts"])
    ny = d.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    mm = ny.dt.hour*60 + ny.dt.minute
    m  = (mm >= 9*60+30) & (mm <= 15*60+55) & (ny.dt.dayofweek < 5)
    d  = d[m].copy(); d["dia"] = ny[m].dt.date; d["min"] = mm[m]
    out = []
    for dia, g in d.groupby("dia", sort=True):
        if len(g) < 120: continue          # sesion incompleta / festivo
        out.append((dia, g["min"].to_numpy(),
                    g.open.to_numpy(), g.high.to_numpy(),
                    g.low.to_numpy(),  g.close.to_numpy()))
    return out

def resuelve(h, l, cl, k, ent, tp, sl, lado):
    """k es la primera barra en la que la posicion ya esta viva."""
    """Primer toque desde la barra k+1.

    Devuelve (estado, puntos_brutos). Estado +1 TP, -1 SL, 0 sin resolver.
    Sin resolver = se cierra a mercado en la ultima vela de la sesion, con
    el resultado que haya (marcado a mercado, NO cero)."""
    if lado > 0: ntp, nsl = ent+tp, ent-sl
    else:        ntp, nsl = ent-tp, ent+sl
    if lado > 0:
        a = np.flatnonzero(h[k:] >= ntp); b = np.flatnonzero(l[k:] <= nsl)
    else:
        a = np.flatnonzero(l[k:] <= ntp); b = np.flatnonzero(h[k:] >= nsl)
    ia = a[0] if len(a) else 10**9
    ib = b[0] if len(b) else 10**9
    if ia == ib == 10**9: return 0, (float(cl[-1])-ent)*lado
    # empate en la misma vela: se asume lo peor (toca antes el stop)
    return (+1, tp) if ia < ib else (-1, -sl)

# ---------------------------------------------------------------- montecarlo
def evalua(pnl, modo):
    """P(pasar la evaluacion) remuestreando `pnl` (dolares por operacion)."""
    x  = rng.choice(pnl, size=(SIMS, NMAX), replace=True)
    eq = np.cumsum(x, axis=1)
    mx = np.maximum.accumulate(x,  axis=1)      # mayor dia ganador hasta aqui
    pk = np.maximum.accumulate(eq, axis=1)
    umbral = -DD if modo == "estatico" else np.minimum(pk - DD, 0.0)
    fal = eq <= umbral
    idx = np.arange(NMAX)[None, :]
    pas = (eq >= OBJ) & (idx >= DIAMIN-1) & (mx <= CONSIS*eq)
    ip = np.where(pas.any(1), pas.argmax(1), NMAX+9)
    if_ = np.where(fal.any(1), fal.argmax(1), NMAX+9)
    return float(np.mean(ip < if_)), float(np.median(ip[ip < if_])) if (ip < if_).any() else float("nan")

# ---------------------------------------------------------------- pase
filas = []
for nom, (ruta, DPP, CPTS) in INSTR.items():
    S = sesiones(ruta)
    rango = float(np.median([hh.max()-ll.min() for _,_,_,hh,ll,_ in S]))
    coste = CPTS * FCOSTE
    print(f"\n{nom}: {len(S)} sesiones · rango diario mediano {rango:.1f} pts "
          f"· coste {coste:.2f} pts ({coste*DPP:.2f} $/contrato)", flush=True)

    # --- entradas: (indice de barra, precio, lado) por dia
    ENT = {"A": [], "B": [], "C": []}
    for dia, mm, oo, hh, ll, cc in S:
        k5 = int(np.searchsorted(mm, 9*60+35))
        if k5 < len(mm)-10:
            ENT["A"].append((dia, mm, hh, ll, cc, k5, float(oo[k5]), +1))
            ENT["C"].append((dia, mm, hh, ll, cc, k5, float(oo[k5]), -1))
        # B: primer retroceso de 0,15 x rango desde la apertura, antes de las 12
        niv = float(oo[0]) - 0.15*rango
        lim = int(np.searchsorted(mm, 12*60))
        j = np.flatnonzero(ll[:lim] <= niv)
        if len(j) and j[0] < len(mm)-10:
            ENT["B"].append((dia, mm, hh, ll, cc, int(j[0])+1, niv, +1))

    for ent_nom, dias in ENT.items():
        for f, (a, b) in itertools.product(SLF, RATS):
            sl = f*rango; tp = sl*a/b
            res, pnl = [], []
            for dia, mm, hh, ll, cc, k, px, lado in dias:
                r, g = resuelve(hh, ll, cc, k, px, tp, sl, lado)
                res.append(r); pnl.append(g - coste)
            res = np.array(res); pnl = np.array(pnl)
            n = len(res)
            if n < 100: continue
            wr   = float(np.mean(pnl > 0))           # acierto real (con el cierre)
            nres = int(np.sum(res != 0))             # cuantas tocan barrera
            base = sl/(sl+tp)                        # acierto geometrico
            wrr  = float(np.sum(res > 0)/nres) if nres else float("nan")
            z    = (wrr-base)/np.sqrt(base*(1-base)/nres) if nres else float("nan")
            for phi in SIZS:
                # dimensionado: la PERDIDA vale `phi` veces el drawdown entero
                ctr  = max(1, int(round(phi*DD/(sl*DPP))))
                usd  = pnl*ctr*DPP
                usd0 = (pnl+coste)*ctr*DPP              # el mismo, sin coste
                pest, dest = evalua(usd,  "estatico")
                pdin, ddin = evalua(usd,  "dinamico")
                pes0, _    = evalua(usd0, "estatico")
                pdi0, _    = evalua(usd0, "dinamico")
                filas.append(dict(instr=nom, entrada=ent_nom, slf=f,
                                  rr=f"1:{b//a}", phi=phi,
                                  n=n, nres=nres, tp=tp, sl=sl, ctr=ctr,
                                  wr=wr, wrr=wrr, base=base, z=z,
                                  perd=float(sl*ctr*DPP), gana=float(tp*ctr*DPP),
                                  Rbruto=float(np.mean(pnl+coste)/sl),
                                  Rneto=float(np.mean(pnl)/sl),
                                  usd=float(np.mean(usd)),
                                  pest=pest, pdin=pdin, pes0=pes0, pdi0=pdi0,
                                  dias=ddin))
                print(f"  {ent_nom} sl={f:.2f} {f'1:{b//a}':>5} phi={phi:.2f} "
                      f"x{ctr:<3d} gana {tp*ctr*DPP:7.1f}$ pierde {sl*ctr*DPP:7.0f}$ "
                      f"| barrera {wrr*100:5.1f}% (geom {base*100:5.1f}% "
                      f"z {z:+6.2f}) | neto {float(np.mean(usd)):+8.2f}$ "
                      f"| P {pest*100:5.1f}/{pdin*100:5.1f}% "
                      f"sinC {pes0*100:5.1f}/{pdi0*100:5.1f}%", flush=True)

D = pd.DataFrame(filas)
D.to_csv(f"data/alto_winrate{'' if FCOSTE==1.0 else f'_c{FCOSTE}'}.csv", index=False)
print(f"\nguardado · {len(D)} celdas")
