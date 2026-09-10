"""SU regla -cuerpo de la M5 rota por el cierre de una M1- en los siete
instrumentos, para ver si el problema es DONDE la aplica.

Lo que se mide exacto: el tamano natural de su stop (extremo de los ultimos 10
minutos) en cada instrumento, y el acierto de la regla a ciegas.

Lo que NO esta medido: el coste real de todos menos EURUSD (1,43 p, verificado
en la cuenta). Los demas son estimaciones de spread tipico de prop firm y estan
marcados como tales.

  python3 bt/su_regla_instrumentos.py
"""
import numpy as np, pandas as pd

TZ, SEP, RETRO = "Europe/Madrid", 4, 10
# instrumento: (ficheros, unidad, coste ida y vuelta en unidades, medido?, ventana)
INSTR = {
 "EURUSD": (["data/eurusd_m1.parquet"],                     1e-4, 1.43, True,  (480, 690)),
 "GBPUSD": (["data/gbpusd_m1.parquet"],                     1e-4, 1.60, False, (480, 690)),
 "USDJPY": (["data/usdjpy_m1.parquet"],                     1e-2, 1.50, False, (480, 690)),
 "XAUUSD": (["data/xauusd_m1.parquet"],                     1e-2, 20.0, False, (480, 690)),
 "GRXEUR": (["data/grxeur_m1.parquet"],                     1e-0, 1.50, False, (480, 690)),
 "NSXUSD": (["data/nsxusd_m1.parquet"],                     1e-0, 1.50, False, (930, 1140)),
 "SPXUSD": (["data/spxusd_m1.parquet"],                     1e-0, 0.50, False, (930, 1140)),
}

def corre(nom):
    rutas, U, COSTE, medido, (INI, FIN) = INSTR[nom]
    d = pd.concat([pd.read_parquet(r) for r in rutas], ignore_index=True)
    d["ts"] = pd.to_datetime(d["ts"])
    d = d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    loc = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    d["dia"] = loc.date; d["min"] = loc.hour*60 + loc.minute
    d = d[(d["min"] >= INI) & (d["min"] <= FIN)].reset_index(drop=True)
    res, rangos = [], []
    for dia, g in d.groupby("dia", sort=False):
        if len(g) < 150: continue
        O,H,L,C,M = (g.open.to_numpy(), g.high.to_numpy(), g.low.to_numpy(),
                     g.close.to_numpy(), g["min"].to_numpy())
        rangos.append(np.median(H-L))
        b5 = {}
        for k in range(len(g)):
            q = M[k]//5
            if q not in b5: b5[q] = [O[k],H[k],L[k],C[k]]
            else: b5[q][1]=max(b5[q][1],H[k]); b5[q][2]=min(b5[q][2],L[k]); b5[q][3]=C[k]
        ult, ulL = -99, 0
        for k in range(len(g)):
            m = int(M[k]); q = m//5 - 1
            if q not in b5: continue
            o5,h5,l5,c5 = b5[q]; cA,cB = min(o5,c5), max(o5,c5)
            lado = 1 if C[k] > cB else (-1 if C[k] < cA else 0)
            if lado == 0 or (m - ult < SEP and lado == ulL): continue
            ult, ulL = m, lado
            k0 = max(0, k-RETRO+1)
            ent = C[k]
            stp = L[k0:k+1].min() if lado > 0 else H[k0:k+1].max()
            rgo = abs(ent-stp)
            if rgo <= 0: continue
            tp = ent + lado*2*rgo
            hh, ll = H[k+1:], L[k+1:]
            if not len(hh): continue
            gs = (ll <= stp) if lado > 0 else (hh >= stp)
            gt = (hh >= tp)  if lado > 0 else (ll <= tp)
            isl = int(np.argmax(gs)) if gs.any() else 10**9
            itp = int(np.argmax(gt)) if gt.any() else 10**9
            if isl == 10**9 and itp == 10**9:
                sal = C[-1]; R = ((sal-ent) if lado > 0 else (ent-sal))/rgo; mot = "fuera"
            else:
                R, mot = (-1.0, "SL") if isl <= itp else (2.0, "TP")
            res.append((rgo/U, mot, R, R - COSTE*U/rgo))
    r = pd.DataFrame(res, columns=["rgo","mot","R","neta"])
    return r, U, COSTE, medido, float(np.median(rangos))/U

print(f"{'instr':>7s} {'n':>8s} {'stop med':>10s} {'rango M1':>9s} {'coste':>8s} "
      f"{'coste/stop':>11s} {'acierto':>9s} {'necesario':>10s} {'R neta':>9s} {'medido?':>8s}")
print("-"*100)
filas = []
for nom in INSTR:
    r, U, COSTE, medido, rgM1 = corre(nom)
    res = r[r.mot.isin(["TP","SL"])]
    ac = 100*(res.mot == "TP").mean()
    st = r.rgo.median()
    cs = 100*COSTE/st
    nec = 100*(1+COSTE/st)/3
    print(f"{nom:>7s} {len(r):8d} {st:9.1f}u {rgM1:8.1f}u {COSTE:7.2f}u {cs:10.1f} % "
          f"{ac:8.1f} % {nec:9.1f} % {r.neta.mean():+9.3f} {'sí' if medido else 'ESTIM':>8s}")
    filas.append(dict(instr=nom, n=len(r), stop=st, rangoM1=rgM1, coste=COSTE,
                      cs=cs, ac=ac, nec=nec, neta=r.neta.mean(), medido=medido))
pd.DataFrame(filas).to_csv("data/su_regla_instrumentos.csv", index=False)
print("\n(u = unidad del instrumento: pip en divisas, 0,01 $ en oro, 1 punto en índices)")
