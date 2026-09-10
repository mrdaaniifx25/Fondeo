import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref, pz, pf, KZ_FX, KZ_IDX
from crt_fib import setups, ejecuta_fib

INSTR = {
 "EURUSD": ("data/eurusd_m1.parquet", 0.0001, 1.2, KZ_FX),
 "GBPUSD": ("data/gbpusd_m1.parquet", 0.0001, 1.5, KZ_FX),
 "USDJPY": ("data/usdjpy_m1.parquet", 0.01,   1.2, KZ_FX),
 "NAS100": ("data/nsxusd_m1.parquet", 1.0,    1.5, KZ_IDX),
 "SP500":  ("data/spxusd_m1.parquet", 1.0,    0.6, KZ_IDX),
}
BASE = dict(fib=0.618, min_leg=0.20, killzone=True, min_rr=1.5, max_rr=15.0,
            min_riesgo_u=3.0,
            buffer=1.0, tope_dia=3, max_horas=48)

M, M5 = {}, {}
print("cargando y construyendo M5...")
for k,(f,u,c,z) in INSTR.items():
    m1 = pd.read_parquet(f); m1["ts"] = pd.to_datetime(m1["ts"]); M[k] = m1
    M5[k] = m1.set_index("ts").resample("5min",label="left",closed="left").agg(
        open=("open","first"), high=("high","max"), low=("low","min"),
        close=("close","last")).dropna().reset_index()
print(f"  listo\n")

CAB = f"{'':34s} {'n':>5s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'%TP':>6s} {'RR':>5s} {'PF neto':>8s}"
def linea(nom, tr):
    if tr is None or len(tr) < 3:
        print(f"{nom:34s} {0 if tr is None else len(tr):>5d}   (muestra insuficiente)"); return None
    z,p = pz(tr.bruto)
    print(f"{nom:34s} {len(tr):>5d} {tr.bruto.mean():>+9.4f} {z:>+6.2f} {p:>7.4f} "
          f"{(tr.motivo=='TP').mean()*100:>5.1f}% {tr.rr.mean():>5.2f} {pf(tr.R):>8.3f}")
    return dict(n=len(tr), bruto=float(tr.bruto.mean()), z=float(z), p=float(p), pf=float(pf(tr.R)))

def corre(tf, cfg):
    tot, det = [], {}
    for k,(f,u,c,z) in INSTR.items():
        ref = velas_ref(M[k], tf, 1)
        s = setups(ref)
        tr = ejecuta_fib(s, M5[k], M[k], cfg, u, c, z)
        det[k] = tr
        if tr is not None and not tr.empty: tot.append(tr)
    return (pd.concat(tot, ignore_index=True) if tot else pd.DataFrame()), det

print("="*96)
print("A · PROFUNDIDAD DEL RETROCESO  (referencia H4, entrada limitada en M5)")
print("="*96); print(CAB)
guarda = {}
for fib in (0.382, 0.5, 0.618, 0.705, 0.79):
    a,det = corre(4, dict(BASE, fib=fib))
    r = linea(f"   fib {fib:.3f}  ({fib*100:.1f}% de retroceso)", a)
    if r: guarda[("H4",fib)] = (r,a,dict(BASE,fib=fib),4)

print("\n" + "="*96)
print("B · CRUCE con la temporalidad de referencia")
print("="*96); print(CAB)
for tf,nom in ((1,"H1"),(4,"H4"),(24,"D1")):
    for fib in (0.5, 0.618, 0.705):
        a,det = corre(tf, dict(BASE, fib=fib))
        r = linea(f"   {nom} + fib {fib:.3f}", a)
        if r: guarda[(nom,fib)] = (r,a,dict(BASE,fib=fib),tf)

print("\n" + "="*96)
print("C · DESGLOSE de la mejor celda por instrumento")
print("="*96); print(CAB)
clave = max(guarda, key=lambda k: guarda[k][0]["bruto"] if guarda[k][0]["n"]>=40 else -9)
r,a,cfg,tf = guarda[clave]
print(f"   (mejor celda con n>=40: {clave[0]} + fib {clave[1]})")
_,det = corre(tf, cfg)
for k in INSTR: linea(f"      {k}", det[k])
linea("   AGREGADO", a)

print("\n" + "="*96)
print("D · CONTROL: misma mecanica, DIRECCION al azar")
print("="*96); print(CAB)
rng = np.random.default_rng(33); azt = []
for k,(f,u,c,z) in INSTR.items():
    ref = velas_ref(M[k], tf, 1); s = setups(ref)
    if s.empty: continue
    for rep in range(8):
        s2 = s.copy()
        s2["largo"] = rng.integers(0,2,len(s2)).astype(bool)
        tr = ejecuta_fib(s2, M5[k], M[k], cfg, u, c, z)
        if tr is not None and not tr.empty: azt.append(tr)
linea("   direccion AL AZAR (8 rep)", pd.concat(azt,ignore_index=True) if azt else None)
n_celdas = 5 + 9
print(f"\n   celdas examinadas: {n_celdas}  ->  umbral Bonferroni p < {0.05/n_celdas:.4f}")
