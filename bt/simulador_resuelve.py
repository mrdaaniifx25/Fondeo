"""Resuelve las decisiones del simulador contra los datos M1 y saca el informe.

Uso: python3 bt/simulador_resuelve.py data/simulador_respuestas_1.txt
El fichero de entrada es lo que copia la pagina, una linea por caso.
"""
import re, sys, numpy as np, pandas as pd
from math import comb, sqrt

U, COSTE, TZ = 0.0001, 1.43, "Europe/Madrid"
ENTRADA = sys.argv[1] if len(sys.argv) > 1 else "data/simulador_respuestas_1.txt"

filas = []
for l in open(ENTRADA):
    m = re.match(r"(\d+) (\S+) (\d\d:\d\d) \(\+(\d+)\) · (\S+)", l.strip())
    if not m: continue
    n, dia, hora, av, acc = m.groups()
    d = dict(n=int(n), dia=dia, hora=hora, avance=int(av), accion=acc)
    if acc != "PASO":
        e = re.search(r"ent ([\d.]+) stop ([\d.]+) \(([\d.]+)p\)", l)
        d.update(lado=1 if acc == "COMPRA" else -1, entrada=float(e.group(1)),
                 stop=float(e.group(2)), rgo=float(e.group(3)))
        # Desde el bloque 50-100 el objetivo se arrastra a mano y ya no es
        # siempre 1:2, asi que se lee el declarado y solo se supone si falta.
        o = re.search(r"obj ([\d.]+)", l)
        d["obj"] = float(o.group(1)) if o else None
    nota = l.split("·")[-1].strip()
    d["nota"] = nota if nota and not nota.startswith(("COMPRA","VENTA","PASO")) else ""
    filas.append(d)
d = pd.DataFrame(filas)
e = d[d.accion != "PASO"].copy()

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1.ts); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
loc = m1["loc"].to_numpy(); H = m1.high.to_numpy(); L = m1.low.to_numpy(); C = m1.close.to_numpy()
s = m1.set_index("loc").close
h1 = s.resample("1h").last().dropna(); m15 = s.resample("15min").last().dropna()

def direccion(se, t, k, minutos):
    """signo de las ultimas k barras REALMENTE CERRADAS antes de t.

    El indice son horas de apertura: hay que restar la duracion de la vela
    antes de buscar, o se lee el cierre de una vela todavia en formacion.
    """
    i = se.index.searchsorted(t - pd.Timedelta(minutes=minutos), side="right") - 1
    return 0 if i < k else int(np.sign(se.iloc[i] - se.iloc[i-k]))

R, mot, fav = [], [], []
for r in e.itertuples():
    t0 = pd.Timestamp(f"{r.dia} {r.hora}") + pd.Timedelta(minutes=5)   # entra al cierre de esa vela
    t1 = pd.Timestamp(r.dia) + pd.Timedelta(hours=22)
    j0 = int(np.searchsorted(loc, np.datetime64(t0), side="left"))
    j1 = max(int(np.searchsorted(loc, np.datetime64(t1), side="left")), j0+1)
    rgo = abs(r.entrada - r.stop)
    tp = r.obj if getattr(r, "obj", None) else r.entrada + 2*rgo*r.lado
    hh, ll = H[j0:j1], L[j0:j1]
    gt, gs = ((hh >= tp, ll <= r.stop) if r.lado > 0 else (ll <= tp, hh >= r.stop))
    it  = int(np.argmax(gt)) if gt.any() else 10**9
    isl = int(np.argmax(gs)) if gs.any() else 10**9
    if it == 10**9 and isl == 10**9:
        sal = C[j1-1]; R.append(((sal-r.entrada) if r.lado > 0 else (r.entrada-sal))/rgo); mot.append("cierre")
    elif isl <= it: R.append(-1.0); mot.append("SL")
    else: R.append(2.0); mot.append("TP")
    fav.append(direccion(h1, t0, 4, 60) == r.lado and direccion(m15, t0, 4, 15) == r.lado)
e["R"] = R; e["motivo"] = mot; e["fav"] = fav; e["neto"] = e.R - COSTE/e.rgo
e.to_csv(ENTRADA.replace("respuestas", "resuelto").replace(".txt", ".csv"), index=False)

n = len(e); k = int((e.motivo == "TP").sum()); p = k/n
z = 1.96
alto = (p + z*z/(2*n) + z*sqrt(p*(1-p)/n + z*z/(4*n*n)))/(1 + z*z/n)
bajo = (p + z*z/(2*n) - z*sqrt(p*(1-p)/n + z*z/(4*n*n)))/(1 + z*z/n)
pv = sum(comb(n,i)*(1/3)**i*(2/3)**(n-i) for i in range(k, n+1))
gb, pb = e.R[e.R > 0].sum(), -e.R[e.R < 0].sum()
gn, pn = e.neto[e.neto > 0].sum(), -e.neto[e.neto < 0].sum()

print("=" * 72)
print(f"{len(d)} decisiones · {n} entradas · {len(d)-n} pasos")
print("=" * 72)
print(f"  TP {k} · SL {int((e.motivo=='SL').sum())} · sin resolver {int((e.motivo=='cierre').sum())}")
print(f"  ACIERTO {100*p:.1f} %   ·   intervalo 95 % de {100*bajo:.1f} % a {100*alto:.1f} %")
print(f"  contra el 33,3 % geométrico: p = {pv:.3f}")
print(f"  R bruta/op {e.R.mean():+.3f} · R neta/op {e.neto.mean():+.3f} · suma neta {e.neto.sum():+.2f} R")
print(f"  profit factor bruto {gb/pb:.2f} · neto {gn/pn:.2f} · con 100 € de riesgo {e.neto.sum()*100:+.0f} €")

def corte(nom, grupos):
    print(f"\n{nom}")
    print(f"  {'':<42}{'n':>4}{'%TP':>7}{'R bruta':>10}{'R neta':>9}{'suma':>9}")
    for et, m in grupos:
        x = e[m]
        if len(x) < 3: continue
        print(f"  {et:<42}{len(x):>4}{100*(x.motivo=='TP').mean():>6.0f}%"
              f"{x.R.mean():>+10.3f}{x.neto.mean():>+9.3f}{x.neto.sum():>+9.2f}")

corte("POR TAMAÑO DE STOP", [("5 pips o menos", e.rgo <= 5), ("6 a 8", e.rgo.between(6,8)),
                             ("9 a 10", e.rgo.between(9,10)), ("más de 10", e.rgo > 10)])
corte("POR CONTEXTO", [("H1 y M15 a favor", e.fav), ("el resto", ~e.fav)])
corte("POR CUÁNTO ESPERÓ", [("entra en la vela del toque", e.avance == 0),
                            ("espera 1-3 velas", e.avance.between(1,3)), ("espera 4 o más", e.avance >= 4)])
corte("POR DIRECCIÓN", [("compras", e.lado > 0), ("ventas", e.lado < 0)])
corte("LAS DOS REGLAS QUE YA SABÍAMOS  (post hoc)",
      [("stop >= 9 y contexto a favor", (e.rgo >= 9) & e.fav),
       ("una de las dos", ((e.rgo >= 9) ^ e.fav)),
       ("ninguna de las dos", (e.rgo < 9) & (~e.fav))])
