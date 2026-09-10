"""Secundario 3, el que mas importa: ¿se replica el hallazgo del cuerpo de la
vela en datos nuevos? Hasta ahora solo estaba confirmado hacia atras.

  python3 bt/examen5_cuerpo.py
"""
import json, numpy as np, pandas as pd
from math import comb
def fisher(a,b,c,d):
    n,r1,c1 = a+b+c+d, a+b, a+c
    if min(a,b,c,d) < 0 or n == 0: return 1.0
    D = lambda k: comb(r1,k)*comb(n-r1,c1-k)/comb(n,c1)
    p0 = D(a)*(1+1e-9)
    return sum(D(k) for k in range(max(0,c1-(n-r1)), min(r1,c1)+1) if D(k) <= p0)

TZ, U, INI = "Europe/Madrid", 1e-4, 480
o = pd.read_csv("data/examen5_ops.csv"); o["dia"] = pd.to_datetime(o.dia).dt.date
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(set(o.dia))].reset_index(drop=True)

fil = []
for r in o.itertuples(index=False, name=None):
    r = dict(zip(o.columns, r))
    d1 = m1[m1.dia == r["dia"]]
    a = d1[d1["min"] < INI]
    if len(a) < 300: fil.append((np.nan, False)); continue
    hi, lo = float(a.high.max()), float(a.low.min())
    cm = (int(r["min"]) // 5)*5              # ultima vela de M5 ya cerrada
    v = d1[(d1["min"] >= cm-5) & (d1["min"] < cm)]
    if len(v) < 3: fil.append((np.nan, False)); continue
    o5, h5, l5, c5 = (float(v.open.iloc[0]), float(v.high.max()),
                      float(v.low.min()), float(v.close.iloc[-1]))
    rango = max(h5-l5, 1e-9)
    fil.append((abs(c5-o5)/rango*100, bool(l5 <= hi <= h5 or l5 <= lo <= h5)))
o["cuerpo_pct"] = [f[0] for f in fil]
o["toca"] = [f[1] for f in fil]
o = o.dropna(subset=["cuerpo_pct"])
o["lleno"] = o.cuerpo_pct >= 60
o["res"] = o.mot.isin(["TP","SL"])
ac = lambda s: 100*(s[s.res].mot=="TP").mean() if s.res.any() else float("nan")
def fs(a, b):
    ra, rb = a[a.res], b[b.res]
    return fisher(int((ra.mot=="TP").sum()), int((ra.mot=="SL").sum()),
                  int((rb.mot=="TP").sum()), int((rb.mot=="SL").sum()))

print("="*74)
print("SECUNDARIO 3 · ¿SE REPLICA EL HALLAZGO DEL CUERPO?")
print("="*74)
print(f"  {len(o)} operaciones con contexto\n")
print(f"  {'cuerpo / rango':22s} {'n':>4s} {'acierto':>9s} {'R neta':>9s}   bloques 1-4")
print("  " + "-"*64)
PREV = {"0-20 %":80.8, "20-40 %":77.3, "40-60 %":76.5, "60-80 %":56.8, "80-100 %":39.1}
for (lo_, hi_), et in (((0,20),"0-20 %"), ((20,40),"20-40 %"), ((40,60),"40-60 %"),
                       ((60,80),"60-80 %"), ((80,101),"80-100 %")):
    s = o[(o.cuerpo_pct >= lo_) & (o.cuerpo_pct < hi_)]
    if not len(s): continue
    print(f"  {et:22s} {len(s):4d} {ac(s):8.1f}% {s.neta.mean():+9.3f}   {PREV[et]:8.1f} %")
a, b = o[o.lleno], o[~o.lleno]
print("\n  " + "-"*64)
print(f"  {'CUERPO LLENO (>=60 %)':22s} {len(a):4d} {ac(a):8.1f}% {a.neta.mean():+9.3f}   "
      f"{'50,0 %':>8s}")
print(f"  {'el resto':22s} {len(b):4d} {ac(b):8.1f}% {b.neta.mean():+9.3f}   "
      f"{'78,0 %':>8s}")
print(f"\n  Fisher en el bloque 5:        p = {fs(a, b):.4f}")
print(f"  (en los bloques 1-4 fue        p = 0,0006)")

print("\n  y el matiz de ayer, lejos del nivel de Asia:")
sin = o[~o.toca]
al, ao = sin[sin.lleno], sin[~sin.lleno]
print(f"    lejos del nivel ({len(sin)} ops):  cuerpo lleno {len(al):2d} ops {ac(al):5.1f} %  ·  "
      f"resto {len(ao):2d} ops {ac(ao):5.1f} %   ·   p = {fs(al, ao):.4f}")
con = o[o.toca]
if len(con) > 5:
    cl, co = con[con.lleno], con[~con.lleno]
    print(f"    en el nivel     ({len(con)} ops):  cuerpo lleno {len(cl):2d} ops {ac(cl):5.1f} %  ·  "
          f"resto {len(co):2d} ops {ac(co):5.1f} %")

print("\n" + "="*74); print("LOS CINCO BLOQUES JUNTOS, SOBRE EL CUERPO"); print("="*74)
prev_a, prev_b = 64, 86        # bloques 1-4: 64 llenas, 86 no llenas
prev_atp, prev_btp = 32, 67    # 50,0 % de 64 y 78,0 % de 86
A = prev_a + len(a); B = prev_b + len(b)
Atp = prev_atp + int((a[a.res].mot=="TP").sum()); Btp = prev_btp + int((b[b.res].mot=="TP").sum())
print(f"  cuerpo lleno   {A:3d} operaciones · acierto ~{100*Atp/A:.1f} %")
print(f"  el resto       {B:3d} operaciones · acierto ~{100*Btp/B:.1f} %")
o.to_csv("data/examen5_cuerpo.csv", index=False)
