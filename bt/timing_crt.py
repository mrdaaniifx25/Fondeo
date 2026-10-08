"""Pre-registro docs/PREREGISTRO_timing_crt.md

El TIMING del CRT con la direccion dada por buena. La direccion se fija por
construccion, asi que cualquier diferencia entre reglas de entrada es timing.

Cuatro reglas: ciego / CRT alineado / espera al azar (CONTROL) / espera fija.
El contraste es el acierto MENOS su propio nulo geometrico, porque las reglas
cambian el R:R y el acierto sube solo cuando el R:R baja.

  python3 bt/timing_crt.py
"""
import numpy as np, pandas as pd
from math import sqrt
rng = np.random.default_rng(20261008)

INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 0.70),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 12.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  0.8)]   # costes ECN
HOR = 3 * 1440


def prepara(ruta):
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    t = (M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York")
          .dt.tz_localize(None))
    M["k4"] = t.dt.floor("240min")
    g = M.groupby("k4", sort=True)
    b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"))
    b = b[b.index.notna()]
    b["fin"] = g.apply(lambda d: d.index[-1], include_groups=False).reindex(b.index)
    return M, b


def resuelve(M, e, lado, rgo, rec):
    HH, LL = M.high.to_numpy(), M.low.to_numpy()
    a, z2 = e, min(e + HOR, len(M))
    hh, ll = HH[a:z2], LL[a:z2]
    ent = M.open.to_numpy()[e]
    if lado > 0:
        ks = np.nonzero(ll <= ent - rgo)[0]; kt = np.nonzero(hh >= ent + rec)[0]
    else:
        ks = np.nonzero(hh >= ent + rgo)[0]; kt = np.nonzero(ll <= ent - rec)[0]
    fs = ks[0] if len(ks) else 10**9
    ft = kt[0] if len(kt) else 10**9
    return (rec/rgo) if ft < fs else (-1.0 if fs < 10**9 else 0.0)


def corre(nom, ruta, U, coste):
    M, b = prepara(ruta)
    O, H, L, C = (b[k].to_numpy() for k in "ohlc")
    fin = b.fin.to_numpy().astype(int)
    ph, pl = np.r_[np.nan, H[:-1]], np.r_[np.nan, L[:-1]]
    # rango H4 ALINEADO con un sesgo: para largos, la vela en curso barrio el
    # minimo de la anterior (y no el maximo). Se lee al CIERRE de esa vela.
    bl, bh = L <= pl, H >= ph
    alin_l = bl & ~bh          # rango alcista activado
    alin_s = bh & ~bl          # rango bajista activado
    # sesgo oraculo: direccion real de la semana (mira al futuro A PROPOSITO)
    sem = pd.Series(b.index).dt.to_period("W").to_numpy()
    cs = pd.Series(C, index=sem).groupby(level=0)
    dirsem = pd.Series(np.sign(cs.last() - cs.first()))
    oraculo = pd.Series(sem).map(dirsem).to_numpy()

    filas = []
    for i in range(2, len(b) - 1):
        e = fin[i] + 1
        if e >= len(M): continue
        for et_s, lado in (("largo", 1), ("oraculo", int(oraculo[i]) if np.isfinite(oraculo[i]) else 0)):
            if lado == 0: continue
            # stop tras la mecha del barrido de la vela que acaba de cerrar
            mecha = L[i] if lado > 0 else H[i]
            ent = M.open.to_numpy()[e]
            rgo = (ent - mecha) * lado
            if rgo <= 0: continue
            obj = ph[i] if lado > 0 else pl[i]          # extremo opuesto del rango H4
            rec = (obj - ent) * lado
            if rec <= 0 or not np.isfinite(rec): continue
            al = bool(alin_l[i]) if lado > 0 else bool(alin_s[i])
            filas.append((nom, et_s, b.index[i], lado, e, rgo/U, rec/U, al))
    D = pd.DataFrame(filas, columns="ins sesgo ts lado e rgo rec alin".split())
    D["R"] = [resuelve(M, int(r.e), r.lado, r.rgo*U, r.rec*U) for _, r in D.iterrows()]
    D["cr"] = coste / D.rgo
    D["geo"] = D.rgo / (D.rgo + D.rec)
    D["dia"] = pd.to_datetime(D.ts).dt.floor("D")
    return D


T = pd.concat([corre(*a) for a in INS], ignore_index=True)
T["gr"] = T.ins + T.dia.astype(str)
print(f"velas H4 evaluadas: {len(T[T.sesgo=='largo']):,} (largo) y "
      f"{len(T[T.sesgo=='oraculo']):,} (oraculo)")
dias = T.dia.nunique()
print(f"dias de calendario con dato: {dias:,}\n")


def z(x, gr):
    m = x.mean()
    su = pd.DataFrame({"x": x.to_numpy(), "g": gr.to_numpy()}).groupby("g").x.apply(
        lambda v: (v - m).sum())
    s2 = float((su**2).sum())
    return m*len(x)/sqrt(s2) if s2 > 0 else float("nan")


def ficha(et, D, nd):
    if len(D) < 30: return print(f"  {et:<26} (pocas: {len(D)})")
    ac, ge = (D.R > 0).mean(), D.geo.mean()
    exc = 100*(ac - ge)
    rr = (D.rec/D.rgo).mean()
    neta = D.R - D.cr
    print(f"  {et:<26}{len(D):>7}{rr:>7.2f}{100*ac:>8.1f}%{100*ge:>8.1f}%"
          f"{exc:>+8.1f}{z(D.R - D.geo*0, D.gr):>+7.2f}{D.R.mean():>+9.4f}"
          f"{neta.mean():>+9.4f}{neta.sum()/nd:>+9.4f}")


CAB = (f"  {'regla':<26}{'n':>7}{'R:R':>7}{'acierto':>9}{'geom':>9}{'exceso':>8}"
       f"{'z bruta':>7}{'R bruta':>9}{'R neta':>9}{'neta/dia':>9}")

for sesgo in ("largo", "oraculo"):
    S = T[T.sesgo == sesgo]
    print("="*104)
    print(f"SESGO = {sesgo.upper()}" + ("  ·  direccion real de la semana, mirando al futuro a proposito"
          if sesgo == "oraculo" else "  ·  comprar siempre"))
    print("="*104); print(CAB)
    ciego = S
    crt = S[S.alin]
    n = len(crt)
    ficha("1 ciego (cada vela H4)", ciego, dias)
    ficha("2 CRT alineado", crt, dias)
    # 3 espera al azar, MISMO numero de operaciones
    exc3, ac3 = [], []
    for _ in range(60):
        m = S.sample(n=min(n, len(S)), random_state=int(rng.integers(1e9)))
        exc3.append(100*((m.R > 0).mean() - m.geo.mean())); ac3.append((m.R > 0).mean())
    azar = S.sample(n=min(n, len(S)), random_state=7)
    ficha("3 espera al azar (CONTROL)", azar, dias)
    print(f"  {'':<26}{'':>7}{'':>7}{'  (media de 60 sorteos: acierto '+f'{100*np.mean(ac3):.1f}%'+'  exceso '+f'{np.mean(exc3):+.1f}'+' pp)':<40}")
    # 4 espera fija: 2 velas H4 despues de una alineada
    idx = S.index.to_numpy()
    pos = {v: k for k, v in enumerate(idx)}
    fij = S[pd.Series(S.alin.to_numpy()).shift(2).fillna(False).to_numpy()]
    ficha("4 espera fija (2 velas H4)", fij, dias)
    print(f"\n  CONTRASTE PRINCIPAL  ·  exceso de la regla 2 sobre su nulo: "
          f"{100*((crt.R>0).mean()-crt.geo.mean()):+.1f} pp")
    print(f"  CONTRASTE DECISIVO   ·  regla 2 menos regla 3 (azar): "
          f"{100*((crt.R>0).mean()-crt.geo.mean()) - np.mean(exc3):+.1f} pp\n")

print("="*104); print("POR INSTRUMENTO  ·  sesgo oraculo"); print("="*104); print(CAB)
for nom, _, _, _ in INS:
    S = T[(T.sesgo == "oraculo") & (T.ins == nom)]
    nd = S.dia.nunique()
    ficha(f"{nom} ciego", S, nd)
    ficha(f"{nom} CRT alineado", S[S.alin], nd)
