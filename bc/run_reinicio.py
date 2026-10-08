import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd, reinicio as RE, nucleo as N

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,1.2),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.5),
       ("USDJPY","data/usdjpy_m1.parquet",0.01, 1.3),
       ("NAS100","data/nsxusd_m1.parquet",1.0,  1.5),
       ("SPX500","data/spxusd_m1.parquet",1.0,  0.6)]
datos = {}
for nom, ruta, u, co in INS:
    d = pd.read_parquet(ruta); d["ts"] = pd.to_datetime(d["ts"])
    datos[nom] = (d.sort_values("ts").reset_index(drop=True), u, co)

def corre(huso, lec, lrein, min_ctx=2):
    tot = []
    for nom, _, _, _ in INS:
        m1, u, co = datos[nom]
        t = RE.opera(m1, huso, lec, lrein, 1.0, u, co, min_ctx=min_ctx,
                     desde="2020-01-01", hasta="2024-01-01")
        if len(t): tot.append(t.assign(ins=nom))
    return pd.concat(tot, ignore_index=True) if tot else pd.DataFrame()

def linea(etq, T):
    if T.empty or len(T) < 2:
        print(f"   {etq:36s} n={len(T):>5}"); return None
    x = T.R_neto.to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x)); z = x.mean()/ee
    rec = float(np.mean(np.minimum(x, np.quantile(x,.99))))
    print(f"   {etq:36s} n={len(T):>5,} ({len(T)/4:>4.0f}/año) acierto {100*(T.R>0).mean():5.1f}% "
          f"bruta {T.R.mean():>+7.3f} NETA {x.mean():>+7.3f} "
          f"[{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}] z {z:>+5.2f}  recortada {rec:>+7.3f}")
    return dict(n=len(T), neta=float(x.mean()), z=float(z), rec=rec)

print("="*128)
print("LA REGLA DEL REINICIO · disparo de transición · desarrollo 2020-2023")
print("  PRINCIPAL, fijada en BC_05 §3 por argumento: huso UTC · lectura B · al menos 2 mayores alineadas")
print("="*128)
prim = corre("UTC","B","R1")
r1 = linea("UTC · B · reinicio R1 (simple)", prim)
prim2 = corre("UTC","B","R2")
r2 = linea("UTC · B · reinicio R2 (estricto)", prim2)

print("\n  secundarios · variando una cosa cada vez")
linea("con 1 sola mayor alineada", corre("UTC","B","R1",min_ctx=1))
linea("con las 3 mayores alineadas", corre("UTC","B","R1",min_ctx=3))

print("\n  las otras once celdas de la rejilla (secundarias)")
filas=[]
for huso in N.HUSOS:
    for lec in ("A","B","C"):
        if huso=="UTC" and lec=="B": continue
        T = corre(huso, lec, "R1")
        d = linea(f"{huso} · {lec}", T)
        if d: filas.append(dict(huso=huso, lec=lec, **d))

if r1:
    prim.to_csv("data/bc_reinicio_principal.csv", index=False)
    print("\n" + "="*128)
    print("VEREDICTO sobre la configuración principal (BC_05 §4)")
    ok_pot = r1["n"] >= 100
    ok = ok_pot and (r1["neta"] - 1.96*prim.R_neto.std(ddof=1)/np.sqrt(len(prim))) > 0
    print(f"   n = {r1['n']:,}   {'potencia suficiente' if ok_pot else 'INFRAPOTENCIADA (BC_05 §4.1): no se concluye nada'}")
    if ok_pot:
        print(f"   IC95 excluye el cero por arriba: {'SI' if ok else 'NO'}")
        print(f"\n   {'CONFIRMADA -> se abre 2024-2026' if ok else 'DESCARTADA -> 2024-2026 sigue cerrado'}")
