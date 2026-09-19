# Resultados · la regla, probada como se debe

Pre-registro `docs/PREREGISTRO_la_regla.md`. Dos pruebas, las dos con el
parámetro fijado a ciegas sobre el primer tramo y el segundo sin tocar.

## Prueba 1 · la regla simple, con filtro de stop mínimo

Elección mirando **solo 2020-2023**:

| X | n | ops/mes | acierto | riesgo | R neta |
|---|---|---|---|---|---|
| 10 p | 2.410 | 50,4 | 32,4 % | 14,8 p | −0,1215 |
| 15 p | 1.177 | 24,6 | 32,6 % | 20,7 p | −0,0876 |
| 20 p | 638 | 13,3 | 31,8 % | 26,6 p | −0,0971 |
| **25 p** | 379 | 8,2 | 32,2 % | 31,7 p | **−0,0769** |
| 30 p | 227 | 4,9 | 30,0 % | 37,9 p | −0,1374 |
| 40 p | 99 | 2,2 | 29,3 % | 49,5 p | −0,1490 |

**Las seis son negativas dentro de muestra.** No había ninguna configuración
positiva que elegir. Se elige la menos mala, X = 25.

**2024-2026 con X = 25:**

    n 143   4,8 al mes   acierto 23,8 %   riesgo 31,8 p   bruta -0,2867
    a 1,43 p de coste   NETA -0,3308   IC95 [-0,541, -0,121]
    a 0,90 p de coste   NETA -0,3145   IC95 [-0,524, -0,104]

Falla, y falla con el intervalo entero por debajo de cero. Bajar el coste de 1,43
a 0,90 mueve el resultado **0,016**: nada, porque con 32 pips de stop el peaje ya
solo era el 4,5 % del riesgo. **El problema aquí no era el coste. Era la bruta.**

## Prueba 2 · el modelo, con 2026 reservado de verdad

Entrenado con ≤2024, umbral elegido mirando **solo 2025**, y 2026 sin tocar.

Elección en 2025:

| X | n | acierto | bruta | neta |
|---|---|---|---|---|
| 0 p | 2.924 | 37,6 % | +0,127 | +0,031 |
| 10 p | 2.504 | 38,1 % | +0,143 | +0,063 |
| 20 p | 1.033 | 34,1 % | +0,022 | −0,030 |
| **30 p** | 358 | 39,4 % | +0,182 | **+0,144** |

**2026, reservado:**

    n 71   acierto 12,7 %   riesgo 36,6 p   bruta -0,6197
    NETA -0,6437 a 0,90 pips   IC95 [-0,877, -0,410]   z -5,40

De **+0,144 a −0,644**. Es la firma exacta del sobreajuste, la misma que hundió
al objetivo pendiente en agosto: lo elegido por ser lo mejor resulta ser lo que
más se había ajustado al ruido del tramo donde se eligió.

## Una equivocación mía, que hay que dejar escrita

Dije que el modelo *"había aprendido una sola cosa: quédate con los stops
anchos"*, porque el riesgo en pips pesaba trece veces más que la siguiente
variable en la importancia.

**Era una lectura errónea.** Esa importancia mide la predicción de la R **neta**,
y la neta depende del riesgo por pura aritmética: el modelo no estaba aprendiendo
a elegir, estaba reproduciendo la división. Por eso la versión simplificada a un
filtro de ancho —la prueba 1— pierde: no capturaba nada de lo que el modelo
hacía. Y la prueba 2 enseña que lo que el modelo hacía tampoco aguanta cuando el
tramo está reservado de verdad.

## Veredicto

Las dos pruebas bien diseñadas de este proyecto —esta y la de agosto— dan lo
mismo: **positivo donde se elige, negativo donde no se ha mirado.**

No hay, en todo lo medido, una configuración que se pueda entregar como rentable.
