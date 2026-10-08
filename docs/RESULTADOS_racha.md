# ¿Dice algo el resultado de una operación sobre la siguiente?

Código `bt/racha.py`. Sale de un vídeo que mandó el usuario, cuya tesis central
es: *«si ayer me saltó el stop y hoy aparece el mismo setup, lo tomo igual»*.

Es una afirmación estadística, así que se comprueba.

## La respuesta: tiene razón

Sobre la regla del día previo, que da 0,84 operaciones al día y **no se solapa**:

| | tras GANAR | tras PERDER | diferencia |
|---|---|---|---|
| EURUSD · 1:1 | 49,7 % | 52,0 % | −2,3 [−7,8, +3,2] |
| EURUSD · 1:2 | 36,0 % | 36,1 % | −0,1 [−5,6, +5,4] |
| oro · 1:1 | 46,3 % | 46,8 % | −0,5 [−7,6, +6,7] |
| oro · 1:2 | 32,8 % | 30,9 % | +1,9 [−5,3, +9,1] |
| DAX · 1:1 | 47,6 % | 45,6 % | +1,9 [−5,0, +8,9] |
| DAX · 1:2 | 29,3 % | 32,5 % | −3,2 [−10,0, +3,7] |

**Seis de seis con el cero dentro.** El resultado anterior no lleva ninguna
información sobre el siguiente. Saltarse un setup porque el anterior falló no
te protege de nada: es tirar una operación a la basura por una corazonada.

## Un resultado que parecía enorme y era un artefacto

La misma prueba sobre la regla de la EMA daba **−10,9 y −14,0 puntos**: después
de perder se ganaba mucho más. Parecía un hallazgo grande.

No lo es. Las operaciones de esa regla:

- se separan **0,67 horas** de mediana, con un horizonte de **20 horas**;
- el **65,8 %** de las consecutivas van en **sentido opuesto**.

O sea que la operación N y la N+1 comparten casi toda su ventana de tiempo y
apuntan a lados contrarios. Si una gana, la otra casi tiene que perder. Es
aritmética del diseño, no comportamiento del mercado. **Descartado.**

Por eso la prueba sólo vale con operaciones separadas.

## La otra cara, que el vídeo no saca

El mismo razonamiento que hace correcto «no te saltes el siguiente» hace neutro
«toma otra para recuperar». Si las operaciones son independientes, **la segunda
no es ni mejor ni peor que la primera** — ni por seguir el plan, ni por
venganza. La diferencia entre las dos cosas no está en la estadística, está en
**el tamaño**: dos operaciones al riesgo de siempre es una cosa, y dos
operaciones dobladas para recuperar es otra. La intención no cambia el
resultado esperado; el tamaño sí.
