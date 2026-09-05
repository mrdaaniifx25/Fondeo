# Resultado · Strategy 4.3.23 "Improved 5.1.20" · XAUUSD H1

Implementada literalmente desde la especificación, sin añadir nada.
Código en `bt/sqx_xauusd.py` y `bt/sqx_controles.py`. Ejecución **minuto a
minuto** dentro de cada vela H1. Datos: XAUUSD M1, 2023-01 → 2026-07.

## El backtest, tal cual

    operaciones          581
    periodo              2023-01-12 -> 2026-07-30   (3,55 años)
    capital final        171.235 $   (+71,2 %)
    CAGR                 +16,38 %
    acierto              42,5 %
    profit factor        1,181
    payoff               1,598
    drawdown máximo      -13,5 %
    racha máxima de pérdidas   13
    salidas: 279 por stop · 302 por tiempo
    coste total          12.540 $   (1,5 % del bruto movido)

      año   ops         neto   acierto
     2023   113       +6.511     37,2 %
     2024   172      +15.869     41,9 %
     2025   219      +43.617     47,0 %
     2026    77       +5.239     39,0 %

Positiva los cuatro años. **Es el primer resultado neto positivo y grande de
todo el proyecto.**

## Los cuatro controles: los pasa

La estrategia la generó **StrategyQuant X**, que busca entre millones de
combinaciones. Los parámetros exactos son los supervivientes de esa búsqueda,
así que había que apretarla.

### 1 · ¿bate a entrar largo al azar?

El oro pasó de 1.850 a 3.300 en el periodo. Con la misma geometría (mismo
stop, misma salida a 5 barras, mismos costes) pero entradas al azar:

    azar 1..8:  -3,4 %  +20,2 %  -22,9 %  +7,6 %  -26,5 %  0,0 %  -63,0 %  -16,4 %
    media -13,1 %        ·        BASE +68,6 %        ->  los bate a los 8

Por operación: **+117 $ la estrategia contra -11,5 $ el azar.**

### 2 · ¿es un filo de navaja de la búsqueda?

    GannHiLo 3/4/8/13         +68,6  +67,2  +59,7  +83,6 %
    máximo 30/40/65/80 velas  +43,0  +32,3 +110,8  +75,6 %
    ATR 60/75/120/150         +70,1  +70,5  +69,2  +74,9 %
    salida 3/4/7/10 barras    +40,6  +91,5  +30,4  +95,8 %
    validez 5/20              +98,2  +48,1 %
    SIN filtro GannHiLo       +87,8 %

    19 de 19 vecinos POSITIVOS  ·  media +69,4 %
    la BASE está en el percentil 42 de su propio vecindario

**Es una meseta ancha, no un pico.** Eso es lo contrario del sobreajuste
típico. Y un detalle que la propia estrategia no sabe: **sin el filtro
GannHiLo gana más (+87,8 %)**. El filtro no aporta nada, es decoración. Lo que
funciona es la rotura de 51 velas más la geometría de salida.

### 3 · ¿y sobre oro sin ninguna estructura?

Bloques de un día permutados, misma volatilidad:

    nulos:  -34,4 %   -29,5 %   -68,3 %   -32,1 %      (los cuatro negativos)
    BASE:   +68,6 %                                    ->  los bate a los 4

### 4 · ¿bate a comprar oro y esperar?

                          retorno     CAGR    DD max   ret/DD
    comprar y esperar      121,3 %   24,90 %  -28,8 %    4,22
    la estrategia           68,6 %   15,74 %  -13,5 %    5,09

**En rentabilidad bruta, NO: comprar y esperar ganó casi el doble.** Ajustado
por riesgo sí gana (5,09 contra 4,22) y con la mitad de drawdown, pero hay que
decir las dos cosas.

## Lo que hay que decir en contra

    Sharpe anualizado                        +0,81
    t del retorno diario (1.294 días)        +1,84      <- no llega a 2
    años necesarios para demostrarlo         6,1
    periodo cubierto                         3,55

Un Sharpe de 0,81 es bueno de verdad -por encima de la literatura de
seguimiento de tendencia- pero **3,55 años no bastan para demostrarlo**, y son
3,55 años de un mercado alcista histórico del oro. Un único régimen.

Y mis datos empiezan en 2023: es muy probable que **solapen con el periodo en
que StrategyQuant la optimizó**. El único tramo razonablemente fuera de
muestra es 2026, y ahí hace +3,2 % en siete meses, el más flojo de los cuatro.

## Y lo importante para lo que usted quiere

P(pasar el reto de FundingPips) con esta estrategia, según el riesgo por
operación:

    riesgo/op   vol anual   fase 1   fase 2   las dos    vs azar 36,9 %
        1 %       14,9 %    36,9 %   58,2 %    21,5 %       -15,4 pp
        2 %       29,8 %    60,3 %   70,8 %    42,7 %        +5,8 pp   <- óptimo
        3 %       44,7 %    51,7 %   61,4 %    31,8 %        -5,1 pp
        5 %       74,5 %    41,6 %   47,8 %    19,9 %       -17,0 pp

**Con el 1 % de riesgo que trae la especificación, esta estrategia -que tiene
ventaja real- pasa el reto MENOS veces (21,5 %) que no tener ninguna ventaja
con la geometría bien puesta (36,9 %).** Porque es buena y lenta, y el reto da
60 días.

Doblando el riesgo al 2 % pasa al 42,7 % y sí bate a la geometría, por 5,8
puntos. Ése es el único ajuste que hay que hacerle.

En cuenta propia, en cambio, el 1 % es lo correcto: 12,1 % anual esperado con
un peor año típico de -17,7 %. Al 2 % el peor año típico es -35,5 %.
