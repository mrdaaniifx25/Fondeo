"""Genera los datos del simulador CRT: velas H12, senales y CONTEXTO superior.

Cada senal lleva tres banderas de contexto, todas calculadas SOLO con lo que
se sabia en el instante de la entrada:

  bd  sesgo diario   signo del cierre de los dos ultimos dias YA CERRADOS
  bs  sesgo semanal  igual con semanas cerradas
  cd  rango diario   +1 si el dia en curso ya se llevo el minimo del dia
                     anterior (y no el maximo), -1 al reves, 0 si ambos o
                     ninguno. Es la cascada de la clase del NASDAQ, aplicada
                     al marco diario.
  po  objetivo diario PENDIENTE: hay un CRT diario ya formado cuyo objetivo
                     todavia NO se ha alcanzado, y en que direccion tira.
  pw  lo mismo en el marco semanal.

El objetivo pendiente es la idea de "hay otro rango pendiente de ocurrir":
si el precio tiene un objetivo superior sin cumplir, la senal que va en su
contra deberia fallar mas. Caduca a los 10 marcos para que un objetivo de
hace medio ano no cuente.

Precalcula el desenlace con los DOS objetivos para que el artefacto pueda
alternar sin recalcular, y guarda el riesgo en pips para que el coste sea un
parametro que el usuario mueva en vivo.

  python3 bt/crt_artefacto_datos.py
"""
import json, numpy as np, pandas as pd

INSTR = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43, 5),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60, 5),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50, 3)}
MINS, VELAS = 720, 3


def uno(par):
    ruta, U, COSTE, DEC = INSTR[par]
    M = pd.read_parquet(ruta)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    # marcos superiores, para el contexto
    Dd = M.set_index("ts").resample("1440min", label="left", closed="left").agg(
        h=("high","max"), l=("low","min"), c=("close","last"), n=("close","size")).dropna()
    Dd = Dd[Dd.n >= 300]
    Ws = M.set_index("ts").resample("W-MON", label="left", closed="left").agg(
        c=("close","last"), n=("close","size")).dropna()
    Ws = Ws[Ws.n >= 1500]
    d_ini = Dd.index.to_numpy()
    d_fin = d_ini + np.timedelta64(1440, "m")
    d_h, d_l, d_c = Dd.h.to_numpy(), Dd.l.to_numpy(), Dd.c.to_numpy()
    w_fin = Ws.index.to_numpy() + np.timedelta64(7, "D")
    w_c = Ws.c.to_numpy()

    def pendientes(idx, hh, ll, cc, fin, caduca):
        """CRT ya formados en ese marco cuyo objetivo sigue sin alcanzarse.

        Devuelve, para cada marco k, la direccion del objetivo pendiente mas
        reciente que siga vivo. Solo mira hacia atras.
        """
        reg = []                                    # (marco, objetivo, lado)
        for k in range(1, len(cc)):
            if hh[k] > hh[k-1] and cc[k] < hh[k-1]: reg.append((k, ll[k-1], -1))
            elif ll[k] < ll[k-1] and cc[k] > ll[k-1]: reg.append((k, hh[k-1], +1))
        # ¿cuando se cumple cada uno?
        cumple = []
        for k, obj, lado in reg:
            j = k + 1
            while j < len(cc) and j - k <= caduca:
                if (hh[j] >= obj) if lado > 0 else (ll[j] <= obj): break
                j += 1
            cumple.append(j)
        vivo = np.zeros(len(cc), dtype=np.int8)
        for (k, obj, lado), j in zip(reg, cumple):
            # pendiente desde el CIERRE del marco k hasta que se cumple o caduca
            vivo[k+1:min(j+1, k+1+caduca, len(cc))] = lado
        return vivo

    vivo_d = pendientes(d_ini, d_h, d_l, d_c, d_fin, 10)
    Wf = M.set_index("ts").resample("W-MON", label="left", closed="left").agg(
        h=("high","max"), l=("low","min"), c=("close","last"), n=("close","size")).dropna()
    Wf = Wf[Wf.n >= 1500]
    w_ini = Wf.index.to_numpy()
    vivo_w = pendientes(w_ini, Wf.h.to_numpy(), Wf.l.to_numpy(), Wf.c.to_numpy(),
                        w_ini + np.timedelta64(7,"D"), 6)

    def contexto(t, j0):
        """t = instante de la entrada; j0 = su indice en el M1."""
        # sesgo diario: los dos ultimos dias CERRADOS antes de t
        k = int(np.searchsorted(d_fin, t, "right"))
        bd = int(np.sign(d_c[k-1] - d_c[k-2])) if k >= 2 else 0
        # sesgo semanal
        kw = int(np.searchsorted(w_fin, t, "right"))
        bs = int(np.sign(w_c[kw-1] - w_c[kw-2])) if kw >= 2 else 0
        # rango diario en curso: que extremo del dia anterior se ha llevado ya
        cd = 0
        di = int(np.searchsorted(d_ini, t, "right")) - 1
        if di >= 1:
            a = int(np.searchsorted(mt_g, d_ini[di]))
            if j0 > a:
                bajo = float(ml_g[a:j0].min()) <= d_l[di-1]
                alto = float(mh_g[a:j0].max()) >= d_h[di-1]
                cd = 1 if (bajo and not alto) else (-1 if (alto and not bajo) else 0)
        # objetivo pendiente: el estado del marco en curso, fijado al cerrar el anterior
        po = int(vivo_d[di]) if 0 <= di < len(vivo_d) else 0
        wi = int(np.searchsorted(w_ini, t, "right")) - 1
        pw = int(vivo_w[wi]) if 0 <= wi < len(vivo_w) else 0
        return bd, bs, cd, po, pw
    B = M.set_index("ts").resample(f"{MINS}min", label="left", closed="left").agg(
        o=("open", "first"), h=("high", "max"), l=("low", "min"),
        c=("close", "last"), n=("close", "size")).dropna()
    B = B[B.n >= MINS * 0.3].reset_index()
    o, h, l, c = (B[x].to_numpy() for x in "ohlc")
    ti = B.ts.to_numpy()
    mh, ml, mc, mt = (M.high.to_numpy(), M.low.to_numpy(),
                      M.close.to_numpy(), M.ts.to_numpy())
    globals()["mh_g"], globals()["ml_g"], globals()["mt_g"] = mh, ml, mt
    velas = [[int(pd.Timestamp(ti[i]).timestamp()), round(float(o[i]), DEC),
              round(float(h[i]), DEC), round(float(l[i]), DEC),
              round(float(c[i]), DEC)] for i in range(len(B))]
    sen = []
    for i in range(1, len(B) - 1):
        rng = h[i - 1] - l[i - 1]
        if rng <= 0:
            continue
        if h[i] > h[i - 1] and c[i] < h[i - 1]:
            d, stop = -1, h[i]
        elif l[i] < l[i - 1] and c[i] > l[i - 1]:
            d, stop = 1, l[i]
        else:
            continue
        ent = float(c[i])
        rgo = abs(ent - stop)
        if rgo < 2 * U:
            continue
        j0 = int(np.searchsorted(mt, ti[i] + np.timedelta64(MINS, "m")))
        j1 = min(j0 + MINS * VELAS, len(mt))
        if j1 <= j0 + 5:
            continue
        hh, ll = mh[j0:j1], ml[j0:j1]
        b = np.flatnonzero(ll <= stop) if d > 0 else np.flatnonzero(hh >= stop)
        ib = int(b[0]) if len(b) else 10 ** 9
        bd, bs, cd, po, pw = contexto(ti[i] + np.timedelta64(MINS, "m"), j0)
        fila = {"i": i, "d": d, "e": round(ent, DEC), "s": round(float(stop), DEC),
                "rp": round(rgo / U, 1), "bd": bd, "bs": bs, "cd": cd,
                "po": po, "pw": pw, "res": {}}
        for nom, tp in (("ext150", ent + 1.5 * rng * d),
                        ("opuesto", float(h[i - 1] if d > 0 else l[i - 1]))):
            if (tp - ent) * d <= 0:
                continue
            a = np.flatnonzero(hh >= tp) if d > 0 else np.flatnonzero(ll <= tp)
            ia = int(a[0]) if len(a) else 10 ** 9
            rr = abs(tp - ent) / rgo
            if ia == ib == 10 ** 9:
                R, cual = (float(mc[j1 - 1]) - ent) * d / rgo, "abierta"
            elif ia < ib:
                R, cual = rr, "objetivo"
            else:
                R, cual = -1.0, "stop"
            fila["res"][nom] = {"tp": round(tp, DEC), "rr": round(rr, 3),
                                "R": round(R, 4), "q": cual}
        if fila["res"]:
            sen.append(fila)
    return {"velas": velas, "senales": sen, "pip": U, "coste": COSTE, "dec": DEC}


if __name__ == "__main__":
    D = {p: uno(p) for p in INSTR}
    js = json.dumps(D, separators=(",", ":"))
    open("data/crt_simulador.json", "w").write(js)
    print(f"{len(js)/1e6:.2f} MB")
    for p, v in D.items():
        print(f"  {p}: {len(v['velas'])} velas H12, {len(v['senales'])} senales, "
              f"{pd.Timestamp(v['velas'][0][0], unit='s').date()} -> "
              f"{pd.Timestamp(v['velas'][-1][0], unit='s').date()}")
