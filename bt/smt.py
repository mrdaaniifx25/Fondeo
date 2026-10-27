"""Pre-registro docs/PREREGISTRO_smt.md

Divergencia SMT: el EURUSD barre su nivel de Asia y el socio NO.
Se mide la DIFERENCIA entre ese brazo y el brazo sin divergencia, que es
la misma operacion con la misma geometria. Si el SMT es real, A bate a B.
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, TZ = 1e-4, 1.43, "Europe/Madrid"
VENT = {"Londres": (900, 1100), "NuevaYork": (1400, 1630)}
MARGEN, VENTANA_SOCIO, FIN = 1.0, 120, 2300        # 1 pip, 2 h, cierre 23:00

def carga(ruta):
    d = pd.read_parquet(ruta); d["ts"] = pd.to_datetime(d["ts"])
    d = d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    d["loc"] = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
    L = d["loc"]; d["dia"] = L.dt.normalize(); d["hm"] = L.dt.hour*100 + L.dt.minute
    return d

def m5(d):
    g = (d.set_index("loc").resample("5min", label="left", closed="left", origin="start_day")
           .agg(h=("high","max"), l=("low","min"), c=("close","last"), n=("close","size")).dropna())
    g = g[g.n >= 2].reset_index().rename(columns={"loc":"t"})
    g["fin"] = g.t + pd.Timedelta(minutes=5)
    return g

def asia(d):
    a = d[d.hm < 800].groupby("dia").agg(hi=("high","max"), lo=("low","min"), n=("close","size"))
    return a[a.n > 120]

E = carga("data/eurusd_m1.parquet")
SOCIOS = {"DAX": carga("data/grxeur_m1.parquet"), "oro": carga("data/xauusd_m1.parquet")}
E5 = m5(E); AE = asia(E)
print(f"EURUSD M5 {len(E5):,}   dias con Asia {len(AE):,}")

EH, EL, EC = E5.h.to_numpy(), E5.l.to_numpy(), E5.c.to_numpy()
ET = E5.t.to_numpy("datetime64[ns]"); EF = E5.fin.to_numpy("datetime64[ns]")
EHM = (pd.DatetimeIndex(E5.t).hour*100 + pd.DatetimeIndex(E5.t).minute).to_numpy()
ED = pd.DatetimeIndex(E5.t).normalize().to_numpy()
mts = E["loc"].to_numpy("datetime64[ns]"); mh = E.high.to_numpy()
ml = E.low.to_numpy(); mc = E.close.to_numpy()
mhm = E.hm.to_numpy(); mdia = E.dia.to_numpy(); M = len(E)

def prepara_socio(d):
    s5 = m5(d); A = asia(d)
    return (s5.t.to_numpy("datetime64[ns]"), s5.h.to_numpy(), s5.l.to_numpy(), A)

def corre(socio, RR):
    ST, SH, SL, SA = prepara_socio(SOCIOS[socio])
    ops = []
    for d_ in np.unique(ED):
        dd = pd.Timestamp(d_)
        if dd not in AE.index or dd not in SA.index: continue
        ehi, elo = float(AE.hi[dd]), float(AE.lo[dd])
        shi, slo = float(SA.hi[dd]), float(SA.lo[dd])
        for ses, (a, b) in VENT.items():
            idx = np.where((ED == d_) & (EHM >= a) & (EHM < b))[0]
            if len(idx) < 3: continue
            for lado, niv in ((+1, elo), (-1, ehi)):     # +1 = barre minimo -> compra
                hecho = False
                for i in idx:
                    if hecho: break
                    barre = (EL[i] < niv and EC[i] > niv) if lado > 0 else \
                            (EH[i] > niv and EC[i] < niv)
                    if not barre: continue
                    # --- el socio, ¿ha barrido SU nivel en las ultimas 2 h? ---
                    j1 = int(np.searchsorted(ST, ET[i], "right"))
                    j0 = max(0, j1 - VENTANA_SOCIO//5)
                    if j1 <= j0: continue
                    if lado > 0: socio_barre = bool((SL[j0:j1] < slo).any())
                    else:        socio_barre = bool((SH[j0:j1] > shi).any())
                    divergencia = not socio_barre
                    P = EC[i]
                    S = (EL[i] - MARGEN*U) if lado > 0 else (EH[i] + MARGEN*U)
                    rgo = abs(S-P)
                    if rgo <= 0: continue
                    O = P + RR*rgo*lado
                    k0 = int(np.searchsorted(mts, EF[i], "left"))
                    kf = np.where((mdia[k0:] != d_) | (mhm[k0:] >= FIN))[0]
                    k1 = max(k0 + (int(kf[0]) if len(kf) else M-k0), k0+1)
                    hh, ll = mh[k0:k1], ml[k0:k1]
                    gt, gs = ((hh >= O, ll <= S) if lado > 0 else (ll <= O, hh >= S))
                    it = int(np.argmax(gt)) if gt.any() else 10**9
                    isl = int(np.argmax(gs)) if gs.any() else 10**9
                    if it == 10**9 and isl == 10**9:
                        sal = mc[k1-1]; R = ((sal-P) if lado > 0 else (P-sal))/rgo; g = 0
                    elif isl <= it: R, g = -1.0, 0
                    else: R, g = float(RR), 1
                    ops.append(dict(fecha=pd.Timestamp(ET[i]), brazo="A div" if divergencia else "B sin",
                                    lado="compra" if lado > 0 else "venta", rgo=rgo/U,
                                    gana=g, R=R))
                    hecho = True
    D = pd.DataFrame(ops)
    if len(D): D["neto"] = D.R - COSTE/D.rgo
    return D

def compara(et, D, RR, ind="  "):
    if len(D) == 0: return print(f"{ind}{et}: sin operaciones")
    A, B = D[D.brazo == "A div"], D[D.brazo == "B sin"]
    azar = 100/(1+RR)
    if len(A) < 30 or len(B) < 30:
        return print(f"{ind}{et:<26} A n={len(A)}  B n={len(B)}   (insuficiente)")
    aA, aB = 100*A.gana.mean(), 100*B.gana.mean()
    sA = 100*sqrt(A.gana.mean()*(1-A.gana.mean())/len(A))
    sB = 100*sqrt(B.gana.mean()*(1-B.gana.mean())/len(B))
    dif = aA-aB; ee = sqrt(sA**2+sB**2)
    dn = A.neto.mean()-B.neto.mean()
    en = sqrt(A.neto.var(ddof=1)/len(A) + B.neto.var(ddof=1)/len(B))
    flag = "   <<< PASA" if dif-1.96*ee > 0 else ("  (pocas)" if min(len(A),len(B)) < 150 else "")
    print(f"{ind}{et:<26} A n={len(A):>4} {aA:>5.1f}%   B n={len(B):>4} {aB:>5.1f}%   "
          f"azar {azar:.1f}%   DIF {dif:>+6.1f} [{dif-1.96*ee:>+5.1f},{dif+1.96*ee:>+5.1f}]   "
          f"neta {dn:>+7.4f} [{dn-1.96*en:>+.4f},{dn+1.96*en:>+.4f}]{flag}")
    return D

print("\n" + "="*150)
print("PRINCIPAL declarado · socio DAX, R:R 2")
print("="*150)
DP = corre("DAX", 2); compara("DAX · R:R 2", DP, 2)

print("\n" + "="*150); print("LAS 8 CELDAS"); print("="*150)
GUARDA = {}
for socio in ("DAX", "oro"):
    for RR in (1, 2, 3, 5):
        D = corre(socio, RR); GUARDA[(socio, RR)] = D
        compara(f"{socio} · R:R {RR}", D, RR)
    print()

print("="*150); print("PARTIDO EN DOS MITADES · el principal"); print("="*150)
c = DP.fecha.sort_values().iloc[len(DP)//2]
for et, m in (("1a mitad", DP.fecha < c), ("2a mitad", DP.fecha >= c)):
    compara(et, DP[m], 2)

# ---- ampliacion declarada en el pre-registro: cambiar el instrumento operado --
print("\n" + "="*150)
print("AMPLIACION · las seis combinaciones (operado × socio), R:R 2")
print("="*150)
print("  Declarado en el pre-registro: 'habria que replicarlo cambiando el")
print("  instrumento operado'. Es ademas la unica forma de ganar muestra.\n")
TODOS = {"EURUSD": (E, 1e-4, 1.43), "DAX": (SOCIOS["DAX"], 1.0, 1.6),
         "oro": (SOCIOS["oro"], 0.01, 35.0)}
CACHE = {}
def prep(nom):
    if nom not in CACHE:
        d, U_, co = TODOS[nom]
        g = m5(d)
        CACHE[nom] = dict(t=g.t.to_numpy("datetime64[ns]"), fin=g.fin.to_numpy("datetime64[ns]"),
            h=g.h.to_numpy(), l=g.l.to_numpy(), c=g.c.to_numpy(),
            hm=(pd.DatetimeIndex(g.t).hour*100+pd.DatetimeIndex(g.t).minute).to_numpy(),
            dia=pd.DatetimeIndex(g.t).normalize().to_numpy(), A=asia(d), U=U_, co=co,
            mts=d["loc"].to_numpy("datetime64[ns]"), mh=d.high.to_numpy(),
            ml=d.low.to_numpy(), mc=d.close.to_numpy(),
            mhm=d.hm.to_numpy(), mdia=d.dia.to_numpy())
    return CACHE[nom]

def corre2(op, socio, RR=2):
    X, S = prep(op), prep(socio)
    U_, co = X["U"], X["co"]; ops = []
    for d_ in np.unique(X["dia"]):
        dd = pd.Timestamp(d_)
        if dd not in X["A"].index or dd not in S["A"].index: continue
        xhi, xlo = float(X["A"].hi[dd]), float(X["A"].lo[dd])
        shi, slo = float(S["A"].hi[dd]), float(S["A"].lo[dd])
        for a, b in VENT.values():
            idx = np.where((X["dia"] == d_) & (X["hm"] >= a) & (X["hm"] < b))[0]
            if len(idx) < 3: continue
            for lado, niv in ((+1, xlo), (-1, xhi)):
                hecho = False
                for i in idx:
                    if hecho: break
                    barre = (X["l"][i] < niv and X["c"][i] > niv) if lado > 0 else \
                            (X["h"][i] > niv and X["c"][i] < niv)
                    if not barre: continue
                    j1 = int(np.searchsorted(S["t"], X["t"][i], "right"))
                    j0 = max(0, j1 - VENTANA_SOCIO//5)
                    if j1 <= j0: continue
                    sb = bool((S["l"][j0:j1] < slo).any()) if lado > 0 else \
                         bool((S["h"][j0:j1] > shi).any())
                    P = X["c"][i]
                    Sl = (X["l"][i] - MARGEN*U_) if lado > 0 else (X["h"][i] + MARGEN*U_)
                    rgo = abs(Sl-P)
                    if rgo <= 0: continue
                    O = P + RR*rgo*lado
                    k0 = int(np.searchsorted(X["mts"], X["fin"][i], "left"))
                    kf = np.where((X["mdia"][k0:] != d_) | (X["mhm"][k0:] >= FIN))[0]
                    k1 = max(k0 + (int(kf[0]) if len(kf) else len(X["mts"])-k0), k0+1)
                    hh, ll = X["mh"][k0:k1], X["ml"][k0:k1]
                    gt, gs = ((hh >= O, ll <= Sl) if lado > 0 else (ll <= O, hh >= Sl))
                    it = int(np.argmax(gt)) if gt.any() else 10**9
                    isl = int(np.argmax(gs)) if gs.any() else 10**9
                    if it == 10**9 and isl == 10**9:
                        sal = X["mc"][k1-1]; R = ((sal-P) if lado > 0 else (P-sal))/rgo; g_ = 0
                    elif isl <= it: R, g_ = -1.0, 0
                    else: R, g_ = float(RR), 1
                    ops.append(dict(brazo="A div" if not sb else "B sin", gana=g_, R=R,
                                    rgo=rgo/U_, co=co, par=f"{op}/{socio}"))
                    hecho = True
    D = pd.DataFrame(ops)
    if len(D): D["neto"] = D.R - D.co/D.rgo
    return D

TODAS = []
for op in ("EURUSD", "DAX", "oro"):
    for so in ("EURUSD", "DAX", "oro"):
        if op == so: continue
        D = corre2(op, so)
        if len(D): TODAS.append(D); compara(f"{op} / socio {so}", D, 2)
T = pd.concat(TODAS, ignore_index=True)
print("\n  " + "-"*100)
compara("LAS SEIS JUNTAS", T, 2, ind="  ")
A, B = T[T.brazo=="A div"], T[T.brazo=="B sin"]
sA = sqrt(A.gana.mean()*(1-A.gana.mean())/len(A)); sB = sqrt(B.gana.mean()*(1-B.gana.mean())/len(B))
dif = A.gana.mean()-B.gana.mean(); ee = sqrt(sA**2+sB**2)
print(f"\n  diferencia {100*dif:+.2f} puntos, t = {dif/ee:+.2f}")
n = ((1.96+0.84)**2 * 2 * 0.22 / max(dif,1e-6)**2)
print(f"  para resolver una diferencia de ese tamanio harian falta "
      f"~{n:,.0f} operaciones por brazo. Hay {len(A):,}.")
