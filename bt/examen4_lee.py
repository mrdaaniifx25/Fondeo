"""Analizador del volcado del bloque 4, con etiquetas y cuentas.

Se escribe ANTES de que el haga el bloque, para que si al formato le falta algo
se arregle antes y no despues de cuatro horas de trabajo suyo.

  python3 bt/examen4_lee.py <fichero>
"""
import re, sys
import numpy as np, pandas as pd

COSTE = 1.43
LIN = re.compile(
    r"^S(?P<ses>\d+) · (?:"
    r"SIN OPERACIONES"
    r"|(?P<h>\d\d:\d\d) (?P<lado>COMPRA|VENTA) ent (?P<ent>[\d.]+) sl (?P<sl>[\d.]+) "
    r"\((?P<rgo>[\d.]+)p\) tp (?P<tp>[\d.]+) -> (?P<mot>\S+) (?P<R>[+-][\d.]+) R "
    r"a las (?P<hs>\d\d:\d\d)"
    r"(?: \[t\+(?P<t>\d+)m T(?P<tanda>\d+)\])?"
    r"(?: \| por: (?P<por>[^|·\n]+?))?"
    r"(?: \| falló: (?P<fallo>[^|·\n]+?))?"
    r"(?: · (?P<nota>.+))?"
    r")\s*$")
CTA = re.compile(r"^\s+intento (?P<n>\d+): (?P<estado>[A-ZÁÉÍÓÚ]+)(?: con (?P<saldo>[\d.]+) €)?"
                 r"(?: en la sesión (?P<ses>\d+))?")

def lee(ruta):
    ops, cuentas, vacias = [], [], 0
    for l in open(ruta, encoding="utf-8"):
        if not l.strip(): continue
        m = LIN.match(l.rstrip("\n"))
        if m:
            if m.group("h") is None: vacias += 1; continue
            d = m.groupdict()
            rgo = float(d["rgo"]); R = float(d["R"])
            ops.append(dict(ses=int(d["ses"]), hora=d["h"], lado=1 if d["lado"]=="COMPRA" else -1,
                            rgo=rgo, mot=d["mot"], R=R, neta=R-COSTE/rgo,
                            t=int(d["t"]) if d["t"] else None,
                            tanda=int(d["tanda"]) if d["tanda"] else None,
                            por=(d["por"] or "").strip(), fallo=(d["fallo"] or "").strip(),
                            nota=(d["nota"] or "").strip()))
            continue
        c = CTA.match(l.rstrip("\n"))
        if c:
            g = c.groupdict()
            cuentas.append(dict(n=int(g["n"]), estado=g["estado"],
                                saldo=float(g["saldo"].replace(".","")) if g["saldo"] else None,
                                ses=int(g["ses"]) if g["ses"] else None))
    return pd.DataFrame(ops), pd.DataFrame(cuentas), vacias

if __name__ == "__main__":
    d, c, vacias = lee(sys.argv[1] if len(sys.argv) > 1 else "data/examen4_prueba.txt")
    print(f"{len(d)} operaciones · {vacias} sesiones sin operar · {len(c)} cuentas cerradas")
    if len(d):
        res = d[d.mot.isin(["TP","SL"])]
        print(f"  acierto {100*(res.mot=='TP').mean():.1f} %  ·  R neta/op {d.neta.mean():+.3f}")
        print(f"  con etiqueta de motivo: {(d.por!='').sum()} de {len(d)}")
        sl = d[d.mot=="SL"]
        print(f"  con diagnóstico de fallo: {(sl.fallo!='').sum()} de {len(sl)} stops")
        print(f"  con nota libre: {(d.nota!='').sum()}")
        if d.tanda.notna().any():
            print(f"  tandas: {sorted(d.tanda.dropna().unique().astype(int))}")
    if len(c):
        print(f"  cuentas: {(c.estado=='PASA').sum()} superadas · "
              f"{(c.estado=='REVIENTA').sum()} reventadas")
