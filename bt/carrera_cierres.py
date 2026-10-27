"""Version fiel de la afirmacion: ellos hablan de PROBABILIDAD de llegar al
siguiente objetivo, no del cierre de la vela siguiente.

Se mide como carrera simetrica desde el cierre de la vela que actua: que llega
antes, +1 ATR o -1 ATR. Simetrica a proposito: comparar "llega al objetivo"
contra "vuelve un poco" estaria sesgado a favor de la distancia mas corta.
Se resuelve vela a vela en M1, asi que el orden dentro de la barra es real.
"""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C

INS = [("EURUSD","data/eurusd_m1.parquet"), ("NAS100","data/nsxusd_m1.parquet"),
       ("GBPUSD","data/gbpusd_m1.parquet"), ("USDJPY","data/usdjpy_m1.parquet")]

def carrera(m1, ref, tfh, k=1.0, horizonte=3):
    h,l,c = (ref[x].to_numpy() for x in ("high","low","close"))
    a = C.atr(h,l,c,20)
    fin = ref["fin"].to_numpy()
    t1 = m1["ts"].to_numpy(); H = m1["high"].to_numpy(); L = m1["low"].to_numpy()
    barras = int(horizonte*tfh*60)
    out = np.full(len(ref), np.nan)
    for i in range(1, len(ref)-1):
        if not np.isfinite(a[i]) or a[i] <= 0: continue
        arriba = c[i] + k*a[i]; abajo = c[i] - k*a[i]
        j0 = int(np.searchsorted(t1, fin[i], side="right"))
        j1 = min(j0+barras, len(t1))
        if j0 >= len(t1): continue
        hh, ll = H[j0:j1], L[j0:j1]
        ga, gb = hh >= arriba, ll <= abajo
        ia = int(np.argmax(ga)) if ga.any() else 10**9
        ib = int(np.argmax(gb)) if gb.any() else 10**9
        if ia == 10**9 and ib == 10**9: continue
        out[i] = +1.0 if ia < ib else (-1.0 if ib < ia else 0.0)
    return out

print("="*100)
print("CARRERA SIMÉTRICA  ·  desde el cierre, ¿llega antes a +1 ATR o a −1 ATR?")
print("  su afirmación: cierra FUERA continúa · cierra DENTRO se da la vuelta")
print("  el 50 % es la moneda al aire. Horizonte 3 velas de referencia.")
print("="*100)

filas = []
for nom, ruta in INS:
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").reset_index(drop=True)
    for tfn, tfh in (("H4",4), ("D1",24)):
        ref = velas_ref(m1, tfh, ancla_ny=1)
        res = carrera(m1, ref, tfh)
        t = C.clasifica(ref)
        t = t.assign(res=res[t.index.to_numpy()])
        t = t[np.isfinite(t.res) & (t.pred != 0)]
        for etq, sel in (("cierra FUERA (continuidad)", t.clase.str.contains("FUERA")),
                         ("cierra DENTRO (reversión)",  t.clase.str.contains("DENTRO"))):
            g = t[sel]
            if len(g) < 50: continue
            ac = (g.res.to_numpy() * g.pred.to_numpy()) > 0
            p = ac.mean(); n = len(g); ee = np.sqrt(p*(1-p)/n)
            filas.append(dict(ins=nom, tf=tfn, celda=etq, n=n, acierto=p,
                              lo=p-1.96*ee, hi=p+1.96*ee))
            print(f"  {nom:7s} {tfn:3s} {etq:28s} n={n:>5,}  acierto {100*p:5.2f} %"
                  f"   IC95 [{100*(p-1.96*ee):5.2f}, {100*(p+1.96*ee):5.2f}]"
                  f"{'   <<<' if p-1.96*ee > 0.50 else ''}")

F = pd.DataFrame(filas)
print("\n" + "="*100)
print("AGREGADO por celda (los cuatro instrumentos)")
print("="*100)
for tfn in ("H4","D1"):
    for etq in F.celda.unique():
        g = F[(F.tf==tfn)&(F.celda==etq)]
        if g.empty: continue
        n = g.n.sum(); p = float((g.acierto*g.n).sum()/n); ee = np.sqrt(p*(1-p)/n)
        print(f"  {tfn:3s} {etq:28s} n={n:>6,}  acierto {100*p:5.2f} %"
              f"   IC95 [{100*(p-1.96*ee):5.2f}, {100*(p+1.96*ee):5.2f}]"
              f"{'   <<<' if p-1.96*ee > 0.50 else ''}")
F.to_csv("data/carrera_cierres.csv", index=False)
