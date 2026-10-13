# Pre-registro · la regla, fijada en 2020-2023 y soltada en 2024-2026

Escrito **antes** de mirar 2024-2026.

Petición suya, literal: *"no te pido una con un 90 % de winrate, te pido que
pueda ser rentable y poquito a poco ir escalando"*. Y la condición de antes:
sencilla, un ABC, que no dependa de cómo se sienta.

## De dónde sale

El modelo con 199.894 filas etiquetadas dio bruta **+0,050 (z +4,11)** fuera de
muestra, batiendo a los nulos por ocho veces. Es señal real.

Y al mirar **qué** había aprendido, la respuesta fue casi una sola cosa:

    riesgo en pips   0,7400   <- trece veces la siguiente
    coste %R         0,0576
    cerro_mas_alla   0,0214

O sea: el modelo aprendió **"quédate con las entradas de stop ancho"**. Eso no
necesita un modelo. Es un filtro de una línea, y por eso se puede escribir.

## La regla

    A   Barrido: el precio se lleva el extremo de la sesión de referencia
        y CIERRA de vuelta dentro (Londres barre Asia, NY barre Londres).
    B   Confirmación: una vela de M5 que cierra a favor del giro, y después
        el precio rompe el extremo opuesto de la vela del barrido. Ahí entras.
    C   Stop en el extremo del barrido. Objetivo 2R. No se mueve nada.

    FILTRO   si el stop queda a menos de X pips, NO SE OPERA.

Es exactamente la regla que él escribió el 16 de septiembre, con su confirmación,
más un único filtro.

## El único parámetro libre

**X**, el stop mínimo. Se elige mirando **solo 2020-2023**, del conjunto declarado
aquí y de ningún otro:

    X ∈ {10, 15, 20, 25, 30, 40} pips

Se coge el de mejor R neta dentro de muestra. Un solo parámetro, seis valores.

## Lo que se informa

**2024-2026 con la X elegida. Un número.** Y a dos niveles de coste:

    1,43 pips   su cuenta de hoy
    0,90 pips   cuenta de spread crudo, el suelo realista de retail

## El criterio

**Funciona si la R neta de 2024-2026 es positiva con el IC95 entero por encima de
cero**, a 0,90 pips de coste.

Si sale positiva pero con el cero dentro, se dirá exactamente eso y no se
presentará como que funciona.

## Lo que se dirá pase lo que pase

Las operaciones al mes que deja el filtro. Si son menos de dos al mes, la regla
puede ser correcta y aun así no servir para lo que él quiere, y se dirá.

## Por qué esta prueba vale y las anteriores no del todo

Todo lo medido hasta ahora se buscaba y se medía sobre los mismos años. Aquí el
parámetro se fija a ciegas sobre el primer tramo y el segundo no se toca hasta
tener la elección hecha. Es la única forma de que el número de 2024-2026
signifique algo.
