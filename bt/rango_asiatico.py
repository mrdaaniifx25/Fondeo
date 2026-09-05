"""Manipulacion del rango asiatico (Tradinverso). Preregistro: aeddfb1.

  RANGO      01:00 - 08:00 hora de Espana
  VENTANA    08:00 - 10:30 hora de Espana
  M15 y solo M15
  SETUP      FVG o MECHA LIQUIDA fuera del rango
  ENTRADA    limitada al 50 % de esa zona
  STOP       al otro lado, 4-8 pips, ajustado a ratio >= 1:3
  OBJETIVO   el extremo OPUESTO del rango
  una operacion al dia

  python3 bt/rango_asiatico.py
"""
import numpy as np, pandas as pd

INSTR = {"EURUSD":("data/eurusd_m1.parquet",1e-4,1.43),
         "GBPUSD":("data/gbpusd_m1.parquet",1e-4,1.60),
         "USDJPY":("data/usdjpy_m1.parquet",1e-2,1.50)}   # control
RRMIN, SLMIN, SLMAX, MECHA = 3.0, 4.0, 8.0, 0.50

def corre(nom, ruta, U, coste):
    d = pd.read_parquet(ruta); d["ts"]=pd.to_datetime(d.ts)
    d = d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    d = d.rename(columns={"open":"o","high":"h","low":"l","close":"c"})
    g = (d.set_index("ts").resample("15min",label="left",closed="left")
         .agg(o=("o","first"),h=("h","max"),l=("l","min"),c=("c","last"),
              n=("c","size")).dropna())
    g = g[g.n>=6].reset_index()
    # hora local de Espana, con cambio de hora resuelto por zona horaria
    loc = g.ts.dt.tz_localize("UTC").dt.tz_convert("Europe/Madrid")
    g["hloc"] = loc.dt.hour + loc.dt.minute/60
    g["dia"]  = loc.dt.date
    o,h,l,c = g.o.to_numpy(),g.h.to_numpy(),g.l.to_numpy(),g.c.to_numpy()
    hl, dia = g.hloc.to_numpy(), g.dia.to_numpy()
    filas=[]
    for D in pd.unique(dia):
        m  = dia==D
        ra = m & (hl>=1) & (hl<8)          # rango asiatico
        vt = m & (hl>=8) & (hl<10.5)       # ventana operativa
        if ra.sum()<20 or vt.sum()<8: continue
        alto, bajo = float(h[ra].max()), float(l[ra].min())
        if alto<=bajo: continue
        idx = np.where(vt)[0]
        hecho=False
        for k in idx[:-1]:
            if hecho: break
            cuerpo = abs(c[k]-o[k]); rango = h[k]-l[k]
            if rango<=0: continue
            for lado in (-1,+1):           # -1 venta (setup arriba), +1 compra
                if hecho: break
                # --- MECHA LIQUIDA: mecha fuera del rango >= 50 % de la vela
                if lado<0:
                    mech = h[k]-max(o[k],c[k])
                    fuera = h[k]>alto
                    zlo, zhi = max(o[k],c[k]), h[k]
                else:
                    mech = min(o[k],c[k])-l[k]
                    fuera = l[k]<bajo
                    zlo, zhi = l[k], min(o[k],c[k])
                ok_mecha = fuera and mech >= MECHA*rango and mech>0
                # --- FVG de M15 fuera del rango
                ok_fvg=False
                if k>=2:
                    if lado<0 and h[k]<l[k-2] and l[k-2]>alto:
                        zlo,zhi,ok_fvg = h[k],l[k-2],True
                    if lado>0 and l[k]>h[k-2] and h[k-2]<bajo:
                        zlo,zhi,ok_fvg = h[k-2],l[k],True
                if not (ok_mecha or ok_fvg): continue
                if zhi<=zlo: continue
                ent = (zlo+zhi)/2
                tp  = bajo if lado<0 else alto
                # stop al otro lado de la zona, acotado a 4-8 pips
                base = (zhi-ent) if lado<0 else (ent-zlo)
                sl_p = min(max(base/U, SLMIN), SLMAX)
                rgo  = sl_p*U
                if abs(tp-ent)/rgo < RRMIN: continue
                # la limitada se rellena en alguna vela posterior de la ventana
                lleno=None
                for j in range(k+1, idx[-1]+1):
                    if (h[j]>=ent) if lado<0 else (l[j]<=ent): lleno=j; break
                if lleno is None: continue
                stp = ent + (rgo if lado<0 else -rgo)
                R=None
                fin = min(len(g)-1, lleno+96)
                for j in range(lleno+1, fin+1):
                    if dia[j]!=D and R is None and j>lleno+40: break
                    if (h[j]>=stp) if lado<0 else (l[j]<=stp): R=-1.0; break
                    if (l[j]<=tp)  if lado<0 else (h[j]>=tp):  R=abs(tp-ent)/rgo; break
                if R is None:
                    sal=c[fin]; R=((ent-sal) if lado<0 else (sal-ent))/rgo
                filas.append(dict(instr=nom, dia=D, lado=lado, ent=ent, stp=stp,
                                  tp=tp, sl_pips=sl_p, rr=abs(tp-ent)/rgo,
                                  R=R, Rn=R-coste/sl_p, tipo="FVG" if ok_fvg else "mecha"))
                hecho=True
    return pd.DataFrame(filas)

if __name__=="__main__":
    T=pd.concat([corre(k,*v) for k,v in INSTR.items()], ignore_index=True)
    T.to_csv("data/rango_asiatico.csv", index=False)
    def z(x): x=np.asarray(x,float); return x.mean()/(x.std(ddof=1)/np.sqrt(len(x))) if len(x)>2 else 0
    print("liston geometrico a 1:3 = 25,0 % de acierto · R = 0\n")
    print(f"{'instr':>7s} {'n':>5s} {'acierto':>9s} {'R:R medio':>10s} {'stop':>7s} "
          f"{'R bruta':>9s} {'z':>7s} {'R NETA':>9s}")
    print("-"*70)
    for i,gg in T.groupby("instr"):
        print(f"{i:>7s} {len(gg):5d} {100*(gg.R>0).mean():8.1f} % {gg.rr.mean():10.2f} "
              f"{gg.sl_pips.mean():6.1f}p {gg.R.mean():+9.3f} {z(gg.R):+7.2f} {gg.Rn.mean():+9.3f}")
    print("-"*70)
    print(f"{'TODOS':>7s} {len(T):5d} {100*(T.R>0).mean():8.1f} % {T.rr.mean():10.2f} "
          f"{T.sl_pips.mean():6.1f}p {T.R.mean():+9.3f} {z(T.R):+7.2f} {T.Rn.mean():+9.3f}")
    print("\npor tipo de zona")
    for t,gg in T.groupby("tipo"):
        print(f"  {t:>7s} {len(gg):5d} {100*(gg.R>0).mean():8.1f} % {gg.R.mean():+9.3f} "
              f"{z(gg.R):+7.2f} {gg.Rn.mean():+9.3f}")
    print("\nEURUSD por ano")
    E=T[T.instr=="EURUSD"].copy(); E["anio"]=pd.to_datetime(E.dia).dt.year
    for a,gg in E.groupby("anio"):
        print(f"  {a} {len(gg):5d} {100*(gg.R>0).mean():8.1f} % {gg.R.mean():+9.3f} "
              f"{z(gg.R):+7.2f} {gg.Rn.mean():+9.3f}")
