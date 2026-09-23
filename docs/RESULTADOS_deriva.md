# Resultados · ¿predicen deriva estas señales?

Pre-registro: `docs/PREREGISTRO_deriva.md` (subido antes de medir).
Código: `bt/deriva.py`, `bt/deriva_sigma.py`, `bt/deriva_pool.py`.

## Veredicto según el criterio pre-registrado

**No se cumple.** La vía queda cerrada, como estaba escrito.

Pero no sale cero limpio como las 27 veces anteriores. Sale **algo real y
demasiado pequeño**, que es un resultado distinto y hay que decirlo con
precisión.

## Lo que aparece

De las 72 pruebas (4 señales × 6 horizontes × 3 instrumentos), una sobrevive:
**la finta a 1 hora en EURUSD.**

| | |
|---|---|
| sucesos | 1 701 |
| deriva media a 1 h | **+0,63 pips** [+0,17, +1,09] |
| en unidades del ruido de esa hora | **+0,0601 σ** [+0,0155, +0,1039] |

La «finta» es sólo la caja apretada más la vela que sale y cierra de vuelta
dentro. Sin pedir FVG. El lado, contra la finta.

Y aguanta todo lo que se le echa encima:

| prueba | resultado |
|---|---|
| N1 · lados barajados | +0,26 [−0,13, +0,66] · en cero |
| N2 · instantes al azar | +0,09 [−0,35, +0,55] · en cero |
| N3 · la señal al revés | −0,63 · el espejo exacto |
| **N4 · misma hora del día, fecha al azar** | **−0,008 [−0,063, +0,045] · en cero** |
| reparto de lados | 49,1 % / 50,9 % · sin sesgo de tendencia |
| primera mitad / segunda mitad | +0,43 / +0,84 · las dos positivas |
| por año | +0,71 · +0,02 · +1,42 · +0,62 · +0,52 · **5 de 5 positivos** |

N4 es el importante: mismas horas del día y mismos lados, pero en fechas al
azar. Descarta que sea «a las 9 de la mañana el EURUSD sube». No lo es.

## Por qué aun así no sirve

Porque es **2,3 veces más pequeño que el coste**.

| | EURUSD | oro | DAX |
|---|---|---|---|
| deriva / ruido | **+0,0601** | −0,0154 | +0,0014 |
| **coste / ruido** | **0,1359** | 0,0415 | 0,0304 |
| efecto más pequeño que la muestra distingue | 0,0438 | 0,0574 | 0,0737 |

Ésta es la tabla que resume el proyecto entero mejor que ninguna otra:

- **Donde hay señal, no se puede cobrar.** EURUSD es el par más barato del
  mundo en horquilla y aun así el coste se lleva el 13,6 % del ruido de una
  hora, más del doble de lo que la señal aporta.
- **Donde se podría cobrar, no se ve.** En el DAX el coste es sólo el 3 % del
  ruido. Un efecto del tamaño del de EURUSD *sí* pagaría ahí. Pero el DAX tiene
  965 sucesos y necesitaría ~11 veces más histórico para distinguirlo del cero.

## Y los tres juntos

Que es la cuenta honesta:

**n = 3 912 · +0,0216 σ [−0,0111, +0,0553]** — el cero dentro.

Un instrumento de tres, al filo, entre 72 pruebas. Y los controles que pasó
(años, mitades, N4) se le hicieron **después** de elegirlo, así que no cuentan
como confirmación independiente. Con 72 pruebas al 5 % se esperan 3 o 4
«significativas» sólo por azar.

**Esto es una hipótesis, no un hallazgo.**

## Los dos nulos que se rompieron, y por qué importa

En oro y DAX, N1 (lados barajados) salía «significativo» a 12 y 72 horas. No es
un fallo de la medición: el oro pasó de ~1 900 a ~3 600 en la muestra, y con un
reparto de lados desigual el nulo hereda la tendencia. Por eso los números de
esos dos instrumentos a horizontes largos no dicen nada, y por eso el reparto
de lados de la finta en EURUSD (49/51) es un dato y no un detalle.

## Lo único que puede resolverlo

No es medir otra variante. Es **datos que no se usaron para encontrarlo**:

| | tiene | necesita | falta |
|---|---|---|---|
| DAX (GRXEUR) | 965 sucesos, 2023-2026 | ~11 300 | histórico 2010-2022 |
| oro (XAUUSD) | 1 246 sucesos, 2023-2026 | ~8 800 | histórico 2010-2022 |

Con eso, la prueba se pre-registra antes de mirar — una sola: *la finta a 1
hora, contra la finta, en σ* — y se ejecuta una vez. Si sale, sale de verdad, y
en instrumentos donde el coste es tres veces menor. Si no sale, se cierra.

Es la primera vez en el proyecto que el cuello de botella no es una idea, son
datos.
