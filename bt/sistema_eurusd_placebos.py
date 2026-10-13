"""Placebos del sistema de bt/sistema_eurusd_intradia.py. Es lo que encontro
el error de signo que inflaba el backtest a profit factor 2,61.

  python3 bt/sistema_eurusd_placebos.py
"""
import numpy as np, pandas as pd
from math import sqrt
src = open("bt/sistema_eurusd_intradia.py").read().split('print(f"{\'sesion\'')[0]
exec(compile(src, "s", "exec"))
rng = np.random.default_rng(1)

S = senales("Europe/London", 8, 12)
S["dia"] = pd.to_datetime(S.ts).dt.floor("D")
print(f"n {len(S)}  riesgo mediano {S.rgo.median():.1f} pips  lado: "
      f"{(S.lado>0).mean()*100:.0f} % largos")

def corre(lados, rr=1.5, trail=False, tope=240):
    R=[];fin=[]
    for (_, r), ld in zip(S.iterrows(), lados):
        ent=OO[int(r.e)]; rg=r.rgo*U; sl=ent-ld*rg; tp=ent+ld*rg*rr
        res=None
        for k in range(int(r.e), min(int(r.e)+tope, len(M))):
            if ld>0:
                if LL[k]<=sl: res=(-1.0,"SL"); break
                if HH[k]>=tp: res=(rr,"TP"); break
            else:
                if HH[k]>=sl: res=(-1.0,"SL"); break
                if LL[k]<=tp: res=(rr,"TP"); break
        if res is None:
            k=min(int(r.e)+tope,len(M))-1
            res=((CC[k]-ent)*ld/rg,"abierta")
        R.append(res[0]); fin.append(res[1])
    return np.array(R), pd.Series(fin)

R, F = corre(S.lado.to_numpy())
print("\ndesenlaces:", F.value_counts().to_dict())
print(f"R media {R.mean():+.4f}   acierto(R>0) {100*(R>0).mean():.1f} %"
      f"   TP puro {100*(F=='TP').mean():.1f} %   SL {100*(F=='SL').mean():.1f} %")
print(f"  (nulo geometrico para R:R 1,5 = 40,0 %)")

print("\nPLACEBO 1 · direccion AL AZAR, mismas entradas y geometria")
for _ in range(3):
    Rp,_ = corre(rng.choice([-1,1], size=len(S)))
    print(f"  R media {Rp.mean():+.4f}   acierto {100*(Rp>0).mean():.1f} %")

print("\nPLACEBO 2 · direccion INVERTIDA")
Ri,_ = corre(-S.lado.to_numpy())
print(f"  R media {Ri.mean():+.4f}   acierto {100*(Ri>0).mean():.1f} %")

print("\nPLACEBO 3 · entradas en minutos AL AZAR de la misma ventana, mismo riesgo")
idx = rng.choice(S.e.to_numpy(), size=len(S), replace=True)
S2 = S.copy(); S2["e"] = idx
gS = S; S = S2
Ra,_ = corre(gS.lado.to_numpy()); S = gS
print(f"  R media {Ra.mean():+.4f}   acierto {100*(Ra>0).mean():.1f} %")

print("\nDIAGNOSTICO · cuanto se mueve el precio DESPUES de la entrada, por lado")
mv = []
for (_, r) in S.iterrows():
    e=int(r.e); k=min(e+240,len(M))-1
    mv.append((CC[k]-OO[e])/U*r.lado)
mv=np.array(mv)
print(f"  movimiento medio a favor del sesgo en 4 h: {mv.mean():+.2f} pips"
      f"  (riesgo mediano {S.rgo.median():.1f})")
print(f"  mediana {np.median(mv):+.2f}   % a favor {100*(mv>0).mean():.1f} %")
