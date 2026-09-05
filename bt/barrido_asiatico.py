"""Barrido de Liquidez Asiatico en la apertura de Londres · EURUSD.

Preregistro en docs/PREREGISTRO_barrido_asiatico.md.

  rango asiatico 02:00-09:00 CEST (M15)  ->  Asian High / Asian Low
  barrido        09:00-11:00 CEST, el precio pasa de un extremo
  MSS            vela M5 que CIERRA CON CUERPO mas alla del ultimo fractal
                 estructural confirmado del lado contrario
  FVG            hueco de 3 velas dentro del impulso del MSS
  entrada        orden limitada en el FVG (borde cercano / 50 % / lejano)
  stop           2 pips mas alla del extremo barrido
  objetivo       1:3 fijo  o  extremo opuesto del rango

  python3 bt/barrido_asiatico.py
"""
import os, itertools, numpy as np, pandas as pd

U, COSTE = 1e-4, 1.43
PAR   = os.environ.get("PAR", "EURUSD")
NULOS = int(os.environ.get("NULOS", 5))
RUTAS = {"EURUSD":"data/eurusd_m1.parquet", "GBPUSD":"data/gbpusd_m1.parquet",
         "USDJPY":"data/usdjpy_m1.parquet"}
rng = np.random.default_rng(20260905)

def carga(par):
    M = pd.read_parquet(RUTAS[par]); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    loc = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
    M["tloc"] = loc; M["dia"] = loc.dt.date
    M["m"] = loc.dt.hour*60 + loc.dt.minute
    return M[(loc.dt.dayofweek < 5).to_numpy()].reset_index(drop=True)

def m5(g):
    h = g.set_index("tloc").resample("5min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return h[h.n >= 2]

def fractales(h, l):
    n = len(h); fh = np.zeros(n, bool); fl = np.zeros(n, bool)
    if n < 5: return fh, fl
    fh[2:n-2] = ((h[2:n-2]>h[1:n-3])&(h[2:n-2]>h[0:n-4])&
                 (h[2:n-2]>h[3:n-1])&(h[2:n-2]>h[4:n]))
    fl[2:n-2] = ((l[2:n-2]<l[1:n-3])&(l[2:n-2]<l[0:n-4])&
                 (l[2:n-2]<l[3:n-1])&(l[2:n-2]<l[4:n]))
    return fh, fl

def dia(g, borde, obj):
    """Devuelve (R_bruta, stop_pips) o None. Una operacion al dia."""
    A = g[(g["m"] >= 120) & (g["m"] < 540)]
    if len(A) < 200: return None
    AH, AL = A.high.max(), A.low.min()
    L = g[(g["m"] >= 540) & (g["m"] <= 1380)]
    if len(L) < 60: return None
    E = m5(L)
    if len(E) < 20: return None
    o,h,l,c = E.o.to_numpy(), E.h.to_numpy(), E.l.to_numpy(), E.c.to_numpy()
    mm = (E.index.hour*60 + E.index.minute).to_numpy()
    fh, fl = fractales(h, l)
    n = len(E)
    # --- 1 · barrido entre 09:00 y 11:00
    sw = None
    for i in range(n):
        if mm[i] > 660: break                      # 11:00
        if h[i] > AH: sw = (i, -1, h[i]); break     # barre el alto -> venta
        if l[i] < AL: sw = (i, +1, l[i]); break     # barre el bajo -> compra
    if sw is None: return None
    isw, lado, ext = sw
    # --- 2 · MSS: cierre de cuerpo mas alla del ultimo fractal confirmado
    mss = None
    for i in range(isw+1, n):
        if mm[i] > 720: break                      # 12:00
        pj = [j for j in range(max(0,isw-24), i-1)
              if (fl[j] if lado < 0 else fh[j]) and j+2 <= i]
        if not pj: continue
        niv = l[pj[-1]] if lado < 0 else h[pj[-1]]
        cuerpo = (c[i] < niv and c[i] < o[i]) if lado < 0 else (c[i] > niv and c[i] > o[i])
        if cuerpo: mss = i; break
    if mss is None: return None
    # --- 3 · FVG de 3 velas dentro del impulso, buscando hacia atras desde el MSS
    fvg = None
    for i in range(mss, max(isw, 1), -1):
        if i-2 < 0: break
        if lado < 0 and l[i-2] > h[i]: fvg = (h[i], l[i-2]); break
        if lado > 0 and h[i-2] < l[i]: fvg = (h[i-2], l[i]); break
    if fvg is None: return None
    lo_f, hi_f = fvg
    ent = ({"cerca": lo_f, "medio": (lo_f+hi_f)/2, "lejos": hi_f}[borde] if lado < 0
           else {"cerca": hi_f, "medio": (lo_f+hi_f)/2, "lejos": lo_f}[borde])
    stop = ext + 2*U if lado < 0 else ext - 2*U
    rgo = abs(ent - stop)
    if rgo < 1.5*U: return None
    tp = (ent - lado*0 + (3*rgo if lado > 0 else -3*rgo)) if obj == "r3" else \
         (AH if lado > 0 else AL)
    if (tp - ent)*lado <= 0: return None
    # --- 4 · ejecucion minuto a minuto desde el MSS hasta el cierre del dia
    t0 = E.index[mss] + pd.Timedelta(minutes=5)
    P = g[(g["tloc"] >= t0) & (g["m"] <= 1380)]
    if len(P) < 5: return None
    ph, pl, pm = P.high.to_numpy(), P.low.to_numpy(), P.m.to_numpy()
    lim = np.flatnonzero(pm > 720)                 # la orden vive hasta las 12:00
    fin = int(lim[0]) if len(lim) else len(P)
    toca = np.flatnonzero(ph[:fin] >= ent) if lado < 0 else np.flatnonzero(pl[:fin] <= ent)
    if not len(toca): return None
    k = int(toca[0])
    # el minuto que LLENA la orden limitada no puede contar como objetivo:
    # el precio venia hacia la orden, asi que su extremo favorable suele ser
    # anterior al llenado. El stop SI se mira en ese minuto (conservador).
    a = np.flatnonzero(ph[k+1:] >= tp) if lado > 0 else np.flatnonzero(pl[k+1:] <= tp)
    b = np.flatnonzero(pl[k:] <= stop)  if lado > 0 else np.flatnonzero(ph[k:] >= stop)
    ia = int(a[0])+1 if len(a) else 10**9
    ib = int(b[0])   if len(b) else 10**9
    if ia == ib == 10**9:
        sal = P.close.to_numpy()[-1]
        R = (sal-ent)*lado/rgo
    else:
        R = (abs(tp-ent)/rgo) if ia < ib else -1.0
    return R, rgo/U

M = carga(PAR)
print(f"{PAR} · {len(M)} minutos · {M.dia.min()} -> {M.dia.max()}")
G = dict(list(M.groupby("dia")))
print(f"  {len(G)} dias de mercado\n")

def pase(G, borde, obj):
    R, S = [], []
    for d, g in G.items():
        r = dia(g, borde, obj)
        if r: R.append(r[0]); S.append(r[1])
    if len(R) < 40: return None
    R = np.array(R); S = np.array(S)
    net = R - COSTE/S
    z = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v))))
    return dict(n=len(R), stop=float(np.median(S)), bruto=float(R.mean()),
                zb=z(R), neto=float(net.mean()), zn=z(net),
                acierto=float((R>0).mean()), coste=float(np.mean(COSTE/S)))

print(f"  {'entrada':>8} {'objetivo':>9} {'n':>5} {'stop':>7} {'BRUTO':>8} {'z':>6} "
      f"{'NETO':>8} {'z':>6} {'acierto':>8} {'coste/R':>8}")
res = {}
for borde, obj in itertools.product(("cerca","medio","lejos"), ("r3","rango")):
    r = pase(G, borde, obj)
    if not r: print(f"  {borde:>8} {obj:>9}  pocas operaciones"); continue
    res[(borde,obj)] = r
    print(f"  {borde:>8} {obj:>9} {r['n']:>5} {r['stop']:>6.1f}p {r['bruto']:>+8.4f} "
          f"{r['zb']:>+6.2f} {r['neto']:>+8.4f} {r['zn']:>+6.2f} "
          f"{r['acierto']*100:>7.1f}% {r['coste']*100:>7.1f}%", flush=True)
if res:
    b = max(res, key=lambda k: res[k]['zb'])
    print(f"\n  mejor por z bruta: {b[0]} / {b[1]}   "
          f"bruto {res[b]['bruto']:+.4f} (z {res[b]['zb']:+.2f})   "
          f"neto {res[b]['neto']:+.4f} (z {res[b]['zn']:+.2f})")
    print(f"  CRITERIO 1 (bruta z>2): {'PASA' if res[b]['zb']>2 else 'FALLA'}")
    print(f"  CRITERIO 2 (neta > 0):  {'PASA' if res[b]['neto']>0 else 'FALLA'}")
    pos = sum(1 for k in res if res[k]['neto'] > 0)
    print(f"  CRITERIO 5 (>=4 de 6 netas positivas): {pos}/6  "
          f"{'PASA' if pos>=4 else 'FALLA'}")

# --------------------------------------------------------------------------
# CONTROL · ¿es culpa del filtro (barrido+MSS+FVG) o de la ventana y la
# geometria? Entradas al azar en la MISMA ventana, con el MISMO tipo de stop
# (2 pips mas alla del extremo del rango asiatico) y el MISMO objetivo.
# --------------------------------------------------------------------------
def dia_azar(g, obj, rg):
    A = g[(g["m"] >= 120) & (g["m"] < 540)]
    if len(A) < 200: return None
    AH, AL = A.high.max(), A.low.min()
    L = g[(g["m"] >= 540) & (g["m"] <= 1380)]
    if len(L) < 60: return None
    P = L[(L["m"] >= 540) & (L["m"] <= 720)]
    if len(P) < 20: return None
    k = int(rg.integers(0, len(P)))
    ent  = float(P.open.to_numpy()[k])
    lado = +1 if rg.random() < .5 else -1
    ext  = AL if lado > 0 else AH
    stop = ext - 2*U if lado > 0 else ext + 2*U
    rgo  = abs(ent-stop)
    if rgo < 1.5*U: return None
    tp = ent + lado*3*rgo if obj == "r3" else (AH if lado > 0 else AL)
    if (tp-ent)*lado <= 0: return None
    Q = L[L["tloc"] >= P["tloc"].to_numpy()[k]]
    ph, pl = Q.high.to_numpy(), Q.low.to_numpy()
    a = np.flatnonzero(ph[1:] >= tp) if lado > 0 else np.flatnonzero(pl[1:] <= tp)
    b = np.flatnonzero(pl >= -1e9) if False else (
        np.flatnonzero(pl <= stop) if lado > 0 else np.flatnonzero(ph >= stop))
    ia = int(a[0])+1 if len(a) else 10**9
    ib = int(b[0])   if len(b) else 10**9
    if ia == ib == 10**9:
        R = (float(Q.close.to_numpy()[-1])-ent)*lado/rgo
    else:
        R = (abs(tp-ent)/rgo) if ia < ib else -1.0
    return R, rgo/U

print(f"\n=== CONTROL · entradas al AZAR en la misma ventana y geometria ===")
print(f"  {'rep':>4} {'objetivo':>9} {'n':>5} {'stop':>7} {'BRUTO':>8} {'z':>6} "
      f"{'acierto':>8}")
for obj in ("r3","rango"):
    br = []
    for rep in range(5):
        rg = np.random.default_rng(1000+rep)
        R, S = [], []
        for d, g in G.items():
            r = dia_azar(g, obj, rg)
            if r: R.append(r[0]); S.append(r[1])
        if len(R) < 40: continue
        R = np.array(R); S = np.array(S); br.append(R.mean())
        print(f"  {rep+1:>4} {obj:>9} {len(R):>5} {np.median(S):>6.1f}p "
              f"{R.mean():>+8.4f} {R.mean()/(R.std(ddof=1)/np.sqrt(len(R))):>+6.2f} "
              f"{(R>0).mean()*100:>7.1f}%", flush=True)
    if br:
        b = np.array(br); e = res[("cerca",obj)]["bruto"]
        print(f"       azar bruto medio {b.mean():+.4f}  ·  la estrategia {e:+.4f}"
              f"  ->  la estrategia es {'PEOR' if e < b.mean() else 'MEJOR'} que el azar\n")
