"""El sistema de bt/sistema_eurusd_intradia.py, tal cual, en oro y DAX.

Misma especificacion exacta, sin tocar ni un parametro:
  D1 EMA(20) da la direccion · H1 posicion en rango de 6 horas < 1/3 · vela
  M15 a favor · riesgo 1,5 x ATR(14) M15 · R:R 1,5 · cierre a las 4 h.

Control OBLIGATORIO aqui y no en EURUSD: el oro subio 143 % y el DAX 573 %
en la muestra, asi que un filtro que este largo casi siempre gana sin saber
nada. Se compara contra COMPRAR Y AGUANTAR con la misma geometria.

  python3 bt/sistema_tres_instrumentos.py
"""
import numpy as np, pandas as pd
from math import sqrt
rng = np.random.default_rng(20261013)

# nombre, ruta, unidad, coste ECN, coste minorista
INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 0.70, 1.43),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 12.0, 35.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  0.8,  1.6)]
VENT = {"Londres 08-12":   ("Europe/London",      8, 12),
        "Fráncfort 09-13": ("Europe/Berlin",      9, 13),
        "NuevaYork 08-12": ("America/New_York",   8, 12)}
TOPE, RR = 4*60, 1.5


def carga(ruta):
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    d = M.assign(k=M.ts.dt.floor("1440min")).groupby("k").agg(c=("close","last"))
    dirD = np.sign(d.c - d.c.ewm(span=20, adjust=False).mean()).shift(1)
    mapD = M.ts.dt.floor("1440min").map(dirD).to_numpy()
    h = M.assign(k=M.ts.dt.floor("60min")).groupby("k").agg(
        h=("high","max"), l=("low","min"), c=("close","last"))
    hh6, ll6 = h.h.rolling(6).max().shift(1), h.l.rolling(6).min().shift(1)
    mapP = M.ts.dt.floor("60min").map((h.c.shift(1)-ll6)/(hh6-ll6)).to_numpy()
    g = M.assign(k=M.ts.dt.floor("15min")).groupby("k", sort=True)
    b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"))
    b["fin"] = g.apply(lambda x: x.index[-1], include_groups=False).reindex(b.index)
    b = b[b.index.notna()]
    tr = pd.concat([b.h-b.l, (b.h-b.c.shift(1)).abs(), (b.l-b.c.shift(1)).abs()],
                   axis=1).max(axis=1)
    b["atr"] = tr.rolling(14).mean().shift(1)
    return M, b, mapD, mapP


def resuelve(M, e, lado, r, rr=RR, tope=TOPE):
    """UNA sola expresion para los dos lados. (ver el error de signo del
    documento RESULTADOS_sistema_eurusd_intradia.md)"""
    HH, LL, CC, OO = (M[k].to_numpy() for k in ("high","low","close","open"))
    ent = OO[e]; sl = ent - lado*r; tp = ent + lado*r*rr
    for k in range(e, min(e+tope, len(M))):
        if lado > 0:
            if LL[k] <= sl: return (sl-ent)*lado/r
            if HH[k] >= tp: return rr
        else:
            if HH[k] >= sl: return (sl-ent)*lado/r
            if LL[k] <= tp: return rr
    k = min(e+tope, len(M))-1
    return (CC[k]-ent)*lado/r


def corre(nom, ruta, U, ecn, mino, et_v, tz, h0, h1):
    M, b, mapD, mapP = carga(ruta)
    O,H,L,C,A = (b[k].to_numpy() for k in ("o","h","l","c","atr"))
    FIN = b.fin.to_numpy().astype(int)
    loc = b.index.tz_localize("UTC").tz_convert(tz).tz_localize(None)
    hor = loc.hour + loc.minute/60.0
    dentro = (hor >= h0) & (hor < h1)
    CCm, OOm = M.close.to_numpy(), M.open.to_numpy()
    f = []
    for i in range(20, len(b)-1):
        if not dentro[i] or not np.isfinite(A[i]) or A[i] <= 0: continue
        j = FIN[i]; lado = mapD[j]; p = mapP[j]
        if not (np.isfinite(lado) and lado != 0 and np.isfinite(p)): continue
        lado = int(lado)
        retro = (p < 1/3) if lado > 0 else (p > 2/3)
        conf  = (C[i] > O[i]) if lado > 0 else (C[i] < O[i])
        if not (retro and conf): continue
        e = j+1
        if e >= len(M): continue
        f.append((b.index[i], e, lado, 1.5*A[i]))
    D = pd.DataFrame(f, columns="ts e lado r".split())
    if len(D) < 50: return None
    D["R"]    = [resuelve(M, int(x.e), x.lado,  x.r) for _, x in D.iterrows()]
    D["Rinv"] = [resuelve(M, int(x.e), -x.lado, x.r) for _, x in D.iterrows()]
    D["Rlar"] = [resuelve(M, int(x.e), 1,       x.r) for _, x in D.iterrows()]
    # comprar y aguantar las mismas 4 horas, mismo riesgo, sin stop ni objetivo
    D["Rbh"] = [(CCm[min(int(x.e)+TOPE, len(M))-1]-OOm[int(x.e)])/x.r
                for _, x in D.iterrows()]
    D["rgo"] = D.r/U
    D["cr"], D["crm"] = ecn/D.rgo, mino/D.rgo
    D["dia"] = pd.to_datetime(D.ts).dt.floor("D")
    D["ins"], D["vent"] = nom, et_v
    return D


def z(x, gr):
    m = x.mean()
    su = pd.DataFrame({"x":x.to_numpy(),"g":gr.to_numpy()}).groupby("g").x.apply(
        lambda v:(v-m).sum())
    s2 = float((su**2).sum())
    return m*len(x)/sqrt(s2) if s2>0 else float("nan")


def pf(x):
    g, p = x[x>0].sum(), -x[x<0].sum()
    return g/p if p>0 else np.inf

T = []
print(f"{'instrumento':<9}{'ventana':<18}{'n':>6}{'riesgo':>9}{'coste':>7}{'acierto':>9}"
      f"{'PFbru':>7}{'PFneto':>7}{'R neta':>9}{'z':>7}{'B&H':>8}{'exceso':>8}")
for nom, ruta, U, ecn, mino in INS:
    for et_v, (tz, h0, h1) in VENT.items():
        D = corre(nom, ruta, U, ecn, mino, et_v, tz, h0, h1)
        if D is None: continue
        T.append(D)
        n = D.R - D.cr
        exc = n.mean() - D.Rbh.mean()
        print(f"  {nom:<8}{et_v:<18}{len(D):>6}{D.rgo.median():>9.1f}"
              f"{100*D.cr.mean():>6.1f}%{100*(D.R>0).mean():>8.1f}%{pf(D.R):>7.2f}"
              f"{pf(n):>7.2f}{n.mean():>+9.4f}{z(n,D.dia.astype(str)):>+7.2f}"
              f"{D.Rbh.mean():>+8.4f}{exc:>+8.4f}")

T = pd.concat(T, ignore_index=True)
print("\n" + "="*104)
print("PLACEBOS Y CONTROLES  ·  por instrumento, agregando ventanas")
print("="*104)
print(f"{'instrumento':<10}{'n':>6}{'REAL':>10}{'invertida':>11}{'siempre largo':>15}"
      f"{'comprar y aguantar':>20}{'% largos':>10}")
for nom, _, _, _, _ in INS:
    S = T[T.ins == nom]
    if not len(S): continue
    print(f"  {nom:<8}{len(S):>6}{S.R.mean():>+10.4f}{S.Rinv.mean():>+11.4f}"
          f"{S.Rlar.mean():>+15.4f}{S.Rbh.mean():>+20.4f}{100*(S.lado>0).mean():>9.0f}%")

print("\n" + "="*104)
print("COSTE MINORISTA en vez de ECN  ·  R neta")
print("="*104)
for nom, _, _, ecn, mino in INS:
    S = T[T.ins == nom]
    if not len(S): continue
    print(f"  {nom:<8} ECN {(S.R-S.cr).mean():>+9.4f}  (coste {100*S.cr.mean():>4.1f}%)"
          f"   minorista {(S.R-S.crm).mean():>+9.4f}  (coste {100*S.crm.mean():>4.1f}%)")
