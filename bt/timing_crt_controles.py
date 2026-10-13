"""Controles POST HOC de bt/timing_crt.py. NO estaban preregistrados.

El propio video dice al final que su regla "no deja de ser esperar un
retroceso". Asi que se compara contra un retroceso GENERICO sin CRT, se
descompone en las cuatro casillas, y se permuta la etiqueta dentro de
instrumento-semana.

  python3 bt/timing_crt_controles.py
"""
import numpy as np, pandas as pd
from math import sqrt
src = open("bt/timing_crt.py").read().split("T = pd.concat")[0]
exec(compile(src, "t", "exec"))

# reconstruye con columnas extra para los controles genericos
def corre2(nom, ruta, U, coste):
    M, b = prepara(ruta)
    O,H,L,C = (b[k].to_numpy() for k in "ohlc")
    fin = b.fin.to_numpy().astype(int)
    ph, pl = np.r_[np.nan, H[:-1]], np.r_[np.nan, L[:-1]]
    bl, bh = L <= pl, H >= ph
    alin_l, alin_s = bl & ~bh, bh & ~bl
    # retroceso GENERICO: el cierre esta en el tercio bajo (o alto) del rango
    # de las ultimas 6 velas H4. Ni rangos ni barridos: solo "ha retrocedido".
    hh6 = pd.Series(H).rolling(6).max().to_numpy()
    ll6 = pd.Series(L).rolling(6).min().to_numpy()
    pos6 = (C - ll6) / (hh6 - ll6)
    sem = pd.Series(b.index).dt.to_period("W").to_numpy()
    cs = pd.Series(C, index=sem).groupby(level=0)
    dirsem = pd.Series(np.sign(cs.last() - cs.first()))
    orac = pd.Series(sem).map(dirsem).to_numpy()
    f=[]
    for i in range(6, len(b)-1):
        e = fin[i]+1
        if e >= len(M) or not np.isfinite(orac[i]) or orac[i]==0: continue
        lado = int(orac[i])
        mecha = L[i] if lado>0 else H[i]
        ent = M.open.to_numpy()[e]
        rgo = (ent-mecha)*lado
        if rgo<=0: continue
        obj = ph[i] if lado>0 else pl[i]
        rec = (obj-ent)*lado
        if rec<=0 or not np.isfinite(rec): continue
        al = bool(alin_l[i]) if lado>0 else bool(alin_s[i])
        # retroceso generico a favor del sesgo
        rt = (pos6[i] < 1/3) if lado>0 else (pos6[i] > 2/3)
        f.append((nom, sem[i], b.index[i], lado, e, rgo/U, rec/U, al, bool(rt)))
    D = pd.DataFrame(f, columns="ins sem ts lado e rgo rec alin retro".split())
    D["R"] = [resuelve(M, int(r.e), r.lado, r.rgo*U, r.rec*U) for _,r in D.iterrows()]
    D["cr"] = coste/D.rgo; D["geo"] = D.rgo/(D.rgo+D.rec)
    D["dia"] = pd.to_datetime(D.ts).dt.floor("D")
    return D

T = pd.concat([corre2(*a) for a in INS], ignore_index=True)
T["gr"] = T.ins + T.dia.astype(str)
T["ex"] = (T.R > 0).astype(float) - T.geo          # exceso por operacion
nd = T.dia.nunique()
print(f"n {len(T):,}  ·  dias {nd:,}  ·  sesgo oraculo en las tres\n")

def ficha(et, D):
    if len(D)<30: return print(f"  {et:<34} (pocas: {len(D)})")
    n=(D.R-D.cr)
    print(f"  {et:<34}{len(D):>7}{(D.rec/D.rgo).mean():>7.2f}{100*(D.R>0).mean():>8.1f}%"
          f"{100*D.geo.mean():>8.1f}%{100*D.ex.mean():>+8.1f}{D.R.mean():>+9.4f}"
          f"{n.mean():>+9.4f}{n.sum()/nd:>+9.4f}")
print(f"  {'regla':<34}{'n':>7}{'R:R':>7}{'acierto':>9}{'geom':>9}{'exceso':>8}"
      f"{'R bruta':>9}{'R neta':>9}{'neta/dia':>9}")
ficha("1 ciego", T)
ficha("2 CRT alineado", T[T.alin])
ficha("5 retroceso GENERICO (sin CRT)", T[T.retro])
ficha("2+5 ambos", T[T.alin & T.retro])
ficha("solo CRT, sin retroceso", T[T.alin & ~T.retro])
ficha("solo retroceso, sin CRT", T[~T.alin & T.retro])

e2 = 100*T[T.alin].ex.mean(); e5 = 100*T[T.retro].ex.mean(); e1 = 100*T.ex.mean()
print(f"\n  exceso: ciego {e1:+.1f}  ·  CRT {e2:+.1f}  ·  retroceso generico {e5:+.1f}")
print(f"  CRT menos retroceso generico: {e2-e5:+.1f} pp")

print("\n  PRUEBA DE PERMUTACION: se baraja la etiqueta 'alineado' DENTRO de")
print("  cada instrumento-semana, conservando cuantas hay. 2.000 barajas.")
rr = np.random.default_rng(4)
obs = e2 - e1
nul = []
for _ in range(2000):
    lab = T.groupby(["ins","sem"]).alin.transform(
        lambda s: pd.Series(rr.permutation(s.to_numpy()), index=s.index))
    nul.append(100*T[lab.astype(bool)].ex.mean() - e1)
nul = np.array(nul)
p = float((np.abs(nul) >= abs(obs)).mean())
print(f"  observado: CRT menos ciego = {obs:+.2f} pp")
print(f"  nulo barajado: media {nul.mean():+.2f}  desv {nul.std():.2f}"
      f"  ·  z {(obs-nul.mean())/nul.std():+.2f}  ·  p {p:.4f}")
