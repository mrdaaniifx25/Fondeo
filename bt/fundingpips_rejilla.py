"""Rejilla de riesgo x operaciones-dia para SU cuenta de FundingPips 10k.

Lo decisivo: n*riesgo nunca debe ACERCARSE al limite diario del 3 %. Al
tocarlo exacto la aprobacion se desploma de ~35 % a ~5 %.

  python3 bt/fundingpips_rejilla.py
"""
import numpy as np, sys
rng = np.random.default_rng(7)
N, DIAS = 40000, 300
F1, F2, DIA, TOT, COSTE = 0.08, 0.05, 0.03, 0.10, 0.10
def carrera(p, rr, rg, nd):
    saldo=np.zeros(N); fase=np.zeros(N,int); vivo=np.ones(N,bool); meta=np.full(N,F1); dd=np.zeros(N)
    for _ in range(DIAS):
        if not vivo.any(): break
        k=int(vivo.sum()); ini=saldo[vivo].copy(); dpl=np.zeros(k); md=np.zeros(k,bool)
        for _o in range(nd):
            act=~md
            if not act.any(): break
            g=rng.random(k)<p
            r=(np.where(g,rr,-1.0)-COSTE)*rg
            dpl=np.where(act,dpl+r,dpl); md|=(dpl<=-DIA)
        saldo[vivo]=ini+dpl
        idx=np.nonzero(vivo)[0]
        fuera=(saldo[vivo]<=-TOT)|md
        vivo[idx[fuera]]=False
        ok=np.nonzero(vivo)[0]
        if len(ok):
            paso=saldo[ok]>=meta[ok]
            sube=ok[paso&(fase[ok]==0)]; fin=ok[paso&(fase[ok]==1)]
            fase[sube]=1; saldo[sube]=0.0; meta[sube]=F2
            fase[fin]=2; vivo[fin]=False
    return (fase==2).mean()
print("FundingPips 10k · fase1 +8 % · fase2 +5 % · día -3 % · total -10 % · coste 0,10 R")
print("ESPERANZA CERO. % que pasa LAS DOS fases.\n")
for rr in (1.0, 2.0):
    p=(1+0.0+COSTE)/(1+rr)
    print(f"  R:R {rr:.0f} · acierto {100*p:.1f} %")
    print(f"  {'ops/día':>8}" + "".join(f"{f'{100*r:.2f}%':>10}" for r in (0.005,0.0075,0.01,0.015,0.02,0.03)))
    for nd in (1,2,3,4):
        fila=f"  {nd:>8}"
        for rg in (0.005,0.0075,0.01,0.015,0.02,0.03):
            fila += (f"{f'{100*carrera(p,rr,rg,nd):.1f}%':>10}" if nd*rg<=DIA+1e-9 else f"{'—':>10}")
        print(fila); sys.stdout.flush()
    print()
