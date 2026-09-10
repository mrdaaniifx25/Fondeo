"""Las roturas de SU regla en las diez sesiones del bloque 6, con su desenlace.

Su regla, dicha por el: el cuerpo de la ultima vela de M5 cerrada, y entra cuando
una vela de M1 CIERRA pasado ese cuerpo. Stop en el extremo de los ultimos diez
minutos -que es donde lo pone el, medido con 1,3 pips de error- y objetivo 1:2.

Se separan las roturas por al menos SEP minutos, porque dos cierres seguidos
pasado el mismo cuerpo son el mismo movimiento y no dos decisiones.

  python3 bt/roturas_datos.py
"""
import json, numpy as np, pandas as pd
TZ, U, INI, FIN, SEP = "Europe/Madrid", 1e-4, 480, 690, 4
POR_SESION = 25

DIAS = {int(k): pd.Timestamp(v).date() for k, v in json.load(open("data/examen_dias6.json")).items()}
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
m1["dia"] = m1["loc"].dt.date; m1["min"] = m1["loc"].dt.hour*60 + m1["loc"].dt.minute
m1 = m1[m1.dia.isin(set(DIAS.values()))].reset_index(drop=True)

todo = {}
resumen = []
for n, dia in DIAS.items():
    d = m1[m1.dia == dia].sort_values("min").reset_index(drop=True)
    O,H,L,C,M = (d.open.to_numpy(), d.high.to_numpy(), d.low.to_numpy(),
                 d.close.to_numpy(), d["min"].to_numpy())
    b5 = {}
    for i in range(len(d)):
        g = M[i]//5
        if g not in b5: b5[g] = [O[i], H[i], L[i], C[i]]
        else:
            b5[g][1] = max(b5[g][1], H[i]); b5[g][2] = min(b5[g][2], L[i]); b5[g][3] = C[i]
    rot, ultimo, ultLado = [], -99, 0
    for i in range(len(d)):
        m = int(M[i])
        if not (INI <= m <= FIN): continue
        g = m//5 - 1
        if g not in b5: continue
        o5,h5,l5,c5 = b5[g]
        cA, cB = min(o5,c5), max(o5,c5)
        lado = 1 if C[i] > cB else (-1 if C[i] < cA else 0)
        if lado == 0: continue
        if m - ultimo < SEP and lado == ultLado: continue
        ultimo, ultLado = m, lado
        k0 = max(0, i-9)
        ent = float(C[i])
        stp = float(L[k0:i+1].min()) if lado > 0 else float(H[k0:i+1].max())
        rgo = abs(ent-stp)
        if rgo < 1.5*U: continue
        tp = ent + lado*2*rgo
        fin = int(np.searchsorted(M, FIN))
        hh, ll = H[i+1:fin], L[i+1:fin]
        if not len(hh): continue
        largo = lado > 0
        gs, gt = ((ll <= stp, hh >= tp) if largo else (hh >= stp, ll <= tp))
        isl = int(np.argmax(gs)) if gs.any() else 10**9
        itp = int(np.argmax(gt)) if gt.any() else 10**9
        if isl == 10**9 and itp == 10**9:
            sal = float(C[fin-1]); R = ((sal-ent) if largo else (ent-sal))/rgo
            mot, msal = "cierre", FIN
        else:
            R, mot = (-1.0, "SL") if isl <= itp else (2.0, "TP")
            msal = int(M[i+1+min(isl,itp)])
        rot.append(dict(m=m-INI, lado=lado, ent=round(ent,5), sl=round(stp,5),
                        tp=round(tp,5), rgo=round(rgo/U,1), mot=mot,
                        R=round(float(R),2), msal=msal-INI,
                        obA=round(cA,5), obB=round(cB,5)))
    # se submuestrea al azar con semilla fija: 25 por sesion son 250 decisiones,
    # que es muestra de sobra y media hora de trabajo en vez de una entera
    if len(rot) > POR_SESION:
        rng = np.random.default_rng(20260904 + n)
        idx = sorted(rng.choice(len(rot), POR_SESION, replace=False))
        rot = [rot[i] for i in idx]
    todo[n] = rot
    r = [x for x in rot if x["mot"] != "cierre"]
    resumen.append((n, str(dia), len(rot), 100*np.mean([x["mot"]=="TP" for x in r]) if r else np.nan))
json.dump(todo, open("data/roturas6.json","w"))
print(f"{'ses':>4s} {'día':>12s} {'roturas':>8s} {'acierto de la regla':>20s}")
for n, dia, k, a in resumen:
    print(f"{n:4d} {dia:>12s} {k:8d} {a:19.1f} %")
tot = sum(len(v) for v in todo.values())
res = [x for v in todo.values() for x in v if x["mot"] != "cierre"]
print(f"\n{tot} roturas en 10 sesiones · {tot/10:.1f} por sesión")
print(f"acierto de la regla a ciegas: {100*np.mean([x['mot']=='TP' for x in res]):.1f} %")
print(f"R neta media: {np.mean([x['R'] - 1.43/x['rgo'] for v in todo.values() for x in v]):+.3f}")
print(f"stop mediano: {np.median([x['rgo'] for v in todo.values() for x in v]):.1f} p")
print(f"tamaño del JSON: {round(len(json.dumps(todo))/1024)} KB")
