"""docs/PREREGISTRO_ob.md, anexo · su definicion: rotura con CUERPO en M1 del
cuerpo de la ultima vela de M5 cerrada.

  python3 bt/ob_rotura.py
"""
import json, numpy as np, pandas as pd
from math import sqrt, comb, erf
TZ, U, INI, FIN = "Europe/Madrid", 1e-4, 480, 690
p2 = lambda z: 2*(1-0.5*(1+erf(abs(z)/sqrt(2))))
def fisher(a,b,c,d):
    n,r1,c1 = a+b+c+d, a+b, a+c
    if min(a,b,c,d) < 0 or n == 0: return 1.0
    D = lambda k: comb(r1,k)*comb(n-r1,c1-k)/comb(n,c1)
    p0 = D(a)*(1+1e-9)
    return sum(D(k) for k in range(max(0,c1-(n-r1)), min(r1,c1)+1) if D(k) <= p0)

t = pd.read_csv("data/operaciones_223.csv"); t["dia"] = pd.to_datetime(t.dia).dt.date
DIAS = {pd.Timestamp(d).date() for d in json.load(open("data/dias_164.json"))}
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(DIAS)].reset_index(drop=True)

filas = []
for dia, d in m1.groupby("dia"):
    d = d.sort_values("min").reset_index(drop=True)
    O,H,L,C,M = (d.open.to_numpy(), d.high.to_numpy(), d.low.to_numpy(),
                 d.close.to_numpy(), d["min"].to_numpy())
    # velas de M5 cerradas: cuerpo de cada una
    b5 = {}
    for i in range(len(d)):
        g = M[i]//5
        if g not in b5: b5[g] = [O[i], H[i], L[i], C[i]]
        else:
            b5[g][1] = max(b5[g][1], H[i]); b5[g][2] = min(b5[g][2], L[i]); b5[g][3] = C[i]
    for i in range(len(d)):
        m = int(M[i])
        if not (INI <= m <= FIN): continue
        g = m//5 - 1                      # la ultima vela de M5 YA cerrada
        if g not in b5: continue
        o5,h5,l5,c5 = b5[g]
        cA, cB = min(o5,c5), max(o5,c5)
        # rotura CON CUERPO: el cierre de M1 queda pasado el cuerpo de la M5
        rompeArriba = C[i] > cB
        rompeAbajo  = C[i] < cA
        # ¿venia de dentro? (el minuto anterior estaba dentro del cuerpo)
        dentroAntes = (cA <= C[i-1] <= cB) if i > 0 else False
        # ¿habia vuelto al cuerpo tras un impulso? (lectura B)
        vuelto = False
        if i >= 6:
            prev = C[max(0,i-15):i]
            vuelto = bool(((prev >= cA) & (prev <= cB)).any() and
                          ((prev > cB).any() or (prev < cA).any()))
        filas.append(dict(dia=dia, min=m, lado=1 if rompeArriba else (-1 if rompeAbajo else 0),
                          dentroAntes=dentroAntes, vuelto=vuelto,
                          cuerpo5=abs(c5-o5)/max(h5-l5,1e-9)*100))
X = pd.DataFrame(filas)
print(f"{len(X):,} minutos en ventana · {X.dia.nunique()} sesiones")

S = t.merge(X, left_on=["dia","ent_min"], right_on=["dia","min"], how="left")
S["res"] = S.mot.isin(["TP","SL"])
ac = lambda s: 100*(s[s.res].mot=="TP").mean() if s.res.any() else float("nan")
A = (S.lado_y == S.lado_x)
B = A & S.vuelto.fillna(False)
ocup = set()
for r in t.itertuples():
    for mm in range(int(r.ent_min), int(r.sal_min)+1): ocup.add((r.dia, mm))
suyas = {(r.dia, int(r.ent_min)) for r in t.itertuples()}
X["suya"] = [(d,m) in suyas for d,m in zip(X.dia, X["min"])]
X["ocup"] = [(d,m) in ocup for d,m in zip(X.dia, X["min"])]
CTL = X[~X.suya & ~X.ocup]

print("\n" + "="*78)
print("SU REGLA: la vela de M1 CIERRA pasado el cuerpo de la última M5 cerrada")
print("="*78)
print(f"  A · rotura en su dirección ....... {100*A.mean():5.1f} % de sus 223 entradas")
print(f"      lo mismo en los controles .... {100*(CTL.lado!=0).mean():5.1f} % de los minutos")
pp = ((A).sum() + (CTL.lado!=0).sum())/(len(S)+len(CTL))
ee = sqrt(pp*(1-pp)*(1/len(S)+1/len(CTL)))
zz = (A.mean() - (CTL.lado!=0).mean())/ee
print(f"      z = {zz:+.2f}   p = {p2(zz):.6f}")
print(f"\n  B · además había vuelto al cuerpo antes ... {100*B.mean():5.1f} % de sus entradas")
print(f"      lo mismo en los controles ............. "
      f"{100*((CTL.lado!=0) & CTL.vuelto).mean():5.1f} %")
print(f"\n  ¿separa sus ganadoras?")
for nom, m in (("A · rompe a su favor", A), ("A · no", ~A),
               ("B · rompe con vuelta", B), ("B · no", ~B)):
    s = S[m]
    print(f"    {nom:24s} n={len(s):3d}  acierto {ac(s):5.1f} %  R neta {s.neta.mean():+.3f}")
a, b = S[A], S[~A]
print(f"    Fisher A: p = {fisher(int((a[a.res].mot=='TP').sum()), int((a[a.res].mot=='SL').sum()), int((b[b.res].mot=='TP').sum()), int((b[b.res].mot=='SL').sum())):.4f}")
a, b = S[B], S[~B]
print(f"    Fisher B: p = {fisher(int((a[a.res].mot=='TP').sum()), int((a[a.res].mot=='SL').sum()), int((b[b.res].mot=='TP').sum()), int((b[b.res].mot=='SL').sum())):.4f}")
S.to_csv("data/ob_rotura.csv", index=False)
X.to_csv("data/ob_rotura_todas.csv.gz", index=False, compression="gzip")
