# Resultados · doble barrido anidado + envolvente de entrada

Pre-registro en `PREREGISTRO_doble_barrido.md`, commit `2db0010`, escrito antes
de medir nada. Código en `bt/doble_barrido.py`. Cinco instrumentos, 2020 a julio
de 2026.

## La tabla entera

| par | entra | n | acierto | riesgo | coste %R | **R bruta** | **R neta** | IC95 | z |
|---|---|---|---|---|---|---|---|---|---|
| **12h+4h** | **M15** | 4.005 | 37,4 % | 6,8 | 19,6 % | **+0,1228** | **−0,1518** | [−0,201, −0,103] | −6,10 |
| 12h+4h | M5 | 11.679 | 34,7 % | 3,8 | 34,9 % | +0,0414 | −0,4471 | [−0,478, −0,416] | −28,09 |
| 8h+4h | M15 | 5.622 | 35,6 % | 6,7 | 19,3 % | +0,0694 | −0,1975 | [−0,239, −0,156] | −9,27 |
| 8h+4h | M5 | 16.283 | 35,5 % | 3,7 | 34,9 % | +0,0655 | −0,4219 | [−0,448, −0,395] | −31,08 |
| 4h+2h | M15 | 6.425 | 34,4 % | 6,5 | 20,3 % | +0,0305 | −0,2596 | [−0,297, −0,222] | −13,50 |
| 4h+2h | M5 | 17.932 | 36,1 % | 3,5 | 36,4 % | +0,0829 | −0,4226 | [−0,448, −0,397] | −32,96 |

**Celda principal declarada: 12h+4h · M15.** Criterio: la neta excluye el cero
**por arriba**. Lo excluye **por abajo**: [−0,201, −0,103], z −6,10. No es un
resultado ambiguo — es negativo con holgura. **La idea se cierra.**

Potencia: el efecto mínimo detectable con n = 4.005 era +0,041 R, por debajo del
+0,05 esperado. La prueba sí tenía potencia para confirmar. No confirmó.

## Las tres predicciones, las tres acertadas

| | predicción | resultado |
|---|---|---|
| 1 | bruta entre +0,05 y +0,15 | ✔ media +0,0687 |
| 2 | coste > 20 % del riesgo | ✔ 27,6 % de mediana |
| 3 | neta negativa en las 6 celdas | ✔ 6 de 6 |

## Lo que sí ha encontrado, y es lo interesante

**La celda principal da +0,1228 R de ventaja bruta.** Es la mayor medida en todo
el proyecto: por encima del +0,082 del CRT desnudo y del +0,089 replicado a
ciegas en oro y DAX.

El doble barrido anidado **sí selecciona**. Exigir que dos temporalidades
encajadas estén barridas del mismo lado a la vez concentra la ventaja bruta
aproximadamente un 50 % por encima del barrido simple. Y se ve el gradiente:
12h+4h da +0,123, 8h+4h da +0,069, 4h+2h da +0,031 — **cuanto más separadas las
temporalidades, más ventaja**, que es exactamente lo que la idea predecía.

Eso es un hallazgo real y no estaba medido.

## Por qué muere igualmente

La envolvente de M15 deja un stop de **6,8 pips**. Con 1,43 de coste eso es el
19,6 % del riesgo, y 0,196 es mayor que 0,123.

```
para empatar con bruta +0,1228  ->  el coste no puede pasar del 12,3 % del riesgo
                                ->  hace falta un stop de 11,6 pips
para sacar +0,05 neto           ->  coste máximo del 7,3 %
                                ->  hace falta un stop de 19,6 pips
```

El stop lo pone el disparador, no el patrón. Y una envolvente de M15 no llega a
11,6 pips ni de lejos: su mediana son 6,8.

## La variante que esto sugiere, y que NO se ha probado

Poner el stop en el **extremo del barrido de 4h** en vez de en el de la
envolvente. El patrón seguiría siendo el mismo —la ventaja bruta no la pone el
stop— pero el riesgo sería mucho más ancho y el peaje caería a la mitad o menos.

Es una hipótesis nueva y honesta: sale de la aritmética del coste, no de haber
visto resultados. **Exige su propio pre-registro** y cuenta como una comparación
más. Queda anotada, sin correr.
