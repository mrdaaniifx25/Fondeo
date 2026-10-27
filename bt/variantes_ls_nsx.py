"""¿Hay ALGUNA variante razonable de las 4 confirmaciones que tenga ventaja
BRUTA en el NASDAQ? Sin coste. Si sin coste no hay nada, el coste no es la
explicacion y la estrategia no funciona, punto."""
import sys; sys.path.insert(0, "bt")
import numpy as np, pandas as pd, estrategia_ls as E

m1 = pd.read_parquet("data/nsxusd_m1.parquet"); m1["ts"] = pd.to_datetime(m1["ts"])
m1 = m1.sort_values("ts").reset_index(drop=True)

def prueba(nom, **kw):
    base = dict(unidad=1.0, marco_disparo="3min", clave="nsx", coste_pips=0.0,
                sl_buffer_pips=1.0, rr=1.0, solo_kz=False, kz_londres=None, kz_ny=None)
    base.update(kw)
    m5, _ = E.construir_senales(m1, E.Config(**base))
    tr, _ = E.simular(m5, m1, E.Config(**base))
    if len(tr) < 50:
        print(f"   {nom:52s} n={len(tr):>5}  (pocas)"); return
    R = tr.R.to_numpy(); ee = R.std(ddof=1)/np.sqrt(len(R))
    marca = "  <<<" if R.mean() - 1.96*ee > 0 else ""
    print(f"   {nom:52s} n={len(tr):>5,}  acierto {100*(R>0).mean():5.2f}%  "
          f"R/op BRUTO {R.mean():+7.4f}  IC95 [{R.mean()-1.96*ee:+.4f},{R.mean()+1.96*ee:+.4f}]{marca}")

print("VENTAJA BRUTA (coste 0) DE CADA VARIANTE · NASDAQ 2020-2026\n")
print("  a · el modelo tal cual y sus piezas")
prueba("tal cual (M3, día entero, sesión+día, H1+H4)")
prueba("solo niveles del DÍA anterior", usar_sesion=False)
prueba("solo niveles de SESIÓN anterior", usar_dia=False)
prueba("sin exigir el barrido en H4 (solo H1)", exigir_h4=False)
prueba("envolvente con cuerpo >= 50% del rango", min_body_ratio=0.5)
prueba("envolvente con cuerpo >= 70% del rango", min_body_ratio=0.7)

print("\n  b · ventanas horarias")
prueba("apertura de Londres 08-11 hora Londres", solo_kz=True, kz_londres=(8,11), kz_ny=None)
prueba("apertura de NY 09-12 hora NY", solo_kz=True, kz_londres=None, kz_ny=(9,12))
prueba("apertura del contado 09-11 hora NY", solo_kz=True, kz_londres=None, kz_ny=(9,11))
prueba("las dos aperturas", solo_kz=True, kz_londres=(8,11), kz_ny=(9,12))

print("\n  c · marco del disparo")
for mk in ("1min", "5min", "15min"):
    prueba(f"disparo en {mk}", marco_disparo=mk)

print("\n  d · gestión (esto ya se desvía del vídeo, que dice 1:1 fijo)")
for rr in (0.5, 1.5, 2.0, 3.0):
    prueba(f"objetivo {rr}:1 en vez de 1:1", rr=rr)
for b in (5.0, 15.0):
    prueba(f"colchón del stop {b:.0f} puntos", sl_buffer_pips=b)

print("\n  e · ancla de la vela H4")
for a in (1, 2, 3):
    prueba(f"H4 anclada a las {a:02d}:00 UTC", h4_anchor_hour=a)
