"""Pre-registro docs/PREREGISTRO_m5_timing.md   (version corregida)

CORRECCION 1 (mira el futuro): la primera version exigia que existiese un FVG
de H1 en las 5 velas posteriores a la finta, y aun asi entraba en B y C ANTES
de que esa vela cerrase. En el 100 % de los casos. B y C ya no piden nada de
H1: se disparan solos con el FVG de la temporalidad menor.

CORRECCION 2 (objetivo ya rebasado): la medicion base usaba abs() para la
distancia al objetivo, asi que admitia entradas con el objetivo ya pasado
-- el 38 % de la muestra, que acertaba el 97 % sola. Aqui el objetivo tiene
que estar por delante del precio de entrada.

A  base H1     entra al cierre de la vela H1 con FVG
B  M5          entra al cierre de la 1a vela M5 con FVG tras cerrar la finta
C  M15         igual con M15
D  filtro M5   precio y stop de A, solo si el FVG de M5 ya existia al entrar
P2 placebo     una vela M5 cualquiera del tramo (sin mirar nada)
P3 placebo     el FVG de M5 al reves

Todo se resuelve en M1, las dos barreras por toque, empate = perdida.
"""
import numpy as np, pandas as pd
from math import sqrt

LIMITE, ESPM, ESPD, ESPF = 0.90, 20, 20, 5
U, COSTE = 1e-4, 1.43
HOR = ESPD * 60
ESP5, ESP15 = 60, 20
M1M = np.timedelta64(1, "m")
rng = np.random.default_rng(23)

def velas(m1, mins):
    g = (m1.set_index("ts").resample(f"{mins}min", label="left", closed="left")
           .agg(h=("high","max"), l=("low","min"), c=("close","last"),
                n=("close","size")).dropna())
    return g[g.n >= mins*0.3].reset_index()

def rma(x, n):
    a = np.full(len(x), np.nan)
    if len(x) < n: return a
    a[n-1] = np.nanmean(x[:n])
    for i in range(n, len(x)): a[i] = (a[i-1]*(n-1) + x[i]) / n
    return a

def huecos(h, l):
    N = len(h); al = np.zeros(N, bool); ba = np.zeros(N, bool)
    al[2:] = l[2:] > h[:-2]; ba[2:] = h[2:] < l[:-2]
    return al, ba

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
mts = m1.ts.to_numpy("datetime64[ns]"); mh = m1.high.to_numpy(); ml = m1.low.to_numpy(); M = len(m1)

def resuelve(t_ent, stop, obj, lado):
    i = int(np.searchsorted(mts, t_ent, "left"))
    for k in range(i, min(i+HOR, M)):
        if lado < 0:
            if mh[k] >= stop: return 0
            if ml[k] <= obj:  return 1
        else:
            if ml[k] <= stop: return 0
            if mh[k] >= obj:  return 1
    return 0

V = velas(m1, 60); V5 = velas(m1, 5); V15 = velas(m1, 15)
ts60 = V.ts.to_numpy("datetime64[ns]"); h, l, c = V.h.to_numpy(), V.l.to_numpy(), V.c.to_numpy(); N = len(V)
ts5  = V5.ts.to_numpy("datetime64[ns]");  h5, l5, c5    = V5.h.to_numpy(), V5.l.to_numpy(), V5.c.to_numpy()
ts15 = V15.ts.to_numpy("datetime64[ns]"); h15, l15, c15 = V15.h.to_numpy(), V15.l.to_numpy(), V15.c.to_numpy()
al5, ba5 = huecos(h5, l5); al15, ba15 = huecos(h15, l15); al60, ba60 = huecos(h, l)

pc = np.roll(c,1); pc[0] = c[0]
tr = np.maximum(h-l, np.maximum(abs(h-pc), abs(l-pc)))
atr = np.roll(rma(tr,14), 1)
n = 8
hi = pd.Series(h).rolling(n).max().to_numpy()
lo = pd.Series(l).rolling(n).min().to_numpy()
ratio = (hi-lo)/(atr*np.sqrt(n))

filas = []; i = n
while i < N-1:
    if not np.isfinite(ratio[i]) or ratio[i] > LIMITE: i += 1; continue
    rHi, rLo = hi[i], lo[i]
    if rHi <= rLo: i += 1; continue
    manip = -1; lado = 0; ext = np.nan; j = i+1
    while j < min(i+1+ESPM, N):
        if h[j] > rHi or l[j] < rLo:
            arr = h[j] > rHi and rLo < c[j] < rHi
            aba = l[j] < rLo and rLo < c[j] < rHi
            if arr or aba: manip = j; lado = -1 if arr else 1; ext = h[j] if arr else l[j]
            break
        j += 1
    if manip < 0: i = max(j, i+1); continue

    obj = rLo if lado < 0 else rHi
    t_finta = ts60[manip] + 60*M1M
    reg = dict(anio=pd.Timestamp(t_finta).year)

    def apunta(tag, P, S, t_ent):
        if not np.isfinite(P) or not np.isfinite(S): return
        if lado < 0 and not (S > P > obj): return     # objetivo POR DELANTE
        if lado > 0 and not (S < P < obj): return
        rgo, rec = abs(S-P), abs(obj-P)
        if rgo <= 0 or rec <= 0: return
        reg[tag] = dict(rgo=rgo/U, rr=rec/rgo, gana=resuelve(t_ent, S, obj, lado),
                        azar=rgo/(rgo+rec))

    # ---- A: FVG de H1, entrada al cierre de esa vela
    kf = -1
    for k in range(manip, min(manip+1+ESPF, N)):
        if (ba60[k] if lado < 0 else al60[k]): kf = k; break
    Ta = None
    if kf >= 0:
        Pa = c[kf]
        Sa = max(ext, h[manip:kf+1].max()) if lado < 0 else min(ext, l[manip:kf+1].min())
        Ta = ts60[kf] + 60*M1M
        apunta("A", Pa, Sa, Ta)

    # ---- menores: el disparo es suyo, no piden nada de H1
    def menor(tag, ts_, h_, l_, c_, al_, ba_, espera, dur, elige):
        i0 = int(np.searchsorted(ts_, t_finta, "left"))
        ib = int(np.searchsorted(ts_, ts60[manip], "left"))
        k = elige(i0, al_, ba_, espera, len(ts_))
        if k < 0 or k >= len(ts_): return None
        P = c_[k]
        S = max(ext, h_[ib:k+1].max()) if lado < 0 else min(ext, l_[ib:k+1].min())
        apunta(tag, P, S, ts_[k] + dur*M1M)
        return ts_[k] + dur*M1M

    def con_fvg(i0, al_, ba_, espera, L):
        for k in range(i0, min(i0+espera, L)):
            if (ba_[k] if lado < 0 else al_[k]): return k
        return -1
    def contra(i0, al_, ba_, espera, L):
        for k in range(i0, min(i0+espera, L)):
            if (al_[k] if lado < 0 else ba_[k]): return k
        return -1
    def al_azar(i0, al_, ba_, espera, L):
        return int(i0 + rng.integers(0, espera))

    t5 = menor("B",  ts5,  h5,  l5,  c5,  al5,  ba5,  ESP5,  5,  con_fvg)
    menor("C",  ts15, h15, l15, c15, al15, ba15, ESP15, 15, con_fvg)
    menor("P2", ts5,  h5,  l5,  c5,  al5,  ba5,  ESP5,  5,  al_azar)
    menor("P3", ts5,  h5,  l5,  c5,  al5,  ba5,  ESP5,  5,  contra)

    # ---- D: la geometria de A, pero solo si el FVG de M5 ya existia al entrar
    if "A" in reg and t5 is not None and Ta is not None and t5 <= Ta:
        reg["D"] = dict(reg["A"])

    if len(reg) > 1: filas.append(reg)
    i = manip+1

# ---------------------------------------------------------------- salida
NOM = {"A":"A  base H1", "B":"B  FVG de M5", "C":"C  FVG de M15",
       "D":"D  filtro M5", "P2":"P2 vela M5 al azar", "P3":"P3 FVG de M5 al reves"}

def saca(tag):
    d = [(f[tag], f["anio"]) for f in filas if tag in f]
    if not d: return None
    D = pd.DataFrame([x for x,_ in d]); D["anio"] = [y for _,y in d]
    D["Rb"] = np.where(D.gana == 1, D.rr, -1.0); D["Rn"] = D.Rb - COSTE/D.rgo
    return D

print(f"\nEURUSD H1 · cajas con finta detectadas: {len(filas):,}\n" + "="*170)
tab = {}
for t in ("A","B","C","D","P2","P3"):
    D = saca(t)
    if D is None or len(D) < 40: continue
    tab[t] = D
    m, ic = D.Rb.mean(), 1.96*D.Rb.std(ddof=1)/sqrt(len(D))
    mn, icn = D.Rn.mean(), 1.96*D.Rn.std(ddof=1)/sqrt(len(D))
    print(f"{NOM[t]:<23} n {len(D):4,}  acierto {100*D.gana.mean():5.1f} % "
          f"(azar {100*D.azar.mean():4.1f}, exceso {100*(D.gana-D.azar).mean():+5.1f})  "
          f"R:R {D.rr.median():4.2f}  riesgo {D.rgo.median():5.1f} p  "
          f"coste {100*(COSTE/D.rgo).median():4.1f} %  "
          f"BRUTA {m:+.4f} [{m-ic:+.4f}, {m+ic:+.4f}]  NETA {mn:+.4f} [{mn-icn:+.4f}, {mn+icn:+.4f}]")

print("\n" + "="*170 + "\ndiferencias emparejadas contra A (solo donde existen las dos)\n" + "="*170)
for t in ("B","C","D"):
    par = [(f["A"], f[t]) for f in filas if "A" in f and t in f]
    if len(par) < 40: continue
    a  = np.array([x["rr"] if x["gana"] else -1.0 for x,_ in par])
    b  = np.array([y["rr"] if y["gana"] else -1.0 for _,y in par])
    an = a - COSTE/np.array([x["rgo"] for x,_ in par])
    bn = b - COSTE/np.array([y["rgo"] for _,y in par])
    ea = np.array([x["gana"]-x["azar"] for x,_ in par])
    eb = np.array([y["gana"]-y["azar"] for _,y in par])
    out = []
    for et, d in (("BRUTA", b-a), ("NETA", bn-an), ("exceso", eb-ea)):
        m, ic = d.mean(), 1.96*d.std(ddof=1)/sqrt(len(d))
        out.append(f"{et} {m:+.4f} [{m-ic:+.4f}, {m+ic:+.4f}]{'  *' if (m-ic)*(m+ic)>0 else ''}")
    print(f"{NOM[t]:<23} n {len(par):4,}   " + "   ".join(out))

print("\nneta media por anio")
print(f"{'anio':>6}" + "".join(f"{t:>9}" for t in tab))
for y in sorted(tab["A"].anio.unique()):
    fila = f"{y:>6}"
    for t in tab:
        s = tab[t][tab[t].anio == y]
        fila += f"{s.Rn.mean():>+9.3f}" if len(s) >= 15 else f"{'.':>9}"
    print(fila)
