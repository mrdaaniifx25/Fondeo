"""Controles sobre Strategy 4.3.23 en XAUUSD.

La estrategia la genero StrategyQuant X buscando entre millones de
combinaciones. Los parametros exactos (GannHiLo 5, 51 velas, ATR 95, salida a
5 barras, validez 10) son los SUPERVIVIENTES de esa busqueda. Antes de
creersela hay que preguntarle cuatro cosas:

  1 LARGOS AL AZAR   con la misma geometria y el mismo numero de operaciones.
                     El oro paso de 1.850 a 3.300 en este periodo: cualquier
                     estrategia larga gana. ¿Bate la senal al azar?
  2 VECINDARIO       si la ventaja es real, los parametros vecinos tambien
                     funcionan. Si solo funciona la combinacion exacta, es
                     sobreajuste.
  3 NULO             la misma estrategia sobre oro con los bloques permutados.
  4 SIN FILTRO       ¿que aporta el GannHiLo? ¿y el maximo de 51?

  python3 bt/sqx_controles.py
"""
import os, itertools, numpy as np, pandas as pd

CAP0, RIESGO = 100_000.0, 0.01
COM_LOTE, SPREAD, SWAP, ONZAS = 6.0, 0.2, 35.0, 100.0
H_INI, H_FIN = 1*60+30, 23*60+30
rng = np.random.default_rng(20260905)

M = pd.concat([pd.read_parquet("data/xauusd_m1.parquet"),
               pd.read_parquet("data/xauusd_m1_2026.parquet")], ignore_index=True)
M["ts"] = pd.to_datetime(M["ts"]); M = M.sort_values("ts").drop_duplicates("ts")
M = M.reset_index(drop=True)

def prepara(M):
    H = M.set_index("ts").resample("60min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    H = H[H.n >= 10]
    Mx = M.copy(); Mx["hb"] = Mx.ts.dt.floor("60min")
    g = Mx.groupby("hb")
    IDX = pd.DataFrame(dict(i0=g.apply(lambda x: x.index[0], include_groups=False),
                            i1=g.apply(lambda x: x.index[-1], include_groups=False))
                       ).reindex(H.index)
    return H, IDX

def gann(H, per):
    sh = H.h.rolling(per).mean().to_numpy(); sl = H.l.rolling(per).mean().to_numpy()
    c = H.c.to_numpy(); est = np.zeros(len(H)); cur = 0
    for i in range(len(H)):
        if not np.isnan(sh[i]):
            if   c[i] > sh[i]: cur = +1
            elif c[i] < sl[i]: cur = -1
        est[i] = cur
    return est

def corre(M, H, IDX, GANN=5, NBAR=51, ATRN=95, NSAL=5, VALIDEZ=10,
          filtro=True, azar=False, prob=None):
    tr = pd.concat([H.h-H.l, (H.h-H.c.shift()).abs(), (H.l-H.c.shift()).abs()],
                   axis=1).max(axis=1)
    at = tr.rolling(ATRN).mean().to_numpy()
    mx = H.h.rolling(NBAR).max().to_numpy()
    gn = gann(H, GANN) if filtro else np.ones(len(H))
    hm = (H.index.hour*60 + H.index.minute).to_numpy()
    i0, i1 = IDX.i0.to_numpy(), IDX.i1.to_numpy()
    mh, ml, mo, mt = (M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy(),
                      M.ts.to_numpy())
    n = len(H); cap = CAP0; ops = []
    k = max(NBAR, ATRN) + 2
    while k < n - NSAL - 1:
        if np.isnan(at[k]) or np.isnan(mx[k]) or not (H_INI <= hm[k] <= H_FIN):
            k += 1; continue
        if azar:
            if rng.random() > prob: k += 1; continue
        elif gn[k] != +1:
            k += 1; continue
        niv = mx[k] if not azar else None
        ent = None
        for j in range(k+1, min(k+1+VALIDEZ, n)):
            if np.isnan(i0[j]): continue
            a, b = int(i0[j]), int(i1[j])
            if azar:                      # entrada a mercado en la barra k+1
                ent = (j, a, mo[a] + SPREAD); break
            t = np.flatnonzero(mh[a:b+1] >= niv)
            if len(t):
                m = a + int(t[0]); ent = (j, m, max(niv, mo[m]) + SPREAD); break
        if ent is None: k += 1; continue
        jent, ment, px = ent
        atr = at[k]; stop = px - atr; lot = RIESGO*cap/(atr*ONZAS)
        jsal = jent + NSAL
        if jsal >= n or np.isnan(i0[jsal]): break
        msal = int(i0[jsal])
        st = np.flatnonzero(ml[ment:msal+1] <= stop)
        if len(st): mfin = ment+int(st[0]); sale = stop-SPREAD; mot="stop"
        else:       mfin = msal;            sale = mo[msal]-SPREAD; mot="tiempo"
        noc = len(pd.date_range(pd.Timestamp(mt[ment]).ceil("D"),
                                pd.Timestamp(mt[mfin]), freq="D"))
        bru = (sale-px)*ONZAS*lot; cos = COM_LOTE*lot + SWAP*lot*noc
        cap += bru-cos
        ops.append((bru-cos, mot, cap))
        k = max(k+1, jsal)
    if not ops: return None
    v = np.array([o[0] for o in ops])
    eq = CAP0 + np.cumsum(v)
    return dict(n=len(v), neto=float(v.sum()), cap=cap,
                ret=cap/CAP0-1, acierto=float((v>0).mean()),
                pf=float(v[v>0].sum()/abs(v[v<=0].sum())) if (v<=0).any() else np.inf,
                dd=float((eq/np.maximum.accumulate(eq)-1).min()),
                t=float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))))

H, IDX = prepara(M)
BASE = corre(M, H, IDX)
print(f"=== BASE (la estrategia tal cual) ===")
print(f"  n {BASE['n']}  neto {BASE['neto']:+,.0f} $  ret {BASE['ret']*100:+.1f} %  "
      f"acierto {BASE['acierto']*100:.1f} %  PF {BASE['pf']:.3f}  "
      f"DD {BASE['dd']*100:.1f} %  t {BASE['t']:+.2f}")

print(f"\n=== CONTROL 1 · LARGOS AL AZAR, misma geometria ===")
prob = BASE['n']/len(H)*3
res = []
for r in range(8):
    R = corre(M, H, IDX, azar=True, prob=prob)
    if R: res.append(R); print(f"  azar {r+1}: n {R['n']:4d}  neto {R['neto']:+9,.0f} $  "
        f"ret {R['ret']*100:+7.1f} %  acierto {R['acierto']*100:4.1f} %  "
        f"PF {R['pf']:.3f}  t {R['t']:+.2f}", flush=True)
a = np.array([r['ret'] for r in res])
print(f"\n  azar: retorno medio {a.mean()*100:+.1f} %  rango {a.min()*100:+.1f} a "
      f"{a.max()*100:+.1f} %")
print(f"  BASE {BASE['ret']*100:+.1f} %   ->   ¿bate a los 8 azares? "
      f"{'SI' if BASE['ret'] > a.max() else 'NO'}")

print(f"\n=== CONTROL 2 · VECINDARIO DE PARAMETROS ===")
print("   si la ventaja es real, los vecinos tambien ganan. Si solo gana la")
print("   combinacion exacta, es sobreajuste de la busqueda de StrategyQuant.\n")
print(f"  {'que cambia':28s} {'n':>5} {'neto':>10} {'ret':>8} {'PF':>6} {'t':>6}")
print(f"  {'BASE 5/51/95/5/10':28s} {BASE['n']:>5} {BASE['neto']:>+10,.0f} "
      f"{BASE['ret']*100:>7.1f}% {BASE['pf']:>6.3f} {BASE['t']:>+6.2f}")
vec = []
for nom, kw in [
    ("GannHiLo 3",  dict(GANN=3)),  ("GannHiLo 4",  dict(GANN=4)),
    ("GannHiLo 8",  dict(GANN=8)),  ("GannHiLo 13", dict(GANN=13)),
    ("maximo 30 velas", dict(NBAR=30)), ("maximo 40 velas", dict(NBAR=40)),
    ("maximo 65 velas", dict(NBAR=65)), ("maximo 80 velas", dict(NBAR=80)),
    ("ATR 60",  dict(ATRN=60)),  ("ATR 75",  dict(ATRN=75)),
    ("ATR 120", dict(ATRN=120)), ("ATR 150", dict(ATRN=150)),
    ("salida 3 barras", dict(NSAL=3)), ("salida 4 barras", dict(NSAL=4)),
    ("salida 7 barras", dict(NSAL=7)), ("salida 10 barras", dict(NSAL=10)),
    ("validez 5",  dict(VALIDEZ=5)),  ("validez 20", dict(VALIDEZ=20)),
    ("SIN filtro GannHiLo", dict(filtro=False)),
]:
    R = corre(M, H, IDX, **kw)
    if not R: continue
    vec.append((nom, R))
    print(f"  {nom:28s} {R['n']:>5} {R['neto']:>+10,.0f} {R['ret']*100:>7.1f}% "
          f"{R['pf']:>6.3f} {R['t']:>+6.2f}", flush=True)
v = np.array([r['ret'] for _, r in vec])
print(f"\n  vecinos positivos: {int((v>0).sum())}/{len(v)}   ·   "
      f"retorno medio {v.mean()*100:+.1f} %   ·   mediana {np.median(v)*100:+.1f} %")
print(f"  BASE {BASE['ret']*100:+.1f} %  ->  percentil {float((v<BASE['ret']).mean())*100:.0f} % "
      f"del vecindario")

print(f"\n=== CONTROL 3 · NULO · el oro con los bloques permutados ===")
def baraja(M, bloq=1440):
    lr = np.diff(np.log(M.close.to_numpy()))
    amp = ((M.high-M.low)/M.close).to_numpy()[1:]
    nb = len(lr)//bloq
    o = rng.permutation(nb)
    idx = (o[:,None]*bloq + np.arange(bloq)[None,:]).ravel()
    px = M.close.iloc[0]*np.exp(np.cumsum(lr[idx])); m = len(px)
    op = np.r_[M.close.iloc[0], px[:-1]]; a = amp[idx]*px
    return pd.DataFrame(dict(ts=M.ts.to_numpy()[:m], open=op,
        high=np.maximum(op,px)+a*rng.random(m)*0.5,
        low=np.minimum(op,px)-a*rng.random(m)*0.5, close=px))
nn = []
for r in range(4):
    Mb = baraja(M); Hb, Ib = prepara(Mb)
    R = corre(Mb, Hb, Ib)
    if R: nn.append(R['ret']); print(f"  nulo {r+1}: n {R['n']:4d}  "
        f"neto {R['neto']:+9,.0f} $  ret {R['ret']*100:+7.1f} %  "
        f"PF {R['pf']:.3f}  t {R['t']:+.2f}", flush=True)
nn = np.array(nn)
print(f"\n  nulos: retorno medio {nn.mean()*100:+.1f} %  rango {nn.min()*100:+.1f} a "
      f"{nn.max()*100:+.1f} %")
print(f"  BASE {BASE['ret']*100:+.1f} %  ->  ¿bate a todos los nulos? "
      f"{'SI' if BASE['ret'] > nn.max() else 'NO'}")

print(f"\n=== CONTROL 4 · ¿BATE A COMPRAR ORO Y ESPERAR? ===")
print("   el oro paso de 1.850 a 3.300 en este periodo. Es la vara de medir.\n")
p0, p1 = M.close.iloc[0], M.close.iloc[-1]
anios = (M.ts.iloc[-1]-M.ts.iloc[0]).days/365.25
byh = p1/p0 - 1
# drawdown de comprar y esperar, en velas H1
c = H.c.to_numpy(); ddb = float((c/np.maximum.accumulate(c) - 1).min())
print(f"  {'':26s} {'retorno':>9} {'CAGR':>8} {'DD max':>9} {'ret/DD':>8}")
print(f"  {'comprar y esperar':26s} {byh*100:>8.1f}% "
      f"{((1+byh)**(1/anios)-1)*100:>7.2f}% {ddb*100:>8.1f}% {abs(byh/ddb):>8.2f}")
print(f"  {'la estrategia':26s} {BASE['ret']*100:>8.1f}% "
      f"{((1+BASE['ret'])**(1/anios)-1)*100:>7.2f}% {BASE['dd']*100:>8.1f}% "
      f"{abs(BASE['ret']/BASE['dd']):>8.2f}")

# Sharpe de la estrategia sobre la serie de equity diaria
O = pd.read_csv("data/sqx_xauusd_operaciones.csv", parse_dates=["entrada","salida"])
s = O.set_index("salida").neto.resample("D").sum()
s = s[s.index >= O.entrada.min()]
eqd = CAP0 + s.cumsum()
rd = eqd.pct_change().dropna()
sh = float(rd.mean()/rd.std(ddof=1)*np.sqrt(252))
print(f"\n  Sharpe anualizado de la estrategia (equity diaria): {sh:+.2f}")
print(f"  t del retorno diario sobre {len(rd)} dias: "
      f"{float(rd.mean()/(rd.std(ddof=1)/np.sqrt(len(rd)))):+.2f}")
print(f"  anios necesarios para demostrar ese Sharpe (t=2): {(2/sh)**2:.1f}")
print(f"\n  P(pasar el reto de FundingPips) con ese Sharpe, si se mantuviera:")
rng2 = np.random.default_rng(3)
def fase(shp, vol, obj):
    mu = shp*vol/252; sd = vol/np.sqrt(252)
    x = rng2.normal(mu, sd, size=(40000,60)); eq = np.cumsum(x,1)
    fal = (eq <= -0.10) | (x <= -0.05); pas = (eq>=obj)&(np.arange(60)[None,:]>=2)
    ip = np.where(pas.any(1), pas.argmax(1), 99); iff = np.where(fal.any(1), fal.argmax(1), 99)
    return float((ip<iff).mean())
volan = float(rd.std(ddof=1)*np.sqrt(252))
a, b = fase(sh, volan, 0.08), fase(sh, volan, 0.05)
print(f"    volatilidad anual de la cuenta {volan*100:.1f} %  ->  "
      f"fase 1 {a*100:.1f} %  fase 2 {b*100:.1f} %  las dos {a*b*100:.1f} %")
print(f"    (la geometria sin ventaja da 36,9 %)")
