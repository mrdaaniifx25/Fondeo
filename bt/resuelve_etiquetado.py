"""Resuelve las respuestas de la baraja ciega del barrido de Asia.

  python3 bt/resuelve_etiquetado.py respuestas.txt

Formato de cada linea (el que copia la pagina):
  S07 | opero | venta | 1.09123 | 1.09180 | 1.09010
  S08 | paso
"""
import sys
import numpy as np
import pandas as pd

UNIDAD, COSTE = 0.0001, 1.2
rng = np.random.default_rng(20260827)

CUAL = "v2" if "v2" in sys.argv else "v1"
SUF = "" if CUAL == "v1" else "2"
ruta = next((a for a in sys.argv[1:] if a not in ("v1", "v2")), f"data/respuestas_asia{SUF}.txt")
ver = pd.read_csv(f"data/etiquetado_asia{SUF}_verdad.csv").set_index("id")
cam = pd.read_parquet(f"data/etiquetado_asia{SUF}_camino.parquet")
caminos = {k: g for k, g in cam.groupby("id")}


def resuelve(sid, lado, ent, sl, tp):
    """devuelve (R bruta, motivo) recorriendo el M1 posterior al corte"""
    g = caminos[sid]
    H, L, C = g.high.to_numpy(), g.low.to_numpy(), g.close.to_numpy()
    cierre = float(ver.loc[sid, "mec_entrada"])
    i0 = 0
    if abs(ent - cierre) > 0.2 * UNIDAD:            # orden pendiente: hay que ir a buscarla
        toca = (L <= ent) & (H >= ent)
        if not toca.any():
            return np.nan, "sin ejecutar"
        i0 = int(np.argmax(toca)) + 1
    H, L, C = H[i0:], L[i0:], C[i0:]
    if len(C) == 0:
        return np.nan, "sin recorrido"
    rgo = abs(ent - sl)
    if rgo <= 0:
        return np.nan, "stop invalido"
    rr = abs(tp - ent) / rgo
    gt, gs = ((H >= tp, L <= sl) if lado > 0 else (L <= tp, H >= sl))
    it = int(np.argmax(gt)) if gt.any() else 10**9
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    if it == 10**9 and isl == 10**9:
        sal = C[-1]
        return ((sal - ent) if lado > 0 else (ent - sal)) / rgo, "cierre Londres"
    if isl <= it:
        return -1.0, "SL"
    return float(rr), "TP"


# --------------------------------------------------------------- respuestas
filas = []
for ln in open(ruta):
    ln = ln.strip()
    if not ln or ln.startswith("#"):
        continue
    p = [x.strip() for x in ln.split("|")]
    sid = p[0]
    if sid not in ver.index:
        print(f"  aviso: {sid} no esta en la baraja, se ignora"); continue
    if len(p) < 2 or p[1] not in ("opero", "paso"):
        continue
    if p[1] == "paso":
        filas.append(dict(id=sid, opera=False)); continue
    lado = 1 if p[2].startswith("comp") else -1
    ent, sl, tp = float(p[3]), float(p[4]), float(p[5])
    R, mot = resuelve(sid, lado, ent, sl, tp)
    filas.append(dict(id=sid, opera=True, lado=lado, entrada=ent, stop=sl, obj=tp,
                      riesgo=abs(ent - sl) / UNIDAD, rr=abs(tp - ent) / abs(ent - sl),
                      R=R, motivo=mot))

t = pd.DataFrame(filas)
if t.empty:
    sys.exit("no hay respuestas legibles en " + ruta)


def mecanica(ids):
    out = []
    for sid in ids:
        r = ver.loc[sid]
        R, mot = resuelve(sid, int(r.lado), float(r.mec_entrada), float(r.mec_sl), float(r.mec_tp))
        out.append(dict(id=sid, lado=int(r.lado), riesgo=abs(r.mec_entrada - r.mec_sl) / UNIDAD,
                        rr=abs(r.mec_tp - r.mec_entrada) / abs(r.mec_entrada - r.mec_sl),
                        R=R, motivo=mot))
    return pd.DataFrame(out).dropna(subset=["R"])


def resumen(nom, d):
    if d.empty or d.R.isna().all():
        print(f"{nom:34s}  sin operaciones"); return
    d = d.dropna(subset=["R"])
    neto = (d.R - COSTE / d.riesgo).to_numpy()
    ee = neto.std(ddof=1) / np.sqrt(len(neto)) if len(neto) > 1 else np.nan
    base = 100 / (1 + d.rr.median())      # geometria pura: P(TP) si no hubiera informacion
    print(f"{nom:34s} {len(d):>4} {d.riesgo.median():>7.1f}p {d.rr.median():>6.2f} "
          f"{100*(d.motivo=='TP').mean():>6.1f}% {base:>8.1f}% {d.R.mean():>+9.3f} "
          f"{neto.mean():>+9.3f} {neto.mean()/ee if ee else float('nan'):>+7.2f}")


ops = t[t.opera] if "opera" in t else t
n_paso = int((~t.opera).sum())
print("=" * 106)
print(f"BARAJA CIEGA {CUAL.upper()} · {len(t)} respondidos de {len(ver)} · "
      f"{len(ops)} operados, {n_paso} pasados")
print("=" * 106)
print(f"{'':34s} {'n':>4} {'riesgo':>8} {'R:R':>6} {'%TP':>7} {'geometría':>9} "
      f"{'R BRUTA':>9} {'R NETA':>9} {'z':>7}")
resumen("tus entradas", ops)
resumen("la regla mecánica, esos mismos", mecanica(ops.id))
resumen("la regla mecánica, los pasados", mecanica(t[~t.opera].id))
resumen(f"la regla mecánica, los {len(ver)}", mecanica(list(ver.index)))

if len(ops) and n_paso:
    a = mecanica(ops.id).R
    b = mecanica(t[~t.opera].id).R
    if len(a) > 1 and len(b) > 1:
        d = a.mean() - b.mean()
        ee = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
        print(f"\n  tu criterio de selección: los que elegiste operar rinden {d:+.3f} R "
              f"más que los que pasaste (z {d/ee:+.2f})")

ops.to_csv(f"data/etiquetado_asia{SUF}_respuestas.csv", index=False)
print(f"\n  guardado en data/etiquetado_asia{SUF}_respuestas.csv")
