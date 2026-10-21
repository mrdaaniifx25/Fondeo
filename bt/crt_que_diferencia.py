"""¿Que diferencia al CRT que gana del que pierde? Con TODO a la vez.

    "no hay manera de encontrar el punto en el cual ese ganador se diferencie
     de los otros? un patron, un orderblock, fvg, patron de vela...?"

Probar las cosas de una en una es debil: cada una por separado puede no verse
y aun asi haber senal en la combinacion. Asi que aqui se le dan TREINTA
variables a la vez a un modelo de arboles y se le deja buscar.

Si un modelo con todas las variables no separa a los ganadores de los
perdedores fuera de muestra, ningun ojo humano ni ningun indicador suelto lo
va a hacer, porque el modelo habria encontrado la combinacion.

Variables, todas causales y medidas al cierre de la vela de manipulacion:

  del setup     tamano, profundidad del barrido, posicion del cierre,
                cuerpo/rango, mecha superior, mecha inferior, envolvente
  order block   tamano de la ultima vela opuesta, su cuerpo/rango
                ("gruesa y pesada"), su distancia a la entrada
  FVG           hay hueco sin rellenar a favor, su distancia, su tamano,
                y si hay uno EN CONTRA entre la entrada y el objetivo
  contexto      distancia a EMA 20/50/200, ATR relativo, hora, dia, retornos
                de 5 y 20 velas, estocastico, RSI, posicion en el rango del
                dia y de la semana, racha de velas, R:R, coste, lado

VALIDACION HACIA DELANTE: se entrena solo con los anos anteriores y se predice
el siguiente. NULO: lo mismo con el resultado barajado por bloques mensuales.

AVISO, y es la leccion de esta medicion: un nulo que baraja el RESULTADO NO
detecta una mirada al futuro metida en una VARIABLE. Si la variable ve el
futuro, con el resultado barajado tampoco predice nada, asi que el nulo sale
limpio y la fuga pasa. La primera version de este script calculaba la posicion
en el rango del dia con el rango COMPLETO del dia -velas posteriores incluidas-
y daba IC +0,2725 contra nulos de +-0,01. Las variables hay que auditarlas una
a una; el nulo no las cubre.

  python3 bt/crt_que_diferencia.py
"""
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

INSTR = {"EURUSD": (["data/eurusd_m1.parquet"], 1e-4, 1.43),
         "GBPUSD": (["data/gbpusd_m1.parquet"], 1e-4, 1.60),
         "USDJPY": (["data/usdjpy_m1.parquet"], 1e-2, 1.50),
         "NAS100": (["data/nsxusd_m1.parquet"], 1e-0, 1.50),
         "SPX500": (["data/spxusd_m1.parquet"], 1e-0, 0.60),
         "XAUUSD": (["data/xauusd_m1_2020_2022.parquet", "data/xauusd_m1.parquet",
                     "data/xauusd_m1_2026.parquet"], 1e-0, 0.30)}
TF, VELAS = 240, 3
rng = np.random.default_rng(2026)


def fvgs(h, l, i, n=20):
    """Huecos de valor justo sin rellenar en las ultimas n velas, causal.

    Alcista: minimo de la vela k por encima del maximo de la k-2.
    Se considera relleno si el precio ha vuelto a entrar en el hueco despues.
    """
    out = []
    for k in range(max(2, i-n), i+1):
        if l[k] > h[k-2]:
            a, b = h[k-2], l[k]
            if l[k:i+1].min() > a: out.append((+1, a, b))
        if h[k] < l[k-2]:
            a, b = h[k], l[k-2]
            if h[k:i+1].max() < b: out.append((-1, a, b))
    return out


def datos(par):
    rutas, U, C = INSTR[par]
    M = pd.concat([pd.read_parquet(f) for f in rutas], ignore_index=True)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    B = M.set_index("ts").resample(f"{TF}min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    B = B[B.n >= TF*0.3]
    o, h, l, c = (B[x].to_numpy(np.float64) for x in "ohlc")
    ti = B.index.to_numpy(); n = len(c)
    tr = np.maximum(h-l, np.maximum(np.abs(h-np.roll(c,1)), np.abs(l-np.roll(c,1))))
    atr = pd.Series(tr).rolling(20).mean().to_numpy()
    atr_med = pd.Series(atr).rolling(100).median().to_numpy()
    e20 = pd.Series(c).ewm(span=20, adjust=False).mean().to_numpy()
    e50 = pd.Series(c).ewm(span=50, adjust=False).mean().to_numpy()
    e200 = pd.Series(c).ewm(span=200, adjust=False).mean().to_numpy()
    hh14 = pd.Series(h).rolling(14).max().to_numpy()
    ll14 = pd.Series(l).rolling(14).min().to_numpy()
    r14 = hh14-ll14
    K = pd.Series(100*(c-ll14)/np.where(r14==0,np.nan,r14)).rolling(3).mean().to_numpy()
    d_ = np.diff(c, prepend=c[0])
    gg = pd.Series(np.where(d_>0,d_,0.)).ewm(alpha=1/14, adjust=False).mean()
    pp = pd.Series(np.where(d_<0,-d_,0.)).ewm(alpha=1/14, adjust=False).mean()
    RSI = (100-100/(1+gg/pp.replace(0,np.nan))).to_numpy()
    dia = pd.Series(ti).dt.floor("1440min").to_numpy()
    sem = pd.Series(ti).dt.to_period("W").astype(str).to_numpy()
    # maximo y minimo ACUMULADOS dentro del dia y de la semana en curso.
    # La version anterior usaba el rango COMPLETO del dia, que incluye velas
    # posteriores a la entrada: eso era mirar al futuro y disparaba el IC.
    dfr = pd.DataFrame(dict(h=h, l=l, dia=dia, sem=sem))
    d_hi = dfr.groupby("dia").h.cummax().to_numpy()
    d_lo = dfr.groupby("dia").l.cummin().to_numpy()
    s_hi = dfr.groupby("sem").h.cummax().to_numpy()
    s_lo = dfr.groupby("sem").l.cummin().to_numpy()
    mh, ml, mc, mt = (M.high.to_numpy(), M.low.to_numpy(),
                      M.close.to_numpy(), M.ts.to_numpy())
    filas = []
    for i in range(210, n-1):
        if not np.isfinite(atr[i]) or atr[i] <= 0: continue
        rgo_v = h[i-1]-l[i-1]
        if rgo_v <= 0: continue
        if   h[i] > h[i-1] and c[i] < h[i-1]: lado, stop, obj = -1, h[i], l[i-1]
        elif l[i] < l[i-1] and c[i] > l[i-1]: lado, stop, obj = +1, l[i], h[i-1]
        else: continue
        ent = c[i]; rgo = abs(ent-stop)
        if rgo < 2*U or (obj-ent)*lado <= 0: continue
        j0 = int(np.searchsorted(mt, ti[i]+np.timedelta64(TF,"m")))
        j1 = min(j0+TF*VELAS, len(mt))
        if j1 <= j0+3: continue
        hh_, ll_ = mh[j0:j1], ml[j0:j1]
        a = np.flatnonzero(hh_ >= obj) if lado>0 else np.flatnonzero(ll_ <= obj)
        b = np.flatnonzero(ll_ <= stop) if lado>0 else np.flatnonzero(hh_ >= stop)
        ia = int(a[0]) if len(a) else 10**9; ib = int(b[0]) if len(b) else 10**9
        rr = abs(obj-ent)/rgo
        R = (float(mc[j1-1])-ent)*lado/rgo if ia==ib==10**9 else (rr if ia<ib else -1.0)
        # --- order block: ultima vela de cierre opuesto antes del impulso
        ob_t = ob_c = ob_d = np.nan
        for k in range(i-1, max(i-11, 0), -1):
            if (c[k] < o[k]) if lado > 0 else (c[k] > o[k]):
                ob_t = (h[k]-l[k])/atr[i]
                ob_c = abs(c[k]-o[k])/max(h[k]-l[k], 1e-12)
                ob_d = abs(ent-(h[k]+l[k])/2)/rgo
                break
        # --- FVG
        G = fvgs(h, l, i)
        favor = [g for g in G if g[0] == lado]
        contra = [g for g in G if g[0] == -lado]
        fv_d = min([abs(ent-(g[1]+g[2])/2)/rgo for g in favor], default=np.nan)
        fv_t = max([(g[2]-g[1])/atr[i] for g in favor], default=0.0)
        en_medio = any(min(ent,obj) < (g[1]+g[2])/2 < max(ent,obj) for g in contra)
        cuerpo = abs(c[i]-o[i])/max(h[i]-l[i], 1e-12)
        racha = 0
        for k in range(i-1, max(i-11, 0), -1):
            if np.sign(c[k]-o[k]) == np.sign(c[i]-o[i]): racha += 1
            else: break
        rd = d_hi[i]-d_lo[i]
        rs = s_hi[i]-s_lo[i]
        filas.append(dict(
            par=par, ts=pd.Timestamp(ti[i]), R=R, neta=R - C*U/rgo, gana=int(ia<ib),
            tam=rgo_v/atr[i], prof=abs(stop-(h[i-1] if lado<0 else l[i-1]))/rgo_v,
            cierre=(c[i]-l[i-1])/rgo_v if lado>0 else (h[i-1]-c[i])/rgo_v,
            cuerpo=cuerpo, mecha_a=(h[i]-max(o[i],c[i]))/max(h[i]-l[i],1e-12),
            mecha_b=(min(o[i],c[i])-l[i])/max(h[i]-l[i],1e-12),
            envuelve=int(h[i] > h[i-1] and l[i] < l[i-1]),
            ob_tam=ob_t, ob_cuerpo=ob_c, ob_dist=ob_d,
            fvg_hay=int(len(favor) > 0), fvg_dist=fv_d, fvg_tam=fv_t,
            fvg_contra=int(en_medio),
            d20=(c[i]-e20[i])*lado/atr[i], d50=(c[i]-e50[i])*lado/atr[i],
            d200=(c[i]-e200[i])*lado/atr[i],
            atr_rel=atr[i]/max(atr_med[i], 1e-12), hora=pd.Timestamp(ti[i]).hour,
            dsem=pd.Timestamp(ti[i]).dayofweek,
            ret5=(c[i]-c[i-5])*lado/atr[i], ret20=(c[i]-c[i-20])*lado/atr[i],
            K=K[i], RSI=RSI[i], racha=racha,
            pos_dia=(c[i]-d_lo[i])/max(rd,1e-12),
            pos_sem=(c[i]-s_lo[i])/max(rs,1e-12),
            rr=rr, cos=C*U/rgo, lado=lado))
    return pd.DataFrame(filas)


VAR = ["tam","prof","cierre","cuerpo","mecha_a","mecha_b","envuelve","ob_tam",
       "ob_cuerpo","ob_dist","fvg_hay","fvg_dist","fvg_tam","fvg_contra","d20",
       "d50","d200","atr_rel","hora","dsem","ret5","ret20","K","RSI","racha",
       "pos_dia","pos_sem","rr","cos","lado"]


def adelante(D, y):
    """Entrena con lo anterior a cada ano y predice ese ano. Nunca ve el futuro."""
    P = []
    for a in range(2021, 2027):
        tr, te = D.ano < a, D.ano == a
        if tr.sum() < 500 or te.sum() < 50: continue
        m = HistGradientBoostingRegressor(max_iter=250, learning_rate=0.05,
                                          max_depth=4, min_samples_leaf=40,
                                          random_state=0)
        m.fit(D.loc[tr, VAR], y[tr.to_numpy()])
        P.append(pd.DataFrame(dict(p=m.predict(D.loc[te, VAR]),
                                   real=D.loc[te, "neta"].to_numpy())))
    if not P: return None
    Q = pd.concat(P, ignore_index=True)
    q = Q.p.quantile(0.8)
    return dict(n=len(Q), ic=float(np.corrcoef(Q.p, Q.real)[0,1]),
                top=float(Q.real[Q.p >= q].mean()), base=float(Q.real.mean()))


if __name__ == "__main__":
    D = pd.concat([datos(p) for p in INSTR], ignore_index=True)
    D["ano"] = D.ts.dt.year
    D = D.sort_values("ts").reset_index(drop=True)
    D.to_csv("data/crt_que_diferencia.csv", index=False)
    print(f"=== ¿QUE DIFERENCIA AL CRT GANADOR? · {len(D)} setups · H4 · 6 instrumentos ===\n")
    print(f"  acierto global {D.gana.mean():.1%}   ·   R neta media {D.neta.mean():+.4f}\n")

    print("  1 · cada variable POR SEPARADO: diferencia entre el quintil alto y el bajo\n")
    print(f"    {'variable':>12} {'quintil bajo':>13} {'quintil alto':>13} {'dif':>8}")
    for v in VAR:
        x = D[v].astype(float)
        if x.nunique() < 5: continue
        lo, hi = x.quantile(0.2), x.quantile(0.8)
        a, b = D.neta[x <= lo].mean(), D.neta[x >= hi].mean()
        if abs(b-a) > 0.04:
            print(f"    {v:>12} {a:>+13.4f} {b:>+13.4f} {b-a:>+8.4f}")
    print("    (solo se listan las que mueven mas de 0,04 R)\n")

    print("  2 · TODAS a la vez, con validacion hacia delante\n")
    real = adelante(D, D.neta.to_numpy())
    print(f"    n fuera de muestra {real['n']}")
    print(f"    correlacion prediccion-resultado (IC)   {real['ic']:+.4f}")
    print(f"    R neta del quintil que el modelo prefiere {real['top']:+.4f}")
    print(f"    R neta de todas                          {real['base']:+.4f}")
    print(f"    mejora                                   {real['top']-real['base']:+.4f}\n")

    print("  3 · el mismo proceso con el resultado BARAJADO por meses\n")
    D["mes"] = D.ts.dt.to_period("M").astype(str)
    ics, tops = [], []
    for k in range(5):
        y = D.neta.to_numpy().copy()
        bl = [g.index.to_numpy() for _, g in D.groupby("mes", sort=True)]
        orden = rng.permutation(len(bl))
        idx = np.concatenate([bl[j] for j in orden])
        y = y[idx]
        r = adelante(D, y)
        ics.append(r["ic"]); tops.append(r["top"]-r["base"])
        print(f"    nulo {k+1}: IC {r['ic']:+.4f}   mejora del quintil {tops[-1]:+.4f}")
    print(f"\n    IC real {real['ic']:+.4f}  ·  nulos de {min(ics):+.4f} a {max(ics):+.4f}")
    print(f"    mejora real {real['top']-real['base']:+.4f}  ·  nulos de "
          f"{min(tops):+.4f} a {max(tops):+.4f}")
