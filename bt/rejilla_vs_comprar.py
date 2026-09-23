"""El control que decide la rejilla: cada celda CONTRA comprar y aguantar.

Un indicador que acierta el 100 % del tiempo en un mercado que sube un 143 %
no demuestra nada si comprar y no tocar nada lo habria batido. Aqui se mide
el EXCESO mes a mes sobre comprar y aguantar, y el porcentaje de tiempo que
la senal esta larga.

  python3 bt/rejilla_vs_comprar.py
"""
import numpy as np, pandas as pd
from math import sqrt
src=open("bt/rejilla_indicadores.py").read().split("FIL = {}")[0]
exec(compile(src,"r","exec"))
print(f"{'':<26}{'B&H t':>9}{'subida':>9}   |  indicador NETO t  y  EXCESO sobre B&H")
for nom, ruta, U, coste in INS:
    M=pd.read_parquet(ruta); M["ts"]=pd.to_datetime(M["ts"]); M=M.sort_values("ts").drop_duplicates("ts")
    print("\n"+"="*104); print(nom); print("="*104)
    for et,mi in TF:
        b=barras(M,mi); r=np.log(b.c).diff(); vol=r.rolling(VENT).std().shift(1)
        ok=(vol>0)&r.notna()&vol.notna(); z=(r/vol).where(ok)
        cr=(coste*U/b.c)/vol
        mbh=z.dropna().resample("ME").sum(); tbh,_=tt(mbh)
        sub=100*(b.c.iloc[-1]/b.c.iloc[0]-1)
        fila=f"  {et:<24}{tbh:>+9.2f}{sub:>8.0f}%   |"
        det=[]
        for k,s in sen(b).items():
            s=s.shift(1).where(ok); p=(s*z); f=(s!=s.shift(1))&ok
            pn=(p-f.astype(float)*cr*s.abs()).dropna()
            mn=pn.resample("ME").sum(); mn=mn[pn.resample("ME").count()>=5]
            tn,_=tt(mn)
            # exceso: el indicador MENOS comprar y aguantar, mes a mes
            ex=(mn-mbh.reindex(mn.index)).dropna(); tx,_=tt(ex)
            # y cuanto tiempo esta LARGO
            lg=100*(s[ok]>0).mean()
            if np.isfinite(tn): det.append((k,tn,tx,lg))
        print(fila)
        for k,tn,tx,lg in det:
            mk="  <-- gana a B&H" if tx>2 else ("" if tx>-2 else "  (pierde vs B&H)")
            print(f"      {k:<20} t {tn:>+6.2f}   exceso t {tx:>+6.2f}   largo {lg:>3.0f}% del tiempo{mk}")
