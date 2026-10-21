"""El patron EXACTO de sus capturas de demo, medido sobre 5 anios.

De su grafico: "Sesiones Europe/Madrid 0000 0800 1400 2300" y
"0800-1100 1300-1600" -> rango de Asia 00:00-08:00 Madrid, killzone de
Londres 08:00-11:00 y de NY 13:00-16:00.

El patron: dentro de la killzone, el precio BARRE el extremo del rango de Asia
y CIERRA de vuelta dentro -> se opera contra el barrido. Stop tras la mecha,
objetivo en R o en el extremo opuesto de Asia.

EL CONTROL QUE DECIDE: "vender siempre a esa hora", misma geometria. Si el
patron no bate a eso, el nivel no aporta: aporta la hora y la tendencia.

  python3 bt/su_patron_londres.py
"""
import numpy as np, pandas as pd
from math import sqrt
rng = np.random.default_rng(20261014)

U, COSTE, HOR = 1e-4, 0.70, 6*60
M = pd.read_parquet("data/eurusd_m1.parquet")
M["ts"] = pd.to_datetime(M["ts"])
M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
loc = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
M["dia"] = loc.dt.floor("D"); M["h"] = loc.dt.hour + loc.dt.minute/60.0
HH, LL, OO, CC = (M[k].to_numpy() for k in ("high","low","open","close"))

# velas M15 en hora de Madrid
g = M.assign(k=loc.dt.floor("15min")).groupby("k", sort=True)
b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"),
          fin=("high", lambda x: x.index[-1]))
b = b[b.index.notna()]
tr = pd.concat([b.h-b.l, (b.h-b.c.shift(1)).abs(), (b.l-b.c.shift(1)).abs()], axis=1).max(axis=1)
b["atr"] = tr.rolling(14).mean().shift(1)
B = b.index
hb = B.hour + B.minute/60.0
dib = pd.Series(B).dt.floor("D").to_numpy()

# rango de Asia del propio dia: 00:00-08:00 Madrid
asia = M[(M.h >= 0) & (M.h < 8)].groupby("dia").agg(ah=("high","max"), al=("low","min"))
AH = pd.Series(dib).map(asia.ah).to_numpy()
AL = pd.Series(dib).map(asia.al).to_numpy()
O15,H15,L15,C15,A15 = (b[k].to_numpy() for k in ("o","h","l","c","atr"))
FIN = b.fin.to_numpy().astype(int)

VENT = {"Londres 08-11": (8, 11), "NuevaYork 13-16": (13, 16)}

def resuelve(e, lado, rgo, rec):
    ent = OO[e]; sl = ent - lado*rgo; tp = ent + lado*rec
    a, z2 = e, min(e+HOR, len(M))
    hh, ll = HH[a:z2], LL[a:z2]
    if lado > 0:
        ks = np.nonzero(ll <= sl)[0]; kt = np.nonzero(hh >= tp)[0]
    else:
        ks = np.nonzero(hh >= sl)[0]; kt = np.nonzero(ll <= tp)[0]
    fs = ks[0] if len(ks) else 10**9; ft = kt[0] if len(kt) else 10**9
    return (rec/rgo) if ft < fs else (-1.0 if fs < 10**9 else 0.0)

def genera(h0, h1, modo, stop, obj):
    """modo: 'barrido' (el suyo) | 'ciego' (entrar en la 1a vela de la ventana)"""
    ops = []
    vistos = set()
    for i in range(2, len(b)-1):
        if not (h0 <= hb[i] < h1): continue
        if not np.isfinite(A15[i]) or A15[i] <= 0: continue
        if not (np.isfinite(AH[i]) and np.isfinite(AL[i])): continue
        e = FIN[i] + 1
        if e >= len(M): continue
        d = dib[i]
        if modo == "ciego":
            if d in vistos: continue
            vistos.add(d)
            for lado in (1, -1):
                ent = OO[e]
                rgo = 1.5*A15[i] if stop == "atr" else abs(ent - (L15[i] if lado>0 else H15[i]))
                if rgo <= 0: continue
                rec = (obj*rgo) if obj > 0 else abs((AH[i] if lado>0 else AL[i]) - ent)
                if rec <= 0: continue
                ops.append((B[i], d, lado, rgo/U, resuelve(e, lado, rgo, rec), rec/rgo))
            continue
        # el patron suyo: barrido del extremo de Asia + cierre de vuelta dentro
        lado = 0
        if H15[i] >= AH[i] and C15[i] < AH[i] and L15[i] > AL[i]: lado = -1
        elif L15[i] <= AL[i] and C15[i] > AL[i] and H15[i] < AH[i]: lado = 1
        if lado == 0: continue
        if (d, lado) in vistos: continue
        vistos.add((d, lado))
        ent = OO[e]
        mecha = H15[i] if lado < 0 else L15[i]
        rgo = 1.5*A15[i] if stop == "atr" else abs(ent - mecha)
        if rgo <= 0: continue
        rec = (obj*rgo) if obj > 0 else abs((AL[i] if lado < 0 else AH[i]) - ent)
        if rec <= 0: continue
        ops.append((B[i], d, lado, rgo/U, resuelve(e, lado, rgo, rec), rec/rgo))
    D = pd.DataFrame(ops, columns="ts dia lado rgo R rr".split())
    if len(D): D["cr"] = COSTE/D.rgo; D["n"] = D.R - D.cr
    return D

def z(x, gr):
    m = x.mean()
    su = pd.DataFrame({"x":x.to_numpy(),"g":gr.to_numpy()}).groupby("g").x.apply(lambda v:(v-m).sum())
    s2 = float((su**2).sum())
    return m*len(x)/sqrt(s2) if s2>0 else np.nan

print(f"{'':<34}{'n':>6}{'R:R':>6}{'riesgo':>8}{'coste':>7}{'acierto':>9}{'geom':>7}"
      f"{'bruta':>9}{'NETA':>9}{'z':>7}")
def ficha(et, D):
    if D is None or len(D) < 30: return print(f"  {et:<32} (pocas)")
    geo = (D.rgo/(D.rgo + D.rr*D.rgo)).mean()
    print(f"  {et:<32}{len(D):>6}{D.rr.mean():>6.2f}{D.rgo.median():>8.1f}"
          f"{100*D.cr.mean():>6.1f}%{100*(D.R>0).mean():>8.1f}%{100*geo:>6.1f}%"
          f"{D.R.mean():>+9.4f}{D.n.mean():>+9.4f}{z(D.n, D.dia.astype(str)):>+7.2f}")
    return D

RES = {}
for et, (h0, h1) in VENT.items():
    print(f"\n=== {et} ===")
    for stop in ("mecha", "atr"):
        for obj, eo in ((2.0, "R:R 2"), (3.0, "R:R 3"), (-1, "extremo opuesto Asia")):
            D = genera(h0, h1, "barrido", stop, obj)
            RES[(et, stop, eo)] = ficha(f"SU PATRON · stop {stop} · {eo}", D)
    for obj, eo in ((2.0, "R:R 2"), (-1, "extremo opuesto Asia")):
        C = genera(h0, h1, "ciego", "atr", obj)
        if len(C):
            ficha(f"CONTROL ciego (los dos lados) · {eo}", C)
            ficha(f"CONTROL ciego CORTO · {eo}", C[C.lado < 0])
            ficha(f"CONTROL ciego LARGO · {eo}", C[C.lado > 0])

print("\n" + "="*96)
print("RACHAS: ¿cuantas veces salen 6 GANADAS SEGUIDAS en su propio patron?")
print("="*96)
D = RES[("Londres 08-11", "mecha", "R:R 2")]
if D is not None and len(D):
    D = D.sort_values("ts")
    gan = (D.n > 0).to_numpy()
    rachas, c, mx = 0, 0, 0
    for v in gan:
        c = c+1 if v else 0
        mx = max(mx, c)
        if c == 6: rachas += 1
    print(f"  operaciones: {len(D)}   acierto neto: {100*gan.mean():.1f} %")
    print(f"  veces que se encadenan 6 ganadas: {rachas}")
    print(f"  racha maxima de ganadas: {mx}")
    p = gan.mean()
    print(f"  probabilidad de 6 seguidas con ese acierto: {100*p**6:.2f} %")
    print(f"  esperadas en {len(D)} operaciones: {len(D)*p**6:.1f}")
    # ventanas de 6 consecutivas con las 6 ganadas
    v6 = sum(1 for i in range(len(gan)-5) if gan[i:i+6].all())
    print(f"  ventanas de 6 consecutivas TODAS ganadas: {v6} de {max(len(gan)-5,0)}")
