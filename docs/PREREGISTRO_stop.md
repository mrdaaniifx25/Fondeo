# Pre-registro · ¿te tocan más el stop por ponerlo en el sitio obvio?

Escrito y subido ANTES de medir. 20/09/2026.

## De dónde viene

Ha aparecido dos veces sin buscarlo, en mediciones hechas para otra cosa:

| | exceso sobre el azar | dónde iba el stop |
|---|---|---|
| `RESULTADOS_amd_fvg.md`, rama sin FVG | **−11,6** | pegado al extremo de la finta |
| `RESULTADOS_ema_sr.md`, las 8 celdas | **−1,0 a −1,6** | en el máximo/mínimo de las últimas velas |

Las dos por debajo del azar. Y en `bt/deriva.py` quedó comprobado que barreras
a distancias fijas puestas en instantes al azar caen **en el azar exacto**
(−1,1 / +0,1 / −1,1). O sea: no es el resolutor. Es dónde va la barrera.

**Hipótesis**: una barrera colocada en un nivel que el precio acaba de visitar
se toca más que una barrera a la misma distancia colocada en un sitio
cualquiera.

Si es verdad, es una regla práctica y no una estrategia: vale para cualquier
cosa que se opere.

## Diseño

20.000 instantes al azar de EURUSD, lado al azar (mitad compras, mitad ventas).
Para cada uno:

- **D** = distancia del precio al extremo de las últimas N velas de M5 en
  contra de la operación (el máximo si es venta, el mínimo si es compra).
  N = 10, 20, 50.
- **Brazo NIVEL**: stop en ese extremo. Objetivo a 2×D al otro lado.
- **Brazo CONTROL**: mismo instante, mismo lado, stop a la **misma distancia D**
  y objetivo a 2×D — pero en un instante distinto elegido al azar, donde esa
  distancia no corresponde a ningún extremo.

Los dos brazos tienen la **misma geometría exacta**: azar = D/(D+2D) = 1/3.
Cualquier diferencia entre ellos no es geometría.

Resolución en M1, las dos barreras por toque, empate = pérdida, horizonte 20 h,
agotarlo = pérdida. Todo idéntico en los dos brazos.

**Intervalos por bootstrap de bloques de mes natural**, 2.000 remuestreos. Esto
corrige el defecto que quedó apuntado en `RESULTADOS_ema_sr.md`, donde las
operaciones se solapaban y los intervalos salían demasiado estrechos.

## Criterio

Para decir que el efecto existe:

1. **NIVEL por debajo de 1/3** con el IC95 sin tocar el cero, **y**
2. **CONTROL en 1/3**, y
3. la diferencia NIVEL − CONTROL con el IC95 sin tocar el cero, **y**
4. el mismo signo en los tres valores de N.

## Predicción

- CONTROL en 33,3 %, que es la calibración.
- NIVEL entre 1 y 4 puntos por debajo, y más marcado con N pequeña (el extremo
  de 10 velas está más cerca y es más visible que el de 50).
- Diferencia significativa. Aquí sí espero que salga: son dos apariciones
  independientes previas y un mecanismo que tiene sentido.

## Si sale

La regla es: **no pongas el stop justo en el máximo o el mínimo obvio.** Y la
medición dirá cuánto cuesta hacerlo, en puntos de acierto.
