"""Cual de las dos sigo: lo decide P(pasar la fase 1), no la esperanza.

Usa las SERIES DIARIAS REALES medidas, no un modelo iid, con bootstrap de
bloques moviles de 92 dias. Asi las rachas y la dependencia temporal entran
tal como pasaron.

Variantes de direccion, todo lo demas identico (stop 1,0xATR, objetivo 2R,
tope 5 dias, apertura de Londres, 3 instrumentos):
  A  continuacion: la direccion del dia anterior en cada instrumento (~50/50)
  B  momento 12 meses (que en 2021-2026 = largo permanente en oro y DAX)
  B' igual que B pero con la DERIVA QUITADA (lo honesto a futuro)

  python3 bt/cual_sigo.py
"""
import numpy as np, pandas as pd, sys

RR, KSTOP, TOPE_D = 2.0, 1.0, 5
COSTE = {"eurusd": 1.0e-4, "xauusd": 0.35, "grxeur": 2.0}
F1, DIA, TOT, VENT = 0.08, 0.03, 0.10, 92

def series(nombre, modo):
    M = pd.read_parquet(f"data/{nombre}_m1.parquet")
    M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
    ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")
    D = M.groupby("dfx").agg(o=("open", "first"), h=("high", "max"),
                             l=("low", "min"), c=("close", "last")).sort_index()
    tr = pd.concat([D.h - D.l, (D.h - D.c.shift()).abs(),
                    (D.l - D.c.shift()).abs()], axis=1).max(axis=1)
    D["atr"] = tr.rolling(14).mean().shift(1)
    if modo == "A":
        D["dir"] = np.sign(D.c - D.o).shift(1)
    else:
        s = np.sign(D.c - D.c.shift(252)).shift(1)
        D["dir"] = s.groupby(D.index.to_period("M")).transform("first")
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
        limite = int(fin_de[dias[min(j + TOPE_D, len(dias) - 1)]])
        if limite <= p0 + 5:
            continue
        lado = int(lado); rgo = KSTOP * atr
        sl = px - lado * rgo; tp = px + lado * RR * rgo
        hi = H[p0:limite]; lo = L[p0:limite]
        gs = (lo <= sl) if lado > 0 else (hi >= sl)
        gt = (hi >= tp) if lado > 0 else (lo <= tp)
        ks = int(np.argmax(gs)) if gs.any() else 10**9
        kt = int(np.argmax(gt)) if gt.any() else 10**9
        if ks == kt == 10**9:
            r = (C[limite - 1] - px) * lado
        elif ks <= kt:
            r = (sl - px) * lado
        else:
            r = (tp - px) * lado
        out.append({"dia": d, "neto": r / rgo - COSTE[nombre] / rgo})
    return pd.DataFrame(out).set_index("dia").neto

def diaria(modo):
    s = [series(n, modo).rename(n) for n in ("eurusd", "xauusd", "grxeur")]
    J = pd.concat(s, axis=1)
    return J.sum(axis=1, min_count=1).dropna(), J.notna().sum(axis=1)

def examen(dia_R, rg, n=20000, semilla=5, quitar_deriva=False):
    """Bootstrap de bloques moviles de 92 dias sobre la serie real."""
    v = dia_R.to_numpy().astype(float)
    if quitar_deriva:
        v = v - v.mean()
    N = len(v)
    rng = np.random.default_rng(semilla)
    ini = rng.integers(0, N - VENT, size=n)
    paso = fallo_dia = fallo_tot = 0
    for a in ini:
        d = v[a:a + VENT] * rg
        if (d <= -DIA).any():
            k = int(np.argmax(d <= -DIA))
        else:
            k = VENT
        c = np.cumsum(d[:k])
        if len(c) and (c >= F1).any() and (
                not (c <= -TOT).any() or np.argmax(c >= F1) < np.argmax(c <= -TOT)):
            paso += 1
        elif len(c) and (c <= -TOT).any():
            fallo_tot += 1
        elif k < VENT:
            fallo_dia += 1
    return paso / n, fallo_dia / n, fallo_tot / n

print("Que estrategia seguir · lo decide P(pasar la fase 1 en 92 dias)")
print("bootstrap de bloques moviles de 92 dias sobre la serie diaria REAL\n")
for modo, etiq in (("A", "A · continuacion dia anterior (~50/50)"),
                   ("B", "B · momento 12 meses (= largo oro y DAX)")):
    dia_R, ncol = diaria(modo)
    print(f"{etiq}")
    print(f"   dias {len(dia_R)} · operaciones/dia medio {ncol.mean():.2f} · "
          f"R medio/dia {dia_R.mean():+.4f} · sigma {dia_R.std():.3f}")
    print(f"   {'riesgo':>8}{'PASA':>8}{'muere dia':>11}{'muere total':>13}"
          f"{'  (deriva quitada: PASA)':>26}")
    for rg in (0.0025, 0.005, 0.0075, 0.010):
        p, fd, ft = examen(dia_R, rg)
        p2, _, _ = examen(dia_R, rg, quitar_deriva=True)
        print(f"   {100*rg:>7.2f}%{100*p:>7.1f}%{100*fd:>10.1f}%{100*ft:>12.1f}%"
              f"{100*p2:>24.1f}%")
        sys.stdout.flush()
    print()

print("=" * 78)
print("LAS DOS FASES, con la serie real y la deriva QUITADA (lo honesto)")
print("=" * 78)

def dos_fases(dia_R, rg, n=20000, semilla=9, tope=300):
    v = dia_R.to_numpy().astype(float); v = v - v.mean()
    N = len(v); rng = np.random.default_rng(semilla)
    paso1 = paso2 = 0
    dur = []
    for _ in range(n):
        a = rng.integers(0, N - tope) if N > tope else 0
        d = v[a:a + tope] * rg
        saldo = 0.0; fase = 0; meta = F1; muerto = False
        for t in range(len(d)):
            saldo += d[t]
            if d[t] <= -DIA or saldo <= -TOT:
                muerto = True; break
            if saldo >= meta:
                if fase == 0:
                    fase = 1; saldo = 0.0; meta = 0.05
                else:
                    fase = 2; dur.append(t); break
        if fase >= 1: paso1 += 1
        if fase == 2: paso2 += 1
    return paso1 / n, paso2 / n, (np.median(dur) if dur else float("nan"))

for modo, etiq in (("A", "A · continuacion dia anterior"),
                   ("B", "B · momento 12 meses")):
    dia_R, _ = diaria(modo)
    print(f"\n  {etiq}")
    print(f"   {'riesgo':>8}{'fase 1':>9}{'LAS DOS':>10}{'dias med':>10}")
    for rg in (0.005, 0.0075, 0.010):
        p1, p2, md = dos_fases(dia_R, rg)
        print(f"   {100*rg:>7.2f}%{100*p1:>8.1f}%{100*p2:>9.1f}%{md:>10.0f}")
        sys.stdout.flush()
