"""El juego justo, version con rejilla de stop y tope, y desglose de salidas.

Lo que arregla respecto a bt/juego_justo.py: con stop de 106 pips y tope de 3
dias casi ninguna operacion llegaba a las barreras, asi que la estructura 1:2
no se materializaba y el "acierto" no era el acierto. Aqui se barre el ancho
del stop y el tope temporal, y se informa QUE fraccion resuelve en barrera.

  python3 bt/juego_justo2.py
"""
import numpy as np, pandas as pd, sys

COSTE_PIPS, RR = 1.0, 2.0
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")

D = M.groupby("dfx").agg(o=("open", "first"), h=("high", "max"),
                         l=("low", "min"), c=("close", "last")).sort_index()
tr = pd.concat([D.h - D.l, (D.h - D.c.shift()).abs(), (D.l - D.c.shift()).abs()],
               axis=1).max(axis=1)
D["atr"] = tr.rolling(14).mean().shift(1)               # ATR hasta AYER
dias = D.index.to_numpy(); ord_d = {d: i for i, d in enumerate(dias)}
fin_de = dict(zip(M.dfx.drop_duplicates().to_numpy(), M.groupby("dfx").size().cumsum().to_numpy()))

M["hm"] = M["loc"].dt.hour * 60 + M["loc"].dt.minute
ent = M[(M.hm >= 8 * 60) & (M.hm < 9 * 60)].groupby("dfx").head(1).set_index("dfx")
fila = dict(zip(M.ts.to_numpy(), range(len(M))))
pos_ent = np.array([fila[t] for t in ent.ts.to_numpy()])
H = M.high.to_numpy(); L = M.low.to_numpy(); C = M.close.to_numpy()

def resuelve(p0, px, sl, tp, lado, limite):
    hi = H[p0:limite]; lo = L[p0:limite]
    if lado > 0:
        gs = lo <= sl; gt = hi >= tp
    else:
        gs = hi >= sl; gt = lo <= tp
    ks = int(np.argmax(gs)) if gs.any() else 10**9
    kt = int(np.argmax(gt)) if gt.any() else 10**9
    if ks == kt == 10**9:
        return (C[limite - 1] - px) * lado, "tiempo"
    if ks <= kt:
        return (sl - px) * lado, "stop"
    return (tp - px) * lado, "objetivo"

def corre(kstop, tope_d):
    out = []
    for d, px, p0 in zip(ent.index.to_numpy(), ent.open.to_numpy(), pos_ent):
        if d not in ord_d:
            continue
        j = ord_d[d]
        atr = D.atr.iloc[j]
        if not np.isfinite(atr) or atr <= 0:
            continue
        jl = min(j + tope_d, len(dias) - 1)
        limite = int(fin_de[dias[jl]])
        if limite <= p0 + 5:
            continue
        rgo = kstop * atr
        f = {"dia": d, "rgo": rgo}
        for lado in (1, -1):
            r, com = resuelve(p0, px, px - lado * rgo, px + lado * RR * rgo, lado, limite)
            f[f"R{lado:+d}"] = r / rgo
            f[f"c{lado:+d}"] = com
        out.append(f)
    R = pd.DataFrame(out)
    R["coste"] = (COSTE_PIPS * 1e-4) / R.rgo
    return R

print("EUR/USD · una operacion al dia en la apertura de Londres · objetivo 2R")
print(f"coste {COSTE_PIPS:.1f} pip ida y vuelta · empates resueltos como perdida\n")
print(f"  {'stop':>14}{'tope':>6}{'n':>6}{'coste/rgo':>11}"
      f"{'%barrera':>10}{'%obj':>7}{'bruto':>9}{'neto':>9}{'z':>7}")
mejores = []
for kstop in (0.25, 0.5, 0.75, 1.0, 1.5):
    for tope_d in (1, 2, 5, 20):
        R = corre(kstop, tope_d)
        amb = pd.concat([R["R+1"], R["R-1"]]).to_numpy()
        com = pd.concat([R["c+1"], R["c-1"]]).to_numpy()
        cos = pd.concat([R.coste, R.coste]).to_numpy()
        n = len(amb)
        barrera = (com != "tiempo").mean(); obj = (com == "objetivo").mean()
        bruto = amb.mean(); neto = (amb - cos).mean()
        se = amb.std(ddof=1) / np.sqrt(n)
        z = neto / se
        pips = 10000 * R.rgo.median()
        print(f"  {f'{kstop:.2f}xATR({pips:.0f}p)':>14}{tope_d:>6}{n:>6}"
              f"{cos.mean():>11.4f}{100*barrera:>9.1f}%{100*obj:>6.1f}%"
              f"{bruto:>9.4f}{neto:>9.4f}{z:>7.2f}")
        mejores.append((abs(bruto), kstop, tope_d, barrera, obj, bruto, neto, z, se, n))
        sys.stdout.flush()

print("\n" + "=" * 86)
print("CONTROL PRINCIPAL: compra ciega + venta ciega juntas debe dar bruto ~ 0")
print("=" * 86)
print("  Si sale ~0 en TODAS las celdas, el mercado es exactamente justo a este")
print("  horizonte y lo unico que quitaba dinero era el diferencial.\n")

# la celda operable: resuelve el mismo dia, coste bajo, estructura 1:2 real
R = corre(0.5, 2)
amb = pd.concat([R["R+1"], R["R-1"]]).to_numpy()
com = pd.concat([R["c+1"], R["c-1"]]).to_numpy()
cos = pd.concat([R.coste, R.coste]).to_numpy()
neto = amb - cos
print("=" * 86)
print("LA CELDA OPERABLE · stop 0,50 x ATR · tope 2 dias")
print("=" * 86)
print(f"  n {len(neto)} · coste {100*cos.mean():.2f} % del riesgo")
print(f"  salidas: objetivo {100*(com=='objetivo').mean():.1f} % · "
      f"stop {100*(com=='stop').mean():.1f} % · tiempo {100*(com=='tiempo').mean():.1f} %")
print(f"  bruto {amb.mean():+.4f} R · neto {neto.mean():+.4f} R · "
      f"z {neto.mean()/(amb.std(ddof=1)/np.sqrt(len(amb))):+.2f}")

# ---- la parte para su cabeza: rachas
print()
print("=" * 86)
print("RACHAS · lo que tiene que esperar antes de que le pase")
print("=" * 86)
gana = (R["R+1"].to_numpy() - R.coste.to_numpy()) > 0      # un lado, en orden temporal
p = gana.mean()
print(f"  con acierto {100*p:.1f} % (compra ciega, neto):")
rachas = []
act = 0
for g in gana:
    if g:
        rachas.append(act) if act else None
        act = 0
    else:
        act += 1
if act:
    rachas.append(act)
rachas = np.array(rachas)
print(f"  racha de perdidas: mediana {np.median(rachas):.0f} · "
      f"p90 {np.percentile(rachas,90):.0f} · PEOR observada {rachas.max():.0f}")
rng = np.random.default_rng(3)
peor100 = [(lambda g: max((len(s) for s in "".join("01"[int(x)] for x in g).split("1")), default=0))(
    rng.random(100) < p) for _ in range(20000)]
peor100 = np.array(peor100)
print(f"  peor racha en 100 operaciones: mediana {np.median(peor100):.0f} · "
      f"p90 {np.percentile(peor100,90):.0f} · p99 {np.percentile(peor100,99):.0f}")
print(f"  P(al menos una racha de 8+ en 100 ops): {100*(peor100>=8).mean():.0f} %")

print()
print("=" * 86)
print("HONESTIDAD: A+B juntos es casi tautologico (son el mismo trade en espejo).")
print("La prueba de verdad es que NINGUN lado y NINGUNA direccion se separe sola.")
print("=" * 86)
D["mom12"] = np.sign(D.c - D.c.shift(252)).shift(1)
D["dia_ant"] = np.sign(D.c - D.o).shift(1)
for kstop, tope_d in ((1.0, 5), (1.0, 20)):
    R = corre(kstop, tope_d)
    R["mom12"] = [D.mom12.iloc[ord_d[d]] for d in R.dia]
    R["dia_ant"] = [D.dia_ant.iloc[ord_d[d]] for d in R.dia]
    print(f"\n  stop {kstop:.2f} x ATR ({10000*R.rgo.median():.0f} pips) · tope {tope_d} dias"
          f" · coste {100*R.coste.mean():.2f} % del riesgo")
    print(f"    {'brazo':<30}{'n':>6}{'acierto':>9}{'bruto':>9}{'neto':>9}{'z':>7}")
    def di(nom, r, c):
        r = np.asarray(r, float); c = np.asarray(c, float)
        n = len(r); se = r.std(ddof=1) / np.sqrt(n)
        print(f"    {nom:<30}{n:>6}{100*(r-c>0).mean():>8.1f}%"
              f"{r.mean():>9.4f}{(r-c).mean():>9.4f}{(r-c).mean()/se:>7.2f}")
    di("A · compra ciega", R["R+1"], R.coste)
    di("B · venta ciega", R["R-1"], R.coste)
    for nom, s in (("C · momento 12 meses", R.mom12),
                   ("E · continuacion dia ant.", R.dia_ant),
                   ("F · reversion dia ant.", -R.dia_ant)):
        m = s.isin([1.0, -1.0]).to_numpy()
        di(nom, np.where(s[m] > 0, R["R+1"][m], R["R-1"][m]), R.coste[m])
    amb = pd.concat([R["R+1"], R["R-1"]]).to_numpy()
    se = amb.std(ddof=1) / np.sqrt(len(amb))
    print(f"    -> error estandar {se:.4f} R · detecta {2*se:+.4f} a z=2 ·"
          f" los +0,149 R que necesita saldrian a z {0.149/se:.1f}")
