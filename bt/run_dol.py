import sys, numpy as np, pandas as pd
from math import sqrt, erf
sys.path.insert(0,"bt")
from estrategia_dol import C, senales, simular
m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
ch = pd.read_parquet("data/ch_dol.parquet")
def pz(x):
    n=len(x); se=x.std(ddof=1)/sqrt(n); z=x.mean()/se
    return z, 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
def run(nom, **kw):
    cfg=C(**kw); sig,emb=senales(ch,cfg); tr=simular(sig,m1,cfg)
    if tr.empty or len(tr)<30: print(f"{nom:44s} {len(tr) if not tr.empty else 0:>5}"); return None
    tr["b"]=(tr.pips+cfg.coste_pips)/tr.riesgo_pips
    z,p=pz(tr.b); gan,per=tr[tr.R>0],tr[tr.R<=0]
    pf=gan.R.sum()/(-per.R.sum()) if per.R.sum()<0 else float('inf')
    print(f"{nom:44s} {len(tr):>5d} {100*(tr.R>0).mean():>6.2f}% {tr.rr.mean():>6.2f} "
          f"{tr.b.mean():>+8.4f} {z:>+5.2f} {p:>7.3f} {tr.R.sum():>+8.2f} {pf:>6.3f}")
    return tr

print(f"{'configuracion':44s} {'ops':>5s} {'WR':>7s} {'RR':>6s} {'bruto/op':>8s} {'z':>5s} "
      f"{'p':>7s} {'R neto':>8s} {'PF':>6s}")
print("-"*106)
run("referencia: TP 3R fijo, sin DOL",            dol_filtro=False, dol_target=False)
run("DOL como FILTRO de direccion, TP 3R",        dol_filtro=True,  dol_target=False)
run("DOL como OBJETIVO",                          dol_filtro=False, dol_target=True)
run("DOL como filtro Y objetivo",                 dol_filtro=True,  dol_target=True)
run("DOL objetivo, solo semanal y mensual",       dol_target=True,  dol_marcos=("W","M"))
run("DOL filtro+objetivo, R:R minimo 2",          dol_filtro=True,  dol_target=True, min_rr=2.0)
run("DOL filtro+objetivo, R:R minimo 3",          dol_filtro=True,  dol_target=True, min_rr=3.0)
run("DOL objetivo, R:R entre 2 y 8",              dol_target=True,  min_rr=2.0, max_rr=8.0)
run("DOL filtro, TP 4R",                          dol_filtro=True,  tp_r=4.0)
run("solo DOL filtro, sin order block",           dol_filtro=True,  usar_ob=False)
