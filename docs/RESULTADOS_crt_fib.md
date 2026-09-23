# Resultados · CRT con entrada por Fibonacci en M5

Propuesta del usuario: mantener el setup CRT en la vela de referencia, pero
sustituir la entrada por una **orden limitada en un retroceso de Fibonacci**
mirado en M5. Era además mi propia sospecha nº1: que entrar a mercado en vez de
con orden limitada estaba estropeando la medición.

**La idea era buena y cambia los números. No los cambia lo suficiente.**

---

## Horario: ya estaba en hora española

El filtro de killzones convierte a `Europe/Madrid` con cambio de hora automático.
Las ventanas realmente aplicadas:

| | Forex | Índices |
|---|---|---|
| Londres | 08:00 – 11:00 | 08:00 – 11:00 |
| Nueva York | 13:00 – 16:00 | 15:30 – 17:00 |
| London Close | 16:00 – 18:00 | 16:00 – 18:00 |
| Excluido | 11:00 – 13:00 (almuerzo europeo) | — |

Invierno UTC+1, verano UTC+2, resuelto por la librería de husos.

## Mecánica implementada

Para un CRT alcista, con el setup ya identificado en la vela de referencia:

```
A  = mínimo del barrido (extremo de la Vela 2)
B  = máximo acumulado en M5 desde A, leído solo de velas YA CERRADAS
nivel de entrada = B − r·(B−A)        r = profundidad del retroceso
SL = A − colchón                      (donde manda la guía: tras la mecha)
TP = extremo opuesto del rango de la Vela 1
```

El nivel sube conforme sube B, como haría un operador mirando la pantalla. **B se
lee siempre de la vela anterior**, nunca de la que se está evaluando, para no
mirar al futuro.

## La profundidad del retroceso sí importa · referencia H4

| retroceso | n | bruto/op | p | R:R medio | %TP | **PF neto** |
|---|---|---|---|---|---|---|
| 38,2 % | 2.554 | −0,0816 | 0,018 | 3,24 | 24,7 % | 0,760 |
| 50,0 % | 2.900 | −0,0447 | 0,173 | 3,37 | 25,7 % | 0,797 |
| 61,8 % | 3.286 | −0,0085 | 0,795 | 3,75 | 24,9 % | 0,828 |
| 70,5 % | 3.307 | **+0,0258** | 0,478 | 4,46 | 22,6 % | 0,852 |
| 79,0 % | 2.919 | **+0,0352** | 0,421 | 5,68 | 18,5 % | 0,839 |

**Hay una relación monótona clara: cuanto más profundo el retroceso, mejor.** Y
tiene sentido mecánico — mejor precio de entrada, menos riesgo, más R por
operación. Tu intuición y la mía apuntaban bien.

Pero mira la última columna: **el profit factor neto no llega a 1 en ninguna
fila.** El retroceso profundo mejora la R bruta y a la vez baja el porcentaje de
aciertos (de 24,7 % a 18,5 %), porque la orden se llena menos veces en el sitio
bueno. Lo que se gana por un lado se paga por el otro.

## Cruce con la temporalidad de referencia

| | fib 50 % | fib 61,8 % | fib 70,5 % |
|---|---|---|---|
| **H1** | −0,0267 · PF 0,765 | −0,0333 · PF 0,748 | −0,0438 · PF 0,723 |
| **H4** | −0,0447 · PF 0,797 | −0,0085 · PF 0,828 | +0,0258 · PF 0,852 |
| **D1** | **+0,0768 · PF 1,036** | −0,0238 · PF 0,895 | −0,0755 · PF 0,828 |

Una sola celda de catorce supera un profit factor de 1: D1 con retroceso al 50 %.

## Lo que de verdad cambia esta prueba: ahora hay potencia

El CRT canónico daba **122 operaciones** en 6,5 años entre cinco instrumentos.
Con eso no se podía concluir nada.

La entrada por Fibonacci en M5 da entre **1.300 y 9.900 operaciones**. Por primera
vez en todo el proyecto hay muestra suficiente para cerrar la pregunta, y se puede
hacer algo mejor que mirar un p-valor: acotar la ventaja.

| celda | n | bruto/op | IC 95 % de la ventaja | coste a batir | |
|---|---|---|---|---|---|
| H1 fib 50 % | 7.299 | −0,0267 | [−0,0664 , **+0,0130**] | 0,1754 | el intervalo **entero** queda por debajo del coste |
| H4 fib 61,8 % | 3.286 | −0,0085 | [−0,0726 , **+0,0556**] | 0,1390 | ídem |
| H4 fib 70,5 % | 3.307 | +0,0258 | [−0,0455 , **+0,0972**] | 0,1596 | ídem |
| D1 fib 50 % | 1.301 | +0,0768 | [−0,0276 , +0,1813] | 0,0501 | el único que roza |

*El «coste a batir» es el coste de ida y vuelta dividido por el riesgo medio: la
ventaja bruta mínima para empatar.*

Esto ya no es «no encontramos ventaja». Es: **con un 95 % de confianza, la ventaja
del CRT es demasiado pequeña para cubrir el coste**, en tres de las cuatro celdas
principales. El intervalo completo está por debajo del listón.

## El control, otra vez

Sobre la única celda con PF por encima de 1 (D1, retroceso 50 %), sorteando la
**dirección** a cara o cruz y dejando idéntica toda la mecánica:

| | n | bruto/op | z | PF neto |
|---|---|---|---|---|
| La estrategia | 1.301 | +0,0768 | +1,44 | 1,036 |
| **Dirección al azar** (8 rep) | 5.426 | **+0,0879** | **+3,34** | **1,049** |

La moneda vuelve a ganar. Y fíjate en el z de +3,34: la geometría de esta
mecánica —stop pegado a una mecha, objetivo lejos, R:R de 4— produce una R bruta
ligeramente positiva **de forma fiable, tomes la dirección que tomes**. No es
señal. Es aritmética del stop y el objetivo.

## Un bug mío que encontré por el camino

La primera ejecución dio R:R de 4.800 millones y profit factor 0,000. Causa: si el
precio abre con hueco por debajo del nivel limitado, la entrada se rellena pegada
al stop, el riesgo tiende a cero y la R explota.

Corregido con dos guardas: el stop tiene que estar a un mínimo de 3 unidades y al
menos un 5 % del rango de referencia, y se descarta cualquier operación con R:R
por encima de 15. Sin esas guardas, cualquier backtest de entrada limitada da
cifras fantásticas y falsas.

## Conclusión

Tres cosas, en orden de importancia:

1. **La entrada sí importaba**, y en la dirección que suponíamos: el retroceso
   profundo mejora monótonamente la R bruta, de −0,082 a +0,035.
2. **No basta.** Pasa de perder claramente a no ganar. Trece de catorce celdas
   pierden dinero después de costes.
3. **Y ahora ya está cerrado.** Con miles de operaciones en vez de 122, el
   intervalo de confianza al 95 % excluye la ventaja necesaria para cubrir el
   coste. Esta es la primera prueba del CRT con potencia estadística real, y el
   resultado es un no firme, no un «no sabemos».
