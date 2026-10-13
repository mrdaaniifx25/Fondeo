"""Como es esto mes a mes, en una cuenta fondeada de 10.000 al 4x.

No estadisticos: el camino. Cuantos meses cobras, cuanto, y que pinta tiene.
"""
import numpy as np, pandas as pd
from math import sqrt
exec(open("bt/sistema.py").read().split('print("="*112); print("EL SISTEMA")')[0])
j = pd.concat([M.rename("m"), K.rename("k")], axis=1).dropna()
SER = 0.5*j.m + 0.5*j.k
BASE = SER.to_numpy()
dd = abs(float(np.min(np.cumsum(BASE)-np.maximum.accumulate(np.cumsum(BASE)))))
rng = np.random.default_rng(1234)
TAM, REP, DD, ESC = 10000, 0.80, 0.08, 4*10/dd
r = BASE*ESC/100.0
print(f"cuenta de {TAM:,} EUR · escala 4x · reparto {100*REP:.0f}% · limite de caida {100*DD:.0f}%\n")

def camino(meses=36):
    bal, pico, pagos = 0.0, 0.0, []
    for m in range(meses):
        bal += rng.choice(r); pico = max(pico, bal)
        if bal <= pico - DD: pagos.append(None); break      # cuenta muerta
        if bal > 0:
            pagos.append(bal*TAM*REP); bal, pico = 0.0, 0.0
        else: pagos.append(0.0)
    return pagos

# --- estadisticas sobre 20.000 caminos ---
vivos, cobros, meses_vivos, todos = 0, [], [], []
for _ in range(20000):
    p = camino()
    murio = p and p[-1] is None
    pag = [x for x in p if x]
    todos += pag
    meses_vivos.append(len(p) - (1 if murio else 0))
    cobros.append(len(pag))
    if not murio: vivos += 1
todos = np.array(todos)
print("EN 36 MESES, SOBRE 20.000 CAMINOS")
print(f"  meses que cobras algo ......... {np.mean(cobros):.0f} de 36  ({100*np.mean(cobros)/36:.0f} %)")
print(f"  cuando cobras, cuanto .........  mediana {np.median(todos):,.0f} EUR  ·  "
      f"media {todos.mean():,.0f} EUR")
print(f"  el cobro mas grande del 10 % ..  {np.percentile(todos,90):,.0f} EUR")
print(f"  la cuenta sigue viva a los 3 años  {100*vivos/20000:.0f} %")
print(f"  si muere, dura ................ {np.median([m for m in meses_vivos if m<36]):.0f} meses de mediana\n")

print("="*96)
print("TRES CAMINOS DE EJEMPLO · lo que verias en tu cuenta, mes a mes")
print("="*96)
rng2 = np.random.default_rng(9)
ejemplos = []
for _ in range(4000):
    p = camino()
    tot = sum(x for x in p if x)
    ejemplos.append((tot, p))
ejemplos.sort(key=lambda e: e[0])
for et, idx in (("UNO MALO (percentil 25)", 1000), ("EL TIPICO (mediana)", 2000),
                ("UNO BUENO (percentil 75)", 3000)):
    tot, p = ejemplos[idx]
    print(f"\n  {et}   ·   total en 3 años: {tot:,.0f} EUR")
    linea = "   "
    for i, x in enumerate(p):
        if x is None: linea += " [MUERE]"; break
        linea += f"{'  ·  ' if x == 0 else f' {x:>4.0f}€'}"
        if (i+1) % 12 == 0: print(linea); linea = "   "
    if linea.strip(): print(linea)
    vivos_m = len([x for x in p if x is not None])
    pag = [x for x in p if x]
    print(f"      {len(pag)} cobros en {vivos_m} meses"
          f"{'  ·  la cuenta murio y hay que comprar otra (89 EUR)' if p[-1] is None else ''}")

print("\n" + "="*104)
print("LO QUE EL PIDIO DE VERDAD: una cuenta que AGUANTE y de para retirar cada mes")
print("="*104)
print("  No es la escala que mas dinero espera. Es otra pregunta distinta.\n")
print(f"{'escala':>7}{'%/año':>8}{'viva a 3 años':>15}{'meses que cobras':>18}"
      f"{'cobro mediano':>15}{'€/mes medio':>13}{'dura (mediana)':>16}")
print("-"*92)
for mult in (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0):
    esc = mult*10/dd; rr = BASE*esc/100.0
    vivos, cob, tot, dur, pagos = 0, [], [], [], []
    for _ in range(20000):
        bal, pico, n, m = 0.0, 0.0, 0, 0
        acum = 0.0
        for m in range(1, 37):
            bal += rng.choice(rr); pico = max(pico, bal)
            if bal <= pico - DD: break
            if bal > 0:
                p = bal*TAM*REP; acum += p; n += 1; pagos.append(p); bal, pico = 0.0, 0.0
        else:
            vivos += 1; m = 36
        cob.append(n/m if m else 0); tot.append(acum); dur.append(m)
    print(f"{mult:>6.2f}x{BASE.mean()*12*esc:>7.1f}%{100*vivos/20000:>14.0f}%"
          f"{100*np.mean(cob):>17.0f}%{np.median(pagos):>14.0f}€"
          f"{np.mean(tot)/36:>12.0f}€{np.median(dur):>15.0f}m")
print("\n  'meses que cobras' = de los meses que la cuenta esta viva")
