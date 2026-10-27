"""Pre-registro docs/PREREGISTRO_crt_maximo.md  ·  EL CRT MAXIMO

Todo lo que midio no-negativo en 45 documentos, ensamblado. La pieza nueva
es la ANTIGUEDAD DEL NIVEL: niveles de 2-4 sesiones batian a los de 1 en
RESULTADOS_cascada.md, y nunca se habia combinado con lo demas.

Dentro 2021-2024 (donde se eligieron los componentes: inflado por
construccion). FUERA 2025-2026: el unico numero que cuenta.

  python3 bt/crt_maximo.py
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, RR, KATR, HOR = 1e-4, 0.70, 2.0, 1.5, 6*60
CORTE = pd.Timestamp("2025-01-01")
# sesiones en hora de Madrid, tal como las tiene el en su grafico
SES = [("Asia", 0, 8), ("Londres", 8, 17), ("NuevaYork", 14, 23)]
VENT = (8, 11)                     # la ventana operable: Londres 08-11

M = pd.read_parquet("data/eurusd_m1.parquet")
M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
loc = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
M["dia"] = loc.dt.floor("D")
M["h"] = loc.dt.hour + loc.dt.minute/60.0
HH, LL, OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()

# ---------- velas M15 ----------
g = M.assign(k=loc.dt.floor("15min")).groupby("k", sort=True)
b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
          fin=("high", lambda x: x.index[-1]))
b = b[b.index.notna()]
tr = pd.concat([b.h-b.l, (b.h-b.c.shift(1)).abs(), (b.l-b.c.shift(1)).abs()], axis=1).max(axis=1)
b["atr"] = tr.rolling(14).mean().shift(1)
B = b.index
hb = B.hour + B.minute/60.0
O15,H15,L15,C15,A15 = (b[k].to_numpy() for k in ("o","h","l","c","atr"))
FIN = b.fin.to_numpy().astype(int)

# ---------- extremos de cada sesion, con su instante de cierre ----------
niveles = []                       # (ts_cierre_sesion, precio, es_max, idx_sesion)
k = 0
for (dia, nom), gg in M.groupby([M.dia, pd.cut(M.h, [-1, 8, 17, 23.99],
        labels=["Asia","Londres","NuevaYork"])], observed=True):
    if len(gg) < 20: continue
    niveles.append((gg.ts.iloc[-1], gg.high.max(), True,  k))
    niveles.append((gg.ts.iloc[-1], gg.low.min(),  False, k))
    k += 1
NV = pd.DataFrame(niveles, columns="ts precio esmax ses".split()).sort_values("ts")
NV = NV.reset_index(drop=True)
nts = NV.ts.to_numpy(); npr = NV.precio.to_numpy()
nmax = NV.esmax.to_numpy(); nses = NV.ses.to_numpy()
print(f"velas M15: {len(b):,}   niveles de sesion: {len(NV):,}")

# ---------- el barrido, con la EDAD del nivel ----------
tsb = B.to_numpy()
ops = []
vistos = set()
for i in range(2, len(b)-1):
    if not (VENT[0] <= hb[i] < VENT[1]): continue
    if not np.isfinite(A15[i]) or A15[i] <= 0: continue
    j = np.searchsorted(nts, tsb[i])          # niveles ya CERRADOS
    if j < 4: continue
    ses_act = nses[j-1]
    # candidatos: niveles cerrados, no barridos todavia en esta vela
    lo_i, hi_i = L15[i], H15[i]
    for s in range(max(0, j-30), j):
        pr, esmax = npr[s], nmax[s]
        edad = ses_act - nses[s] + 1          # 1 = la sesion inmediatamente anterior
        if edad < 1 or edad > 8: continue
        if esmax:
            if not (hi_i >= pr and C15[i] < pr): continue
            lado = -1
        else:
            if not (lo_i <= pr and C15[i] > pr): continue
            lado = 1
        clave = (B[i].date(), lado)
        if clave in vistos: continue
        vistos.add(clave)
        e = FIN[i] + 1
        if e >= len(M): continue
        ent = OO[e]; rgo = KATR*A15[i]
        sl = ent - lado*rgo; tp = ent + lado*RR*rgo
        a, z2 = e, min(e+HOR, len(M))
        hh, ll = HH[a:z2], LL[a:z2]
        if lado > 0:
            ks = np.nonzero(ll <= sl)[0]; kt = np.nonzero(hh >= tp)[0]
        else:
            ks = np.nonzero(hh >= sl)[0]; kt = np.nonzero(ll <= tp)[0]
        fs = ks[0] if len(ks) else 10**9; ft = kt[0] if len(kt) else 10**9
        R = RR if ft < fs else (-1.0 if fs < 10**9 else 0.0)
        ops.append((B[i], lado, edad, rgo/U, R))
        break
D = pd.DataFrame(ops, columns="ts lado edad rgo R".split())
D["cr"] = COSTE/D.rgo
D["n"] = D.R - D.cr
D["dia"] = pd.to_datetime(D.ts).dt.floor("D")
D["dentro"] = D.ts < CORTE
print(f"operaciones: {len(D):,}   dentro {int(D.dentro.sum()):,}   fuera {int((~D.dentro).sum()):,}\n")

def z(x, gr):
    m = x.mean()
    su = pd.DataFrame({"x":x.to_numpy(),"g":gr.to_numpy()}).groupby("g").x.apply(lambda v:(v-m).sum())
    s2 = float((su**2).sum())
    return m*len(x)/sqrt(s2) if s2>0 else np.nan

def ficha(et, S, ind="  "):
    if len(S) < 30: return print(f"{ind}{et:<34} (pocas: {len(S)})")
    geo = 1.0/(1.0+RR)
    print(f"{ind}{et:<34}{len(S):>6}{100*(S.R>0).mean():>9.1f}%{100*geo:>7.1f}%"
          f"{100*S.cr.mean():>7.1f}%{S.R.mean():>+9.4f}{S.n.mean():>+9.4f}"
          f"{z(S.n, S.dia.astype(str)):>+7.2f}")

CAB = (f"  {'':<34}{'n':>6}{'acierto':>10}{'geom':>7}{'coste':>7}"
       f"{'bruta':>9}{'NETA':>9}{'z':>7}")
print("="*96); print("1 · EL CRT MÁXIMO, todas las edades de nivel"); print("="*96)
print(CAB)
ficha("DENTRO 2021-2024 (inflado)", D[D.dentro])
ficha("FUERA 2025-2026  <-- EL NÚMERO", D[~D.dentro])
ficha("muestra completa", D)

print("\n" + "="*96); print("2 · LA PIEZA NUEVA · antigüedad del nivel"); print("="*96)
for et, m in (("DENTRO 2021-2024", D.dentro), ("FUERA 2025-2026", ~D.dentro)):
    print(f"\n  {et}"); print(CAB)
    S = D[m]
    ficha("nivel de 1 sesión", S[S.edad == 1], "    ")
    ficha("nivel de 2 a 4 sesiones", S[(S.edad >= 2) & (S.edad <= 4)], "    ")
    ficha("nivel de 5 o más", S[S.edad >= 5], "    ")

print("\n" + "="*96); print("3 · CONTRA LA VERSIÓN SIMPLE (solo rango de Asia del día)"); print("="*96)
print(CAB)
ficha("máximo · fuera de muestra", D[~D.dentro])
ficha("máximo · solo edad 2-4 · fuera", D[(~D.dentro) & (D.edad>=2) & (D.edad<=4)])
print("\n  (la versión simple está medida en RESULTADOS_su_patron.md: neta -0,0208)")
