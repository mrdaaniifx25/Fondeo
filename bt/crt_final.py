"""La estrategia CRT ensamblada: todo lo que ha sobrevivido, medido como UN objeto.

Lo que entra, y de donde sale cada pieza:

  rango        vela anterior cerrada                    CRT canonico
  manipulacion barre un extremo y CIERRA de vuelta      CRT canonico
  entrada      al cierre de la vela de manipulacion     agresiva gana 19/20 (crt_9am)
  stop         el extremo del barrido, no el del rango  liquidacion gana 19/20 (crt_9am)
  temporalidad H12 y D1                                 unico sitio donde coste/riesgo < 4 %

Las dos reglas de Brad Gould YA estaban dentro del +0,125 de H12. No anaden
nada nuevo: explican por que H12 era la mejor celda.

La UNICA palanca que la ecuacion del coste deja libre es el ancho del stop:

    neta = (p - p0)·(1 + R:R) - coste/riesgo

Ensanchar el stop baja el coste en R y baja el R:R a la vez. Cual gana es
empirico, y hay motivo para probarlo: el resultado de Brad dice que los stops
estrechos los saltan por encima de lo que su geometria compensa.

DISCIPLINA. 24 celdas (2 TF x 4 anchos x 3 objetivos). La celda se elige
MIRANDO SOLO 2020-2023 y se informa su resultado en 2024-2026. Un numero.

  python3 bt/crt_final.py
"""
import numpy as np, pandas as pd

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
         "NAS100": ("data/nsxusd_m1.parquet", 1e-0, 1.50),
         "SPX500": ("data/spxusd_m1.parquet", 1e-0, 0.60)}
TFS = {"H12": 720, "D1": 1440}
ANCHOS = (1.0, 1.25, 1.5, 2.0)          # multiplo del riesgo sobre el barrido
OBJS = ("opuesto", "medio", "ext150")
CORTE = np.datetime64("2024-01-01")


def corre(par, TF, mins):
    ruta, U, COSTE = INSTR[par]
    M = pd.read_parquet(ruta)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    B = M.set_index("ts").resample(f"{mins}min", label="left", closed="left").agg(
        o=("open", "first"), h=("high", "max"), l=("low", "min"),
        c=("close", "last"), n=("close", "size")).dropna()
    B = B[B.n >= mins * 0.3]
    h, l, c = B.h.to_numpy(), B.l.to_numpy(), B.c.to_numpy()
    ti = B.index.to_numpy()
    mh, ml, mc, mt = (M.high.to_numpy(), M.low.to_numpy(),
                      M.close.to_numpy(), M.ts.to_numpy())
    filas = []
    for i in range(1, len(B) - 1):
        rng = h[i - 1] - l[i - 1]
        if rng <= 0:
            continue
        if h[i] > h[i - 1] and c[i] < h[i - 1]:
            lado, ext = -1, h[i]
        elif l[i] < l[i - 1] and c[i] > l[i - 1]:
            lado, ext = 1, l[i]
        else:
            continue
        ent = c[i]
        base = (ent - ext) * lado                       # riesgo del barrido
        if base < 2 * U:
            continue
        j0 = int(np.searchsorted(mt, ti[i] + np.timedelta64(mins, "m")))
        j1 = min(j0 + mins * 3, len(mt))
        if j1 <= j0 + 5:
            continue
        hh, ll = mh[j0:j1], ml[j0:j1]
        objs = {"opuesto": (h[i - 1] if lado > 0 else l[i - 1]),
                "medio": (l[i - 1] + h[i - 1]) / 2,
                "ext150": ent + 1.5 * rng * lado}
        for a in ANCHOS:
            rgo = base * a
            stop = ent - rgo * lado
            b = np.flatnonzero(ll <= stop) if lado > 0 else np.flatnonzero(hh >= stop)
            ib = int(b[0]) if len(b) else 10 ** 9
            for nom in OBJS:
                tp = objs[nom]
                if (tp - ent) * lado <= 0:
                    continue
                aa = np.flatnonzero(hh >= tp) if lado > 0 else np.flatnonzero(ll <= tp)
                ia = int(aa[0]) if len(aa) else 10 ** 9
                rr = abs(tp - ent) / rgo
                R = ((float(mc[j1 - 1]) - ent) * lado / rgo if ia == ib == 10 ** 9
                     else (rr if ia < ib else -1.0))
                filas.append(dict(par=par, tf=TF, fecha=ti[i], lado=lado,
                                  ancho=a, obj=nom, R=R, rr=rr,
                                  coste=COSTE * U / rgo, tp=int(ia < ib)))
    return pd.DataFrame(filas)


def z(v):
    return float(v.mean() / (v.std(ddof=1) / np.sqrt(len(v)))) if len(v) > 5 else np.nan


if __name__ == "__main__":
    D = pd.concat([corre(p, k, m) for p in INSTR for k, m in TFS.items()],
                  ignore_index=True)
    D["N"] = D.R - D.coste
    D["fuera"] = D.fecha >= CORTE
    D.to_csv("data/crt_final.csv", index=False)
    A, F = D[~D.fuera], D[D.fuera]
    anios_a = (CORTE - D.fecha.min()) / np.timedelta64(365, "D")
    anios_f = (D.fecha.max() - CORTE) / np.timedelta64(365, "D")

    print(f"=== CRT ENSAMBLADO · {len(D)} filas · 5 instrumentos ===")
    print(f"    DENTRO 2020-2023 ({anios_a:.1f} anos)  ·  FUERA 2024-2026 ({anios_f:.1f} anos)\n")
    print("  A · LAS 24 CELDAS, ELEGIDAS MIRANDO SOLO 2020-2023\n")
    print(f"    {'tf':>4} {'ancho':>6} {'objetivo':>9} | {'n':>5} {'R:R':>5} {'cos%':>5} "
          f"{'NETA':>8} {'z':>6} | {'n':>5} {'NETA fuera':>11} {'z':>6}")
    res = []
    for (tf, an, ob), g in A.groupby(["tf", "ancho", "obj"]):
        gf = F[(F.tf == tf) & (F.ancho == an) & (F.obj == ob)]
        res.append((g.N.mean(), tf, an, ob, len(g), g.rr.mean(), g.coste.mean(),
                    z(g.N), len(gf), gf.N.mean(), z(gf.N)))
    for m, tf, an, ob, n, rr, co, za, nf, mf, zf in sorted(res, reverse=True):
        print(f"    {tf:>4} {an:>6.2f} {ob:>9} | {n:>5} {rr:>5.2f} {co:>5.1%} "
              f"{m:>+8.4f} {za:>+6.2f} | {nf:>5} {mf:>+11.4f} {zf:>+6.2f}")

    m, tf, an, ob = max(res)[:4]
    G = F[(F.tf == tf) & (F.ancho == an) & (F.obj == ob)]
    print(f"\n  B · LA CELDA ELEGIDA: {tf} · stop x{an:.2f} · objetivo {ob}")
    print(f"      dentro (2020-2023): neta {m:+.4f} sobre {len(A[(A.tf==tf)&(A.ancho==an)&(A.obj==ob)])} operaciones")
    print(f"      FUERA  (2024-2026): neta {G.N.mean():+.4f}  z {z(G.N):+.2f}  "
          f"sobre {len(G)} operaciones\n")
    print(f"    {'instr':>8} {'n':>5} {'R:R':>5} {'acierto':>8} {'geom':>6} "
          f"{'BRUTA':>8} {'NETA':>8} {'z':>6}")
    for k, g in G.groupby("par"):
        print(f"    {k:>8} {len(g):>5} {g.rr.mean():>5.2f} {g.tp.mean():>7.1%} "
              f"{(1/(1+g.rr)).mean():>5.1%} {g.R.mean():>+8.4f} {g.N.mean():>+8.4f} "
              f"{z(g.N):>+6.2f}")
    G = G.copy(); G["ano"] = pd.to_datetime(G.fecha).dt.year
    print()
    for k, g in G.groupby("ano"):
        print(f"    {k:>8} {len(g):>5} {g.rr.mean():>5.2f} {g.tp.mean():>7.1%} "
              f"{(1/(1+g.rr)).mean():>5.1%} {g.R.mean():>+8.4f} {g.N.mean():>+8.4f} "
              f"{z(g.N):>+6.2f}")

    print("\n  C · LO QUE ESO ES EN DINERO · cuenta 10.000 €, riesgo 1 % = 100 €/op\n")
    for et, X in (("2020-2023", A), ("2024-2026", F)):
        S = X[(X.tf == tf) & (X.ancho == an) & (X.obj == ob)]
        ops = len(S) / (anios_a if et.startswith("2020") else anios_f)
        eur = S.N.mean() * 100
        print(f"    {et}  ·  {ops:>5.0f} operaciones/ano  ·  {eur:>+7.2f} € por operacion  "
              f"·  {ops*eur:>+9.0f} €/ano")
    print(f"\n    (repartidas entre 5 instrumentos; en EURUSD solo, la quinta parte)")

    print("\n  D · ¿SIGUE VIVA LA VENTAJA BRUTA? diferencia fuera - dentro por celda\n")
    dif = []
    for (tf_, an_, ob_), g in A.groupby(["tf", "ancho", "obj"]):
        gf = F[(F.tf == tf_) & (F.ancho == an_) & (F.obj == ob_)]
        if len(gf) > 20:
            dif.append(gf.R.mean() - g.R.mean())
    dif = np.array(dif)
    print(f"    {len(dif)} celdas  ·  {(dif<0).sum()} bajan, {(dif>0).sum()} suben  "
          f"·  media {dif.mean():+.4f}")
