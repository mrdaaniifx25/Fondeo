"""BC_09 · la temporalidad de ejecucion. Todo igual menos donde se busca la entrada."""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd, motor as M

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,1.2),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.5),
       ("USDJPY","data/usdjpy_m1.parquet",0.01, 1.3),
       ("NAS100","data/nsxusd_m1.parquet",1.0,  1.5),
       ("SPX500","data/spxusd_m1.parquet",1.0,  0.6)]
EJEC = [("1H", 1.0), ("15M", 0.25), ("10M", 1/6), ("5M", 1/12)]
DESDE, HASTA = "2020-01-01", "2024-01-01"
rng = np.random.default_rng(20260827)

def ee_bloques(x, largo=20, reps=3000):
    n = len(x)
    if n < largo*3: return x.std(ddof=1)/np.sqrt(n)
    nb = int(np.ceil(n/largo))
    ini = rng.integers(0, n-largo+1, size=(reps, nb))
    idx = (ini[:,:,None] + np.arange(largo)[None,None,:]).reshape(reps,-1)[:,:n]
    return float(x[idx].mean(axis=1).std(ddof=1))

datos = {}
for nom, ruta, u, co in INS:
    d = pd.read_parquet(ruta); d["ts"] = pd.to_datetime(d["ts"])
    datos[nom] = d.sort_values("ts").reset_index(drop=True)

print("="*118)
print("BC_09 · TEMPORALIDAD DE EJECUCION · contexto 1D/12H/4H · lectura B · RR>=3 · 2020-2023")
print("   umbral pre-registrado: |z| > 3,3   (Bonferroni 20 celdas x factor 1,1 de BC_08)")
print("="*118)
print(f"{'ejec':6s} {'n':>7s} {'ops/año':>8s} {'riesgo':>8s} {'R:R':>7s} {'%TP':>7s} "
      f"{'coste en R':>11s} {'R bruta':>9s} {'R neta':>9s} {'z bloq':>8s} {'recortada':>10s}")
print("-"*118)

res = []
for nom_e, h in EJEC:
    tot = []
    for nom, ruta, u, co in INS:
        t = M.opera(datos[nom], "Madrid", "B", colchon=1.0, unidad=u, coste=co,
                    desde=DESDE, hasta=HASTA, ejec_h=h)
        if len(t): tot.append(t.assign(ins=nom, coste_R=co/t.riesgo_u))
    if not tot:
        print(f"{nom_e:6s} sin operaciones"); continue
    T = pd.concat(tot, ignore_index=True).sort_values("ts")
    x = T.R_neto.to_numpy()
    ee = ee_bloques(x); z = x.mean()/ee
    rec = float(np.mean(np.minimum(x, np.quantile(x, 0.99))))
    marca = "  <<<" if z > 3.3 else ""
    print(f"{nom_e:6s} {len(T):>7,} {len(T)/4:>8.0f} {T.riesgo_u.median():>7.1f}u "
          f"{T.rr.median():>7.1f} {100*(T.motivo=='TP').mean():>6.1f}% "
          f"{100*T.coste_R.median():>10.1f}% {T.R.mean():>+9.3f} {x.mean():>+9.3f} "
          f"{z:>+8.2f} {rec:>+10.3f}{marca}")
    res.append(dict(ejec=nom_e, n=len(T), riesgo=T.riesgo_u.median(), rr=T.rr.median(),
                    tp=(T.motivo=='TP').mean(), coste=T.coste_R.median(),
                    bruta=T.R.mean(), neta=x.mean(), z=z, rec=rec))
    T.to_csv(f"data/bc09_{nom_e}.csv", index=False)

R = pd.DataFrame(res)
R.to_csv("data/bc09_ejecucion.csv", index=False)
print("\n" + "="*118)
print("LAS CINCO PREDICCIONES DE BC_09")
if len(R) >= 2:
    mono = lambda s: "SÍ" if all(a < b for a, b in zip(s, s[1:])) else "NO"
    print(f"  1 · el R:R bruto sube al bajar de temporalidad ........ {mono(list(R.rr))}"
          f"   ({' → '.join(f'{v:.1f}' for v in R.rr)})")
    print(f"  2 · la tasa de aciertos baja ......................... "
          f"{'SÍ' if all(a>b for a,b in zip(R.tp,R.tp[1:])) else 'NO'}"
          f"   ({' → '.join(f'{100*v:.1f}%' for v in R.tp)})")
    print(f"  3 · el coste en R sube ............................... {mono(list(R.coste))}"
          f"   ({' → '.join(f'{100*v:.0f}%' for v in R.coste)})")
    print(f"  4 · el neto EMPEORA al bajar ......................... "
          f"{'SÍ' if all(a>b for a,b in zip(R.neta,R.neta[1:])) else 'NO'}"
          f"   ({' → '.join(f'{v:+.3f}' for v in R.neta)})")
    print(f"  5 · la R bruta se queda entre +0,05 y +0,20 .......... "
          f"{'SÍ' if R.bruta.between(0.05,0.20).all() else 'NO'}"
          f"   ({' → '.join(f'{v:+.3f}' for v in R.bruta)})")
    print()
    mejor = R.loc[R.neta.idxmax()]
    if mejor.ejec != "1H" and mejor.neta > R.neta.iloc[0]:
        print(f"  >> EL NETO MEJORA AL BAJAR. Mejor celda: {mejor.ejec} con {mejor.neta:+.3f}.")
        print("     Es el resultado que segun BC_09 obliga a replantear el enfoque entero.")
    else:
        print("  >> El neto NO mejora al bajar: la prediccion se cumple y el enfoque aguanta.")
