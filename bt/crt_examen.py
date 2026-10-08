"""El examen: todas las senales CRT del periodo fuera de muestra, sin filtrar.

Las mismas reglas del indicador pine/CRT_operativo.pine. Se generan DOS
ficheros: las preguntas (sin resultado) y las respuestas. La idea es que el
usuario mire cada fecha en su propio grafico y decida por si mismo.

No hay seleccion posible: salen TODAS las senales del periodo.

  python3 bt/crt_examen.py
"""
import numpy as np, pandas as pd

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50)}
MINS, VELAS, DESDE = 720, 3, "2026-01-01"


def señales(par):
    ruta, U, COSTE = INSTR[par]
    M = pd.read_parquet(ruta)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    B = M.set_index("ts").resample(f"{MINS}min", label="left", closed="left").agg(
        o=("open", "first"), h=("high", "max"), l=("low", "min"),
        c=("close", "last"), n=("close", "size")).dropna()
    B = B[B.n >= MINS * 0.3]
    h, l, c = B.h.to_numpy(), B.l.to_numpy(), B.c.to_numpy()
    ti = B.index.to_numpy()
    mh, ml, mc, mt = (M.high.to_numpy(), M.low.to_numpy(),
                      M.close.to_numpy(), M.ts.to_numpy())
    dec = 3 if U == 1e-2 else 5
    out = []
    for i in range(1, len(B) - 1):
        if ti[i] < np.datetime64(DESDE):
            continue
        rng = h[i - 1] - l[i - 1]
        if rng <= 0:
            continue
        if h[i] > h[i - 1] and c[i] < h[i - 1]:
            lado, stop = -1, h[i]
        elif l[i] < l[i - 1] and c[i] > l[i - 1]:
            lado, stop = 1, l[i]
        else:
            continue
        ent = c[i]
        rgo = abs(ent - stop)
        obj = ent + 1.5 * rng * lado
        if rgo < 2 * U or (obj - ent) * lado <= 0:
            continue
        j0 = int(np.searchsorted(mt, ti[i] + np.timedelta64(MINS, "m")))
        j1 = min(j0 + MINS * VELAS, len(mt))
        if j1 <= j0 + 5:
            continue
        hh, ll = mh[j0:j1], ml[j0:j1]
        a = np.flatnonzero(hh >= obj) if lado > 0 else np.flatnonzero(ll <= obj)
        b = np.flatnonzero(ll <= stop) if lado > 0 else np.flatnonzero(hh >= stop)
        ia = int(a[0]) if len(a) else 10 ** 9
        ib = int(b[0]) if len(b) else 10 ** 9
        rr = abs(obj - ent) / rgo
        if ia == ib == 10 ** 9:
            R, res = (float(mc[j1 - 1]) - ent) * lado / rgo, "vencida a mercado"
        elif ia < ib:
            R, res = rr, "OBJETIVO"
        else:
            R, res = -1.0, "stop"
        out.append(dict(par=par, senal=pd.Timestamp(ti[i] + np.timedelta64(MINS, "m")),
                        orden="COMPRA" if lado > 0 else "VENTA",
                        entrada=round(ent, dec), stop=round(stop, dec),
                        objetivo=round(obj, dec), riesgo_pips=round(rgo / U, 1),
                        rr=round(rr, 2), coste_pct=round(COSTE * U / rgo * 100, 1),
                        resultado=res, R=round(R, 3),
                        R_neta=round(R - COSTE * U / rgo, 3)))
    return pd.DataFrame(out)


if __name__ == "__main__":
    D = pd.concat([señales(p) for p in INSTR], ignore_index=True).sort_values("senal")
    D.to_csv("data/examen_crt_respuestas.csv", index=False)
    D.drop(columns=["resultado", "R", "R_neta"]).to_csv(
        "data/examen_crt_preguntas.csv", index=False)
    print(f"=== EXAMEN CRT · {len(D)} senales · H12 · desde {DESDE} · SIN FILTRAR ===\n")
    print(f"  {'instr':>7} {'n':>4} {'R:R':>5} {'objetivo':>9} {'stop':>6} {'vencida':>8} "
          f"{'acierto':>8} {'azar':>6} {'R BRUTA':>9} {'R NETA':>9}")
    for k, g in list(D.groupby("par")) + [("TODOS", D)]:
        ac = (g.resultado == "OBJETIVO").mean()
        print(f"  {k:>7} {len(g):>4} {g.rr.mean():>5.2f} "
              f"{(g.resultado=='OBJETIVO').sum():>9} {(g.resultado=='stop').sum():>6} "
              f"{(g.resultado=='vencida a mercado').sum():>8} {ac:>7.1%} "
              f"{(1/(1+g.rr)).mean():>5.1%} {g.R.mean():>+9.4f} {g.R_neta.mean():>+9.4f}")
    print(f"\n  suma total en R neta: {D.R_neta.sum():+.2f} R")
    print(f"  con riesgo del 1 % en una cuenta de 10.000 €: "
          f"{D.R_neta.sum()*100:+,.0f} € en {len(D)} operaciones")
