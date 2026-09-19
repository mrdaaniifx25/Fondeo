"""El CRT de H4 y de M15 como CONTEXTO de sus 150 entradas.

CRT segun la especificacion del proyecto (docs/CRT_H4_especificacion.md):
una vela barre el extremo de la anterior y CIERRA DENTRO DE SU CUERPO.

Se declara ANTES de mirar: seis variables, y a estas alturas ya se han corrido
unos 45 contrastes sobre las mismas 150 operaciones, asi que el umbral es
p < 0,001 Y que la direccion se repita en los cuatro bloques. Cualquier cosa por
debajo se reporta como no encontrada.

  python3 bt/crt_contexto.py
"""
import json, numpy as np, pandas as pd
from math import comb
TZ, INI, FIN = "Europe/Madrid", 480, 690
def fisher(a,b,c,d):
    n,r1,c1 = a+b+c+d, a+b, a+c
    if min(a,b,c,d) < 0 or n == 0: return 1.0
    D = lambda k: comb(r1,k)*comb(n-r1,c1-k)/comb(n,c1)
    p0 = D(a)*(1+1e-9)
    return sum(D(k) for k in range(max(0,c1-(n-r1)), min(r1,c1)+1) if D(k) <= p0)

m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
DIAS = set()
for dj in ("data/examen_dias.json","data/examen_dias2.json",
           "data/examen_dias3.json","data/examen_dias4.json"):
    DIAS |= {pd.Timestamp(v).date() for v in json.load(open(dj)).values()}
m1 = m1[m1.dia.isin(DIAS)].reset_index(drop=True)

def velas(df, paso):
    g = df.assign(b=(df["min"]//paso)*paso).groupby(["dia","b"])
    v = g.agg(o=("open","first"), h=("high","max"), l=("low","min"),
              c=("close","last"), n=("close","size")).reset_index()
    return v[v.n >= max(2, paso//3)].reset_index(drop=True)
H4, M15, M5 = velas(m1, 240), velas(m1, 15), velas(m1, 5)

def crt(o0,h0,l0,c0, o1,h1,l1,c1):
    """¿La vela 1 barre el extremo de la 0 y cierra dentro de su CUERPO?
    Devuelve +1 alcista (barre el minimo), -1 bajista (barre el maximo), 0 no."""
    cuerpoA, cuerpoB = min(o0,c0), max(o0,c0)
    if l1 < l0 and cuerpoA <= c1 <= cuerpoB: return 1
    if h1 > h0 and cuerpoA <= c1 <= cuerpoB: return -1
    return 0

filas = []
for dia, d1 in m1.groupby("dia"):
    h4 = H4[H4.dia == dia].sort_values("b").reset_index(drop=True)
    if len(h4) < 3: continue
    v0 = h4[h4.b == 0]; v4 = h4[h4.b == 240]
    if v0.empty or v4.empty: continue
    v0, v4 = v0.iloc[0], v4.iloc[0]
    crt_h4_cer = crt(v0.o, v0.h, v0.l, v0.c, v4.o, v4.h, v4.l, v4.c)
    g15 = M15[M15.dia == dia].sort_values("b").reset_index(drop=True)
    g5  = M5[(M5.dia == dia)].sort_values("b").reset_index(drop=True)
    O,H,L,C,B = g5.o.to_numpy(), g5.h.to_numpy(), g5.l.to_numpy(), g5.c.to_numpy(), g5.b.to_numpy()
    cuerpo4 = (min(v4.o, v4.c), max(v4.o, v4.c))
    for i in range(len(g5)):
        cm = int(B[i]) + 5
        if not (INI <= cm <= FIN): continue
        # H4 viva: lo que lleva la vela de 08:00 hasta este cierre
        m = (B >= INI) & (B <= B[i])
        cv = float(C[i])
        hv = float(H[m].max()) if m.any() else cv     # la vela de 08:00 aun no ha empezado
        lv = float(L[m].min()) if m.any() else cv
        crt_h4_viva = 0
        if lv < v4.l and cuerpo4[0] <= cv <= cuerpo4[1]: crt_h4_viva = 1
        elif hv > v4.h and cuerpo4[0] <= cv <= cuerpo4[1]: crt_h4_viva = -1
        pos_h4 = (cv - v4.l) / max(v4.h - v4.l, 1e-9)
        # M15: la ultima cerrada contra la anterior, y la viva contra la ultima cerrada
        k = int((cm - 1)//15)
        q = g15[g15.b <= (k-1)*15].tail(2)
        crt_m15 = 0
        if len(q) == 2:
            a, b = q.iloc[0], q.iloc[1]
            crt_m15 = crt(a.o,a.h,a.l,a.c, b.o,b.h,b.l,b.c)
        crt_m15_viva = 0
        if len(q) >= 1:
            b = q.iloc[-1]
            mv = (B >= k*15) & (B <= B[i])
            if mv.any():
                hh, ll = float(H[mv].max()), float(L[mv].min())
                cb = (min(b.o,b.c), max(b.o,b.c))
                if ll < b.l and cb[0] <= cv <= cb[1]: crt_m15_viva = 1
                elif hh > b.h and cb[0] <= cv <= cb[1]: crt_m15_viva = -1
        filas.append(dict(dia=dia, cierre_min=cm, crt_h4_cer=crt_h4_cer,
                          crt_h4_viva=crt_h4_viva, pos_h4=pos_h4,
                          crt_m15=crt_m15, crt_m15_viva=crt_m15_viva))
X = pd.DataFrame(filas)
print(f"{len(X):,} velas de M5 con estado de CRT · {X.dia.nunique()} sesiones")
print(f"  días con CRT en la H4 cerrada de 04:00-08:00: "
      f"{X.groupby('dia').crt_h4_cer.first().ne(0).sum()} de {X.dia.nunique()}")
X.to_csv("data/crt_contexto.csv", index=False)

S = pd.read_csv("data/cuerpo_vela.csv"); S["dia"] = pd.to_datetime(S.dia).dt.date
S = S.merge(X, on=["dia","cierre_min"], how="left")
S["res"] = S.mot.isin(["TP","SL"])
S["lado"] = S.lado_t
ac = lambda s: 100*(s[s.res].mot=="TP").mean() if s.res.any() else float("nan")
TP, SL = S[S.mot=="TP"], S[S.mot=="SL"]
ctl = X.merge(S[["dia","cierre_min"]].assign(suya=1), on=["dia","cierre_min"], how="left")
ctl = ctl[ctl.suya.isna()]

print("\n" + "="*84)
print("EL CRT COMO CONTEXTO · declarado antes de mirar · umbral p < 0,001")
print("="*84)
print(f"  {'variable':44s} {'TP':>8s} {'SL':>8s} {'control':>9s} {'p':>8s}")
print("  " + "-"*80)
def prop(nom, f, fc=None):
    a, b = f(TP), f(SL)
    c = fc(ctl).mean() if fc is not None else float("nan")
    p = fisher(int(a.sum()), int((~a).sum()), int(b.sum()), int((~b).sum()))
    print(f"  {nom:44s} {100*a.mean():7.1f}% {100*b.mean():7.1f}% "
          + (f"{100*c:8.1f}%" if fc is not None else f"{'—':>9s}") + f" {p:8.4f}"
          + ("  *" if p < 0.001 else ""))
    return p
prop("hay CRT en la H4 cerrada (04:00-08:00)", lambda d: d.crt_h4_cer != 0,
     lambda d: d.crt_h4_cer != 0)
prop("...y va en su dirección", lambda d: d.crt_h4_cer == d.lado)
prop("la H4 viva ha barrido la anterior (CRT vivo)", lambda d: d.crt_h4_viva != 0,
     lambda d: d.crt_h4_viva != 0)
prop("...y va en su dirección", lambda d: d.crt_h4_viva == d.lado)
prop("hay CRT en la última M15 cerrada", lambda d: d.crt_m15 != 0, lambda d: d.crt_m15 != 0)
prop("...y va en su dirección", lambda d: d.crt_m15 == d.lado)
prop("la M15 viva ha barrido la anterior", lambda d: d.crt_m15_viva != 0,
     lambda d: d.crt_m15_viva != 0)
prop("...y va en su dirección", lambda d: d.crt_m15_viva == d.lado)

print("\n  dónde está el precio dentro de la vela de H4 de 04:00-08:00:")
for nom, d in (("ganadoras", TP), ("perdedoras", SL)):
    q = np.where(d.lado > 0, d.pos_h4, 1-d.pos_h4)
    print(f"    {nom:12s} mediana {np.median(q):.2f}  ·  en el tercio a su favor "
          f"{100*np.mean(q >= 2/3):.0f} %")
print("\n  reparto de sus 150 por estado de CRT:")
for nom, m in (("sin CRT en ninguna parte", (S.crt_h4_viva==0) & (S.crt_m15_viva==0)),
               ("CRT vivo solo en M15", (S.crt_h4_viva==0) & (S.crt_m15_viva!=0)),
               ("CRT vivo solo en H4",  (S.crt_h4_viva!=0) & (S.crt_m15_viva==0)),
               ("CRT vivo en las dos",  (S.crt_h4_viva!=0) & (S.crt_m15_viva!=0))):
    s = S[m.fillna(False)]
    print(f"    {nom:26s} {len(s):3d} ({100*len(s)/len(S):4.1f} %)  acierto {ac(s):5.1f} %  "
          f"R neta {s.neta.mean():+.3f}")
S.to_csv("data/crt_suyas.csv", index=False)
