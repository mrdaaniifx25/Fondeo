"""Control positivo: se INYECTA una ventaja conocida y se comprueba que el
motor la recupera.

El validador `bt/valida_motor.py` demuestra que el motor no FABRICA
ventajas donde no las hay. Esto demuestra lo contrario: que no las
DESTRUYE cuando si las hay. Son dos comprobaciones distintas y hasta
ahora solo estaba hecha una.

  python3 bt/control_positivo.py
"""
import numpy as np, pandas as pd

U, STOP, VIDA = 1e-4, 10.0, 240      # 10 pips de stop, 1:1, 4 h de vida

def prueba(deriva_pips, sesgo_real, sims=1):
    d = pd.read_parquet("data/eurusd_m1.parquet")
    d["ts"]=pd.to_datetime(d.ts); d=d.sort_values("ts").drop_duplicates("ts")
    d=d.reset_index(drop=True).rename(columns={"open":"o","high":"h","low":"l","close":"c"})
    c = d.c.to_numpy().copy(); h=d.h.to_numpy().copy(); l=d.l.to_numpy().copy()
    n=len(c)
    rng=np.random.default_rng(2026)
    # disparadores: una vez al dia a las 08:00 UTC
    disp = np.where((d.ts.dt.hour==8)&(d.ts.dt.minute==0))[0]
    disp = disp[(disp>10)&(disp<n-VIDA-1)]
    # a una fraccion `sesgo_real` se le inyecta deriva a favor de COMPRAS
    favor = rng.random(len(disp)) < sesgo_real
    ajuste = np.zeros(n)
    for k,i in enumerate(disp):
        paso = (deriva_pips*U/VIDA) * (1 if favor[k] else -1)
        ajuste[i+1:i+1+VIDA] += paso
    acum = np.cumsum(ajuste)
    c2, h2, l2 = c+acum, h+acum, l+acum
    # el motor: entra SIEMPRE en compras en el disparador, 1:1, stop 10 pips
    Rs=[]
    for i in disp:
        ent=c2[i]; sl=ent-STOP*U; tp=ent+STOP*U
        H,L=h2[i+1:i+1+VIDA], l2[i+1:i+1+VIDA]
        ms=L<=sl; mt=H>=tp
        iS=int(np.argmax(ms)) if ms.any() else 10**9
        iT=int(np.argmax(mt)) if mt.any() else 10**9
        if iS==10**9 and iT==10**9: Rs.append((c2[min(i+VIDA,n-1)]-ent)/(STOP*U))
        else: Rs.append(-1.0 if iS<=iT else 1.0)
    R=np.array(Rs)
    z=R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))
    return len(R), 100*(R>0).mean(), R.mean(), z

if __name__=="__main__":
    print("Se inyecta una deriva conocida a favor de las compras en una")
    print("fraccion de los dias, y se mira si el motor la recupera.")
    print("Entrada fija a las 08:00, stop 10 pips, objetivo 10 pips (1:1).")
    print("Sin inyeccion, el liston es 50 % de acierto y R = 0.\n")
    print(f"{'deriva':>8s} {'% dias a favor':>15s} {'n':>6s} {'acierto':>9s} {'R':>8s} {'z':>8s}")
    print("-"*60)
    for deriva, sesgo in ((0,0.5),(0,0.5),(5,0.60),(10,0.60),(10,0.70),(20,0.70),(20,0.90)):
        n,ac,r,z = prueba(deriva, sesgo)
        et = "ninguna" if deriva==0 else f"{deriva} pips"
        print(f"{et:>8s} {100*sesgo:14.0f} % {n:6d} {ac:8.1f} % {r:+8.3f} {z:+8.2f}")
