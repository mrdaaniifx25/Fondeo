"""Afinado de la GEOMETRIA (no de la senal) y validacion fuera de muestra.

El pase grueso demostro que la geometria decide P(pasar). Esto la afina en
2020-2023 y comprueba el resultado en 2024-2026, que no se ha tocado.
La entrada es siempre la misma compra ciega: no hay senal que optimizar.
"""
import os, itertools, numpy as np, pandas as pd
os.environ.setdefault("SIMS","20000")
exec(open("bt/alto_winrate.py").read().split("# ---------------------------------------------------------------- pase")[0])

TOPE  = int(os.environ.get("TOPE", 10))        # micros maximos de la prop firm
NOM   = os.environ.get("NOM", "NASDAQ")
ruta, DPP, CPTS = INSTR[NOM]
S = sesiones(ruta)
rango = float(np.median([hh.max()-ll.min() for _,_,_,hh,ll,_ in S]))
print(f"{NOM} · {len(S)} sesiones · rango diario mediano {rango:.1f} pts "
      f"· coste {CPTS:.2f} pts · tope {TOPE} micros\n")

SLF  = (0.35, 0.50, 0.75, 1.00)
RR   = (1.0, 1.5, 2.0, 3.0, 5.0)               # SL/TP
PHI  = (0.25, 0.35, 0.50, 0.65, 0.80, 1.00)

# precalcula el resultado bruto en puntos de cada dia para cada (slf, rr)
crudo = {}
for f, r in itertools.product(SLF, RR):
    sl = f*rango; tp = sl/r
    v = []
    for dia, mm, oo, hh, ll, cc in S:
        k5 = int(np.searchsorted(mm, 9*60+35))
        if k5 >= len(mm)-10: continue
        _, g = resuelve(hh, ll, cc, k5, float(oo[k5]), tp, sl, +1)
        v.append((dia.year, g-CPTS))
    crudo[(f,r)] = pd.DataFrame(v, columns=["anio","pnl"])

filas = []
for (f, r), T in crudo.items():
    sl = f*rango; tp = sl/r
    for phi in PHI:
        ctr = int(round(phi*DD/(sl*DPP)))
        if ctr < 1 or ctr > TOPE: continue
        A = T[T.anio <= 2023].pnl.to_numpy()*ctr*DPP     # ajuste
        B = T[T.anio >= 2024].pnl.to_numpy()*ctr*DPP     # fuera de muestra
        pa,_ = evalua(A,"dinamico"); pb,db = evalua(B,"dinamico")
        ea,_ = evalua(A,"estatico"); eb,_  = evalua(B,"estatico")
        filas.append(dict(slf=f, rr=r, phi=phi, ctr=ctr, sl=sl, tp=tp,
                          riesgo=sl*ctr*DPP, premio=tp*ctr*DPP,
                          din_ajuste=pa, din_fuera=pb,
                          est_ajuste=ea, est_fuera=eb,
                          usd_ajuste=float(A.mean()), usd_fuera=float(B.mean()),
                          dias=db))
D = pd.DataFrame(filas).sort_values("din_ajuste", ascending=False)
D.to_csv(f"data/alto_winrate_optimo_{NOM}.csv", index=False)

print("  las 10 mejores segun 2020-2023, y lo que hicieron en 2024-2026")
print(f"  {'stop':>6} {'TP':>6} {'x':>3} {'riesgo':>7} {'premio':>7} "
      f"{'AJUSTE din':>11} {'FUERA din':>10} {'FUERA est':>10} {'$/op':>8} {'dias':>5}")
for _, r in D.head(10).iterrows():
    print(f"  {r.sl:6.1f} {r.tp:6.1f} {int(r.ctr):3d} {r.riesgo:7.0f} {r.premio:7.0f} "
          f"{r.din_ajuste*100:10.1f}% {r.din_fuera*100:9.1f}% {r.est_fuera*100:9.1f}% "
          f"{r.usd_fuera:+8.2f} {r.dias:5.0f}")
c = np.corrcoef(D.din_ajuste, D.din_fuera)[0,1]
print(f"\n  correlacion ajuste-fuera de muestra sobre las {len(D)} celdas: {c:+.3f}")
print(f"  mejor en ajuste: {D.iloc[0].din_ajuste*100:.1f} %  ->  "
      f"fuera de muestra {D.iloc[0].din_fuera*100:.1f} %")
print(f"  mejor DEL FUERA de muestra (inalcanzable a priori): "
      f"{D.din_fuera.max()*100:.1f} %")
