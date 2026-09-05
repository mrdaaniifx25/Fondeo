"""Los 16 patrones de velas japonesas del PDF de IG, medidos en la vela de M5
de cada una de sus 150 entradas y en los 3.400 momentos de control.

Definiciones tal como las describe el PDF, cuantificadas. En forex intradia no
hay huecos, asi que en los patrones que el PDF describe con gap -penetrante,
cubierta de nube oscura, estrellas- se usa la adaptacion habitual: apertura igual
o mas alla del cierre anterior en vez de hueco.

Ademas del patron se mide lo que el llama "tipo de cierre": donde queda el cierre
dentro del rango de la vela, y cuanto cuerpo tiene.

  python3 bt/patrones_velas.py
"""
import json, numpy as np, pandas as pd
from math import sqrt, erf

U, TZ, INI, FIN = 1e-4, "Europe/Madrid", 480, 690
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))

# ─── los 16 patrones ──────────────────────────────────────────────────────
def cuerpo(o, c): return abs(c-o)
def rango(h, l):  return max(h-l, 1e-12)

def patrones(O, H, L, C, i, tend):
    """Devuelve la lista de patrones que se cumplen en la vela i.
    `tend` es la direccion de las velas anteriores: +1 sube, -1 baja, 0 plano.
    Hace falta para distinguir martillo de hombre colgado y martillo invertido
    de estrella fugaz, que son la misma forma en tendencia contraria."""
    o, h, l, c = O[i], H[i], L[i], C[i]
    b, r = cuerpo(o, c), rango(h, l)
    msup, minf = h - max(o, c), min(o, c) - l
    verde, roja = c > o, c < o
    P = []

    # --- de una vela ---
    if b <= 0.05*r:                                   P.append("doji")
    elif b <= 0.30*r and msup >= 0.25*r and minf >= 0.25*r: P.append("trompo")
    if b <= 0.33*r and minf >= 2*b and msup <= max(b, 0.10*r):
        P.append("martillo" if tend < 0 else "hombre colgado")
    if b <= 0.33*r and msup >= 2*b and minf <= max(b, 0.10*r):
        P.append("martillo invertido" if tend < 0 else "estrella fugaz")

    # --- de dos velas ---
    if i >= 1:
        o1, c1 = O[i-1], C[i-1]
        b1 = cuerpo(o1, c1)
        if c1 < o1 and verde and c >= o1 and o <= c1 and b > b1:
            P.append("envolvente alcista")
        if c1 > o1 and roja and o >= c1 and c <= o1 and b > b1:
            P.append("envolvente bajista")
        med1 = (o1+c1)/2
        if c1 < o1 and verde and o <= c1 and med1 < c < o1 and b1 > 0.5*rango(H[i-1], L[i-1]):
            P.append("penetrante")
        if c1 > o1 and roja and o >= c1 and o1 < c < med1 and b1 > 0.5*rango(H[i-1], L[i-1]):
            P.append("cubierta de nube oscura")

    # --- de tres velas ---
    if i >= 2:
        o2, c2 = O[i-2], C[i-2]
        b2, b1 = cuerpo(o2, c2), cuerpo(O[i-1], C[i-1])
        med2 = (o2+c2)/2
        if c2 < o2 and b1 <= 0.4*b2 and verde and c > med2:
            P.append("estrella de la mañana")
        if c2 > o2 and b1 <= 0.4*b2 and roja and c < med2:
            P.append("estrella del atardecer")
        tresV = all(C[j] > O[j] for j in (i-2, i-1, i)) and C[i] > C[i-1] > C[i-2]
        if tresV and all(H[j]-max(O[j],C[j]) <= 0.30*rango(H[j],L[j]) for j in (i-2,i-1,i)) \
           and O[i-1] <= C[i-2] and O[i] <= C[i-1]:
            P.append("tres soldados blancos")
        tresR = all(C[j] < O[j] for j in (i-2, i-1, i)) and C[i] < C[i-1] < C[i-2]
        if tresR and all(min(O[j],C[j])-L[j] <= 0.30*rango(H[j],L[j]) for j in (i-2,i-1,i)) \
           and O[i-1] >= C[i-2] and O[i] >= C[i-1]:
            P.append("tres cuervos negros")

    # --- de cinco velas ---
    if i >= 4:
        g0 = C[i-4] > O[i-4]
        peq = all(cuerpo(O[j],C[j]) < cuerpo(O[i-4],C[i-4]) and
                  L[j] >= L[i-4] and H[j] <= H[i-4] for j in (i-3,i-2,i-1))
        if g0 and peq and verde and c > C[i-4]:   P.append("triple formación alcista")
        if (not g0) and peq and roja and c < C[i-4]: P.append("triple formación bajista")
    return P

ALCISTA = {"martillo","martillo invertido","envolvente alcista","penetrante",
           "estrella de la mañana","tres soldados blancos","triple formación alcista"}
BAJISTA = {"hombre colgado","estrella fugaz","envolvente bajista",
           "cubierta de nube oscura","estrella del atardecer","tres cuervos negros",
           "triple formación bajista"}
NEUTRO  = {"doji","trompo"}

def tipo_cierre(o, h, l, c):
    r = rango(h, l); pos = (c - l)/r
    if pos >= 0.75: t = "cierra arriba"
    elif pos <= 0.25: t = "cierra abajo"
    else: t = "cierra en medio"
    b = cuerpo(o, c)/r
    f = "cuerpo lleno" if b >= 0.6 else "cuerpo medio" if b >= 0.3 else "cuerpo pequeño"
    return t, f, pos, b

# ─── datos ────────────────────────────────────────────────────────────────
DIAS = set()
for dj in ("data/examen_dias.json","data/examen_dias2.json",
           "data/examen_dias3.json","data/examen_dias4.json"):
    DIAS |= {pd.Timestamp(v).date() for v in json.load(open(dj)).values()}
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(DIAS)].reset_index(drop=True)

def barras(df, paso):
    g = df.assign(b=(df["min"]//paso)*paso).groupby(["dia","b"])
    v = g.agg(o=("open","first"), h=("high","max"), l=("low","min"),
              c=("close","last"), n=("close","size")).reset_index()
    v = v[v.n >= max(2, paso//3)].reset_index(drop=True)
    v["cierre_min"] = v.b + paso
    return v
V5, V15 = barras(m1, 5), barras(m1, 15)

t = pd.read_csv("data/operaciones_150.csv"); t["dia"] = pd.to_datetime(t.dia).dt.date

filas = []
for dia, g5 in V5.groupby("dia"):
    g5 = g5.reset_index(drop=True)
    O,H,L,C = g5.o.to_numpy(), g5.h.to_numpy(), g5.l.to_numpy(), g5.c.to_numpy()
    g15 = V15[V15.dia == dia].reset_index(drop=True)
    O15,H15,L15,C15 = g15.o.to_numpy(), g15.h.to_numpy(), g15.l.to_numpy(), g15.c.to_numpy()
    cm15 = g15.cierre_min.to_numpy()
    for i, r in enumerate(g5.itertuples()):
        if not (INI <= r.cierre_min <= FIN): continue
        if i < 5: continue
        tend = float(np.sign(C[i-1] - C[max(i-4,0)]))
        P = patrones(O, H, L, C, i, tend)
        tc, tf, pos, bfr = tipo_cierre(r.o, r.h, r.l, r.c)
        # M15: la ultima cerrada y la que se esta formando
        k = int(np.searchsorted(cm15, r.cierre_min, side="right")) - 1
        if k < 3: continue
        m15dir  = float(np.sign(C15[k] - O15[k]))           # ultima M15 cerrada
        m15tend = float(np.sign(C15[k] - C15[k-3]))         # tendencia de 4 velas
        m15pos  = float((r.c - L15[k]) / max(H15[k]-L15[k], 1e-12))
        m5tend  = tend
        filas.append(dict(dia=dia, cierre_min=int(r.cierre_min), o=r.o, h=r.h, l=r.l, c=r.c,
                          patrones="+".join(P) if P else "ninguno",
                          alcista=any(p in ALCISTA for p in P),
                          bajista=any(p in BAJISTA for p in P),
                          neutro=any(p in NEUTRO for p in P),
                          cierre=tc, cuerpo=tf, pos_cierre=pos, frac_cuerpo=bfr,
                          verde=r.c > r.o, m5tend=m5tend, m15dir=m15dir,
                          m15tend=m15tend, m15pos=m15pos))
B = pd.DataFrame(filas)
print(f"{len(B):,} velas de M5 analizadas en {B.dia.nunique()} sesiones")

# ancla de cada entrada suya
B["suya"] = False; B["lado"] = 0; B["R"] = np.nan; B["mot"] = ""
B["ocupada"] = False
for r in t.itertuples():
    cand = B[(B.dia == r.dia) & (B.cierre_min <= r.ent_min)]
    if cand.empty: continue
    i = cand.index[-1]
    B.loc[i, ["suya","lado","R","mot"]] = [True, r.lado, r.R, r.mot]
    B.loc[(B.dia==r.dia) & (B.cierre_min>r.ent_min) & (B.cierre_min<=r.sal_min) & ~B.suya,
          "ocupada"] = True
print(f"ancladas {int(B.suya.sum())} entradas suyas")
B.to_csv("data/patrones_velas.csv", index=False)
