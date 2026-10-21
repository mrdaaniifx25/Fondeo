"""Pre-registro docs/PREREGISTRO_dax_horario.md

El CRT desnudo en DAX, partido por si la entrada cae en el horario operable
del usuario (08-12h y 13-16h de Madrid).

Reutiliza el codigo de bt/crt_por_temporalidad.py sin reimplementar nada.
"""
import sys; sys.path.insert(0, "bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

RUTA, U, COSTE = "data/grxeur_m1.parquet", 1.0, 1.6
TFS = [("H1",1),("H2",2),("H4",4),("H6",6),("H8",8),("H12",12),("D1",24)]

m1 = pd.read_parquet(RUTA); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
anos = (m1.ts.max() - m1.ts.min()).days / 365.25
print(f"DAX (GRXEUR) · {m1.ts.min():%Y-%m-%d} a {m1.ts.max():%Y-%m-%d} · {anos:.1f} anios")
print(f"coste {COSTE} puntos · horario operable 08-12h y 13-16h de Madrid\n")
print(f"{'TF':<5} {'tramo':<16} {'n':>6} {'al anio':>8} {'acierto':>8} {'R:R':>6} "
      f"{'riesgo':>8} {'coste':>7} {'R BRUTA':>9} {'IC95':>19} {'R NETA':>9}")
print("-"*120)

for tfn, tfh in TFS:
    ref = velas_ref(m1, tfh, ancla_ny=1)
    if len(ref) < 50: print(f"{tfn:<5} (pocas velas)"); continue
    h, l, c = (ref[x].to_numpy() for x in ("high","low","close"))
    a = C.atr(h, l, c, 20)
    seq = LM.secuencias(ref, usar_cuerpo=False)
    if seq.empty: continue
    seq = LM.resuelve(seq, ref, m1, tfh, a)
    seq = seq[seq.k == 1].dropna(subset=["nat","rr"]).copy()
    if seq.empty: continue
    seq["riesgo_u"] = (seq.entrada - seq.stop).abs()/U
    seq = seq[seq.riesgo_u > 0]
    seq["R"] = np.where(seq.nat > 0, seq.rr, -1.0)
    seq["Rn"] = seq.R - COSTE/seq.riesgo_u
    fin = ref["fin"].to_numpy()
    loc = pd.DatetimeIndex(fin[seq.i_ent.to_numpy()]).tz_localize("UTC").tz_convert("Europe/Madrid")
    hh = loc.hour.to_numpy()
    dentro = ((hh >= 8) & (hh < 12)) | ((hh >= 13) & (hh < 16))
    for nom, T in (("DENTRO 8-12/13-16", seq[dentro]), ("fuera", seq[~dentro]),
                   ("todo", seq)):
        if len(T) < 40: print(f"{tfn:<5} {nom:<16} {len(T):>6,}  (pocas)"); continue
        x = T.R.to_numpy(); ee = 1.96*x.std(ddof=1)/np.sqrt(len(x))
        print(f"{tfn:<5} {nom:<16} {len(T):>6,} {len(T)/anos:>8.0f} "
              f"{100*(T.R > 0).mean():>7.1f}% {T.rr.median():>6.2f} "
              f"{T.riesgo_u.median():>7.1f}p {100*(COSTE/T.riesgo_u).median():>6.1f}% "
              f"{x.mean():>+9.3f} [{x.mean()-ee:>+8.3f},{x.mean()+ee:>+8.3f}] "
              f"{T.Rn.mean():>+9.3f}")
    print()
