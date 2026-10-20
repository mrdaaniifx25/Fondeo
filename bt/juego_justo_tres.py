"""El mismo juego justo en los TRES instrumentos del repositorio.

Motivo: con una sola operacion al dia en EUR/USD la aprobacion del examen es
26,2 %; con tres apuestas casi independientes al dia sube a 35,5 % (ver
docs/RESULTADOS_lo_simple.md). Tres instrumentos dan esas tres apuestas sin
apilar riesgo correlacionado en el mismo par.

  python3 bt/juego_justo_tres.py
"""
import numpy as np, pandas as pd, sys

RR, KSTOP, TOPE_D = 2.0, 1.0, 5
# coste ida y vuelta en unidades de precio, por instrumento (conservador)
COSTE = {"eurusd": 1.0e-4, "xauusd": 0.35, "grxeur": 2.0}

def mide(nombre):
    M = pd.read_parquet(f"data/{nombre}_m1.parquet")
    M["loc"] = M.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid").dt.tz_localize(None)
    ny = M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None)
    M["dfx"] = (ny - pd.Timedelta(hours=17)).dt.floor("D")
    D = M.groupby("dfx").agg(o=("open", "first"), h=("high", "max"),
                             l=("low", "min"), c=("close", "last")).sort_index()
    tr = pd.concat([D.h - D.l, (D.h - D.c.shift()).abs(),
                    (D.l - D.c.shift()).abs()], axis=1).max(axis=1)
    D["atr"] = tr.rolling(14).mean().shift(1)
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
        j = ord_d[d]; atr = D.atr.iloc[j]
        if not np.isfinite(atr) or atr <= 0:
            continue
        limite = int(fin_de[dias[min(j + TOPE_D, len(dias) - 1)]])
        if limite <= p0 + 5:
            continue
        rgo = KSTOP * atr
        f = {"dia": d, "rgo": rgo}
        for lado in (1, -1):
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
            f[f"R{lado:+d}"] = r / rgo
        out.append(f)
    R = pd.DataFrame(out)
    R["coste"] = COSTE[nombre] / R.rgo
    return R, D

print(f"Juego justo · stop {KSTOP:.2f} x ATR diaria · objetivo {RR:.0f}R · "
      f"tope {TOPE_D} dias · apertura de Londres\n")
print(f"  {'instrumento':<12}{'n':>6}{'coste/rgo':>11}{'acierto':>9}"
      f"{'bruto':>9}{'neto':>9}{'z':>7}")
guardado = {}
for nombre in ("eurusd", "xauusd", "grxeur"):
    R, D = mide(nombre)
    guardado[nombre] = R
    amb = pd.concat([R["R+1"], R["R-1"]]).to_numpy()
    cos = pd.concat([R.coste, R.coste]).to_numpy()
    se = amb.std(ddof=1) / np.sqrt(len(amb))
    print(f"  {nombre:<12}{len(amb):>6}{cos.mean():>11.4f}"
          f"{100*(amb-cos>0).mean():>8.1f}%{amb.mean():>9.4f}"
          f"{(amb-cos).mean():>9.4f}{(amb-cos).mean()/se:>7.2f}")
    sys.stdout.flush()

print("\n  por lados, para que no sea el espejo:")
print(f"  {'instrumento':<12}{'lado':<8}{'n':>6}{'bruto':>9}{'neto':>9}{'z':>7}")
for nombre, R in guardado.items():
    for lado in ("+1", "-1"):
        r = R[f"R{lado}"].to_numpy(); c = R.coste.to_numpy()
        se = r.std(ddof=1) / np.sqrt(len(r))
        print(f"  {nombre:<12}{('compra' if lado=='+1' else 'venta'):<8}{len(r):>6}"
              f"{r.mean():>9.4f}{(r-c).mean():>9.4f}{(r-c).mean()/se:>7.2f}")

print("\n  CORRELACION de los resultados diarios entre instrumentos (compra ciega):")
J = pd.concat([R.set_index("dia")["R+1"].rename(n) for n, R in guardado.items()],
              axis=1).dropna()
print(J.corr().round(3).to_string())
print(f"\n  dias con los tres a la vez: {len(J)}")
print("  Si la correlacion es baja, tres instrumentos SON tres apuestas y el")
print("  examen pasa del 26,2 % (una al dia) al 35,5 % (tres al dia).")
