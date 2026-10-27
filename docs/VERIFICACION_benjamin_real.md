# Verificación · una operación real suya contra mi mecanización

Vídeo que el usuario recibió por su comunidad de WhatsApp, 17/09/2026.
Fotogramas extraídos con ffmpeg; el que sirve está en
`docs/img/benjamin_trade_20260917.jpg`.

## Lo leído de su pantalla

EURUSD, gráfico de **M2**, entrada en torno a las **09:50** (ventana de
Londres). Herramienta de posición corta de TradingView:

| | precio |
|---|---|
| Stop (marca roja) | **1,15567** |
| Entrada (borde rojo/verde) | **1,15508** |
| Objetivo (marca verde) | **1,15389** |

```
riesgo    = 1,15567 - 1,15508 =  5,9 pips
recorrido = 1,15508 - 1,15389 = 11,8 pips
R:R = 2,0                    <- su 1:2, exacto
coste     = 1,43 / 5,9 = 24,2 % del riesgo
umbral    = (1 + 0,242) / 3 = 41,4 % de acierto para EMPATAR
```

## Contra lo medido en `RESULTADOS_benjamin_regla.md`

| | su operación real | mi mecanización (M2, sus horas) |
|---|---|---|
| riesgo | **5,9 p** | **6,4 p** |
| coste sobre el riesgo | **24,2 %** | **22,3 %** |
| umbral de empate | **41,4 %** | **40,8 %** |
| acierto medido | — | **33,4 %** sobre 29.959 operaciones |

**El stop real se reproduce con medio pip de error.**

## Por qué importa

Hasta ahora, todo lo medido de su estrategia salía de transcripciones, y siempre
quedaba la duda de si yo estaba midiendo mi interpretación en vez de su regla.

Esta operación cierra esa duda: **la geometría que él ejecuta delante de la
cámara es la que yo estaba midiendo.** Cuando el resultado dice «acierta 33,4 %
y necesita 40,8 %», está hablando de su operativa real, no de una versión mía.

## Límite

La operación es del **17/09/2026** y el parquet llega al **01/09/2026**, así que
**no se puede comprobar cómo acabó**. No hace falta: el resultado de una sola
operación no informa de nada (`docs/RESULTADOS_payouts.md`). Lo que informa es
la geometría, y la geometría está leída.

## Qué haría falta para ir más lejos

Más operaciones suyas con los tres precios visibles. Con 30-50 se podría
estimar su acierto real y compararlo con el 41,4 % que necesita.

---

# Ampliación 21/09/2026 · dos operaciones más, leídas de la etiqueta

Dos capturas nuevas. Esta vez no hizo falta el eje: **la herramienta de posición
de TradingView escribe las distancias en su propia etiqueta**, que es el dato
exacto y no una lectura de la escala.

| | 17/09 09:50 | 17/09 17:30 | 21/09 10:37 |
|---|---|---|---|
| riesgo | **5,9 p** | **5,5 p** | **5,8 p** |
| recorrido | 11,9 p | 16,6 p | 27,6 p |
| **R:R** | **2,02** | **3,02** | **4,76** |
| coste sobre el riesgo | 24,2 % | 26,0 % | 24,7 % |
| su precio justo | 33,1 % | 24,9 % | 17,4 % |
| **umbral de empate** | **41,2 %** | **31,4 %** | **21,6 %** |
| **exceso que necesita** | **+8,0** | **+6,5** | **+4,3** |

## Lo que revelan

**1 · Su stop es siempre el mismo: 5,5 a 5,9 pips.** Tres operaciones, tres
días, y el riesgo no se mueve. Es su firma, y confirma la mecanización
(`RESULTADOS_benjamin_regla.md` midió 6,4 p en M2).

**2 · Su R:R NO es 1:2 fijo.** Va de 2,02 a 4,76. Lo que enseña en los vídeos
(«ratio uno a dos y no seas avaricioso») no es lo que ejecuta.

**3 · Y eso importa, por una razón que no estaba escrita en el repo:**

```
neta = ventaja × (1 + R:R) − coste/riesgo
```

El R:R **multiplica la ventaja** que tengas; el stop sólo divide el coste. Por
eso el exceso de acierto que necesita cae de **+8,0** a **+4,3** puntos
simplemente alargando el objetivo, sin tocar el stop.

Esto matiza lo que se venía diciendo en el proyecto («ensancha el stop»). Las
dos palancas son reales y son independientes:

| palanca | qué hace |
|---|---|
| **stop más ancho** | baja `coste/riesgo`, el término que resta |
| **objetivo más lejos** | sube `(1 + R:R)`, el término que multiplica |

## Una observación sobre la primera captura

La del **17/09 17:30** está tomada con el **modo Reproducción** de TradingView
activo (la barra de replay y el panel «Reproducir trading» se ven en la
captura). Es decir: **es un backtest, no una operación en vivo.** Y las 17:30
quedan además fuera de sus propios horarios declarados (9-11 y 14-16:30).

No lo invalida como dato de geometría —un backtest suyo enseña igual de bien
cómo coloca las cosas— pero no cuenta como operación real.
