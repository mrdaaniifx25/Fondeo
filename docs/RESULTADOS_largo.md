# Resultados · horizonte largo, muchos mercados

Pre-registro: `docs/PREREGISTRO_largo.md` (subido antes de medir, con la
potencia declarada por delante). Código: `bt/largo.py`.

## Veredicto

**«No se puede saber con estos datos.»** Que es exactamente lo que predijo el
pre-registro, y que **no es lo mismo** que los 29 resultados anteriores.

En los 29 anteriores medimos y salió cero: el efecto estaba en su precio justo.
Aquí no hemos medido nada — la muestra no da para ver un efecto del tamaño que
haría falta ver.

## Lo medido

Efecto en unidades de ruido, juntando los tres instrumentos:

| barras | K | efecto | IC95 | coste/ruido | percentil frente a 1.000 barajas |
|---|---|---|---|---|---|
| semanas | 1 | +0,0254 | [−0,054, +0,105] | 0,0016-0,0107 | 65 |
| **semanas** | **3** | **+0,0612** | [−0,018, +0,141] | 0,0016-0,0107 | **89** |
| semanas | 6 | +0,0296 | [−0,051, +0,110] | | — |
| semanas | 12 | +0,0258 | [−0,056, +0,107] | | — |
| meses | 1 | +0,1338 | [−0,035, +0,302] | 0,0008-0,0048 | 85 |
| meses | 3 | +0,1406 | [−0,031, +0,313] | 0,0008-0,0048 | 75 |
| meses | 6 | +0,0961 | [−0,083, +0,275] | | — |
| meses | 12 | +0,1153 | [−0,081, +0,312] | | — |

**Las ocho positivas. Las ocho muy por encima del coste** — entre 6 y 170 veces
el coste de ese horizonte. Y las ocho con el cero dentro del intervalo.

Ninguna llega al percentil 95. La mejor, semanas K=3, se queda en 89.

## Las dos comprobaciones que cambian cómo se lee

**1. El nulo no está en cero.** Con 1.000 barajas, la media de los nulos sale
en +0,010 (semanas) y **+0,052 a +0,084 (meses)**. Barajar los signos conserva
el desequilibrio entre largos y cortos, y si el instrumento subió, el nulo
hereda la subida. Por eso el percentil es la lectura correcta y la media a
secas no lo es.

**2. En barras mensuales, la señal está sesgada a largo:**

| | señal larga | el instrumento subió |
|---|---|---|
| EURUSD mensual | 41,5 % | −4,3 % |
| **oro mensual** | **79,5 %** | **+109,7 %** |
| **DAX mensual** | **71,8 %** | **+514,4 %** |

Los números mensuales de oro y DAX **no miden momento**: miden estar largo en
un mercado alcista, en una muestra que sólo cubre 2023-2026. Hay que
descartarlos. Las semanas están mucho menos sesgadas (48,5 % / 60,7 % / 59,6 %)
y por eso la fila que vale es la de semanas K=3.

## Lo que hace falta para saberlo

| | hay | hace falta |
|---|---|---|
| semanas, los tres juntos | **613** | **~1.275** |

Poco más del doble. Y se consigue exactamente con lo que ya está pedido: el
histórico 2010-2022 de DAX y oro, que multiplicaría por tres las barras de esos
dos.

## Por qué esto no es un resultado más

Los 29 anteriores murieron por el coste: la señal era más chica que la
horquilla. **Aquí la señal medida es entre 6 y 170 veces el coste.** Si el
efecto existe siquiera parecido a como se mide, el coste no lo mata.

Lo que falta no es una idea mejor. Son barras.

Y hay que decir la otra mitad: el percentil 89 es exactamente lo que produce el
ruido con esta muestra bastante a menudo. **Esto no es un hallazgo.** Es la
primera vez en el proyecto que el resultado es «todavía no se ve» en vez de
«no está».
