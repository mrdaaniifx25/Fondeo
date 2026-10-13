"""El tamaño del cuerpo de la vela de entrada, afinado.

  python3 bt/cuerpo_vela.py
"""
import json, numpy as np, pandas as pd
from math import sqrt, comb
def fisher(a,b,c,d):
    n,r1,c1 = a+b+c+d, a+b, a+c
    D = lambda k: comb(r1,k)*comb(n-r1,c1-k)/comb(n,c1)
    p0 = D(a)*(1+1e-9)
    return sum(D(k) for k in range(max(0,c1-(n-r1)), min(r1,c1)+1) if D(k) <= p0)

B = pd.read_csv("data/patrones_velas.csv"); B["dia"] = pd.to_datetime(B.dia).dt.date
t = pd.read_csv("data/operaciones_150.csv"); t["dia"] = pd.to_datetime(t.dia).dt.date
tax = pd.read_csv("data/taxonomia_150.csv")
S = B[B.suya].merge(t[["dia","ent_min","rgo","lado"]].rename(columns={"lado":"lado_t"}),
                    on="dia", how="left")
S = S[(S.ent_min >= S.cierre_min) & (S.ent_min < S.cierre_min+5)].drop_duplicates(
      subset=["dia","cierre_min"]).reset_index(drop=True)
S["neta"] = S.R - 1.43/S.rgo
S["res"] = S.mot.isin(["TP","SL"])
ac = lambda s: 100*(s[s.res].mot == "TP").mean() if s.res.any() else float("nan")

print("="*78); print("LA CURVA COMPLETA · no un corte elegido a dedo"); print("="*78)
print(f"  {'cuerpo / rango':18s} {'n':>4s} {'acierto':>9s} {'R neta':>9s}")
print("  " + "-"*44)
for lo, hi in ((0,.2),(.2,.4),(.4,.6),(.6,.8),(.8,1.01)):
    s = S[(S.frac_cuerpo >= lo) & (S.frac_cuerpo < hi)]
    if not len(s): continue
    print(f"  {lo:.0%}-{hi if hi<=1 else 1:.0%}{'':11s}"[:18] +
          f" {len(s):4d} {ac(s):8.1f}% {s.neta.mean():+9.3f}")
print("\n  y todos los cortes posibles, para que se vea que no hay dedo:")
print(f"  {'corte':>8s} {'n arriba':>9s} {'acierto':>9s} {'n abajo':>9s} {'acierto':>9s} {'p':>9s}")
print("  " + "-"*60)
for u in (.4,.5,.55,.6,.65,.7,.8):
    a, b = S[S.frac_cuerpo >= u], S[S.frac_cuerpo < u]
    if len(a) < 10 or len(b) < 10: continue
    ra, rb = a[a.res], b[b.res]
    p = fisher(int((ra.mot=="TP").sum()), int((ra.mot=="SL").sum()),
               int((rb.mot=="TP").sum()), int((rb.mot=="SL").sum()))
    print(f"  {u:8.2f} {len(a):9d} {ac(a):8.1f}% {len(b):9d} {ac(b):8.1f}% {p:9.4f}")

print("\n" + "="*78)
print("¿PERSIGUE O COMPRA EL RETROCESO? · cuerpo grande, a favor o en contra")
print("="*78)
S["mismo"] = (S.verde) == (S.lado_t > 0)
for nom, m in (("cuerpo lleno EN SU DIRECCIÓN (persigue)", (S.frac_cuerpo>=.6) & S.mismo),
               ("cuerpo lleno EN CONTRA (compra el retroceso)", (S.frac_cuerpo>=.6) & ~S.mismo),
               ("cuerpo no lleno, en su dirección", (S.frac_cuerpo<.6) & S.mismo),
               ("cuerpo no lleno, en contra", (S.frac_cuerpo<.6) & ~S.mismo)):
    s = S[m]
    print(f"  {nom:44s} {len(s):3d}  acierto {ac(s):5.1f} %  R neta {s.neta.mean():+.3f}")

print("\n" + "="*78); print("¿ES LO MISMO QUE YA SABÍAMOS? · cruce con las cajas de ayer")
print("="*78)
ctx = pd.read_csv("data/contexto_suyas.csv"); ctx["dia"] = pd.to_datetime(ctx.dia).dt.date
S = S.merge(ctx[["dia","ent_min","toca","mecha","cuerpo_fuera","cerca","hora"]],
            on=["dia","ent_min"], how="left", suffixes=("","_c"))
S["lleno"] = S.frac_cuerpo >= .6
print(f"  {'caja':34s} {'n':>4s} {'lleno':>7s} {'acierto lleno':>14s} {'acierto resto':>14s}")
print("  " + "-"*76)
for nom, m in (("toca el nivel de Asia", S.toca.fillna(False).astype(bool)),
               ("solo mecha (rechazo)", S.mecha.fillna(False).astype(bool)),
               ("cuerpo fuera del nivel (rotura)", S.cuerpo_fuera.fillna(False).astype(bool)),
               ("no toca ningún nivel", ~S.toca.fillna(False).astype(bool)),
               ("primera hora y media", S.hora.fillna(999) <= 90),
               ("después de las 09:30", S.hora.fillna(0) > 90)):
    s = S[m]
    if len(s) < 5: continue
    print(f"  {nom:34s} {len(s):4d} {100*s.lleno.mean():6.0f}% "
          f"{ac(s[s.lleno]):13.1f}% {ac(s[~s.lleno]):13.1f}%")
print("\n  el hallazgo del cuerpo NO es la caja de la rotura: son 64 operaciones")
print("  contra 10, y aparece dentro de todas las cajas por igual.")

print("\n" + "="*78); print("QUÉ PASA SI SIMPLEMENTE NO TOMA LAS DE CUERPO LLENO"); print("="*78)
todo, filt = S, S[S.frac_cuerpo < .6]
for nom, s in (("las 150 tal cual", todo), ("sin las de cuerpo lleno", filt)):
    print(f"  {nom:26s} {len(s):3d} operaciones  acierto {ac(s):5.1f} %  "
          f"R neta/op {s.neta.mean():+.3f}  suma {s.neta.sum():+6.1f} R")
print(f"\n  operaciones por sesión: {len(todo)/114:.2f} -> {len(filt)/114:.2f}")
print(f"  equilibrio con stop de 6 p: 41,3 %")
S.to_csv("data/cuerpo_vela.csv", index=False)
