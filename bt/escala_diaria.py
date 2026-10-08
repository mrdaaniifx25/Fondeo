"""docs/PREREGISTRO_escala_diaria.md · una sola pasada.

  python3 bt/escala_diaria.py
"""
import numpy as np, pandas as pd
from math import sqrt, erf

TZ, TOPE = "Europe/Madrid", 20          # tope de 20 dias habiles
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
zf = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x))) if len(x) > 2 else np.nan

# unidad y coste de ida y vuelta, en unidades del instrumento
INS = {
 "EURUSD": (["data/eurusd_m1.parquet","data/eurusd_m1_2026_08.parquet"], 1e-4, 1.43),
 "GBPUSD": (["data/gbpusd_m1.parquet"],                                   1e-4, 1.80),
 "USDJPY": (["data/usdjpy_m1.parquet"],                                   1e-2, 1.50),
 "XAUUSD": (["data/xauusd_m1.parquet","data/xauusd_m1_2026.parquet"],     0.10, 5.00),
 "NSXUSD": (["data/nsxusd_m1.parquet"],                                   1.00, 2.00),
 "SPXUSD": (["data/spxusd_m1.parquet"],                                   1.00, 0.80),
 "GRXEUR": (["data/grxeur_m1.parquet","data/grxeur_m1_2026.parquet"],     1.00, 2.00),
}

def carga(fs):
    d = pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True)
    d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").reset_index(drop=True)
    d["loc"] = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    d["dia"] = d["loc"].dt.date
    return d

def diarias(m1):
    g = m1.groupby("dia").agg(o=("open","first"), h=("high","max"), l=("low","min"),
                              c=("close","last"), n=("close","size")).reset_index()
    return g[g.n >= 300].reset_index(drop=True)     # dias con sesion de verdad

def senales(D, regla):
    """Devuelve (indice del dia de entrada, lado, stop) para cada disparo."""
    O,H,L,C = D.o.to_numpy(), D.h.to_numpy(), D.l.to_numpy(), D.c.to_numpy()
    out = []
    if regla == "A":                      # barrido diario contra el cuerpo de ayer
        for i in range(1, len(D)):
            cA, cB = min(O[i-1], C[i-1]), max(O[i-1], C[i-1])
            dentro = cA <= C[i] <= cB
            if L[i] < L[i-1] and dentro:  out.append((i,  1, L[i]))
            elif H[i] > H[i-1] and dentro: out.append((i, -1, H[i]))
    elif regla == "B":                    # Donchian 20, stop en el extremo de 10
        for i in range(20, len(D)):
            if C[i] > H[i-20:i].max():    out.append((i,  1, L[i-10:i+1].min()))
            elif C[i] < L[i-20:i].min():  out.append((i, -1, H[i-10:i+1].max()))
    elif regla == "C":                    # ruptura del rango de ayer
        for i in range(1, len(D)):
            if C[i] > H[i-1]:   out.append((i,  1, L[i-1]))
            elif C[i] < L[i-1]: out.append((i, -1, H[i-1]))
    return out

filas = []
for nom, (fs, U, COSTE) in INS.items():
    m1 = carga(fs)
    D = diarias(m1)
    T = m1["loc"].to_numpy(); Hm = m1.high.to_numpy(); Lm = m1.low.to_numpy()
    Cm = m1.close.to_numpy()
    dia_ts = {d: i for i, d in enumerate(D.dia)}
    for regla in ("A","B","C"):
        S = senales(D, regla)
        for k in (1, 2, 3):
            libre_hasta = -1
            for i, lado, stp in S:
                if i <= libre_hasta: continue
                ent = float(D.c.iloc[i])
                rgo = abs(ent - stp)
                if rgo < 2*U: continue
                tp = ent + lado*k*rgo
                ini = np.datetime64(pd.Timestamp(D.dia.iloc[i]) + pd.Timedelta(days=1))
                jfin = min(i + TOPE, len(D)-1)
                fin = np.datetime64(pd.Timestamp(D.dia.iloc[jfin]) + pd.Timedelta(days=1))
                a = int(np.searchsorted(T, ini)); b = int(np.searchsorted(T, fin))
                b = min(max(b, a+1), len(T))
                hh, ll = Hm[a:b], Lm[a:b]
                largo = lado > 0
                gs, gt = ((ll <= stp, hh >= tp) if largo else (hh >= stp, ll <= tp))
                isl = int(np.argmax(gs)) if gs.any() else 10**9
                itp = int(np.argmax(gt)) if gt.any() else 10**9
                if isl == 10**9 and itp == 10**9:
                    sal = Cm[b-1]; R = ((sal-ent) if largo else (ent-sal))/rgo; mot="cierre"
                    dias = jfin - i
                elif isl <= itp:
                    R, mot = -1.0, "SL"; dias = None
                else:
                    R, mot = float(k), "TP"; dias = None
                fin_idx = i + TOPE
                if mot != "cierre":
                    # dia en que se resolvio, para no solapar
                    j = min(isl, itp)
                    ts = T[a+j]
                    dd = pd.Timestamp(ts).date()
                    fin_idx = dia_ts.get(dd, i+1)
                    dias = fin_idx - i
                libre_hasta = fin_idx
                filas.append(dict(ins=nom, regla=regla, k=k, dia=D.dia.iloc[i],
                                  lado=lado, rgo_u=rgo/U, R=R, mot=mot,
                                  neta=R - COSTE/(rgo/U), dias=dias))
    print(f"  {nom}: {len(D)} días · {sum(1 for f in filas if f['ins']==nom)} operaciones",
          flush=True)
t = pd.DataFrame(filas)
t.to_csv("data/escala_diaria.csv", index=False)
print(f"\n{len(t):,} operaciones en total")

print("\n" + "="*94)
print("CONTRASTE PRINCIPAL · nueve celdas, siete instrumentos agrupados")
print("="*94)
print(f"  {'regla':>6s} {'k':>2s} {'n':>5s} {'acierto':>9s} {'geom':>7s} {'dif':>7s} "
      f"{'stop':>7s} {'c/s':>6s} {'R neta':>8s} {'z':>7s} {'signo':>7s} {'c*':>7s}")
print("  " + "-"*90)
NOM = {"A":"A barrido diario","B":"B Donchian 20","C":"C ruptura de ayer"}
res = []
for regla in ("A","B","C"):
    for k in (1,2,3):
        s = t[(t.regla==regla) & (t.k==k)]
        if len(s) < 30: continue
        r = s[s.mot != "cierre"]
        ac, geo = (r.mot=="TP").mean(), 1/(1+k)
        z = zf(s.neta.to_numpy())
        signos = s.groupby("ins").neta.mean()
        nsig = int((np.sign(signos) == np.sign(s.neta.mean())).sum())
        cstar = s.R.mean() / (1/s.rgo_u).mean()      # coste al que la neta seria cero
        cmed = np.mean([INS[i][2] for i in s.ins])
        print(f"  {regla:>6s} {k:2d} {len(s):5d} {100*ac:8.1f}% {100*geo:6.1f}% "
              f"{100*(ac-geo):+6.1f}pt {s.rgo_u.median():6.1f} "
              f"{100*(cmed/s.rgo_u.median()):5.1f}% {s.neta.mean():+8.3f} {z:+7.2f} "
              f"{nsig:5d}/7 {cstar:7.2f}" + ("  *" if abs(z) > 2.77 and nsig >= 5 else ""))
        res.append((regla,k,z,nsig))
print("\n  * = pasa el umbral firmado (|z| > 2,77 y signo en 5 de 7)")
print(f"  celdas que lo pasan: {sum(1 for _,_,z,n in res if abs(z)>2.77 and n>=5)} de {len(res)}")
