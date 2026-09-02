# `pine/londres_operativa.pine` · qué hace y qué no

## Qué no hace

**No da señales de entrada.** Y no es por pereza: se midió. El modelo que
reproduce dónde entra —AUC 0,800, ocho veces la base— puesto a operar solo saca
**37,4 % en 1.449 operaciones sobre 1.032 días nuevos**, y el equilibrio con el
coste real está en el 41,3 %. La selección de la vela es suya y no se automatiza.

Lo que sí está medido, y es lo que el indicador automatiza:

| lo que dibuja | de dónde sale |
|---|---|
| alto y bajo de Asia (00:00-08:00) | los niveles que la página le pintaba |
| **alto y bajo que lleva Londres** | el 36,7 % de sus entradas están pegadas ahí, y aciertan el 73,5 % |
| el stop | el extremo de los últimos 10 minutos: mediana 5,9 p contra sus 6,0 p, error mediano 1,3 p |
| el objetivo | 1:2 sobre ese stop |
| los lotes | riesgo elegido ÷ (pips de stop × valor del pip) |
| aviso de rotura | cuerpo cerrado fuera del nivel de Asia: su peor caja, 33,3 % |
| ventana buena | los primeros 90 minutos; su mediana de entrada es 08:40 |

## Cómo se pone

1. TradingView → Editor Pine → pegar el fichero entero → **Añadir al gráfico**.
2. Gráfico de **M1 o M5**. Por encima de M5 el stop pierde sentido y la tabla lo
   avisa.
3. En los ajustes: capital, y **riesgo 0,5 %** para las primeras 20 operaciones
   en directo.

## Cómo se lee la tabla

```
LONDRES        09:14      136 min      <- reloj y lo que queda de ventana
ventana        BUENA      +74 min      <- BUENA los primeros 90 minutos
alto de Asia   1.16542    +8.3 p
bajo de Asia   1.16301   -15.8 p
alto Londres   1.16498    +3.9 p       <- pegado a esto es su mejor caja
bajo Londres   1.16352   -10.6 p
stop compra    1.16401     5.8 p
objetivo       1.16575     2.0 R
stop venta     1.16512     6.3 p
objetivo       1.16333     2.0 R
0.5 % de 10000  0.17 lotes  0.16 lotes
pegado al alto de Londres · tu mejor caja
dos pérdidas y paras · 1:2 siempre
```

Los triángulos marcan el rechazo del nivel de Asia y la equis la rotura. **Son
contexto, no órdenes**: el rechazo mecánico sale 34,7 % y la rotura 33,3 %.

## Las reglas que no están en el código

```
ventana   08:00-11:30, y vive en la primera hora y media
NUNCA     la rotura del nivel de Asia. Es su peor caja: 33 %
parada    dos pérdidas, o las 11:30
riesgo    0,5 % las primeras 20 operaciones · 1 % si el acierto aguanta
          por encima del 55 % · nunca 2 %
```

## Por qué 0,5 % al principio

Las primeras veinte operaciones en directo son la medición que falta: separar
«lee algo que no sé medir» de «el simulador le favorece». A 0,5 % cada R son
50 $, el límite total son 20 R y su peor día en 150 operaciones fueron dos
pérdidas. Veinte operaciones a ese riesgo no pueden reventar la cuenta ni en el
peor escenario razonable, y el examen de FundingPips **no tiene límite de
tiempo**, así que medir no cuesta nada.

| si en directo acierta | operaciones para saberlo | sesiones |
|---|---|---|
| 66 % (lo medido) | 24 | ~18 |
| 60 % | 43 | ~33 |
| 55 % | 80 | ~62 |

Por encima del 55 % a las veinte, sube a 1 % y va a por el 8 %. Por debajo del
45 %, para: era el simulador.
