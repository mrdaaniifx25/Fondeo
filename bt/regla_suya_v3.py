"""SU regla v3, escrita desde sus propias palabras del 14 de agosto.

Lo que dijo, literal:
  1 (08:00) "la vela que rompe deja mecha... la siguiente ya es bajista y espero
            a ver como reacciona el precio, aqui no haria entrada"
  2 (08:26) "empezaria a pensar en compras en el momento que el movimiento
            alcista [rompa] el ultimo alto que hay entre las 8 y las 8:30"
  3 (08:45) "cierra por encima pero con POCO CUERPO... esperaria a que el precio
            cerrase con alguna VELA ALCISTA CON CUERPO por encima del nivel"
  4 (09:40) "rompe el ULTIMO ALTO del movimiento alcista entre las 9 - 9:30"

O sea: el nivel de Asia no dispara nada, solo enciende la alarma. El disparo es
una vela CON CUERPO que rompe el ultimo pivote de la estructura reciente, y la
direccion la da el pivote que se rompa primero.

  python3 bt/regla_suya_v3.py
"""
import numpy as np, pandas as pd
TZ, U, INI, FIN = "Europe/Madrid", 1e-4, 480, 690
PIV, CUERPO_MIN = 3, 0.40      # pivote de N velas a cada lado; cuerpo >= 40 % del rango

d = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
               pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
loc = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
d["dia"] = loc.date; d["min"] = loc.hour*60+loc.minute; d["hm"] = loc.strftime("%H:%M")
d = d.reset_index(drop=True)

def corre(piv=PIV, cmin=CUERPO_MIN, una=True):
    out = []
    for dia, g in d.groupby("dia", sort=False):
        g = g.reset_index(drop=True); m = g["min"].to_numpy()
        if (m < INI).sum() < 200 or ((m>=INI)&(m<=FIN)).sum() < 150: continue
        aHi, aLo = g.high[m<INI].max(), g.low[m<INI].min()
        H,L,C,O = (g.high.to_numpy(),g.low.to_numpy(),g.close.to_numpy(),g.open.to_numpy())
        hm = g.hm.to_numpy()
        # la alarma: el primer extremo de Asia que se rompe dentro de la ventana
        rot = np.flatnonzero(((H > aHi) | (L < aLo)) & (m >= INI))
        if not len(rot): continue
        b = int(rot[0])
        # pivotes CAUSALES: un pivote en i no se confirma hasta i+piv
        SH = SL = None
        for k in range(b+1, len(g)):
            if m[k] > FIN: break
            i = k - piv                                   # el que acaba de confirmarse
            if i - piv >= 0:
                if H[i] == H[i-piv:i+piv+1].max(): SH = H[i]
                if L[i] == L[i-piv:i+piv+1].min(): SL = L[i]
            rango = H[k] - L[k]
            if rango <= 0: continue
            cuerpo = abs(C[k]-O[k]) / rango
            if cuerpo < cmin: continue                    # "poco cuerpo" -> no vale
            lado = 0
            if SH is not None and C[k] > SH and C[k] > O[k]: lado = +1
            elif SL is not None and C[k] < SL and C[k] < O[k]: lado = -1
            if lado == 0: continue
            # stop: el pivote contrario vigente
            stop = SL if lado > 0 else SH
            if stop is None: continue
            if (stop >= C[k]) if lado > 0 else (stop <= C[k]): continue
            out.append(dict(dia=str(dia), lado=lado, h_rot=hm[b], h_ent=hm[k],
                            ent=C[k], stop=stop, rgo=abs(stop-C[k])/U))
            if una: break
    return pd.DataFrame(out)

R = corre()
print(f"{len(R)} entradas (una por día)  ·  ventas {(R.lado<0).sum()}  "
      f"compras {(R.lado>0).sum()}  ·  riesgo mediano {R.rgo.median():.1f} p\n")

V = pd.read_csv("data/agosto_verificacion.csv")
V["fecha"] = pd.to_datetime(V.fecha).dt.strftime("%Y-%m-%d")
print("CONTRASTE CON SUS 12 DÍAS\n")
print(f"{'día':<12}{'ÉL':<22}{'LA REGLA v3':<30}")
print("-"*66)
ok = tot = 0
for f, g in V.groupby("fecha"):
    if f > "2026-08-21": continue
    mias = R[R.dia == f]
    suyas = " · ".join(("venta" if r.lado<0 else "compra") for r in g.itertuples())
    reglas = " · ".join(f"{r.h_ent} {'venta' if r.lado<0 else 'compra'} ({r.rgo:.1f}p)"
                        for r in mias.itertuples()) or "— no dispara —"
    marca = ""
    if len(mias):
        tot += 1
        if set(g.lado) & set(mias.lado): ok += 1; marca = "  ✓"
        else: marca = "  ✗"
    print(f"{f:<12}{suyas:<22}{reglas:<30}{marca}")
print(f"\ncoincide el lado en {ok} de {tot}")
