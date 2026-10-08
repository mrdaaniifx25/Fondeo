"""SU regla, version 2: la carrera entre el origen y el pico del impulso.

El confirma que opera las dos caras. Entonces, tras romperse el nivel de Asia:

    L = origen del impulso que lo rompio      (minimo, si rompe por arriba)
    P = pico de ese impulso                   (maximo, si rompe por arriba)

    cierre con cuerpo por debajo de L  ->  la rotura fallo    ->  VENTA
    cierre con cuerpo por encima de P  ->  la rotura aguanto  ->  COMPRA

Gana el primero. Es simetrico y no hay que adivinar nada.

  python3 bt/regla_suya_v2.py
"""
import numpy as np, pandas as pd
TZ, U, INI, FIN = "Europe/Madrid", 1e-4, 480, 690
K, P_PIV, MAXESP = 3, 2, 180

d = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
               pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
loc = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
d["dia"] = loc.date; d["min"] = loc.hour*60+loc.minute; d["hm"] = loc.strftime("%H:%M")
d = d.reset_index(drop=True)

def origen(arr, b, K, bajo):
    """Origen del impulso que acaba en la vela b."""
    mejor, imejor, sin = arr[b], b, 0
    for i in range(b-1, -1, -1):
        if (arr[i] < mejor) if bajo else (arr[i] > mejor):
            mejor, imejor, sin = arr[i], i, 0
        else:
            sin += 1
            if sin >= K: break
    return mejor, imejor

def corre():
    out = []
    for dia, g in d.groupby("dia", sort=False):
        g = g.reset_index(drop=True); m = g["min"].to_numpy()
        if (m < INI).sum() < 200 or ((m>=INI)&(m<=FIN)).sum() < 150: continue
        aHi, aLo = g.high[m<INI].max(), g.low[m<INI].min()
        H,L,C,O = (g.high.to_numpy(),g.low.to_numpy(),g.close.to_numpy(),g.open.to_numpy())
        hm = g.hm.to_numpy()
        for arriba in (True, False):
            niv = aHi if arriba else aLo
            rot = (np.flatnonzero((H > niv) & (m>=INI)) if arriba
                   else np.flatnonzero((L < niv) & (m>=INI)))
            if not len(rot): continue
            b = int(rot[0])
            # origen del impulso y, desde ahi, su pico
            Lv, iL = origen(L if arriba else H, b, K, bajo=arriba)
            if b - iL < 2: continue
            # el pico se va actualizando mientras el precio siga extendiendo
            for k in range(b+1, min(b+1+MAXESP, len(g))):
                if m[k] > FIN: break
                Pv = (H[iL:k].max() if arriba else L[iL:k].min())
                cuerpoBajo, cuerpoAlto = min(O[k],C[k]), max(O[k],C[k])
                falla = (C[k] < Lv and cuerpoBajo < Lv) if arriba else (C[k] > Lv and cuerpoAlto > Lv)
                sigue = (C[k] > Pv and cuerpoAlto > Pv) if arriba else (C[k] < Pv and cuerpoBajo < Pv)
                if not (falla or sigue): continue
                lado = (-1 if falla else +1) if arriba else (+1 if falla else -1)
                tipo = "giro" if falla else "continuacion"
                # stop: ultimo pivote en contra antes de entrar
                piv = None
                for i in range(k-P_PIV-1, iL, -1):
                    if i-P_PIV < 0 or i+P_PIV >= len(g): continue
                    ok = (H[i] == H[i-P_PIV:i+P_PIV+1].max() if lado < 0
                          else L[i] == L[i-P_PIV:i+P_PIV+1].min())
                    if ok: piv = i; break
                if piv is None: break
                stop = H[piv] if lado < 0 else L[piv]
                if (stop <= C[k]) if lado < 0 else (stop >= C[k]): break
                out.append(dict(dia=str(dia), lado=lado, tipo=tipo, h_rot=hm[b],
                                h_ent=hm[k], ent=C[k], stop=stop,
                                rgo=abs(stop-C[k])/U))
                break
    return pd.DataFrame(out)

R = corre()
print(f"{len(R)} entradas   ·   giros {(R.tipo=='giro').sum()}   "
      f"continuaciones {(R.tipo=='continuacion').sum()}")
print(f"ventas {(R.lado<0).sum()}  ·  compras {(R.lado>0).sum()}  ·  "
      f"riesgo mediano {R.rgo.median():.1f} p\n")

V = pd.read_csv("data/agosto_verificacion.csv")
V["fecha"] = pd.to_datetime(V.fecha).dt.strftime("%Y-%m-%d")
print("CONTRASTE CON SUS 12 DÍAS DE AGOSTO\n")
print(f"{'día':<12}{'ÉL':<26}{'LA REGLA v2':<44}")
print("-"*82)
ok = tot = 0
for f, g in V.groupby("fecha"):
    if f > "2026-08-21": continue
    mias = R[R.dia == f]
    suyas = " · ".join(("venta" if r.lado < 0 else "compra") for r in g.itertuples())
    reglas = " · ".join(f"{r.h_ent} {'venta' if r.lado<0 else 'compra'} [{r.tipo[:4]}]"
                        for r in mias.itertuples()) or "— no dispara —"
    ladosSuyos = set(g.lado); ladosMios = set(mias.lado)
    marca = ""
    if ladosMios:
        tot += 1
        if ladosSuyos & ladosMios: ok += 1; marca = "  ✓"
        else: marca = "  ✗"
    print(f"{f:<12}{suyas:<26}{reglas:<44}{marca}")
print(f"\ncoincide el lado en {ok} de {tot} días en que la regla dispara")
