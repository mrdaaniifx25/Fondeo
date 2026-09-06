import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref, pz, pf, KZ_FX, KZ_IDX
from crt_fib import setups, ejecuta_fib
from crt_confluencias import bias_diario, bias_en, entrada_nested

INSTR = {
 "EURUSD": ("data/eurusd_m1.parquet", 0.0001, 1.2, KZ_FX),
 "GBPUSD": ("data/gbpusd_m1.parquet", 0.0001, 1.5, KZ_FX),
 "USDJPY": ("data/usdjpy_m1.parquet", 0.01,   1.2, KZ_FX),
 "NAS100": ("data/nsxusd_m1.parquet", 1.0,    1.5, KZ_IDX),
 "SP500":  ("data/spxusd_m1.parquet", 1.0,    0.6, KZ_IDX),
}
CFG = dict(fib=0.705, min_leg=0.20, killzone=True, min_rr=1.5, max_rr=15.0,
           min_riesgo_u=3.0, buffer=1.0, tope_dia=3, max_horas=48)

M,M5,M15,BIAS,REF = {},{},{},{},{}
print("preparando...")
for k,(f,u,c,z) in INSTR.items():
    m1 = pd.read_parquet(f); m1["ts"] = pd.to_datetime(m1["ts"]); M[k]=m1
    g = m1.set_index("ts")
    M5[k]  = g.resample("5min", label="left",closed="left").agg(open=("open","first"),
             high=("high","max"),low=("low","min"),close=("close","last")).dropna().reset_index()
    M15[k] = g.resample("15min",label="left",closed="left").agg(open=("open","first"),
             high=("high","max"),low=("low","min"),close=("close","last")).dropna().reset_index()
    BIAS[k] = bias_diario(m1)
    REF[k]  = setups(velas_ref(m1, 4, 1))
    print(f"  {k:7s} setups H4 {len(REF[k]):>4}  |  dias con CRT diario {len(BIAS[k]):>4}")

CAB=f"{'':38s} {'n':>5s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'%TP':>6s} {'RR':>5s} {'PF neto':>8s}"
def linea(nom,tr):
    if tr is None or len(tr)<3:
        print(f"{nom:38s} {0 if tr is None else len(tr):>5d}   (muestra insuficiente)"); return None
    z,p=pz(tr.bruto)
    print(f"{nom:38s} {len(tr):>5d} {tr.bruto.mean():>+9.4f} {z:>+6.2f} {p:>7.4f} "
          f"{(tr.motivo=='TP').mean()*100:>5.1f}% {tr.rr.mean():>5.2f} {pf(tr.R):>8.3f}")
    return dict(n=len(tr),bruto=float(tr.bruto.mean()),z=float(z),p=float(p),pf=float(pf(tr.R)))

def filtra_bias(s, bias, largo_col="largo"):
    if s.empty: return s
    ok=[]
    for r in s.itertuples():
        b = bias_en(bias, pd.Timestamp(r.ini3))
        ok.append(b is not None and b == getattr(r, largo_col))
    return s[np.array(ok)]

def corre(entrada, usar_bias):
    tot={}
    for k,(f,u,c,z) in INSTR.items():
        s = REF[k]
        if entrada=="fib":
            if usar_bias: s = filtra_bias(s, BIAS[k])
            tr = ejecuta_fib(s, M5[k], M[k], CFG, u, c, z) if not s.empty else pd.DataFrame()
        else:
            tr = entrada_nested(s, M15[k], M[k], CFG, u, c, z,
                                bias=BIAS[k] if usar_bias else None)
        tot[k]=tr
    j=[t for t in tot.values() if t is not None and not t.empty]
    return (pd.concat(j,ignore_index=True) if j else pd.DataFrame()), tot

print("\n"+"="*104)
print("LAS DOS CONFLUENCIAS DE LA GUIA  ·  referencia H4, killzones en hora espanola")
print("="*104); print(CAB)
res={}
for ent,nom in (("fib","entrada fib 70,5% en M5"),("nested","entrada CRT anidado en M15")):
    for ub,etq in ((False,"sin Daily Bias"),(True,"CON Daily Bias")):
        a,det = corre(ent,ub)
        res[(ent,ub)] = (linea(f"   {nom} · {etq}", a), a, det)

print("\n"+"="*104)
print("DESGLOSE por instrumento de las dos celdas con anidado")
print("="*104); print(CAB)
for ub,etq in ((False,"sin bias"),(True,"con bias")):
    r,a,det = res[("nested",ub)]
    print(f"  -- anidado {etq}")
    for k in INSTR: linea(f"      {k}", det[k])

print("\n"+"="*104)
print("CONTROL: misma mecanica, DIRECCION al azar")
print("="*104); print(CAB)
rng=np.random.default_rng(77)
for ent in ("fib","nested"):
    azt=[]
    for k,(f,u,c,z) in INSTR.items():
        s=REF[k]
        if s.empty: continue
        for rep in range(6):
            s2=s.copy(); s2["largo"]=rng.integers(0,2,len(s2)).astype(bool)
            s2["A"]=np.where(s2.largo, s2.A, s2.A)
            tr = (ejecuta_fib(s2,M5[k],M[k],CFG,u,c,z) if ent=="fib"
                  else entrada_nested(s2,M15[k],M[k],CFG,u,c,z))
            if tr is not None and not tr.empty: azt.append(tr)
    linea(f"   {ent} · direccion AL AZAR (6 rep)", pd.concat(azt,ignore_index=True) if azt else None)
