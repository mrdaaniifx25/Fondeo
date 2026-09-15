"""Prueba el motor NSBE de Multi Bias como FILTRO sobre las senales del CRT.

NSBE: estado +1 si el precio cierra por encima del ultimo swing alto confirmado
y no consumido; -1 si cierra por debajo del ultimo swing bajo. Sensibilidad 5
velas a la izquierda, 3 de confirmacion a la derecha (los valores de fabrica).

Se calcula sobre velas CERRADAS de cada temporalidad y se mapea a la vela M15
con el mismo desplazamiento antirrepintado que usa el indicador.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "bt")
from estrategia_crt import Config, marcos, senales, simular, metricas

def nsbe(df, sL=5, sR=3, brk_close=True):
    hi, lo, cl = df.high.to_numpy(), df.low.to_numpy(), df.close.to_numpy()
    n = len(df); estado = np.zeros(n, dtype=int)
    sHi = sLo = np.nan; hiLive = loLive = False; st = 0
    for i in range(n):
        # pivote confirmado en la vela i-sR (necesita sL a la izq y sR a la der)
        j = i - sR
        if j - sL >= 0:
            if hi[j] == hi[j-sL:j+sR+1].max() and (hi[j-sL:j+sR+1] == hi[j]).sum() == 1:
                sHi, hiLive = hi[j], True
            if lo[j] == lo[j-sL:j+sR+1].min() and (lo[j-sL:j+sR+1] == lo[j]).sum() == 1:
                sLo, loLive = lo[j], True
        up = hiLive and not np.isnan(sHi) and (cl[i] > sHi if brk_close else hi[i] > sHi)
        dn = loLive and not np.isnan(sLo) and (cl[i] < sLo if brk_close else lo[i] < sLo)
        if up and dn:                      # envolvente que rompe los dos lados
            if cl[i] >= (sHi + sLo) * 0.5: dn = False
            else: up = False
        if up: hiLive, st = False, 1
        if dn: loLive, st = False, -1
        estado[i] = st
    return estado

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config()
ch = marcos(m1, cfg)
sig, _ = senales(ch, cfg)
tr, _ = simular(sig, m1, cfg)

for regla, nombre in (("4h", "H4"), ("1D", "D1")):
    g = m1.set_index("ts").resample(regla, label="left", closed="left")
    htf = g.agg(high=("high","max"), low=("low","min"), close=("close","last")).dropna().reset_index()
    htf["bias"] = nsbe(htf)
    htf["bias"] = htf["bias"].shift(1)          # solo velas cerradas
    htf["disp"] = htf["ts"] + pd.Timedelta(regla)
    tr = pd.merge_asof(tr.sort_values("ts"),
                       htf[["disp","bias"]].rename(columns={"disp":"ts","bias":f"bias_{nombre}"}).sort_values("ts"),
                       on="ts", direction="backward")

print(f"Operaciones base: {len(tr)}  |  R total {tr.R.sum():+.2f}  PF ref 0.889\n")
print(f"{'filtro':34s} {'ops':>5s} {'WR%':>7s} {'R tot':>8s} {'R/op':>8s} {'PF':>7s}")
print("-"*72)

def linea(nombre, sub):
    if len(sub) == 0:
        print(f"{nombre:34s} {'0':>5s}"); return
    gan, per = sub[sub.R>0], sub[sub.R<=0]
    pf = gan.R.sum()/(-per.R.sum()) if len(per) and per.R.sum() < 0 else float('inf')
    print(f"{nombre:34s} {len(sub):>5d} {100*(sub.R>0).mean():>7.2f} "
          f"{sub.R.sum():>8.2f} {sub.R.mean():>8.4f} {pf:>7.3f}")

linea("sin filtro", tr)
for tf in ("H4", "D1"):
    b = tr[f"bias_{tf}"]
    largo, corto = tr["dir"] == "largo", tr["dir"] == "corto"
    linea(f"a favor del sesgo {tf}",   tr[(largo & (b==1)) | (corto & (b==-1))])
    linea(f"en contra del sesgo {tf}", tr[(largo & (b==-1)) | (corto & (b==1))])
alin = (tr.bias_H4 == tr.bias_D1) & tr.bias_H4.notna() & (tr.bias_H4 != 0)
largo, corto = tr["dir"]=="largo", tr["dir"]=="corto"
linea("H4 y D1 alineados, a favor", tr[alin & ((largo & (tr.bias_H4==1)) | (corto & (tr.bias_H4==-1)))])
linea("H4 y D1 alineados, en contra", tr[alin & ((largo & (tr.bias_H4==-1)) | (corto & (tr.bias_H4==1)))])
tr.to_csv("data/trades_crt_bias.csv", index=False)
