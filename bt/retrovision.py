"""¿Por que los ejemplos se ven perfectos y los numeros no?

Mide la diferencia entre la poblacion EX ANTE (todo lo que barre un extremo, se
sepa o no lo que hara despues) y el conjunto EX POST que queda visible al
repasar un grafico (solo lo que reacciono, porque lo que no reacciono deja de
llamarse turtle soup y pasa a llamarse liquidity run).
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "bt")
from estrategia_ob import Config, preparar, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config()
org = pd.Timestamp("2020-01-01") + pd.Timedelta(hours=cfg.ancla_h4)
h4 = m1.set_index("ts").resample("4h", origin=org, label="left", closed="left").agg(
    open=("open","first"), high=("high","max"), low=("low","min"),
    close=("close","last")).dropna().reset_index()
h4["p_hi"], h4["p_lo"] = h4.high.shift(1), h4.low.shift(1)
h4 = h4.dropna().reset_index(drop=True)

t1 = m1["ts"].to_numpy(); HH=m1["high"].to_numpy(); LL=m1["low"].to_numpy()

print("=== 1. QUE PASA CON TODAS LAS VELAS H4 QUE BARREN EL EXTREMO ANTERIOR ===")
for lado, nom in ((True,"barre el MAXIMO anterior"), (False,"barre el MINIMO anterior")):
    if lado:
        barre = h4.high > h4.p_hi
        ls = barre & (h4.close < h4.p_hi)     # turtle soup: cierra de vuelta dentro
        lr = barre & (h4.close >= h4.p_hi)    # liquidity run: cierra fuera
    else:
        barre = h4.low < h4.p_lo
        ls = barre & (h4.close > h4.p_lo)
        lr = barre & (h4.close <= h4.p_lo)
    n, nls, nlr = int(barre.sum()), int(ls.sum()), int(lr.sum())
    print(f"  {nom}: {n:>5} velas")
    print(f"     -> turtle soup (cierra dentro) : {nls:>5}  ({100*nls/n:.1f}%)")
    print(f"     -> liquidity run (cierra fuera): {nlr:>5}  ({100*nlr/n:.1f}%)  <- invisible al repasar")

print("\n=== 2. DE LOS TURTLE SOUP CONFIRMADOS, ¿CUANTOS COMPLETAN EL RANGO? ===")
print("   (llegar al extremo OPUESTO antes que al extremo del propio barrido)")
res = {}
for lado, nom in ((True,"cortos (barrido de maximo)"), (False,"largos (barrido de minimo)")):
    ok = fail = 0; horizonte = 48*60
    sub = h4[(h4.high > h4.p_hi) & (h4.close < h4.p_hi)] if lado else \
          h4[(h4.low  < h4.p_lo) & (h4.close > h4.p_lo)]
    for r in sub.itertuples():
        # se actua al CIERRE de la vela H4 que hizo el turtle soup
        ini = np.datetime64(r.ts + pd.Timedelta(hours=4))
        i0 = int(np.searchsorted(t1, ini)); i1 = min(i0+horizonte, len(t1))
        if i0 >= len(t1) or i1 <= i0: continue
        a, b = HH[i0:i1], LL[i0:i1]
        if lado:
            gtp, gsl = b <= r.p_lo, a >= r.high      # objetivo: minimo del rango
        else:
            gtp, gsl = a >= r.p_hi, b <= r.low
        itp = int(np.argmax(gtp)) if gtp.any() else 10**9
        isl = int(np.argmax(gsl)) if gsl.any() else 10**9
        if itp < isl: ok += 1
        elif isl < 10**9: fail += 1
    tot = ok + fail
    res[nom] = (ok, tot)
    print(f"  {nom}: completa el rango {ok}/{tot} = {100*ok/tot:.1f}%")

print("\n=== 3. LO QUE VE EL OJO FRENTE A LO QUE HAY ===")
tot_ok = sum(v[0] for v in res.values()); tot_n = sum(v[1] for v in res.values())
print(f"  Al repasar un grafico marcas turtle soups y ves que 'casi siempre' funcionan,")
print(f"  porque los que no reaccionaron no los marcas: son liquidity runs.")
print(f"  Ex ante, contando todo: un barrido de extremo H4 acaba completando el rango")
print(f"  el {100*tot_ok/tot_n:.1f}% de las veces, y eso YA condicionado a que haya cerrado dentro.")

print("\n=== 4. EL SESGO DE LA SEGUNDA CAPA: ¿cuantos barridos hay por rango? ===")
# cuantas veces el precio barre el extremo VARIAS veces antes de irse
cfgp = Config(); ch = preparar(m1, cfgp)
g = ch.dropna(subset=["r_hi"]).groupby("h4_id")
mult = g.apply(lambda x: int(((x.high > x.r_hi).any()) + ((x.low < x.r_lo).any())),
               include_groups=False)
print(f"  velas H4 que barren los DOS extremos del rango anterior: "
      f"{int((mult==2).sum()):>5} de {len(mult)} ({100*(mult==2).mean():.1f}%)")
print("  En esos casos, al repasar eliges a posteriori cual era 'el bueno'.")
