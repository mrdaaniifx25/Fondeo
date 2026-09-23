"""Dos cosas que faltaban.

1) El nulo fuerte: mismas HORAS DEL DIA y mismo reparto de lados, pero en
   fechas al azar. Si la deriva es de la finta sobrevive; si era 'las 9 de la
   manana en el EURUSD', se cae.
2) Juntar los tres instrumentos en unidades de su propio ruido. Si el efecto
   es relativo y universal, juntarlos es donde mas potencia hay.
"""
import numpy as np, pandas as pd
exec(open("bt/deriva.py").read().split("for ins, (ruta, U, coste) in INS.items():")[0])
COSTES = {"EURUSD": 1.43e-4, "oro": 0.35, "DAX": 1.6}

todo = []          # (r/sigma, instrumento+mes)
print("nulo fuerte: misma hora del dia, mismo lado, fecha al azar\n" + "-"*78)
for ins, (ruta, U, _) in INS.items():
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    mts = m1.ts.to_numpy("datetime64[ns]"); mc = m1.close.to_numpy()
    ev = sucesos(velas(m1, 60), 8)["finta"]
    R, mes = mide(ev, mts, mc, U)
    sig = R[:, 0].std(ddof=1)
    todo.append((R[:, 0]/sig, np.array([ins+"|"+x for x in mes])))

    # --- N4: misma hora del dia, fecha al azar
    t = pd.DatetimeIndex([x[0] for x in ev]); s = np.array([x[1] for x in ev], float)
    horas = t.hour.to_numpy()
    mh = pd.DatetimeIndex(mts)
    por_hora = {hh: np.flatnonzero((mh.hour == hh) & (mh.minute == 0)) for hh in set(horas)}
    tope = len(mts) - 200*60
    fal = []
    for hh, ss in zip(horas, s):
        c = por_hora[hh]; c = c[c < tope]
        if len(c): fal.append((mts[rng.choice(c)], ss))
    Rn, mesn = mide(fal, mts, mc, U)
    m0, l0, h0 = bloques(R[:, :1], mes); m1n, l1n, h1n = bloques(Rn[:, :1], mesn)
    print(f"  {ins:<8} senal {m0[0]/sig:+.4f} [{l0[0]/sig:+.4f}, {h0[0]/sig:+.4f}]   "
          f"nulo-hora {m1n[0]/sig:+.4f} [{l1n[0]/sig:+.4f}, {h1n[0]/sig:+.4f}]"
          f"{'   <- el nulo tambien' if l1n[0] > 0 else ''}")

# --- juntando los tres, en sigmas
r = np.concatenate([a for a, _ in todo]); g = np.concatenate([b for _, b in todo])
R2 = r.reshape(-1, 1)
med, lo, hi = bloques(R2, g)
print(f"\nlos tres juntos, en sigmas:  n {len(r):,}   {med[0]:+.4f} [{lo[0]:+.4f}, {hi[0]:+.4f}]")
print(f"  coste en sigmas:  EURUSD 0,1359   oro 0,0415   DAX 0,0304")
sem = (hi[0]-lo[0])/2
print(f"\npotencia: para distinguir del cero un efecto de {med[0]:+.4f} hace falta")
for ins, n_act, mde in (("oro", 1246, 0.0574), ("DAX", 965, 0.0737)):
    need = n_act * (mde/max(med[0], 1e-9))**2
    print(f"  {ins}: ~{need:,.0f} sucesos (tiene {n_act:,}) = {need/n_act:.1f} veces mas historico")
