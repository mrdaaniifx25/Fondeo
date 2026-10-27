# Resultado · manipulación del rango asiático

Preregistro sellado en `aeddfb1`, antes de programar. Un solo pase.

## El resultado

      instr     n   acierto  R:R medio    stop   R bruta       z    R NETA
    ----------------------------------------------------------------------
     EURUSD   757     14.7 %       7.21    4.2p    +0.058   +0.58    -0.290
     GBPUSD   850     15.3 %       8.73    4.5p    +0.336   +2.87    -0.035
     USDJPY   544     11.4 %      11.94    4.6p    +0.063   +0.43    -0.279
    ----------------------------------------------------------------------
      TODOS  2151     14.1 %       9.00    4.4p    +0.169   +2.45    -0.186

    por tipo:  mecha líquida  2022  +0.183  z +2.53
               FVG             129  -0.037  z -0.16

## Las cinco predicciones firmadas

    1 · n entre 400 y 1.400                          FALLA (2.151)
    2 · acierto entre 22 % y 32 %                    FALLA (14,1 %)
    3 · la R bruta no supera +0,15 con z > 2         **FALLA: +0,169, z +2,45**
    4 · la R NETA es negativa                        ACIERTA (-0,186)
    5 · el 40 % que afirma no se reproduce           ACIERTA, y de sobra

## La nº3 es la primera derrota del proyecto en este sentido

En dos meses y diez familias medidas, es la primera vez que una prueba
principal preregistrada sale POSITIVA y en contra de lo que firmé.
+0,169 R brutas con z +2,45 sobre 2.151 operaciones no es ruido.

Hay que decirlo tal cual, porque la disciplina sirve justo para esto.

## Por qué las predicciones 1 y 2 fallaron: el ratio real no es 1:3

Él dice "mínimo 1:3" y sus ejemplos son de 3,1 a 3,5. En mi
implementación, con el stop acotado a 4-8 pips y el objetivo en el
extremo opuesto del rango, el ratio medio sale **9,0**.

Eso cambia el listón: a 1:9 el azar da 1/(1+9) = 10 %, no 25 %. El 14,1 %
medido está por ENCIMA de su listón correspondiente, y de ahí sale la R
bruta positiva.

O sea: mi predicción del acierto era contra el listón equivocado. La nº3,
que es la que importa, no depende de eso y falló limpiamente.

## Pero el neto sigue siendo negativo, y por lo que ya sabíamos

    stop medio 4,4 pips · coste EURUSD 1,43 pips
    -> el coste se lleva el 32 % de cada R

Es el muro de costes más alto de todo el proyecto. La aritmética estaba
calculada ANTES de correr nada y se cumple: bruto +0,169, neto -0,186.

## Lo que NO se reproduce

Él afirma 40 % de acierto en EURUSD y 52-54 % en GBPUSD.
Medido: 14,7 % y 15,3 %.

No es una diferencia de matiz. Con sus ratios de 1:3 y un 40 % saldrían
+0,60 R por operación; aquí salen +0,058 en EURUSD.

Y el efecto no está donde él lo pone: EURUSD, su instrumento principal,
da z +0,58. Todo el peso lo lleva GBPUSD. Por años, EURUSD va de +0,517
en 2025 a -0,515 en 2026. Inestable.

## Hipótesis que sale de aquí, SIN PROBAR

El edge bruto existe y lo mata el stop de 4-8 pips. Si el stop fuera al
extremo real de la mecha -a menudo 10-20 pips- el coste bajaría del 32 %
al 7-14 % de la R y el neto podría cambiar de signo.

Eso es una MODIFICACIÓN de su regla, no su regla. Probarlo ahora, después
de ver este resultado, sería exactamente la trampa que este proyecto
evita. Requiere preregistro nuevo y, a poder ser, datos reservados.
