"""CONFIRMACION de la candidata de docs/CANDIDATA_cero.md. Se abre UNA vez.

No hay ningun parametro que ajustar aqui. Todo viene de data/umbrales_cero.txt.
Lo unico que se recalcula por par es el percentil 80 del ATR, y se recalcula
sobre 2020-2023 de ESE par, que es periodo de entrenamiento en los dos casos.
"""
import sys; sys.path.insert(0, "bt")
import json
import numpy as np, pandas as pd
import variables as V, cero

COSTE = {"eurusd": 1.20, "gbpusd": 1.50, "usdjpy": 1.30}
UNID  = {"eurusd": 0.0001, "gbpusd": 0.0001, "usdjpy": 0.01}
umb = cero.lee_umbrales()
VEN, HOR = int(umb["VENTANA_RANGO"]), int(umb["HORIZONTE"])

def prepara(par):
    m1 = pd.read_parquet(f"data/{par}_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
    d = V.m15(m1); X = V.construye(d)
    u = UNID[par]
    return d, (V.atr(d, 48)/u).to_numpy(), cero.senal(X, VEN).to_numpy(), u

def opera(d, atr, s, u, coste, amin, ini=None, fin=None):
    r = ((d.close.shift(-HOR) - d.close)/u).to_numpy()
    vol = atr >= amin
    lado = np.where(vol & (s >= umb["SENAL_ALTA"]), 1,
            np.where(vol & (s <= umb["SENAL_BAJA"]), -1, 0))
    m = (lado != 0) & np.isfinite(r) & np.isfinite(s)
    if ini is not None: m &= (d.ts >= ini).to_numpy()
    if fin is not None: m &= (d.ts < fin).to_numpy()
    b = lado[m]*r[m]
    return pd.DataFrame({"ts": d.ts[m].to_numpy(), "lado": lado[m],
                         "bruto": b, "neto": b - coste})

def linea(etq, t, anos):
    if len(t) < 2:
        print(f"{etq:34s} n={len(t):>5}   (sin datos suficientes)"); return None
    x = t.neto.to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x))
    print(f"{etq:34s} n={len(t):>5,} ({len(t)/anos:>4.0f}/año)  bruto {t.bruto.mean():+6.3f}"
          f"   NETA {x.mean():+6.3f}  IC95 [{x.mean()-1.96*ee:+6.3f}, {x.mean()+1.96*ee:+6.3f}]"
          f"  aciertos {100*(t.bruto>0).mean():4.1f}%")
    return dict(n=len(t), por_ano=len(t)/anos, bruto=float(t.bruto.mean()),
                neto=float(x.mean()), ic=[float(x.mean()-1.96*ee), float(x.mean()+1.96*ee)],
                aciertos=float((t.bruto>0).mean()))

out = {}
print("="*104)
print("CONFIRMACION · candidata de reversion de una hora en volatilidad alta")
print("="*104)

# ── 1 · EURUSD 2024-2026, numeros congelados tal cual ──────────────────────
d, atr, s, u = prepara("eurusd")
print("\n1 · EURUSD  ·  el mismo par, periodo nunca usado  ·  ATR(48) >= 9,4708 pips fijo\n")
t_tr = opera(d, atr, s, u, COSTE["eurusd"], umb["ATR48_MIN"], fin="2024-01-01")
out["eurusd_train"] = linea("2020-2023 (descubrimiento)", t_tr, 4.0)
t = opera(d, atr, s, u, COSTE["eurusd"], umb["ATR48_MIN"], ini="2024-01-01")
anos = (d.ts.max() - pd.Timestamp("2024-01-01")).days/365.25
out["eurusd_test"] = linea("2024-2026 (CONFIRMACION)", t, anos)
print()
for a, g in t.groupby(pd.DatetimeIndex(t.ts).year):
    linea(f"    solo {a}", g, 1.0)
print()
for lado, nom in ((1, "compras"), (-1, "ventas")):
    linea(f"    2024-2026, {nom}", t[t.lado == lado], anos)
t.to_csv("data/trades_cero_eurusd.csv", index=False)

# ── 2 · GBPUSD y USDJPY, 2020-2026 ─────────────────────────────────────────
print("\n2 · Otros pares  ·  2020-2026 entero  ·  percentil 80 de su propio ATR en 2020-2023\n")
for par in ("gbpusd", "usdjpy"):
    d2, atr2, s2, u2 = prepara(par)
    tr = (d2.ts < "2024-01-01").to_numpy() & np.isfinite(s2)
    p80 = float(np.quantile(atr2[tr], .80))
    t2 = opera(d2, atr2, s2, u2, COSTE[par], p80)
    an = (d2.ts.max() - d2.ts.min()).days/365.25
    print(f"  {par.upper()}  p80 del ATR = {p80:.4f} pips   coste {COSTE[par]:.2f}")
    out[par] = linea(f"    2020-2026", t2, an)
    out[par+"_lit"] = linea(f"    idem con 9,4708 literal", 
                            opera(d2, atr2, s2, u2, COSTE[par], umb["ATR48_MIN"]), an)
    print()

# ── veredicto ──────────────────────────────────────────────────────────────
e = out["eurusd_test"]
c1 = e["neto"] > 0
c2 = e["neto"] >= 0.70
c3 = (out["gbpusd"] or {}).get("neto", -9) > 0 or (out["usdjpy"] or {}).get("neto", -9) > 0
print("="*104)
print("CRITERIOS DECLARADOS ANTES DE MIRAR")
print(f"  1. signo se mantiene en EURUSD 2024-2026        {'CUMPLE' if c1 else 'FALLA':>8s}"
      f"   (neta {e['neto']:+.3f})")
print(f"  2. neta >= +0,70 pips (mitad de +1,41)          {'CUMPLE' if c2 else 'FALLA':>8s}")
print(f"  3. signo se mantiene en GBPUSD o USDJPY         {'CUMPLE' if c3 else 'FALLA':>8s}")
print(f"\n  VEREDICTO: {'CONFIRMADA' if (c1 and c2 and c3) else 'DESCARTADA'}")
print("="*104)
out["veredicto"] = dict(c1=bool(c1), c2=bool(c2), c3=bool(c3),
                        confirmada=bool(c1 and c2 and c3))
json.dump(out, open("data/informe_cero.json", "w"), indent=1)
