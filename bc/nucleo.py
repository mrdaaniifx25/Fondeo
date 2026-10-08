"""Motor del metodo de bctrades. Escrito de cero segun docs/BC_02_especificacion.md.

No importa nada de bt/. Los motores de alli llevan dentro decisiones mias -el
anclaje de la rejilla, que cuenta como cierre "dentro", como se resuelve un
empate- que no son suyas. Reutilizarlos seria arrastrar lo anterior con otro
nombre.
"""
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

HUSOS = {"UTC": "UTC", "NY": "America/New_York",
         "Madrid": "Europe/Madrid", "Broker": "Etc/GMT-2"}

# ─────────────────────────────────────────────────────────────────────────────
#  VELAS
# ─────────────────────────────────────────────────────────────────────────────
def velas(m1: pd.DataFrame, horas: float, huso: str, ancla_h: int = 0) -> pd.DataFrame:
    """Agrega M1 a bloques de `horas`, con la rejilla anclada en el huso dado.

    El bloque empieza a las `ancla_h` de ese huso y se repite cada `horas`. Se
    trabaja sobre la hora local para que el cambio de horario se gestione solo.
    """
    tz = HUSOS[huso]
    loc = pd.DatetimeIndex(m1["ts"]).tz_localize("UTC").tz_convert(tz).tz_localize(None)
    d = m1.copy()
    d["loc"] = loc
    delta = pd.Timedelta(hours=ancla_h)
    paso = f"{int(horas)}h" if horas >= 1 else f"{int(horas*60)}min"
    d["id"] = (d["loc"] - delta).dt.floor(paso) + delta
    g = d.groupby("id").agg(open=("open", "first"), high=("high", "max"),
                            low=("low", "min"), close=("close", "last"),
                            ini=("ts", "min"), fin=("ts", "max"),
                            n=("ts", "size")).reset_index()
    # se exige media vela de datos para no tratar un festivo como vela real
    return g[g.n >= horas * 60 * 0.5].reset_index(drop=True)

# ─────────────────────────────────────────────────────────────────────────────
#  ACTIVACION DE RANGO   ·  BC_02 §3.2
# ─────────────────────────────────────────────────────────────────────────────
def activaciones(v: pd.DataFrame, lectura: str) -> pd.DataFrame:
    """Marca en que velas se ACTIVA un rango, en que direccion y con que objetivo.

    lectura "A"  apertura estricta: la vela abre fuera del rango de la anterior
    lectura "B"  barrido con cierre dentro del CUERPO de la anterior
    lectura "C"  las dos a la vez
    """
    o, h, l, c = (v[x].to_numpy() for x in ("open", "high", "low", "close"))
    ph, pl = np.roll(h, 1), np.roll(l, 1)
    po, pc = np.roll(o, 1), np.roll(c, 1)
    ph[0] = pl[0] = po[0] = pc[0] = np.nan
    cuerpo_alto = np.maximum(po, pc)
    cuerpo_bajo = np.minimum(po, pc)

    abre_debajo = o < pl
    abre_encima = o > ph
    barre_bajo = l < pl
    barre_alto = h > ph
    dentro = (c >= cuerpo_bajo) & (c <= cuerpo_alto)

    if lectura == "A":
        alc, baj = abre_debajo, abre_encima
    elif lectura == "B":
        alc, baj = barre_bajo & dentro, barre_alto & dentro
    elif lectura == "C":
        alc = abre_debajo & barre_bajo & dentro
        baj = abre_encima & barre_alto & dentro
    else:
        raise ValueError(lectura)

    # si se disparan las dos, la vela envuelve a la base: no es activacion limpia
    ambas = alc & baj
    alc, baj = alc & ~ambas, baj & ~ambas

    lado = np.where(alc, 1, np.where(baj, -1, 0))
    objetivo = np.where(alc, ph, np.where(baj, pl, np.nan))
    base_hi = np.where(lado != 0, ph, np.nan)
    base_lo = np.where(lado != 0, pl, np.nan)
    return v.assign(lado=lado, objetivo=objetivo, base_hi=base_hi, base_lo=base_lo)

# ─────────────────────────────────────────────────────────────────────────────
#  VIDA DEL RANGO   ·  BC_02 §3.4
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Rango:
    tf: str
    lado: int
    objetivo: float
    base_hi: float
    base_lo: float
    nace: pd.Timestamp
    muere: object = None    # cuando deja de dar contexto; None = sigue vivo al final
    tomas: int = 1          # doble y triple liquidez  ·  BC_02 §3.6
    reiniciado: bool = False
    vivo: bool = True
    fin_por: str = ""       # completado | descartado | relevado

def vida(v: pd.DataFrame, tf: str) -> list:
    """Recorre las velas y devuelve los rangos con su historia.

    Un rango muere solo cuando el precio CIERRA fuera del rango principal tras
    haber sido reiniciado, o cuando completa su objetivo. Tomar el extremo
    contrario NO lo mata: lo reinicia.
    """
    h, l, c = (v[x].to_numpy() for x in ("high", "low", "close"))
    lado, obj = v["lado"].to_numpy(), v["objetivo"].to_numpy()
    bhi, blo = v["base_hi"].to_numpy(), v["base_lo"].to_numpy()
    fin = v["fin"].to_numpy()

    out, cur = [], None
    for i in range(len(v)):
        if cur is not None and cur.vivo:
            # completado
            llega = (h[i] >= cur.objetivo) if cur.lado > 0 else (l[i] <= cur.objetivo)
            if llega:
                cur.vivo = False
                cur.muere = pd.Timestamp(fin[i]); cur.fin_por = "completado"
            else:
                # El rango se REINICIA cuando el precio vuelve a llevarse el extremo
                # que lo activo -el bajo en un rango alcista-. NO el contrario: el
                # contrario es el objetivo, y esta rama solo se evalua cuando el
                # objetivo no se ha alcanzado, asi que con la lectura anterior era
                # inalcanzable (0 reinicios en 8.575 rangos). BC_01 §3 casos 1 y 2.
                otra = (l[i] < cur.base_lo) if cur.lado > 0 else (h[i] > cur.base_hi)
                if otra:
                    cur.reiniciado = True
                    dentro = (min(cur.base_lo, cur.base_hi) <= c[i]
                              <= max(cur.base_lo, cur.base_hi))
                    if dentro:
                        cur.tomas += 1        # caso 1: doble/triple toma, sigue vivo
                # descarte: tras el reinicio, CIERRE fuera de la estructura  ·  caso 2
                if cur.reiniciado:
                    fuera = (c[i] < cur.base_lo) if cur.lado > 0 else (c[i] > cur.base_hi)
                    if fuera:
                        cur.vivo = False
                        cur.muere = pd.Timestamp(fin[i]); cur.fin_por = "descartado"
        if lado[i] != 0:
            if cur is not None and cur.vivo:
                cur.vivo = False          # un rango nuevo releva al anterior
                cur.muere = pd.Timestamp(fin[i]); cur.fin_por = "relevado"
            cur = Rango(tf, int(lado[i]), float(obj[i]), float(bhi[i]), float(blo[i]),
                        pd.Timestamp(fin[i]))
            out.append(cur)
    return out

def mapa_vivos(rangos: list, v_ejec: pd.DataFrame) -> pd.DataFrame:
    """Para cada vela de ejecucion, que rango de esa TF estaba vivo y en que sentido.

    Un rango solo esta disponible a partir del CIERRE de la vela que lo activa:
    nunca antes. Es lo que evita mirar al futuro.
    """
    if not rangos:
        return pd.DataFrame(index=v_ejec.index,
                            columns=["r_lado", "r_obj", "r_tomas"], dtype=float)
    t = pd.DataFrame([dict(nace=r.nace, muere=r.muere, lado=r.lado, obj=r.objetivo,
                           tomas=r.tomas) for r in rangos]).sort_values("nace")
    m = pd.merge_asof(pd.DataFrame({"ts": v_ejec["fin"].to_numpy()}).sort_values("ts"),
                      t.rename(columns={"nace": "ts"}), on="ts", direction="backward")
    # un rango YA MUERTO no da contexto. Sin esta mascara, un objetivo alcanzado
    # hace dias seguiria contando: merge_asof devuelve el ultimo rango creado, no
    # el ultimo rango vivo.
    muerto = m["muere"].notna() & (m["ts"] >= m["muere"])
    for col in ("lado", "obj", "tomas"):
        m.loc[muerto, col] = np.nan
    return pd.DataFrame({"r_lado": m["lado"].to_numpy(),
                         "r_obj": m["obj"].to_numpy(),
                         "r_tomas": m["tomas"].to_numpy()}, index=v_ejec.index)
