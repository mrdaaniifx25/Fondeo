"""Tres comprobaciones sobre las 11 operaciones que el usuario no tomo.

1. Su suelo horario real: cuantas de sus 25 entradas caen antes de las 09:00.
2. Las 11 con SU colocacion del stop (al otro lado del nivel de Asia) en vez
   de la de la regla (al otro lado de la vela anterior).
3. El binomial contra el 33,3 % geometrico en cada escenario.
"""
import pandas as pd, numpy as np
from math import comb
U, COSTE, EUR = 0.0001, 1.2, 150.0

o = pd.read_csv("data/agosto_operaciones.csv")
o["h"] = o.hora.str.slice(0,2).astype(int)*100 + o.hora.str.slice(3,5).astype(int)
print("1) SUS 25 ENTRADAS")
print(f"   antes de 08:20 {int((o.h<820).sum())}  ·  08:20-09:00 {int(((o.h>=820)&(o.h<900)).sum())}"
      f"  ·  desde 09:00 {int((o.h>=900).sum())}")

ver = pd.read_csv("data/agosto_verificacion.csv"); ver = ver[ver.suyo != "abierta"].copy()
ver["R"] = np.where(ver.mot.isin(["TP","SL"]), ver.R, np.where(ver.suyo=="TP", ver.rr, -1.0))
ver["fecha"] = pd.to_datetime(ver.fecha)
suyas = ver[["fecha","R","rgo"]].rename(columns={"rgo":"riesgo"})

t = pd.read_csv("data/asia_nivel.csv", parse_dates=["ts"]); a = t[t.ts>="2026-08-01"].copy()
loc = a.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
a["hm"] = loc.dt.hour*100 + loc.dt.minute; a["fecha"] = pd.to_datetime(a.dia)
SUY = {("2026-08-03",-1),("2026-08-06",-1),("2026-08-11",-1)}
s = a[~a.apply(lambda r:(str(r.dia),r.lado) in SUY, axis=1)]
once = s[~((s.dia=="2026-08-07")&(s.tipo=="B"))]; once = once[once.tipo!="A"].copy()

print("\n2) LAS 11 CON SU STOP  (data/agosto_11_tu_stop.csv)")
tu = pd.read_csv("data/agosto_11_tu_stop.csv", parse_dates=["fecha"])
print(f"   regla:   TP {int((once.R>0).sum())} / SL {int((once.R<0).sum())}  riesgo mediano {once.riesgo.median():.1f}p")
print(f"   su stop: TP {int((tu.R>0).sum())} / SL {int((tu.R<0).sum())}  riesgo mediano {tu.riesgo.median():.1f}p")

def bl(nom, d):
    d = d.copy(); d["neto"] = d.R - COSTE/d.riesgo
    g = d.groupby("fecha").agg(neto=("neto","mean"))
    ee = g.neto.std(ddof=1)/np.sqrt(len(g)); k, n = int((d.R>0).sum()), len(d)
    p = sum(comb(n,i)*(1/3)**i*(2/3)**(n-i) for i in range(k, n+1))
    print(f"   {nom:<42}{n:>4}{len(g):>6}{100*k/n:>8.1f}%{g.neto.mean():>+9.3f}"
          f"{g.neto.mean()/ee:>+7.2f}{d.neto.sum()*EUR:>+9.0f}   1 entre {1/p:,.0f}".replace(",","."))

c = ["fecha","R","riesgo"]
print(f"\n3) ESCENARIOS\n   {'':<42}{'ops':>4}{'días':>6}{'acierto':>9}{'neta/d':>9}{'z':>7}{'euros':>9}"
      "   binomial vs 33,3 %")
bl("como lo opero", suyas[c])
bl("+ las 11 (todo lo que dijo que si)", pd.concat([suyas[c], once[c]]))
bl("+ las 8 que no son la apertura (>=08:20)", pd.concat([suyas[c], once[once.hm>=820][c]]))
bl("+ las 6 desde las 09:00", pd.concat([suyas[c], once[once.hm>=900][c]]))
