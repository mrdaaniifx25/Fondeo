"""CRT detectado en M15, con la entrada afinada en M1.

Preregistrado en docs/PREREGISTRO_crt_m15_m1.md. Un solo pase.

Cuatro formas de ejecutar LA MISMA senal, para aislar que aporta bajar a M1:
  A  M15 a mercado          entrada en la apertura de la Vela 3
  B  M15 orden stop         disparo en el extremo de la Vela 2
  C  M1 confirmacion        primer M1 que CIERRA mas alla del extremo de la V2
  D  C, pero con el stop pegado a las 3 velas M1 cerradas  <- su metodo
  D2 D con objetivo fijo 1:2 en vez del extremo del rango

  python3 bt/crt_m15_m1.py [minutos de la rejilla, 15 por defecto]
"""
import sys; sys.path.insert(0, "bt")
import types
import numpy as np, pandas as pd
from math import sqrt, erf

KZ_FX    = [(8.0, 11.0), (13.0, 16.0), (16.0, 18.0)]   # CET, de la guia
KZ_LON   = [(8.0, 11.0)]
BUFFER   = 1.0        # pips detras del extremo
COSTE    = 1.43       # pips, redondo (docs/COSTE_real.md)
MAX_MIN  = 8 * 60     # tope de vida de la operacion

INS = [("EURUSD", "data/eurusd_m1.parquet", 0.0001),
       ("GBPUSD", "data/gbpusd_m1.parquet", 0.0001),
       ("USDJPY", "data/usdjpy_m1.parquet", 0.01)]


def rejilla(m1, tf):
    """Rejilla de `tf` minutos alineada a la hora. El indice es la APERTURA."""
    g = (m1.set_index("ts").resample(f"{tf}min", label="left", closed="left")
           .agg(open=("open", "first"), high=("high", "max"),
                low=("low", "min"), close=("close", "last"), n=("close", "size")))
    return g[g.n >= tf/2].reset_index()       # media vela como minimo


def senales(m15, tf):
    """Vela 1 rango, Vela 2 barre un lado y cierra dentro, Vela 3 la ventana."""
    hi, lo, cl = (m15[c].to_numpy() for c in ("high", "low", "close"))
    ts = m15["ts"].to_numpy()
    i = np.arange(1, len(m15) - 1)
    r_hi, r_lo = hi[i-1], lo[i-1]
    # la Vela 3 tiene que ser la barra siguiente de verdad, sin hueco de sesion
    seguida = (ts[i+1] - ts[i]) == np.timedelta64(tf, "m")
    barre_lo = lo[i] < r_lo
    barre_hi = hi[i] > r_hi
    uno = barre_lo ^ barre_hi                              # uno de los dos, no ambos
    dentro = (cl[i] >= r_lo) & (cl[i] <= r_hi)             # cierra dentro del rango
    ok = uno & dentro & (r_hi > r_lo) & seguida
    i = i[ok]
    return pd.DataFrame(dict(
        largo=barre_lo[ok], r_hi=r_hi[ok], r_lo=r_lo[ok],
        v2_hi=hi[i], v2_lo=lo[i],
        sweep=np.where(barre_lo[ok], lo[i], hi[i]),
        t3=ts[i+1]))


def en_kz(ts, zonas):
    """Vectorizado: hora CET de cada sello contra las killzones."""
    ce = pd.DatetimeIndex(ts).tz_localize("UTC").tz_convert("Europe/Madrid")
    h = ce.hour + ce.minute / 60
    m = np.zeros(len(h), bool)
    for a, b in zonas:
        m |= (h >= a) & (h < b)
    return m


def resuelve(T, H, L, C, O, it, e, sl, tp, largo):
    """Camina M1 desde `it` buscando stop u objetivo. Empate en el minuto -> SL."""
    i2 = min(it + MAX_MIN, len(T))
    a, b = H[it:i2], L[it:i2]
    gsl, gtp = ((b <= sl, a >= tp) if largo else (a >= sl, b <= tp))
    isl = int(np.argmax(gsl)) if gsl.any() else 10**9
    itp = int(np.argmax(gtp)) if gtp.any() else 10**9
    if isl == 10**9 and itp == 10**9: return C[i2-1], "tiempo"
    if isl <= itp: return sl, "SL"
    return tp, "TP"


def corre(sig, m1, unit, modo, zonas, tf):
    T = m1["ts"].to_numpy(); H = m1["high"].to_numpy()
    L = m1["low"].to_numpy(); C = m1["close"].to_numpy(); O = m1["open"].to_numpy()
    buf = BUFFER * unit
    if sig.empty:
        return pd.DataFrame(columns=["ts", "largo", "motivo", "rr", "riesgo_p",
                                     "bruto_p", "R", "R_neto"])
    # Los indices se calculan de una vez y vectorizados. Llamar a searchsorted
    # dentro del bucle con un Timestamp de pandas contra un array datetime64
    # obliga a numpy a recorrer los 2,4 M de elementos uno a uno: 170 ms por
    # llamada. Asi son dos llamadas en total.
    t3 = sig["t3"].to_numpy()
    I0 = np.searchsorted(T, t3)
    I1 = np.searchsorted(T, t3 + np.timedelta64(tf, "m"))
    cols = {c: sig[c].to_numpy() for c in
            ("largo", "r_hi", "r_lo", "v2_hi", "v2_lo", "sweep")}
    out, descartadas = [], [0]
    for k in range(len(sig)):
        i0, i1 = int(I0[k]), int(I1[k])
        if i0 >= len(T) or i1 <= i0: continue
        r = types.SimpleNamespace(**{c: v[k] for c, v in cols.items()})
        niv = r.v2_hi if r.largo else r.v2_lo

        if modo == "A":
            it, e = i0, O[i0]
        elif modo == "B":
            g = (H[i0:i1] >= niv) if r.largo else (L[i0:i1] <= niv)
            if not g.any(): continue
            it = i0 + int(np.argmax(g))
            e = max(niv, O[it]) if r.largo else min(niv, O[it])   # hueco: peor precio
        else:                                    # C, D y D2: cierre de M1 mas alla
            g = (C[i0:i1] > niv) if r.largo else (C[i0:i1] < niv)
            if not g.any(): continue
            ic = i0 + int(np.argmax(g))          # la vela que confirma
            it = ic + 1                          # se entra en la SIGUIENTE
            if it >= len(T): continue
            e = O[it]

        if modo in ("D", "D2"):
            k0 = max(0, ic - 2)                  # 3 velas M1 ya cerradas
            base = L[k0:ic+1].min() if r.largo else H[k0:ic+1].max()
            sl = base - buf if r.largo else base + buf
        else:
            sl = r.sweep - buf if r.largo else r.sweep + buf

        riesgo = (e - sl) if r.largo else (sl - e)
        # Si el precio abre con hueco AL OTRO LADO del extremo que da el stop,
        # el riesgo puede salir de una milesima de pip y la R se dispara a
        # millones. Un stop mas estrecho que el propio buffer no es ejecutable
        # en ningun broker, asi que esas se descartan y se cuentan aparte.
        if riesgo < BUFFER * unit:
            descartadas[0] += 1
            continue
        tp = (e + 2*riesgo if r.largo else e - 2*riesgo) if modo == "D2" \
             else (r.r_hi if r.largo else r.r_lo)
        premio = (tp - e) if r.largo else (e - tp)
        if premio <= 0: continue

        sal, mot = resuelve(T, H, L, C, O, it, e, sl, tp, r.largo)
        br = ((sal - e) if r.largo else (e - sal)) / unit
        rg = riesgo / unit
        out.append((T[it], r.largo, mot, premio/riesgo, rg, br, br/rg,
                    (br - COSTE)/rg))
    d = pd.DataFrame(out, columns=["ts", "largo", "motivo", "rr", "riesgo_p",
                                   "bruto_p", "R", "R_neto"])
    if descartadas[0]:
        print(f"   {modo}: {descartadas[0]} señales descartadas por hueco "
              f"(stop mas estrecho que el buffer)")
    if not d.empty and zonas is not None:
        d = d[en_kz(d.ts, zonas)].reset_index(drop=True)
    return d


def z_de(x):
    n = len(x)
    if n < 3: return 0.0, 1.0
    se = x.std(ddof=1) / sqrt(n)
    z = x.mean() / se if se > 0 else 0.0
    return z, 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))


def bloque(titulo, res):
    print(f"\n{titulo}")
    print(f"  {'':3s} {'n':>6s} {'stop':>6s} {'RR':>5s} {'cost%':>6s} "
          f"{'acierto':>8s} {'geom':>6s} {'p pips':>7s} {'R bruta':>8s} "
          f"{'R neta':>8s} {'z neta':>7s} {'suma':>9s}")
    print("  " + "-" * 96)
    for nom, d in res:
        if d.empty or len(d) < 3:
            print(f"  {nom:3s} {'sin operaciones':>20s}"); continue
        k = d.rr.median()
        geom = 100 / (1 + k)
        ac = 100 * (d.motivo == "TP").mean()
        cost = 100 * (COSTE / d.riesgo_p).median()
        zb, _ = z_de(d.R_neto.to_numpy())
        print(f"  {nom:3s} {len(d):6d} {d.riesgo_p.median():6.1f} {k:5.2f} "
              f"{cost:5.0f}% {ac:7.1f}% {geom:5.1f}% {d.bruto_p.mean():+7.3f} "
              f"{d.R.mean():+8.3f} {d.R_neto.mean():+8.3f} {zb:+7.2f} "
              f"{d.R_neto.sum():+9.1f}")


def main():
    MODOS = [("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("D2", "D2")]

    TF = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    print("=" * 100)
    print(f"CRT EN M{TF} CON ENTRADA EN M1")
    print(f"  coste {COSTE} pips · buffer {BUFFER} p · tope {MAX_MIN//60} h · "
          f"umbral Bonferroni |z| > 2,50")
    print("=" * 100)

    for nom_ins, ruta, unit in INS:
        m1 = pd.read_parquet(ruta)
        m1["ts"] = pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").reset_index(drop=True)
        m15 = rejilla(m1, TF)
        sig = senales(m15, TF)
        print(f"\n{'='*100}\n{nom_ins}  ·  {len(m15):,} velas M{TF}  ·  "
              f"{len(sig):,} señales del patrón\n{'='*100}")
        guarda = {}
        for etq, modo in MODOS:
            guarda[etq] = corre(sig, m1, unit, modo, None, TF)  # sin filtro horario
        bloque("SIN FILTRO HORARIO", [(e, guarda[e]) for e, _ in MODOS])
        bloque("PRINCIPAL · las tres killzones de la guía",
               [(e, guarda[e][en_kz(guarda[e].ts, KZ_FX)].reset_index(drop=True))
                for e, _ in MODOS])
        bloque("SOLO LONDRES 08-11 CET",
               [(e, guarda[e][en_kz(guarda[e].ts, KZ_LON)].reset_index(drop=True))
                for e, _ in MODOS])
        if nom_ins == "EURUSD":
            guarda["D"].to_csv(f"data/crt_m{TF}_m1_D.csv", index=False)
            guarda["A"].to_csv(f"data/crt_m{TF}_m1_A.csv", index=False)


if __name__ == "__main__":
    main()
