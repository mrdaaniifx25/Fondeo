# Resultados · el filtro de sesión sobre el CRT canónico

Pre-registro en `PREREGISTRO_londres_sesion.md`, escrito y subido en el commit
`1c298c0` **antes de abrir los ficheros**. Una sola pasada. XAUUSD y GRXEUR,
enero-julio de 2026, catorce ficheros mensuales que no habían entrado nunca en
este proyecto. Código en `bt/run_londres_ciego.py`.

Conversión horaria validada: el hueco semanal cae en las 23 h UTC en invierno y
las 22 h en verano — el desplazamiento de una hora que confirma que los ficheros
vienen en hora de Nueva York con horario de verano.

## El resultado, entero

**H1 · n = 1.614**

| ventana | n | % | acierto | R:R | riesgo | coste %R | **R bruta** | ee | R neta |
|---|---|---|---|---|---|---|---|---|---|
| LONDRES 09-11 | 141 | 8,7 % | 51,8 % | 1,08 | 204,4 | 3,3 % | **+0,0075** | 0,092 | −0,0364 |
| NY 14-16:30 | 154 | 9,5 % | 48,7 % | 1,03 | 110,2 | 3,1 % | −0,0010 | 0,097 | −0,0414 |
| CTRL_A 04-06 | 154 | 9,5 % | 43,5 % | 1,44 | 63,5 | 5,7 % | −0,0012 | 0,126 | −0,0977 |
| CTRL_B 19-21:30 | 146 | 9,0 % | 41,1 % | 1,40 | 379,4 | 5,4 % | −0,0573 | 0,109 | −0,1501 |
| **FUERA** | 1.019 | 63,1 % | 49,6 % | 1,28 | 390,0 | 4,2 % | **+0,0866** | 0,042 | +0,0219 |

**H4 · n = 411**

| ventana | n | acierto | riesgo | coste %R | R bruta | ee | R neta |
|---|---|---|---|---|---|---|---|
| LONDRES | 67 | 44,8 % | 1.065,0 | 1,9 % | −0,0765 | 0,149 | −0,0997 |
| NY | 67 | 41,8 % | 219,4 | 1,9 % | −0,0026 | 0,169 | −0,0320 |
| CTRL_A | 9 | 77,8 % | 269,0 | 1,4 % | +0,8340 | 0,400 | +0,8161 |
| CTRL_B | 3 | 33,3 % | 132,9 | 1,5 % | +0,5095 | 1,510 | +0,4883 |
| FUERA | 265 | 46,4 % | 204,4 | 2,2 % | +0,0450 | 0,094 | +0,0082 |

## La celda principal

```
LONDRES     n   141    bruta  +0,0075
FUERA       n 1.019    bruta  +0,0866
DIFERENCIA                    -0,0791    ee 0,1016
IC95                          [-0,2782, +0,1200]     z -0,78
```

**Criterio declarado: «LONDRES claramente negativa, o por debajo de FUERA →
falsación».** Está por debajo de FUERA. **La idea se cierra.**

## Las cinco predicciones

| | predicción | resultado |
|---|---|---|
| 1 | bruta LONDRES > FUERA | **✘** +0,0075 vs +0,0866 |
| 2 | ningún control supera a LONDRES | ✔ CTRL_A −0,0012 · CTRL_B −0,0573 |
| 3 | NY no supera a LONDRES | ✔ NY −0,0010 |
| 4 | riesgo mediano LONDRES ≈ FUERA (±20 %) | **✘** 204,4 vs 390,0 → −47,6 % |
| 5 | neta negativa en las cinco ventanas | **✘** FUERA sale +0,0219 |

Las dos que se cumplen no rescatan nada: dicen que los controles tampoco
funcionan, no que Londres funcione.

## Qué dice el fallo de la predicción 4, que es lo interesante

Era una comprobación de mecanismo, puesta ahí precisamente para esto: **si el
filtro cambia sobre todo el tamaño del stop, lo que se mide es geometría y no
sesión.**

Y eso es exactamente lo que pasa. El riesgo mediano dentro de la ventana de
Londres es **la mitad** del de fuera (204 contra 390 unidades). La ventana de
Nueva York, todavía menos: 110. La de las 04-06 de la madrugada, 63.

La ventana horaria no selecciona barridos mejores. Selecciona **barridos más
pequeños**, porque a esas horas los rangos de la vela previa son más estrechos.
Y como el objetivo es el extremo opuesto de esa misma vela, un rango estrecho
da un R:R más bajo (1,08 en Londres contra 1,28 fuera) y un acierto más alto
(51,8 % contra 49,6 %) sin ninguna ventaja: es el teorema de barrera otra vez.

Por eso el acierto de Londres parece bueno y la R no lo es.

## La fila de nueve operaciones, para que se vea el peligro

`CTRL_A` en H4: **+0,8340 R de media, 77,8 % de acierto, n = 9.**

Es la mejor cifra de toda la tabla y no significa absolutamente nada. Su error
típico es 0,400: el intervalo va de +0,05 a +1,62. Si esta prueba no hubiera
tenido criterio escrito de antemano, ahí había titular.

Queda aquí impresa a propósito.

## Lo que no se puede concluir

Esta prueba **no demuestra que Londres sea peor**. Con 141 operaciones en la
ventana, la diferencia mínima detectable declarada de antemano era **+0,24 R** y
el intervalo va de −0,28 a +0,12. Lo que demuestra es que **no hay ningún apoyo**
para que sea mejor, en los únicos datos ciegos disponibles, y por el criterio
escrito antes de mirarlos la hipótesis se cierra.

Es la diferencia entre «se ha refutado» y «no se ha sostenido». Esto es lo
segundo, y es suficiente para dejar de perseguirlo.

## Una cosa que sí llama la atención, y que NO se va a perseguir

La neta de FUERA en H1 sale **+0,0219**, y la predicción 5 decía que todas serían
negativas. El motivo es visible en la tabla: en este periodo el riesgo mediano es
de 390 unidades y el coste declarado se queda en el 4,2 % del riesgo, cuando en
`RESULTADOS_h12_ciego.md` (2023-2025, mismos instrumentos) era del 11,9 %.

Es el mismo mecanismo del coste de siempre, visto en un régimen de volatilidad
mucho más alta: siete meses de 2026 con el oro disparado. **Un régimen no es una
estrategia**, y este proyecto ya se estrelló una vez exactamente contra eso
(`RESULTADOS_sqx_fuera_muestra.md`: −55,4 % al salir del tramo alcista del oro).

Queda anotado como observación de una sola ventana temporal. No se explora.

## Los datos reservados, gastados

`reservado/` ya se ha abierto. Esos catorce ficheros no vuelven a ser ciegos y
no pueden servir para una segunda prueba. Si alguna vez hace falta otra, hay que
conseguir instrumentos o periodos que no hayan participado en nada.
