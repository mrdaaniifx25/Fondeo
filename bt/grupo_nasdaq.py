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


# ------------------------------- las tres confluencias del segundo pase
# Definiciones cerradas en docs/PREREGISTRO_grupo_nasdaq_2.md (dcfbfe7)

def pivotes(H, L):
    """Pivotes de M1 confirmados por la vela siguiente. Causal: el pivote
    en j solo se conoce en j+1, y aqui el array llega hasta la barra de
    entrada, asi que el ultimo utilizable es len-2."""
    n = len(H)
    if n < 5: return np.array([]), np.array([])
    ph = np.array([H[j] for j in range(1, n-1) if H[j] >= H[j-1] and H[j] >= H[j+1]])
    pl = np.array([L[j] for j in range(1, n-1) if L[j] <= L[j-1] and L[j] <= L[j+1]])
    return ph, pl

def grupo_lrl(piv, tol):
    """Niveles donde se acumulan 3 o mas pivotes dentro de `tol`.
    Es la LRL: liquidez de baja resistencia."""
    if len(piv) < 3: return []
    p = np.sort(piv); out = []
    i = 0
    while i < len(p):
        j = i
        while j+1 < len(p) and p[j+1]-p[i] <= tol: j += 1
        if j-i+1 >= 3: out.append(float(p[i:j+1].mean()))
        i = j+1 if j > i else i+1
    return out

def confluencias_extra(mh, ml, mo, mc, i0, k, ini_v, s, ent, rgo, acum):
    """Devuelve (judas, lrl_favor, lrl_contra_ok)."""
    a = max(0, i0+k-120); b = i0+k+1          # 2 horas hasta la entrada
    H, L = mh[a:b], ml[a:b]
    if len(H) < 10: return False, False, False
    rango = float(H.max()-L.min())
    tol = 0.10*rango if rango > 0 else 0.0

    ph, pl = pivotes(H, L)
    # a favor = liquidez en la direccion del OBJETIVO
    favor  = grupo_lrl(ph if s > 0 else pl, tol)
    favor  = [x for x in favor if (x-ent)*s > 0]
    # en contra = liquidez en la direccion del STOP, tiene que estar barrida
    contra = grupo_lrl(pl if s > 0 else ph, tol)
    contra = [x for x in contra if (ent-x)*s > 0 and abs(ent-x) <= 2*rgo]
    sin_barrer_contra = []
    for x in contra:
        tocado = (L[:len(L)-1] <= x).any() if s > 0 else (H[:len(H)-1] >= x).any()
        if not tocado: sin_barrer_contra.append(x)

    # Judas: acumulacion estrecha + manipulacion en contra dentro de la ventana
    judas = False
    if acum is not None:
        alo, ahi, estrecha = acum
        if estrecha:
            V_h = mh[ini_v:i0+k+1]; V_l = ml[ini_v:i0+k+1]
            if len(V_h):
                judas = bool(V_l.min() < alo) if s > 0 else bool(V_h.max() > ahi)
    return judas, len(favor) > 0, len(sin_barrer_contra) == 0

def acumulacion(mt, mh, ml, A, hist):
    """Rango de los 30 min previos a la apertura, y si es estrecho frente
    a la mediana de ese mismo rango en los 20 dias anteriores."""
    j1 = int(np.searchsorted(mt, np.datetime64(A), "left"))
    j0 = int(np.searchsorted(mt, np.datetime64(A)-np.timedelta64(30,"m"), "left"))
    if j1-j0 < 10: return None
    lo, hi = float(ml[j0:j1].min()), float(mh[j0:j1].max())
    r = hi-lo
    hist.append(r)
    if len(hist) < 20: return (lo, hi, False)
    med = float(np.median(hist[-21:-1]))
    return (lo, hi, r <= med)

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
    HIST = {v[0]: [] for v in VENTANAS}
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

            acum = acumulacion(mt, mh, ml, A, HIST[nom])

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

            visto = {}
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

                jud, fav, con = confluencias_extra(mh, ml, mo, mc, i0, k,
                                                   i0, s, px, rgo, acum)
                nconf = 2 + int(jud) + int(fav) + int(con)   # 1 y 2 ya pasaron

                # UNA operacion por ventana y por nivel de exigencia: la
                # PRIMERA barra que alcanza ese nivel. Un mismo dia puede
                # dar una entrada distinta segun cuantas confluencias exijas.
                fila = dict(instr=op, ventana=nom, ts=pd.Timestamp(ah),
                            lado=s, ent=px, stp=ext, rgo=rgo, tf=disp,
                            rr_dol=rr, i=i0+k, judas=jud, lrl_fav=fav,
                            lrl_con=con, nconf=nconf)
                for L in (3,4,5):
                    if nconf >= L and L not in visto:
                        visto[L] = True
                        filas.append(dict(fila, nivel=L))
                if 5 in visto: break
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
        if not len(T): print(f"  {op}: 0 senales"); continue
        Mb = carga(otro)
        T["smt"] = [smt(Ma,Mb,int(r.i),r.ts,r.lado) for r in T.itertuples()]
        T = resuelve(Ma, T)
        T.to_csv(f"data/grupo2_{op}.csv", index=False)
        print(f"  {op}: {len(T)} filas")
        TT.append(T)
    D = pd.concat(TT, ignore_index=True)
    D.to_csv("data/grupo2_todo.csv", index=False)

    print(f"\n{'='*74}")
    print(f"SEGUNDO PASE · {D.ts.min().date()} a {D.ts.max().date()}")
    print(f"preregistro sellado en dcfbfe7, antes de implementar")
    print("="*74)
    print(f"\n{'exigencia':>28s} {'n':>6s} {'acierto':>9s} {'R bruta':>9s} {'z':>7s} {'R NETA':>9s}")
    print("-"*74)
    for L,nom in ((3,"3 de 5 confluencias"),(4,"4 de 5"),(5,"5 de 5  ·  PRINCIPAL")):
        g=D[D.nivel==L]
        if not len(g): continue
        print(f"{nom:>28s} {len(g):6d} {100*(g.R_A>0).mean():8.1f} % {g.R_A.mean():+9.3f} {z(g.R_A):+7.2f} {g.Rn_A.mean():+9.3f}")
    print(f"\n{'con TP al DOL (tope 4R)':>28s}")
    for L,nom in ((3,"3 de 5"),(4,"4 de 5"),(5,"5 de 5")):
        g=D[D.nivel==L]
        if not len(g): continue
        print(f"{nom:>28s} {len(g):6d} {100*(g.R_B>0).mean():8.1f} % {g.R_B.mean():+9.3f} {z(g.R_B):+7.2f} {g.Rn_B.mean():+9.3f}")
    g5, g3 = D[D.nivel==5], D[D.nivel==3]
    if len(g5)>2 and len(g3)>2:
        zz=(g5.R_A.mean()-g3.R_A.mean())/np.sqrt(g5.R_A.var(ddof=1)/len(g5)+g3.R_A.var(ddof=1)/len(g3))
        print(f"\n{'diferencia 5/5 menos 3/5':>28s} {g5.R_A.mean()-g3.R_A.mean():+9.3f}   z = {zz:+.2f}")
    if len(g5) > 50:
        print(f"\n{'5 de 5, por ventana':>28s}")
        for w,g in g5.groupby("ventana"):
            print(f"{w:>28s} {len(g):6d} {100*(g.R_A>0).mean():8.1f} % {g.R_A.mean():+9.3f} {z(g.R_A):+7.2f} {g.Rn_A.mean():+9.3f}")
        print(f"\n{'5 de 5, por instrumento':>28s}")
        for w,g in g5.groupby("instr"):
            print(f"{w:>28s} {len(g):6d} {100*(g.R_A>0).mean():8.1f} % {g.R_A.mean():+9.3f} {z(g.R_A):+7.2f} {g.Rn_A.mean():+9.3f}")
        print(f"\n{'5 de 5, por ano':>28s}")
        for w,g in g5.groupby(g5.ts.dt.year):
            if len(g)<20: continue
            print(f"{str(w):>28s} {len(g):6d} {100*(g.R_A>0).mean():8.1f} % {g.R_A.mean():+9.3f} {z(g.R_A):+7.2f} {g.Rn_A.mean():+9.3f}")
