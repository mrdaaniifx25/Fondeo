"""docs/PREREGISTRO_ob.md · el order block de M5 y la vela de M1.

  python3 bt/order_block.py
"""
import json, numpy as np, pandas as pd
from math import sqrt, comb, erf

TZ, U, INI, FIN, VIDA = "Europe/Madrid", 1e-4, 480, 690, 24
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
def fisher(a,b,c,d):
    n,r1,c1 = a+b+c+d, a+b, a+c
    if min(a,b,c,d) < 0 or n == 0: return 1.0
    D = lambda k: comb(r1,k)*comb(n-r1,c1-k)/comb(n,c1)
    p0 = D(a)*(1+1e-9)
    return sum(D(k) for k in range(max(0,c1-(n-r1)), min(r1,c1)+1) if D(k) <= p0)

t = pd.read_csv("data/operaciones_223.csv"); t["dia"] = pd.to_datetime(t.dia).dt.date
DIAS = {pd.Timestamp(d).date() for d in json.load(open("data/dias_164.json"))}
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(DIAS)].reset_index(drop=True)

def velas(d, paso):
    g = d.assign(b=(d["min"]//paso)*paso).groupby(["dia","b"]).agg(
        o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
        n=("close","size")).reset_index()
    return g[g.n >= max(2, paso//3)].reset_index(drop=True)
V5 = velas(m1, 5)

# ─── order blocks vigentes, vela a vela ───────────────────────────────────
filas = []
for dia, g in V5.groupby("dia"):
    g = g.sort_values("b").reset_index(drop=True)
    O,H,L,C,B = (g.o.to_numpy(), g.h.to_numpy(), g.l.to_numpy(), g.c.to_numpy(),
                 g.b.to_numpy())
    obs = []                       # (i, lado, zLo, zHi, cLo, cHi)
    for i in range(len(g)):
        # ¿la vela i-k era un OB que se confirma ahora?
        for k in (1, 2, 3):
            j = i - k
            if j < 0: continue
            if C[j] < O[j] and C[i] > H[j]:          # ultima bajista antes del impulso
                obs.append((j, 1, L[j], H[j], min(O[j],C[j]), max(O[j],C[j])))
            if C[j] > O[j] and C[i] < L[j]:          # ultima alcista antes del impulso
                obs.append((j, -1, L[j], H[j], min(O[j],C[j]), max(O[j],C[j])))
        if B[i]+5 < INI or B[i]+5 > FIN: continue
        cierre = C[i]
        dentro_z = dentro_c = 0
        for (j, lado, zl, zh, cl, ch) in obs:
            if i - j > VIDA: continue
            if zl <= cierre <= zh: dentro_z = lado if dentro_z == 0 else dentro_z
            if cl <= cierre <= ch: dentro_c = lado if dentro_c == 0 else dentro_c
        filas.append(dict(dia=dia, cierre_min=int(B[i])+5, c=cierre,
                          ob_zona=dentro_z, ob_cuerpo=dentro_c))
OB = pd.DataFrame(filas)
print(f"{len(OB):,} velas de M5 en ventana · {OB.dia.nunique()} sesiones")

# ─── la vela de M1 del minuto exacto ──────────────────────────────────────
idx = m1.set_index(["dia","min"])
def velaM1(dia, minuto, k=0):
    try:
        v = idx.loc[(dia, minuto-k)]
        v = v.iloc[0] if isinstance(v, pd.DataFrame) else v
        return float(v.open), float(v.high), float(v.low), float(v.close)
    except KeyError:
        return None

def rasgos(dia, minuto, lado):
    a = velaM1(dia, minuto); b = velaM1(dia, minuto, 1)
    if a is None or b is None: return None
    o,h,l,c = a; o1,h1,l1,c1 = b
    rango = max(h-l, 1e-9)
    envolvente = 0
    if c > o and c1 < o1 and c >= o1 and o <= c1: envolvente = 1
    if c < o and c1 > o1 and o >= c1 and c <= o1: envolvente = -1
    return dict(cuerpo_pct=abs(c-o)/rango*100, verde=c > o,
                envolvente=envolvente, rompe_alto=h > h1, rompe_bajo=l < l1,
                pos_cierre=(c-l)/rango)

# ─── unir con sus entradas ────────────────────────────────────────────────
t["cierre_min"] = (t.ent_min//5)*5 + 5
S = t.merge(OB, on=["dia","cierre_min"], how="left")
S["ocupada"] = False
S["res"] = S.mot.isin(["TP","SL"])
r1 = [rasgos(r.dia, int(r.ent_min), r.lado) for r in S.itertuples()]
for c in ("cuerpo_pct","verde","envolvente","rompe_alto","rompe_bajo","pos_cierre"):
    S[c] = [x[c] if x else np.nan for x in r1]
S = S.dropna(subset=["ob_zona"])

# controles: velas donde no entro y no estaba dentro de una operacion
ocupado = set()
for r in t.itertuples():
    for m in range(int(r.ent_min), int(r.sal_min)+1, 5):
        ocupado.add((r.dia, (m//5)*5+5))
suyas = {(r.dia, r.cierre_min) for r in t.itertuples()}
OB["suya"] = [(d, c) in suyas for d, c in zip(OB.dia, OB.cierre_min)]
OB["ocup"] = [(d, c) in ocupado for d, c in zip(OB.dia, OB.cierre_min)]
CTL = OB[~OB.suya & ~OB.ocup]
print(f"{len(S)} entradas suyas con contexto · {len(CTL):,} velas de control\n")

ac = lambda s: 100*(s[s.res].mot=="TP").mean() if s.res.any() else float("nan")
print("="*78); print("1 · EL ORDER BLOCK DE M5"); print("="*78)
for col, nom in (("ob_zona","zona completa (mínimo-máximo)"), ("ob_cuerpo","solo el cuerpo")):
    mismo = (S[col] == S.lado)
    hay_s = (S[col] != 0).mean()
    hay_c = (CTL[col] != 0).mean()
    pp = ((S[col]!=0).sum() + (CTL[col]!=0).sum())/(len(S)+len(CTL))
    ee = sqrt(pp*(1-pp)*(1/len(S)+1/len(CTL)))
    zz = (hay_s-hay_c)/ee
    print(f"\n  {nom}")
    print(f"    entra dentro de un OB vigente ........ {100*hay_s:5.1f} %   "
          f"control {100*hay_c:5.1f} %   z = {zz:+.2f}   p = {p2(zz):.5f}")
    print(f"    y ademas en su misma direccion ....... {100*mismo.mean():5.1f} % de sus entradas")
    a, b = S[mismo], S[~mismo]
    print(f"    acierto dentro de OB a favor ......... {ac(a):5.1f} % (n={len(a)})   "
          f"fuera {ac(b):5.1f} % (n={len(b)})   p = "
          f"{fisher(int((a[a.res].mot=='TP').sum()), int((a[a.res].mot=='SL').sum()), int((b[b.res].mot=='TP').sum()), int((b[b.res].mot=='SL').sum())):.4f}")

print("\n" + "="*78); print("2 · LA VELA DE M1 EN EL MINUTO EXACTO"); print("="*78)
env = (S.envolvente == S.lado)
print(f"  es una envolvente en su direccion ...... {100*env.mean():5.1f} % de sus entradas")
print(f"  rompe el extremo de la vela anterior ... "
      f"{100*np.where(S.lado>0, S.rompe_alto, S.rompe_bajo).mean():5.1f} %")
a, b = S[env], S[~env]
print(f"  acierto con envolvente {ac(a):5.1f} % (n={len(a)})  ·  sin ella {ac(b):5.1f} % (n={len(b)})"
      f"   p = {fisher(int((a[a.res].mot=='TP').sum()), int((a[a.res].mot=='SL').sum()), int((b[b.res].mot=='TP').sum()), int((b[b.res].mot=='SL').sum())):.4f}")
print(f"\n  el cuerpo de la vela de M1:")
for lo_, hi_ in ((0,40),(40,60),(60,80),(80,101)):
    s = S[(S.cuerpo_pct>=lo_)&(S.cuerpo_pct<hi_)]
    if len(s) < 5: continue
    print(f"    {lo_}-{hi_ if hi_<=100 else 100} %  n={len(s):3d}  acierto {ac(s):5.1f} %  "
          f"R neta {s.neta.mean():+.3f}")
S.to_csv("data/order_block.csv", index=False)
