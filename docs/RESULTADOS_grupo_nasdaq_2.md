# Resultado · segundo pase de la estrategia del grupo

Preregistro sellado en `dcfbfe7`, antes de implementar las tres
confluencias que faltaban. Un solo pase.

## El resultado

                       exigencia      n   acierto   R bruta       z    R NETA
    --------------------------------------------------------------------------
             3 de 5 confluencias   9277     48.4 %    -0.035   -3.36    -0.187
                          4 de 5   9078     48.5 %    -0.032   -3.05    -0.191
            5 de 5  ·  PRINCIPAL   3258     47.8 %    -0.044   -2.55    -0.227

         con TP al DOL (tope 4R)
                          5 de 5   3258     42.9 %    -0.014   -0.65    -0.197

        diferencia 5/5 menos 3/5    -0.010   z = -0.49

## Las cinco predicciones firmadas

    1 · n con 5/5 entre 150 y 1.500                       FALLA (3.258)
    2 · PRINCIPAL: R bruta con 5/5 no supera +0,10, z>2    ACIERTA
    3 · acierto entre 45 % y 55 %                          ACIERTA (47,8 %)
    4 · R neta negativa                                    ACIERTA (-0,227)
    5 · sin mejora monótona al exigir más confluencias     ACIERTA (z -0,49)

## Lo importante: ahora la frecuencia SÍ coincide con la suya

    3.258 operaciones en 1.253 días distintos
    NASDAQ  1,29 al día · opera el 84 % de los días
    SP500   1,31 al día · opera el 83 % de los días

Él dice: una operación al día, y hay días que ninguna. Con las cinco
confluencias exigidas, la reconstrucción opera a SU RITMO. El problema
del primer pase -disparar en el 91 % de las ventanas- está resuelto.

Y a su ritmo, la estrategia sigue sin tener ventaja.

## Sus confluencias no discriminan

    Judas Swing        se cumple el 29,8 %  ·  con -0.063  sin -0.023  z -1.78
    LRL a favor        se cumple el 81,4 %  ·  con -0.043  sin +0.002  z -1.73
    LRL contra barrida se cumple el 100 %   ·  no filtra (ver abajo)

Ninguna mejora el resultado. Las dos que filtran apuntan al lado
CONTRARIO del que él afirma, aunque sin alcanzar significación.

Y exigir las cinco en vez de tres empeora ligeramente: -0.044 frente a
-0.035. Es la predicción nº5 y se cumple.

## Un fallo de mi implementación, declarado

"LRL en contra ya barrida" se cumple el 100 % de las veces: mi definición
-ningún grupo de 3+ pivotes sin barrer a menos de 2R en la dirección del
stop- no llega a excluir nada nunca. Esa confluencia, en la práctica, no
está medida. Las otras dos sí.

## Qué queda establecido, sumando los dos pases

    - A la frecuencia real a la que él opera, el esqueleto mecánico
      completo NO tiene ventaja: -0,044 bruto, -0,227 neto.
    - El SMT no aporta          (pase 1, z -0,21 sobre 9.277)
    - Las confluencias no aportan (pase 2, z -0,49)
    - El TP a 1:1 es peor que el TP al DOL, otra vez.
    - No es estable: 2023 sale plano-positivo, 2022 y 2025 negativos.
      No hay ventaja ni anti-ventaja robusta.

## Qué sigue sin estar medido

LA BALANZA. Su juicio sobre qué confluencias pesan más en cada caso
concreto. No es programable desde vídeos y este backtest no la toca.

La única forma de medirla es el registro real de operaciones del grupo:
entrada, stop, objetivo, instrumento y hora. Con 30-50 operaciones reales
se puede comparar su selección contra las señales que la reconstrucción
genera esos mismos días, que es exactamente el examen del bloque 8 pero
aplicado a él en lugar de al usuario.

## Décima familia medida en el proyecto

Y la décima que aterriza en el listón geométrico o por debajo.
