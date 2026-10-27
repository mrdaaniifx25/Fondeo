"""La version definitiva: una posicion por instrumento, sin solapar, con el P&L
diario MARCADO A MERCADO de verdad.

Por que asi y no de otra forma:
  - stop ancho (1,0 x ATR diaria) -> el coste es el 1,4 % del riesgo, no el 67 %
  - objetivo 2R alcanzable        -> hace falta dejar correr varios dias
  - UNA posicion por instrumento  -> como maximo 3 abiertas, exposicion acotada
  - P&L diario marcado a mercado  -> el limite diario del 3 % se mide BIEN

  python3 bt/version_final.py
"""
import numpy as np, pandas as pd, sys

RR, KSTOP, TOPE_D = 2.0, 1.0, 5
COSTE = {"eurusd": 1.0e-4, "xauusd": 0.35, "grxeur": 2.0}
NOM = {"eurusd": "EUR/USD", "xauusd": "oro", "grxeur": "DAX"}
F1, F2, DIA, TOT = 0.08, 0.05, 0.03, 0.10

def opera(nombre):
    M = pd.read_parquet(f"data/{nombre}_m1.parquet")
    M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
    ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")
    D = M.groupby("dfx").agg(o=("open", "first"), h=("high", "max"),
                             l=("low", "min"), c=("close", "last")).sort_index()
    tr = pd.concat([D.h - D.l, (D.h - D.c.shift()).abs(),
                    (D.l - D.c.shift()).abs()], axis=1).max(axis=1)
    D["atr"] = tr.rolling(14).mean().shift(1)
    D["dir"] = np.sign(D.c - D.o).shift(1)
    dias = D.index.to_numpy(); ord_d = {d: i for i, d in enumerate(dias)}
    fin_de = dict(zip(M.dfx.drop_duplicates().to_numpy(),
                      M.groupby("dfx").size().cumsum().to_numpy()))
    M["hm"] = M["loc"].dt.hour * 60 + M["loc"].dt.minute
    ent = M[(M.hm >= 8*60) & (M.hm < 9*60)].groupby("dfx").head(1).set_index("dfx")
    fila = dict(zip(M.ts.to_numpy(), range(len(M))))
    H = M.high.to_numpy(); L = M.low.to_numpy(); C = M.close.to_numpy()
    cierre = D.c.to_numpy()
    # minuto final de cada dia FX, para marcar a mercado
    fin_min = {d: int(fin_de[d]) - 1 for d in dias if d in fin_de}

    ops = []
    j = 0
    while j < len(dias):
        d = dias[j]
        if d not in ent.index or not np.isfinite(D.atr.iloc[j]) or D.atr.iloc[j] <= 0 \
           or D["dir"].iloc[j] not in (1.0, -1.0):
            j += 1; continue
        px = float(ent.open.loc[d]); p0 = fila[ent.ts.loc[d]]
        lado = int(D["dir"].iloc[j]); rgo = KSTOP * float(D.atr.iloc[j])
        jl = min(j + TOPE_D, len(dias) - 1)
        limite = int(fin_de[dias[jl]])
        if limite <= p0 + 5:
            j += 1; continue
        sl = px - lado*rgo; tp = px + lado*RR*rgo
        hi = H[p0:limite]; lo = L[p0:limite]
        gs = (lo <= sl) if lado > 0 else (hi >= sl)
        gt = (hi >= tp) if lado > 0 else (lo <= tp)
        ks = int(np.argmax(gs)) if gs.any() else 10**9
        kt = int(np.argmax(gt)) if gt.any() else 10**9
        if ks == kt == 10**9:
            kfin, pxs, com = limite - 1 - p0, float(C[limite-1]), "tiempo"
        elif ks <= kt:
            kfin, pxs, com = ks, sl, "stop"
        else:
            kfin, pxs, com = kt, tp, "objetivo"
        pfin = p0 + kfin
        # dia FX en que sale
        jsal = j
        while jsal < len(dias) and fin_de[dias[jsal]] - 1 < pfin:
            jsal += 1
        jsal = min(jsal, len(dias)-1)
        ops.append({"j_ent": j, "j_sal": jsal, "px": px, "pxs": pxs, "lado": lado,
                    "rgo": rgo, "com": com,
                    "R": (pxs-px)*lado/rgo - COSTE[nombre]/rgo})
        j = jsal + 1                              # SIN SOLAPAR
    O = pd.DataFrame(ops)

    # ---- P&L diario marcado a mercado
    dR = np.zeros(len(dias))
    for o in ops:
        a, b = o["j_ent"], o["j_sal"]
        marca = o["px"]
        for jj in range(a, b+1):
            m = o["pxs"] if jj == b else float(cierre[jj])
            dR[jj] += (m - marca) * o["lado"] / o["rgo"]
            marca = m
        dR[b] -= COSTE[nombre] / o["rgo"]
    return O, pd.Series(dR, index=dias)

print("VERSION FINAL · una posicion por instrumento, sin solapar")
print(f"stop {KSTOP:.1f}xATR diaria · objetivo {RR:.0f}R · tope {TOPE_D} dias · "
      f"direccion = continuacion del dia anterior\n")
print(f"  {'instr':<9}{'n ops':>7}{'ops/anio':>10}{'acierto':>9}{'%obj':>7}"
      f"{'%stop':>7}{'neto R':>9}{'z':>7}")
S = {}
for nombre in ("eurusd", "xauusd", "grxeur"):
    O, dR = opera(nombre); S[nombre] = dR
    se = O.R.std(ddof=1)/np.sqrt(len(O))
    anios = len(dR)/252
    print(f"  {NOM[nombre]:<9}{len(O):>7}{len(O)/anios:>10.0f}{100*(O.R>0).mean():>8.1f}%"
          f"{100*(O.com=='objetivo').mean():>6.1f}%{100*(O.com=='stop').mean():>6.1f}%"
          f"{O.R.mean():>9.4f}{O.R.mean()/se:>7.2f}")
    sys.stdout.flush()

dia_R = pd.concat(S, axis=1).fillna(0.0).sum(axis=1)
dia_R = dia_R[pd.concat(S, axis=1).notna().any(axis=1)]
print(f"\n  serie diaria MARCADA: {len(dia_R)} dias · R/dia {dia_R.mean():+.4f}"
      f" · sigma {dia_R.std():.3f}")
print(f"  peor dia {dia_R.min():+.2f} R · mejor {dia_R.max():+.2f} R · "
      f"dias con algo abierto {100*(dia_R!=0).mean():.0f} %")

def examen(v, rg, n=20000, semilla=5, tope=300):
    v = v - v.mean()
    N = len(v); rng = np.random.default_rng(semilla)
    p1 = p2 = mdia = 0; dur = []
    for _ in range(n):
        a = rng.integers(0, max(N-tope, 1))
        d = v[a:a+tope]*rg
        saldo = 0.0; fase = 0; meta = F1
        for t in range(len(d)):
            saldo += d[t]
            if d[t] <= -DIA:
                mdia += 1; break
            if saldo <= -TOT: break
            if saldo >= meta:
                if fase == 0: fase, saldo, meta = 1, 0.0, F2
                else: fase = 2; dur.append(t); break
        if fase >= 1: p1 += 1
        if fase == 2: p2 += 1
    return p1/n, p2/n, (np.median(dur) if dur else float("nan")), mdia/n

print("\n" + "=" * 80)
print("EL EXAMEN · serie diaria marcada, deriva QUITADA, bloques moviles")
print("=" * 80)
v = dia_R.to_numpy().astype(float)
print(f"   {'riesgo':>8}{'expos. max':>12}{'fase 1':>9}"
      f"{'LAS DOS':>10}{'dias med':>10}{'muere dia':>11}")
mejor = None
for rg in (0.005, 0.0075, 0.010, 0.0125, 0.015, 0.020):
    p1, p2, md, mdia = examen(v, rg)
    print(f"   {100*rg:>7.2f}%{f'{100*3*rg:.2f} %':>12}{100*p1:>8.1f}%{100*p2:>9.1f}%"
          f"{md:>10.0f}{100*mdia:>10.1f}%")
    if mejor is None or p2 > mejor[1]: mejor = (rg, p2, p1, md, mdia)
    sys.stdout.flush()
print(f"\n   MEJOR: riesgo {100*mejor[0]:.2f} % -> fase 1 {100*mejor[2]:.1f} % · "
      f"LAS DOS {100*mejor[1]:.1f} % · {mejor[3]:.0f} dias · muere dia {100*mejor[4]:.1f} %")

print("\n  RACHAS de dias en rojo:")
act = dia_R[dia_R != 0]
g = (act > 0).to_numpy(); rach = []; c = 0
for x in g:
    if x:
        if c: rach.append(c)
        c = 0
    else: c += 1
if c: rach.append(c)
rach = np.array(rach)
print(f"    dias en verde {100*g.mean():.0f} % · mediana {np.median(rach):.0f} · "
      f"p90 {np.percentile(rach,90):.0f} · peor {rach.max():.0f}")

print("\n" + "=" * 80)
print("EL TOPE DE TIEMPO LO DECIDE TODO")
print("=" * 80)
print("  Los examenes de FundingPips de 2 fases no tienen limite de dias (hay que")
print("  confirmarlo en SU cuenta). Si no hay limite, arriesgar MENOS es mejor:")
print("  la barrera da 10/(8+10) = 55,6 % sea lenta o rapida, y el limite diario")
print("  del 3 % deja de morder.\n")
print(f"   {'riesgo':>8}{'tope 300d: LAS DOS':>21}{'tope 1200d: LAS DOS':>22}"
      f"{'muere dia':>11}{'dias med':>10}")
for rg in (0.0025, 0.005, 0.0075, 0.010, 0.015):
    _, p300, _, _ = examen(v, rg, tope=300)
    p1L, p2L, mdL, mdiaL = examen(v, rg, tope=1200, n=8000)
    print(f"   {100*rg:>7.2f}%{100*p300:>20.1f}%{100*p2L:>21.1f}%"
          f"{100*mdiaL:>10.1f}%{mdL:>10.0f}")
    sys.stdout.flush()
print("\n  teorico sin limite de tiempo ni de dia: 10/18 x 10/15 = 37,0 %")
