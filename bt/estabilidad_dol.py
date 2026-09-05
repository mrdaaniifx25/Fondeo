"""¿La inestabilidad entre mitades es azar o es real?
¿Y el filtro DOL es una meseta en el espacio de parametros o un filo?"""
import sys, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0,"bt")
from estrategia_dol import C, senales, simular

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
ch = pd.read_parquet("data/ch_dol.parquet")
def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
cfg = C(dol_filtro=True, tp_r=3.0)
sig,_ = senales(ch, cfg); tr = simular(sig, m1, cfg)
tr["b"] = (tr.pips+cfg.coste_pips)/tr.riesgo_pips

print("=== 1. ¿ES COMPATIBLE CON UNA VENTAJA CONSTANTE? ===")
b = tr.b.to_numpy(); n = len(b)
obs = b[n//2:].mean() - b[:n//2].mean()
rng = np.random.default_rng(0)
dif = np.array([(lambda x: x[n//2:].mean()-x[:n//2].mean())(rng.permutation(b)) for _ in range(20000)])
pval = (np.abs(dif) >= abs(obs)).mean()
print(f"  diferencia observada entre mitades: {obs:+.4f} R/op")
print(f"  bajo ventaja constante (20.000 permutaciones): |dif| >= observada en {100*pval:.1f}% de los casos")
print(f"  -> {'NO se puede descartar el azar' if pval>0.05 else 'la inestabilidad es REAL'}")

print("\n=== 2. ¿MESETA O FILO? sensibilidad del umbral del filtro ===")
print("   k = cuanto mas lejos puede estar el DOL a favor que el contrario y aun asi operar")
import estrategia_dol as ed
src = open("bt/estrategia_dol.py").read()
for k in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 3.0, 99.0):
    mod = src.replace("if d_fav > d_con: continue", f"if d_fav > {k}*d_con: continue")
    ns = {}
    exec(compile(mod, "m", "exec"), ns)
    c2 = ns["C"](dol_filtro=True, tp_r=3.0)
    s2,_ = ns["senales"](ch, c2); t2 = ns["simular"](s2, m1, c2)
    if t2.empty or len(t2)<40: print(f"  k={k:<5} pocas ops"); continue
    bb = (t2.pips+c2.coste_pips)/t2.riesgo_pips
    z,p = pz(bb)
    h = len(t2)//2
    print(f"  k={k:<5} n {len(t2):>4} | bruto/op {bb.mean():+.4f} | z {z:+5.2f} | p {p:.3f} "
          f"| 1a mitad {bb.iloc[:h].mean():+.3f} | 2a mitad {bb.iloc[h:].mean():+.3f}")

print("\n=== 3. ¿DE QUE MARCO VIENE EL FILTRO? ===")
for marcos in (("D",), ("W",), ("M",), ("D","W"), ("W","M"), ("D","W","M")):
    c3 = C(dol_filtro=True, tp_r=3.0, dol_marcos=marcos)
    s3,_ = senales(ch, c3); t3 = simular(s3, m1, c3)
    if t3.empty or len(t3)<40: print(f"  {'+'.join(marcos):<8} pocas ops"); continue
    bb=(t3.pips+c3.coste_pips)/t3.riesgo_pips; z,p=pz(bb); h=len(t3)//2
    print(f"  {'+'.join(marcos):<8} n {len(t3):>4} | bruto/op {bb.mean():+.4f} | p {p:.3f} "
          f"| 1a {bb.iloc[:h].mean():+.3f} | 2a {bb.iloc[h:].mean():+.3f}")
