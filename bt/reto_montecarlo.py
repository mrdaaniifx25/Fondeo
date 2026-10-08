"""¿Se pasa un challenge con esta estrategia? ¿Y cuánto dura la cuenta?

Bootstrap sobre las R netas reales de SMC-71 en M30 (los 6 instrumentos, sin
el oro). Reglas supuestas de FundingPips: fase 1 objetivo +8 %, fase 2 +5 %,
límite de pérdida total 10 % en las dos.

AVISO: el modelo NO incluye la regla de consistencia, el mínimo de días
operados ni el drawdown móvil. Todas ellas juegan en contra, así que estos
números son OPTIMISTAS.

  python3 bt/reto_montecarlo.py
"""
import glob
import numpy as np, pandas as pd

RK   = 0.0075      # riesgo por operación
SIMS = 20000
RITMO = 16.3       # señales al mes en M30 con los 6 instrumentos

fs = [f for f in sorted(glob.glob("data/smc71_tf30_*.csv")) if "XAUUSD" not in f]
R = pd.concat([pd.read_csv(f) for f in fs]).neta.to_numpy()
rng = np.random.default_rng(11)

def fase(obj, dd, muestra=R, nmax=400, sims=SIMS):
    p = 0
    for _ in range(sims):
        eq = 0.0
        for r in rng.choice(muestra, nmax, replace=True):
            eq += RK*r
            if eq <= -dd: break
            if eq >=  obj: p += 1; break
    return p/sims

if __name__ == "__main__":
    print(f"{len(R)} operaciones reales · R neta media {R.mean():+.3f} · "
          f"desviación {R.std():.3f} · riesgo {100*RK:.2f} % por operación\n")
    p1, p2 = fase(0.08, 0.10), fase(0.05, 0.10)
    print(f"  fase 1 (+8 %, límite -10 %): pasa {100*p1:.1f} %")
    print(f"  fase 2 (+5 %, límite -10 %): pasa {100*p2:.1f} %")
    print(f"  LLEGA A FONDEADO: {100*p1*p2:.1f} %  ->  1 de cada {1/(p1*p2):.1f}")
    print(f"\n  el listón de la pura geometría de las barreras es "
          f"{100*0.10/(0.08+0.10):.1f} % en fase 1: con ventaja CERO se pasa igual")

    sac = []
    for _ in range(SIMS):
        eq = s = 0.0
        for r in rng.choice(R, 3000, replace=True):
            eq += RK*r
            if eq >=  0.05: s += eq; eq = 0.0
            if eq <= -0.10: break
        sac.append(s)
    sac = np.array(sac)
    print(f"\nYa fondeado, retirando cada +5 %, hasta que toca el -10 %:")
    print(f"  retirado medio   {100*sac.mean():+.1f} % de la cuenta")
    print(f"  retirado mediano {100*np.median(sac):+.1f} %")
    print(f"  no retira nada nunca: {100*(sac==0).mean():.1f} % de las veces")

    print("\nQué haría falta para que el fondeo fuese razonable:")
    for m in (R.mean(), 0.10, 0.20, 0.30):
        Rm = R - R.mean() + m
        a, b = fase(0.08, 0.10, Rm, sims=8000), fase(0.05, 0.10, Rm, sims=8000)
        print(f"  R neta media {m:+.3f}  ->  llega a fondeado el {100*a*b:.1f} %")
