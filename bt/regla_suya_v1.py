"""SU regla, LOS DOS LADOS, contrastada con sus operaciones reales de agosto."""
import numpy as np, pandas as pd
TZ, U, INI, FIN = "Europe/Madrid", 1e-4, 480, 690

d = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
               pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
d["ts"] = pd.to_datetime(d["ts"]); d = d.sort_values("ts").drop_duplicates("ts")
loc = pd.DatetimeIndex(d.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
d["dia"] = loc.date; d["min"] = loc.hour*60+loc.minute; d["hm"] = loc.strftime("%H:%M")
d = d.reset_index(drop=True)

def origen(arr, b, K, bajo=True):
    mejor, imejor, sin = arr[b], b, 0
    for i in range(b-1, -1, -1):
        if (arr[i] < mejor) if bajo else (arr[i] > mejor):
            mejor, imejor, sin = arr[i], i, 0
        else:
            sin += 1
            if sin >= K: break
    return mejor, imejor

def corre(K=3, P=2, maxEsp=180):
    out = []
    for dia, g in d.groupby("dia", sort=False):
        g = g.reset_index(drop=True); m = g["min"].to_numpy()
        if (m < INI).sum() < 200 or ((m>=INI)&(m<=FIN)).sum() < 150: continue
        aHi, aLo = g.high[m<INI].max(), g.low[m<INI].min()
        H,L,C,O = (g.high.to_numpy(),g.low.to_numpy(),g.close.to_numpy(),g.open.to_numpy())
        hm = g.hm.to_numpy()
        for lado in (-1, +1):
            # lado -1: rompe el maximo de Asia -> se busca VENTA
            # lado +1: rompe el minimo de Asia -> se busca COMPRA
            rot = (np.flatnonzero((H > aHi) & (m>=INI)) if lado < 0
                   else np.flatnonzero((L < aLo) & (m>=INI)))
            if not len(rot): continue
            b = int(rot[0])
            niv, iN = origen(L if lado<0 else H, b, K, bajo=lado<0)
            if b - iN < 2: continue
            ent = None
            for k in range(b+1, min(b+1+maxEsp, len(g))):
                if m[k] > FIN: break
                cuerpo = min(O[k],C[k]) if lado<0 else max(O[k],C[k])
                if (C[k] < niv and cuerpo < niv) if lado<0 else (C[k] > niv and cuerpo > niv):
                    ent = k; break
            if ent is None: continue
            piv = None
            for i in range(ent-P-1, iN, -1):
                if i-P < 0 or i+P >= len(g): continue
                ok = H[i] == H[i-P:i+P+1].max() if lado<0 else L[i] == L[i-P:i+P+1].min()
                if ok: piv = i; break
            if piv is None: continue
            stop = H[piv] if lado<0 else L[piv]
            if (stop <= C[ent]) if lado<0 else (stop >= C[ent]): continue
            out.append(dict(dia=str(dia), lado=lado, h_rot=hm[b], h_ent=hm[ent],
                            ent=C[ent], stop=stop, rgo=abs(stop-C[ent])/U))
    return pd.DataFrame(out)

R = corre()
print(f"{len(R)} entradas · ventas {(R.lado<0).sum()} · compras {(R.lado>0).sum()}")
print(f"riesgo mediano {R.rgo.median():.1f} p\n")

# --- contraste con SUS operaciones de agosto -------------------------------
V = pd.read_csv("data/agosto_verificacion.csv")
V["fecha"] = pd.to_datetime(V.fecha).dt.strftime("%Y-%m-%d")
print("SUS OPERACIONES DE AGOSTO contra lo que da la regla codificada\n")
print(f"{'día':<12}{'ÉL':<34}{'LA REGLA CODIFICADA':<34}")
print("-"*60)
for f, g in V.groupby("fecha"):
    mias = R[R.dia == f]
    suyas = " · ".join(f"{'venta' if r.lado<0 else 'compra'} {r.rgo:.1f}p"
                       for r in g.itertuples())
    reglas = (" · ".join(f"{r.h_ent} {'venta' if r.lado<0 else 'compra'} ({r.rgo:.1f}p)"
                         for r in mias.itertuples()) or "— no dispara —")
    print(f"{f:<12}{suyas:<34}{reglas:<34}")
