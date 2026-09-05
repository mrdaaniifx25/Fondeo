"""La estrategia del grupo de WhatsApp, reconstruida de 20 transcripciones.

Toda la estrategia usa UNA primitiva -el fair value gap- a cuatro escalas:

  SESGO        FVGs de H4/H1: cuales se respetan y cuales se invalidan
  DOL          nivel de liquidez sin barrer EN LOS DOS indices
  CONFLUENCIA  tapeo de FVG de M15 o M5, vale en cualquiera de los dos
  GATILLO      invalidacion de FVG en M1-M5, en el activo que se opera

Especificacion en docs/NASDAQ_grupo_ESPECIFICACION.md
Preregistro sellado en docs/PREREGISTRO_grupo_nasdaq.md (commit 6011c5b)

Para que sea causal, de cada FVG se precalcula UNA VEZ el minuto en que
se tapea por primera vez y el minuto en que se invalida. El estado en
cualquier instante es entonces una comparacion, no un rescaneo.

  python3 bt/grupo_nasdaq.py
"""
import numpy as np, pandas as pd

COSTE = {"NASDAQ": 1.50, "SP500": 0.50}     # estimados, no medidos
RUTA  = {"NASDAQ": "data/nsxusd_m1.parquet",
         "SP500":  "data/spxusd_m1.parquet"}
VIG_CONF = 30        # minutos que vale el tapeo de M15/M5 para disparar
TOPE_R   = 4.0       # DOL mas lejos de esto no se considera objetivo
VIDA     = 240       # minutos que vive la operacion
ESCANEO  = 20*1440   # cuanto se mira hacia delante para tapeo/invalidacion
INF      = np.datetime64("2100-01-01T00:00:00","ns")   # ns: con
                                                       # precision de dia
                                                       # se truncaban los
                                                       # minutos de tapeo

def carga(nom):
    d = pd.read_parquet(RUTA[nom])
    d["ts"] = pd.to_datetime(d["ts"])
    d = d.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    return d.rename(columns={"open":"o","high":"h","low":"l","close":"c"})

def agrega(d, m):
    g = (d.set_index("ts").resample(f"{m}min", label="left", closed="left")
         .agg(o=("o","first"), h=("h","max"), l=("l","min"),
              c=("c","last"), n=("c","size")).dropna())
    g = g[g.n >= max(1, m*0.4)].reset_index()
    g["fin"] = g.ts + pd.Timedelta(minutes=m)     # cuando se conoce entera
    return g

def fvgs(g, M):
    """FVGs de tres velas, con el minuto de primer tapeo y el de
    invalidacion ya resueltos. La invalidacion exige cierre al otro lado
    Y que la vela que lo hace sea del color de la rotura (regla nº19)."""
    h, l, fin = g.h.to_numpy(), g.l.to_numpy(), g.fin.to_numpy()
    br = []
    for i in range(2, len(g)):
        if   l[i] > h[i-2]: br.append((fin[i], +1, h[i-2], l[i]))
        elif h[i] < l[i-2]: br.append((fin[i], -1, h[i],   l[i-2]))
    if not br:
        return pd.DataFrame(columns=["t","lado","lo","hi","tap","inv"])
    F = pd.DataFrame(br, columns=["t","lado","lo","hi"])
    mt = M.ts.to_numpy(); mh = M.h.to_numpy(); ml = M.l.to_numpy()
    mo = M.o.to_numpy(); mc = M.c.to_numpy(); n = len(mt)
    tap = np.full(len(F), INF, dtype="datetime64[ns]")
    inv = np.full(len(F), INF, dtype="datetime64[ns]")
    for k,(t,lado,lo,hi) in enumerate(F[["t","lado","lo","hi"]].itertuples(index=False)):
        a = int(np.searchsorted(mt, np.datetime64(t), side="left"))
        b = min(n, a+ESCANEO)
        if a >= b: continue
        H,L,O,C = mh[a:b], ml[a:b], mo[a:b], mc[a:b]
        m1 = (H >= lo) & (L <= hi)
        if m1.any(): tap[k] = mt[a+int(np.argmax(m1))]
        m2 = ((C < lo) & (C < O)) if lado > 0 else ((C > hi) & (C > O))
        if m2.any(): inv[k] = mt[a+int(np.argmax(m2))]
    F["tap"], F["inv"] = tap, inv
    return F

def recorta(F, a, b):
    """Solo los FVGs que pueden importar en [a,b]. Los arrays pasan de
    miles de filas a decenas, que es lo que hace el backtest viable."""
    if not len(F): return None
    t = F.t.to_numpy()
    m = (t >= a) & (t <= b)
    if not m.any(): return None
    return (t[m], F.lado.to_numpy()[m], F.lo.to_numpy()[m],
            F.hi.to_numpy()[m], F.tap.to_numpy()[m], F.inv.to_numpy()[m])

def serie_sesgo(P4, P1, rejilla):
    """ALCISTA = se invalidan los FVGs bajistas y se respetan los alcistas.
    Recibe los FVGs ya recortados a la ventana."""
    v = np.zeros(len(rejilla))
    for P, dias in ((P4, 5), (P1, 2)):
        if P is None: continue
        t, lado, _, _, tap, inv = P
        vent = np.timedelta64(dias*1440, "m")
        for k, ah in enumerate(rejilla):
            m = (t <= ah) & (t >= ah - vent)
            if not m.any(): continue
            yai = inv <= ah
            v[k] += -lado[m & yai].sum() + lado[m & (~yai) & (tap <= ah)].sum()
    return np.sign(v).astype(int)

VENTANAS = [("FRANKFURT","Europe/Madrid",   8, 0,  9, 0),
            ("LONDRES",  "Europe/Madrid",   9, 0, 10, 0),
            ("NUEVAYORK","America/New_York",9,30, 11,30)]

def sesiones(dia):
    ini = pd.Timestamp(dia)
    return {"asia":    (ini,                          ini+pd.Timedelta(hours=8)),
            "londres": (ini+pd.Timedelta(hours=8),    ini+pd.Timedelta(hours=16.5)),
            "nyprev":  (ini-pd.Timedelta(hours=9.5),  ini-pd.Timedelta(hours=3))}

def corre(op, otro, verbose=True):
    """op = instrumento en el que se entra; otro = el correlacionado."""
    Ma, Mb = carga(op), carga(otro)
    F4 = fvgs(agrega(Ma,240), Ma)
    F1 = fvgs(agrega(Ma, 60), Ma)
    # confluencia: FVGs de M15 y M5 de LOS DOS indices
    CONF = [fvgs(agrega(M,m), M) for M in (Ma,Mb) for m in (15,5)]
    # gatillo: FVGs de M5..M1 SOLO del activo operado  (regla nº18)
    GAT  = {m: fvgs(agrega(Ma,m), Ma) for m in (5,3,2,1)}
    if verbose:
        print(f"  {op}: H4 {len(F4)} FVGs · H1 {len(F1)} · "
              f"confluencia {sum(len(c) for c in CONF)} · "
              f"gatillo {sum(len(g) for g in GAT.values())}")

    mt = Ma.ts.to_numpy(); mh = Ma.h.to_numpy(); ml = Ma.l.to_numpy()
    mo = Ma.o.to_numpy(); mc = Ma.c.to_numpy()
    bt = Mb.ts.to_numpy(); bh = Mb.h.to_numpy(); bl = Mb.l.to_numpy()

    filas = []
    dias = pd.Index(pd.Series(Ma.ts).dt.normalize().unique())
    for dia in dias:
        for nom, tz, h1, m1, h2, m2 in VENTANAS:
            try:
                A = (pd.Timestamp(dia.date(), tz=tz)+pd.Timedelta(hours=h1,minutes=m1)
                     ).tz_convert("UTC").tz_localize(None)
                B = (pd.Timestamp(dia.date(), tz=tz)+pd.Timedelta(hours=h2,minutes=m2)
                     ).tz_convert("UTC").tz_localize(None)
            except Exception: continue
            i0 = int(np.searchsorted(mt, np.datetime64(A), "left"))
            i1 = int(np.searchsorted(mt, np.datetime64(B), "left"))
            if i1 - i0 < 20: continue

            a5 = np.datetime64(A) - np.timedelta64(5*1440,"m")
            a2 = np.datetime64(A) - np.timedelta64(2*1440,"m")
            aC = np.datetime64(A) - np.timedelta64(400,"m")
            aG = np.datetime64(A) - np.timedelta64(90,"m")
            bB = np.datetime64(B)
            P4 = recorta(F4, a5, bB); P1 = recorta(F1, a2, bB)
            if P4 is None and P1 is None: continue
            PC = [p for p in (recorta(F, aC, bB) for F in CONF) if p is not None]
            PG = {m: recorta(GAT[m], aG, bB) for m in (5,3,2,1)}
            if not PC: continue

            rej = mt[i0:i1]
            S = serie_sesgo(P4, P1, rej)

            # niveles del dia, calculados con lo anterior a la ventana
            d0 = np.datetime64(pd.Timestamp(dia))
            niv = []
            for a,b in sesiones(dia).values():
                a,b = np.datetime64(a), np.datetime64(min(b, A))
                j0,j1 = np.searchsorted(mt,a,"left"), np.searchsorted(mt,b,"left")
                if j1-j0 > 5:
                    niv.append((float(mh[j0:j1].max()), +1))
                    niv.append((float(ml[j0:j1].min()), -1))
            if not niv: continue

            for k in range(5, i1-i0):
                s = int(S[k])
                if s == 0: continue
                ah = mt[i0+k]; px = float(mc[i0+k])
                o1 = float(mo[i0+k])
                if s > 0 and not (px > o1): continue      # vela del color
                if s < 0 and not (px < o1): continue

                # confluencia: algun FVG de M15/M5 tapeado hace poco
                lim = ah - np.timedelta64(VIG_CONF+180, "m")
                hay = False
                for t, _, _, _, tp, _ in PC:
                    if ((t <= ah) & (tp <= ah) & (tp >= lim)).any(): hay = True; break
                if not hay: continue

                # gatillo: IFVG contrario al sesgo, mayor TF, invalidado AQUI
                disp = None
                for m in (5,3,2,1):
                    P = PG[m]
                    if P is None: continue
                    t, ld, _, _, _, iv = P
                    if ((t <= ah) & (ld == -s) & (iv == ah)).any(): disp = m; break
                if disp is None: continue

                # stop al extremo de la induccion (nº9)
                j = max(i0, i0+k-30)
                ext = float(ml[j:i0+k+1].min()) if s>0 else float(mh[j:i0+k+1].max())
                rgo = abs(px-ext)
                if rgo <= 0: continue

                # DOL: mas cercano en la direccion, sin barrer en LOS DOS
                cand = []
                for nv, ld in niv:
                    if ld != s or (nv-px)*s <= 0: continue
                    ja = int(np.searchsorted(mt, d0, "left"))
                    jb = i0+k+1
                    if s>0 and mh[ja:jb].max() >= nv: continue
                    if s<0 and ml[ja:jb].min() <= nv: continue
                    ka = int(np.searchsorted(bt, d0, "left"))
                    kb = int(np.searchsorted(bt, ah, "right"))
                    if kb>ka:
                        if s>0 and bh[ka:kb].max() >= nv: continue
                        if s<0 and bl[ka:kb].min() <= nv: continue
                    cand.append(nv)
                dol = (min(cand) if s>0 else max(cand)) if cand else None
                rr = (abs(dol-px)/rgo) if dol is not None else np.nan

                filas.append(dict(instr=op, ventana=nom, ts=pd.Timestamp(ah),
                                  lado=s, ent=px, stp=ext, rgo=rgo, tf=disp,
                                  rr_dol=rr, i=i0+k))
                break        # una operacion por ventana
    return pd.DataFrame(filas), Ma

def smt(Ma, Mb, i, ts, lado):
    """Divergencia: uno de los dos hace un extremo contrario al trade que
    el otro NO hace. Es la definicion que el usa (nº2, nº11, nº12)."""
    mt=Ma.ts.to_numpy(); bt=Mb.ts.to_numpy()
    def hizo(M, T, t):
        j = int(np.searchsorted(T, np.datetime64(t), "right"))
        a, b = max(0,j-15), max(0,j-75)
        if a-b < 10 or j-a < 5: return None
        H=M.h.to_numpy(); L=M.l.to_numpy()
        return (H[a:j].max() > H[b:a].max()) if lado<0 else (L[a:j].min() < L[b:a].min())
    x, y = hizo(Ma,mt,ts), hizo(Mb,bt,ts)
    return None if x is None or y is None else (x != y)

def resuelve(Ma, T):
    """R de cada variante. Si no resuelve en VIDA minutos se marca a
    mercado: tirarlas sesgaria contra el objetivo lejano."""
    mt=Ma.ts.to_numpy(); mh=Ma.h.to_numpy(); ml=Ma.l.to_numpy(); mc=Ma.c.to_numpy()
    n=len(mt); out={"A":[], "B":[], "EL":[]}
    for r in T.itertuples():
        i, s, ent, stp, rgo = int(r.i), r.lado, r.ent, r.stp, r.rgo
        rr = r.rr_dol
        obj = {"A": 1.0,
               "B": (min(rr,TOPE_R) if (rr==rr and rr>=1.0) else 1.0),
               "EL": (rr if (rr==rr and 1.0<=rr<=1.5) else 1.0)}
        j2 = min(n, i+1+VIDA)
        H,L,C = mh[i+1:j2], ml[i+1:j2], mc[i+1:j2]
        iS = np.argmax((L<=stp) if s>0 else (H>=stp)) if ((L<=stp) if s>0 else (H>=stp)).any() else 10**9
        for v,k in obj.items():
            tp = ent + s*k*rgo
            m = (H>=tp) if s>0 else (L<=tp)
            iT = int(np.argmax(m)) if m.any() else 10**9
            if iS==10**9 and iT==10**9:
                sal = float(C[-1]) if len(C) else ent
                out[v].append(((sal-ent) if s>0 else (ent-sal))/rgo)
            else:
                out[v].append(-1.0 if iS <= iT else k)
    for v in out: T[f"R_{v}"] = out[v]
    for v in out: T[f"Rn_{v}"] = T[f"R_{v}"] - COSTE[T.instr.iloc[0]]/T.rgo
    return T

def z(x):
    x=np.asarray(x,float)
    return x.mean()/(x.std(ddof=1)/np.sqrt(len(x))) if len(x)>2 and x.std()>0 else 0.0

if __name__ == "__main__":
    TT=[]
    for op, otro in (("NASDAQ","SP500"), ("SP500","NASDAQ")):
        T, Ma = corre(op, otro)
        if not len(T): print(f"  {op}: 0 señales"); continue
        Mb = carga(otro)
        T["smt"] = [smt(Ma,Mb,int(r.i),r.ts,r.lado) for r in T.itertuples()]
        T = resuelve(Ma, T)
        T.to_csv(f"data/grupo_{op}.csv", index=False)
        print(f"  {op}: {len(T)} operaciones")
        TT.append(T)
    if not TT: raise SystemExit("sin señales")
    D = pd.concat(TT, ignore_index=True)
    D.to_csv("data/grupo_todo.csv", index=False)
    print(f"\n{'='*66}\n{len(D)} OPERACIONES · {D.ts.min().date()} a {D.ts.max().date()}\n{'='*66}")
    print(f"\n{'variante':>26s} {'n':>6s} {'acierto':>9s} {'R bruta':>9s} {'z':>7s} {'R NETA':>9s}")
    print("-"*72)
    for v,nom in (("A","A · TP a 1:1"),("EL","EL · DOL si 1:1-1:1,5"),("B","B · DOL tope 4R")):
        R,N = D[f"R_{v}"], D[f"Rn_{v}"]
        print(f"{nom:>26s} {len(D):6d} {100*(R>0).mean():8.1f} % {R.mean():+9.3f} {z(R):+7.2f} {N.mean():+9.3f}")
    print(f"\n{'por ventana (variante A)':>26s}")
    for w,g in D.groupby("ventana"):
        print(f"{w:>26s} {len(g):6d} {100*(g.R_A>0).mean():8.1f} % {g.R_A.mean():+9.3f} {z(g.R_A):+7.2f} {g.Rn_A.mean():+9.3f}")
    print(f"\n{'por instrumento (A)':>26s}")
    for w,g in D.groupby("instr"):
        print(f"{w:>26s} {len(g):6d} {100*(g.R_A>0).mean():8.1f} % {g.R_A.mean():+9.3f} {z(g.R_A):+7.2f} {g.Rn_A.mean():+9.3f}")
    S = D[D.smt.notna()]
    if len(S) > 100:
        print(f"\n{'SMT (variante A)':>26s}")
        for w,g in S.groupby("smt"):
            et = "C · CON SMT" if w else "D · SIN SMT"
            print(f"{et:>26s} {len(g):6d} {100*(g.R_A>0).mean():8.1f} % {g.R_A.mean():+9.3f} {z(g.R_A):+7.2f} {g.Rn_A.mean():+9.3f}")
        a,b = S[S.smt].R_A, S[~S.smt].R_A
        if len(a)>2 and len(b)>2:
            zz=(a.mean()-b.mean())/np.sqrt(a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))
            print(f"{'diferencia C-D':>26s} {a.mean()-b.mean():+9.3f}  z = {zz:+.2f}")
