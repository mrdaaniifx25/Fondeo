"""¿Separa la vela diaria los setups que llegan al objetivo de los que no?

Se parte de la unica celda con ventaja bruta real medida hasta ahora: la
liquidez SIMPLE en H4, +0,085 R sobre 9.197 casos. Solo le faltan 0,023 R para
pasar el coste, asi que basta con un filtro que aporte poco.

Se prueban cinco lecturas del contexto diario. Cinco contrastes: el umbral
honesto no es 0,05 sino 0,01, y asi se dice.
"""
import sys; sys.path.insert(0,"bt")
import numpy as np, pandas as pd
from crt_canonico import velas_ref
import cierres as C, liquidez_multiple as LM

INS = [("EURUSD","data/eurusd_m1.parquet",0.0001,1.2),
       ("NAS100","data/nsxusd_m1.parquet",1.0,1.5),
       ("GBPUSD","data/gbpusd_m1.parquet",0.0001,1.5),
       ("USDJPY","data/usdjpy_m1.parquet",0.01,1.3)]

def diarias(m1):
    """Velas diarias con el corte de las 17:00 de Nueva York, el de los CFD."""
    d = velas_ref(m1, 24, ancla_ny=17)
    h,l,o,c = (d[x].to_numpy() for x in ("high","low","open","close"))
    d["ph"], d["pl"] = np.roll(h,1), np.roll(l,1)
    d.loc[0,["ph","pl"]] = np.nan
    ph, pl = d.ph.to_numpy(), d.pl.to_numpy()
    # CRT diario: se lleva un extremo de la anterior y cierra dentro
    barre_lo = l < pl; barre_hi = h > ph
    dentro = (c >= pl) & (c <= ph)
    d["crt_dir"] = np.where(barre_lo & ~barre_hi & dentro, +1,
                     np.where(barre_hi & ~barre_lo & dentro, -1, 0))
    d["atrD"] = C.atr(h,l,c,20)
    return d

filas = []
for nom, ruta, U, CO in INS:
    m1 = pd.read_parquet(ruta); m1["ts"] = pd.to_datetime(m1["ts"])
    m1 = m1.sort_values("ts").reset_index(drop=True)
    ref = velas_ref(m1, 4, ancla_ny=1)
    h,l,c = (ref[x].to_numpy() for x in ("high","low","close"))
    a4 = C.atr(h,l,c,20)
    seq = LM.secuencias(ref, usar_cuerpo=False)
    seq = LM.resuelve(seq, ref, m1, 4, a4)
    seq = seq[(seq.k == 1)].dropna(subset=["nat","rr"]).copy()

    D = diarias(m1)
    # cada setup H4 se asocia a la vela diaria en curso y a la ANTERIOR ya cerrada
    t_ent = ref["fin"].to_numpy()[seq.i_ent.to_numpy()]
    idx = np.searchsorted(D["fin"].to_numpy(), t_ent, side="left")
    ok = (idx > 0) & (idx < len(D))
    seq, idx = seq[ok].copy(), idx[ok]
    prev = idx - 1                                   # la diaria ya cerrada
    for col in ("high","low","close","crt_dir","atrD"):
        seq["d_"+col] = D[col].to_numpy()[prev]
    # la diaria EN CURSO, pero SOLO hasta el cierre de la vela de entrada.
    # Usar el maximo y el minimo del dia entero seria mirar al futuro: incluye
    # barras posteriores a la entrada, y para una compra el minimo del dia baja
    # justamente cuando la operacion sale mal. Se acumula con las velas H4.
    rf = ref.copy()
    rf["did"] = np.searchsorted(D["fin"].to_numpy(), rf["fin"].to_numpy(), side="left")
    rf["run_hi"] = rf.groupby("did")["high"].cummax()
    rf["run_lo"] = rf.groupby("did")["low"].cummin()
    seq["dc_high"] = rf["run_hi"].to_numpy()[seq.i_ent.to_numpy()]
    seq["dc_low"]  = rf["run_lo"].to_numpy()[seq.i_ent.to_numpy()]
    seq["ins"] = nom; seq["U"] = U; seq["CO"] = CO
    filas.append(seq)

t = pd.concat(filas, ignore_index=True)
lado = np.where(t.alcista, 1, -1)
t["R"] = np.where(t.nat > 0, t.rr, -1.0)
t["riesgo_u"] = (t.entrada - t.stop).abs()/t.U
t["Rneto"] = t.R - t.CO/t.riesgo_u

# ── las cinco lecturas del contexto ────────────────────────────────────────
t["f1_acuerdo"]  = t.d_crt_dir.to_numpy() == lado
t["f2_obj_dentro"] = (t.objetivo <= t.d_high) & (t.objetivo >= t.d_low)
t["f3_dist"]     = (t.objetivo - t.entrada).abs()/t.d_atrD
t["f4_ya_barrio"] = np.where(t.alcista, t.dc_low < t.d_low, t.dc_high > t.d_high)
t["f5_pos"]      = (t.entrada - t.d_low)/(t.d_high - t.d_low).replace(0, np.nan)

def linea(etq, g):
    if len(g) < 100: return None
    x = g.R.to_numpy(); ee = x.std(ddof=1)/np.sqrt(len(x))
    z = x.mean()/ee
    print(f"     {etq:42s} n={len(g):>5,}  bruta {x.mean():>+6.3f} "
          f"[{x.mean()-1.96*ee:+.3f},{x.mean()+1.96*ee:+.3f}]  z {z:>+5.2f}"
          f"   NETA {g.Rneto.mean():>+6.3f}{'   <<<' if g.Rneto.mean() > 0 and z > 2.58 else ''}")
    return x.mean()

print("="*108)
print("¿SEPARA LA VELA DIARIA?  ·  liquidez simple en H4, cuatro instrumentos, 2020-2026")
print("  base a batir: bruta +0,085 R, coste 0,070 R, neta -0,023 R")
print("  cinco contrastes -> el umbral honesto es z > 2,58, no z > 1,96")
print("="*108)
linea("TODOS (sin filtrar)", t)

print("\n  1 · ¿coincide con el CRT de la vela diaria anterior?")
linea("de acuerdo con la diaria", t[t.f1_acuerdo])
linea("la diaria no dice nada o dice lo contrario", t[~t.f1_acuerdo])

print("\n  2 · ¿el objetivo cae DENTRO del rango de la diaria anterior?")
linea("objetivo dentro del rango diario", t[t.f2_obj_dentro])
linea("objetivo fuera: pide que la diaria se extienda", t[~t.f2_obj_dentro])

print("\n  3 · distancia al objetivo en ATR diario")
q = pd.qcut(t.f3_dist, 4, labels=False, duplicates="drop")
for i in range(4):
    g = t[q == i]
    if len(g): linea(f"cuartil {i+1}  ({g.f3_dist.min():.2f}–{g.f3_dist.max():.2f} ATR-D)", g)

print("\n  4 · ¿la diaria en curso ya barrió a la anterior a favor?")
linea("ya barrió a favor", t[t.f4_ya_barrio])
linea("todavía no", t[~t.f4_ya_barrio])

print("\n  5 · posición de la entrada dentro del rango diario anterior")
q = pd.qcut(t.f5_pos.clip(-1,2), 4, labels=False, duplicates="drop")
for i in range(4):
    g = t[q == i]
    if len(g): linea(f"cuartil {i+1}", g)

t.to_csv("data/contexto_diario.csv", index=False)
