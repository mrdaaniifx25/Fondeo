"""POTENCIA por OPERACION: cual es la ventaja minima detectable en las entradas reales.

Complementa docs/SUELO_DE_DETECCION.md, que calcula el suelo en Sharpe sobre
meses. Aqui el suelo se calcula en puntos de acierto sobre OPERACIONES reales.
La calibracion del motor ya estaba hecha: bt/valida_motor.py (no fabrica
ventajas) y bt/control_positivo.py (no las destruye), docs/VALIDACION_motor.md.

  1 inyecta ventajas de tamanio CONOCIDO en las operaciones reales y comprueba
    si mi estadistico las recupera, y a partir de que tamanio.
  2 mide el SESGO DE EMPATE del motor de resolucion: cuando stop y objetivo
    caen en el mismo minuto, el motor da por perdida la operacion.
  3 recalcula con costes de broker ECN real en vez de los que uso.

  python3 bt/control_positivo.py
"""
import numpy as np, pandas as pd
from math import sqrt, erf
rng = np.random.default_rng(20261008)

INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 1.43, 0.70),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 35.0, 12.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  1.6,  0.8)]
HOR = 2 * 1440

def barrido_m15(M):
    """Entradas reales: barrido de la vela M15 anterior + cierre de vuelta dentro.
    Es la forma de operacion mas repetida de todo el proyecto."""
    t = (M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York")
          .dt.tz_localize(None))
    k = t.dt.floor("15min")
    q = M.assign(k=k).groupby("k", sort=True).agg(
        o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"))
    q = q[q.index.notna()]
    ph, pl = q.h.shift(1).to_numpy(), q.l.shift(1).to_numpy()
    H, L, C = q.h.to_numpy(), q.l.to_numpy(), q.c.to_numpy()
    up = (L <= pl) & (C > pl) & (C < ph) & (H < ph)
    dn = (H >= ph) & (C < ph) & (C > pl) & (L > pl)
    s = np.where(up, 1, np.where(dn, -1, 0)).astype(np.int8)
    fin = M.assign(k=k).groupby("k", sort=True).apply(
        lambda d: d.index[-1], include_groups=False).reindex(q.index).to_numpy()
    return q, s, fin, L, H

def ops(nom, ruta, U, coste, ecn):
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    q, s, fin, L15, H15 = barrido_m15(M)
    HH, LL, OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()
    ts = M.ts.to_numpy()
    out = []
    for i in np.nonzero(s)[0]:
        j = int(fin[i]); e = j + 1
        if e >= len(M): continue
        lado = int(s[i])
        ent = OO[e]
        mecha = L15[i] if lado > 0 else H15[i]
        rgo = (ent - mecha) * lado
        if rgo <= 0: continue
        rec = 2.0 * rgo                      # objetivo fijo a 2R
        a, b = e, min(e + HOR, len(M))
        hh, ll = HH[a:b], LL[a:b]
        # resolucion para AMBOS lados sobre la misma geometria
        res = {}
        for sg in (1, -1):
            if sg > 0:
                ks = np.nonzero(ll <= ent - rgo)[0]; kt = np.nonzero(hh >= ent + rec)[0]
            else:
                ks = np.nonzero(hh >= ent + rgo)[0]; kt = np.nonzero(ll <= ent - rec)[0]
            fs = ks[0] if len(ks) else 10**9
            ft = kt[0] if len(kt) else 10**9
            res[sg] = (2.0 if ft < fs else (-1.0 if fs < 10**9 else 0.0), fs, ft)
        emp = int(res[1][1] == res[1][2] < 10**9) + int(res[-1][1] == res[-1][2] < 10**9)
        out.append((nom, ts[e], lado, rgo/U, res[1][0], res[-1][0], emp,
                    coste/(rgo/U), ecn/(rgo/U)))
    return pd.DataFrame(out, columns="ins ts lado rgo Rlargo Rcorto empates cr crecn".split())

T = pd.concat([ops(*a) for a in INS], ignore_index=True)
T["dia"] = pd.to_datetime(T.ts).dt.floor("D")
T["gr"] = T.ins + T.dia.astype(str)
T["Rreal"] = np.where(T.lado > 0, T.Rlargo, T.Rcorto)
T["mej"] = T[["Rlargo","Rcorto"]].max(axis=1)
T["peo"] = T[["Rlargo","Rcorto"]].min(axis=1)
print(f"operaciones reales usadas: {len(T):,}  ({T.ins.value_counts().to_dict()})")
print(f"riesgo mediano: {T.rgo.median():.1f}  ·  objetivo 2R  ·  coste/riesgo medio "
      f"{100*T.cr.mean():.1f} % (mio)  {100*T.crecn.mean():.1f} % (ECN)\n")

def z(x, gr):
    m = x.mean()
    su = pd.DataFrame({"x": x.to_numpy(), "g": gr.to_numpy()}).groupby("g").x.apply(
        lambda v: (v - m).sum())
    s2 = float((su ** 2).sum())
    return m * len(x) / sqrt(s2) if s2 > 0 else float("nan")

print("="*92)
print("1 · CONTROL POSITIVO: inyecto ventajas de tamanio conocido")
print("="*92)
print("  Cada operacion tiene dos desenlaces reales (largo y corto) sobre la MISMA")
print("  geometria. Un operador con habilidad h elige el lado bueno con probabilidad h.")
print("  h = 0,50 es no tener ninguna ventaja.\n")
base = 0.5
geo = (T.rgo/(T.rgo + 2*T.rgo)).mean()
print(f"{'habilidad':>10}{'pp sobre azar':>15}{'acierto':>9}{'R/op BRUTA':>12}{'z':>8}"
      f"{'R/op NETA':>12}{'z':>8}{'detectada?':>12}")
for h in (0.500, 0.505, 0.510, 0.520, 0.540, 0.560, 0.600):
    reps = []
    for _ in range(40):
        pick = rng.random(len(T)) < h
        r = pd.Series(np.where(pick, T.mej.to_numpy(), T.peo.to_numpy()))
        reps.append((r.mean(), z(r, T.gr), (r - T.cr.to_numpy()).mean(),
                     z(r - T.cr.to_numpy(), T.gr), (r > 0).mean()))
    a = np.mean(reps, axis=0)
    print(f"{h:>10.3f}{100*(h-base):>14.1f}pp{100*a[4]:>8.1f}%{a[0]:>+12.4f}{a[1]:>+8.2f}"
          f"{a[2]:>+12.4f}{a[3]:>+8.2f}{('SI' if a[3] > 2 else 'no'):>12}")

# ventaja minima detectable: busca la h donde la z NETA cruza +2
lo, hi = 0.50, 0.75
for _ in range(28):
    mid = (lo + hi)/2
    zz = np.mean([z(pd.Series(np.where(rng.random(len(T)) < mid, T.mej.to_numpy(),
                   T.peo.to_numpy())) - T.cr.to_numpy(), T.gr) for _ in range(25)])
    lo, hi = (lo, mid) if zz > 2 else (mid, hi)
hmin = (lo + hi)/2
print(f"\n  VENTAJA MINIMA DETECTABLE con {len(T):,} operaciones, z>+2 en NETA:")
print(f"    habilidad {hmin:.4f}  =  {100*(hmin-base):+.2f} pp sobre el azar")
print(f"    por debajo de eso, una ventaja REAL habria salido 'no significativa'.")

print("\n" + "="*92)
print("2 · SESGO DE EMPATE del motor de resolucion")
print("="*92)
tot = len(T)*2
print(f"  veces que stop y objetivo caen en el MISMO minuto: {int(T.empates.sum()):,}"
      f" de {tot:,} resoluciones = {100*T.empates.sum()/tot:.2f} %")
print(f"  el motor las resuelve siempre como PERDIDA (sesgo pesimista)")
opt = T.Rreal.copy()
emp1 = (T.lado > 0) & (T.empates > 0)
alt = T.Rreal.where(T.empates == 0, 2.0)      # optimista: las dudosas ganan
print(f"  R/op con el motor actual (pesimista): {T.Rreal.mean():+.4f}")
print(f"  R/op dando por ganadas las dudosas  : {alt.mean():+.4f}"
      f"   diferencia {alt.mean()-T.Rreal.mean():+.4f}")

print("\n" + "="*92)
print("3 · COSTE: el mio contra uno de broker ECN real")
print("="*92)
print(f"{'':<22}{'coste/riesgo':>14}{'R/op NETA':>12}{'z':>8}{'umbral acierto':>16}")
for et, c in (("el que uso", T.cr), ("ECN realista", T.crecn)):
    n = T.Rreal - c
    um = 100*(1 + c.mean())/3
    print(f"  {et:<20}{100*c.mean():>13.1f}%{n.mean():>+12.4f}{z(n, T.gr):>+8.2f}{um:>15.1f}%")
print(f"  acierto real de la senal: {100*(T.Rreal > 0).mean():.1f}%   "
      f"nulo geometrico: {100*geo:.1f}%")
