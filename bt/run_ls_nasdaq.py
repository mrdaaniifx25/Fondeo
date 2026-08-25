"""Estrategia de las 4 confirmaciones (video de liquidez) sobre el NASDAQ.

Es el mismo motor que se uso en EURUSD, con la unidad y el marco de disparo
del indice: el autor dice literalmente "en indices utilizo la temporalidad de
M3". Se prueba tal cual, y luego se le pasan los controles.
"""
import sys; sys.path.insert(0, "bt")
import json
import numpy as np, pandas as pd
import estrategia_ls as E

PT = 1.0            # un punto del NASDAQ
COSTE = 1.5         # spread + deslizamiento, ida y vuelta, en puntos

m1 = pd.read_parquet("data/nsxusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").reset_index(drop=True)
anos = (m1.ts.max() - m1.ts.min()).days / 365.25
print(f"NSXUSD  {len(m1):,} velas M1   {m1.ts.min()} -> {m1.ts.max()}   {anos:.1f} años\n")

def cfg(**kw):
    base = dict(unidad=PT, marco_disparo="3min", clave="nsx", coste_pips=COSTE,
                sl_buffer_pips=1.0, rr=1.0, solo_kz=False,
                kz_londres=None, kz_ny=None)
    base.update(kw)
    return E.Config(**base)

def corre(c, etiqueta, mostrar_embudo=False):
    m5, emb = E.construir_senales(m1, c)
    tr, amb = E.simular(m5, m1, c)
    if mostrar_embudo:
        print("  embudo de las 4 confirmaciones")
        prev = None
        for k, v in emb.items():
            pct = f"{v/prev*100:6.1f} %" if prev and k != "C4 envolvente M5" else ""
            print(f"     {k:26s} {v:>9,} {pct}")
            if k.startswith("C2/C3 LS en H1+H4"): prev = v
            elif prev is None: prev = v
        print()
    if tr.empty:
        print(f"{etiqueta:38s}  sin operaciones"); return tr, None
    mt = E.metricas(tr)
    R = tr.R.to_numpy()
    ee = R.std(ddof=1)/np.sqrt(len(R))
    bruto = tr.pips.to_numpy() + c.coste_pips
    wr_bruto = 100*(bruto > 0).mean()
    print(f"{etiqueta:38s}  n={len(tr):>5,} ({len(tr)/anos:>5.0f}/año)  "
          f"acierto {mt['win rate %']:5.2f}%  R/op {R.mean():+7.4f} "
          f"IC95 [{R.mean()-1.96*ee:+.4f},{R.mean()+1.96*ee:+.4f}]  "
          f"PF {mt['profit factor']:.3f}  riesgo mediano {mt['riesgo mediano (pips)']:.1f} pts")
    return tr, dict(n=len(tr), wr=mt["win rate %"], wr_bruto=wr_bruto,
                    R=float(R.mean()), ic=[float(R.mean()-1.96*ee), float(R.mean()+1.96*ee)],
                    pf=mt["profit factor"], riesgo=mt["riesgo mediano (pips)"],
                    Rtot=float(R.sum()), dd=mt["max drawdown %"])

out = {}
print("="*118)
print("1 · LA ESTRATEGIA TAL CUAL LA EXPLICA EL VIDEO  ·  NASDAQ  ·  disparo en M3  ·  coste 1,5 puntos")
print("="*118)
t_base, out["dia_entero"] = corre(cfg(), "día entero (como su backtest)", mostrar_embudo=True)
t_kz, out["aperturas"] = corre(cfg(solo_kz=True, kz_londres=(8,11), kz_ny=(9,12)),
                               "solo aperturas Londres y NY")
_, out["m5"] = corre(cfg(marco_disparo="5min"), "idem, disparo en M5 en vez de M3")

print("\n" + "="*118)
print("2 · LA PREGUNTA QUE MANDA: ¿cuánto cuesta operar frente a lo que se arriesga?")
print("="*118)
if not t_base.empty:
    r = t_base.riesgo_pips
    print(f"   riesgo por operación: mediana {r.median():.1f} pts, media {r.mean():.1f} pts, "
          f"p10 {r.quantile(.1):.1f}, p90 {r.quantile(.9):.1f}")
    print(f"   coste 1,5 puntos = {100*1.5/r.median():.1f} % del riesgo (mediana)")
    print(f"   a 1:1, para salir en tablas hace falta acertar "
          f"{50*(1+1.5/r.median()):.2f} % de las veces")
    b = t_base.pips.to_numpy() + COSTE
    print(f"   acierto BRUTO observado: {100*(b>0).mean():.2f} %")

print("\n" + "="*118)
print("3 · CONTROLES")
print("="*118)
if not t_base.empty:
    R = t_base.R.to_numpy(); n = len(R)
    inv = -t_base.pips.to_numpy() - 2*COSTE      # al revés, pagando coste igual
    print(f"   dirección invertida (mismo momento, mismo stop)   R/op "
          f"{(inv/t_base.riesgo_pips.to_numpy()).mean():+.4f}")
    rng = np.random.default_rng(7)
    print(f"   sin coste ninguno                                 R/op "
          f"{((t_base.pips.to_numpy()+COSTE)/t_base.riesgo_pips.to_numpy()).mean():+.4f}")
    bs = np.array([rng.choice(R, n, replace=True).mean() for _ in range(4000)])
    print(f"   bootstrap 4.000 remuestreos: IC95 de R/op [{np.quantile(bs,.025):+.4f}, "
          f"{np.quantile(bs,.975):+.4f}]   P(R/op>0) = {100*(bs>0).mean():.1f} %")

print("\n" + "="*118)
print("4 · SENSIBILIDAD AL COSTE  (día entero, disparo M3)")
print("="*118)
if not t_base.empty:
    bruto = t_base.pips.to_numpy() + COSTE
    rp = t_base.riesgo_pips.to_numpy()
    fila = []
    for cst in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0):
        Rm = ((bruto - cst)/rp).mean()
        fila.append((cst, Rm))
    print("   coste (pts) " + "".join(f"{c:>9.1f}" for c, _ in fila))
    print("   R por op    " + "".join(f"{r:>+9.4f}" for _, r in fila))
    out["sensib"] = [(c, float(r)) for c, r in fila]

print("\n" + "="*118)
print("5 · AÑO A AÑO  (día entero, disparo M3, coste 1,5)")
print("="*118)
if not t_base.empty:
    for a, g in t_base.groupby(pd.DatetimeIndex(t_base.ts).year):
        print(f"   {a}   n={len(g):>4}  acierto {100*(g.R>0).mean():5.1f}%  "
              f"R total {g.R.sum():+8.2f}  R/op {g.R.mean():+.4f}")
    t_base.to_csv("data/trades_ls_nsx.csv", index=False)
json.dump(out, open("data/informe_ls_nsx.json", "w"), indent=1)
