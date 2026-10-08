"""La afirmacion fundacional de todo el material de bctrades, aislada.

Dicen dos cosas OPUESTAS sobre el mismo suceso -que el precio se lleve el
extremo de la vela anterior-, y lo que las separa es donde cierra:

  saca el extremo y CIERRA FUERA con cuerpo  ->  "aumenta la probabilidad
                                                  de CONTINUIDAD"
  saca el extremo y CIERRA DENTRO            ->  se crea el rango; la
                                                  direccion es la CONTRARIA
  no saca nada (vela interna)                ->  consolidacion, invalido

Esto se puede medir sin simular ninguna operacion: sin coste, sin entrada, sin
stop, sin objetivo. Es estadistica condicionada pura. Si las dos celdas no se
separan, todo lo que se construye encima esta en el aire.
"""
import numpy as np, pandas as pd

def atr(h, l, c, n=20):
    pc = np.concatenate([[np.nan], c[:-1]])
    tr = np.nanmax(np.column_stack([h-l, np.abs(h-pc), np.abs(l-pc)]), axis=1)
    return pd.Series(tr).rolling(n).mean().to_numpy()

def clasifica(ref):
    """Clasifica cada vela por lo que hizo con la vela anterior.

    Devuelve un DataFrame con una fila por vela i (la que actua), la vela i-1
    es la base. El resultado se mide en la vela i+1, que aun no ha pasado.
    """
    h, l, o, c = (ref[x].to_numpy() for x in ("high","low","open","close"))
    n = len(ref)
    a = atr(h, l, c, 20)

    ph, pl = np.roll(h,1), np.roll(l,1)
    ph[0] = pl[0] = np.nan

    saca_alto = h > ph
    saca_bajo = l < pl
    ambos = saca_alto & saca_bajo
    solo_alto = saca_alto & ~saca_bajo
    solo_bajo = saca_bajo & ~saca_alto
    interna = ~saca_alto & ~saca_bajo

    # "cierra con cuerpo mas alla del nivel"
    fuera_alto = solo_alto & (c > ph)
    dentro_alto = solo_alto & (c <= ph)
    fuera_bajo = solo_bajo & (c < pl)
    dentro_bajo = solo_bajo & (c >= pl)

    # lo que hace la vela SIGUIENTE, normalizado por el ATR de la referencia
    sig = np.roll(c, -1); sig[-1] = np.nan
    ret = (sig - c) / a

    clase = np.full(n, "", dtype=object)
    clase[fuera_alto]  = "saca alto · cierra FUERA"
    clase[dentro_alto] = "saca alto · cierra DENTRO"
    clase[fuera_bajo]  = "saca bajo · cierra FUERA"
    clase[dentro_bajo] = "saca bajo · cierra DENTRO"
    clase[interna]     = "vela interna (no saca)"
    clase[ambos]       = "saca los dos extremos"

    # lo que PREDICEN ellos, como signo: +1 esperan subida, -1 bajada
    pred = np.zeros(n)
    pred[fuera_alto]  = +1     # continuidad al alza
    pred[dentro_alto] = -1     # rango creado, reversion a la baja
    pred[fuera_bajo]  = -1     # continuidad a la baja
    pred[dentro_bajo] = +1     # rango creado, reversion al alza

    return pd.DataFrame(dict(ts=ref["id"].to_numpy(), clase=clase, pred=pred,
                             ret=ret, atr=a)).iloc[1:-1].dropna(subset=["ret","atr"])

def resumen(t, etiqueta):
    print(f"\n  {etiqueta}")
    print(f"     {'clase':30s} {'n':>7s} {'media':>9s} {'IC95':>20s} {'acierto':>9s}")
    orden = ["saca alto · cierra FUERA", "saca alto · cierra DENTRO",
             "saca bajo · cierra FUERA", "saca bajo · cierra DENTRO",
             "vela interna (no saca)", "saca los dos extremos"]
    for k in orden:
        g = t[t.clase == k]
        if len(g) < 30: continue
        x = g.ret.to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x))
        # acierto en el sentido que ELLOS predicen
        p = g.pred.to_numpy()
        ac = float(((x*p) > 0).mean()) if p[0] != 0 else float("nan")
        ic = f"[{x.mean()-1.96*ee:+.4f},{x.mean()+1.96*ee:+.4f}]"
        if p[0] == 0:
            print(f"     {k:30s} {len(g):>7,} {x.mean():>+9.4f} {ic:>20s} {'—':>9s}")
        else:
            marca = "  <<<" if (x.mean() - 1.96*ee) * p[0] > 0 else ""
            print(f"     {k:30s} {len(g):>7,} {x.mean():>+9.4f} {ic:>20s} "
                  f"{100*ac:>8.2f}%{marca}")
    # la prueba de verdad: la señal firmada, juntando las cuatro celdas
    d = t[t.pred != 0]
    x = (d.ret * d.pred).to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x))
    print(f"     {'TODO junto, en su sentido':30s} {len(x):>7,} {x.mean():>+9.4f} "
          f"[{x.mean()-1.96*ee:+.4f},{x.mean()+1.96*ee:+.4f}]  {100*(x>0).mean():>8.2f}%")
    # y por separado los dos polos, que predicen cosas opuestas
    for pol, sel in (("solo CONTINUIDAD (cierra fuera)", d.clase.str.contains("FUERA")),
                     ("solo REVERSIÓN (cierra dentro)",  d.clase.str.contains("DENTRO"))):
        g = d[sel]; y = (g.ret*g.pred).to_numpy()
        if len(y) < 30: continue
        e2 = y.std(ddof=1)/np.sqrt(len(y))
        print(f"     {pol:30s} {len(y):>7,} {y.mean():>+9.4f} "
              f"[{y.mean()-1.96*e2:+.4f},{y.mean()+1.96*e2:+.4f}]  {100*(y>0).mean():>8.2f}%")
