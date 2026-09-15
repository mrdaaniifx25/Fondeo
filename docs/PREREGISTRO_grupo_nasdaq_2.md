# Preregistro · segundo pase de la estrategia del grupo

Firmado ANTES de implementar y correr. El primer pase (`6011c5b`,
resultados en `docs/RESULTADOS_grupo_nasdaq.md`) implementó 2 de sus 5
confluencias y disparó en el 91 % de las ventanas. Este pase implementa
las tres que faltaban. **No se cambia ninguna otra cosa.**

## Lo que se añade, y su definición operativa

    3 · JUDAS SWING
        acumulación: el rango de los 30 minutos anteriores a la apertura
                     no supera la mediana de ese mismo rango en los 20
                     días anteriores
        manipulación: entre la apertura y la barra de entrada, el precio
                     ha superado el extremo de la acumulación EN CONTRA
                     de la dirección del trade
        el gatillo cae dentro de la ventana, nunca en premarket    (nº20)

    4 · LRL A FAVOR
        existe un grupo de 3 o más pivotes de M1 alineados -dentro de una
        tolerancia del 10 % del rango de las últimas 2 horas- situados en
        la DIRECCIÓN DEL OBJETIVO

    5 · LRL EN CONTRA YA BARRIDA
        ningún grupo equivalente en la DIRECCIÓN DEL STOP, situado a menos
        de 2R de la entrada, sigue sin barrer en el momento de entrar

## Variantes, declaradas antes de correr

    PRINCIPAL   5 de 5 confluencias  (sus setups "A+")
    secundaria  4 de 5
    secundaria  3 de 5
    TP siempre a 1:1 (variante A del primer pase) para poder comparar.
    Se reporta además el TP al DOL con tope 4R.

## PREDICCIONES FIRMADAS

    1 · con 5 de 5, el número de operaciones queda entre 150 y 1.500

    2 · PRINCIPAL: la R bruta con 5 de 5 NO supera +0,10 con z > 2,0

    3 · el acierto con 5 de 5 queda entre el 45 % y el 55 %

    4 · la R NETA con 5 de 5 es negativa

    5 · NO hay mejora monótona: pasar de 3 a 4 a 5 confluencias reduce el
        número de operaciones pero no sube la R bruta media de forma
        significativa (|z| de la diferencia 5/5 contra 3/5 menor que 2,0)

## Umbrales

    |z| > 2,0 para declarar efecto.
    Menos de 100 operaciones en una celda: no se interpreta, y si eso
    ocurre con 5 de 5 la principal pasa a 4 de 5.

## Qué contaría como que ME EQUIVOCO, a favor de la estrategia

    R bruta con 5 de 5 por encima de +0,10 con z > 2,0 Y R neta positiva.
    Sería el primer resultado mecánico claramente positivo del proyecto.

## Compromiso

Este es el ÚLTIMO pase sobre estos datos. Si hiciera falta un tercero,
tendría que ser sobre datos reservados que aún no se han mirado, o sobre
las operaciones reales del grupo con sus precios y horas.

Sigue sin medirse LA BALANZA, que no es programable.
