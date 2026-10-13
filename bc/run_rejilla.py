"""La rejilla entera sobre 2020-2023. Doce celdas, todas reportadas.

La calibracion no discrimino (BC_04), asi que segun BC_02 §11 fase 2 se reporta
todo y se dice cuantas celdas se han probado. Con 12 celdas el umbral honesto
por Bonferroni es |z| > 2,87, no 1,96.
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd, motor as M, nucleo as N

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,1.2),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.5),
       ("USDJPY","data/usdjpy_m1.parquet",0.01, 1.3),
       ("NAS100","data/nsxusd_m1.parquet",1.0,  1.5),
       ("SPX500","data/spxusd_m1.parquet",1.0,  0.6)]
DESDE, HASTA = "2020-01-01", "2024-01-01"

datos = {}
for nom, ruta, u, co in INS:
    d = pd.read_parquet(ruta); d["ts"] = pd.to_datetime(d["ts"])
    datos[nom] = (d.sort_values("ts").reset_index(drop=True), u, co)

print("="*112)
print("REJILLA COMPLETA · desarrollo 2020-2023 · RR>=3 · colchon 1 tick · 12 celdas")
print("  guarda de ejecutabilidad: el stop tiene que estar a >= 3x el coste")
print("  umbral honesto con 12 contrastes: |z| > 2,87")
print("="*112)
print(f"{'huso':8s} {'lec':4s} {'n':>6s} {'ops/año':>8s} {'aciertos':>9s} "
      f"{'R bruta':>9s} {'R neta':>9s} {'IC95 neta':>20s} {'z':>7s}")
print("-"*112)

filas = []
for huso in N.HUSOS:
    for lec in ("A","B","C"):
        tot = []
        for nom, ruta, u, co in INS:
            m1, u, co = datos[nom]
            t = M.opera(m1, huso, lec, colchon=1.0, unidad=u, coste=co,
                        desde=DESDE, hasta=HASTA)
            if len(t): tot.append(t.assign(ins=nom))
        if not tot:
            print(f"{huso:8s} {lec:4s} {'0':>6s}   (sin operaciones)"); continue
        T = pd.concat(tot, ignore_index=True)
        x = T.R_neto.to_numpy()
        if len(x) < 2: continue
        ee = x.std(ddof=1)/np.sqrt(len(x)); z = x.mean()/ee
        # cuanto de la media la sostiene la cola: media recortada al 1 % superior
        rec = float(np.mean(np.minimum(x, np.quantile(x, 0.99))))
        marca = "  <<<" if z > 2.87 else ""
        print(f"{huso:8s} {lec:4s} {len(T):>6,} {len(T)/4:>8.0f} "
              f"{100*(T.R>0).mean():>8.1f}% {T.R.mean():>+9.3f} {x.mean():>+9.3f} "
              f"[{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}] {z:>+7.2f}{marca}")
        filas.append(dict(huso=huso, lectura=lec, n=len(T), bruta=T.R.mean(),
                          neta=x.mean(), neta_rec=rec, z=z, aciertos=(T.R>0).mean(),
                          riesgo=T.riesgo_u.median(), rr=T.rr.median()))
        T.to_csv(f"data/bc_{huso}_{lec}.csv", index=False)

R = pd.DataFrame(filas)
R.to_csv("data/bc_rejilla.csv", index=False)
print("\n" + "="*112)
if R.empty:
    print("Ninguna celda produce operaciones.")
else:
    print(f"celdas con n>=100 (BC_03 §4.1, umbral de potencia): "
          f"{int((R.n>=100).sum())} de {len(R)}")
    print(f"celdas que superan |z|>2,87:  {int((R.z>2.87).sum())}")
    print(f"\nrango de n: {R.n.min():,} a {R.n.max():,}   "
          f"mediana de operaciones por celda: {R.n.median():,.0f}")
    print("\n¿cuanto de cada media la sostiene el 1 % superior?  (neta vs neta recortada)")
    for r in R.sort_values("neta", ascending=False).itertuples():
        print(f"   {r.huso:8s} {r.lectura}   neta {r.neta:+7.3f}   recortada {r.neta_rec:+7.3f}"
              f"   riesgo mediano {r.riesgo:5.1f}   R:R mediano {r.rr:6.1f}")
