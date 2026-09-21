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
