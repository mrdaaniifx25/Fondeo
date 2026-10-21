"""El juego justo: que queda cuando el coste baja al 1 % del riesgo.

Pre-registro: docs/PREREGISTRO_juego_justo.md

Una operacion al dia, apertura de Londres, stop de 1,5 x ATR DIARIA (~100 pips)
para que el coste pase del 67 % del riesgo al 1 %. ~1.400 dias: error estandar
0,038 R, potencia para ver +0,075 R a z=2.

  python3 bt/juego_justo.py
"""
import numpy as np, pandas as pd, sys

COSTE_PIPS, KSTOP, RR, TOPE_D = 1.0, 1.5, 2.0, 3
M = pd.read_parquet("data/eurusd_m1.parquet")
M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")      # dia FX, cierre 17:00 NY

# ---- barras diarias y ATR
D = M.groupby("dfx").agg(o=("open", "first"), h=("high", "max"),
                         l=("low", "min"), c=("close", "last")).sort_index()
tr = pd.concat([D.h - D.l, (D.h - D.c.shift()).abs(), (D.l - D.c.shift()).abs()],
               axis=1).max(axis=1)
D["atr"] = tr.rolling(14).mean()
D["mom12"] = np.sign(D.c - D.c.shift(252))
D["mx20"] = D.c.rolling(20).max().shift(1)
D["mn20"] = D.c.rolling(20).min().shift(1)
D["dia_ant"] = np.sign(D.c - D.o).shift(1)
print(f"dias FX: {len(D)}   {D.index[0].date()} -> {D.index[-1].date()}")

# ---- la barra de entrada: primer minuto >= 08:00 Madrid de cada dia FX
M["hm"] = M["loc"].dt.hour * 60 + M["loc"].dt.minute
cand = M[(M.hm >= 8 * 60) & (M.hm < 9 * 60)]
ent = cand.groupby("dfx").head(1).set_index("dfx")
print(f"dias con apertura de Londres localizada: {len(ent)}")

H = M.high.to_numpy(); L = M.low.to_numpy(); C = M.close.to_numpy()
POS = {d: i for i, d in enumerate(M.index.to_numpy())}
idx_ent = ent.index.to_numpy()
fila = {d: i for i, d in enumerate(M.ts.to_numpy())}
pos_ent = np.array([fila[t] for t in ent.ts.to_numpy()])

# limite temporal: TOPE_D dias FX despues
dias = D.index.to_numpy()
ord_d = {d: i for i, d in enumerate(dias)}
ult = M.groupby("dfx").size().cumsum().to_numpy()      # fin de cada dia FX en filas
fin_de = dict(zip(M.dfx.drop_duplicates().to_numpy(), ult))

def resuelve(p0, ent_px, sl, tp, lado, limite):
    """Minuto a minuto desde p0 hasta limite. Devuelve R bruto."""
    hi = H[p0:limite]; lo = L[p0:limite]
    if lado > 0:
        ks = np.argmax(lo <= sl) if (lo <= sl).any() else 10**9
        kt = np.argmax(hi >= tp) if (hi >= tp).any() else 10**9
    else:
        ks = np.argmax(hi >= sl) if (hi >= sl).any() else 10**9
        kt = np.argmax(lo <= tp) if (lo <= tp).any() else 10**9
    if ks == kt == 10**9:
        return (C[limite - 1] - ent_px) * lado
    if ks <= kt:                                        # empate -> perdida
        return (sl - ent_px) * lado
    return (tp - ent_px) * lado

res = []
for d, px, p0 in zip(idx_ent, ent.open.to_numpy(), pos_ent):
    if d not in ord_d:
        continue
    j = ord_d[d]
    atr = D.atr.iloc[j - 1] if j > 0 else np.nan        # ATR hasta AYER: causal
    if not np.isfinite(atr) or atr <= 0:
        continue
    jl = min(j + TOPE_D, len(dias) - 1)
    limite = int(fin_de[dias[jl]])
    if limite <= p0 + 5:
        continue
    rgo = KSTOP * atr
    fila_r = {"dia": d, "atr": atr, "rgo": rgo}
    for lado in (1, -1):
        sl = px - lado * rgo
        tp = px + lado * RR * rgo
        fila_r[f"R{lado:+d}"] = resuelve(p0, px, sl, tp, lado, limite) / rgo
    fila_r["mom12"] = D.mom12.iloc[j - 1] if j > 0 else np.nan
    fila_r["canal"] = (1.0 if px > (D.mx20.iloc[j] or 0) else
                       (-1.0 if (D.mn20.iloc[j] is not None and px < D.mn20.iloc[j]) else 0.0))
    fila_r["dia_ant"] = D.dia_ant.iloc[j]
    res.append(fila_r)

R = pd.DataFrame(res).dropna(subset=["R+1", "R-1"])
R["coste"] = (COSTE_PIPS * 1e-4) / R.rgo                # coste en R
print(f"operaciones resueltas: {len(R)}")
print(f"ATR diaria mediana: {10000*R.atr.median():.1f} pips -> stop "
      f"{10000*R.rgo.median():.0f} pips")
print(f"COSTE en R: mediana {R.coste.median():.4f}  = "
      f"{100*R.coste.median():.2f} % del riesgo\n")

def informe(nombre, r, c):
    n = len(r)
    if n < 30:
        print(f"  {nombre:<34}{n:>6}  (muestra insuficiente)")
        return
    bruto = r.mean(); neto = (r - c).mean()
    se = r.std(ddof=1) / np.sqrt(n)
    z = neto / se if se > 0 else np.nan
    win = (r > 0).mean()
    pf_g = r[r > 0].sum() / abs(r[r < 0].sum()) if (r < 0).any() else np.nan
    print(f"  {nombre:<34}{n:>6}{100*win:>8.1f}%{bruto:>9.4f}{neto:>9.4f}"
          f"{z:>8.2f}{pf_g:>8.2f}")

print("=" * 86)
print("EL JUEGO JUSTO · una operacion al dia · stop 1,5 x ATR diaria · objetivo 2R")
print("=" * 86)
print(f"  {'brazo':<34}{'n':>6}{'acierto':>8}{'bruto':>9}{'neto':>9}{'z neto':>8}{'PF br':>8}")
informe("A · compra ciega", R["R+1"], R.coste)
informe("B · venta ciega", R["R-1"], R.coste)
amb = pd.concat([R["R+1"], R["R-1"]])
informe("A+B (control: debe dar ~0)", amb, pd.concat([R.coste, R.coste]))
print()
for nom, s in (("C · momento 12 meses", R.mom12),
               ("E · continuacion dia anterior", R.dia_ant),
               ("F · reversion dia anterior", -R.dia_ant)):
    m = s.isin([1.0, -1.0])
    r = np.where(s[m] > 0, R["R+1"][m], R["R-1"][m])
    informe(nom, pd.Series(r), R.coste[m].to_numpy())
m = R.canal != 0
r = np.where(R.canal[m] > 0, R["R+1"][m], R["R-1"][m])
informe("D · canal 20 dias (rotura)", pd.Series(r), R.coste[m].to_numpy())
print()
se = amb.std(ddof=1) / np.sqrt(len(R))
print(f"  error estandar con n={len(R)}: {se:.4f} R -> detecta {2*se:+.4f} R a z=2")
print(f"  ventaja que necesita para 300 EUR/mes sobre 10.000: +0,149 R"
      f"  ->  z = {0.149/se:.1f} si existiera")
