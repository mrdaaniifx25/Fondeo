"""La pasada ciega de docs/PREREGISTRO_londres_sesion.md. Se ejecuta UNA vez.

Maquinaria canonica sin tocar. Lo unico nuevo: clasificar cada secuencia por la
hora de Madrid en que cierra su vela de manipulacion.
"""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("XAUUSD","data/res_xauusd_m1.parquet", 0.01, 35.0),
       ("GRXEUR","data/res_grxeur_m1.parquet", 1.0,   2.0)]
TFS = [("H1",1),("H4",4)]
PRINCIPAL = ("H1","LONDRES")
# ventanas en hora de Madrid, tal y como las declara el video
VENT = [("LONDRES", 9.0, 11.0), ("NY", 14.0, 16.5),
        ("CTRL_A",  4.0,  6.0), ("CTRL_B", 19.0, 21.5)]
rng = np.random.default_rng(20260909)

def ventana(ts_utc):
    ce = pd.DatetimeIndex(ts_utc).tz_localize("UTC").tz_convert("Europe/Madrid")
    hh = ce.hour + ce.minute/60
    out = np.full(len(ce), "FUERA", dtype=object)
    for nom, a, b in VENT:
        out[(hh >= a) & (hh < b)] = nom
    return out

filas = []
for tfn, tfh in TFS:
    for nom, ruta, u, co in INS:
        m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
        m1 = m1.sort_values("ts").reset_index(drop=True)
        ref = velas_ref(m1, tfh, ancla_ny=1)
        h,l,c = (ref[x].to_numpy() for x in ("high","low","close"))
        a = C.atr(h,l,c,20)
        s = LM.resuelve(LM.secuencias(ref, usar_cuerpo=False), ref, m1, tfh, a)
        s = s[s.k==1].dropna(subset=["nat","rr"]).copy()
        if s.empty: continue
        # la vela de manipulacion es i_ent; su cierre marca la hora
        s["ts"] = ref["fin"].to_numpy()[s.i_ent.to_numpy().astype(int)]
        s["vent"] = ventana(s.ts)
        s["riesgo_u"] = (s.entrada - s.stop).abs()/u
        s = s[s.riesgo_u > 0]
        s["R"] = np.where(s.nat > 0, s.rr, -1.0)
        s["coste_R"] = co/s.riesgo_u
        s["R_neto"] = s.R - s.coste_R
        filas.append(s.assign(tf=tfn, ins=nom))
D = pd.concat(filas, ignore_index=True)
D.to_csv("data/londres_ciego.csv", index=False)

print("="*104)
print("PASADA CIEGA · docs/PREREGISTRO_londres_sesion.md · una sola vez")
print("  XAUUSD y GRXEUR · enero-julio 2026 · datos nunca abiertos")
print(f"  celda principal declarada: {PRINCIPAL[0]} · {PRINCIPAL[1]} · R BRUTA vs FUERA")
print("="*104)

ORD = ["LONDRES","NY","CTRL_A","CTRL_B","FUERA"]
for tfn,_ in TFS:
    T = D[D.tf==tfn]
    print(f"\n--- {tfn} · n total {len(T):,} " + "-"*62)
    print(f"{'ventana':<9} {'n':>6} {'%':>6} {'acierto':>8} {'R:R':>6} {'riesgo':>9} "
          f"{'coste%R':>8} {'R BRUTA':>9} {'ee':>6} {'R NETA':>9}")
    for v in ORD:
        g = T[T.vent==v]
        if g.empty: continue
        x = g.R.to_numpy()
        print(f"{v:<9} {len(g):>6} {100*len(g)/len(T):>5.1f}% {(x>0).mean():>7.1%} "
              f"{g.rr.median():>6.2f} {g.riesgo_u.median():>9.1f} "
              f"{100*np.median(g.coste_R):>7.1f}% {x.mean():>+9.4f} "
              f"{x.std(ddof=1)/np.sqrt(len(x)):>6.3f} {g.R_neto.mean():>+9.4f}")

print("\n" + "="*104)
print("LA CELDA PRINCIPAL")
T = D[D.tf=="H1"]
L = T[T.vent=="LONDRES"].R.to_numpy(); F = T[T.vent=="FUERA"].R.to_numpy()
dif = L.mean() - F.mean()
se  = np.sqrt(L.var(ddof=1)/len(L) + F.var(ddof=1)/len(F))
print(f"  LONDRES  n {len(L):>5}   bruta {L.mean():+.4f}")
print(f"  FUERA    n {len(F):>5}   bruta {F.mean():+.4f}")
print(f"  DIFERENCIA  {dif:+.4f}   ee {se:.4f}   IC95 [{dif-1.96*se:+.4f}, {dif+1.96*se:+.4f}]"
      f"   z {dif/se:+.2f}")
print(f"  diferencia minima detectable declarada de antemano: +0,24 R")

print("\nLAS CINCO PREDICCIONES DEL PRE-REGISTRO")
mej = {v: T[T.vent==v].R.mean() for v in ORD if len(T[T.vent==v])}
p1 = mej["LONDRES"] > mej["FUERA"]
p2 = all(mej["LONDRES"] >= mej[k] for k in ("CTRL_A","CTRL_B") if k in mej)
p3 = mej["LONDRES"] >= mej.get("NY", -9)
rl = T[T.vent=="LONDRES"].riesgo_u.median(); rf = T[T.vent=="FUERA"].riesgo_u.median()
p4 = abs(rl-rf)/rf <= 0.20
p5 = all(T[T.vent==v].R_neto.mean() < 0 for v in ORD if len(T[T.vent==v]))
print(f"  1 · bruta LONDRES > FUERA ................. {'SÍ' if p1 else 'NO'}   "
      f"({mej['LONDRES']:+.4f} vs {mej['FUERA']:+.4f})")
print(f"  2 · ningun CONTROL supera a LONDRES ....... {'SÍ' if p2 else 'NO'}   "
      + "  ".join(f"{k} {mej[k]:+.4f}" for k in ("CTRL_A","CTRL_B") if k in mej))
print(f"  3 · NY no supera a LONDRES ................ {'SÍ' if p3 else 'NO'}   "
      f"(NY {mej.get('NY', float('nan')):+.4f})")
print(f"  4 · riesgo mediano LONDRES ~ FUERA (±20 %)  {'SÍ' if p4 else 'NO'}   "
      f"({rl:.1f} vs {rf:.1f}, {100*(rl-rf)/rf:+.1f} %)")
print(f"  5 · neta negativa en las cinco ventanas ... {'SÍ' if p5 else 'NO'}")

print("\nLECTURA DECLARADA DE ANTEMANO")
if not p2:
    print("  >> FALSACIÓN. Un control supera a Londres: se esta midiendo la")
    print("     maquinaria, no la sesion. La idea se cierra aqui.")
elif not p1:
    print("  >> FALSACIÓN. Londres no supera a fuera de sesion. La idea se cierra.")
elif dif - 1.96*se > 0:
    print("  >> POSITIVO CON SIGNIFICACIÓN. Exige un efecto de +0,24 R, tres veces")
    print("     el esperado. Se reporta con esa advertencia, no como confirmacion.")
else:
    print("  >> NO CONCLUYENTE. Londres va por delante pero el intervalo incluye")
    print("     el cero, que es lo que el calculo de potencia anticipaba. No es un")
    print("     exito y no se cuenta como tal.")

print("\nPOR INSTRUMENTO · H1 · celda principal")
for ins, g in T[T.vent=="LONDRES"].groupby("ins"):
    f = T[(T.vent=="FUERA") & (T.ins==ins)]
    print(f"  {ins:<8} LONDRES n {len(g):>4} bruta {g.R.mean():+.4f} neta {g.R_neto.mean():+.4f}"
          f"   |  FUERA n {len(f):>5} bruta {f.R.mean():+.4f}")
