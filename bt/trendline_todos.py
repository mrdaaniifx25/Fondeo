"""El signo de la rotura de linea en los otros seis instrumentos · ventana de Londres."""
import numpy as np, pandas as pd
from math import sqrt
import importlib.util
spec = importlib.util.spec_from_file_location("tl", "bt/trendline.py")
tl = importlib.util.module_from_spec(spec)
import sys; sys.argv = ["tl"]; spec.loader.exec_module(tl)
zf = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x))) if len(x) > 2 else np.nan
print(f"{'instrumento':>11s} {'stop':>5s} {'k':>2s} {'n':>6s} {'acierto':>9s} {'dif':>7s} "
      f"{'stop':>7s} {'R neta':>8s} {'z':>7s}")
print("-"*68)
todo = []
for nom in ("EURUSD","GBPUSD","USDJPY","XAUUSD","NSXUSD","SPXUSD","GRXEUR"):
    t, nr = tl.corre(nom, "londres")
    todo.append(t)
    for sq, k in (("A",2), ("B",1)):
        s = t[(t.stop==sq)&(t.k==k)]
        if len(s) < 30: continue
        r = s[s.mot!="cierre"]; ac = (r.mot=="TP").mean(); geo = 1/(1+k)
        print(f"{nom:>11s} {sq:>5s} {k:2d} {len(s):6d} {100*ac:8.1f}% {100*(ac-geo):+6.1f}pt "
              f"{s.rgo.median():6.1f} {s.neta.mean():+8.3f} {zf(s.neta.to_numpy()):+7.2f}",
              flush=True)
T = pd.concat(todo, ignore_index=True)
T.to_csv("data/trendline_todos.csv", index=False)
print("\nsigno de la R neta por celda, sobre los siete instrumentos:")
for sq in ("A","B"):
    for k in (1,2,3):
        s = T[(T.stop==sq)&(T.k==k)]
        m = s.groupby("ins").neta.mean()
        print(f"  stop {sq} k={k}:  negativa en {int((m<0).sum())} de {len(m)} instrumentos"
              f"  ·  media {s.neta.mean():+.3f}")
