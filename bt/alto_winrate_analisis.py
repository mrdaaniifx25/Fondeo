"""Analisis del pase de bt/alto_winrate.py: prediccion 5, tope de contratos,
esperanza del boleto y numero de evaluaciones necesarias."""
import numpy as np, pandas as pd

OBJ, DD, DIAMIN, NMAX, SIMS = 3000., 2000., 5, 200, 20000
rng = np.random.default_rng(20260905)
D = pd.read_csv("data/alto_winrate.csv"); D["res"] = D.nres/D.n

# ---- P5 · cuanto mata la regla de consistencia, por geometria -------------
def pasa(pnl, consis, modo="estatico"):
    x  = rng.choice(pnl, size=(SIMS, NMAX), replace=True)
    eq = np.cumsum(x,1); mx = np.maximum.accumulate(x,1); pk = np.maximum.accumulate(eq,1)
    umb = -DD if modo=="estatico" else np.minimum(pk-DD, 0.0)
    fal = eq <= umb; idx = np.arange(NMAX)[None,:]
    p = (eq>=OBJ) & (idx>=DIAMIN-1) & (mx <= consis*eq)
    ip = np.where(p.any(1), p.argmax(1), NMAX+9)
    if_= np.where(fal.any(1), fal.argmax(1), NMAX+9)
    return float(np.mean(ip < if_))

print("=== P5 · descalificacion por la regla de consistencia (40 %) ===")
print("   simulado sin coste y con drawdown estatico, para aislar la regla\n")
print(f"   {'TP:SL':>6} {'phi':>5} {'sin regla':>10} {'con regla':>10} {'coste de la regla':>19}")
res5 = []
for rr in ("1:1","1:3","1:10","1:30"):
    for phi in (0.5, 1.0):
        S = D[(D.rr==rr)&(D.phi==phi)&(D.instr=="NASDAQ")&(D.entrada=="A")]
        if not len(S): continue
        r = S.iloc[len(S)//2]
        # reconstruye el pnl bruto en dolares de esa celda: gana/pierde/mercado
        # (aproximacion: distribucion de dos puntos con la tasa de barrera)
        w = r.wrr; g, p = r.gana, r.perd
        pnl = np.where(rng.random(20000) < w, g, -p)
        a = pasa(pnl, 1e9); b = pasa(pnl, 0.40)
        res5.append((rr, phi, a, b, a-b))
        print(f"   {rr:>6} {phi:>5.2f} {a*100:9.1f}% {b*100:9.1f}% {(a-b)*100:+18.1f} pp")
alto = np.mean([x[4] for x in res5 if x[0] in ("1:10","1:30")])
bajo = np.mean([x[4] for x in res5 if x[0] in ("1:1","1:3")])
print(f"\n   coste medio de la regla   alto acierto {alto*100:+.1f} pp"
      f"   ·   bajo acierto {bajo*100:+.1f} pp")
print(f"   P5 predecia que mataria 10 pp MAS a las de bajo acierto: "
      f"{'SE CUMPLE' if bajo-alto >= 0.10 else 'NO SE CUMPLE'}")

# ---- tope de contratos de las prop firms reales --------------------------
print("\n=== mejores celdas respetando el tope de contratos ===")
for tope, quien in ((5,"tipo Topstep 50K"), (10,"tipo Apex 50K")):
    B = D[D.ctr <= tope].sort_values("pdin", ascending=False).head(3)
    print(f"\n  tope {tope} micros ({quien})")
    for _, r in B.iterrows():
        print(f"    {r.instr:6s} entrada {r.entrada}  stop {r.sl:6.1f} pts  "
              f"TP {r.tp:6.1f} pts  x{int(r.ctr)}  "
              f"gana {r.gana:6.0f}$ / pierde {r.perd:6.0f}$  "
              f"acierto {r.wrr*100:4.1f}%  neto/op {r.usd:+7.2f}$  "
              f"P {r.pest*100:4.1f}/{r.pdin*100:4.1f}%  mediana {r.dias:.0f} dias")

# ---- la esperanza del boleto --------------------------------------------
print("\n=== la esperanza del boleto ===")
CUOTA, PAGO = 80.0, 1823.0
for etiq, p in (("simulacion, mejor celda con tope 5", float(D[D.ctr<=5].pdin.max())),
                ("simulacion, mejor celda sin tope",  float(D.pdin.max())),
                ("observado por el psicologo (13/78)", 13/78)):
    ev = p*PAGO - CUOTA
    be = CUOTA/p
    n90 = int(np.ceil(np.log(0.10)/np.log(1-p)))
    print(f"  {etiq:36s} P {p*100:5.1f}%  EV {ev:+8.0f} EUR  "
          f"umbral de pago {be:5.0f} EUR  "
          f"evaluaciones para 90 % de acabar en verde: {n90} ({n90*CUOTA:.0f} EUR)")
