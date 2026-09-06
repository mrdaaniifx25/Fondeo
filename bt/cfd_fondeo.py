"""Lo mismo que bt/alto_winrate_optimo.py, pero en CFDs y con las reglas de
FundingPips: dos fases, 8 % y 5 %, limite diario 5 %, limite total 10 %.

Ajusta la geometria en 2020-2023 y la comprueba en 2024-2026.

  COSTE=2.0 python3 bt/cfd_fondeo.py
"""
import os, itertools, numpy as np, pandas as pd
os.environ.setdefault("SIMS","20000")
exec(open("bt/alto_winrate.py").read().split("# ---------------------------------------------------------------- pase")[0])

CUENTA = 10_000.0
OBJ1, OBJ2 = 0.08, 0.05
LIM_DIA, LIM_TOT = 0.05, 0.10
DMAX, DMIN = 60, 3
CST   = float(os.environ.get("COSTE", 2.0))   # puntos de US100, ida y vuelta
SIMS  = 20000
rng   = np.random.default_rng(20260905)

S = sesiones("data/nsxusd_m1.parquet")
rango = float(np.median([hh.max()-ll.min() for _,_,_,hh,ll,_ in S]))
print(f"US100 · {len(S)} sesiones · rango diario mediano {rango:.1f} pts "
      f"· coste asumido {CST:.1f} pts\n")

def fase(pnl, obj):
    """P(pasar una fase). pnl en fraccion de la cuenta, una operacion al dia."""
    x  = rng.choice(pnl, size=(SIMS, DMAX), replace=True)
    eq = np.cumsum(x, 1); idx = np.arange(DMAX)[None,:]
    fal = (eq <= -LIM_TOT) | (x <= -LIM_DIA)      # total o diario
    pas = (eq >= obj) & (idx >= DMIN-1)
    ip = np.where(pas.any(1), pas.argmax(1), DMAX+9)
    if_= np.where(fal.any(1), fal.argmax(1), DMAX+9)
    ok = ip < if_
    return float(ok.mean()), (float(np.median(ip[ok])) if ok.any() else float("nan"))

SLF  = (0.25, 0.35, 0.50, 0.75, 1.00)
RR   = (1.0, 1.5, 2.0, 3.0, 5.0)
RSK  = (0.005, 0.0075, 0.01, 0.015, 0.02, 0.03)   # riesgo por operacion

filas = []
for f, r in itertools.product(SLF, RR):
    sl = f*rango; tp = sl/r
    v = []
    for dia, mm, oo, hh, ll, cc in S:
        k5 = int(np.searchsorted(mm, 9*60+35))
        if k5 >= len(mm)-10: continue
        _, g = resuelve(hh, ll, cc, k5, float(oo[k5]), tp, sl, +1)
        v.append((dia.year, (g-CST)/sl))          # en R netas
    T = pd.DataFrame(v, columns=["anio","R"])
    for k in RSK:
        A = T[T.anio<=2023].R.to_numpy()*k
        B = T[T.anio>=2024].R.to_numpy()*k
        a1,_  = fase(A, OBJ1); a2,_ = fase(A, OBJ2)
        b1,d1 = fase(B, OBJ1); b2,d2 = fase(B, OBJ2)
        filas.append(dict(slf=f, rr=r, riesgo=k, sl=sl, tp=tp,
                          ajuste=a1*a2, fuera=b1*b2, f1=b1, f2=b2,
                          R=float(T[T.anio>=2024].R.mean()), dias=d1+d2))
D = pd.DataFrame(filas).sort_values("ajuste", ascending=False)
D.to_csv("data/cfd_fondeo.csv", index=False)

print("  las 8 mejores segun 2020-2023, y lo que hicieron en 2024-2026")
print(f"  {'stop':>6} {'TP':>6} {'riesgo':>7} {'AJUSTE':>8} {'FUERA':>7} "
      f"{'fase1':>7} {'fase2':>7} {'R/op':>8} {'dias':>5}")
for _, x in D.head(8).iterrows():
    print(f"  {x.sl:6.1f} {x.tp:6.1f} {x.riesgo*100:6.2f}% {x.ajuste*100:7.1f}% "
          f"{x.fuera*100:6.1f}% {x.f1*100:6.1f}% {x.f2*100:6.1f}% "
          f"{x.R:+8.3f} {x.dias:5.0f}")
c = np.corrcoef(D.ajuste, D.fuera)[0,1]
print(f"\n  correlacion ajuste-fuera de muestra ({len(D)} celdas): {c:+.3f}")
print(f"  techo teorico con ventaja CERO: "
      f"{(LIM_TOT/(OBJ1+LIM_TOT))*(LIM_TOT/(OBJ2+LIM_TOT))*100:.1f} %")

p = float(D.iloc[0].fuera)
print(f"\n=== la economia del boleto en FundingPips ===")
print(f"  P(fondeado) con la mejor geometria, fuera de muestra: {p*100:.1f} %")
for cuota in (89, 189, 349, 549):
    print(f"    cuota {cuota:4d} EUR  ->  la cuenta fondeada tiene que rendir "
          f"mas de {cuota/p:6.0f} EUR de media para que el boleto no pierda")
print(f"\n  comparativa con la evaluacion de futuros medida ayer:")
print(f"    futuros  P 34,4 %  cuota   80 EUR  ->  umbral   233 EUR")
print(f"    CFD      P {p*100:4.1f} %  cuota  349 EUR  ->  umbral {349/p:6.0f} EUR")

# ---------------------------------------------------------------- la fondeada
print("\n=== y despues, la cuenta fondeada ===")
mej = D.iloc[0]
sl = mej.sl; tp = mej.tp; k = mej.riesgo
v = []
for dia, mm, oo, hh, ll, cc in S:
    k5 = int(np.searchsorted(mm, 9*60+35))
    if k5 >= len(mm)-10: continue
    _, g = resuelve(hh, ll, cc, k5, float(oo[k5]), tp, sl, +1)
    v.append((dia.year, (g-CST)/sl*k))
T = pd.DataFrame(v, columns=["anio","x"])
pnl = T[T.anio>=2024].x.to_numpy()

RETIRO, REPARTO, DMAXF = 0.05, 0.80, 500
def fondeada(pnl, sims=SIMS):
    """Retira cada vez que toca +5 %; muere al -10 %. Devuelve retiradas."""
    x  = rng.choice(pnl, size=(sims, DMAXF), replace=True)
    ret = np.zeros(sims); eq = np.zeros(sims); viva = np.ones(sims, bool)
    for j in range(DMAXF):
        eq = np.where(viva, eq + x[:, j], eq)
        muere = viva & ((eq <= -LIM_TOT) | (x[:, j] <= -LIM_DIA))
        viva &= ~muere
        cobra = viva & (eq >= RETIRO)
        ret += cobra; eq = np.where(cobra, 0.0, eq)
    return ret
R_ = fondeada(pnl)
print(f"  retiradas por cuenta fondeada: media {R_.mean():.2f}  "
      f"mediana {np.median(R_):.0f}  ·  {float((R_==0).mean())*100:.0f} % no retira nunca")
print(f"  (modelo de barreras: retira al +5 %, muere al -10 %, reparto {REPARTO*100:.0f} %)")
print(f"\n  {'cuenta':>8} {'cuota':>7} {'por retirada':>13} {'esperado':>10} "
      f"{'EV boleto':>10} {'x la cuota':>11} {'13 boletos':>11}")
for cta, cuota in ((5000,49),(10000,89),(25000,189),(50000,349),(100000,549)):
    porret = cta*RETIRO*REPARTO
    esp    = R_.mean()*porret
    ev     = p*esp - cuota
    print(f"  {cta:8d} {cuota:7d} {porret:13.0f} {p*esp:10.0f} "
          f"{ev:+10.0f} {p*esp/cuota:10.1f}x {13*cuota:11d}")
