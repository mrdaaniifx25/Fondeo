"""Lo mas simple que se puede defender: optimizar la SUPERVIVENCIA, no la ventaja.

Pre-registro: docs/PREREGISTRO_lo_simple.md

Supone explicitamente que la entrada NO tiene ventaja (esperanza cero), que es
lo unico que tres meses de medicion han podido establecer. Lo que se optimiza
es la probabilidad de pasar las dos fases del examen de FundingPips 10k, que es
un problema de varianza y de limites, no de ventaja.

  python3 bt/lo_simple.py
"""
import numpy as np, sys

N, DIAS = 20000, 300
F1, F2, DIA, TOT = 0.08, 0.05, 0.03, 0.10
COSTE, RR = 0.10, 2.0

def acierto(edge, rr=RR, coste=COSTE):
    """p tal que p*rr-(1-p)-coste = edge."""
    return (1.0 + coste + edge) / (1.0 + rr)

def carrera(edge, rg, nd, regla, semilla=7, n=N, dias=DIAS):
    """Devuelve (p_fase1, p_las_dos, dias_mediana, %muerte_diaria, %muerte_total)."""
    rng = np.random.default_rng(semilla)
    p = acierto(edge)
    saldo = np.zeros(n)
    fase = np.zeros(n, int)
    vivo = np.ones(n, bool)
    meta = np.full(n, F1)
    llego1 = np.zeros(n, bool)
    dia_fin = np.full(n, -1, int)
    muerte = np.zeros(n, int)          # 1 diaria, 2 total
    for d in range(dias):
        if not vivo.any():
            break
        idx = np.nonzero(vivo)[0]
        k = len(idx)
        dpl = np.zeros(k)              # P&L del dia, en fraccion de cuenta
        parado = np.zeros(k, bool)
        roto = np.zeros(k, bool)
        for _ in range(nd):
            act = ~parado & ~roto
            if not act.any():
                break
            gana = rng.random(k) < p
            r = (np.where(gana, RR, -1.0) - COSTE) * rg
            dpl = np.where(act, dpl + r, dpl)
            roto |= (dpl <= -DIA)
            if regla == "B":           # parar tras la primera perdida
                parado |= act & ~gana
            elif regla == "C":         # parar tras la primera ganancia
                parado |= act & gana
            elif regla == "D":         # parar al tocar +-2R
                parado |= act & (np.abs(dpl) >= 2.0 * rg)
        saldo[idx] += dpl
        fuera = roto | (saldo[idx] <= -TOT)
        muerte[idx[roto]] = 1
        muerte[idx[~roto & fuera]] = 2
        vivo[idx[fuera]] = False
        ok = np.nonzero(vivo)[0]
        if not len(ok):
            continue
        paso = saldo[ok] >= meta[ok]
        sube = ok[paso & (fase[ok] == 0)]
        fin = ok[paso & (fase[ok] == 1)]
        llego1[sube] = True
        fase[sube] = 1
        saldo[sube] = 0.0
        meta[sube] = F2
        fase[fin] = 2
        dia_fin[fin] = d
        vivo[fin] = False
    dos = fase == 2
    med = float(np.median(dia_fin[dos])) if dos.any() else float("nan")
    return llego1.mean(), dos.mean(), med, (muerte == 1).mean(), (muerte == 2).mean()

RIESGOS = (0.0025, 0.005, 0.0075, 0.010, 0.015, 0.020)
print("FundingPips 10k · fase1 +8 % · fase2 +5 % · dia -3 % · total -10 %")
print(f"R:R 1:2 · coste {COSTE:.2f} R · {N} cuentas · tope {DIAS} dias habiles")
print(f"VENTAJA CERO -> acierto {100*acierto(0.0):.2f} %\n")

print("=" * 78)
print("1 · RIESGO x OPERACIONES-DIA  (sin regla de cierre de dia)   % pasa LAS DOS")
print("=" * 78)
print(f"  {'ops/dia':>8}" + "".join(f"{f'{100*r:.2f}%':>10}" for r in RIESGOS))
mejor = []
for nd in (1, 2, 3, 4):
    fila = f"  {nd:>8}"
    for rg in RIESGOS:
        if nd * rg > DIA + 1e-9:
            fila += f"{'—':>10}"
            continue
        _, dos, _, _, _ = carrera(0.0, rg, nd, "A")
        mejor.append((dos, rg, nd))
        fila += f"{f'{100*dos:.1f}%':>10}"
    print(fila); sys.stdout.flush()

mejor.sort(reverse=True)
print(f"\n  mejores tres celdas sin regla:")
for dos, rg, nd in mejor[:3]:
    print(f"    riesgo {100*rg:.2f} % x {nd} ops/dia  ->  {100*dos:.1f} %")
sys.stdout.flush()

print()
print("=" * 78)
print("2 · REGLA DE CIERRE DE DIA, en las tres mejores celdas")
print("=" * 78)
NOM = {"A": "sin regla", "B": "parar tras 1a perdida", "C": "parar tras 1a ganancia",
       "D": "parar al tocar +-2R"}
tabla = []
for dos0, rg, nd in mejor[:3]:
    print(f"\n  riesgo {100*rg:.2f} % x {nd} ops/dia")
    print(f"    {'regla':<24}{'fase1':>8}{'LAS DOS':>10}{'dias med':>10}{'mu.diaria':>11}{'mu.total':>10}")
    for rr_ in ("A", "B", "C", "D"):
        f1, dos, med, m1, m2 = carrera(0.0, rg, nd, rr_)
        tabla.append((dos, rg, nd, rr_))
        print(f"    {NOM[rr_]:<24}{100*f1:>7.1f}%{100*dos:>9.1f}%{med:>10.0f}{100*m1:>10.1f}%{100*m2:>9.1f}%")
        sys.stdout.flush()

tabla.sort(reverse=True)
dosb, rgb, ndb, rb = tabla[0]
print(f"\n  GANADORA: riesgo {100*rgb:.2f} % x {ndb} ops/dia · {NOM[rb]} -> {100*dosb:.1f} %")
sys.stdout.flush()

print()
print("=" * 78)
print(f"3 · QUE PASA SI SI HAY VENTAJA  (celda ganadora: {100*rgb:.2f} % x {ndb}, {NOM[rb]})")
print("=" * 78)
print(f"    {'ventaja R':>10}{'acierto':>9}{'fase1':>8}{'LAS DOS':>10}{'dias med':>10}")
for e in (-0.05, -0.02, 0.0, 0.02, 0.05, 0.10):
    f1, dos, med, _, _ = carrera(e, rgb, ndb, rb)
    print(f"    {e:>+10.2f}{100*acierto(e):>8.1f}%{100*f1:>7.1f}%{100*dos:>9.1f}%{med:>10.0f}")
    sys.stdout.flush()

print()
print("=" * 78)
print("4 · CONTROL: la misma celda con el limite diario DESACTIVADO")
print("=" * 78)
DIA_ORIG = DIA
DIA = 1.0
f1, dos, med, m1, m2 = carrera(0.0, rgb, ndb, rb)
print(f"    sin limite diario  fase1 {100*f1:.1f} %  LAS DOS {100*dos:.1f} %  dias {med:.0f}")
DIA = DIA_ORIG
print("    (la barrera teorica sin coste ni limite diario: 10/(8+10) = 55,6 % para la fase 1)")

print()
print("=" * 78)
print("5 · YA FONDEADO: 12 meses, 10.000 EUR, reparto 80 % para el")
print("=" * 78)

def fondeado(edge, rg=0.005, nd=4, meses=12, dias_mes=21, reparto=0.80,
             semilla=11, n=20000, retira=True):
    """Simula la cuenta fondeada. Retira el beneficio al cierre de cada mes.
    Devuelve (media EUR/mes, P(mes >= 300 EUR), P(revienta en 12 meses))."""
    rng = np.random.default_rng(semilla)
    p = acierto(edge)
    CUENTA = 10000.0
    saldo = np.zeros(n)
    vivo = np.ones(n, bool)
    cobrado = np.zeros(n)
    meses_vivo = np.zeros(n)
    buenos = np.zeros(n)
    for m in range(meses):
        ini_mes = saldo.copy()
        for d in range(dias_mes):
            if not vivo.any():
                break
            idx = np.nonzero(vivo)[0]
            k = len(idx)
            dpl = np.zeros(k)
            parado = np.zeros(k, bool)
            roto = np.zeros(k, bool)
            for _ in range(nd):
                act = ~parado & ~roto
                if not act.any():
                    break
                gana = rng.random(k) < p
                r = (np.where(gana, RR, -1.0) - COSTE) * rg
                dpl = np.where(act, dpl + r, dpl)
                roto |= (dpl <= -DIA)
                parado |= act & gana          # parar tras la primera ganancia
            saldo[idx] += dpl
            fuera = roto | (saldo[idx] <= -TOT)
            vivo[idx[fuera]] = False
        ok = np.nonzero(vivo)[0]
        meses_vivo[ok] += 1
        if not len(ok):
            break
        gan = np.maximum(saldo[ok] - ini_mes[ok], 0.0)
        eur = gan * CUENTA * reparto
        cobrado[ok] += eur
        buenos[ok] += (eur >= 300.0)
        if retira:
            saldo[ok] -= np.maximum(saldo[ok] - ini_mes[ok], 0.0)
    return cobrado.mean() / meses, (buenos / meses).mean(), 1.0 - vivo.mean()

print(f"    riesgo 0,50 % · 4 ops/dia · parar tras la primera ganancia · 21 dias/mes")
print(f"    {'ventaja R':>10}{'EUR/mes':>10}{'P(mes>=300)':>13}{'revienta 12m':>14}")
for e in (-0.05, -0.02, 0.0, 0.02, 0.05, 0.09, 0.15):
    eur, p300, rev = fondeado(e)
    print(f"    {e:>+10.2f}{eur:>10.0f}{100*p300:>12.1f}%{100*rev:>13.1f}%")
    sys.stdout.flush()

print()
print("=" * 78)
print("6 · LA CUENTA DE LA SERVILLETA: que ventaja hace falta")
print("=" * 78)
CUENTA, rg, nd, dm, rep = 10000.0, 0.005, 4, 21, 0.80
ops = nd * dm * 0.60     # ~60 % de las ops: se para el dia tras la 1a ganancia
eur_por_R = CUENTA * rg * rep
print(f"    cuenta 10.000 · riesgo 0,50 % -> {eur_por_R:.0f} EUR por cada R (tras reparto 80 %)")
print(f"    ~{ops:.0f} operaciones al mes")
for objetivo in (300.0, 500.0, 750.0):
    need = objetivo / (ops * eur_por_R)
    print(f"    para {objetivo:>4.0f} EUR/mes hace falta una ventaja de {need:>+6.3f} R por operacion"
          f"   (acierto {100*acierto(need):.1f} % a 1:2)")

print()
print("=" * 78)
print("7 · EL TEOREMA DE LA SERVILLETA: cuanto paga EN TOTAL una cuenta fondeada")
print("=" * 78)
print("    Con ventaja CERO el saldo es una martingala. El teorema del muestreo")
print("    opcional dice que lo que se retira EN TOTAL antes de reventar es el")
print("    colchon, 10 % x 10.000 = 1.000 EUR, por el reparto 0,80 = 800 EUR.")
print("    Y que eso NO depende del tamano de posicion ni de la politica de retiro.\n")

def vida_entera(edge, rg, nd, frac_retiro, semilla=13, n=20000, tope_meses=240):
    """Total retirado hasta reventar (o hasta el tope). frac_retiro del beneficio
    mensual se saca; el resto engorda el colchon."""
    rng = np.random.default_rng(semilla)
    p = acierto(edge)
    CUENTA, dias_mes, rep = 10000.0, 21, 0.80
    saldo = np.zeros(n)
    vivo = np.ones(n, bool)
    cobrado = np.zeros(n)
    for m in range(tope_meses):
        if not vivo.any():
            break
        ini_mes = saldo.copy()
        for d in range(dias_mes):
            if not vivo.any():
                break
            idx = np.nonzero(vivo)[0]
            k = len(idx)
            dpl = np.zeros(k)
            parado = np.zeros(k, bool)
            roto = np.zeros(k, bool)
            for _ in range(nd):
                act = ~parado & ~roto
                if not act.any():
                    break
                gana = rng.random(k) < p
                r = (np.where(gana, RR, -1.0) - COSTE) * rg
                dpl = np.where(act, dpl + r, dpl)
                roto |= (dpl <= -DIA)
                parado |= act & gana
            saldo[idx] += dpl
            fuera = roto | (saldo[idx] <= -TOT)
            vivo[idx[fuera]] = False
        ok = np.nonzero(vivo)[0]
        if not len(ok):
            break
        gan = np.maximum(saldo[ok] - ini_mes[ok], 0.0) * frac_retiro
        cobrado[ok] += gan * CUENTA * rep
        saldo[ok] -= gan
    return cobrado.mean(), 1.0 - vivo.mean()

print(f"    {'riesgo':>8}{'ops/dia':>9}{'retiro':>9}{'total EUR':>12}{'revienta':>11}")
for rg, nd, fr in ((0.0025, 4, 1.0), (0.005, 4, 1.0), (0.010, 2, 1.0),
                   (0.020, 1, 1.0), (0.005, 4, 0.5), (0.005, 4, 0.0)):
    tot, rev = vida_entera(0.0, rg, nd, fr)
    print(f"    {100*rg:>7.2f}%{nd:>9}{100*fr:>8.0f}%{tot:>12.0f}{100*rev:>10.1f}%")
    sys.stdout.flush()
print("\n    (con retiro 0 % no se cobra nada: el dinero se queda dentro y revienta igual)")

print()
print("=" * 78)
print("8 · Y CON VENTAJA, la misma cuenta a vida entera")
print("=" * 78)
print(f"    {'ventaja R':>10}{'total EUR':>12}{'revienta':>11}")
for e in (0.0, 0.02, 0.05, 0.09, 0.15):
    tot, rev = vida_entera(e, 0.005, 4, 1.0)
    print(f"    {e:>+10.2f}{tot:>12.0f}{100*rev:>10.1f}%")
    sys.stdout.flush()

print()
print("=" * 78)
print("9 · LA GESTION DE RIESGO MULTIPLICA UNA VENTAJA; NO LA CREA")
print("=" * 78)
print("    Misma celda, cambiando SOLO que fraccion del beneficio se retira.")
print(f"    {'ventaja R':>10}{'retiro 100%':>13}{'retiro 50%':>12}{'retiro 25%':>12}")
for e in (0.0, 0.02, 0.05, 0.09):
    fila = f"    {e:>+10.2f}"
    for fr in (1.0, 0.5, 0.25):
        tot, _ = vida_entera(e, 0.005, 4, fr)
        fila += f"{tot:>12.0f} "
    print(fila); sys.stdout.flush()
print("\n    Con ventaja cero las tres columnas son la misma: el colchon y nada mas.")
print("    Con ventaja, retirar menos deja crecer el colchon y el total se dispara.")
print("    Eso es exactamente lo que decia el video. Y sigue necesitando la ventaja.")
