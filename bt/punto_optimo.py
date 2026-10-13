"""Pre-registro docs/PREREGISTRO_punto_optimo.md

Rejilla EXHAUSTIVA del instante de entrada en el CRT: 11 entradas x 4 stops
x 5 objetivos = 220 celdas. El criterio no es "sale alguna positiva" (con 220
siempre sale) sino si la mejor supera E[maximo de 220 celdas de ruido].

Se precalculan los MINIMOS y MAXIMOS acumulados del camino de cada operacion,
asi cada celda se evalua vectorizada en vez de con un bucle por operacion.

  python3 bt/punto_optimo.py
"""
import numpy as np, pandas as pd
from math import sqrt
rng = np.random.default_rng(20261013)

INS = [("EURUSD", "data/eurusd_m1.parquet", 1e-4, 0.70),
       ("oro",    "data/xauusd_m1.parquet", 1e-2, 12.0),
       ("DAX",    "data/grxeur_m1.parquet", 1e-0,  0.8)]
HOR, MAXOP = 240, 7000
ENTRADAS = ([("inmediata", "ya", 0.0)] +
            [(f"retroceso {r:.3f}", "ret", r) for r in (0.25, 0.382, 0.50, 0.618, 0.75)] +
            [(f"espera {n} velas", "esp", n) for n in (1, 2, 3, 4, 6)])
STOPS   = [("mecha", 1.0), ("mecha x1,5", 1.5), ("mecha x2,0", 2.0), ("rango opuesto", -1)]
OBJETIVOS = [("R:R 1,0", 1.0), ("R:R 1,5", 1.5), ("R:R 2,0", 2.0), ("R:R 3,0", 3.0),
             ("rango opuesto", -1)]

def prepara(nom, ruta, U, coste):
    M = pd.read_parquet(ruta); M["ts"] = pd.to_datetime(M["ts"])
    M = M.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    t = (M.ts.dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None))
    g = M.assign(k=t.dt.floor("15min")).groupby("k", sort=True)
    b = g.agg(o=("open","first"), h=("high","max"), l=("low","min"), c=("close","last"))
    b["fin"] = g.apply(lambda x: x.index[-1], include_groups=False).reindex(b.index)
    b = b[b.index.notna()]
    H, L, C, O = (b[k].to_numpy() for k in "hlco")
    ph, pl = np.r_[np.nan, H[:-1]], np.r_[np.nan, L[:-1]]
    up = (L <= pl) & (C > pl) & (C < ph) & (H < ph)
    dn = (H >= ph) & (C < ph) & (C > pl) & (L > pl)
    s = np.where(up, 1, np.where(dn, -1, 0)).astype(np.int8)
    idx = np.nonzero(s)[0]
    idx = idx[(idx > 2) & (idx < len(b) - 8)]
    if len(idx) > MAXOP: idx = idx[np.linspace(0, len(idx)-1, MAXOP).astype(int)]
    FIN = b.fin.to_numpy().astype(int)
    HH, LL, OO = M.high.to_numpy(), M.low.to_numpy(), M.open.to_numpy()
    ts = b.index.to_numpy()
    n = len(idx)
    # para cada operacion: camino de 8 velas M15 (para las ordenes limite) y
    # minimos/maximos acumulados del minuto 0 al 240 desde cada entrada posible
    D = pd.DataFrame({"ins": nom, "ts": ts[idx], "lado": s[idx],
                      "mecha": np.where(s[idx] > 0, L[idx], H[idx]),
                      "cierre": C[idx], "op": ph[idx], "oq": pl[idx],
                      "U": U, "coste": coste})
    D["opuesto"] = np.where(D.lado > 0, D.op, D.oq)
    # apertura de las velas +1..+8 y extremos de cada una, para las limite
    for k in range(1, 9):
        D[f"o{k}"] = O[idx+k]; D[f"h{k}"] = H[idx+k]; D[f"l{k}"] = L[idx+k]
        D[f"e{k}"] = FIN[idx+k-1] + 1          # minuto de apertura de la vela +k
    # caminos: para cada entrada candidata hace falta runmin/runmax desde su minuto
    return D, HH, LL, OO


def camino(HH, LL, e):
    """minimos y maximos acumulados de HOR minutos desde cada e (n x HOR)."""
    n = len(e)
    ix = e[:, None] + np.arange(HOR)[None, :]
    ix = np.clip(ix, 0, len(HH)-1)
    return np.minimum.accumulate(LL[ix], axis=1), np.maximum.accumulate(HH[ix], axis=1)


def primera(run, umbral, mayor):
    """primer indice donde run cruza el umbral; HOR si nunca."""
    hit = (run >= umbral[:, None]) if mayor else (run <= umbral[:, None])
    tiene = hit.any(axis=1)
    return np.where(tiene, hit.argmax(axis=1), HOR)


def z(x, gr):
    m = x.mean()
    su = pd.DataFrame({"x": x, "g": gr}).groupby("g").x.apply(lambda v: (v-m).sum())
    s2 = float((su**2).sum())
    return m*len(x)/sqrt(s2) if s2 > 0 else np.nan


PART = []
for a in INS:
    D, HH, LL, OO = prepara(*a)
    PART.append((D, HH, LL, OO))
    print(f"{a[0]}: {len(D):,} configuraciones CRT")

UMB = float(np.mean(np.abs(rng.standard_normal((200000, 220))).max(axis=1)))
print(f"\nUMBRAL DE SELECCION declarado: E[max |z| de 220 celdas de ruido] = {UMB:.2f}\n")

res = []
for et_e, tipo, par in ENTRADAS:
    # resolver el precio y el minuto de entrada de esta regla, por instrumento
    ENT = []
    for D, HH, LL, OO in PART:
        lado = D.lado.to_numpy()
        if tipo == "ya":
            pe, me, viva = OO[D.e1.to_numpy()], D.e1.to_numpy(), np.ones(len(D), bool)
        elif tipo == "esp":
            k = int(par); pe = OO[D[f"e{k}"].to_numpy()]
            me = D[f"e{k}"].to_numpy(); viva = np.ones(len(D), bool)
        else:
            # limite al retroceso par del tramo mecha->cierre, valida 8 velas
            niv = D.cierre.to_numpy() - lado*par*(D.cierre.to_numpy()-D.mecha.to_numpy())
            me = np.full(len(D), -1); viva = np.zeros(len(D), bool)
            for k in range(1, 9):
                lo, hi = D[f"l{k}"].to_numpy(), D[f"h{k}"].to_numpy()
                toca = (~viva) & ((lo <= niv) if lado[0] >= 0 else (hi >= niv))
                toca = (~viva) & np.where(lado > 0, lo <= niv, hi >= niv)
                me = np.where(toca, D[f"e{k}"].to_numpy(), me); viva |= toca
            pe = niv
        ENT.append((pe, np.where(me < 0, 0, me), viva))
    for et_s, ks in STOPS:
        for et_o, ko in OBJETIVOS:
            R, CR, GR = [], [], []
            for (D, HH, LL, OO), (pe, me, viva) in zip(PART, ENT):
                if viva.sum() < 50: continue
                lado = D.lado.to_numpy()[viva]; ent = pe[viva]
                mecha, opu = D.mecha.to_numpy()[viva], D.opuesto.to_numpy()[viva]
                sl = ent - lado*ks*np.abs(ent-mecha) if ks > 0 else opu*0 + np.where(
                    lado > 0, D.oq.to_numpy()[viva], D.op.to_numpy()[viva])
                rgo = (ent-sl)*lado
                ok = rgo > 0
                if ok.sum() < 50: continue
                tp = (ent + lado*ko*rgo) if ko > 0 else opu
                rec = (tp-ent)*lado
                ok &= rec > 0
                if ok.sum() < 50: continue
                rmin, rmax = camino(HH, LL, me[viva][ok])
                l2, e2 = lado[ok], ent[ok]
                fs = np.where(l2 > 0, primera(rmin, sl[ok], False), primera(rmax, sl[ok], True))
                ft = np.where(l2 > 0, primera(rmax, tp[ok], True), primera(rmin, tp[ok], False))
                rr = rec[ok]/rgo[ok]
                r = np.where(ft < fs, rr, np.where(fs < HOR, -1.0, 0.0))
                R.append(r); CR.append(D.coste.iloc[0]/(rgo[ok]/D.U.iloc[0]))
                GR.append(D.ins.iloc[0] + pd.to_datetime(D.ts.to_numpy()[viva][ok]).strftime("%Y%m%d"))
            if not R: continue
            R, CR = np.concatenate(R), np.concatenate(CR)
            GR = np.concatenate(GR)
            n = R - CR
            res.append((et_e, et_s, et_o, len(R), float(np.mean(R)), float(n.mean()),
                        float(z(n, GR)), float((R > 0).mean()), float(CR.mean())))

T = pd.DataFrame(res, columns="entrada stop objetivo n bruta neta z acierto cr".split())
T = T[T.n >= 300]
print(f"celdas con n>=300: {len(T)} de 220\n")
print("LAS DIEZ MEJORES POR z NETA")
print(f"  {'entrada':<18}{'stop':<14}{'objetivo':<14}{'n':>6}{'acierto':>9}{'coste':>7}"
      f"{'bruta':>9}{'neta':>9}{'z':>7}")
for _, r in T.nlargest(10, "z").iterrows():
    print(f"  {r.entrada:<18}{r.stop:<14}{r.objetivo:<14}{int(r.n):>6}{100*r.acierto:>8.1f}%"
          f"{100*r.cr:>6.1f}%{r.bruta:>+9.4f}{r.neta:>+9.4f}{r.z:>+7.2f}")
print("\nLAS TRES PEORES")
for _, r in T.nsmallest(3, "z").iterrows():
    print(f"  {r.entrada:<18}{r.stop:<14}{r.objetivo:<14}{int(r.n):>6}{100*r.acierto:>8.1f}%"
          f"{100*r.cr:>6.1f}%{r.bruta:>+9.4f}{r.neta:>+9.4f}{r.z:>+7.2f}")
print(f"\n{'='*92}")
print(f"  mejor |z| de las {len(T)} celdas : {T.z.abs().max():.2f}")
print(f"  UMBRAL de seleccion (220 celdas): {UMB:.2f}")
print(f"  celdas con neta > 0             : {int((T.neta>0).sum())} de {len(T)}")
print(f"  celdas con z > +2               : {int((T.z>2).sum())}")
print(f"  VEREDICTO: {'ESPACIO CERRADO' if T.z.max() < UMB else 'REVISAR: supera el umbral'}")
print(f"{'='*92}")
print("\nPOR DIMENSION  ·  z neta mediana")
for col in ("entrada", "stop", "objetivo"):
    print(f"\n  {col}:")
    for k, v in T.groupby(col).z.median().sort_values(ascending=False).items():
        sub = T[T[col] == k]
        print(f"    {k:<18} z mediana {v:>+6.2f}   neta mediana {sub.neta.median():>+8.4f}"
              f"   n medio {int(sub.n.mean()):>5}")
T.to_csv("data/punto_optimo_celdas.csv", index=False)
print("\n  las 220 celdas completas en data/punto_optimo_celdas.csv")
