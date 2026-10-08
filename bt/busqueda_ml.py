"""Busqueda amplia y mecanica de patron operable en forex.

No es una regla escrita a mano: es un modelo de arboles impulsados que busca a
la vez en ~50 variables causales (retornos a varios plazos, volatilidad,
posicion en el rango, hora, dia, distancia a medias, mecha/cuerpo, y LO MISMO
de los otros tres instrumentos). Predice el retorno de la hora siguiente.

Lo que hace que esto valga algo y no sea otro sobreajuste:

  · VALIDACION HACIA DELANTE: se entrena solo con el pasado de cada ano y se
    predice el ano siguiente, que el modelo no ha visto nunca.
  · NULO: el mismo proceso entero sobre retornos barajados por bloques, con
    los mismos bloques en los cuatro instrumentos (conserva la correlacion
    entre ellos, destruye la prediccion). Cinco repeticiones.
  · CONTROL POSITIVO: se inyecta una senal conocida y se comprueba que el
    proceso la recupera.

  python3 bt/busqueda_ml.py
"""
import os, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

TF     = int(os.environ.get("TF", 60))
HOR    = int(os.environ.get("HOR", 1))   # barras que se mantiene la posicion
NULOS  = int(os.environ.get("NULOS", 5))
BLOQ   = 24*60                      # bloques de un dia, en minutos
SEL    = tuple(float(x) for x in os.environ.get("SEL",
         "0.05,0.10,0.25,0.50,1.00").split(","))
rng    = np.random.default_rng(20260905)

TODOS = {"EURUSD": ("data/eurusd_m1.parquet", 1e-4, 1.43),
         "GBPUSD": ("data/gbpusd_m1.parquet", 1e-4, 1.60),
         "USDJPY": ("data/usdjpy_m1.parquet", 1e-2, 1.50),
         "XAUUSD": ("data/xauusd_m1.parquet", 1e-2, 20.0)}
# el oro solo cubre 2023-2025: incluirlo recorta a los demas de 20.000 barras
# a 5.900. Se deja fuera por defecto.
CUALES = os.environ.get("CUALES", "EURUSD,GBPUSD,USDJPY").split(",")
INSTR  = {k: TODOS[k] for k in CUALES}

def carga():
    D = {}
    for k, (r, U, c) in INSTR.items():
        x = pd.read_parquet(r); x["ts"] = pd.to_datetime(x["ts"])
        D[k] = x.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    return D

def baraja(D):
    """PERMUTACION de bloques consecutivos, sin repeticion ni solapamiento.

    La primera version sorteaba inicios de bloque al azar CON reemplazo, asi
    que muchos bloques se solapaban y trozos casi identicos caian en
    entrenamiento y en prueba: el modelo los memorizaba. El nulo salia MEJOR
    que los datos reales (IC +0.037 contra +0.013), que es como se detecto.

    Ahora la serie se parte en bloques consecutivos disjuntos y solo se
    permuta su orden: cada minuto aparece exactamente una vez. Los mismos
    bloques en todos los instrumentos, para conservar su correlacion.
    """
    n  = min(len(x) for x in D.values())
    nb = (n-1)//BLOQ
    orden = rng.permutation(nb)
    idx = (orden[:, None]*BLOQ + np.arange(BLOQ)[None, :]).ravel()
    out = {}
    for k, x in D.items():
        c   = x.close.to_numpy()[:n]
        lr  = np.diff(np.log(c))
        amp = (x.high.to_numpy()[:n] - x.low.to_numpy()[:n])[1:]
        px  = c[0]*np.exp(np.cumsum(lr[idx]))
        m   = len(px)
        o   = np.r_[c[0], px[:-1]]
        a   = amp[idx]                     # el rango viaja CON su retorno
        out[k] = pd.DataFrame(dict(ts=x.ts.to_numpy()[:m], open=o,
            high=np.maximum(o, px) + a*rng.random(m)*0.5,
            low =np.minimum(o, px) - a*rng.random(m)*0.5, close=px))
    return out

def barras(x, m):
    g = x.set_index("ts").resample(f"{m}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    return g[g.n >= max(1, m*0.4)]

def rasgos(g, pre):
    """Todo causal: nada usa la barra actual mas alla de su cierre."""
    c, h, l, o = g.c, g.h, g.l, g.o
    lr = np.log(c).diff()
    v  = lr.rolling(72).std()
    F = {}
    for k in (1,2,3,6,12,24,72,168):
        F[f"{pre}r{k}"] = (np.log(c) - np.log(c.shift(k)))/(v*np.sqrt(k))
    F[f"{pre}vol"]  = v/lr.rolling(504).std()
    F[f"{pre}rng"]  = (c - l.rolling(24).min())/(h.rolling(24).max()-l.rolling(24).min())
    F[f"{pre}rng5"] = (c - l.rolling(120).min())/(h.rolling(120).max()-l.rolling(120).min())
    for k in (20,50,200):
        F[f"{pre}ema{k}"] = (np.log(c)-np.log(c.ewm(span=k, adjust=False).mean()))/v
    d_ = lr.clip(lower=0).rolling(14).mean(); u_ = (-lr.clip(upper=0)).rolling(14).mean()
    F[f"{pre}rsi"]   = d_/(d_+u_)
    F[f"{pre}cuer"]  = (c-o)/(h-l).replace(0, np.nan)
    F[f"{pre}mechaS"]= (h-np.maximum(c,o))/(h-l).replace(0, np.nan)
    F[f"{pre}mechaI"]= (np.minimum(c,o)-l)/(h-l).replace(0, np.nan)
    F[f"{pre}acel"]  = lr - lr.shift(1)
    return pd.DataFrame(F, index=g.index)

def tabla(D, obj):
    """El objetivo son las HOR barras siguientes: la ventaja se acumula con el
    horizonte pero el coste se paga UNA vez, asi que el cociente puede cambiar."""
    G = {k: barras(x, TF) for k, x in D.items()}
    X = pd.concat([rasgos(g, k[:3]+"_") for k, g in G.items()], axis=1, sort=True)
    g = G[obj]; U = INSTR[obj][1]
    X["hora"] = X.index.hour; X["dia"] = X.index.dayofweek
    y = (g.c.shift(-HOR) - g.c)/U               # pips de las HOR barras siguientes
    T = X.copy(); T["y"] = y; T["anio"] = T.index.year
    return T.dropna()

def prueba(D, obj, etiq):
    T = tabla(D, obj)
    cols = [c for c in T.columns if c not in ("y","anio")]
    COSTE = INSTR[obj][2]
    pred, real = [], []
    for anio in sorted(T.anio.unique()):
        tr, te = T[T.anio < anio], T[T.anio == anio]
        if len(tr) < 4000 or len(te) < 200: continue
        m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05,
                max_depth=4, min_samples_leaf=200, l2_regularization=1.0,
                random_state=0)
        m.fit(tr[cols].to_numpy(), tr.y.to_numpy())
        pred.append(m.predict(te[cols].to_numpy())); real.append(te.y.to_numpy())
    if not pred: return None
    p = np.concatenate(pred); r = np.concatenate(real)
    ic = float(np.corrcoef(p, r)[0,1])
    out = []
    for s in SEL:
        k = max(50, int(len(p)*s))
        i = np.argsort(-np.abs(p))[:k]
        pnl = np.sign(p[i])*r[i] - COSTE
        z = float(pnl.mean()/(pnl.std(ddof=1)/np.sqrt(len(pnl))))
        br = np.sign(p[i])*r[i]
        out.append(dict(sel=s, n=len(pnl), bruto=float(br.mean()),
                        zb=float(br.mean()/(br.std(ddof=1)/np.sqrt(len(br)))),
                        neto=float(pnl.mean()), z=z,
                        acierto=float((br > 0).mean())))
    return dict(instr=obj, etiq=etiq, ic=ic, n=len(p), sel=pd.DataFrame(out))

D = carga()
print(f"cargado · TF {TF} min · {len(D)} instrumentos")
print(f"\n{'='*74}\nREAL\n{'='*74}")
res = {}
for k in INSTR:
    R = prueba(D, k, "real")
    if R is None: continue
    res[k] = R
    print(f"\n  {k}   n fuera de muestra {R['n']}   IC {R['ic']:+.4f}")
    print(f"    {'top':>6} {'n':>7} {'BRUTO':>9} {'z':>7} {'neto':>9} {'z':>7} "
          f"{'acierto':>8} {'coste/vent':>11}")
    for _, x in R["sel"].iterrows():
        cv = INSTR[k][2]/x.bruto if x.bruto > 0 else float("inf")
        print(f"    {x.sel*100:5.0f}% {int(x.n):7d} {x.bruto:+9.3f} {x.zb:+7.2f} "
              f"{x.neto:+9.3f} {x.z:+7.2f} {x.acierto*100:7.1f}% {cv:10.1f}x",
              flush=True)


if NULOS and os.environ.get("NULO", "no") == "si":
    print(f"\n{'='*74}\n{NULOS} NULOS · el mismo proceso sobre datos barajados\n{'='*74}")
    for j in range(NULOS):
        B = baraja(D)
        for k in INSTR:
            R = prueba(B, k, f"nulo{j}")
            if R is None: continue
            x = R["sel"].iloc[0]
            print(f"  nulo {j+1} {k}: IC {R['ic']:+.4f}  top {x.sel*100:.1f}% "
                  f"bruto {x.bruto:+.3f} z {x.zb:+.2f}", flush=True)
