"""H4 marca la direccion, el CRT se busca en M15, M5 confirma, M1 ejecuta.

Preregistrado en docs/PREREGISTRO_cascada_h4_m1.md. Un solo pase.

  python3 bt/cascada_h4_m1.py
"""
import numpy as np, pandas as pd
from math import sqrt, erf

U_DEF, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"
BUF, VIDA = 1.0, 8*60
CONFLU  = 3.0                      # pips al nivel de Asia
VENTANA = (800, 1700)              # hora de Madrid
LONDRES = (800, 1130)
GEO = 100/3

INS = [("EURUSD", "data/eurusd_m1.parquet", 0.0001),
       ("GBPUSD", "data/gbpusd_m1.parquet", 0.0001),
       ("USDJPY", "data/usdjpy_m1.parquet", 0.01)]


def rejilla(m1, minutos, col="loc"):
    b = m1[col].dt.floor(f"{minutos}min")
    g = (m1.groupby(b).agg(o=("open","first"), h=("high","max"), l=("low","min"),
                           c=("close","last"), n=("open","size")).reset_index())
    g.columns = ["t", "o", "h", "l", "c", "n"]
    return g[g.n >= minutos/2].reset_index(drop=True)


def direccion(g, ts, atras, minutos):
    """Signo de las ultimas `atras` velas REALMENTE CERRADAS antes de `ts`.

    El indice de `g` son horas de APERTURA, asi que una vela solo esta cerrada
    si su apertura mas su duracion es menor o igual que ts. Buscar con
    searchsorted(ts)-1 devolveria una vela AUN EN FORMACION: es el fallo de
    docs/CORRECCION_mirada_al_futuro.md.
    """
    lim = ts - np.timedelta64(minutos, "m")
    idx = np.searchsorted(g.t.to_numpy(), lim, side="right") - 1
    out = np.zeros(len(ts), dtype=int)
    ok = idx >= atras
    c = g.c.to_numpy()
    out[ok] = np.sign(c[idx[ok]] - c[idx[ok] - atras])
    return out


def niveles_asia(m15):
    """Por dia: alto y bajo de la sesion 00:00-08:00, mas los fractales de M15
    de dentro de esa ventana. Todos disponibles a partir de las 08:00."""
    a = m15[m15.hm < 800]
    por_dia = {}
    for dia, g in a.groupby("dia"):
        if len(g) < 16: continue
        h, l = g.h.to_numpy(), g.l.to_numpy()
        niv = [float(h.max()), float(l.min())]
        for k in range(2, len(g)-2):                    # fractales, 2 a cada lado
            if h[k] == h[k-2:k+3].max(): niv.append(float(h[k]))
            if l[k] == l[k-2:k+3].min(): niv.append(float(l[k]))
        por_dia[dia] = np.array(sorted(set(niv)))
    return por_dia


def senales(m15, asia, unit):
    """Vela 1 rango, Vela 2 barre un lado y cierra dentro, Vela 3 la ventana."""
    h, l, c, t = (m15[x].to_numpy() for x in ("h","l","c","t"))
    dia, hm = m15.dia.to_numpy(), m15.hm.to_numpy()
    i = np.arange(1, len(m15)-1)
    seguida = (t[i+1] - t[i]) == np.timedelta64(15, "m")
    r_hi, r_lo = h[i-1], l[i-1]
    b_lo, b_hi = l[i] < r_lo, h[i] > r_hi
    ok = (b_lo ^ b_hi) & (c[i] >= r_lo) & (c[i] <= r_hi) & (r_hi > r_lo) & seguida
    ok &= (hm[i+1] >= VENTANA[0]) & (hm[i+1] < VENTANA[1])
    i = i[ok]
    largo = b_lo[ok]
    sweep = np.where(largo, l[i], h[i])
    # confluencia: el extremo barrido, a CONFLU pips o menos de un nivel de Asia
    cerca = np.zeros(len(i), bool)
    for j, (d, s) in enumerate(zip(dia[i], sweep)):
        n = asia.get(d)
        if n is None or not len(n): continue
        cerca[j] = np.abs(n - s).min() / unit <= CONFLU
    return pd.DataFrame(dict(largo=largo, r_hi=r_hi[ok], r_lo=r_lo[ok],
                             v2_hi=h[i], v2_lo=l[i], sweep=sweep,
                             t3=t[i+1], hm3=hm[i+1], asia=cerca))


def ejecuta(sig, m1, m5, unit, stop_m1=True, obj_fijo=True):
    T1 = m1.ts.to_numpy(); H1 = m1.high.to_numpy(); L1 = m1.low.to_numpy()
    T5 = m5.t.to_numpy(); C5 = m5.c.to_numpy()
    buf = BUF*unit
    t3 = sig.t3.to_numpy()
    A5 = np.searchsorted(T5, t3)                       # M5 dentro de la Vela 3
    B5 = np.searchsorted(T5, t3 + np.timedelta64(15, "m"))
    col = {k: sig[k].to_numpy() for k in
           ("largo","r_hi","r_lo","v2_hi","v2_lo","sweep")}
    out = []
    for k in range(len(sig)):
        a, b = int(A5[k]), int(B5[k])
        if b <= a: continue
        largo = bool(col["largo"][k])
        niv = col["v2_hi"][k] if largo else col["v2_lo"][k]
        g = (C5[a:b] > niv) if largo else (C5[a:b] < niv)   # M5 CIERRA mas alla
        if not g.any(): continue
        i5 = a + int(np.argmax(g))
        # el M5 se cierra 5 minutos despues de su apertura: se entra despues
        cierre = T5[i5] + np.timedelta64(5, "m")
        j = int(np.searchsorted(T1, cierre))
        if j >= len(T1): continue
        e = m1.open.to_numpy()[j]
        if stop_m1:
            j0 = max(0, j-3)
            base = L1[j0:j].min() if largo else H1[j0:j].max()
        else:
            base = col["sweep"][k]
        sl = base - buf if largo else base + buf
        rgo = (e - sl) if largo else (sl - e)
        if rgo < buf: continue
        tp = (e + 2*rgo if largo else e - 2*rgo) if obj_fijo else \
             (col["r_hi"][k] if largo else col["r_lo"][k])
        if ((tp - e) if largo else (e - tp)) <= 0: continue
        fin = min(j + VIDA, len(T1))
        hh, ll = H1[j:fin], L1[j:fin]
        gs, gt = ((ll <= sl, hh >= tp) if largo else (hh >= sl, ll <= tp))
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        itp = int(np.argmax(gt)) if gt.any() else 10**9
        if isl == 10**9 and itp == 10**9: R, mot = 0.0, "abierta"
        elif isl <= itp: R, mot = -1.0, "SL"
        else: R, mot = ((tp-e) if largo else (e-tp))/rgo, "TP"
        out.append((T1[j], largo, mot, R, rgo/unit, R - COSTE/(rgo/unit)))
    return pd.DataFrame(out, columns=["ts","largo","motivo","R","riesgo","neta"])


def linea(nom, d):
    if len(d) < 5:
        print(f"  {nom:34s} {len(d):5d}  muestra insuficiente"); return
    res = d[d.motivo != "abierta"]
    ac = 100*(res.motivo == "TP").mean() if len(res) else float("nan")
    ee = 100*sqrt((GEO/100)*(1-GEO/100)/max(len(res),1))
    x = d.neta.to_numpy(); z = x.mean()/(x.std(ddof=1)/sqrt(len(x)))
    print(f"  {nom:34s} {len(d):5d} {d.riesgo.median():5.1f}p "
          f"{100*(COSTE/d.riesgo).median():4.0f}% {ac:6.1f}% {ac-GEO:+6.1f}pp "
          f"{(ac-GEO)/ee:+6.2f} {d.R.mean():+7.3f} {d.neta.mean():+7.3f} "
          f"{z:+7.2f} {d.neta.sum():+8.1f}")


CAB = (f"  {'':34s} {'n':>5s} {'stop':>6s} {'cost':>5s} {'acierto':>7s} "
       f"{'vs geo':>8s} {'z ac':>6s} {'R brut':>7s} {'R neta':>7s} {'z neta':>7s} {'suma':>8s}")

print("="*118)
print("H4 MARCA · CRT EN M15 · CONFIRMA M5 · EJECUTA M1 · CONFLUENCIA CON ASIA")
print(f"  coste {COSTE} p · confluencia {CONFLU} p · ventana 08:00-17:00 Madrid · "
      f"principal |z| > 1,96")
print("="*118)

for nom_ins, ruta, unit in INS:
    m1 = pd.read_parquet(ruta)
    m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
    m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    m5  = rejilla(m1, 5)
    m15 = rejilla(m1, 15)
    h4  = rejilla(m1, 240)
    m15["dia"] = m15.t.dt.date; m15["hm"] = m15.t.dt.hour*100 + m15.t.dt.minute
    m5["dia"]  = m5.t.dt.date
    sig = senales(m15, niveles_asia(m15), unit)
    sig["h4"] = direccion(h4, sig.t3.to_numpy(), 4, 240)
    sig["favor"] = np.where(sig.largo, sig.h4 > 0, sig.h4 < 0)
    print(f"\n{'='*118}\n{nom_ins} · {len(sig):,} señales de CRT en M15 · "
          f"{sig.asia.sum():,} sobre un nivel de Asia\n{'='*118}")
    print(CAB); print("  " + "-"*114)

    base = ejecuta(sig[sig.favor & sig.asia], m1, m5, unit)
    linea("PRINCIPAL  H4 + Asia + stop M1 + 1:2", base)
    linea("sin filtro de Asia", ejecuta(sig[sig.favor], m1, m5, unit))
    linea("sin filtro de H4", ejecuta(sig[sig.asia], m1, m5, unit))
    linea("sin ninguno de los dos", ejecuta(sig, m1, m5, unit))
    linea("stop en el barrido, no en M1",
          ejecuta(sig[sig.favor & sig.asia], m1, m5, unit, stop_m1=False))
    linea("objetivo al extremo del rango",
          ejecuta(sig[sig.favor & sig.asia], m1, m5, unit, obj_fijo=False))
    lon = sig[sig.favor & sig.asia & (sig.hm3 >= LONDRES[0]) & (sig.hm3 < LONDRES[1])]
    linea("solo Londres 08:00-11:30", ejecuta(lon, m1, m5, unit))

# ---------------------------------------------------------------------------
# POST HOC. Esto NO estaba preregistrado. Sale de mirar el resultado y juntar
# las dos piezas que salieron mejor: el filtro de Asia, que sube el acierto, y
# el stop ancho, que baja el coste. Se reporta marcado, y no cuenta como
# hallazgo: escoger la mejor combinacion DESPUES de ver los numeros es
# exactamente el sesgo contra el que sirve un preregistro.
# ---------------------------------------------------------------------------
print("\n" + "="*118)
print("POST HOC · Asia + stop ancho, sin H4   (elegido tras ver los números, no cuenta)")
print("="*118)
print(CAB); print("  " + "-"*114)
for nom_ins, ruta, unit in INS:
    m1 = pd.read_parquet(ruta)
    m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
    m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    m5, m15 = rejilla(m1, 5), rejilla(m1, 15)
    m15["dia"] = m15.t.dt.date; m15["hm"] = m15.t.dt.hour*100 + m15.t.dt.minute
    sig = senales(m15, niveles_asia(m15), unit)
    linea(nom_ins, ejecuta(sig[sig.asia], m1, m5, unit, stop_m1=False))
