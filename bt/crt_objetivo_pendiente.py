"""El contraste que propone el usuario, con su control de permutacion.

    "si pasa lo que he visto es porque hay algun otro rango pendiente de ocurrir"

Hipotesis: un CRT falla mas cuando hay un objetivo superior SIN CUMPLIR
tirando del precio en sentido contrario.

Contraste declarado: R bruta de las senales A FAVOR del objetivo diario
pendiente menos las que van EN CONTRA. Se esperaba positivo ANTES de mirar.

Control: se baraja la etiqueta del objetivo pendiente 4.000 veces sobre las
mismas senales. Eso responde a la vez a "¿es casualidad?" y a "¿es por haber
probado 14 filtros?", porque el nulo pasa por el mismo embudo.

  python3 bt/crt_objetivo_pendiente.py
"""
import json, numpy as np, pandas as pd

D = json.load(open("data/crt_simulador.json"))
filas = []
for par, P in D.items():
    for s in P["senales"]:
        r = s["res"].get("ext150")
        if not r: continue
        filas.append(dict(par=par, t=P["velas"][s["i"]][0], d=s["d"], po=s["po"],
                          pw=s["pw"], rr=r["rr"], R=r["R"], neta=r["R"]-P["coste"]/s["rp"],
                          tp=1 if r["q"] == "objetivo" else 0))
T = pd.DataFrame(filas)
T["ano"] = pd.to_datetime(T.t, unit="s").dt.year
T["blq"] = T.par + "|" + (pd.to_datetime(T.t, unit="s").dt.isocalendar().week.astype(str)
                          + pd.to_datetime(T.t, unit="s").dt.year.astype(str))
T = T[T.po != 0].reset_index(drop=True)
T["fav"] = (T.po == T.d)

def dif(fav, col="R"):
    return T[col][fav].mean() - T[col][~fav].mean()

obs = dif(T.fav)
print(f"=== EL OBJETIVO DIARIO PENDIENTE · {len(T)} senales con objetivo vivo ===\n")
print(f"  a favor   n {T.fav.sum():>5}   bruta {T.R[T.fav].mean():+.4f}   "
      f"neta {T.neta[T.fav].mean():+.4f}   acierto {T.tp[T.fav].mean():.1%}")
print(f"  en contra n {(~T.fav).sum():>5}   bruta {T.R[~T.fav].mean():+.4f}   "
      f"neta {T.neta[~T.fav].mean():+.4f}   acierto {T.tp[~T.fav].mean():.1%}")
print(f"\n  DIFERENCIA observada (bruta): {obs:+.4f}")

rng = np.random.default_rng(11)
N = 4000
nulo = np.array([dif(pd.Series(rng.permutation(T.fav.to_numpy()))) for _ in range(N)])
p = float((np.abs(nulo) >= abs(obs)).mean())
print(f"  nulo por permutacion ({N}): media {nulo.mean():+.4f}  "
      f"desv {nulo.std():.4f}  |  p a dos colas = {p:.3f}")
print(f"  la diferencia observada esta a {obs/nulo.std():+.2f} desviaciones del nulo")

# nulo por BLOQUES: se rotan semanas enteras, que respeta la correlacion
# dentro de la semana. Es el mismo nulo de bloques del resto del repositorio.
print("\n  el mismo nulo pero rotando semanas enteras (mas exigente):")
bloques = [g.index.to_numpy() for _, g in T.groupby("blq", sort=True)]
Rv, favv = T.R.to_numpy(), T.fav.to_numpy()
nulo2 = []
for _ in range(N // 2):
    k = int(rng.integers(1, len(bloques)))
    orden = np.concatenate(bloques[k:] + bloques[:k])
    rp = Rv[orden]
    nulo2.append(rp[favv].mean() - rp[~favv].mean())
nulo2 = np.array(nulo2)
p2 = float((np.abs(nulo2) >= abs(obs)).mean())
print(f"    desv {nulo2.std():.4f}  ·  p = {p2:.3f}  ·  {obs/nulo2.std():+.2f} desviaciones")

print("\n  ¿aguanta partido? a favor, por instrumento y por ano\n")
F = T[T.fav]
zz = lambda v: float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))) if len(v) > 5 else np.nan
print(f"    {'':>8} {'n':>5} {'acierto':>8} {'azar':>7} {'BRUTA':>9} {'z':>7} {'NETA':>9}")
for k, x in list(F.groupby("par")) + list(F.groupby("ano")):
    print(f"    {str(k):>8} {len(x):>5} {x.tp.mean():>7.1%} {(1/(1+x.rr)).mean():>6.1%} "
          f"{x.R.mean():>+9.4f} {zz(x.R):>+7.2f} {x.neta.mean():>+9.4f}")

print("\n  y el mismo contraste en SEMANAL, que la hipotesis exige que vaya igual:")
W = pd.DataFrame(filas); W = W[W.pw != 0]
fw = (W.pw == W.d)
print(f"    a favor   n {fw.sum():>5}  bruta {W.R[fw].mean():+.4f}")
print(f"    en contra n {(~fw).sum():>5}  bruta {W.R[~fw].mean():+.4f}")
print(f"    DIFERENCIA: {W.R[fw].mean()-W.R[~fw].mean():+.4f}")
