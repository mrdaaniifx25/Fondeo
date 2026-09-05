"""Liquidez simple, doble y triple.  Su unica afirmacion con gradiente.

  «El precio puede tomar la liquidez las veces que quiera mientras siga
   cerrando dentro de la vela base. La doble y la triple AUMENTAN LA
   PROBABILIDAD del movimiento.»

EL SESGO QUE HAY QUE MATAR: con cada barrido extra el minimo baja, asi que el
stop se aleja solo. Con objetivo fijo en el extremo opuesto, eso sube el
acierto SIN NINGUNA VENTAJA, solo por geometria. Por eso se mide dos veces:

  (a) la operacion natural  objetivo = extremo opuesto de la vela base
                            stop     = extremo del barrido
      -> el acierto sube por geometria; lo que decide es la esperanza en R.

  (b) carrera SIMETRICA     +1 ATR contra -1 ATR desde la misma entrada
      -> misma distancia para k=1, 2 y 3. Si el gradiente es real, aqui sale.
         Si solo sale en (a), era el stop alejandose.
"""
import numpy as np, pandas as pd

def secuencias(ref, usar_cuerpo=False):
    """Encuentra vela base + k velas seguidas que barren el MISMO extremo y
    cierran dentro. Devuelve una fila por secuencia."""
    h, l, o, c = (ref[x].to_numpy() for x in ("high","low","open","close"))
    n = len(ref)
    filas = []
    for i in range(n - 2):
        rh, rl = h[i], l[i]
        if not np.isfinite(rh) or rh <= rl: continue
        # "cerrar dentro" del rango o del cuerpo, segun la variante
        if usar_cuerpo:
            dh, dl = max(o[i], c[i]), min(o[i], c[i])
            if dh <= dl: continue
        else:
            dh, dl = rh, rl
        for alcista in (True, False):
            j = i + 1; k = 0; ext = np.nan
            while j < n:
                barre = (l[j] < rl and h[j] <= rh) if alcista else (h[j] > rh and l[j] >= rl)
                dentro = dl <= c[j] <= dh
                if not (barre and dentro):
                    break
                nuevo = l[j] if alcista else h[j]
                ext = nuevo if k == 0 else (min(ext, nuevo) if alcista else max(ext, nuevo))
                k += 1; j += 1
            # la entrada es el cierre de la ULTIMA vela del barrido, la i+k
            if k >= 1 and (i + k + 1) < n:
                filas.append(dict(i_base=i, i_ent=i+k, k=k, alcista=alcista,
                                  entrada=c[i+k], objetivo=rh if alcista else rl,
                                  stop=ext))
    return pd.DataFrame(filas)

def resuelve(seq, ref, m1, tfh, atr, horizonte=10):
    """Dos carreras a la vez, resueltas vela a vela en M1."""
    fin = ref["fin"].to_numpy()
    t1 = m1["ts"].to_numpy(); H = m1["high"].to_numpy(); L = m1["low"].to_numpy()
    barras = int(horizonte * tfh * 60)
    nat = np.full(len(seq), np.nan); sim = np.full(len(seq), np.nan)
    rr = np.full(len(seq), np.nan)
    for z, r in enumerate(seq.itertuples()):
        ie = int(r.i_ent)
        if ie < 0 or ie >= len(fin): continue
        a = atr[ie]
        if not np.isfinite(a) or a <= 0: continue
        e = r.entrada
        riesgo = abs(e - r.stop); premio = abs(r.objetivo - e)
        if riesgo <= 0 or premio <= 0: continue
        rr[z] = premio / riesgo
        j0 = int(np.searchsorted(t1, fin[ie], side="right"))
        j1 = min(j0 + barras, len(t1))
        if j0 >= len(t1): continue
        hh, ll = H[j0:j1], L[j0:j1]
        # (a) natural
        if r.alcista: ga, gb = hh >= r.objetivo, ll <= r.stop
        else:         ga, gb = ll <= r.objetivo, hh >= r.stop
        ia = int(np.argmax(ga)) if ga.any() else 10**9
        ib = int(np.argmax(gb)) if gb.any() else 10**9
        if ia != 10**9 or ib != 10**9: nat[z] = 1.0 if ia < ib else 0.0
        # (b) simetrica, misma distancia para todos los k
        arr, aba = e + a, e - a
        ga2, gb2 = hh >= arr, ll <= aba
        i2 = int(np.argmax(ga2)) if ga2.any() else 10**9
        i3 = int(np.argmax(gb2)) if gb2.any() else 10**9
        if i2 != 10**9 or i3 != 10**9:
            gana_arriba = i2 < i3
            sim[z] = 1.0 if (gana_arriba == r.alcista) else 0.0
    return seq.assign(nat=nat, sim=sim, rr=rr)

def tabla(t, etiqueta):
    print(f"\n  {etiqueta}")
    print(f"     {'':12s} {'n':>7s}   {'(a) NATURAL':>26s}      {'(b) SIMÉTRICA':>24s}")
    print(f"     {'liquidez':12s} {'':>7s}   {'acierto':>9s} {'R:R':>6s} {'esperanza R':>9s}"
          f"      {'acierto':>9s} {'IC95':>16s}")
    for k, sel in (("simple",  t.k == 1), ("doble",   t.k == 2), ("triple+", t.k >= 3)):
        g = t[sel]
        gn = g.dropna(subset=["nat"]); gs = g.dropna(subset=["sim"])
        if len(gn) < 30:
            print(f"     {k:12s} {len(g):>7,}   (pocas)"); continue
        pn = gn.nat.mean(); rr = gn.rr.median()
        # esperanza real: cada operacion gana su propio R:R o pierde 1
        R = np.where(gn.nat.to_numpy() > 0, gn.rr.to_numpy(), -1.0)
        esp = float(R.mean())
        ps = gs.sim.mean(); ee = np.sqrt(ps*(1-ps)/len(gs))
        marca = "  <<<" if ps - 1.96*ee > 0.50 else ""
        print(f"     {k:12s} {len(g):>7,}   {100*pn:>8.2f}% {rr:>6.2f} {esp:>+9.3f}"
              f"      {100*ps:>8.2f}% [{100*(ps-1.96*ee):5.2f},{100*(ps+1.96*ee):5.2f}]{marca}")
