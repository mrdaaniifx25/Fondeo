# Preregistro · manipulación del rango asiático (Tradinverso)

Firmado ANTES de programar y medir. Reglas tomadas literalmente del vídeo,
sin añadir ni quitar nada.

## La estrategia, tal cual la explica

    INSTRUMENTO   EURUSD (también GBPUSD, que él reporta aparte)
    RANGO         alto y bajo entre las 01:00 y las 08:00 hora de España
    VENTANA       08:00 a 10:30 hora de España
    TEMPORALIDAD  M15, y solo M15 ("no vamos a subir de temporalidades,
                  no vamos a buscar dirección del día")
    SETUP         por ENCIMA o por DEBAJO del rango, un FVG o una MECHA
                  LÍQUIDA en M15
    ENTRADA       orden LIMITADA en el 50 % de ese FVG o de esa mecha
    DIRECCIÓN     reversión: setup arriba -> ventas; abajo -> compras
    STOP          al otro lado de la mecha o el FVG, entre 4 y 8 pips,
                  ajustado para que el ratio dé como mínimo 1:3
    OBJETIVO      el EXTREMO OPUESTO del rango asiático
    RATIO         mínimo 1:3; si no llega, no se opera
    FRECUENCIA    una operación al día

## Lo que él afirma

    2024  GBPUSD 52 % de acierto · +90 % de rentabilidad
          EURUSD 40 % de acierto · +46 %
    2025  54 % de acierto · +62,8 %

Con 1:3 y 40 % de acierto salen +0,60 R brutas por operación.

## La aritmética del coste, calculada antes de mirar los datos

    coste real EURUSD verificado: 1,43 pips
    listón geométrico a 1:3: 25,0 %

    stop 4 pips  ->  coste 35,8 % de la R  ->  break-even 33,9 %
    stop 6 pips  ->  coste 23,8 %          ->  break-even 30,9 %
    stop 8 pips  ->  coste 17,9 %          ->  break-even 29,5 %

Necesita entre +4,5 y +8,9 puntos sobre el azar solo para no perder.

## PREDICCIONES FIRMADAS

    1 · el número de operaciones queda entre 400 y 1.400

    2 · PRINCIPAL: el acierto queda entre el 22 % y el 32 %, es decir
        pegado al listón geométrico del 25 %

    3 · la R bruta NO supera +0,15 con z > 2,0

    4 · la R NETA es negativa

    5 · el 40 % que él afirma NO se reproduce: el acierto medido queda
        al menos 8 puntos por debajo de 40 %

## Umbral

    |z| > 2,0 para declarar efecto. Un solo pase.
    Se mide EURUSD y GBPUSD por separado, y también USDJPY como control.

## Qué contaría como que ME EQUIVOCO

    Acierto por encima del 32 % con z > 2,0 y R neta positiva.
    Sería, con diferencia, el mejor resultado de todo el proyecto, y la
    primera estrategia enteramente mecánica que lo consigue.
