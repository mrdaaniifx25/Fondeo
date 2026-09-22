"""ESTRATEGIA EUR/USD - LIQUIDEZ DE SESIONES. Spec del usuario, 22/09/2026.
Pre-registro docs/PREREGISTRO_liquidez_sesiones_v2.md

Secuencia obligatoria (su art. 14):
  NIVEL (PDH/PDL/PSH/PSL) -> SWEEP -> SWEEP H4 -> SWEEP H1 -> ENVOLVENTE M5
"""
import numpy as np, pandas as pd
from math import sqrt

U, COSTE, SPREAD_SL, CONFLU = 1e-4, 1.43, 1.0, 2.0
TZ = "Europe/Madrid"
H4_ATRAS, H1_ATRAS = 6, 6
VENTANAS = {"Londres": (900, 1100), "NuevaYork": (1400, 1630)}
FIN_DIA = 2300
rng = np.random.default_rng(31)

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
L = m1["loc"]; m1["dia"] = L.dt.normalize(); m1["hm"] = L.dt.hour*100 + L.dt.minute
MH, ML, MC = m1.high.to_numpy(), m1.low.to_numpy(), m1.close.to_numpy()
MT = m1["loc"].to_numpy("datetime64[ns]"); MHM = m1.hm.to_numpy(); MDIA = m1.dia.to_numpy()

def velas(mins, ancla=None):
    g = (m1.set_index("loc").resample(f"{mins}min", label="left", closed="left", origin="start_day")
           .agg(o=("open","first"), h=("high","max"), l=("low","min"),
                c=("close","last"), n=("close","size")).dropna())
    g = g[g.n >= max(1, mins*0.3)].reset_index().rename(columns={"loc":"t"})
    g["fin"] = g.t + pd.Timedelta(minutes=mins)
    return g

V5, V60, V240 = velas(5), velas(60), velas(240)
print(f"M1 {len(m1):,}   M5 {len(V5):,}   H1 {len(V60):,}   H4 {len(V240):,}")

# ---------- niveles: PDH/PDL del dia anterior, PSH/PSL de la sesion previa ----
dia = (m1.groupby("dia").agg(h=("high","max"), l=("low","min"), n=("close","size")))
dia = dia[dia.n > 200]
PD = {d: (dia.h.iloc[i-1], dia.l.iloc[i-1]) for i, d in enumerate(dia.index) if i > 0}
asia = m1[m1.hm < 800].groupby("dia").agg(h=("high","max"), l=("low","min"), n=("close","size"))
asia = asia[asia.n > 120]
lon = m1[(m1.hm >= 800) & (m1.hm < 1400)].groupby("dia").agg(h=("high","max"), l=("low","min"), n=("close","size"))
lon = lon[lon.n > 120]

def niveles(d, ses):
    if d not in PD: return []
    pdh, pdl = PD[d]
    S = asia if ses == "Londres" else lon
    if d not in S.index: return []
    psh, psl = float(S.h[d]), float(S.l[d])
    out = [("PDH", pdh, -1), ("PDL", pdl, +1), ("PSH", psh, -1), ("PSL", psl, +1)]
    # confluencia: si el nivel de sesion esta a <= CONFLU pips del PDH/PDL, es el mismo
    fin = []
    for nom, p, lado in out:
        dup = any(abs(p-q)/U <= CONFLU for n2, q, l2, d2 in fin if l2 == lado)
        fin.append((nom, p, lado, dup))
    return fin

# ---------- envolvente M5 (su art. 6) ----------
O5, H5, L5, C5 = (V5[x].to_numpy() for x in ("o","h","l","c"))
T5 = V5.t.to_numpy("datetime64[ns]"); F5 = V5.fin.to_numpy("datetime64[ns]")
HM5 = (pd.DatetimeIndex(V5.t).hour*100 + pd.DatetimeIndex(V5.t).minute).to_numpy()
D5 = pd.DatetimeIndex(V5.t).normalize().to_numpy()

def envolvente(i, lado):
    """lado -1 = short: vela bajista cuyo CUERPO cubre el de la ultima alcista."""
    baj = C5[i] < O5[i]
    if lado < 0 and not baj: return False
    if lado > 0 and C5[i] <= O5[i]: return False
    for j in range(i-1, max(i-13, -1), -1):
        if (C5[j] < O5[j]) == baj: continue        # busca la ultima CONTRARIA
        a, b = min(O5[j], C5[j]), max(O5[j], C5[j])
        return (O5[i] >= b and C5[i] <= a) if lado < 0 else (O5[i] <= a and C5[i] >= b)
    return False

def barre(h, l, c, niv, lado):
    """su art. 3: alcanza el nivel y CIERRA de vuelta dentro."""
    if lado < 0: return (h > niv) and (c < niv)
    return (l < niv) and (c > niv)

def corre(margen, espera, h1_estricto, sin_cadena=False, baraja=False):
    T60, F60 = V60.t.to_numpy("datetime64[ns]"), V60.fin.to_numpy("datetime64[ns]")
    H60, L60, C60 = V60.h.to_numpy(), V60.l.to_numpy(), V60.c.to_numpy()
    HM60 = (pd.DatetimeIndex(V60.t).hour*100 + pd.DatetimeIndex(V60.t).minute).to_numpy()
    T240, F240 = V240.t.to_numpy("datetime64[ns]"), V240.fin.to_numpy("datetime64[ns]")
    H240, L240, C240 = V240.h.to_numpy(), V240.l.to_numpy(), V240.c.to_numpy()
    ops = []
    for d in np.unique(D5):
        perdido = False
        for ses, (a, b) in VENTANAS.items():
            if perdido: break
            NIV = niveles(pd.Timestamp(d), ses)
            if not NIV: continue
            idx = np.where((D5 == d) & (HM5 >= a) & (HM5 < b))[0]
            if len(idx) < 3: continue
            for nom, niv, lado, dup in NIV:
                if dup or perdido: continue
                hecho = False; run = False
                for i in idx:
                    if hecho or run: break
                    # RUN: cierra con el cuerpo claramente fuera -> nivel muerto (art.3)
                    if (lado < 0 and C5[i] > niv) or (lado > 0 and C5[i] < niv): run = True; break
                    if not barre(H5[i], L5[i], C5[i], niv, lado): continue
                    if not sin_cadena:
                        # --- SWEEP H4 del mismo nivel, ya cerrada (art. 4) ---
                        k4 = int(np.searchsorted(F240, T5[i], "right"))
                        if not any(barre(H240[q], L240[q], C240[q], niv, lado)
                                   for q in range(max(0, k4-H4_ATRAS), k4)): continue
                        # --- SWEEP H1, ya cerrada, dentro de la ventana (art. 5) ---
                        k1 = int(np.searchsorted(F60, T5[i], "right"))
                        okh1 = False
                        for q in range(max(0, k1-H1_ATRAS), k1):
                            if not barre(H60[q], L60[q], C60[q], niv, lado): continue
                            if h1_estricto and not (a <= HM60[q] < b): continue
                            okh1 = True; break
                        if not okh1: continue
                    # --- ENVOLVENTE M5 (art. 6) ---
                    ext = H5[i] if lado < 0 else L5[i]
                    for z in range(i, min(i+espera+1, len(V5))):
                        if D5[z] != d or HM5[z] >= b: break
                        ext = max(ext, H5[z]) if lado < 0 else min(ext, L5[z])
                        if z == i or not envolvente(z, lado): continue
                        P = C5[z]
                        S = ext + (SPREAD_SL+margen)*U*(1 if lado < 0 else -1)
                        rgo = abs(S-P)
                        if rgo <= 0: break
                        Ld = lado if not baraja else (1 if rng.random() < .5 else -1)
                        if Ld != lado: S = P + rgo if Ld < 0 else P - rgo
                        O = P - 2*rgo*(1 if Ld < 0 else -1) if Ld < 0 else P + 2*rgo
                        j0 = int(np.searchsorted(MT, F5[z], "left"))
                        jf = np.where((MDIA[j0:] != d) | (MHM[j0:] >= FIN_DIA))[0]
                        j1 = j0 + (int(jf[0]) if len(jf) else len(MT)-j0)
                        j1 = max(j1, j0+1)
                        hh, ll = MH[j0:j1], ML[j0:j1]
                        gt, gs = ((ll <= O, hh >= S) if Ld < 0 else (hh >= O, ll <= S))
                        it = int(np.argmax(gt)) if gt.any() else 10**9
                        isl = int(np.argmax(gs)) if gs.any() else 10**9
                        if it == 10**9 and isl == 10**9:
                            sal = MC[j1-1]; R = ((P-sal) if Ld < 0 else (sal-P))/rgo; mot = "cierre"
                        elif isl <= it: R, mot = -1.0, "SL"
                        else: R, mot = 2.0, "TP"
                        mae = (hh.max()-P if Ld < 0 else P-ll.min())/rgo
                        mfe = (P-ll.min() if Ld < 0 else hh.max()-P)/rgo
                        ops.append(dict(fecha=pd.Timestamp(T5[z]), sesion=ses, nivel=nom,
                                        lado="SHORT" if Ld < 0 else "LONG", entrada=P, sl=S, tp=O,
                                        rgo=rgo/U, R=R, motivo=mot, mae=mae, mfe=mfe,
                                        minutos=int(min(it, isl)) if mot != "cierre" else int(j1-j0)))
                        hecho = True
                        if R < 0: perdido = True          # art. 12
                        break
    if not ops: return pd.DataFrame()
    D = pd.DataFrame(ops)
    D["neto"] = D.R - COSTE/D.rgo
    return D

def ficha(et, D, ind=""):
    if len(D) < 20: return print(f"  {ind}{et:<30} n {len(D):>4}   (insuficiente)")
    cr = (COSTE/D.rgo).mean(); um = 100*(1+cr)/3
    ac = 100*(D.motivo == "TP").mean()
    mn, ic = D.neto.mean(), 1.96*D.neto.std(ddof=1)/sqrt(len(D))
    print(f"  {ind}{et:<30} n {len(D):>4}  riesgo {D.rgo.median():>5.1f}p  coste {100*cr:>5.1f}%  "
          f"acierto {ac:>5.1f}%  umbral {um:>5.1f}  NETA {mn:>+7.4f} [{mn-ic:>+.4f},{mn+ic:>+.4f}]"
          f"{'  CRUZA' if mn-ic > 0 else ''}")
    return D

print("\n" + "="*128)
print("PRINCIPAL declarado en el pre-registro · margen 1 pip · espera 12 velas · H1 estricto")
print("="*128)
P = corre(1.0, 12, True); ficha("PRINCIPAL", P)

print("\n" + "="*128); print("LAS 16 CELDAS"); print("="*128)
for h1e in (True, False):
    for esp in (6, 12):
        for mar in (0.0, 1.0, 2.0, 3.0):
            ficha(f"H1 {'estricto' if h1e else 'laxo':<8} espera {esp:>2} margen {mar:.0f}p",
                  corre(mar, esp, h1e), "  ")
    print()
P.to_csv("data/liquidez_v2_operaciones.csv", index=False)
print(f"\noperaciones del principal volcadas en data/liquidez_v2_operaciones.csv")

# ======================= INFORME COMPLETO (sus art. 15 y 16) =================
LX = corre(1.0, 12, False)          # H1 laxo: la unica celda con potencia
LX.to_csv("data/liquidez_v2_laxo.csv", index=False)

def informe(et, D):
    print("\n" + "="*128); print(f"INFORME · {et}  (art. 15 y 16 de su spec)"); print("="*128)
    n = len(D); tp = (D.motivo == "TP").sum(); sl = (D.motivo == "SL").sum()
    ci = (D.motivo == "cierre").sum()
    cr = (COSTE/D.rgo).mean()
    print(f"  operaciones {n}   TP {tp} ({100*tp/n:.1f} %)   SL {sl} ({100*sl/n:.1f} %)   "
          f"sin resolver al cierre del dia {ci} ({100*ci/n:.1f} %)")
    print(f"  win rate {100*tp/n:.1f} %   loss rate {100*sl/n:.1f} %   "
          f"azar de un 1:2 = 33,3 %   umbral con coste = {100*(1+cr)/3:.1f} %")
    print(f"  R bruta total {D.R.sum():+.1f}   R neta total {D.neto.sum():+.1f}   "
          f"esperanza/op bruta {D.R.mean():+.4f}  neta {D.neto.mean():+.4f}")
    g = D.neto[D.neto > 0].sum(); p = -D.neto[D.neto < 0].sum()
    print(f"  profit factor (neto) {g/p if p else float('inf'):.3f}")
    cum = D.neto.cumsum(); dd = (cum - cum.cummax()).min()
    print(f"  maximo drawdown {dd:+.2f} R")
    s = (D.motivo == "TP").astype(int).to_numpy(); mx_g = mx_p = c_g = c_p = 0
    for x in s:
        if x: c_g += 1; c_p = 0
        else: c_p += 1; c_g = 0
        mx_g = max(mx_g, c_g); mx_p = max(mx_p, c_p)
    print(f"  racha maxima de ganancias {mx_g}   de perdidas {mx_p}")
    print(f"  MAE medio {D.mae.mean():.2f} R   MFE medio {D.mfe.mean():.2f} R   "
          f"duracion mediana {D.minutos.median():.0f} min")
    for k, tit in (("sesion","SESION"), ("lado","DIRECCION"), ("nivel","NIVEL ATACADO")):
        print(f"\n  por {tit}:")
        for x, gg in D.groupby(k):
            print(f"    {str(x):<12} n {len(gg):>4}  TP {100*(gg.motivo=='TP').mean():>5.1f} %  "
                  f"bruta {gg.R.mean():>+7.3f}  neta {gg.neto.mean():>+7.3f}")
    print("\n  por AÑO:")
    for x, gg in D.groupby(D.fecha.dt.year):
        print(f"    {x}         n {len(gg):>4}  TP {100*(gg.motivo=='TP').mean():>5.1f} %  "
              f"neta {gg.neto.mean():>+7.3f}  suma {gg.neto.sum():>+7.1f} R")

informe("H1 LAXO · margen 1p · espera 12  (n con potencia)", LX)
informe("PRINCIPAL declarado · H1 estricto", P)

print("\n" + "="*128); print("PLACEBOS (criterio 4 del pre-registro)"); print("="*128)
ficha("lados barajados", corre(1.0, 12, False, baraja=True))
ficha("SIN la cadena H4+H1", corre(1.0, 12, False, sin_cadena=True))
ficha("la señal completa (referencia)", LX)

print("\n" + "="*128); print("PARTIDO EN DOS MITADES (criterio 3)"); print("="*128)
c = LX.fecha.sort_values().iloc[len(LX)//2]
for et, m in (("1a mitad", LX.fecha < c), ("2a mitad", LX.fecha >= c)):
    ficha(et, LX[m])

# --- lectura alternativa del art. 5: "un maximo RELEVANTE" = cualquier pivote
#     reciente de H1, no forzosamente el mismo nivel de liquidez atacado ------
def corre_h1_pivote(margen, espera, PIV=3):
    T60, F60 = V60.t.to_numpy("datetime64[ns]"), V60.fin.to_numpy("datetime64[ns]")
    H60, L60, C60 = V60.h.to_numpy(), V60.l.to_numpy(), V60.c.to_numpy()
    T240, F240 = V240.t.to_numpy("datetime64[ns]"), V240.fin.to_numpy("datetime64[ns]")
    H240, L240, C240 = V240.h.to_numpy(), V240.l.to_numpy(), V240.c.to_numpy()
    piv_h = np.array([i for i in range(PIV, len(H60)-PIV)
                      if H60[i] == H60[i-PIV:i+PIV+1].max()])
    piv_l = np.array([i for i in range(PIV, len(L60)-PIV)
                      if L60[i] == L60[i-PIV:i+PIV+1].min()])
    ops = []
    for d in np.unique(D5):
        perdido = False
        for ses, (a, b) in VENTANAS.items():
            if perdido: break
            NIV = niveles(pd.Timestamp(d), ses)
            if not NIV: continue
            idx = np.where((D5 == d) & (HM5 >= a) & (HM5 < b))[0]
            if len(idx) < 3: continue
            for nom, niv, lado, dup in NIV:
                if dup or perdido: continue
                hecho = False
                for i in idx:
                    if hecho: break
                    if (lado < 0 and C5[i] > niv) or (lado > 0 and C5[i] < niv): break
                    if not barre(H5[i], L5[i], C5[i], niv, lado): continue
                    k4 = int(np.searchsorted(F240, T5[i], "right"))
                    if not any(barre(H240[q], L240[q], C240[q], niv, lado)
                               for q in range(max(0, k4-H4_ATRAS), k4)): continue
                    # H1: barre CUALQUIER pivote reciente y cierra de vuelta dentro
                    k1 = int(np.searchsorted(F60, T5[i], "right"))
                    ok = False
                    for q in range(max(0, k1-H1_ATRAS), k1):
                        cand = [H60[x] for x in piv_h if x < q and x > q-40] if lado < 0 \
                          else [L60[x] for x in piv_l if x < q and x > q-40]
                        if any(barre(H60[q], L60[q], C60[q], nv, lado) for nv in cand): ok = True; break
                    if not ok: continue
                    ext = H5[i] if lado < 0 else L5[i]
                    for z in range(i, min(i+espera+1, len(V5))):
                        if D5[z] != d or HM5[z] >= b: break
                        ext = max(ext, H5[z]) if lado < 0 else min(ext, L5[z])
                        if z == i or not envolvente(z, lado): continue
                        P = C5[z]; S = ext + (SPREAD_SL+margen)*U*(1 if lado < 0 else -1)
                        rgo = abs(S-P)
                        if rgo <= 0: break
                        O = P - 2*rgo if lado < 0 else P + 2*rgo
                        j0 = int(np.searchsorted(MT, F5[z], "left"))
                        jf = np.where((MDIA[j0:] != d) | (MHM[j0:] >= FIN_DIA))[0]
                        j1 = max(j0 + (int(jf[0]) if len(jf) else len(MT)-j0), j0+1)
                        hh, ll = MH[j0:j1], ML[j0:j1]
                        gt, gs = ((ll <= O, hh >= S) if lado < 0 else (hh >= O, ll <= S))
                        it = int(np.argmax(gt)) if gt.any() else 10**9
                        isl = int(np.argmax(gs)) if gs.any() else 10**9
                        if it == 10**9 and isl == 10**9:
                            sal = MC[j1-1]; R = ((P-sal) if lado < 0 else (sal-P))/rgo; mot = "cierre"
                        elif isl <= it: R, mot = -1.0, "SL"
                        else: R, mot = 2.0, "TP"
                        ops.append(dict(fecha=pd.Timestamp(T5[z]), sesion=ses, nivel=nom,
                                        lado="SHORT" if lado < 0 else "LONG", entrada=P, sl=S,
                                        tp=O, rgo=rgo/U, R=R, motivo=mot, mae=0.0, mfe=0.0,
                                        minutos=int(min(it, isl)) if mot != "cierre" else int(j1-j0)))
                        hecho = True
                        if R < 0: perdido = True
                        break
    D = pd.DataFrame(ops)
    if len(D): D["neto"] = D.R - COSTE/D.rgo
    return D

print("\n" + "="*128)
print("LECTURA ALTERNATIVA DEL ART. 5 · H1 barre CUALQUIER pivote reciente")
print("="*128)
for mar in (0.0, 1.0, 2.0, 3.0):
    ficha(f"pivote H1 · margen {mar:.0f}p", corre_h1_pivote(mar, 12), "  ")
