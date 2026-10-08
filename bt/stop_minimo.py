"""Pre-registro docs/PREREGISTRO_stop_minimo.md

CRT en H4. Exigir riesgo >= k x ATR y ver si la neta cruza sin que suba el
exceso. Se publican las 15 celdas y el diagnostico por tramo de stop.
"""
import sys; sys.path.insert(0, "bt")
import numpy as np, pandas as pd
from math import sqrt
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("EURUSD","data/eurusd_m1.parquet",1e-4,1.43),
       ("oro","data/xauusd_m1.parquet",0.01,35.0),
       ("DAX","data/grxeur_m1.parquet",1.0,1.6)]
KS = [0.0, 0.25, 0.5, 0.75, 1.0]
RRS = [1.5, 2.0, 3.0]
TFH, HOR = 4, 60*24*5

# ---------- se recogen las operaciones una sola vez ----------
OPS = []   # (rg_u, cr, atr_u, alcista, j0, idx_instr, fecha)
SER = []   # (H, L) por instrumento
for z, (nom, ruta, U, co) in enumerate(INS):
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    ref = velas_ref(m1, TFH, ancla_ny=1)
    h, l, c = (ref[x].to_numpy() for x in ("high","low","close"))
    a = C.atr(h, l, c, 20)
    seq = LM.secuencias(ref, usar_cuerpo=False)
    seq = seq[seq.k == 1].copy()
    seq["rg"] = (seq.entrada - seq.stop).abs()
    seq = seq[seq.rg > 0]
    fin = ref["fin"].to_numpy()
    t1 = m1["ts"].to_numpy()
    SER.append((m1["high"].to_numpy(), m1["low"].to_numpy()))
    for r in seq.itertuples():
        ie = int(r.i_ent)
        if ie >= len(a) or not np.isfinite(a[ie]) or a[ie] <= 0: continue
        j0 = int(np.searchsorted(t1, fin[ie], side="right"))
        if j0 >= len(t1): continue
        OPS.append((r.entrada, r.stop, r.rg, co/(r.rg/U), r.rg/a[ie],
                    bool(r.alcista), j0, z, pd.Timestamp(fin[ie])))
print(f"operaciones recogidas: {len(OPS):,}\n")

def resuelve(RR, kmin):
    G, CR, F = [], [], []
    for e, s, rg, cr, ratr, alc, j0, z, fe in OPS:
        if ratr < kmin: continue
        H, L = SER[z]
        o = e + RR*rg if alc else e - RR*rg
        j1 = min(j0+HOR, len(H))
        hh, ll = H[j0:j1], L[j0:j1]
        if alc: ga, gb = hh >= o, ll <= s
        else:   ga, gb = ll <= o, hh >= s
        ia = int(np.argmax(ga)) if ga.any() else 10**9
        ib = int(np.argmax(gb)) if gb.any() else 10**9
        G.append(0.0 if (ia == 10**9 and ib == 10**9) else (1.0 if ia < ib else 0.0))
        CR.append(cr); F.append(fe)
    return np.array(G), np.array(CR), np.array(F)

print("LAS 15 CELDAS")
print(f"{'R:R':>5} {'k':>5} {'n':>6} {'acierto':>9} {'exceso':>17} {'coste medio':>12} "
      f"{'NETA':>22}")
print("-"*92)
guarda = {}
for RR in RRS:
    for k in KS:
        G, CR, F = resuelve(RR, k)
        if len(G) < 100: print(f"{RR:>5.1f} {k:>5.2f} {len(G):>6,}  (pocas)"); continue
        azar = 1/(1+RR); ex = G.mean()-azar
        eic = 1.96*G.std(ddof=1)/sqrt(len(G))
        Rn = np.where(G == 1, RR, -1.0) - CR
        mn, icn = Rn.mean(), 1.96*Rn.std(ddof=1)/sqrt(len(Rn))
        guarda[(RR,k)] = (G, CR, F, mn, icn)
        print(f"{RR:>5.1f} {k:>5.2f} {len(G):>6,} {100*G.mean():>8.1f}% "
              f"{100*ex:>+6.1f} [{100*(ex-eic):>+5.1f},{100*(ex+eic):>+5.1f}] "
              f"{100*CR.mean():>11.1f}% {mn:>+9.4f} [{mn-icn:>+.4f},{mn+icn:>+.4f}]"
              f"{'  CRUZA' if mn-icn > 0 else ''}")
    print()

print("="*92)
print("DIAGNOSTICO · ¿donde vive el exceso? (R:R 2,0, SIN filtrar, por tramo de stop/ATR)")
print("="*92)
G, CR, F = resuelve(2.0, 0.0)
ratr = np.array([o[4] for o in OPS])
cortes = [0, 0.25, 0.5, 0.75, 1.0, 1.5, 99]
print(f"{'stop/ATR':>12} {'n':>6} {'acierto':>9} {'exceso':>17} {'coste medio':>12} {'neta':>10}")
print("-"*72)
for a_, b_ in zip(cortes, cortes[1:]):
    m = (ratr >= a_) & (ratr < b_)
    if m.sum() < 80: continue
    g, cr = G[m], CR[m]
    ex = g.mean()-1/3; eic = 1.96*g.std(ddof=1)/sqrt(len(g))
    rn = (np.where(g==1, 2.0, -1.0) - cr).mean()
    print(f"{a_:>5.2f}-{b_:<6.2f} {len(g):>6,} {100*g.mean():>8.1f}% "
          f"{100*ex:>+6.1f} [{100*(ex-eic):>+5.1f},{100*(ex+eic):>+5.1f}] "
          f"{100*cr.mean():>11.1f}% {rn:>+10.4f}")

print("\n" + "="*92)
print("PARTIDO EN DOS MITADES · las cuatro celdas con mejor neta")
print("="*92)
mejores = sorted(guarda.items(), key=lambda kv: -kv[1][3])[:4]
for (RR, k), (G, CR, F, mn, icn) in sorted(mejores):
    corte = np.sort(F)[len(F)//2]
    linea = f"  R:R {RR} k {k} "
    for et, m in (("1a", F < corte), ("2a", F >= corte)):
        g, cr = G[m], CR[m]
        if len(g) < 80: continue
        ex = g.mean() - 1/(1+RR)
        rn = np.where(g == 1, RR, -1.0) - cr
        mm, ii = rn.mean(), 1.96*rn.std(ddof=1)/sqrt(len(rn))
        linea += (f"| {et} n {len(g):>5,} exceso {100*ex:>+5.1f} "
                  f"neta {mm:>+.4f} [{mm-ii:>+.4f},{mm+ii:>+.4f}] ")
    print(linea)
print("\n  corte temporal:", pd.Timestamp(np.sort(guarda[(2.0,0.5)][2])[len(guarda[(2.0,0.5)][2])//2]).date())

print("\n" + "="*92)
print("¿Y CUANTO SERIA ESO EN DINERO? (aunque la neta fuese real)")
print("="*92)
print("  riesgo por operacion 0,25 % — el unico nivel que respeta el limite del 10 %")
print(f"{'R:R':>5} {'k':>5} {'n':>6} {'anios':>7} {'ops/anio':>9} {'R/anio':>8} "
      f"{'%/anio':>8} {'€/mes s/50k':>12}")
print("-"*72)
for (RR, k), (G, CR, F, mn, icn) in sorted(guarda.items()):
    if mn <= 0: continue
    f = np.sort(F)
    anios = (pd.Timestamp(f[-1]) - pd.Timestamp(f[0])).days / 365.25
    opa = len(G)/anios; ra = opa*mn; pct = ra*0.25
    print(f"{RR:>5.1f} {k:>5.2f} {len(G):>6,} {anios:>7.1f} {opa:>9.0f} {ra:>+8.1f} "
          f"{pct:>+7.1f}% {50000*pct/100/12:>+11.0f}€")
