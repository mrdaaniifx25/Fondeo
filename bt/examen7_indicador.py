"""Las candidatas del indicador para las 40 sesiones del bloque 7, y el sorteo
de en cuales se enseña y en cuales no.

Replica exactamente pine/londres_roturas.pine con sus valores por defecto:
  cuerpo de la ultima M5 CERRADA, roto por el CIERRE de una M1
  filtros: cuerpo M5 < 80 % del rango · stop 4-10 pips · ventana 08:00-11:30
  stop: extremo de los ultimos 10 minutos · objetivo 1:2

El sorteo se hace aqui, con semilla fija, y se guarda ANTES de que el empiece.

  python3 bt/examen7_indicador.py
"""
import json, numpy as np

UMB_CUERPO, STOP_MIN, STOP_MAX, RETRO, RATIO = 80.0, 4.0, 10.0, 10, 2.0
VEN_INI, VEN_FIN = 0, 210            # minutos desde las 08:00 (08:00 a 11:30)
P = 100000.0                          # los precios vienen en enteros x100000
PIP = 10.0                            # 1 pip = 10 unidades de esas

SES = json.load(open("data/examen_sesiones7.json"))
todo = {}
for s in SES:
    m1 = s["m1"]                                   # [min, o, h, l, c] desde -120
    idx = {b[0]: k for k, b in enumerate(m1)}
    O = [b[1] for b in m1]; H = [b[2] for b in m1]
    L = [b[3] for b in m1]; C = [b[4] for b in m1]; M = [b[0] for b in m1]
    # las velas de M5 se arman desde M1, igual que en el grafico
    b5 = {}
    for k in range(len(m1)):
        g = M[k] // 5 if M[k] >= 0 else -((-M[k] + 4) // 5)
        g = M[k] // 5                              # division entera hacia abajo
        if g not in b5: b5[g] = [O[k], H[k], L[k], C[k]]
        else:
            b5[g][1] = max(b5[g][1], H[k]); b5[g][2] = min(b5[g][2], L[k])
            b5[g][3] = C[k]
    cand, ant = [], 0
    for k in range(len(m1)):
        m = M[k]
        g = m // 5 - 1
        if g not in b5:
            ant = 0; continue
        o5, h5, l5, c5 = b5[g]
        cA, cB = min(o5, c5), max(o5, c5)
        roto = 1 if C[k] > cB else (-1 if C[k] < cA else 0)
        nueva = roto != 0 and roto != ant
        ant = roto
        if not nueva: continue
        if not (VEN_INI <= m < VEN_FIN): continue
        rango = max(h5 - l5, 1)
        cuerpo = abs(c5 - o5) / rango * 100
        k0 = max(0, k - RETRO + 1)
        stp = min(L[k0:k+1]) if roto > 0 else max(H[k0:k+1])
        pips = abs(C[k] - stp) / PIP
        obj = C[k] + roto * RATIO * (C[k] - stp)
        pasa = (cuerpo < UMB_CUERPO) and (STOP_MIN <= pips <= STOP_MAX)
        cand.append(dict(m=m, lado=roto, ent=C[k], sl=int(round(stp)),
                         tp=int(round(obj)), pips=round(pips, 1),
                         cuerpo=round(cuerpo), pasa=bool(pasa),
                         obA=cA, obB=cB))
    todo[s["n"]] = cand

# ─── el sorteo: mitad con indicador, mitad sin ──────────────────────────────
rng = np.random.default_rng(20260905)
ns = sorted(todo.keys())
orden = rng.permutation(len(ns))
con = set(int(ns[i]) for i in orden[:len(ns)//2])
asig = {str(n): (n in con) for n in ns}
json.dump({"cand": {str(k): v for k, v in todo.items()}, "con": asig},
          open("data/examen7_ind.json", "w"), separators=(",", ":"))

flechas = [sum(1 for c in v if c["pasa"]) for v in todo.values()]
grises  = [sum(1 for c in v if not c["pasa"]) for v in todo.values()]
print(f"{len(todo)} sesiones  ·  {sum(con.__contains__(n) for n in ns)} CON indicador"
      f"  ·  {len(ns)-len(con)} SIN")
print(f"  flechas (pasan los filtros) por sesión: media {np.mean(flechas):.1f}"
      f"  ·  mediana {np.median(flechas):.0f}  ·  de {min(flechas)} a {max(flechas)}")
print(f"  grises  (no pasan)         por sesión: media {np.mean(grises):.1f}")
print(f"  roturas totales por sesión: media {np.mean(flechas)+np.mean(grises):.1f}")
print(f"\n  con indicador: {sorted(con)}")
print(f"  sin indicador: {sorted(set(ns)-con)}")
