# Los dos bloques juntos · 53 operaciones, 40 sesiones

Post hoc: el análisis conjunto no era la regla de decisión de ninguno de los dos
pre-registros. Se reporta como lo que es.

## 1 · La ventaja aguanta un coste mucho peor del real

| coste redondo | R neta / op | z | por sesión | z sesión |
|---|---|---|---|---|
| 1,28 p | +0,451 | +2,28 | +0,597 | +2,03 |
| **1,43 p** | **+0,426** | **+2,16** | +0,565 | +1,93 |
| 1,58 p | +0,401 | +2,03 | +0,532 | +1,83 |
| 2,00 p | +0,332 | +1,69 | +0,440 | +1,54 |
| 3,00 p | +0,167 | +0,85 | +0,221 | +0,81 |

**Su neta llegaría a cero con 4,01 pips de coste redondo**, casi el triple del
real. Es lo primero en todo el proyecto que tiene margen sobre el coste en vez de
morir por él: las familias mecánicas rendían entre 0,06 y 1,22 pips de ventaja
contra 1,43 de coste.

## 2 · Se le cae el rendimiento a mitad de bloque, y pasa en los dos

| | n | TP | SL | acierto | R neta media |
|---|---|---|---|---|---|
| **primera mitad** de cada bloque | 27 | 19 | 8 | **70,4 %** | **+0,866** |
| **segunda mitad** | 26 | 8 | 14 | **36,4 %** | −0,031 |

Fisher a dos colas **p = 0,023**. Y no sale de un bloque: sale de los dos por
separado.

```
bloque 1   1ª mitad 72,7 %   ->   2ª mitad 45,5 %
bloque 2   1ª mitad 73,3 %   ->   2ª mitad 25,0 %
```

De las nueve variables medidas sobre las 53, **la única que separa ganadoras de
perdedoras es el número de operación dentro del bloque**: t = −2,44, p = 0,015.
Ni la hora, ni el stop, ni la dirección, ni la duración.

| | gana | pierde | t | p |
|---|---|---|---|---|
| nº dentro del bloque | 11 | 15,5 | **−2,44** | **0,015** |
| nº de sesión | 7 | 10 | −2,09 | 0,037 |
| minutos hasta salir | 45 | 29,5 | +1,73 | 0,084 |
| stop en pips | 6,8 | 7,5 | −1,19 | 0,232 |
| hora de entrada | 08:29 | 08:46 | +0,13 | 0,896 |

## Lo que esto cambia

La pregunta de las últimas semanas era *qué ve en el gráfico*. Sobre 53
operaciones, **ninguna variable del gráfico separa sus aciertos de sus fallos**.
La que lo hace es **cuántas decisiones lleva encadenadas**.

Si eso se confirma, la regla que le falta no es sobre el precio: es sobre
**cuánto puede operar seguido**. Nunca lo habíamos considerado, y es la primera
hipótesis del proyecto con un tamaño de efecto grande y una consecuencia práctica
inmediata.

Se pone a prueba en `PREREGISTRO_examen3.md`, declarado antes: 24 sesiones en
tres tandas de ocho, con la hora de cada decisión registrada por la página.

## Reproducir

`python3 bt/examen_juntos.py` · datos en `data/examen_juntos.csv`
