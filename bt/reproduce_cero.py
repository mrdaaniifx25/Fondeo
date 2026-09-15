"""Comprueba que bt/cero.py reproduce el descubrimiento 2020-2023 de EURUSD.

Si no lo reproduce, la especificacion escrita no es la que se congelo y hay que
arreglar el documento ANTES de mirar nada nuevo.
"""
import sys; sys.path.insert(0, "bt")
import numpy as np, pandas as pd
import variables as V, cero

U = 0.0001
umb = cero.lee_umbrales()
print("umbrales congelados:", umb)

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
d = V.m15(m1)
X = V.construye(d)
atr = V.atr(d, 48) / U
s = cero.senal(X, int(umb["VENTANA_RANGO"]))

tr = d.ts < "2024-01-01"
print(f"\nvelas M15 totales {len(d):,} | entrenamiento {int(tr.sum()):,}")

# donde caen los umbrales dentro del periodo de descubrimiento
for etq, m in (("todo el entrenamiento", tr),
               ("entrenamiento con ATR>=umbral", tr & (atr >= umb["ATR48_MIN"]))):
    v = s[m].dropna()
    print(f"{etq:32s} n={len(v):>7,} q02={v.quantile(.02):+.6f} q98={v.quantile(.98):+.6f}")
p80 = atr[tr].quantile(.80)
print(f"p80 del ATR(48) en entrenamiento: {p80:.4f}  (congelado {umb['ATR48_MIN']:.4f})")

# las dos orientaciones posibles de la regla
n = int(umb["HORIZONTE"])
fut = d.close.shift(-n)
r = (fut - d.close) / U
vol = atr >= umb["ATR48_MIN"]
alto = vol & (s >= umb["SENAL_ALTA"])      # estirado ABAJO
bajo = vol & (s <= umb["SENAL_BAJA"])      # estirado ARRIBA

print("\nrendimiento BRUTO en pips, solo 2020-2023, por celda:")
for etq, m in (("senal ALTA (estirado abajo)", alto & tr),
               ("senal BAJA (estirado arriba)", bajo & tr)):
    x = r[m & np.isfinite(r)]
    print(f"  {etq:30s} n={len(x):>6,}  media largo {x.mean():+.3f}  media corto {-x.mean():+.3f}")

for etq, largo_en_alta in (("A  comprar en ALTA / vender en BAJA (reversion)", True),
                           ("B  vender en ALTA / comprar en BAJA (momento)", False)):
    lado = np.where(alto, 1 if largo_en_alta else -1,
             np.where(bajo, -1 if largo_en_alta else 1, 0))
    br = lado * r
    m = tr & (lado != 0) & np.isfinite(br)
    x = br[m]
    print(f"\n{etq}\n   n={len(x):,} ({len(x)/4:.0f}/ano) bruto {x.mean():+.3f} "
          f"neto {x.mean()-1.20:+.3f} pips")
