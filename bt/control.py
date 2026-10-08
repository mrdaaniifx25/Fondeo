"""Controles para distinguir 'la estrategia pierde' de 'la estrategia no tiene
ninguna ventaja'.

  A) Verificacion manual de una operacion, paso a paso, contra los datos crudos.
  B) Entrada ALEATORIA: mismas velas de senal y mismas distancias de stop, pero
     direccion echada a suerte. Si el resultado es indistinguible del real, las
     cuatro confirmaciones no aportan informacion.
  C) Prueba binomial del win rate contra el equilibrio teorico.
"""
import sys, numpy as np, pandas as pd
from math import comb
sys.path.insert(0, "bt")
from estrategia_ls import Config, construir_senales, simular, metricas, PIP

m1 = pd.read_parquet("data/eurusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
cfg = Config()
m5, _ = construir_senales(m1, cfg)
tr, _ = simular(m5, m1, cfg)

# ── A) verificacion manual ──────────────────────────────────────────────────
print("=== A) VERIFICACION MANUAL DE UNA OPERACION ===")
t = tr.iloc[7]
fila = m5[m5.ts == t.ts].iloc[0]
print(f"Senal M5 en {t.ts} UTC  ({t['dir']})")
print(f"  vela M5      O={fila.open:.5f} H={fila.high:.5f} L={fila.low:.5f} C={fila.close:.5f}")
print(f"  vela M5 ant. O={m5[m5.ts<t.ts].iloc[-1].open:.5f} C={m5[m5.ts<t.ts].iloc[-1].close:.5f}"
      f"   -> envolvente: cuerpo actual engulle al anterior")
print(f"  H1 en curso  apertura={fila.h1_op:.5f} max={fila.h1_hi:.5f} min={fila.h1_lo:.5f}")
print(f"  H4 en curso  apertura={fila.h4_op:.5f} max={fila.h4_hi:.5f} min={fila.h4_lo:.5f}")
niv = fila.niv_corto if t['dir'] == "corto" else fila.niv_largo
print(f"  nivel barrido = {niv:.5f}")
if t['dir'] == "corto":
    print(f"  LS H1: max {fila.h1_hi:.5f} > nivel {niv:.5f} ? {fila.h1_hi>niv}"
          f" | cuerpo max(ap,cierre)={max(fila.h1_op,fila.close):.5f} < nivel ? {max(fila.h1_op,fila.close)<niv}")
    print(f"  LS H4: max {fila.h4_hi:.5f} > nivel {niv:.5f} ? {fila.h4_hi>niv}"
          f" | cuerpo max(ap,cierre)={max(fila.h4_op,fila.close):.5f} < nivel ? {max(fila.h4_op,fila.close)<niv}")
print(f"  entrada={t.entrada:.5f} SL={t.sl:.5f} TP={t.tp:.5f} "
      f"riesgo={t.riesgo_pips:.1f} pips")
sub = m1[(m1.ts > t.ts) & (m1.ts <= t.salida_ts)]
print(f"  resolucion en M1: {len(sub)} velas hasta {t.salida_ts}, "
      f"max={sub.high.max():.5f} min={sub.low.min():.5f} -> {t.motivo} ({t.R:+.3f}R)")

# ── B) control con direccion aleatoria ──────────────────────────────────────
print("\n=== B) CONTROL: MISMAS SENALES, DIRECCION ALEATORIA ===")
t1 = m1["ts"].to_numpy(); hh, ll = m1["high"].to_numpy(), m1["low"].to_numpy()
cierre = m1["close"].to_numpy()
cand = m5[(m5.sig_corto | m5.sig_largo)]

def corrida(semilla):
    rng = np.random.default_rng(semilla)
    libre = np.datetime64("1970-01-01"); Rs = []
    for r in cand.itertuples():
        ets = np.datetime64(r.ts + pd.Timedelta(minutes=5))
        if ets < libre: continue
        corto = rng.random() < 0.5                    # <-- moneda al aire
        ent = r.close
        if corto:
            sl = max(r.h1_hi, r.high) + cfg.sl_buffer_pips*PIP; riesgo = sl-ent
            tp = ent - cfg.rr*riesgo
        else:
            sl = min(r.h1_lo, r.low) - cfg.sl_buffer_pips*PIP; riesgo = ent-sl
            tp = ent + cfg.rr*riesgo
        if riesgo <= 0: continue
        i0 = int(np.searchsorted(t1, ets)); i1 = min(i0+cfg.max_trade_horas*60, len(t1))
        if i0 >= len(t1): continue
        a, b = hh[i0:i1], ll[i0:i1]
        gsl, gtp = (a>=sl, b<=tp) if corto else (b<=sl, a>=tp)
        isl = int(np.argmax(gsl)) if gsl.any() else 10**9
        itp = int(np.argmax(gtp)) if gtp.any() else 10**9
        if isl==10**9 and itp==10**9: sal, ifin = cierre[i1-1], (i1-i0)-1
        elif isl <= itp: sal, ifin = sl, isl
        else: sal, ifin = tp, itp
        bruto = (ent-sal) if corto else (sal-ent)
        Rs.append((bruto/PIP - cfg.coste_pips)/(riesgo/PIP))
        libre = t1[i0+ifin]
    return np.array(Rs)

res = [corrida(s) for s in range(30)]
wr = np.array([100*(r>0).mean() for r in res])
rt = np.array([r.sum() for r in res])
print(f"  30 corridas aleatorias:")
print(f"    win rate  media {wr.mean():.2f}%  (rango {wr.min():.2f} - {wr.max():.2f})")
print(f"    R total   media {rt.mean():+.2f}  (rango {rt.min():+.2f} - {rt.max():+.2f})")
print(f"  ESTRATEGIA REAL:")
print(f"    win rate  {100*(tr.R>0).mean():.2f}%   R total {tr.R.sum():+.2f}")
z = (tr.R.sum() - rt.mean())/rt.std(ddof=1)
print(f"  -> la estrategia real queda a {z:+.2f} desviaciones tipicas del azar")

# ── C) prueba binomial ──────────────────────────────────────────────────────
print("\n=== C) PRUEBA BINOMIAL DEL WIN RATE (objetivo 1R -> equilibrio 50%) ===")
dec = tr[tr.motivo.isin(["TP","SL"])]
n, k = len(dec), int((dec.motivo=="TP").sum())
p_dos_colas = sum(comb(n,i)*0.5**n for i in range(0,min(k,n-k)+1))*2
print(f"  {k} aciertos de {n} decididas = {100*k/n:.2f}%")
print(f"  p-valor (bilateral) contra 50% = {min(1.0,p_dos_colas):.4f}")
print("  p alto = indistinguible de una moneda.")
