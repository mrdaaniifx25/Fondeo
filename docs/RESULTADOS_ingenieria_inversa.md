# Resultados · sacarle la regla de entrada a sus 150 operaciones

Preregistrado en `docs/PREREGISTRO_ingenieria_inversa.md`, escrito antes de mirar
ninguna medida. Reconstrucción validada primero: **los 150 precios de entrada
caen dentro del rango real de su vela de M1** de ese día y ese minuto.

```
bt/contexto_150.py         valida la reconstruccion       150 de 150
bt/ingenieria_inversa.py   casos contra controles         data/ingenieria_inversa_salida.txt
bt/regla_rechazo.py        la regla derivada, confirmatorio
bt/su_stop.py              donde pone el stop
```

150 entradas suyas contra **3.400 velas de M5 de esos mismos 114 días** en las que
tenía las manos libres y no entró (se descartan 1.354 por estar ya dentro de una
operación: esas no eran elección suya).

## Dónde entra · exploratorio, Bonferroni p < 0,00625

| variable | suyas | controles | z | p |
|---|---|---|---|---|
| distancia al nivel de Asia | **4,3 p** | 7,5 p | −8,14 | 0,000000 * |
| cuerpo cerrado fuera del nivel | 6,7 % | 8,6 % | −0,81 | 0,42 |
| **solo mecha** (pincha y cierra dentro) | **23,3 %** | 8,1 % | +6,45 | 0,000000 * |
| la vela toca el nivel | 30,0 % | 16,7 % | +4,23 | 0,000024 * |
| toques previos del nivel | 1,0 | 2,0 | −7,23 | 0,000000 * |
| **minutos desde las 08:00** | **40** | 122,5 | −17,60 | 0,000000 * |
| rango de la vela | 4,2 p | 4,4 p | −1,82 | 0,069 |

Cinco de siete pasan Bonferroni, y algunas por mucho. **Dónde entra es
describible con una claridad que no habíamos tenido nunca en este proyecto.**

Pero la fila que más importa es la segunda: **no opera roturas**. El 6,7 % de sus
entradas tiene el cuerpo cerrado fuera del nivel, exactamente lo mismo que el
8,6 % del azar. Lo que hace es lo contrario:

```
pincha el ALTO de Asia y cierra por debajo:  16 entradas · vende 11, compra 5
pincha el BAJO de Asia y cierra por encima:  19 entradas · compra 19, vende 0
```

**30 de 35 van contra el nivel: rechazo, no rotura.** Y aciertan el 73-78 %.

Y H4 no manda. El 60 % de sus operaciones va **en contra** de la dirección de la
vela de H4 de 04:00-08:00, y acierta igual (67,4 % en contra, 64,3 % a favor).
Con M15, lo mismo. Es la tercera vez en el proyecto que se mide el filtro de H4 y
la tercera que no hace nada.

## La pregunta que decide: nada separa sus ganadoras de sus perdedoras

94 ganadoras contra 48 perdedoras, once variables:

| variable | gana | pierde | p |
|---|---|---|---|
| distancia al nivel | 4,0 p | 4,7 p | 0,62 |
| toques previos | 1,0 | 0,0 | 0,74 |
| minutos desde las 08:00 | 32,5 | 47,5 | 0,57 |
| stop en pips | 5,8 | 6,2 | 0,48 |
| dirección de H4 | −1 | −1 | 0,29 |
| dirección de M15 | −1 | −1 | 0,56 |
| nº de operación del bloque | 12 | 16 | 0,13 |
| la vela toca el nivel | 29,8 % | 29,2 % | 0,94 |
| solo mecha | 26,6 % | 16,7 % | 0,19 |
| cuerpo fuera | 3,2 % | 12,5 % | 0,031 |
| entra por encima del nivel | 42,6 % | 35,4 % | 0,41 |

**Ninguna pasa Bonferroni.** La mayor es «cuerpo fuera» con p = 0,031, y apunta en
contra de las roturas: el 12,5 % de sus perdedoras tiene el cuerpo fuera contra el
3,2 % de sus ganadoras. Son diez operaciones en total; no decide nada.

## El contraste confirmatorio: la regla derivada falla

Regla congelada: la vela de M5 pincha el nivel de Asia con la mecha y cierra de
vuelta dentro, primer o segundo toque, entrada al cierre, stop en el extremo de
la mecha, 1:2, cierre a mercado a las 11:30, coste 1,43.

| | disparos | acierto | stop | coste/riesgo | R neta | z |
|---|---|---|---|---|---|---|
| los 114 días del examen | 110 | 37,8 % | 3,0 p | 54,8 % | −0,375 | −2,71 |
| **fuera de muestra, 2020-2026** | **1.473** | **34,7 %** | 3,3 p | 51,2 % | **−0,459** | **−12,31** |

Hacía falta z > +1,96. Sale **−12,31**. Negativa los siete años, sin excepción.

Y no es el stop estrecho. Ensanchándolo, el coste baja y el acierto baja con él:

| stop mínimo | stop mediano | coste/riesgo | acierto | R neta | z |
|---|---|---|---|---|---|
| ninguno | 3,3 p | 51,2 % | 34,7 % | −0,459 | −12,31 |
| 4 p | 4,0 p | 31,4 % | 34,6 % | −0,255 | −7,03 |
| 6 p | 6,0 p | 22,7 % | 32,6 % | −0,194 | −5,55 |
| 10 p | 10,0 p | 14,1 % | 29,9 % | −0,099 | −3,14 |

Es la ley geométrica otra vez: ensanchar el stop no compra acierto.

**Predicción 6 confirmada.** Predije que quedaría por debajo del 45 % en datos
nuevos. Quedó en 34,7 %.

## Dónde vive entonces la diferencia

De sus 150, solo **36 (24 %)** coinciden con un disparo de la regla a menos de
quince minutos. Es más que el 13 % de la regla de rotura, pero tres de cada
cuatro de sus entradas siguen sin ser las que la regla elige.

En esos 36 disparos compartidos:

| | acierto | stop | R bruta | R neta |
|---|---|---|---|---|
| él | 65,7 % | 5,5 p | +0,987 | +0,711 |
| la regla | 55,9 % | 2,6 p | +0,664 | +0,074 |

Diferencia emparejada **+0,637 R por disparo, z = +1,94** (36 parejas, y son los
mismos días de los que salió la regla: descriptivo, no confirmatorio). Van en la
misma dirección solo 22 de 36.

Fíjese en la fila de la regla: sobre las velas que él también eligió acierta el
**55,9 %**, contra el 34,7 % sobre todas. **Su selección dentro de las velas
candidatas lleva información que las ocho variables no capturan.**

## Lo que sí es mecanizable: su stop

| referencia | mediana | error medio | \|error\| mediano | correlación |
|---|---|---|---|---|
| extremo de la vela del disparo | 5,3 p | +0,68 p | 1,55 p | 0,43 |
| **extremo de las 2 últimas de M5** | **6,2 p** | **−0,40 p** | **1,30 p** | **0,58** |
| extremo de las 3 últimas de M5 | 6,7 p | −1,10 p | 1,30 p | 0,57 |
| extremo de los últimos 15 min de M1 | 6,5 p | −0,89 p | 1,10 p | 0,59 |

Su stop (mediana 6,0 p) es **el extremo de las dos últimas velas de M5**, con
1,3 pips de error mediano. Eso se escribe en una línea y ya no depende de su ojo.
Lo pone por fuera del extremo de la vela del disparo el 67 % de las veces.

## Las seis predicciones

| | | |
|---|---|---|
| 1 · la distancia al nivel será lo que más separe | acierta la dirección, falla la magnitud (controles a 7,5 p, no a 15-20) | ± |
| 2 · entrará mucho antes | 40 min contra 122,5 | ✓ |
| 3 · cuerpo fuera más frecuente que en controles | **falla**: no es más frecuente, es igual | ✗ |
| 4 · H4 y M15 no separarán | no separan | ✓ |
| 5 · dominará el primer toque | mediana 1 contra 2 | ✓ |
| 6 · la regla mecánica no reproducirá su 66 % | 34,7 % fuera de muestra | ✓ |

## Qué significa

Tres codificaciones distintas de «lo que hace» han fallado ya: la rotura de nivel
(30,8 %), la cascada H4/M15/M5/M1 (90 celdas, todas negativas) y ahora el rechazo
(34,7 %). Lo que separa sus ganadoras de sus perdedoras **no está en las ocho
variables**, y las ocho variables son las que él mismo describe como su método.

Quedan tres explicaciones, y no son excluyentes:

1. Lee algo en M1 que ninguna de estas variables recoge —la forma, la velocidad,
   el orden en que llegan los ticks—. El 55,9 % de la regla sobre las velas que él
   eligió, contra el 34,7 % sobre todas, apunta aquí.
2. Parte del resultado está en la ejecución y no en la señal: su stop es el doble
   de ancho que el de la regla, y eso ya se sabe describir.
3. El simulador le favorece de una forma que no hemos aislado.

Las tres se distinguen con lo mismo, y solo con lo mismo: **operar hacia delante y
medir**. El componente «regla escrita» sigue en 6 de 20 y ya no por falta de
intentos.
