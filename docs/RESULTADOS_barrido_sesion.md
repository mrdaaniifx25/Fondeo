# Resultados · el barrido de sesión, su regla

Pre-registro `60054e3`, escrito antes de medir. Código en `bt/barrido_sesion.py`.
EURUSD, M5, 2020-2026, Londres y Nueva York.

## Primero: la traducción es fiel

    barridos brutos                     16.098
    con "un nivel, una operación"        3.055
    operaciones al día                    1,92

Él opera **una o dos al día**. La regla escrita da **1,92**. El pre-registro decía
que menos de 100 operaciones en seis años significaría que la traducción está mal;
hay 3.055 al ritmo correcto. Lo que se ha medido es lo que él describe.

## La celda principal

    C2, Londres + NY   n 3.055   acierto 34,3 %   (necesita 41,7 %)
                       riesgo 5,7 p   coste 25,1 % del riesgo
                       bruta +0,0291 (z +1,13)   NETA -0,2577
                       IC95 [-0,309, -0,207]   z -9,90

**El criterio no se cumple.** El intervalo queda entero por debajo de cero.

## Su confirmación funciona, y es el mayor hallazgo del proyecto

Las dos confirmaciones declaradas de antemano:

| | acierto | riesgo | bruta | neta |
|---|---|---|---|---|
| C1 · entrar al cierre del barrido | 25,5 % | 3,9 p | −0,2363 | −0,7894 |
| **C2 · esperar confirmación (la suya)** | **34,3 %** | **5,7 p** | **+0,0291** | −0,2577 |

**Esperar a la confirmación vale +0,27 R en bruta.** Es la mejora más grande que
ha producido cualquier filtro en dos meses de pruebas, y la idea es suya.

Hace dos cosas a la vez: sube el acierto casi nueve puntos **y** ensancha el stop
de 3,9 a 5,7 pips, que baja el peaje del 37 % al 25 %. Las dos van en la buena
dirección.

## Pero la bruta es cero

    bruta +0,0291   z +1,13

Con 2R, el acierto de equilibrio en bruto es 33,3 %. La regla da 34,3 %. **Un
punto por encima del azar, y ese punto no es distinguible de cero.**

Esto importa porque cambia el diagnóstico. Las otras veces la ventaja bruta
existía y el coste se la comía. Aquí **no hay ventaja bruta que comerse**:
ensanchar el stop reduciría el peaje, pero no hay nada debajo que rescatar.

## El resto, informado como se prometió

Por sesión, por nivel y por año no cambia nada: todo negativo, sin excepción.

| año | acierto | riesgo | coste %R | bruta | neta |
|---|---|---|---|---|---|
| 2020 | 32,0 % | 6,5 p | 21,8 % | −0,039 | −0,295 |
| 2021 | 32,1 % | 5,0 p | 28,6 % | −0,037 | −0,345 |
| 2022 | 35,8 % | 7,8 p | 18,3 % | +0,074 | **−0,135** |
| 2023 | 36,4 % | 5,9 p | 24,2 % | +0,092 | −0,176 |
| 2024 | **37,6 %** | 4,4 p | 32,5 % | +0,127 | −0,249 |
| 2025 | 34,2 % | 5,9 p | 24,2 % | +0,025 | −0,250 |
| 2026 | 30,0 % | 4,7 p | 30,4 % | −0,100 | −0,428 |

Dos filas que conviene mirar juntas. **2024 tiene el mejor acierto de los siete
años (37,6 %) y aun así pierde 0,25**, porque el riesgo mediano era de 4,4 pips y
el coste se llevó un tercio. **2022 tiene peor acierto y es el año menos malo**,
porque el riesgo era de 7,8 pips. El orden de la columna neta lo pone el ancho
del stop, no el acierto.

Barrer el máximo (−0,261) y barrer el mínimo (−0,255) son idénticos. Londres
(−0,255) y Nueva York (−0,261), también.

## Reparto del riesgo

    10 %   2,9 p        mediana  5,7 p
    25 %   4,0 p        75 %     8,5 p
                        90 %    12,8 p

La mitad de las señales nacen con el coste llevándose más del 25 % del riesgo.

## Veredicto

La regla escrita, tal y como él la especificó, **no funciona**: bruta cero, neta
−0,26, sobre 3.055 operaciones y siete años sin un solo año positivo.

Lo que sí deja, y es suyo:

- **La confirmación en M5 vale +0,27 R en bruta**, medido y grande. Su intuición
  de no entrar al primer rechazo es correcta.
- La traducción es fiel: 1,92 operaciones al día contra las 1-2 que él hace. Eso
  deja **muy poco sitio** para que su criterio explique la diferencia — no está
  eligiendo 2 entre 50, está eligiendo 2 entre 2.
