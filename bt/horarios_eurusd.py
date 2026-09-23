"""Los horarios de reversion y continuacion del EURUSD, en hora de Espana.

  reversion     09:00 - 15:00
  continuacion  12:00 - 17:00
  (se solapan de 12 a 15; se trata como banda aparte)

Si el marco es correcto, DENTRO de la banda de reversion el patron "barre y
cierra dentro" deberia girarse, y DENTRO de la de continuacion el patron
"barre y cierra fuera" deberia seguir. La prueba fundacional salio plana
mezclando las 24 horas; esta es la version que podria explicar por que.
"""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C

BANDAS = [("madrugada 00-09", 0, 9), ("solo REVERSION 09-12", 9, 12),
          ("solapan 12-15", 12, 15), ("solo CONTINUACION 15-17", 15, 17),
          ("tarde 17-24", 17, 24)]

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])

print("="*104)
print("HORARIOS DE REVERSION Y CONTINUACION · EURUSD · hora de España · 2020-2026")
print("  retorno de la vela siguiente en unidades de ATR, con el signo que predice el marco")
print("="*104)

for tfn, tfh in (("H1",1), ("M15",0.25)):
    if tfh >= 1:
        ref = velas_ref(m1, int(tfh), ancla_ny=1)
    else:
        ch = m1.set_index("ts").resample("15min",label="left",closed="left").agg(
            open=("open","first"),high=("high","max"),low=("low","min"),
            close=("close","last")).dropna().reset_index()
        ref = ch.rename(columns={"ts":"id"}); ref["fin"] = ref["id"]
    t = C.clasifica(ref)
    mad = pd.DatetimeIndex(t.ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    t = t.assign(h=mad.hour)

    print(f"\n{'─'*104}\n{tfn}   ({len(t):,} observaciones)\n")
    print(f"   {'banda horaria':26s} {'':>6s} {'REVERSION (cierra dentro)':>30s}   {'CONTINUACION (cierra fuera)':>30s}")
    print(f"   {'':26s} {'n':>6s} {'media':>9s} {'IC95':>19s}   {'media':>9s} {'IC95':>19s}")
    for nom, a, b in BANDAS:
        g = t[(t.h >= a) & (t.h < b)]
        out = []
        for sel in ("DENTRO", "FUERA"):
            gg = g[g.clase.str.contains(sel) & (g.pred != 0)]
            if len(gg) < 40: out.append(("", "")); continue
            x = (gg.ret * gg.pred).to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x))
            mk = "*" if abs(x.mean()) > 1.96*ee else " "
            out.append((f"{x.mean():>+9.4f}{mk}",
                        f"[{x.mean()-1.96*ee:+.4f},{x.mean()+1.96*ee:+.4f}]"))
        print(f"   {nom:26s} {len(g):>6,} {out[0][0]:>10s} {out[0][1]:>19s}   "
              f"{out[1][0]:>10s} {out[1][1]:>19s}")

    # la prueba que decide: ¿se separan las dos celdas DENTRO de cada banda?
    print(f"\n   ¿se separan las dos celdas dentro de cada banda?  (lo que exige el marco)")
    for nom, a, b in BANDAS:
        g = t[(t.h >= a) & (t.h < b) & (t.pred != 0)]
        d = g[g.clase.str.contains("DENTRO")]; f = g[g.clase.str.contains("FUERA")]
        if len(d) < 40 or len(f) < 40: continue
        xd = (d.ret*d.pred).to_numpy(); xf = (f.ret*f.pred).to_numpy()
        se = np.sqrt(xd.var(ddof=1)/len(xd) + xf.var(ddof=1)/len(xf))
        z = (xd.mean()-xf.mean())/se
        print(f"      {nom:26s} reversion {xd.mean():+.4f}  vs  continuacion {xf.mean():+.4f}"
              f"   dif {xd.mean()-xf.mean():+.4f}  z {z:+.2f}{'  <<<' if abs(z)>2.58 else ''}")
