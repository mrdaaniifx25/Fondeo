"""El AMD medido en todo el EURUSD. Pre-registro docs/PREREGISTRO_amd.md

Se arma un rango en TODAS las velas, estrecho o no, y se anota su estrechez.
Asi se puede ver si la fase de acumulacion aporta algo o es un adorno.
"""
import numpy as np, pandas as pd
from math import sqrt

ESPM, ESPD = 20, 20
TFS = {"M15": 15, "H1": 60, "H4": 240}
NS = [8, 12, 16, 24, 32]

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)

def velas(mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    return g[g.n >= mins * 0.3].reset_index()

def atr(h, l, c, n):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    s = pd.Series(tr).rolling(n).mean().to_numpy()
    return np.roll(s, 1)          # desplazado: solo velas ya cerradas

def estudio(V, n):
    h = V.h.to_numpy(); l = V.l.to_numpy(); c = V.c.to_numpy()
    N = len(V)
    a14 = atr(h, l, c, 14)
    hi = pd.Series(h).rolling(n).max().to_numpy()
    lo = pd.Series(l).rolling(n).min().to_numpy()
    normal = a14 * sqrt(n)
    ratio = np.where(normal > 0, (hi - lo) / normal, np.nan)

    filas = []
    i = n
    while i < N - 1:
        if not np.isfinite(ratio[i]):
            i += 1; continue
        rHi, rLo, r0 = hi[i], lo[i], ratio[i]
        if not (rHi > rLo):
            i += 1; continue
        # M: sale y cierra de vuelta dentro, dentro de ESPM velas
        manip = -1; lado = 0
        j = i + 1
        while j < min(i + 1 + ESPM, N):
            if h[j] > rHi or l[j] < rLo:
                arriba = h[j] > rHi and rLo < c[j] < rHi
                abajo  = l[j] < rLo and rLo < c[j] < rHi
                if arriba or abajo:
                    manip = j; lado = -1 if arriba else 1
                break                      # sale del rango: o manipula o rompe
            j += 1
        if manip < 0:
            i = max(j, i + 1); continue

        # posicion tras la manipulacion y el azar que le corresponde
        P = c[manip]
        dv = (P - rLo) if lado < 0 else (rHi - P)     # hacia donde se espera ir
        dc = (rHi - P) if lado < 0 else (P - rLo)     # hacia el lado barrido
        if dv <= 0 or dc <= 0:
            i = manip + 1; continue
        azar = dc / (dv + dc)

        # D: cierre mas alla del extremo contrario, antes que volver al barrido
        hecho = 0; k = manip + 1
        while k < min(manip + 1 + ESPD, N):
            if lado < 0:
                if c[k] < rLo: hecho = 1; break
                if c[k] > rHi: break
            else:
                if c[k] > rHi: hecho = 1; break
                if c[k] < rLo: break
            k += 1
        filas.append((r0, lado, hecho, azar, manip - i, k - manip))
        i = manip + 1
    return pd.DataFrame(filas, columns=["ratio","lado","D","azar","velasM","velasD"])

print(f"{'tf':>4}{'n':>4}{'secuencias':>12}{'completa':>10}{'azar':>8}"
      f"{'diferencia':>12}{'IC95':>20}{'velas A→M':>11}")
todo = {}
for tf, mins in TFS.items():
    V = velas(mins)
    for n in NS:
        D = estudio(V, n)
        if len(D) < 100: continue
        todo[(tf, n)] = D
        dif = D.D - D.azar
        m, s = dif.mean(), dif.std(ddof=1)
        ic = 1.96 * s / sqrt(len(D))
        print(f"{tf:>4}{n:>4}{len(D):>12,}{100*D.D.mean():>9.1f} %{100*D.azar.mean():>7.1f} %"
              f"{100*m:>+11.1f} %   [{100*(m-ic):+5.1f}, {100*(m+ic):+5.1f}]"
              f"{D.velasM.median():>11.0f}")

print("\n\n¿IMPORTA QUE EL RANGO SEA ESTRECHO?  (M15, n=12)")
D = todo[("M15", 12)].copy()
D["dec"] = pd.qcut(D.ratio.rank(method="first"), 10, labels=False) + 1
print(f"{'decil':>6}{'estrechez':>11}{'n':>8}{'completa':>10}{'azar':>8}{'diferencia':>12}")
for d, S in D.groupby("dec"):
    print(f"{d:>6}{S.ratio.median():>11.2f}{len(S):>8,}{100*S.D.mean():>9.1f} %"
          f"{100*S.azar.mean():>7.1f} %{100*(S.D - S.azar).mean():>+11.1f} %")

print("\n\nMISMO ANALISIS EN H1, n=12")
D = todo[("H1", 12)].copy()
D["dec"] = pd.qcut(D.ratio.rank(method="first"), 10, labels=False) + 1
for d, S in D.groupby("dec"):
    print(f"{d:>6}{S.ratio.median():>11.2f}{len(S):>8,}{100*S.D.mean():>9.1f} %"
          f"{100*S.azar.mean():>7.1f} %{100*(S.D - S.azar).mean():>+11.1f} %")

# ── ¿y en dinero? entrada al cierre de la M, stop en el extremo barrido,
#    objetivo el extremo contrario del rango ──────────────────────────────
print("\n\n" + "=" * 104)
print("EN DINERO · entras al cierre de la M, stop en el extremo del barrido,")
print("objetivo el extremo contrario. Coste 1,43 pips.")
print("=" * 104)

U, COSTE = 1e-4, 1.43

def dinero(V, n, nom):
    h = V.h.to_numpy(); l = V.l.to_numpy(); c = V.c.to_numpy(); N = len(V)
    a14 = atr(h, l, c, 14)
    hi = pd.Series(h).rolling(n).max().to_numpy()
    lo = pd.Series(l).rolling(n).min().to_numpy()
    normal = a14 * sqrt(n)
    ratio = np.where(normal > 0, (hi - lo) / normal, np.nan)
    filas = []; i = n
    while i < N - 1:
        if not np.isfinite(ratio[i]): i += 1; continue
        rHi, rLo, r0 = hi[i], lo[i], ratio[i]
        if not (rHi > rLo): i += 1; continue
        manip = -1; lado = 0; ext = np.nan
        j = i + 1
        while j < min(i + 1 + ESPM, N):
            if h[j] > rHi or l[j] < rLo:
                arriba = h[j] > rHi and rLo < c[j] < rHi
                abajo  = l[j] < rLo and rLo < c[j] < rHi
                if arriba or abajo:
                    manip = j; lado = -1 if arriba else 1
                    ext = h[j] if arriba else l[j]
                break
            j += 1
        if manip < 0: i = max(j, i + 1); continue
        P = c[manip]
        stop = ext
        obj = rLo if lado < 0 else rHi
        rgo = abs(stop - P); rec = abs(obj - P)
        if rgo <= 0 or rec <= 0: i = manip + 1; continue
        rr = rec / rgo
        gana = 0; k = manip + 1
        while k < min(manip + 1 + ESPD, N):
            if lado < 0:
                if h[k] >= stop: break
                if c[k] < obj: gana = 1; break
            else:
                if l[k] <= stop: break
                if c[k] > obj: gana = 1; break
            k += 1
        filas.append((r0, rgo / U, rr, gana))
        i = manip + 1
    D = pd.DataFrame(filas, columns=["ratio","rgoP","rr","gana"])
    D["Rb"] = np.where(D.gana == 1, D.rr, -1.0)
    D["Rn"] = D.Rb - COSTE / D.rgoP
    D["dec"] = pd.qcut(D.ratio.rank(method="first"), 5, labels=False) + 1
    print(f"\n{nom}   n {len(D):,}")
    print(f"{'quintil':>8}{'estrechez':>11}{'n':>8}{'acierto':>9}{'R:R':>7}"
          f"{'riesgo':>9}{'coste':>8}{'BRUTA':>10}{'NETA':>10}{'IC95':>20}")
    for d, S in D.groupby("dec"):
        m, s = S.Rn.mean(), S.Rn.std(ddof=1); ic = 1.96 * s / sqrt(len(S))
        print(f"{d:>8}{S.ratio.median():>11.2f}{len(S):>8,}{100*S.gana.mean():>8.1f} %"
              f"{S.rr.median():>7.1f}{S.rgoP.median():>8.1f} p"
              f"{100*COSTE/S.rgoP.median():>7.0f} %{S.Rb.mean():>+10.4f}{m:>+10.4f}"
              f"   [{m-ic:+.3f}, {m+ic:+.3f}]")
    return D

for tf, mins, n in (("M15", 15, 12), ("H1", 60, 12), ("H4", 240, 8)):
    dinero(velas(mins), n, f"{tf}  n={n}")
