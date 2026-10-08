"""Para cada barrido, que habria pasado entrando en CADA vela posible."""
import json
import numpy as np, pandas as pd

U, COSTE, RR = 1e-4, 1.43, 2.0
casos = {c["id"]: c for c in json.load(open("data/barridos_casos.json"))}
d = json.load(open("/tmp/claude-0/-home-user-Fondeo/0d8c92b4-16e7-53a1-886b-22385a3d6383/scratchpad/barridos/v1.json"))
marcas = d.get("data", d)["marcas"]

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
t1 = m1.ts.to_numpy(); h1 = m1.high.to_numpy(); l1 = m1.low.to_numpy()

def utc_de(c, j):
    loc = pd.Timestamp(c["hora"]) + pd.Timedelta(minutes=5 * (j - c["i_barr"] + 1))
    return loc.tz_localize("Europe/Madrid", ambiguous=True,
                           nonexistent="shift_forward").tz_convert("UTC").tz_localize(None)

def sale(c, j):
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

fuera = {}
for k, c in casos.items():
    fila = []
    for j in range(c["i_barr"], len(c["velas"])):
        r = sale(c, j)
        fila.append(None if r is None else {"j": j, "gana": r[0], "rgo": round(r[1], 1),
                                            "Rn": round(r[0]*RR - (1-r[0]) - COSTE/r[1], 3)})
    fuera[k] = fila

json.dump(fuera, open("data/barridos_salidas.json", "w"), separators=(",", ":"))

print("entrando en CADA vela, sobre los 60 casos\n")
print(f"{'desfase':>8}{'n':>6}{'acierto':>10}{'riesgo':>9}{'coste %R':>10}{'bruta':>9}{'NETA':>9}")
for off in range(0, 13):
    rs = [f[off] for f in fuera.values() if len(f) > off and f[off]]
    if len(rs) < 15: continue
    g = np.array([r["gana"] for r in rs]); p = np.array([r["rgo"] for r in rs])
    Rb = np.where(g == 1, RR, -1.0); Rn = np.array([r["Rn"] for r in rs])
    print(f"{'+'+str(off):>8}{len(rs):>6}{100*g.mean():>9.1f} %{np.median(p):>8.1f} p"
          f"{100*COSTE/np.median(p):>9.1f} %{Rb.mean():>+9.3f}{Rn.mean():>+9.3f}")

# la mejor vela de cada caso, y donde cae
mejores = []
for k, f in fuera.items():
    v = [r for r in f if r]
    if not v: continue
    b = max(v, key=lambda r: r["Rn"])
    mejores.append(b["j"] - casos[k]["i_barr"])
print(f"\nla MEJOR vela de cada caso cae en el desfase:")
s = pd.Series(mejores).value_counts().sort_index()
for off, n in s.items(): print(f"  +{off:2d}  {'#'*n} {n}")
print(f"\ncuantas de las 13 velas ganan, por caso (mediana): "
      f"{np.median([sum(r['gana'] for r in f if r) for f in fuera.values()]):.0f} de 13")
