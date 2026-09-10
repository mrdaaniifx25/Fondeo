"""El filtro negativo del reinicio.  BC_05 §5.

  «Si en esa temporalidad que tenemos cerrada al alza se nos crea una reiniciada
   bajista, debemos protegernos, porque las demas temporalidades todavia no han
   cerrado y el precio nos esta mostrando que todavia tiene posibilidad de
   desplazarse en ambas direcciones.»

No es una regla de entrada sino de abstencion. Se mide sobre las operaciones ya
generadas en BC_04: las que se tomaron habiendo una reiniciada EN CONTRA, con
las mayores todavia sin rango creado, deberian rendir claramente peor.
"""
import sys; sys.path.insert(0, "bc")
import numpy as np, pandas as pd, nucleo as N, reinicio as RE

INS = {"EURUSD":"data/eurusd_m1.parquet","GBPUSD":"data/gbpusd_m1.parquet",
       "USDJPY":"data/usdjpy_m1.parquet","NAS100":"data/nsxusd_m1.parquet",
       "SPX500":"data/spxusd_m1.parquet"}

def marca(celda):
    huso, lec = celda.split("_")
    t = pd.read_csv(f"data/bc_{celda}.csv"); t["ts"] = pd.to_datetime(t.ts)
    out = []
    for nom, ruta in INS.items():
        sub = t[t.ins == nom]
        if sub.empty: continue
        m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").reset_index(drop=True)
        ej = RE.reiniciadas(N.velas(m1, 1, huso, 0), "R1")
        r = pd.DataFrame({"ts": ej["fin"].to_numpy(), "rein": ej["rein"].to_numpy()})
        # reiniciada EN CONTRA en la misma vela de entrada o en las 3 previas
        r["rein_prev"] = r.rein.rolling(4, min_periods=1).apply(
            lambda w: w[w != 0][-1] if (w != 0).any() else 0, raw=True)
        m = pd.merge_asof(sub.sort_values("ts"), r.sort_values("ts"),
                          on="ts", direction="backward")
        m["contra"] = (m.rein_prev != 0) & (np.sign(m.rein_prev) != np.sign(m.lado))
        out.append(m)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()

print("="*104)
print("FILTRO NEGATIVO DEL REINICIO · ¿rinden peor las operaciones tomadas con una")
print("reiniciada en contra?   umbral BC_05 §5: |z| > 2,58 sobre la DIFERENCIA")
print("="*104)
print(f"   {'celda':10s} {'con reinicio en contra':>26s} {'sin él':>16s} {'diferencia':>13s} {'z':>7s}")
difs = []
for celda in ("UTC_A","UTC_B","NY_A","NY_B","Madrid_A","Madrid_B","Broker_A","Broker_B"):
    try: t = marca(celda)
    except FileNotFoundError: continue
    if t.empty: continue
    a = t[t.contra].R_neto; b = t[~t.contra].R_neto
    if len(a) < 40 or len(b) < 40:
        print(f"   {celda:10s} n={len(a)} / {len(b)}  (pocas)"); continue
    se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    d = a.mean() - b.mean(); difs.append(d)
    print(f"   {celda:10s} {a.mean():>+13.3f} (n={len(a):>5,}) {b.mean():>+9.3f} (n={len(b):>5,})"
          f" {d:>+13.3f} {d/se:>+7.2f}{'  <<<' if abs(d/se) > 2.58 else ''}")
if difs:
    d = np.array(difs)
    print(f"\n   resumen por celda: media {d.mean():+.3f}   {int((d<0).sum())} de {len(d)} negativas")
    print(f"   (su filtro predice NEGATIVO: las operaciones con reiniciada en contra deberían ser peores)")
