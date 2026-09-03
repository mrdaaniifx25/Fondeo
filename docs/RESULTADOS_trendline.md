# Resultados · rotura de línea de tendencia en M5

Preregistrado en `docs/PREREGISTRO_trendline.md`. Una sola pasada.

```
bt/trendline.py         las doce celdas en EURUSD
bt/trendline_todos.py   el signo en los siete instrumentos
```

La línea se define en código, sin dibujo y sin mirar al futuro: dos pivotes
fractales de cinco velas unidos y prolongados, válida mientras ningún cierre haya
quedado al otro lado, y la rotura es el primer cierre que la cruza. **10.504
roturas en la ventana de Londres y 70.461 en el día entero**, solo en EURUSD.

## Las doce celdas · EURUSD

| ventana | stop | k | n | acierto | geom | dif | stop | coste/riesgo | R neta | z | c\* |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Londres | A | 1 | 7.548 | 49,8 % | 50,0 % | −0,2 pt | 4,2 p | 34,0 % | −0,390 | −34,03 | −0,02 |
| Londres | A | 2 | 6.496 | 31,7 % | 33,3 % | −1,6 pt | 4,2 p | 34,0 % | −0,373 | −22,42 | 0,03 |
| Londres | A | 3 | 5.854 | 22,1 % | 25,0 % | −2,9 pt | 4,2 p | 34,0 % | −0,364 | −17,65 | 0,07 |
| Londres | B | 1 | 3.221 | 50,2 % | 50,0 % | +0,2 pt | 14,3 p | 10,0 % | −0,140 | −10,01 | −0,04 |
| Londres | B | 2 | 2.714 | 26,9 % | 33,3 % | −6,4 pt | 15,8 p | 9,1 % | −0,109 | −5,78 | 0,21 |
| Londres | B | 3 | 2.564 | 13,6 % | 25,0 % | −11,4 pt | 16,2 p | 8,8 % | −0,121 | −5,78 | 0,06 |
| día | A | 1 | 40.478 | 48,6 % | 50,0 % | −1,4 pt | 3,7 p | 38,6 % | −0,454 | −89,67 | −0,09 |
| día | A | 2 | 31.296 | 32,0 % | 33,3 % | −1,4 pt | 3,8 p | 37,6 % | −0,450 | −56,74 | −0,10 |
| día | A | 3 | 26.098 | 23,6 % | 25,0 % | −1,4 pt | 3,8 p | 37,6 % | −0,445 | −42,46 | −0,09 |
| día | B | 1 | 19.903 | 48,1 % | 50,0 % | −1,9 pt | 7,9 p | 18,1 % | −0,267 | −38,29 | −0,22 |
| día | B | 2 | 13.513 | 30,7 % | 33,3 % | −2,6 pt | 7,8 p | 18,3 % | −0,268 | −23,38 | −0,21 |
| día | B | 3 | 11.225 | 22,3 % | 25,0 % | −2,7 pt | 7,8 p | 18,3 % | −0,252 | −16,73 | −0,08 |

Hacía falta z > +2,87. La mejor de las doce está en **−5,78** y la peor en
**−89,67**.

Mírese la última columna, `c*`, el coste al que cada celda llegaría a cero:
**está en cero o por debajo en las doce.** No es que el coste se coma la ventaja:
**es que no hay ventaja que comerse.** La R bruta de una rotura de línea de
tendencia en M5 es cero.

## Los siete instrumentos

| instrumento | stop A, k=2 | | stop B, k=1 | |
|---|---|---|---|---|
| | acierto | R neta | acierto | R neta |
| EURUSD | 31,7 % | −0,373 | 50,2 % | −0,140 |
| GBPUSD | 32,5 % | −0,361 | 50,6 % | −0,128 |
| USDJPY | 32,2 % | −0,350 | 49,1 % | −0,141 |
| XAUUSD | 32,2 % | −0,448 | 49,7 % | −0,145 |
| NSXUSD | 33,1 % | −0,250 | 50,8 % | −0,089 |
| SPXUSD | 30,4 % | −0,296 | 49,2 % | −0,134 |
| GRXEUR | 33,5 % | −0,207 | 48,2 % | −0,128 |

```
stop A k=1   negativa en 7 de 7   media -0,342
stop A k=2   negativa en 7 de 7   media -0,328
stop A k=3   negativa en 7 de 7   media -0,326
stop B k=1   negativa en 7 de 7   media -0,129
stop B k=2   negativa en 7 de 7   media -0,114
stop B k=3   negativa en 7 de 7   media -0,114
```

**Cuarenta y dos de cuarenta y dos.** No hay un solo instrumento, un solo stop,
un solo objetivo donde salga positiva.

## La rotura es algo peor que una moneda

Con 40.478 roturas en el día, el acierto bruto queda en **48,6 %** contra el
50,0 % geométrico. El error típico es de 0,25 puntos, así que ese −1,4 es
**z ≈ −5,6**: la rotura de una línea de tendencia en M5 no es neutral, es
**ligeramente adversa**. Encaja con lo que se sabe de las roturas en
temporalidades pequeñas: son sitios donde se va a buscar liquidez.

¿Y desvanecerla, entonces?

| ventana | stop | acierto invertido | R neta invertida | z |
|---|---|---|---|---|
| Londres | A | 50,2 % | −0,379 | −33,36 |
| Londres | B | 49,8 % | −0,132 | −9,44 |
| día | A | 51,4 % | −0,399 | −78,82 |
| día | B | 51,9 % | −0,197 | −28,25 |

Tampoco. **El coste se resta en las dos direcciones**: con un stop de 4 pips son
el 34-39 % del riesgo, y el 1,4-1,9 puntos que da la inversión no llegan ni de
lejos. Es la misma aritmética que mató la regla del barrido diario.

## Las cinco predicciones

| | | |
|---|---|---|
| 1 · stop A entre 4 y 9 pips, B entre 10 y 20 | A sale en 3,7-4,2 en EURUSD, por debajo del rango | ± |
| 2 · ninguna de las doce pasará el umbral | acierta | ✓ |
| 3 · acierto a menos de 3 pt de su geometría | falla en Londres B con k=2 (−6,4) y k=3 (−11,4) | ✗ |
| 4 · el stop B saldrá menos malo que el A | acierta: −0,140 contra −0,390 | ✓ |
| 5 · Londres no será mejor que el día entero | falla, por poco: −0,390 contra −0,454 | ✗ |

## Lo que deja escrito

Es la ilustración más limpia del muro del coste que tiene el proyecto. Ciento
cincuenta mil operaciones, siete instrumentos, dos sitios para el stop, tres
objetivos y dos ventanas, y **la ventaja bruta es cero**. Con un stop de cuatro
pips el coste se lleva el 34-39 % del riesgo, así que da igual: aunque la rotura
tuviera una ventaja pequeña, no se podría cobrar.

Con esto, las familias mecánicas medidas y descartadas en el proyecto son seis:

```
rotura del nivel de Asia          -2,5 pt sobre la geometria
cascada H4/M15/M5/M1, 90 celdas   -1 a +1 pt
rechazo del nivel de Asia         +1,4 pt
modelo de 16 variables            +4,1 pt   (la mejor, y no llega)
barrido diario                    -2,5 pt
LINEA DE TENDENCIA EN M5           0,0 pt
```
