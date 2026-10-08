"""GPSO · Trading en 5 Pasos, la version COMPLETA con el fibonacci y la gestion.

  1  NIVELES      H1: maximo y minimo de los NDIAS dias previos
  2-4 REACCION    una vela de H1 toca el nivel y CIERRA a un lado
                  cierra por encima -> compra   ·   por debajo -> venta
  5  IMPULSO      esa misma vela ya cerrada de H1 es el impulso.
                  El fibonacci se traza sobre ella: 0 % en el extremo de destino,
                  100 % en el de origen.
  6  RETROCESO    se espera en M5 a que el precio vuelva al 38,2 / 50 / 60 %
  7  INVALIDEZ    si el retroceso pasa del 75 %, la operacion se anula
  8  CONFIRMACION vela ENVOLVENTE (cuerpo y mecha) o MARTILLO en M5,
                  en la direccion del impulso. Los doji no valen.
  9  ENTRADA      al cierre de esa vela de M5
 10  STOP         detras del extremo de la vela de confirmacion
 11  GESTION      A: 2R seco   B: BE a 1R y 2R   C: BE a 1R, 80 % a 2R, resto corre

  python3 bt/gpso_completa.py [instrumento ...]
"""
import os, sys
import numpy as np, pandas as pd

NDIAS = int(os.environ.get("NDIAS", 5))
VENT  = int(os.environ.get("VENT", 8))     # horas para que llegue el retroceso
VIDA  = int(os.environ.get("VIDA", 48))
INVAL = float(os.environ.get("INVAL", 0.75))
FIBS  = [float(x) for x in os.environ.get("FIBS", "0.382,0.50,0.60").split(",")]
CONF  = os.environ.get("CONF", "si")       # "no" para saltarse la confirmacion

INSTR = {
 "EURUSD": (["data/eurusd_m1.parquet"], 1e-4, 1.43),
 "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
 "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
 "XAUUSD": (["data/xauusd_m1.parquet"], 1e-2, 20.0),
 "GRXEUR": (["data/grxeur_m1.parquet"], 1e-0, 1.50),
 "NSXUSD": (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
 "SPXUSD": (["data/spxusd_m1.parquet"], 1e-0, 0.50),
}

def envolvente(o, h, l, c, po, ph, pl, pc, lado):
    if lado > 0 and not (c > o): return False
    if lado < 0 and not (c < o): return False
    return h >= ph and l <= pl and abs(c-o) > abs(pc-po)

def martillo(o, h, l, c, lado):
    rango = h - l
    if rango <= 0: return False
    cuerpo = abs(c-o)
    if cuerpo/rango > 0.34: return False
    sup, inf = h - max(o,c), min(o,c) - l
    if lado > 0: return inf/rango >= 0.50 and sup/rango <= 0.25   # mecha abajo
    else:        return sup/rango >= 0.50 and inf/rango <= 0.25   # mecha arriba

def corre(nom):
    rutas, U, COSTE = INSTR[nom]
    d = pd.concat([pd.read_parquet(r) for r in rutas], ignore_index=True)
    d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
    d = d.reset_index(drop=True); d["dia"] = pd.DatetimeIndex(d.ts).date
    def agr(m):
        g = d.set_index("ts").resample(f"{m}min", label="left", closed="left").agg(
            o=("open","first"), h=("high","max"), l=("low","min"),
            c=("close","last"), n=("close","size")).dropna()
        return g[g.n >= max(1, m*0.4)].reset_index()
    H, M5 = agr(60), agr(5)
    dia = d.groupby("dia").agg(hi=("high","max"), lo=("low","min"))
    dias = list(dia.index); niv = {}
    for k, x in enumerate(dias):
        if k < NDIAS: continue
        v = []
        for j in range(k-NDIAS, k): v += [float(dia.hi.iloc[j]), float(dia.lo.iloc[j])]
        niv[x] = sorted(set(v))
    T1, O1, HI, LO = d.ts.to_numpy(), d.open.to_numpy(), d.high.to_numpy(), d.low.to_numpy()
    ht, hh, hl, hc = H.ts.to_numpy(), H.h.to_numpy(), H.l.to_numpy(), H.c.to_numpy()
    hdia = pd.DatetimeIndex(H.ts).date
    mt, mo, mh, ml, mc = (M5.ts.to_numpy(), M5.o.to_numpy(), M5.h.to_numpy(),
                          M5.l.to_numpy(), M5.c.to_numpy())
    filas, visto = [], set()
    n_react = n_zona = n_inval = n_conf = 0
    for i in range(len(H)):
        x = hdia[i]
        if x not in niv: continue
        for L in niv[x]:
            if not (hl[i] <= L <= hh[i]): continue
            lado = 1 if hc[i] > L else (-1 if hc[i] < L else 0)
            if lado == 0: continue
            clave = (x, round(L, 6), lado)
            if clave in visto: continue
            visto.add(clave); n_react += 1
            # el fibonacci sobre la vela YA CERRADA de H1
            fin = hh[i] if lado > 0 else hl[i]          # 0 % · final del impulso
            ini = hl[i] if lado > 0 else hh(i) if False else hl[i]
            ini = hl[i] if lado > 0 else hh[i]          # 100 % · inicio
            imp = abs(fin - ini)
            if imp <= 0: continue
            zona_a = fin - lado*max(FIBS)*imp           # el retroceso mas profundo
            zona_b = fin - lado*min(FIBS)*imp           # el mas superficial
            lim    = fin - lado*INVAL*imp               # el 75 %: invalida
            a = int(np.searchsorted(mt, ht[i] + np.timedelta64(60, "m")))
            b = int(np.searchsorted(mt, ht[i] + np.timedelta64(60 + VENT*60, "m")))
            if b <= a+1: continue
            en_zona = False; ent = None
            for k in range(a, b):
                # invalidez: el precio se pasa del 75 %
                if (lado > 0 and ml[k] < lim) or (lado < 0 and mh[k] > lim):
                    n_inval += 1; break
                if not en_zona:
                    toca = (ml[k] <= zona_b) if lado > 0 else (mh[k] >= zona_b)
                    if toca: en_zona = True; n_zona += 1
                    else: continue
                if k == a: continue
                if CONF == "si":
                    ok = (envolvente(mo[k], mh[k], ml[k], mc[k],
                                     mo[k-1], mh[k-1], ml[k-1], mc[k-1], lado)
                          or martillo(mo[k], mh[k], ml[k], mc[k], lado))
                else:
                    ok = (mc[k] > mo[k]) if lado > 0 else (mc[k] < mo[k])
                if not ok: continue
                ent = float(mc[k]); stp = float(ml[k] if lado > 0 else mh[k])
                tk = k; n_conf += 1; break
            if ent is None: continue
            rgo = abs(ent - stp)
            if rgo <= 0: continue
            j  = int(np.searchsorted(T1, mt[tk] + np.timedelta64(5, "m")))
            j2 = int(np.searchsorted(T1, mt[tk] + np.timedelta64(VIDA, "h")))
            if j2 <= j+1: continue
            hs, ls = HI[j:j2], LO[j:j2]
            n1 = ent + lado*1*rgo; n2 = ent + lado*2*rgo
            def primer(gate):
                return int(np.argmax(gate)) if gate.any() else 10**9
            iS  = primer((ls <= stp) if lado > 0 else (hs >= stp))
            i1  = primer((hs >= n1)  if lado > 0 else (ls <= n1))
            i2  = primer((hs >= n2)  if lado > 0 else (ls <= n2))
            # A · 2R seco
            RA = -1.0 if iS <= i2 else (2.0 if i2 < 10**9 else
                 ((float(O1[j2-1])-ent) if lado > 0 else (ent-float(O1[j2-1])))/rgo)
            # B · BE a 1R. Tras tocar 1R el stop pasa a la ENTRADA, asi que a
            # partir de ahi hay que mirar la vuelta a entrada, no el stop viejo.
            def trasBE(desde):
                h2, l2 = hs[desde+1:], ls[desde+1:]
                if not len(h2): return 0.0
                ib = primer((l2 <= ent) if lado > 0 else (h2 >= ent))
                ig = primer((h2 >= n2)  if lado > 0 else (l2 <= n2))
                return 2.0 if ig < ib else 0.0
            RB = -1.0 if iS <= i1 else (0.0 if i1 == 10**9 else trasBE(i1))
            # C · BE a 1R, 80 % a 2R, 20 % corre a por el siguiente nivel
            if iS <= i1: RC = -1.0
            elif i1 == 10**9 or trasBE(i1) == 0.0: RC = 0.0
            else:
                cand = [v for v in niv[x] if (v > ent if lado > 0 else v < ent)]
                obj = (min(cand) if lado > 0 else max(cand)) if cand else None
                resto = 2.0
                if obj is not None and abs(obj-ent)/rgo > 2:
                    io = primer((hs >= obj) if lado > 0 else (ls <= obj))
                    # tras el parcial el stop esta en BE
                    ib = primer((ls <= ent) if lado > 0 else (hs >= ent))
                    resto = abs(obj-ent)/rgo if io < ib else 0.0
                RC = 0.8*2.0 + 0.2*resto
            c = COSTE*U/rgo
            filas.append((RA, RA-c, RB, RB-c, RC, RC-c, rgo/U, lado,
                          pd.Timestamp(ht[i]).year))
    df = pd.DataFrame(filas, columns=["RA","nA","RB","nB","RC","nC","rgo","lado","anio"])
    return df, dict(react=n_react, zona=n_zona, inval=n_inval, conf=n_conf)

if __name__ == "__main__":
    print(f"fibs={FIBS} invalidez={INVAL} confirmación={CONF} ventana={VENT}h\n")
    print(f"{'instr':>7s} {'reacc':>7s} {'zona':>6s} {'inval':>6s} {'ENTRA':>6s} "
          f"{'A 2R':>16s} {'B BE+2R':>16s} {'C parciales':>16s}")
    print("-"*96)
    tot = []
    for nom in (sys.argv[1:] or ["EURUSD","GBPUSD","USDJPY","NSXUSD"]):
        d, c = corre(nom)
        if not len(d): print(f"{nom:>7s}  sin operaciones"); continue
        d.to_csv(f"data/gpsoC_{nom}.csv", index=False)
        f = lambda R, n: f"{100*(d[R]>0).mean():4.1f}% {d[n].mean():+6.3f}"
        print(f"{nom:>7s} {c['react']:7d} {c['zona']:6d} {c['inval']:6d} {len(d):6d} "
              f"{f('RA','nA'):>16s} {f('RB','nB'):>16s} {f('RC','nC'):>16s}")
        tot.append(dict(instr=nom, n=len(d), **{k: d[k].mean() for k in
                        ("RA","nA","RB","nB","RC","nC")}))
    t = pd.DataFrame(tot)
    if len(t):
        print("-"*96)
        for g,n in (("RA","nA"),("RB","nB"),("RC","nC")):
            print(f"  {g}: bruta media {t[g].mean():+.3f} (positiva {(t[g]>0).sum()}/{len(t)})"
                  f"   ·   NETA media {t[n].mean():+.3f} (positiva {(t[n]>0).sum()}/{len(t)})")
