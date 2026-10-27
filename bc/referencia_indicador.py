"""Lo que el indicador de Pine TIENE que dibujar, sacado del motor ya auditado.

El Pine es una implementacion distinta del mismo metodo, y no la ha comprobado
nadie. Esto genera la respuesta correcta para un mes concreto de EURUSD: cada
rango, cuando nace, en que direccion, con que objetivo, y como muere. Se pone el
indicador en ese mes y se compara con lo que dibuja.
"""
import sys; sys.path.insert(0, "bc")
import pandas as pd, nucleo as N

DESDE, HASTA = "2026-06-01", "2026-07-01"
HUSO = "Madrid"

m1 = pd.read_parquet("data/eurusd_m1.parquet")
m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").reset_index(drop=True)

filas = []
for tf, h in [("1D", 24), ("12H", 12), ("4H", 4), ("1H", 1)]:
    v = N.activaciones(N.velas(m1, h, HUSO, 0), "B")
    for r in N.vida(v, tf):
        if not (pd.Timestamp(DESDE) <= r.nace < pd.Timestamp(HASTA)):
            continue
        filas.append(dict(marco=tf, nace=r.nace,
                          lado="alcista" if r.lado > 0 else "bajista",
                          base_bajo=round(r.base_lo, 5), base_alto=round(r.base_hi, 5),
                          objetivo=round(r.objetivo, 5), tomas=r.tomas,
                          reiniciado=r.reiniciado,
                          fin=r.fin_por or "seguia vivo", muere=r.muere))

t = pd.DataFrame(filas).sort_values(["marco", "nace"])
t.to_csv("data/referencia_indicador.csv", index=False)
print(f"EURUSD · {DESDE} a {HASTA} · huso {HUSO} · lectura B · ancla 0")
print(f"{len(t)} rangos escritos en data/referencia_indicador.csv\n")
print(t.groupby("marco").agg(rangos=("marco","size"),
                             completados=("fin", lambda s: (s=="completado").sum()),
                             descartados=("fin", lambda s: (s=="descartado").sum()),
                             relevados=("fin", lambda s: (s=="relevado").sum())))
print("\nlos de 1D y 12H, uno a uno — son los que se comprueban a ojo en el gráfico:")
print(t[t.marco.isin(["1D","12H"])][
      ["marco","nace","lado","base_bajo","base_alto","objetivo","tomas","fin"]
      ].to_string(index=False))
