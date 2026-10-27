"""La estrategia CERRADA: cero decisiones al dia. Direccion = momento 12 meses.

El agujero del plan anterior era la direccion ("la que tu veas"). Se cierra con
la unica regla de direccion del proyecto que tiene un resultado independiente y
potente detras: el momento de 12 meses (RESULTADOS_momento_largo.md, t +5,04
sobre 26 series y 632 meses). Se mira una vez al mes y no se toca.

  python3 bt/estrategia_cerrada.py
"""
import numpy as np, pandas as pd, sys

RR, KSTOP, TOPE_D, RIESGO = 2.0, 1.0, 5, 0.005
COSTE = {"eurusd": 1.0e-4, "xauusd": 0.35, "grxeur": 2.0}
NOM = {"eurusd": "EUR/USD", "xauusd": "oro", "grxeur": "DAX"}

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
    # direccion: precio de AYER contra el de hace 252 dias habiles; se congela
    # el primer dia de cada mes y no se vuelve a mirar hasta el mes siguiente
    señal = np.sign(D.c - D.c.shift(252)).shift(1)
    mes = D.index.to_period("M")
    D["dir"] = señal.groupby(mes).transform("first")
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
            r, com = (C[limite - 1] - px) * lado, "tiempo"
        elif ks <= kt:
            r, com = (sl - px) * lado, "stop"
        else:
            r, com = (tp - px) * lado, "objetivo"
        out.append({"dia": d, "lado": lado, "R": r / rgo,
                    "coste": COSTE[nombre] / rgo, "com": com})
    R = pd.DataFrame(out)
    R["neto"] = R.R - R.coste
    return R

print("ESTRATEGIA CERRADA · cero decisiones al dia")
print(f"direccion = momento 12 meses congelado por mes · stop {KSTOP:.1f}xATR diaria"
      f" · objetivo {RR:.0f}R · tope {TOPE_D} dias\n")
print(f"  {'instr':<9}{'n':>6}{'%largo':>8}{'acierto':>9}{'%obj':>7}"
      f"{'bruto':>9}{'neto':>9}{'z':>7}{'PF':>7}")
G = {}
for nombre in ("eurusd", "xauusd", "grxeur"):
    R = mide(nombre); G[nombre] = R
    se = R.R.std(ddof=1) / np.sqrt(len(R))
    pf = R.neto[R.neto > 0].sum() / abs(R.neto[R.neto < 0].sum())
    print(f"  {NOM[nombre]:<9}{len(R):>6}{100*(R.lado>0).mean():>7.0f}%"
          f"{100*(R.neto>0).mean():>8.1f}%{100*(R.com=='objetivo').mean():>6.1f}%"
          f"{R.R.mean():>9.4f}{R.neto.mean():>9.4f}{R.neto.mean()/se:>7.2f}{pf:>7.2f}")
    sys.stdout.flush()

T = pd.concat([R.assign(instr=n) for n, R in G.items()])
se = T.R.std(ddof=1) / np.sqrt(len(T))
print(f"\n  {'LAS TRES':<9}{len(T):>6}{100*(T.lado>0).mean():>7.0f}%"
      f"{100*(T.neto>0).mean():>8.1f}%{100*(T.com=='objetivo').mean():>6.1f}%"
      f"{T.R.mean():>9.4f}{T.neto.mean():>9.4f}{T.neto.mean()/se:>7.2f}"
      f"{T.neto[T.neto>0].sum()/abs(T.neto[T.neto<0].sum()):>7.2f}")

# ---- la curva de la cartena: 0,50 % por operacion, dia a dia
dia = T.groupby("dia").neto.sum() * RIESGO
cur = dia.cumsum()
pico = cur.cummax()
print(f"\n  CARTERA a 0,50 % por operacion, {len(dia)} dias:")
print(f"    retorno total     {100*cur.iloc[-1]:+.2f} %   "
      f"({100*cur.iloc[-1]/(len(dia)/252):+.2f} % anual)")
print(f"    caida maxima      {100*(cur-pico).min():.2f} %")
print(f"    peor dia          {100*dia.min():.2f} %   "
      f"(limite diario de FundingPips: -3,00 %)")
print(f"    dias por debajo de -2 %: {(dia<-0.02).sum()}  ·  de -3 %: {(dia<-0.03).sum()}")

# ---- rachas sobre la cartera, para su cabeza
g = (dia > 0).to_numpy()
rach, act = [], 0
for x in g:
    if x:
        if act: rach.append(act)
        act = 0
    else:
        act += 1
if act: rach.append(act)
rach = np.array(rach)
print(f"\n  RACHAS DE DIAS en rojo: mediana {np.median(rach):.0f} · "
      f"p90 {np.percentile(rach,90):.0f} · peor {rach.max():.0f}")
print(f"  dias en verde: {100*g.mean():.0f} %")

# ---- descomposicion honesta: cuanto es deriva
print("\n  HONESTIDAD · cuanto de esto es deriva del activo y no la regla:")
for nombre, R in G.items():
    largo = R[R.lado > 0]; corto = R[R.lado < 0]
    print(f"    {NOM[nombre]:<9} largo n={len(largo):<5} neto {largo.neto.mean():+.4f}"
          f"   corto n={len(corto):<5} neto {corto.neto.mean():+.4f}")
