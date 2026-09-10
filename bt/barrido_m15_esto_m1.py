"""Barrido de liquidez en M15 + estocastico de M1: la idea del usuario.

    "estocastico en M1 y buscar reversiones de M15. Si hay sobrecompra por
     encima del 80 y en M15 hay un liquidity sweep, subirse al movimiento"

  barrido    el precio se lleva el maximo (o minimo) de las ultimas N velas M15
  filtro     estocastico de M1 en sobrecompra (>=80) al barrer el maximo
  entrada    al cierre de esa vela de M1
  stop       la propia vela del barrido, o el extremo de las ultimas 5 de M1
  objetivo   multiplo del riesgo

Se miden DOS direcciones sobre exactamente las mismas senales:

  REVERSION     lo que propone: barrido de maximos -> venta
  CONTINUACION  el control: barrido de maximos -> compra

Y se informa SIEMPRE bruto y neto por separado, porque son dos preguntas
distintas: si el patron predice algo, y si sobrevive al coste. Con stops de
M1 el coste es enorme en proporcion, y conviene ver donde muere exactamente.

  python3 bt/barrido_m15_esto_m1.py
"""
import numpy as np, pandas as pd

INSTR = {"EURUSD": (["data/eurusd_m1.parquet"], 1e-4, 1.43),
         "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
         "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
         "NAS100": (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
         "SPX500": (["data/spxusd_m1.parquet"], 1e-0, 0.60),
         "XAUUSD": (["data/xauusd_m1_2020_2022.parquet", "data/xauusd_m1.parquet",
                     "data/xauusd_m1_2026.parquet"], 1e-0, 0.30)}
VENTANAS, STOPS, RRS_ = (6, 12, 24), ("barrido", "5velas"), (1.0, 2.0, 3.0)
HOR = 60          # minutos de vida de la operacion


def corre(par):
    rutas, U, C = INSTR[par]
    M = pd.concat([pd.read_parquet(f) for f in rutas], ignore_index=True)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    o, h, l, c = (M[x].to_numpy(np.float64) for x in ("open","high","low","close"))
    ts = M.ts.to_numpy(); n = len(c)

    # estocastico de M1 (14,3)
    hh14 = pd.Series(h).rolling(14).max().to_numpy()
    ll14 = pd.Series(l).rolling(14).min().to_numpy()
    r14 = hh14 - ll14
    K = pd.Series(100.0*(c-ll14)/np.where(r14 == 0, np.nan, r14)).rolling(3).mean().to_numpy()

    # velas M15 y, por minuto, el extremo de las N velas M15 YA CERRADAS
    k15 = M.ts.dt.floor("15min")
    B = M.groupby(k15).agg(h=("high","max"), l=("low","min"))
    idx = B.index
    filas = []
    for V in VENTANAS:
        ph = B.h.rolling(V).max().shift(1)      # cerradas, sin la actual
        pl = B.l.rolling(V).min().shift(1)
        nh = k15.map(ph).to_numpy(); nl = k15.map(pl).to_numpy()
        # primer minuto de cada vela M15 que se lleva el nivel
        gh = (h >= nh) & np.isfinite(nh)
        gl = (l <= nl) & np.isfinite(nl)
        blq = k15.to_numpy()
        primero_h = gh & (blq != np.roll(np.where(gh, blq, np.datetime64("NaT")), 1))
        primero_l = gl & (blq != np.roll(np.where(gl, blq, np.datetime64("NaT")), 1))
        for lado_barr, marca in ((-1, primero_h), (+1, primero_l)):
            ii = np.flatnonzero(marca)
            ii = ii[(ii > 20) & (ii < n-HOR-1)]
            for i in ii:
                if not np.isfinite(K[i]): continue
                # el filtro: sobrecompra al barrer maximos, sobreventa al barrer minimos
                if lado_barr < 0 and K[i] < 80: continue
                if lado_barr > 0 and K[i] > 20: continue
                ent = c[i]
                for snom in STOPS:
                    if snom == "barrido":
                        ext_alto, ext_bajo = h[i], l[i]
                    else:
                        ext_alto, ext_bajo = h[i-4:i+1].max(), l[i-4:i+1].min()
                    for dire, dnom in ((lado_barr, "reversion"), (-lado_barr, "continuacion")):
                        stop = ext_alto if dire < 0 else ext_bajo
                        rgo = (ent-stop)*dire
                        if rgo < 1.5*U: continue
                        hh_, ll_ = h[i+1:i+1+HOR], l[i+1:i+1+HOR]
                        b = (np.flatnonzero(ll_ <= stop) if dire > 0
                             else np.flatnonzero(hh_ >= stop))
                        ib = b[0] if len(b) else 10**9
                        for rr in RRS_:
                            tp = ent + dire*rgo*rr
                            a = (np.flatnonzero(hh_ >= tp) if dire > 0
                                 else np.flatnonzero(ll_ <= tp))
                            ia = a[0] if len(a) else 10**9
                            R = ((c[i+HOR]-ent)*dire/rgo if ia == ib == 10**9
                                 else (rr if ia < ib else -1.0))
                            filas.append((par, V, snom, rr, dnom, ts[i], R,
                                          C*U/rgo, rgo/U))
    return pd.DataFrame(filas, columns=["par","vent","stop","rr","dir","ts",
                                        "R","cos","rgo_p"])


def zano(g, col="R"):
    if len(g) < 30: return np.nan
    m = g[col].mean(); r = (g[col]-m).groupby(pd.to_datetime(g.ts).dt.year).sum()
    se = np.sqrt((r**2).sum())/len(g)
    return float(m/se) if se > 0 else np.nan


if __name__ == "__main__":
    T = pd.concat([corre(p) for p in INSTR], ignore_index=True)
    T["N"] = T.R - T.cos
    T.to_csv("data/barrido_m15_esto_m1.csv", index=False)
    print(f"\n=== BARRIDO M15 + ESTOCASTICO M1 · {len(T)} operaciones · 6 instrumentos ===")
    print("    z agrupado por ano. BRUTO = ¿predice? · NETO = ¿sobrevive al coste?\n")
    print(f"  {'direccion':>14} | {'n':>7} {'riesgo':>8} {'coste':>7} | "
          f"{'R BRUTA':>9} {'z':>7} | {'R NETA':>9} {'z':>7} | {'inst +':>7}")
    for dnom, g in T.groupby("dir"):
        pos = sum(1 for p, x in g.groupby("par") if x.N.mean() > 0)
        print(f"  {dnom:>14} | {len(g):>7} {g.rgo_p.mean():>7.1f}p {g.cos.mean():>6.1%} | "
              f"{g.R.mean():>+9.4f} {zano(g):>+7.2f} | {g.N.mean():>+9.4f} "
              f"{zano(g,'N'):>+7.2f} | {pos:>4}/6")

    print(f"\n  la REVERSION -lo que propone- por instrumento\n")
    print(f"  {'':>8} {'n':>7} {'riesgo':>8} {'coste':>7} {'BRUTA':>9} {'z':>7} "
          f"{'NETA':>9} {'z':>7}")
    for p, g in T[T.dir == "reversion"].groupby("par"):
        print(f"  {p:>8} {len(g):>7} {g.rgo_p.mean():>7.1f}p {g.cos.mean():>6.1%} "
              f"{g.R.mean():>+9.4f} {zano(g):>+7.2f} {g.N.mean():>+9.4f} {zano(g,'N'):>+7.2f}")

    print(f"\n  ¿y si el stop fuera mas ancho? por tipo de stop y ventana\n")
    print(f"  {'direccion':>14} {'stop':>8} {'vent':>5} | {'riesgo':>8} {'coste':>7} "
          f"{'BRUTA':>9} {'NETA':>9} {'z neta':>8}")
    for k, g in T.groupby(["dir","stop","vent"]):
        print(f"  {k[0]:>14} {k[1]:>8} {k[2]:>5} | {g.rgo_p.mean():>7.1f}p "
              f"{g.cos.mean():>6.1%} {g.R.mean():>+9.4f} {g.N.mean():>+9.4f} "
              f"{zano(g,'N'):>+8.2f}")
