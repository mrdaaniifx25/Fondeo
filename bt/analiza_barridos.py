"""Que regla mecanica reproduce sus 52 entradas, y que tienen los 8 descartes."""
import json, collections
import numpy as np, pandas as pd

d = json.load(open("/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/barridos/v1.json"))
m = d.get("data", d)["marcas"]
casos = {c["id"]: c for c in json.load(open("data/barridos_casos.json"))}

# ── que distingue a los 8 que descarta ────────────────────────────────────
filas = []
for k, v in m.items():
    c = casos[k]
    vs = c["velas"]; b = c["i_barr"]; L = c["lado"]
    o, h, l, cl = vs[b]
    filas.append(dict(id=k, toma=(v != "no"), pick=(None if v == "no" else v),
        lado=L, ses=c["ses"], rgo=c["rgo"], hora=int(c["hora"][11:13]),
        cuerpo=abs(cl - o) / 1e-4, mecha=(h - max(o, cl) if L < 0 else min(o, cl) - l) / 1e-4,
        dentro=abs(cl - c["niv"]) / 1e-4))
F = pd.DataFrame(filas)
print(f"toma {F.toma.sum()} de {len(F)}  ({100*F.toma.mean():.0f} %)\n")
print("           toma   descarta")
for col in ("rgo", "cuerpo", "mecha", "dentro", "hora"):
    a, b = F[F.toma][col].median(), F[~F.toma][col].median()
    print(f"{col:>8}  {a:7.1f}   {b:7.1f}")
print("\ndescartes por sesion:", F[~F.toma].ses.value_counts().to_dict())
print("descartes por lado:  ", F[~F.toma].lado.value_counts().to_dict())
print("\nlos 8 descartados:")
print(F[~F.toma][["id","ses","lado","rgo","cuerpo","mecha","dentro","hora"]].to_string(index=False))

# ── que regla mecanica reproduce sus 52 elecciones ────────────────────────
def reglas(c):
    """Para cada regla candidata, que indice elegiria."""
    vs = c["velas"]; b = c["i_barr"]; L = c["lado"]; n = len(vs)
    ob, hb, lb, cb = vs[b]
    disp = lb if L < 0 else hb          # extremo opuesto de la vela del barrido
    baja = L < 0

    def primera(cond):
        for j in range(b + 1, n):
            if cond(j): return j
        return None

    def cierre_favor(j): 
        return vs[j][3] < vs[j][0] if baja else vs[j][3] > vs[j][0]
    def rompe_barrido(j):
        return vs[j][2] < disp if baja else vs[j][1] > disp
    def rompe_anterior(j):
        return vs[j][2] < vs[j-1][2] if baja else vs[j][1] > vs[j-1][1]
    def cierra_tras_cierre(j):
        return vs[j][3] < cb if baja else vs[j][3] > cb
    def cierra_tras_extremo(j):
        return vs[j][3] < disp if baja else vs[j][3] > disp

    out = {}
    out["R1 la propia vela del barrido"] = b
    out["R2 1er cierre a favor"] = primera(cierre_favor)
    out["R3 1a que rompe el extremo de la del barrido"] = primera(rompe_barrido)
    out["R4 1a que rompe el extremo de la anterior"] = primera(rompe_anterior)
    out["R5 1er cierre mas alla del cierre del barrido"] = primera(cierra_tras_cierre)
    out["R6 1er cierre mas alla del extremo de la del barrido"] = primera(cierra_tras_extremo)
    # R7 su propuesta escrita: cierre a favor, y despues romper ese extremo
    j7 = None; visto = False
    for j in range(b, n):
        if not visto:
            if cierre_favor(j): visto = True
            if j == b: continue
        if not visto: continue
        if rompe_barrido(j): j7 = j; break
    out["R7 su propuesta escrita"] = j7
    return out

ent = [(k, v) for k, v in m.items() if v != "no"]
acc = collections.defaultdict(lambda: [0, 0, 0])   # exacto, +-1, con valor
for k, p in ent:
    for nom, j in reglas(casos[k]).items():
        if j is None: continue
        acc[nom][2] += 1
        if j == p: acc[nom][0] += 1
        if abs(j - p) <= 1: acc[nom][1] += 1

print(f"\n\nque regla reproduce sus {len(ent)} entradas")
print(f"{'':<52}{'exacta':>9}{'±1 vela':>10}{'define':>9}")
for nom, (e, u, t) in sorted(acc.items(), key=lambda x: -x[1][0]):
    print(f"{nom:<52}{e:>4} {100*e/t:4.0f}%{u:>5} {100*u/t:4.0f}%{t:>8}")

off = collections.Counter(p - casos[k]["i_barr"] for k, p in ent)
med = int(np.median([p - casos[k]["i_barr"] for k, p in ent]))
print(f"\ndesfase mediano: +{med} velas   ({5*med} minutos tras el barrido)")

# ── ¿sus entradas salen mejor que las mecanicas? ──────────────────────────
U, COSTE, RR = 1e-4, 1.43, 2.0
m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
t1 = m1.ts.to_numpy(); h1 = m1.high.to_numpy(); l1 = m1.low.to_numpy()

def utc_de(c, j):
    """Instante UTC del CIERRE de la vela j del caso."""
    loc = pd.Timestamp(c["hora"]) + pd.Timedelta(minutes=5 * (j - c["i_barr"] + 1))
    return loc.tz_localize("Europe/Madrid", ambiguous=True,
                           nonexistent="shift_forward").tz_convert("UTC").tz_localize(None)

def resultado(c, j):
    vs = c["velas"]; L = c["lado"]; ent = vs[j][3]; stop = c["ext"]
    rgo = abs(ent - stop)
    if rgo <= 0: return None
    obj = ent + L * RR * rgo
    i = int(np.searchsorted(t1, np.datetime64(utc_de(c, j)), side="right"))
    for k in range(i, min(len(t1), i + 60 * 24 * 3)):
        if L > 0:
            if l1[k] <= stop: return (0, rgo / U)
            if h1[k] >= obj:  return (1, rgo / U)
        else:
            if h1[k] >= stop: return (0, rgo / U)
            if l1[k] <= obj:  return (1, rgo / U)
    return None

def resume(nom, pares):
    filas = [r for r in pares if r]
    if not filas: return
    g = np.array([r[0] for r in filas]); p = np.array([r[1] for r in filas])
    Rb = np.where(g == 1, RR, -1.0); Rn = Rb - COSTE / p
    n = len(filas); s = Rn.std(ddof=1)
    print(f"{nom:<34} n {n:3d}   acierto {100*g.mean():5.1f} %   "
          f"riesgo {np.median(p):5.1f} p   coste {100*COSTE/np.median(p):5.1f} %   "
          f"bruta {Rb.mean():+.3f}   NETA {Rn.mean():+.3f} "
          f"± {1.96*s/np.sqrt(n):.3f}")

print("\n\nsus 52 entradas, contra las mecanicas sobre LOS MISMOS 52 casos")
print("(con la advertencia de que el vio 12 velas posteriores al marcar)\n")
resume("SUS entradas", [resultado(casos[k], p) for k, p in ent])
resume("R1 al cierre del barrido", [resultado(casos[k], casos[k]["i_barr"]) for k, _ in ent])
for nom in ("R2 1er cierre a favor", "R7 su propuesta escrita"):
    rs = []
    for k, _ in ent:
        j = reglas(casos[k]).get(nom)
        if j is not None: rs.append(resultado(casos[k], j))
    resume(nom, rs)

# ── comparacion EMPAREJADA: mismos casos, su entrada contra la mecanica ───
print("\ncomparacion emparejada (mismo caso, su vela contra la mecanica)")
for nom, idx in (("R1 al cierre del barrido", lambda c: c["i_barr"]),
                 ("R7 su propuesta escrita", lambda c: reglas(c).get("R7 su propuesta escrita"))):
    dif = []
    for k, p in ent:
        c = casos[k]; j = idx(c)
        if j is None: continue
        a, b = resultado(c, p), resultado(c, j)
        if a and b:
            dif.append((a[0]*RR - (1-a[0]) - COSTE/a[1]) - (b[0]*RR - (1-b[0]) - COSTE/b[1]))
    dif = np.array(dif); n = len(dif); s = dif.std(ddof=1)
    print(f"  suyo - {nom:<26} n {n:3d}   diferencia {dif.mean():+.3f} "
          f"± {1.96*s/np.sqrt(n):.3f}   z {dif.mean()/(s/np.sqrt(n)):+.2f}")

# control de que marco en serio: su riesgo contra el de sus capturas reales
rr = [resultado(casos[k], p) for k, p in ent]
rr = [r[1] for r in rr if r]
print(f"\nriesgo de sus 52 marcas: mediana {np.median(rr):.1f} p, "
      f"cuartiles {np.percentile(rr,25):.1f}-{np.percentile(rr,75):.1f}")
print("sus operaciones reales de esta semana: 2 a 4 pips")
