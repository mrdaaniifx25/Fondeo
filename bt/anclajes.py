"""Pre-registro docs/PREREGISTRO_anclajes.md

¿Da lo mismo el CRT en los doce anclajes de la rejilla? Se publican TODOS.
"""
import sys; sys.path.insert(0, "bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = {"DAX": ("data/grxeur_m1.parquet", 1.0, 1.6),
       "EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
       "oro": ("data/xauusd_m1.parquet", 0.01, 35.0)}

def corre(m1, tfh, anc, U, coste):
    ref = velas_ref(m1, tfh, ancla_ny=anc)
    if len(ref) < 60: return None
    h, l, c = (ref[x].to_numpy() for x in ("high","low","close"))
    a = C.atr(h, l, c, 20)
    seq = LM.secuencias(ref, usar_cuerpo=False)
    if seq.empty: return None
    seq = LM.resuelve(seq, ref, m1, tfh, a)
    seq = seq[seq.k == 1].dropna(subset=["nat","rr"]).copy()
    if len(seq) < 40: return None
    seq["rg"] = (seq.entrada - seq.stop).abs()/U
    seq = seq[seq.rg > 0]
    if len(seq) < 40: return None
    seq["R"] = np.where(seq.nat > 0, seq.rr, -1.0)
    seq["Rn"] = seq.R - coste/seq.rg
    fin = ref["fin"].to_numpy()
    loc = pd.DatetimeIndex(fin[seq.i_ent.to_numpy()]).tz_localize("UTC").tz_convert("Europe/Madrid")
    hh = loc.hour.to_numpy()
    seq["suyo"] = ((hh >= 8) & (hh < 12)) | ((hh >= 13) & (hh < 16))
    return seq

for tfn, tfh, nanc in (("H12", 12, 12), ("D1", 24, 24)):
    for ins, (ruta, U, coste) in INS.items():
        m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
        print("\n" + "="*104)
        print(f"{tfn} · {ins} · los {nanc} anclajes, TODOS")
        print("="*104)
        print(f"{'ancla NY':>9} {'cierra (Madrid)':>17} {'n':>6} {'R bruta':>9} "
              f"{'IC95':>19} {'R neta':>9} {'% en su horario':>17}")
        print("-"*104)
        med, ses, netas, suyos = [], [], [], []
        for anc in range(nanc):
            s = corre(m1, tfh, anc, U, coste)
            if s is None: print(f"{anc:>9} {'':>17} (pocas)"); continue
            x = s.R.to_numpy(); se = x.std(ddof=1)/np.sqrt(len(x))
            ref = velas_ref(m1, tfh, ancla_ny=anc)
            horas = sorted(set(pd.DatetimeIndex(ref["fin"]).tz_localize("UTC")
                               .tz_convert("Europe/Madrid").hour))
            med.append(x.mean()); ses.append(se); netas.append(s.Rn.mean())
            suyos.append(100*s.suyo.mean())
            print(f"{anc:>9} {str(horas[:4]):>17} {len(s):>6,} {x.mean():>+9.3f} "
                  f"[{x.mean()-1.96*se:>+8.3f},{x.mean()+1.96*se:>+8.3f}] "
                  f"{s.Rn.mean():>+9.3f} {100*s.suyo.mean():>16.1f}%")
        if len(med) < 3: continue
        med = np.array(med); ses = np.array(ses); netas = np.array(netas)
        w = 1/ses**2; mu = (w*med).sum()/w.sum()
        Q = (w*(med-mu)**2).sum(); gl = len(med)-1
        print("-"*104)
        print(f"{'':>9} media ponderada de la bruta: {mu:+.3f}")
        print(f"{'':>9} dispersion Q = {Q:.2f} con {gl} grados de libertad "
              f"(se espera ~{gl} si todos miden lo mismo)")
        print(f"{'':>9} NETA: peor {netas.min():+.3f} · mediana {np.median(netas):+.3f} "
              f"· MEJOR {netas.max():+.3f}   (el azar da +{0.137 if nanc==12 else 0.164:.3f})")
        print(f"{'':>9} % en su horario: de {min(suyos):.0f} % a {max(suyos):.0f} %")
