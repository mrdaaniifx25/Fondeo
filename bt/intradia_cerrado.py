"""Version sin solapamiento: se abre y se cierra DENTRO del dia.

Arregla un fallo del modelo anterior: con tope de 5 dias y 3 operaciones al dia
habria hasta 15 posiciones abiertas, cuyo movimiento conjunto puede romper el
limite diario del 3 % aunque mi simulacion lo diera a 0,0 % (yo atribuia el
resultado de cada operacion al dia en que se ABRIA, no a los dias que vivia).

Con cierre dentro del dia el P&L diario es exactamente el de las operaciones de
ese dia, el modelo es exacto, y de paso no hay riesgo de fin de semana ni swap.

  python3 bt/intradia_cerrado.py
"""
import numpy as np, pandas as pd, sys

RR, KSTOP = 2.0, 1.0
COSTE = {"eurusd": 1.0e-4, "xauusd": 0.35, "grxeur": 2.0}
NOM = {"eurusd": "EUR/USD", "xauusd": "oro", "grxeur": "DAX"}
F1, F2, DIA, TOT, VENT = 0.08, 0.05, 0.03, 0.10, 92

def series(nombre, kstop=KSTOP):
    M = pd.read_parquet(f"data/{nombre}_m1.parquet")
    M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
    ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")
    D = M.groupby("dfx").agg(o=("open", "first"), h=("high", "max"),
                             l=("low", "min"), c=("close", "last")).sort_index()
    tr = pd.concat([D.h - D.l, (D.h - D.c.shift()).abs(),
                    (D.l - D.c.shift()).abs()], axis=1).max(axis=1)
    D["atr"] = tr.rolling(14).mean().shift(1)
    D["dir"] = np.sign(D.c - D.o).shift(1)          # continuacion del dia anterior
    dias = D.index.to_numpy(); ord_d = {d: i for i, d in enumerate(dias)}
    fin_de = dict(zip(M.dfx.drop_duplicates().to_numpy(),
                      M.groupby("dfx").size().cumsum().to_numpy()))
    M["hm"] = M["loc"].dt.hour * 60 + M["loc"].dt.minute
    ent = M[(M.hm >= 8 * 60) & (M.hm < 9 * 60)].groupby("dfx").head(1).set_index("dfx")
    fila = dict(zip(M.ts.to_numpy(), range(len(M))))
    pos = np.array([fila[t] for t in ent.ts.to_numpy()])
    H = M.high.to_numpy(); L = M.low.to_numpy(); C = M.close.to_numpy()
    out = []
    for d, px, p0 in zip(ent.index.to_numpy(), ent.open.to_numpy(), pos):
        if d not in ord_d:
            continue
        j = ord_d[d]; atr = D.atr.iloc[j]; lado = D["dir"].iloc[j]
        if not np.isfinite(atr) or atr <= 0 or lado not in (1.0, -1.0):
            continue
        limite = int(fin_de[d])                      # FIN DEL MISMO DIA FX
        if limite <= p0 + 5:
            continue
        lado = int(lado); rgo = kstop * atr
        sl = px - lado * rgo; tp = px + lado * RR * rgo
        hi = H[p0:limite]; lo = L[p0:limite]
        gs = (lo <= sl) if lado > 0 else (hi >= sl)
        gt = (hi >= tp) if lado > 0 else (lo <= tp)
        ks = int(np.argmax(gs)) if gs.any() else 10**9
        kt = int(np.argmax(gt)) if gt.any() else 10**9
        if ks == kt == 10**9:
            r, com = (C[limite - 1] - px) * lado, "cierre"
        elif ks <= kt:
            r, com = (sl - px) * lado, "stop"
        else:
            r, com = (tp - px) * lado, "objetivo"
        out.append({"dia": d, "neto": r / rgo - COSTE[nombre] / rgo, "com": com,
                    "horas": None})
    return pd.DataFrame(out)

print("INTRADIA CERRADO · abre 08:00 Madrid, cierra al final del dia FX")
print(f"direccion = continuacion del dia anterior · stop {KSTOP:.1f}xATR · objetivo {RR:.0f}R\n")
print(f"  {'instr':<9}{'n':>6}{'acierto':>9}{'%obj':>7}{'%stop':>7}{'%cierre':>9}"
      f"{'neto':>9}{'z':>7}")
G = {}
for nombre in ("eurusd", "xauusd", "grxeur"):
    R = series(nombre); G[nombre] = R
    se = R.neto.std(ddof=1) / np.sqrt(len(R))
    print(f"  {NOM[nombre]:<9}{len(R):>6}{100*(R.neto>0).mean():>8.1f}%"
          f"{100*(R.com=='objetivo').mean():>6.1f}%{100*(R.com=='stop').mean():>6.1f}%"
          f"{100*(R.com=='cierre').mean():>8.1f}%{R.neto.mean():>9.4f}"
          f"{R.neto.mean()/se:>7.2f}")
    sys.stdout.flush()
T = pd.concat(G.values())
se = T.neto.std(ddof=1) / np.sqrt(len(T))
print(f"  {'LAS TRES':<9}{len(T):>6}{100*(T.neto>0).mean():>8.1f}%"
      f"{100*(T.com=='objetivo').mean():>6.1f}%{100*(T.com=='stop').mean():>6.1f}%"
      f"{100*(T.com=='cierre').mean():>8.1f}%{T.neto.mean():>9.4f}{T.neto.mean()/se:>7.2f}")

dia_R = pd.concat([R.set_index("dia").neto.rename(n) for n, R in G.items()],
                  axis=1).sum(axis=1, min_count=1).dropna()
print(f"\n  serie diaria: {len(dia_R)} dias · R/dia {dia_R.mean():+.4f} · "
      f"sigma {dia_R.std():.3f} · peor dia {dia_R.min():.2f} R · mejor {dia_R.max():.2f} R")
print("  (el P&L diario es EXACTO: no hay posiciones abiertas de otros dias)")

def examen(v, rg, n=20000, semilla=5, tope=300, dos=True):
    v = v - v.mean()                                  # deriva quitada: lo honesto
    N = len(v); rng = np.random.default_rng(semilla)
    p1 = p2 = md = 0; dur = []; mdia = 0
    for _ in range(n):
        a = rng.integers(0, max(N - tope, 1))
        d = v[a:a + tope] * rg
        saldo = 0.0; fase = 0; meta = F1
        for t in range(len(d)):
            saldo += d[t]
            if d[t] <= -DIA:
                mdia += 1; break
            if saldo <= -TOT:
                break
            if saldo >= meta:
                if fase == 0:
                    fase = 1; saldo = 0.0; meta = F2
                else:
                    fase = 2; dur.append(t); break
        if fase >= 1: p1 += 1
        if fase == 2: p2 += 1
    return p1/n, p2/n, (np.median(dur) if dur else float("nan")), mdia/n

print("\n" + "=" * 78)
print("EL EXAMEN · bootstrap de bloques sobre la serie real, deriva QUITADA")
print("=" * 78)
v = dia_R.to_numpy().astype(float)
print(f"   {'riesgo':>8}{'exposicion/dia':>16}{'fase 1':>9}{'LAS DOS':>10}"
      f"{'dias med':>10}{'muere dia':>11}")
for rg in (0.005, 0.0075, 0.010, 0.0125, 0.015):
    p1, p2, md, mdia = examen(v, rg)
    print(f"   {100*rg:>7.2f}%{f'{100*3*rg:.2f} %':>16}{100*p1:>8.1f}%{100*p2:>9.1f}%"
          f"{md:>10.0f}{100*mdia:>10.1f}%")
    sys.stdout.flush()

print("\n  RACHAS de dias en rojo (para la cabeza):")
g = (dia_R > 0).to_numpy(); rach = []; act = 0
for x in g:
    if x:
        if act: rach.append(act)
        act = 0
    else: act += 1
if act: rach.append(act)
rach = np.array(rach)
print(f"    dias en verde {100*g.mean():.0f} % · racha roja mediana "
      f"{np.median(rach):.0f} · p90 {np.percentile(rach,90):.0f} · peor {rach.max():.0f}")
