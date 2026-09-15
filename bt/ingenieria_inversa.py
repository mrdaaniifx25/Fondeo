"""Sus 150 entradas contra los ~4.800 momentos en que no entro, esos mismos dias.

Descriptivo y EXPLORATORIO, declarado asi en docs/PREREGISTRO_ingenieria_inversa.md.
Ocho variables, Bonferroni a p < 0,00625.

  python3 bt/ingenieria_inversa.py
"""
import json, sys
import numpy as np, pandas as pd
from math import sqrt, erf

TZ, U = "Europe/Madrid", 1e-4
INI, FIN = 480, 690                      # 08:00 y 11:30 en minutos
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

t = pd.read_csv("data/operaciones_150.csv")
t["dia"] = pd.to_datetime(t.dia).dt.date
DIAS_OP = set(t.dia)
# el universo son los 114 dias de sesion de los cuatro bloques, opere o no
DIAS = set()
for dj in ("data/examen_dias.json", "data/examen_dias2.json",
           "data/examen_dias3.json", "data/examen_dias4.json"):
    DIAS |= {pd.Timestamp(v).date() for v in json.load(open(dj)).values()}
print(f"{len(t)} entradas suyas · {len(DIAS)} sesiones en el universo "
      f"({len(DIAS_OP)} con operación)")

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date
m1 = m1[m1.dia.isin(DIAS)].reset_index(drop=True)
m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute

def velas(df, paso):
    """Barras de `paso` minutos. `cierre_min` es el minuto en que YA esta cerrada."""
    g = df.assign(b=(df["min"]//paso)*paso).groupby(["dia","b"])
    v = g.agg(o=("open","first"), h=("high","max"), l=("low","min"),
              c=("close","last"), n=("close","size")).reset_index()
    v = v[v.n >= max(2, paso//3)].reset_index(drop=True)
    v["cierre_min"] = v.b + paso
    return v

M5, M15 = velas(m1, 5), velas(m1, 15)
filas = []
for dia, d1 in m1.groupby("dia"):
    a = d1[d1["min"] < INI]
    if len(a) < 300: continue                       # Asia casi entera
    hi, lo = float(a.high.max()), float(a.low.min())
    h4 = d1[(d1["min"] >= 240) & (d1["min"] < INI)]  # la vela de H4 de 04:00 a 08:00
    if h4.empty: continue
    h4dir = np.sign(float(h4.close.iloc[-1]) - float(h4.open.iloc[0]))
    ap = d1[d1["min"] >= INI]
    if ap.empty: continue
    ap0 = float(ap.open.iloc[0])
    v = M5[(M5.dia == dia) & (M5.cierre_min >= INI) & (M5.cierre_min <= FIN)]
    q = M15[(M15.dia == dia)].reset_index(drop=True)
    toques = {hi: 0, lo: 0}
    for r in v.itertuples():
        cer = min(abs(r.c-hi), abs(r.c-lo))/U
        L, arriba = (hi, True) if abs(r.c-hi) <= abs(r.c-lo) else (lo, False)
        toca  = r.l <= L <= r.h
        fuera = (r.c > L) if arriba else (r.c < L)
        # M15 cerrados antes de este cierre
        qq = q[q.cierre_min <= r.cierre_min]
        m15dir = (np.sign(float(qq.c.iloc[-1]) - float(qq.c.iloc[-5]))
                  if len(qq) >= 5 else 0.0)
        filas.append(dict(dia=dia, cierre_min=int(r.cierre_min), c=r.c,
                          cerca=cer, nivel_alto=arriba, toca=toca,
                          cuerpo_fuera=bool(toca and fuera), mecha=bool(toca and not fuera),
                          toque=toques[L], h4=h4dir, m15=m15dir,
                          hora=int(r.cierre_min-INI), rango=(r.h-r.l)/U,
                          dia_dir=np.sign(r.c-ap0)))
        if toca: toques[L] += 1
C = pd.DataFrame(filas)
print(f"{len(C):,} velas candidatas ({len(C)/C.dia.nunique():.0f} por sesión)")

# ancla de cada entrada: la ultima vela de M5 ya cerrada en ese minuto
llave = {(r.dia, r.cierre_min): i for i, r in enumerate(C.itertuples())}
C["suya"] = False; C["ocupada"] = False
anc = []
for r in t.itertuples():
    cand = C[(C.dia == r.dia) & (C.cierre_min <= r.ent_min)]
    if cand.empty: anc.append(None); continue
    i = cand.index[-1]; C.loc[i, "suya"] = True; anc.append(i)
    # los minutos en los que estaba dentro de una operacion no son eleccion suya
    C.loc[(C.dia == r.dia) & (C.cierre_min > r.ent_min) & (C.cierre_min <= r.sal_min),
          "ocupada"] = True
t["ancla"] = anc
print(f"ancladas {t.ancla.notna().sum()} de {len(t)}  ·  "
      f"velas distintas usadas: {C.suya.sum()}")
libre = C[~C.suya & ~C.ocupada]
print(f"controles con las manos libres: {len(libre):,}  "
      f"(descartadas {int(C.ocupada.sum()):,} por estar dentro de una operación)\n")

S = C[C.suya]
print("="*78); print("SUS ENTRADAS CONTRA LOS MOMENTOS EN QUE NO ENTRÓ  (EXPLORATORIO)")
print("="*78)
print(f"  {'variable':26s} {'suyas':>9s} {'controles':>10s} {'dif':>8s} {'z':>7s} {'p':>10s}")
print("  " + "-"*74)
def cont(nom, col):
    a, b = S[col].astype(float), libre[col].astype(float)
    ee = sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    z = (a.mean()-b.mean())/ee if ee > 0 else 0.0
    print(f"  {nom:26s} {a.median():9.1f} {b.median():10.1f} "
          f"{a.mean()-b.mean():+8.1f} {z:+7.2f} {p2(z):10.6f}"
          + ("  *" if p2(z) < 0.00625 else ""))
def prop(nom, col):
    a, b = S[col].astype(bool), libre[col].astype(bool)
    pa, pb = a.mean(), b.mean()
    pp = (a.sum()+b.sum())/(len(a)+len(b))
    ee = sqrt(pp*(1-pp)*(1/len(a)+1/len(b)))
    z = (pa-pb)/ee if ee > 0 else 0.0
    print(f"  {nom:26s} {100*pa:8.1f}% {100*pb:9.1f}% {100*(pa-pb):+7.1f}pt {z:+7.2f} "
          f"{p2(z):10.6f}" + ("  *" if p2(z) < 0.00625 else ""))
cont("1 distancia al nivel (p)", "cerca")
prop("2a cuerpo fuera del nivel", "cuerpo_fuera")
prop("2b solo mecha", "mecha")
prop("2c la vela toca el nivel", "toca")
cont("3 toques previos del nivel", "toque")
cont("6 minutos desde las 08:00", "hora")
cont("7 rango de la vela (p)", "rango")
print("  (4 H4 y 5 M15 son direcciones: se miran abajo, contra SU dirección)")
print("\n  * = pasa Bonferroni (p < 0,00625)")

print("\n" + "="*78); print("HACIA DÓNDE ENTRA  (solo sus 150)"); print("="*78)
t2 = t.dropna(subset=["ancla"]).copy()
t2["ancla"] = t2.ancla.astype(int)
for c in ("nivel_alto", "cuerpo_fuera", "mecha", "toca", "h4", "m15", "dia_dir",
          "cerca", "toque", "hora", "rango"):
    t2[c] = C.loc[t2.ancla, c].to_numpy()
t2["gana"] = t2.R > 0
def reparto(nom, mask, n=None):
    s = t2[mask]
    r = s[s.mot.isin(["TP","SL"])]
    ac = 100*(r.mot == "TP").mean() if len(r) else float("nan")
    print(f"  {nom:38s} {len(s):3d} ({100*len(s)/len(t2):4.1f} %)   acierto {ac:5.1f} %")
print("  con la rotura (compra por encima del alto, venta por debajo del bajo):")
con = ((t2.lado > 0) & t2.nivel_alto & t2.cuerpo_fuera) | \
      ((t2.lado < 0) & ~t2.nivel_alto & t2.cuerpo_fuera)
reparto("a favor de la rotura", con)
reparto("desvaneciendo (contra la rotura)", t2.cuerpo_fuera & ~con)
reparto("sin cuerpo fuera del nivel", ~t2.cuerpo_fuera)
print("\n  contra la dirección de las temporalidades altas:")
reparto("a favor de H4", t2.lado == t2.h4)
reparto("en contra de H4", (t2.h4 != 0) & (t2.lado != t2.h4))
reparto("a favor de M15", t2.lado == t2.m15)
reparto("en contra de M15", (t2.m15 != 0) & (t2.lado != t2.m15))
reparto("a favor del día hasta ese momento", t2.lado == t2.dia_dir)
reparto("en contra del día", (t2.dia_dir != 0) & (t2.lado != t2.dia_dir))
print("\n  por cercanía al nivel:")
for lo, hi in ((0,3),(3,6),(6,12),(12,10_000)):
    reparto(f"a {lo}-{hi if hi<1000 else '+'} pips del nivel",
            (t2.cerca >= lo) & (t2.cerca < hi))
C.to_csv("data/contexto_velas.csv", index=False)
t2.to_csv("data/contexto_suyas.csv", index=False)

print("\n" + "="*78)
print("LA PREGUNTA QUE DECIDE: ¿ALGUNA DE ESAS VARIABLES SEPARA SUS GANADORAS?")
print("="*78)
res = t2[t2.mot.isin(["TP","SL"])].copy()
G, P = res[res.mot == "TP"], res[res.mot == "SL"]
print(f"  {len(G)} ganadoras · {len(P)} perdedoras")
print(f"  {'variable':30s} {'gana':>8s} {'pierde':>8s} {'dif':>8s} {'t':>7s} {'p':>9s}")
print("  " + "-"*72)
for nom, col in (("distancia al nivel (p)","cerca"), ("toques previos","toque"),
                 ("minutos desde las 08:00","hora"), ("stop en pips","rgo"),
                 ("dirección de H4 (±1)","h4"), ("dirección de M15 (±1)","m15"),
                 ("nº de operación del bloque","ses")):
    a, b = G[col].astype(float), P[col].astype(float)
    ee = sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    z = (a.mean()-b.mean())/ee if ee > 0 else 0.0
    print(f"  {nom:30s} {a.median():8.1f} {b.median():8.1f} {a.mean()-b.mean():+8.2f} "
          f"{z:+7.2f} {p2(z):9.4f}" + ("  *" if p2(z) < 0.00625 else ""))
for nom, col in (("la vela toca el nivel","toca"), ("solo mecha","mecha"),
                 ("cuerpo fuera","cuerpo_fuera"), ("entra por encima del nivel","nivel_alto")):
    a, b = G[col].astype(bool), P[col].astype(bool)
    pp = (a.sum()+b.sum())/(len(a)+len(b))
    ee = sqrt(pp*(1-pp)*(1/len(a)+1/len(b)))
    z = (a.mean()-b.mean())/ee if ee > 0 else 0.0
    print(f"  {nom:30s} {100*a.mean():7.1f}% {100*b.mean():7.1f}% "
          f"{100*(a.mean()-b.mean()):+7.1f}pt {z:+7.2f} {p2(z):9.4f}"
          + ("  *" if p2(z) < 0.00625 else ""))
print("\n  a favor / en contra, acierto:")
for nom, m in (("H4", t2.lado == t2.h4), ("M15", t2.lado == t2.m15),
               ("día", t2.lado == t2.dia_dir)):
    for et, mm in ((f"a favor de {nom}", m), (f"en contra de {nom}", ~m)):
        r = t2[mm & t2.mot.isin(["TP","SL"])]
        print(f"    {et:22s} n={len(r):3d}  acierto {100*(r.mot=='TP').mean():5.1f} %  "
              f"R neta {(r.R - 1.43/r.rgo).mean():+.3f}")
