"""El cuarto bloque: 50 sesiones con cuenta de 10.000 y presion de reventar.

Tres contrastes firmados, los mismos de siempre, a una cola y los tres tienen
que salir:

    acierto sobre el 33,3 % geometrico          z > +1,64
    R neta por operacion                        z > +1,64
    diferencia contra la regla, emparejada      z > +1,64

Y lo nuevo del bloque: sus etiquetas. Se comprueba tambien si su diagnostico de
cada stop coincide con lo que hizo el precio despues.

  python3 bt/examen4.py
"""
import json, re, sys
import numpy as np, pandas as pd
from math import sqrt, erf

COSTE, TZ, GEO = 1.43, "Europe/Madrid", 1/3
z  = lambda x: x.mean()/(x.std(ddof=1)/sqrt(len(x)))
p2 = lambda zz: 2*(1-0.5*(1+erf(abs(zz)/sqrt(2))))
p1 = lambda zz: 1-0.5*(1+erf(zz/sqrt(2)))

def fisher(tab):
    """Fisher exacto a dos colas sobre una tabla 2x2, sin scipy."""
    from math import comb
    (a, b), (c, d) = tab
    n, r1, c1 = a+b+c+d, a+b, a+c
    dens = lambda k: comb(r1, k)*comb(n-r1, c1-k)/comb(n, c1)
    p0 = dens(a) * (1 + 1e-9)
    return sum(dens(k) for k in range(max(0, c1-(n-r1)), min(r1, c1)+1) if dens(k) <= p0)

LIN = re.compile(
    r"^S(?P<ses>\d+) · (?P<h>\d\d):(?P<m>\d\d) (?P<lado>COMPRA|VENTA) ent (?P<ent>[\d.]+) "
    r"sl (?P<sl>[\d.]+) \((?P<rgo>[\d.]+)p\) tp (?P<tp>[\d.]+) -> (?P<mot>\S+) "
    r"(?P<R>[+-][\d.]+) R a las (?P<hs>\d\d):(?P<ms>\d\d)"
    r"(?: \[t\+(?P<t>\d+)m T(?P<tanda>\d+)\])?"
    r"(?: \| por: (?P<por>[^|·\n]+?))?"
    r"(?: \| falló: (?P<fallo>[^|·\n]+?))?"
    r"(?: · (?P<nota>.+))?\s*$")

def lee(ruta, dias_json):
    dias = {int(k): pd.Timestamp(v).date() for k, v in json.load(open(dias_json)).items()}
    out, vacias = [], 0
    for l in open(ruta, encoding="utf-8"):
        l = l.rstrip("\n")
        if not l.strip(): continue
        if "SIN OPERACIONES" in l: vacias += 1; continue
        if not re.match(r"^S\d+ · \d", l): continue      # bloque de cuentas y titulos
        m = LIN.match(l)
        if not m: print("NO LEIDA:", l); continue
        d = m.groupdict()
        ent, rgo, R = float(d["ent"]), float(d["rgo"]), float(d["R"])
        out.append(dict(
            ses=int(d["ses"]), dia=dias[int(d["ses"])],
            min=int(d["h"])*60+int(d["m"]), salida=int(d["hs"])*60+int(d["ms"]),
            lado=1 if d["lado"] == "COMPRA" else -1, ent=ent, sl=float(d["sl"]),
            tp=float(d["tp"]), rgo=rgo, mot=d["mot"], R=R, neta=R-COSTE/rgo,
            t=int(d["t"]) if d["t"] else None, tanda=int(d["tanda"]) if d["tanda"] else None,
            por=(d["por"] or "").strip(), fallo=(d["fallo"] or "").strip(),
            nota=(d["nota"] or "").strip()))
    t = pd.DataFrame(out)
    t["dura"] = t.salida - t["min"]
    t["n"] = np.arange(1, len(t)+1)
    return t, sorted(dias.values()), vacias

t, idx, vacias = lee("data/examen_respuestas_4.txt", "data/examen_dias4.json")
res = t[t.mot.isin(["TP", "SL"])]
ac = (res.mot == "TP").mean()
se = sqrt(GEO*(1-GEO)/len(res))
zac = (ac-GEO)/se

print("="*74); print("BLOQUE 4 · 50 SESIONES CON CUENTA"); print("="*74)
print(f"  operaciones            {len(t)}   en {t.ses.nunique()} sesiones "
      f"({vacias} sin operar)  ·  {len(t)/50:.2f} por sesión")
print(f"  desenlaces             TP {(t.mot=='TP').sum()} · SL {(t.mot=='SL').sum()} · "
      f"cierre a las 11:30 {(t.mot=='cierre').sum()}")
print(f"  ACIERTO                {100*ac:.1f} %  sobre {len(res)} resueltas"
      f"   ·   z contra 33,3 % = {zac:+.2f}   (p={p1(zac):.5f})")
print(f"  stop mediano           {t.rgo.median():.1f} p   (media {t.rgo.mean():.1f})")
print(f"  coste sobre riesgo     {100*(COSTE/t.rgo).mean():.1f} %")
print(f"  R BRUTA por operación  {t.R.mean():+.3f}   ·   suma {t.R.sum():+.2f} R")
zn = z(t.neta.to_numpy())
print(f"  R NETA  por operación  {t.neta.mean():+.3f}   ·   z = {zn:+.2f}   (p={p1(zn):.6f})")
print(f"  suma neta              {t.neta.sum():+.2f} R")
suyo = t.groupby("dia").neta.sum().reindex(idx).fillna(0)
zs = z(suyo.to_numpy())
print(f"  por sesión             {suyo.mean():+.3f}   ·   z = {zs:+.2f}")
print(f"  minutos hasta salir    mediana {t.dura.median():.0f}   (media {t.dura.mean():.0f})")

print("\n" + "="*74); print("CONTRA LA REGLA MECÁNICA, EN LOS MISMOS 50 DÍAS"); print("="*74)
g = pd.read_csv("data/examen_regla4.csv")
g["dia"] = pd.to_datetime(g.dia).dt.date
regla = g.groupby("dia").neta.sum().reindex(idx).fillna(0)
dif = suyo - regla
zd = z(dif.to_numpy())
print(f"  regla   {regla.mean():+.3f} R/sesión   ({len(g)} disparos, "
      f"acierto {100*(g[g.motivo!='cierre'].motivo=='TP').mean():.1f} %)")
print(f"  él      {suyo.mean():+.3f} R/sesión   ({len(t)} operaciones)")
print(f"  DIFERENCIA emparejada  {dif.mean():+.3f} R/sesión   ·   z = {zd:+.2f}   "
      f"(p={p1(zd):.7f})")

print("\n" + "="*74); print("LOS TRES UMBRALES FIRMADOS  (z > +1,64, los tres)"); print("="*74)
for nom, val in (("acierto sobre 33,3 %", zac), ("R neta por operación", zn),
                 ("diferencia contra la regla", zd)):
    print(f"  {nom:32s} z = {val:+6.2f}   {'PASA' if val > 1.64 else 'NO PASA'}")

print("\n" + "="*74); print("CANSANCIO · TODO EL BLOQUE EN UNA SOLA TANDA"); print("="*74)
print(f"  marcas de tanda distintas: {sorted(t.tanda.dropna().unique().astype(int))}"
      f"  ·  duración de la sentada: {t.t.max():.0f} min")
mit = len(t)//2
for nom, sub in (("1ª mitad", t.iloc[:mit]), ("2ª mitad", t.iloc[mit:])):
    r = sub[sub.mot.isin(["TP","SL"])]
    print(f"  {nom}  n={len(sub):2d}  acierto {100*(r.mot=='TP').mean():5.1f} %  "
          f"neta {sub.neta.mean():+.3f}  stop {sub.rgo.median():.1f}p")
a, b = t.iloc[:mit], t.iloc[mit:]
ra, rb = a[a.mot.isin(["TP","SL"])], b[b.mot.isin(["TP","SL"])]
tab = [[int((ra.mot=="TP").sum()), int((ra.mot=="SL").sum())],
       [int((rb.mot=="TP").sum()), int((rb.mot=="SL").sum())]]
print(f"  Fisher entre las dos mitades: p = {fisher(tab):.3f}   "
      f"(en los bloques 1 y 2 la caída era de 34 puntos, p = 0,023)")
print("  por tercios de la sentada (minutos desde la primera decisión):")
for lo, hi in ((0,24),(24,48),(48,100)):
    sub = t[(t.t >= lo) & (t.t < hi)]
    r = sub[sub.mot.isin(["TP","SL"])]
    print(f"    t+{lo:02d}-{hi:02d}m  n={len(sub):2d}  acierto {100*(r.mot=='TP').mean():5.1f} %  "
          f"neta {sub.neta.mean():+.3f}")

print("\n" + "="*74); print("ETIQUETAS"); print("="*74)
print(f"  «por qué entro»   usadas en {(t.por!='').sum()} de {len(t)} operaciones")
print(f"  «qué falló»       usadas en {(t.fallo!='').sum()} de {len(t)} operaciones, "
      f"de las cuales {((t.fallo!='') & (t.mot!='SL')).sum()} NO son stops")
print(f"  notas libres      {(t.nota!='').sum()}")
mal = t[(t.fallo!="") & (t.mot!="SL")]
if len(mal):
    print("\n  etiquetas de fallo colgadas de una operación que no perdió:")
    for r in mal.itertuples():
        prev = t[(t.ses==r.ses) & (t.n < r.n)]
        p = prev.iloc[-1] if len(prev) else None
        print(f"    S{r.ses:02d} {r.min//60:02d}:{r.min%60:02d} {r.mot:6s} «{r.fallo}»"
              + (f"   ← anterior de la sesión: {p['min']//60:02d}:{p['min']%60:02d} {p.mot}"
                 if p is not None else "   (no hay anterior)"))
print("\n  reparto de «qué falló», tal como llegó:")
for e, n in t[t.fallo!=""].fallo.value_counts().items():
    print(f"    {e:24s} {n}")

print("\n" + "="*74); print("SU DIAGNÓSTICO DE CADA STOP CONTRA LO QUE HIZO EL PRECIO"); print("="*74)
print("""  Para cada stop se mira que hizo el precio DESPUES de saltarlo, hasta las
  11:30 del mismo dia: si llego a tocar el objetivo que el habia puesto, la
  direccion era buena y lo que fallo fue el sitio -entro pronto, o el stop era
  corto-. Si no llego, la lectura estaba mal.""")
m1 = pd.concat([pd.read_parquet("data/eurusd_m1.parquet"),
                pd.read_parquet("data/eurusd_m1_2026_08.parquet")], ignore_index=True)
m1["ts"] = pd.to_datetime(m1["ts"]); m1 = m1.sort_values("ts").reset_index(drop=True)
m1["loc"] = pd.DatetimeIndex(m1.ts).tz_localize("UTC").tz_convert(TZ).tz_localize(None)
T = m1["loc"].to_numpy(); HI = m1.high.to_numpy(); LO = m1.low.to_numpy()

def llego(r):
    """¿Toco su objetivo entre el minuto en que salto el stop y las 11:30?"""
    ini = np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(minutes=int(r.salida)))
    fin = np.datetime64(pd.Timestamp(r.dia) + pd.Timedelta(hours=11, minutes=30))
    a, b = int(np.searchsorted(T, ini)), int(np.searchsorted(T, fin))
    if b <= a: return None
    return bool((HI[a:b] >= r.tp).any() if r.lado > 0 else (LO[a:b] <= r.tp).any())

sl = t[t.mot == "SL"].copy()
sl["sitio"] = [llego(r) for r in sl.itertuples()]
n_si = int(sl.sitio.sum())
print(f"\n  de los {len(sl)} stops, en {n_si} ({100*n_si/len(sl):.0f} %) el precio SI llego "
      f"despues a su objetivo:")
print("  en esas la direccion era buena y lo que fallo fue el sitio o el stop.\n")
# el diagnostico verdadero de cada stop, corrigiendo el desplazamiento de etiquetas
sl["fallo_real"] = sl.fallo
for r in t[(t.fallo != "") & (t.mot != "SL")].itertuples():
    prev = t[(t.ses == r.ses) & (t.n < r.n) & (t.mot == "SL")]
    if len(prev):
        sl.loc[prev.index[-1], "fallo_real"] = r.fallo
etq = sl[sl.fallo_real != ""]
print(f"  con etiqueta (ya reasignada al stop que le toca): {len(etq)} de {len(sl)}")
print(f"  {'lo que dijo':24s} {'n':>3s}   {'a quién culpa':18s} ¿lo confirma el precio?")
print("  " + "-"*66)
SITIO = {"precipitada", "stopcorto", "tarde"}
def espera(e):
    """Que tendria que haber hecho el precio si su diagnostico es correcto."""
    if bool(SITIO & set(e.split("+"))): return True,  "el sitio"
    if e == "nada":                     return False, "nada, no fue"
    return False, "la lectura"
for e in sorted(etq.fallo_real.unique()):
    s = etq[etq.fallo_real == e]
    esp, nom = espera(e)
    ok_e = int((s.sitio == esp).sum())
    print(f"  {e:24s} {len(s):3d}   culpa {nom:12s} "
          f"acierta {ok_e}/{len(s)}")
ok = int(sum(r.sitio == espera(r.fallo_real)[0] for r in etq.itertuples()))
print(f"\n  se lee bien a si mismo en {ok} de {len(etq)} stops etiquetados "
      f"({100*ok/len(etq):.0f} %) — a cara o cruz saldria 50 %")


print("\n" + "="*74); print("LOS CUATRO BLOQUES JUNTOS"); print("="*74)
todo = [t.assign(bloque=4)]
for b, (f, dj) in enumerate([("data/examen_respuestas_1.txt", "data/examen_dias.json"),
                             ("data/examen_respuestas_2.txt", "data/examen_dias2.json"),
                             ("data/examen_respuestas_3.txt", "data/examen_dias3.json")], 1):
    x, ix, _ = lee(f, dj)
    todo.append(x.assign(bloque=b))
    idx = idx + ix
T4 = pd.concat(todo, ignore_index=True).sort_values(["bloque", "n"])
print(f"  {'':10s} {'opera':>5s} {'ops':>4s} {'acierto':>8s} {'stop':>6s} {'R bruta':>8s} "
      f"{'R neta':>8s} {'z':>7s}")
print("  " + "-"*62)
for b in (1, 2, 3, 4):
    s = T4[T4.bloque == b]; r = s[s.mot.isin(["TP","SL"])]
    print(f"  bloque {b}   {s.ses.nunique():5d} {len(s):4d} {100*(r.mot=='TP').mean():7.1f} % "
          f"{s.rgo.median():5.1f}p {s.R.mean():+8.3f} {s.neta.mean():+8.3f} "
          f"{z(s.neta.to_numpy()):+7.2f}")
r = T4[T4.mot.isin(["TP","SL"])]
acT = (r.mot == "TP").mean(); zT = (acT-GEO)/sqrt(GEO*(1-GEO)/len(r))
znT = z(T4.neta.to_numpy())
print("  " + "-"*62)
print(f"  LOS CUATRO {T4.groupby(['bloque','ses']).ngroups:5d} {len(T4):4d} {100*acT:7.1f} % {T4.rgo.median():5.1f}p "
      f"{T4.R.mean():+8.3f} {T4.neta.mean():+8.3f} {znT:+7.2f}")
print(f"\n  («opera» = sesiones en las que llegó a operar; el bloque completo fueron "
      f"{len(idx)} sesiones)")
print(f"  acierto contra el 33,3 % geométrico:  z = {zT:+.2f}")
print(f"  acierto de equilibrio con su coste:   "
      f"{100*(1+COSTE/T4.rgo.median())/3:.1f} %   ·   tiene {100*acT:.1f} %")
print(f"  suma neta de las {len(T4)} operaciones:   {T4.neta.sum():+.2f} R")

print("\n  ritmo de cada bloque (minutos por sesión, donde hay marca de tiempo):")
for b in (3, 4):
    s = T4[(T4.bloque == b) & T4.t.notna()]
    if not len(s): continue
    print(f"    bloque {b}: {s.t.max():.0f} min de sentada · {s.ses.nunique()} sesiones operadas"
          f" · hora mediana de entrada {int(s['min'].median())//60:02d}:"
          f"{int(s['min'].median())%60:02d}")
for b in (1, 2):
    s = T4[T4.bloque == b]
    print(f"    bloque {b}: sin marca de tiempo · hora mediana de entrada "
          f"{int(s['min'].median())//60:02d}:{int(s['min'].median())%60:02d}")


print("\n" + "="*74); print("LAS CUENTAS · SE REPRODUCE EL LIBRO MAYOR DESDE LAS OPERACIONES")
print("="*74)
CUENTA, LIM_DIA, LIM_TOT, OBJ, DIAS_MIN = 10_000, 500, 1000, 800, 3

def reto(ops, riesgo=0.01, neto=False, verboso=False):
    """Mismas reglas que la pagina: 1 % del inicial por operacion, 5 %/10 %, 8 %."""
    unidad = CUENTA*riesgo
    saldo, ini, diaIni, dias, n = CUENTA, CUENTA, CUENTA, 0, 1
    pasa = revienta = 0
    peor_dia, peor_tot, salidas = 0.0, 0.0, []
    for ses in range(1, 51):
        s = ops[ops.ses == ses]
        diaIni, contado = saldo, False
        for r in s.itertuples():
            saldo += (r.neta if neto else r.R)*unidad
            if not contado: contado = True; dias += 1
            dia, gan = saldo-diaIni, saldo-ini
            peor_dia, peor_tot = min(peor_dia, dia), min(peor_tot, gan)
            fin = None
            if   dia <= -LIM_DIA:              fin, revienta = "REVIENTA (día)", revienta+1
            elif gan <= -LIM_TOT:              fin, revienta = "REVIENTA (total)", revienta+1
            elif gan >= OBJ and dias>=DIAS_MIN: fin, pasa     = "PASA", pasa+1
            if fin:
                salidas.append((n, fin, saldo, ses, dias))
                if verboso:
                    print(f"    intento {n}: {fin:16s} {saldo:9,.0f} $  en la sesión {ses:2d}"
                          f"  ·  {dias} días operados")
                n += 1; saldo = ini = diaIni = CUENTA; dias = 0; contado = False
    if verboso:
        print(f"    intento {n}: en curso         {saldo:9,.0f} $  al acabar el bloque"
              f"  ·  {dias} días operados")
        print(f"\n    peor día dentro de un intento: {peor_dia:+.0f} $ (límite -500)")
        print(f"    peor caída total:              {peor_tot:+.0f} $ (límite -1.000)")
    return pasa, revienta, salidas, saldo

print("  tal cual lo jugó (R bruta, riesgo 1 %):")
pa, rv, sal, fin = reto(t, 0.01, neto=False, verboso=True)
print(f"\n  {pa} superados · {rv} reventados   ·   la simulación predecía 99,9 % de paso"
      f" y 0,1 % de reventón por intento")
ses_por = [sal[0][3]] + [sal[i][3]-sal[i-1][3] for i in range(1, len(sal))]
print(f"  sesiones por intento: {ses_por}  ·  mediana {int(np.median(ses_por))}"
      f"   (la simulación predecía 8 días operados de mediana)")
print(f"  días operados por intento: {[s[4] for s in sal]}")

print("\n  y con el coste real de 1,43 pips descontado, que la página no cobra:")
print(f"  {'riesgo':>7s} {'bruta: pasa/revienta':>22s} {'neta: pasa/revienta':>22s}")
print("  " + "-"*54)
for rg in (0.005, 0.01, 0.02):
    b = reto(t, rg, neto=False); nn = reto(t, rg, neto=True)
    print(f"  {100*rg:6.1f}% {b[0]:>13d} / {b[1]:<8d} {nn[0]:>13d} / {nn[1]:<8d}")
