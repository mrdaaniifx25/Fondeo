"""Autopsia de la candidata descartada. Esto YA NO decide nada: el veredicto
esta dado. Solo sirve para saber que fallo exactamente."""
import sys; sys.path.insert(0, "bt")
import numpy as np, pandas as pd, variables as V, cero
U=0.0001; umb=cero.lee_umbrales()
m1=pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"]=pd.to_datetime(m1["ts"])
d=V.m15(m1); X=V.construye(d); atr=(V.atr(d,48)/U).to_numpy(); s=cero.senal(X,2688).to_numpy()
r=((d.close.shift(-4)-d.close)/U).to_numpy()
tr=(d.ts<"2024-01-01").to_numpy(); te=~tr; ok=np.isfinite(s)&np.isfinite(r)

print("A · ¿cambio el regimen de volatilidad?  ATR(48) en pips")
for e,m in (("2020-2023",tr&ok),("2024-2026",te&ok)):
    a=atr[m]; print(f"   {e}  mediana {np.median(a):6.2f}   p80 {np.quantile(a,.80):6.2f}"
                    f"   %velas sobre 9,4708: {100*(a>=9.4708).mean():5.1f}%")

print("\nB · ¿sobrevive la señal antes del filtro de volatilidad?  (bruto, sin coste)")
for e,m in (("2020-2023",tr&ok),("2024-2026",te&ok)):
    lado=np.where(s>=umb["SENAL_ALTA"],1,np.where(s<=umb["SENAL_BAJA"],-1,0))
    mm=m&(lado!=0); b=lado[mm]*r[mm]
    print(f"   {e}  todas las velas extremas: n={mm.sum():>5,}  bruto {b.mean():+6.3f}")

print("\nC · la rejilla entera, recalculada en 2024-2026 (NETA, coste 1,20)")
qa=np.array([np.quantile(atr[tr&ok],q) for q in (.40,.60,.80)])
print(f"   {'':14s}"+"".join(f"{p:>9s}" for p in ("1 %","2 %","5 %","10 %")))
for nom,amin in (("ATR >= p80",qa[2]),("ATR >= p60",qa[1]),("ATR >= p40",qa[0]),("todas",-1)):
    fila=[]
    for p in (.01,.02,.05,.10):
        vol=atr>=amin
        base=tr&ok&vol
        lo,hi=np.quantile(s[base],p),np.quantile(s[base],1-p)
        lado=np.where(vol&(s>=hi),1,np.where(vol&(s<=lo),-1,0))
        mm=te&ok&(lado!=0); b=lado[mm]*r[mm]
        fila.append(f"{b.mean()-1.20:+9.2f}" if mm.sum()>30 else "        —")
    print(f"   {nom:14s}"+"".join(fila))
print("   (umbrales de señal recalculados sobre 2020-2023; solo cambia la celda)")

print("\nD · ¿cuanto tendria que costar operar para que 2024-2026 fuese rentable?")
lado=np.where((atr>=umb["ATR48_MIN"])&(s>=umb["SENAL_ALTA"]),1,
      np.where((atr>=umb["ATR48_MIN"])&(s<=umb["SENAL_BAJA"]),-1,0))
mm=te&ok&(lado!=0); b=lado[mm]*r[mm]
print(f"   ventaja bruta 2024-2026: {b.mean():+.3f} pips. Coste supuesto 1,20.")
print(f"   haria falta un coste por debajo de {b.mean():.2f} pips: ida y vuelta, imposible.")

print("\nE · ¿cuantas operaciones harian falta para distinguir +1,4 de 0?")
sd=b.std(ddof=1); print(f"   desviacion tipica por operacion: {sd:.2f} pips")
n=(2.8*sd/1.404)**2
print(f"   para detectar +1,404 al 80% de potencia: {n:.0f} operaciones = {n/187:.1f} años")
print(f"   el descubrimiento tenia 748. Su IC95 ya era [-0,002, +2,811]: tocaba el cero.")
