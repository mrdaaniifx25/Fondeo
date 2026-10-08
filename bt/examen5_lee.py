"""Analizador del volcado del bloque 5: entradas, DESCARTES y confianza.

Se escribe y se prueba ANTES de que el haga el bloque. En el bloque 4 esa
disciplina evito perder cuatro horas de trabajo suyo; aqui hay ademas un formato
nuevo -las lineas de DESCARTA- que conviene tener leido antes.

  python3 bt/examen5_lee.py [fichero]
"""
import re, sys
import numpy as np, pandas as pd

COSTE = 1.43
OP = re.compile(
    r"^S(?P<ses>\d+) · (?P<h>\d\d):(?P<m>\d\d) (?P<lado>COMPRA|VENTA) ent (?P<ent>[\d.]+) "
    r"sl (?P<sl>[\d.]+) \((?P<rgo>[\d.]+)p\) tp (?P<tp>[\d.]+) -> (?P<mot>\S+) "
    r"(?P<R>[+-][\d.]+) R a las (?P<hs>\d\d):(?P<ms>\d\d)"
    r"(?: \[t\+(?P<t>\d+)m T(?P<tanda>\d+)\])?"
    r"(?: \{(?P<conf>claro|normal|dudando)\})?"
    r"(?P<ind> \[ind\])?"
    r"(?: \| por: (?P<por>[^|·\n]+?))?"
    r"(?: \| falló: (?P<fallo>[^|·\n]+?))?"
    r"(?: · (?P<nota>.+))?\s*$")
DES = re.compile(
    r"^S(?P<ses>\d+) · (?P<h>\d\d):(?P<m>\d\d) DESCARTA (?P<lado>COMPRA|VENTA) "
    r"en (?P<ent>[\d.]+) \((?P<rgo>[\d.]+)p\) · (?P<motivo>[^\[·\n]+?)"
    r"(?: \[t\+(?P<t>\d+)m T(?P<tanda>\d+)\])?"
    r"(?P<ind> \[ind\])?\s*$")
CTA = re.compile(r"^\s+intento (?P<n>\d+): (?P<estado>PASA|REVIENTA|en curso)"
                 r"(?: con (?P<saldo>[\d.]+) ?[€$])?(?: en la sesión (?P<ses>\d+))?")

def lee(ruta):
    ops, des, cuentas, vacias = [], [], [], 0
    for l in open(ruta, encoding="utf-8"):
        l = l.rstrip("\n")
        if not l.strip(): continue
        if "SIN OPERACIONES" in l: vacias += 1; continue
        m = OP.match(l)
        if m:
            d = m.groupdict(); rgo = float(d["rgo"]); R = float(d["R"])
            ops.append(dict(ses=int(d["ses"]), min=int(d["h"])*60+int(d["m"]),
                salida=int(d["hs"])*60+int(d["ms"]),
                lado=1 if d["lado"] == "COMPRA" else -1, ent=float(d["ent"]),
                sl=float(d["sl"]), tp=float(d["tp"]), rgo=rgo, mot=d["mot"], R=R,
                neta=R - COSTE/rgo, t=int(d["t"]) if d["t"] else None,
                tanda=int(d["tanda"]) if d["tanda"] else None,
                conf=d["conf"] or "", ind=bool(d["ind"]),
                por=(d["por"] or "").strip(), fallo=(d["fallo"] or "").strip(),
                nota=(d["nota"] or "").strip()))
            continue
        m = DES.match(l)
        if m:
            d = m.groupdict()
            des.append(dict(ses=int(d["ses"]), min=int(d["h"])*60+int(d["m"]),
                lado=1 if d["lado"] == "COMPRA" else -1, ent=float(d["ent"]),
                rgo=float(d["rgo"]), motivo=d["motivo"].strip(),
                t=int(d["t"]) if d["t"] else None,
                tanda=int(d["tanda"]) if d["tanda"] else None, ind=bool(d["ind"])))
            continue
        c = CTA.match(l)
        if c:
            g = c.groupdict()
            cuentas.append(dict(n=int(g["n"]), estado=g["estado"],
                saldo=float(g["saldo"].replace(".","")) if g["saldo"] else None,
                ses=int(g["ses"]) if g["ses"] else None))
    return pd.DataFrame(ops), pd.DataFrame(des), pd.DataFrame(cuentas), vacias

if __name__ == "__main__":
    o, d, c, vac = lee(sys.argv[1] if len(sys.argv) > 1 else "data/examen5_prueba.txt")
    print(f"{len(o)} entradas · {len(d)} descartes · {vac} sesiones sin operar · "
          f"{len(c)} líneas de cuenta")
    if len(o):
        r = o[o.mot.isin(["TP","SL"])]
        print(f"  acierto {100*(r.mot=='TP').mean():.1f} %  ·  R neta/op {o.neta.mean():+.3f}")
        print(f"  con confianza marcada: {(o.conf!='').sum()} de {len(o)}  ·  "
              f"reparto {dict(o[o.conf!=''].conf.value_counts())}")
        print(f"  con indicador: {int(o.ind.sum())} de {len(o)}")
        print(f"  con nota libre: {(o.nota!='').sum()}  ·  con diagnóstico: {(o.fallo!='').sum()}")
    if len(d):
        print(f"  motivos de descarte: {dict(d.motivo.value_counts())}")
        print(f"  descartes con indicador: {int(d.ind.sum())} de {len(d)}")
        print(f"  stop mediano del descarte: {d.rgo.median():.1f} p")
    if len(c):
        print(f"  cuentas: {(c.estado=='PASA').sum()} superadas · "
              f"{(c.estado=='REVIENTA').sum()} reventadas · "
              f"{(c.estado=='en curso').sum()} en curso")
