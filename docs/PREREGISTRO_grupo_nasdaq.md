# Preregistro · la estrategia del grupo (NASDAQ / SP500)

Firmado ANTES de ejecutar el backtest. Especificación en
`docs/NASDAQ_grupo_ESPECIFICACION.md`, reglas en `docs/NASDAQ_grupo_reglas.md`.
Un solo pase. Sin barrido de parámetros después de ver el resultado.

## Qué se mide

Datos: NASDAQ y SP500, M1, 2020-01 a 2026-07 (~1.650 días por ventana).
Tres ventanas: Frankfurt, Londres y Nueva York. Una operación por ventana.

    R  = resultado en múltiplos del riesgo, bruto
    Rn = lo mismo descontando coste (1,50 pts NASDAQ · 0,50 pts SP500,
         AMBOS ESTIMADOS por mí, no medidos en su cuenta)

Bajo la hipótesis nula de entrada aleatoria con la misma geometría de
stop y objetivo, E[R] = 0. Está validado en `bt/valida_motor.py` con
128.000 entradas aleatorias: R bruta cero en 32 de 32 celdas.

## Variantes que se corren (todas en el mismo pase)

    A · TP a 1:1                        (lo que él hace en evaluación)
    B · TP al DOL, tope 4R              (lo que hace ya fondeado)
    C · A, solo operaciones CON SMT
    D · A, solo operaciones SIN SMT

## PREDICCIONES FIRMADAS

    1 · el número de operaciones queda entre 600 y 2.500

    2 · PRINCIPAL: la R bruta de la variante A NO supera +0,10
        con z > 2,0.  Es decir: predigo que NO bate al azar.

    3 · el acierto de la variante A queda entre el 45 % y el 55 %
        (el azar a 1:1 es 50 %)

    4 · la variante B tiene MAYOR R bruta media que la A, porque el
        1:1 exige más del 60 % de acierto y eso es el listón más duro

    5 · la R NETA de la variante A es negativa: el stop en el extremo
        de la inducción es estrecho y el coste pesa mucho sobre la R

    6 · C y D no se diferencian: |z| de la diferencia < 2,0.
        Es decir: el SMT no aporta.

## Umbrales

    Prueba principal (nº2): |z| > 2,0 para declarar que hay efecto.
    Diferencias entre variantes: |z| > 2,0.
    Cualquier resultado con menos de 100 operaciones no se interpreta.

## Qué contaría como que ME EQUIVOCO, y a favor de la estrategia

    R bruta de A o de B por encima de +0,10 con z > 2,0
    Y R neta positiva.

Si eso pasa, la estrategia del grupo sería el primer resultado
mecánico claramente positivo de todo el proyecto, por delante del
SMC-71, cuyo neto no está demostrado en ninguna temporalidad.

## Qué NO demuestra este backtest

No mide LA BALANZA -su juicio sobre confluencias a favor y en contra-
ni su decisión de saltarse sesiones. Mide LA ESTRATEGIA SIN SU OJO.
Un resultado plano deja abierta la posibilidad de que todo el valor
esté en la parte que no se puede programar, y eso solo lo contrastarían
sus operaciones reales con precios y horas.

## Limitaciones conocidas de los datos

    - serie del ÍNDICE, no del futuro NQ mini de la CME
    - granularidad mínima 1 minuto: los gatillos de 30 segundos que él
      usa en 3 de las 20 transcripciones no se pueden reproducir
    - el coste de ambos índices es estimación mía
