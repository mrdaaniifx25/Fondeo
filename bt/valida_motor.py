"""¿Está bien hecho el motor de backtest? Se le meten entradas AL AZAR.

Si el motor es correcto, una entrada al azar con objetivo 1:k tiene que acertar
exactamente 1/(1+k) y dar R bruta CERO. Ni mas ni menos. Si sale otra cosa, el
motor miente y todo el proyecto es basura.

Se usa exactamente el mismo codigo de resolucion que todas las estrategias:
empate dentro del minuto = STOP, entrada al cierre, stop y objetivo desde ahi.

  python3 bt/valida_motor.py
"""
import numpy as np, pandas as pd

RATIOS = [1.0, 2.0, 2.45, 3.0]
STOPS  = [5, 10, 20, 50]        # en pips, para ver si el tamaño del stop sesga
N      = 4000                   # entradas al azar por celda
VIDA   = 48*60                  # minutos de vida

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4),
         "NSXUSD": ("data/nsxusd_m1.parquet", 1e-0)}

for nom, (ruta, U) in INSTR.items():
    d = pd.read_parquet(ruta)
    d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").reset_index(drop=True)
    H, L, C = d.high.to_numpy(), d.low.to_numpy(), d.close.to_numpy()
    n = len(d)
    print(f"\n{nom} · {n:,} minutos")
    print(f"{'stop':>6s} {'ratio':>7s} {'n':>6s} {'acierto':>9s} {'esperado':>9s} "
          f"{'dif':>7s} {'R bruta':>9s} {'z':>7s}")
    print("-"*66)
    for stop in STOPS:
        for k in RATIOS:
            rng = np.random.default_rng(20260906 + int(stop*100 + k*10))
            idx = rng.integers(1000, n - VIDA - 10, N)
            lados = rng.choice([-1, 1], N)
            Rs = []
            for i, lado in zip(idx, lados):
                ent = C[i]; s = stop*U
                stp = ent - lado*s
                tp  = ent + lado*k*s
                hs, ls = H[i+1:i+1+VIDA], L[i+1:i+1+VIDA]
                gs = (ls <= stp) if lado > 0 else (hs >= stp)
                gt = (hs >= tp)  if lado > 0 else (ls <= tp)
                isl = int(np.argmax(gs)) if gs.any() else 10**9
                itp = int(np.argmax(gt)) if gt.any() else 10**9
                if isl == 10**9 and itp == 10**9:
                    # NO se tira: se cierra a mercado, que es lo que hacen las
                    # estrategias. Tirarlas sesga contra el objetivo lejano.
                    sal = C[min(i+VIDA, n-1)]
                    Rs.append(((sal-ent) if lado > 0 else (ent-sal))/s)
                else:
                    Rs.append(-1.0 if isl <= itp else k)       # empate = STOP
            R = np.array(Rs)
            ac = (R >= k-1e-9).mean(); esp = 1/(1+k)
            z  = R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))
            print(f"{stop:5d}p {'1:'+str(k):>7s} {len(R):6d} {100*ac:8.2f} % "
                  f"{100*esp:8.2f} % {100*(ac-esp):+6.2f} {R.mean():+9.4f} {z:+7.2f}")
