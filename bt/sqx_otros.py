"""Las MISMAS reglas de Strategy 4.3.23, en otros instrumentos y otro periodo.

Es la prueba fuera de muestra mas dura que permiten los datos: StrategyQuant
la optimizo sobre XAUUSD, probablemente en un tramo que solapa con 2023-2026.
Los indices cubren 2020-2026 y esa busqueda no los vio nunca.

Si la ventaja es la rotura de 51 velas mas la geometria de salida -y no un
ajuste al oro-, tiene que aparecer tambien aqui.

  python3 bt/sqx_otros.py
"""
import numpy as np, pandas as pd

CAP0, RIESGO = 100_000.0, 0.01
H_INI, H_FIN = 1*60+30, 23*60+30
rng = np.random.default_rng(20260905)

# ruta(s), valor de un punto por "lote" de referencia, spread en puntos,
# comision por lote ida y vuelta, swap por lote y noche
INSTR = {
 "XAUUSD": (["data/xauusd_m1.parquet","data/xauusd_m1_2026.parquet"], 100.0, 0.2, 6.0, 35.0),
 "US100":  (["data/nsxusd_m1.parquet"],  1.0, 1.5, 0.0, 3.0),
 "US500":  (["data/spxusd_m1.parquet"],  1.0, 0.6, 0.0, 1.5),
 "GER40":  (["data/grxeur_m1.parquet","data/grxeur_m1_2026.parquet"], 1.0, 1.2, 0.0, 2.0),
 "EURUSD": (["data/eurusd_m1.parquet"], 100000.0, 0.00007, 5.0, 3.0),
 "GBPUSD": (["data/gbpusd_m1.parquet"], 100000.0, 0.00008, 5.0, 3.0),
}

def prepara(rutas):
    M = pd.concat([pd.read_parquet(r) for r in rutas], ignore_index=True)
    M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    H = M.set_index("ts").resample("60min", label="left", closed="left").agg(
        o=("open","first"), h=("high","max"), l=("low","min"),
        c=("close","last"), n=("close","size")).dropna()
    H = H[H.n >= 10]
    Mx = M.copy(); Mx["hb"] = Mx.ts.dt.floor("60min"); g = Mx.groupby("hb")
    IDX = pd.DataFrame(dict(i0=g.apply(lambda x: x.index[0], include_groups=False),
                            i1=g.apply(lambda x: x.index[-1], include_groups=False))
                       ).reindex(H.index)
    return M, H, IDX

def corre(M, H, IDX, PV, SPR, COM, SWP, NBAR=51, ATRN=95, NSAL=5, VALIDEZ=10):
    """Sin filtro GannHiLo: el control 2 demostro que no aporta."""
    tr = pd.concat([H.h-H.l, (H.h-H.c.shift()).abs(), (H.l-H.c.shift()).abs()],
                   axis=1).max(axis=1)
    at = tr.rolling(ATRN).mean().to_numpy(); mx = H.h.rolling(NBAR).max().to_numpy()
    hm = (H.index.hour*60 + H.index.minute).to_numpy()
    i0, i1 = IDX.i0.to_numpy(), IDX.i1.to_numpy()
    mh, ml, mo, mt = (M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy(),
                      M.ts.to_numpy())
    n = len(H); cap = CAP0; v = []; fechas = []
    k = max(NBAR, ATRN) + 2
    while k < n - NSAL - 1:
        if np.isnan(at[k]) or np.isnan(mx[k]) or not (H_INI <= hm[k] <= H_FIN):
            k += 1; continue
        niv = mx[k]; ent = None
        for j in range(k+1, min(k+1+VALIDEZ, n)):
            if np.isnan(i0[j]): continue
            a, b = int(i0[j]), int(i1[j])
            t = np.flatnonzero(mh[a:b+1] >= niv)
            if len(t):
                m = a+int(t[0]); ent = (j, m, max(niv, mo[m]) + SPR); break
        if ent is None: k += 1; continue
        jent, ment, px = ent
        atr = at[k]; stop = px - atr; lot = RIESGO*cap/(atr*PV)
        jsal = jent + NSAL
        if jsal >= n or np.isnan(i0[jsal]): break
        msal = int(i0[jsal])
        st = np.flatnonzero(ml[ment:msal+1] <= stop)
        if len(st): mfin = ment+int(st[0]); sale = stop-SPR
        else:       mfin = msal;            sale = mo[msal]-SPR
        noc = len(pd.date_range(pd.Timestamp(mt[ment]).ceil("D"),
                                pd.Timestamp(mt[mfin]), freq="D"))
        neto = (sale-px)*PV*lot - COM*lot - SWP*lot*noc
        cap += neto; v.append(neto); fechas.append(pd.Timestamp(mt[ment]))
        k = max(k+1, jsal)
    if len(v) < 30: return None
    v = np.array(v); eq = CAP0 + np.cumsum(v)
    F = pd.Series(v, index=pd.DatetimeIndex(fechas))
    anios = (F.index[-1]-F.index[0]).days/365.25
    return dict(n=len(v), ret=cap/CAP0-1, cagr=(cap/CAP0)**(1/anios)-1,
                acierto=float((v>0).mean()), anios=anios,
                pf=float(v[v>0].sum()/abs(v[v<=0].sum())) if (v<=0).any() else np.inf,
                dd=float((eq/np.maximum.accumulate(eq)-1).min()),
                t=float(v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))), F=F)

print(f"  {'instr':8s} {'periodo':>21} {'n':>5} {'ret':>9} {'CAGR':>8} "
      f"{'acierto':>8} {'PF':>6} {'DD':>7} {'t':>6}")
R = {}
for k, (rutas, PV, SPR, COM, SWP) in INSTR.items():
    try:
        M, H, IDX = prepara(rutas)
        r = corre(M, H, IDX, PV, SPR, COM, SWP)
        if not r: print(f"  {k:8s} pocas operaciones"); continue
        R[k] = r
        print(f"  {k:8s} {str(r['F'].index[0].date()):>10}->{str(r['F'].index[-1].date()):<10} "
              f"{r['n']:>5} {r['ret']*100:>8.1f}% {r['cagr']*100:>7.2f}% "
              f"{r['acierto']*100:>7.1f}% {r['pf']:>6.3f} {r['dd']*100:>6.1f}% "
              f"{r['t']:>+6.2f}", flush=True)
    except Exception as e:
        print(f"  {k:8s} error: {type(e).__name__}: {e}")

idx = [k for k in ("US100","US500","GER40") if k in R]
if idx:
    print(f"\n  indices (fuera de la optimizacion del oro, 2020-2026):")
    print(f"    positivos {sum(R[k]['ret']>0 for k in idx)}/{len(idx)}   "
          f"·   CAGR medio {np.mean([R[k]['cagr'] for k in idx])*100:+.2f} %   "
          f"·   PF medio {np.mean([R[k]['pf'] for k in idx]):.3f}")
fx = [k for k in ("EURUSD","GBPUSD") if k in R]
if fx:
    print(f"  forex: positivos {sum(R[k]['ret']>0 for k in fx)}/{len(fx)}   "
          f"·   CAGR medio {np.mean([R[k]['cagr'] for k in fx])*100:+.2f} %")

print(f"\n=== ¿ES DEL INSTRUMENTO O DEL REGIMEN? ===")
print("   oro y GER40 solo cubren 2023-2026, que fue alcista puro. Los indices")
print("   americanos cubren 2020-2026, con el bajista de 2022 dentro.")
print("   Si el mismo tramo 2023-2026 tambien funciona en ellos, entonces la")
print("   ventaja no es del oro: es de 'rotura larga en mercado alcista'.\n")
print(f"  {'instr':8s} {'tramo':>12} {'n':>5} {'ret':>9} {'CAGR':>8} {'PF':>6} {'t':>6}")
for k in ("XAUUSD","US100","US500","GER40","EURUSD","GBPUSD"):
    if k not in R: continue
    F = R[k]["F"]
    for et, sub in (("2020-2022", F[F.index.year <= 2022]),
                    ("2023-2026", F[F.index.year >= 2023])):
        if len(sub) < 30: continue
        v = sub.to_numpy(); eq = CAP0 + np.cumsum(v)
        an = (sub.index[-1]-sub.index[0]).days/365.25
        pf = v[v>0].sum()/abs(v[v<=0].sum()) if (v<=0).any() else np.inf
        t  = v.mean()/(v.std(ddof=1)/np.sqrt(len(v)))
        ret = eq[-1]/CAP0 - 1
        print(f"  {k:8s} {et:>12} {len(v):>5} {ret*100:>8.1f}% "
              f"{((1+ret)**(1/an)-1)*100:>7.2f}% {pf:>6.3f} {t:>+6.2f}")
