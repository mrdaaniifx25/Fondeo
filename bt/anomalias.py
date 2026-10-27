"""Anomalias de horario y calendario publicadas en la literatura academica.

Preregistro sellado en docs/PREREGISTRO_anomalias.md (commit 748ab3a).

  H1  la noche (cierre -> apertura) frente al dia (apertura -> cierre)
  H2  la ventana 02:00-03:00 NY, que el propio NY Fed dice que murio en 2021
  H3  cambio de mes
  H4  la noche que sigue a un dia bajista

Placebos: EURUSD y XAUUSD, donde el mecanismo NO deberia existir.

  python3 bt/anomalias.py
"""
import numpy as np, pandas as pd

# instrumento -> (ruta, zona horaria de la sesion, apertura, cierre, es indice)
INSTR = {
 "NASDAQ": ("data/nsxusd_m1.parquet", "America/New_York",  9*60+30, 16*60, True),
 "SP500":  ("data/spxusd_m1.parquet", "America/New_York",  9*60+30, 16*60, True),
 "GER40":  ("data/grxeur_m1.parquet", "Europe/Berlin",     9*60,    17*60+30, True),
 "EURUSD": ("data/eurusd_m1.parquet", "America/New_York",  9*60+30, 16*60, False),
 "XAUUSD": ("data/xauusd_m1.parquet", "America/New_York",  9*60+30, 16*60, False),
}

def carga(nom):
    ruta, tz, ini, fin, _ = INSTR[nom]
    d = pd.read_parquet(ruta)
    d["ts"] = pd.to_datetime(d["ts"])
    loc = d.ts.dt.tz_localize("UTC").dt.tz_convert(tz).dt.tz_localize(None)
    ny  = d.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    d["m"]   = loc.dt.hour*60 + loc.dt.minute
    d["dia"] = loc.dt.date
    d["dow"] = loc.dt.dayofweek
    d["mny"] = ny.dt.hour*60 + ny.dt.minute
    d["dny"] = ny.dt.date
    d = d[d.dow < 5]
    # --- sesion de contado: apertura y cierre de cada dia
    s = d[(d.m >= ini) & (d.m <= fin)]
    g = s.groupby("dia").agg(ap=("open","first"), ci=("close","last"), n=("close","size"))
    g = g[g.n >= 120].reset_index()
    g["dia"] = pd.to_datetime(g.dia)
    # --- ventana 02:00-03:00 NY, indexada al dia de NY siguiente
    w = d[(d.mny >= 120) & (d.mny < 180)]
    gw = w.groupby("dny").agg(wa=("open","first"), wc=("close","last"), nw=("close","size"))
    gw = gw[gw.nw >= 30].reset_index(); gw["dia"] = pd.to_datetime(gw.dny)
    g = g.merge(gw[["dia","wa","wc"]], on="dia", how="left")
    # --- rendimientos, en % sobre el precio
    g["dia_r"]   = (g.ci/g.ap - 1)*100                       # apertura -> cierre
    g["noche_r"] = (g.ap/g.ci.shift(1) - 1)*100              # cierre previo -> apertura
    g["vent_r"]  = (g.wc/g.wa - 1)*100                       # 02:00 -> 03:00 NY
    # un tick corrupto en el GER40 (2023-12-04) daba +271 % de noche: se anula
    # cualquier salto de mas del 15 %, que no es un movimiento, es un error
    for c in ("dia_r","noche_r","vent_r"):
        g.loc[g[c].abs() > 15, c] = np.nan
    g["anio"]    = g.dia.dt.year
    g["mes"]     = g.dia.dt.to_period("M")
    # --- cambio de mes: ultimo dia habil del mes + los 3 primeros del siguiente
    idx = np.arange(len(g))
    ult = g.groupby("mes").apply(lambda x: x.index[-1], include_groups=False).to_numpy()
    tom = np.zeros(len(g), bool)
    for u in ult:
        tom[u] = True
        for k in (1,2,3):
            if u+k < len(g): tom[u+k] = True
    g["tom"] = tom
    return g.dropna(subset=["dia_r"]).reset_index(drop=True)

def z(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    return (x.mean()/(x.std(ddof=1)/np.sqrt(len(x))) if len(x) > 2 else np.nan), len(x)

def zdif(a, b):
    a = np.asarray(a,float); a = a[~np.isnan(a)]
    b = np.asarray(b,float); b = b[~np.isnan(b)]
    s = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    return (a.mean()-b.mean())/s, a.mean()-b.mean()

G = {k: carga(k) for k in INSTR}
IDX = [k for k in INSTR if INSTR[k][4]]
PLA = [k for k in INSTR if not INSTR[k][4]]

print("=" * 78)
print("H1 · LA NOCHE FRENTE AL DIA        (rendimiento medio diario, en %)")
print("=" * 78)
print(f"  {'instr':8s} {'n':>5} {'NOCHE':>9} {'z':>7} {'DIA':>9} {'z':>7} "
      f"{'dif':>9} {'z dif':>7}")
for k in IDX + PLA:
    g = G[k]; zn,n = z(g.noche_r); zd,_ = z(g.dia_r); zz,df = zdif(g.noche_r, g.dia_r)
    et = "" if k in IDX else "   <- placebo"
    print(f"  {k:8s} {n:5d} {np.nanmean(g.noche_r):+9.4f} {zn:+7.2f} "
          f"{np.nanmean(g.dia_r):+9.4f} {zd:+7.2f} {df:+9.4f} {zz:+7.2f}{et}")
todo_n = np.concatenate([G[k].noche_r.to_numpy() for k in IDX])
todo_d = np.concatenate([G[k].dia_r.to_numpy()   for k in IDX])
zz, df = zdif(todo_n, todo_d)
print(f"  {'AGREGADO':8s} {len(todo_n):5d} {np.nanmean(todo_n):+9.4f} "
      f"{z(todo_n)[0]:+7.2f} {np.nanmean(todo_d):+9.4f} {z(todo_d)[0]:+7.2f} "
      f"{df:+9.4f} {zz:+7.2f}")

print("\n  por anio, agregando los tres indices:")
print(f"  {'anio':>6} {'NOCHE':>9} {'z':>7} {'DIA':>9} {'z':>7}")
A = pd.concat([G[k][["anio","noche_r","dia_r"]] for k in IDX])
for y, x in A.groupby("anio"):
    print(f"  {y:>6} {np.nanmean(x.noche_r):+9.4f} {z(x.noche_r)[0]:+7.2f} "
          f"{np.nanmean(x.dia_r):+9.4f} {z(x.dia_r)[0]:+7.2f}")

print("\n" + "=" * 78)
print("H2 · LA VENTANA 02:00-03:00 NY     (predigo que esta MUERTA desde 2021)")
print("=" * 78)
print(f"  {'instr':8s} {'periodo':>12} {'n':>5} {'media':>9} {'z':>7} {'anualiz.':>9}")
for k in IDX:
    g = G[k]
    for et, m in (("2020-2021", g.anio<=2021), ("2022-2026", g.anio>=2022)):
        v = g.vent_r[m]; zv,n = z(v)
        print(f"  {k:8s} {et:>12} {n:5d} {np.nanmean(v):+9.4f} {zv:+7.2f} "
              f"{np.nanmean(v)*252:+8.2f} %")

print("\n" + "=" * 78)
print("H3 · CAMBIO DE MES                 (dia completo: noche + sesion)")
print("=" * 78)
print(f"  {'instr':8s} {'n TOM':>6} {'TOM':>9} {'resto':>9} {'dif':>9} {'z dif':>7}")
for k in IDX + PLA:
    g = G[k]; tot = g.noche_r.fillna(0) + g.dia_r
    a, b = tot[g.tom], tot[~g.tom]; zz, df = zdif(a, b)
    et = "" if k in IDX else "   <- placebo"
    print(f"  {k:8s} {len(a):6d} {a.mean():+9.4f} {b.mean():+9.4f} "
          f"{df:+9.4f} {zz:+7.2f}{et}")
TA = pd.concat([pd.DataFrame(dict(t=G[k].tom, r=G[k].noche_r.fillna(0)+G[k].dia_r)) for k in IDX])
zz, df = zdif(TA.r[TA.t], TA.r[~TA.t])
print(f"  {'AGREGADO':8s} {int(TA.t.sum()):6d} {TA.r[TA.t].mean():+9.4f} "
      f"{TA.r[~TA.t].mean():+9.4f} {df:+9.4f} {zz:+7.2f}")

print("\n" + "=" * 78)
print("H4 · LA NOCHE QUE SIGUE A UN DIA BAJISTA")
print("=" * 78)
print(f"  {'instr':8s} {'n baja':>7} {'tras BAJA':>10} {'tras SUBE':>10} "
      f"{'dif':>9} {'z dif':>7}")
for k in IDX + PLA:
    g = G[k]
    sig = g.noche_r.shift(-1)                    # la noche que viene DESPUES
    baj = g.dia_r < 0
    a, b = sig[baj], sig[~baj]; zz, df = zdif(a, b)
    et = "" if k in IDX else "   <- placebo"
    print(f"  {k:8s} {int(baj.sum()):7d} {np.nanmean(a):+10.4f} {np.nanmean(b):+10.4f} "
          f"{df:+9.4f} {zz:+7.2f}{et}")
QA = []
for k in IDX:
    g = G[k]; QA.append(pd.DataFrame(dict(b=(g.dia_r<0).to_numpy(),
                                          s=g.noche_r.shift(-1).to_numpy())))
QA = pd.concat(QA); zz, df = zdif(QA.s[QA.b], QA.s[~QA.b])
print(f"  {'AGREGADO':8s} {int(QA.b.sum()):7d} {np.nanmean(QA.s[QA.b]):+10.4f} "
      f"{np.nanmean(QA.s[~QA.b]):+10.4f} {df:+9.4f} {zz:+7.2f}")
