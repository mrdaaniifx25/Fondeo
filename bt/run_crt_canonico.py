import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd, json
from crt_canonico import velas_ref, senales, ejecuta, pz, pf, KZ_FX, KZ_IDX

INSTR = {
 "EURUSD": ("data/eurusd_m1.parquet", 0.0001, 1.2, KZ_FX),
 "GBPUSD": ("data/gbpusd_m1.parquet", 0.0001, 1.5, KZ_FX),
 "USDJPY": ("data/usdjpy_m1.parquet", 0.01,   1.2, KZ_FX),
 "NAS100": ("data/nsxusd_m1.parquet", 1.0,    1.5, KZ_IDX),
 "SP500":  ("data/spxusd_m1.parquet", 1.0,    0.6, KZ_IDX),
}
BASE = dict(entrada="v2", cierre_estricto=True, killzone=True, min_rr=1.5,
            buffer=1.0, tope_dia=3, max_horas=48)

M = {}
for k,(f,u,c,z) in INSTR.items():
    m1 = pd.read_parquet(f); m1["ts"] = pd.to_datetime(m1["ts"]); M[k] = m1

CAB = f"{'':32s} {'n':>5s} {'bruto/op':>9s} {'z':>6s} {'p':>7s} {'%TP':>6s} {'RR':>5s} {'PF neto':>8s}"
def linea(nom, tr):
    if tr is None or len(tr) < 3:
        print(f"{nom:32s} {0 if tr is None else len(tr):>5d}   (muestra insuficiente)"); return None
    z,p = pz(tr.bruto)
    print(f"{nom:32s} {len(tr):>5d} {tr.bruto.mean():>+9.4f} {z:>+6.2f} {p:>7.4f} "
          f"{(tr.motivo=='TP').mean()*100:>5.1f}% {tr.rr.mean():>5.2f} {pf(tr.R):>8.3f}")
    return dict(n=len(tr), bruto=float(tr.bruto.mean()), z=float(z), p=float(p), pf=float(pf(tr.R)))

def corre(tf, ancla, cfg):
    tot, det = [], {}
    for k,(f,u,c,z) in INSTR.items():
        ref = velas_ref(M[k], tf, ancla)
        s = senales(ref, cfg)
        tr = ejecuta(s, M[k], cfg, u, c, z)
        det[k] = tr
        if tr is not None and not tr.empty: tot.append(tr)
    return (pd.concat(tot, ignore_index=True) if tot else pd.DataFrame()), det

print("="*92)
print("A · EL ANCLAJE DE LA REJILLA H4  (mi error nº1)")
print("="*92); print(CAB)
for ancla,nom in ((1,"01:00 NUEVA YORK  (la guia)"), (0,"00:00 Nueva York"),
                  (5,"05:00 Nueva York")):
    a,_ = corre(4, ancla, BASE)
    linea(f"   H4 anclada a {nom}", a)

print("\n" + "="*92)
print("B · ENTRAR EN VELA 3 FRENTE A VELA 2  (mi error nº2, el 'error fatal' de la guia)")
print("="*92); print(CAB)
res = {}
for ent,nom in (("v2","Vela 2 - agresiva, la de la guia"), ("v3","Vela 3 - conservadora")):
    cfg = dict(BASE, entrada=ent)
    a,det = corre(4, 1, cfg)
    res[ent] = linea(f"   entrada en {nom}", a)
    for k in INSTR: linea(f"      {k}", det[k])

print("\n" + "="*92)
print("C · QUE APORTA CADA REGLA  (quitando de una en una, H4 ancla NY, entrada v2)")
print("="*92); print(CAB)
a,_ = corre(4,1,BASE); linea("   completa", a)
for campo,val,nom in (("cierre_estricto",False,"sin exigir cierre de V2 dentro"),
                      ("killzone",False,"sin killzones"),
                      ("min_rr",1.0,"con R:R minimo 1.0"),
                      ("tope_dia",99,"sin tope diario")):
    a,_ = corre(4,1,dict(BASE, **{campo:val})); linea(f"   {nom}", a)

print("\n" + "="*92)
print("D · OTRAS TEMPORALIDADES DE REFERENCIA")
print("="*92); print(CAB)
for tf,nom in ((1,"H1"),(4,"H4"),(24,"D1")):
    a,_ = corre(tf,1,BASE); linea(f"   referencia {nom}", a)

print("\n" + "="*92)
print("E · CONTROLES sobre la configuracion de la guia")
print("="*92); print(CAB)
a,det = corre(4,1,BASE)
esp = a.copy(); esp["bruto"] = -esp["bruto"]
linea("   ESPEJO (invertir el resultado)", esp)
rng = np.random.default_rng(5)
azt = []
for k,(f,u,c,z) in INSTR.items():
    ref = velas_ref(M[k],4,1); s = senales(ref, BASE)
    if s.empty: continue
    for rep in range(5):
        s2 = s.copy()
        s2["largo"] = rng.integers(0,2,len(s2)).astype(bool)
        # el rango y el barrido se recalculan segun la direccion sorteada
        s2["sweep"] = np.where(s2.largo, s2.v2_lo, s2.v2_hi)
        tr = ejecuta(s2, M[k], BASE, u, c, z)
        if tr is not None and not tr.empty: azt.append(tr)
linea("   DIRECCION AL AZAR (5 rep)", pd.concat(azt, ignore_index=True) if azt else None)

print("\n" + "="*92)
print("F · CRUCE: las dos mejoras juntas (H1/D1 de referencia + entrada en Vela 3)")
print("="*92); print(CAB)
mejor = {}
for tf,nom in ((1,"H1"),(4,"H4"),(24,"D1")):
    for ent in ("v2","v3"):
        cfg = dict(BASE, entrada=ent)
        a,det = corre(tf,1,cfg)
        r = linea(f"   {nom} + entrada {ent}", a)
        if r: mejor[f"{nom}_{ent}"] = (r,a,cfg,tf)

print("\n" + "="*92)
print("G · CONTROL LIMPIO sobre la mejor celda: direccion al azar, misma mecanica")
print("="*92); print(CAB)
clave = max(mejor, key=lambda k: mejor[k][0]["bruto"])
r,a,cfg,tf = mejor[clave]
print(f"   (celda con mayor ventaja: {clave})")
linea(f"   {clave} real", a)
rng = np.random.default_rng(21); azt=[]
for k,(f,u,c,z) in INSTR.items():
    ref = velas_ref(M[k],tf,1); s = senales(ref, cfg)
    if s.empty: continue
    for rep in range(10):
        s2 = s.copy()
        s2["largo"] = rng.integers(0,2,len(s2)).astype(bool)
        s2["sweep"] = np.where(s2.largo, s2.v2_lo, s2.v2_hi)
        tr = ejecuta(s2, M[k], cfg, u, c, z)
        if tr is not None and not tr.empty: azt.append(tr)
az = pd.concat(azt, ignore_index=True)
linea("   direccion AL AZAR (10 rep)", az)
print(f"\n   celdas examinadas en total: 3 anclajes + 2 entradas + 4 reglas + 3 TF + 6 cruces = 18")
print(f"   umbral de Bonferroni para 18: p < {0.05/18:.4f}")
