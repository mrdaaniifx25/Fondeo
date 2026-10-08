"""P1-P4 del pre-registro sobre indices. Parametros CONGELADOS desde EURUSD.

P1  CRT+DOL en NAS100
P2  CRT+DOL en SP500
P3  H3a confluencia: NAS100 barre a la vez que SP500
P4  H1a divergencia: NAS100 barre y SP500 no   (control exacto de P3)
"""
import os, numpy as np, pandas as pd
import sys; sys.path.insert(0,"bt")
from prueba_indices import (prepara, senales, simula, pz, ANCLA_H4, TP_R,
                            SL_BUFFER, MAX_HORAS)

COSTE = {"NSX": 1.5, "SPX": 0.6}          # principal, declarado en el pre-registro
SENS  = [0.6, 1.0, 1.5, 2.0, 3.0, 4.0]

def carga(sym):
    m1 = pd.read_parquet(f"data/{sym.lower()}usd_m1.parquet")
    m1["ts"] = pd.to_datetime(m1["ts"])
    return m1

def canal(sym, m1, unit):
    f = f"data/ch_{sym.lower()}.parquet"
    if os.path.exists(f):
        ch = pd.read_parquet(f); ch["ts"]=pd.to_datetime(ch["ts"]); return ch
    ch = prepara(m1, unit)
    ch.to_parquet(f, index=False)
    return ch

def informe(tr, nom, unit, coste_principal, etiqueta_u="puntos"):
    if tr is None or tr.empty:
        print(f"\n{nom}: sin operaciones."); return None
    z,p = pz(tr.bruto)
    wr  = (tr.motivo=="TP").mean() if "motivo" in tr else np.nan
    print(f"\n=== {nom} ===")
    print(f"  {len(tr)} operaciones   |  riesgo medio {tr.riesgo_u.mean():.1f} {etiqueta_u}")
    if not np.isnan(wr):
        print(f"  win rate {wr*100:5.2f}%   (equilibrio a {TP_R:.0f}R: {100/(1+TP_R):.2f}%)")
    h = len(tr)//2
    print(f"  VENTAJA BRUTA {tr.bruto.mean():+.4f} R/op | z {z:+.2f} | p {p:.4f}")
    print(f"  mitades: 1a {tr.bruto.iloc[:h].mean():+.4f}  2a {tr.bruto.iloc[h:].mean():+.4f}")
    for c in SENS:
        R = (tr.bruto*tr.riesgo_u - c)/tr.riesgo_u
        g,pe = R[R>0].sum(), -R[R<=0].sum()
        pf = g/pe if pe>0 else float("inf")
        mark = "  <- principal" if abs(c-coste_principal)<1e-9 else ""
        print(f"  coste {c:>4.1f} -> {c/tr.riesgo_u.mean()*100:4.1f}% del riesgo | "
              f"R neto {R.sum():+8.2f} | PF {pf:.3f}{mark}")
    return dict(n=len(tr), bruto=float(tr.bruto.mean()), z=float(z), p=float(p),
                riesgo=float(tr.riesgo_u.mean()),
                h1=float(tr.bruto.iloc[:h].mean()), h2=float(tr.bruto.iloc[h:].mean()))

def rasgos_h4(m1, pref):
    """Extremos acumulados de la H4 en curso y extremos de la H4 anterior, por vela M15."""
    ch = m1.set_index("ts").resample("15min",label="left",closed="left").agg(
        high=("high","max"), low=("low","min")).dropna().reset_index()
    org = pd.Timestamp("2020-01-01")+pd.Timedelta(hours=ANCLA_H4)
    h4 = m1.set_index("ts").resample("4h",origin=org,label="left",closed="left").agg(
        high=("high","max"), low=("low","min")).dropna().reset_index()
    h4["p_hi"], h4["p_lo"] = h4.high.shift(1), h4.low.shift(1)
    ch["h4_id"] = (ch["ts"]-pd.Timedelta(hours=ANCLA_H4)).dt.floor("4h")+pd.Timedelta(hours=ANCLA_H4)
    ch = ch.merge(h4[["ts","p_hi","p_lo"]].rename(columns={"ts":"h4_id"}), on="h4_id", how="left")
    ch["run_hi"] = ch.groupby("h4_id")["high"].cummax()
    ch["run_lo"] = ch.groupby("h4_id")["low"].cummin()
    return ch[["ts","p_hi","p_lo","run_hi","run_lo"]].rename(
        columns={c:f"{pref}_{c}" for c in ("p_hi","p_lo","run_hi","run_lo")})

if __name__ == "__main__":
    res = {}
    print("cargando...")
    nsx = carga("NSX"); spx = carga("SPX")
    print(f"  NSXUSD {len(nsx):,} velas | SPXUSD {len(spx):,} velas")

    # ── P1 y P2 ────────────────────────────────────────────────────────────
    for sym, m1 in (("NSX", nsx), ("SPX", spx)):
        ch = canal(sym, m1, 1.0)
        sig, emb = senales(ch, 1.0)
        print(f"\n[{sym}] embudo: turtle H4+H1 {emb['ts_h4h1']} -> con OB {emb['con_ob']} "
              f"-> DOL ok {emb['dol_ok']} -> senales {emb['senales']}")
        tr = simula(sig, m1, 1.0, COSTE[sym])
        tr.to_csv(f"data/trades_{sym.lower()}.csv", index=False)
        nom = "P1 · CRT+DOL congelado en NAS100" if sym=="NSX" else "P2 · CRT+DOL congelado en SP500"
        res[sym] = informe(tr, nom, 1.0, COSTE[sym])
        res[f"{sym}_sig"] = sig

    # ── P3 y P4: confluencia y divergencia de barrido ──────────────────────
    print("\nconstruyendo rasgos de barrido de SP500 para cruzarlos con NAS100...")
    fe = rasgos_h4(spx, "s")
    s = res["NSX_sig"].merge(fe, on="ts", how="left")
    con_datos = s.s_p_hi.notna().sum()
    print(f"  setups de NAS100: {len(s)}  |  con rasgos de SP500: {con_datos}")
    s = s[s.s_p_hi.notna()].copy()
    L = s.largo.to_numpy()
    barrio_spx = np.where(L, s.s_run_lo < s.s_p_lo, s.s_run_hi > s.s_p_hi)

    for nom, mask, etq in (
        ("P3 · H3a confluencia: SP500 tambien barre", barrio_spx,  "conf"),
        ("P4 · H1a divergencia: SP500 no barre",     ~barrio_spx,  "div")):
        sub = s[mask]
        tr = simula(sub.drop(columns=[c for c in sub.columns if c.startswith("s_")]),
                    nsx, 1.0, COSTE["NSX"])
        tr.to_csv(f"data/trades_nsx_{etq}.csv", index=False)
        res[etq] = informe(tr, nom, 1.0, COSTE["NSX"])

    # ── comparacion P3 vs P4 ───────────────────────────────────────────────
    from math import sqrt, erf
    a = pd.read_csv("data/trades_nsx_conf.csv").bruto
    b = pd.read_csv("data/trades_nsx_div.csv").bruto
    dif = a.mean()-b.mean()
    se  = sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    z   = dif/se; p = 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
    print("\n=== P3 frente a P4 (una sola estadistica) ===")
    print(f"  confluencia {a.mean():+.4f} (n={len(a)})  |  divergencia {b.mean():+.4f} (n={len(b)})")
    print(f"  diferencia {dif:+.4f} R/op | z {z:+.2f} | p {p:.4f}")
    print(f"  signo esperado (EURUSD: confluencia mejor): "
          f"{'SE REPLICA' if dif>0 else 'NO se replica'}")
    print(f"  p<0.05 {'si' if p<0.05 else 'no'} | Bonferroni p<0.0125 {'si' if p<0.0125 else 'no'}")

    import json
    json.dump({k:v for k,v in res.items() if not k.endswith("_sig")},
              open("data/informe_indices.json","w"), indent=1)
