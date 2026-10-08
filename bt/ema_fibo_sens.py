"""Sensibilidad de EMA+Fibo a la ambiguedad dentro de la vela de entrada.

La vela que ejecuta la orden limitada puede tocar el objetivo Y el stop, y con
OHLC no se sabe en que orden. Hay tres tratamientos y la verdad esta entre
ellos:

  PESIMISTA   objetivo desde la vela siguiente, stop desde la misma  (el usado)
  NEUTRO      los dos desde la vela siguiente
  OPTIMISTA   los dos desde la misma vela                (el fallo original)

Ademas separa BRUTO y NETO, para saber si lo que mata es el coste o no hay nada.

  MODO=neutro python3 bt/ema_fibo_sens.py
"""
import os, itertools, numpy as np, pandas as pd
MODO = os.environ.get("MODO", "neutro")
exec(open("bt/ema_fibo.py").read().split("def evalua(")[0].replace(
     'NULOS = int(os.environ.get("NULOS", 10))', 'NULOS = 0'))

def evalua2(S, HL, fib, rr, modo):
    h, l = HL; n = len(h); B = []
    for i, lado, A, Bp in S:
        rec = abs(Bp-A)
        if rec < 5*U: continue
        ent = Bp - lado*rec*fib; stop = A; rgo = abs(ent-stop)
        if rgo < 3*U: continue
        tp = ent + lado*rgo*rr
        j0, j1 = i+1, min(i+1+VIDA, n)
        if j1 <= j0: continue
        hh, ll = h[j0:j1], l[j0:j1]
        e = np.flatnonzero(ll <= ent) if lado > 0 else np.flatnonzero(hh >= ent)
        if not len(e): continue
        k = e[0]
        ks, ko = {"pesimista": (k, k+1), "neutro": (k+1, k+1),
                  "optimista": (k, k)}[modo]
        st = (ll[ks:] <= stop) if lado > 0 else (hh[ks:] >= stop)
        ob = (hh[ko:] >= tp)   if lado > 0 else (ll[ko:] <= tp)
        b = np.flatnonzero(st); a = np.flatnonzero(ob)
        ia = a[0]+(ko-k) if len(a) else 10**9
        ib = b[0]+(ks-k) if len(b) else 10**9
        if ia == ib == 10**9: continue
        B.append((rr if ia < ib else -1.0, COSTE*U/rgo))
    return np.array(B)

out = []
for tf in TFS:
    E = agrega(d, tf)
    for per in EMAS:
        S, HL = senales(E, per)
        for fib, rr in itertools.product(FIBS, RRS):
            X = evalua2(S, HL, fib, rr, MODO)
            if len(X) < 60: continue
            g, nt = X[:,0], X[:,0]-X[:,1]
            out.append(dict(tf=tf, ema=per, fib=fib, rr=rr, n=len(X),
                bruto=float(g.mean()), zb=float(g.mean()/(g.std(ddof=1)/np.sqrt(len(g)))),
                neto=float(nt.mean()), zn=float(nt.mean()/(nt.std(ddof=1)/np.sqrt(len(nt)))),
                coste=float(X[:,1].mean())))
D = pd.DataFrame(out); D.to_csv(f"data/ema_fibo_{MODO}.csv", index=False)
print(f"=== MODO {MODO.upper()} · {len(D)} celdas ===")
print(f"  {'tf':>4} {'ema':>4} {'fib':>6} {'rr':>4} {'n':>6} {'BRUTO':>9} {'z':>7} "
      f"{'NETO':>9} {'z':>7} {'coste/R':>8}")
for _, r in D.sort_values("zb", ascending=False).head(6).iterrows():
    print(f"  {int(r.tf):4d} {int(r.ema):4d} {r.fib:6.3f} {r.rr:4.1f} {int(r.n):6d} "
          f"{r.bruto:+9.4f} {r.zb:+7.2f} {r.neto:+9.4f} {r.zn:+7.2f} {r.coste:8.3f}")
print(f"\n  BRUTO: mejor z {D.zb.max():+.2f} · celdas z>2 {int((D.zb>2).sum())}/{len(D)}"
      f" · z medio {D.zb.mean():+.2f}")
print(f"  NETO : mejor z {D.zn.max():+.2f} · celdas z>2 {int((D.zn>2).sum())}/{len(D)}")
print(f"  coste/riesgo mediano: {D.coste.median():.3f}  "
      f"(= {D.coste.median()*100:.1f} % de cada R se lo lleva el coste)")
