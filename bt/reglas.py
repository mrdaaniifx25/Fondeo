"""El plan bajo distintos juegos de reglas, porque no puedo verificar las de
FundingPips desde aqui (la politica de red solo deja pasar GitHub).

Se busca ademas la ESCALA OPTIMA bajo cada juego, porque un limite de caida
mas estrecho la empuja hacia abajo.
"""
import numpy as np, pandas as pd
from math import sqrt, erf
exec(open("bt/sistema.py").read().split('print("="*112); print("EL SISTEMA")')[0])
j = pd.concat([M.rename("m"), K.rename("k")], axis=1).dropna()
SER = 0.5*j.m + 0.5*j.k
BASE = SER.to_numpy(); REC = SER[SER.index.year >= 2013].to_numpy()
dd = abs(float(np.min(np.cumsum(BASE)-np.maximum.accumulate(np.cumsum(BASE)))))
rng = np.random.default_rng(404)
REP, SIMS, MESES, CUOTA, TAM = 0.80, 6000, 48, 89.0, 10000

REGLAS = {
 "A · lo que simulé":        dict(f1=.08, f2=.04, dd=.10, dia=.05),
 "B · FundingPips 2 fases":  dict(f1=.08, f2=.05, dd=.08, dia=.04),
 "C · más duro aún":         dict(f1=.10, f2=.05, dd=.06, dia=.04),
}

def carrera(serie, esc, R, n_cuentas=4):
    r = serie*esc/100.0
    vol_d = r.std()/sqrt(21)
    p_dia = min(1.0, 21*0.5*(1-erf(R["dia"]/(vol_d*sqrt(2)))))
    llega = 0; rentas = []; gastos = []
    for _ in range(SIMS):
        caja = CUOTA*n_cuentas; gast = 0.0; cts = []; renta = []
        for m in range(MESES):
            while caja >= CUOTA and len(cts) < n_cuentas:
                caja -= CUOTA; gast += CUOTA
                cts.append([1, 0.0, 0.0, False])          # fase, bal, pico, refund
            cobro = 0.0
            for c in cts:
                if rng.random() < p_dia: c[0] = -1; continue
                c[1] += rng.choice(r); c[2] = max(c[2], c[1])
                lim = -R["dd"] if c[0] <= 2 else c[2]-R["dd"]
                if c[1] <= lim: c[0] = -1; continue
                if c[0] == 1 and c[1] >= R["f1"]: c[0], c[1], c[2] = 2, 0.0, 0.0
                elif c[0] == 2 and c[1] >= R["f2"]: c[0], c[1], c[2] = 3, 0.0, 0.0
                elif c[0] == 3 and c[1] > 0:
                    p = c[1]*TAM*REP; c[1], c[2] = 0.0, 0.0
                    if not c[3]: p += CUOTA; c[3] = True
                    cobro += p
            cts = [c for c in cts if c[0] > 0]
            renta.append(cobro)
            if len(cts) < n_cuentas: caja += cobro
        r12 = np.mean(renta[-12:])
        if max(np.mean(renta[i:i+12]) for i in range(len(renta)-11)) >= 300: llega += 1
        rentas.append(r12); gastos.append(gast)
    return 100*llega/SIMS, np.median(rentas), np.mean(gastos)

for et_s, serie in (("MUESTRA COMPLETA", BASE), ("SOLO 2013-2026", REC)):
    print("="*104)
    print(f"{et_s} · cuatro cuentas de 10.000 € · 48 meses · {SIMS:,} carreras")
    print("="*104)
    print(f"{'reglas':<26}{'escala':>8}{'caída hist.':>13}{'%/año':>9}"
          f"{'llega a 300€':>14}{'renta mediana':>16}{'retos':>9}")
    print("-"*95)
    for et, R in REGLAS.items():
        mejor = None
        for mult in (1, 2, 3, 4, 5, 6, 8):
            esc = mult*10/dd
            pct, ren, ga = carrera(serie, esc, R)
            if mejor is None or pct > mejor[1] + 1e-9: mejor = (mult, pct, ren, ga, esc)
            print(f"{(et if mult == 1 else ''):<26}{mult:>7}x{10*mult:>12.0f}%"
                  f"{serie.mean()*12*esc:>8.1f}%{pct:>13.1f}%{ren:>15.0f}€{ga:>8.0f}€")
        print(f"{'':<26}{'óptimo -> ' + str(mejor[0]) + 'x':>29}"
              f"{'':>9}{mejor[1]:>13.1f}%{mejor[2]:>15.0f}€")
        print()
