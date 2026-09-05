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

## Control 5 · la prueba más dura: otros instrumentos, otro periodo

StrategyQuant optimizó sobre XAUUSD, probablemente en un tramo que solapa con
mis datos. Los índices americanos y el forex cubren **2020-2026**, que esa
búsqueda no vio. Mismas reglas (sin el filtro GannHiLo, que no aporta):

    instr                periodo     n       ret     CAGR     PF      t
    XAUUSD    2023-01 -> 2026-07   597     +87,8 % +19,40 %  1,202  +1,80
    US100     2020-01 -> 2026-07  1279      -5,4 %  -0,84 %  0,992  -0,11
    US500     2020-01 -> 2026-07  1291     -82,4 % -23,29 %  0,773  -3,58
    GER40     2023-01 -> 2026-07   606    +896,3 % +91,15 %  1,247  +0,75
    EURUSD    2020-01 -> 2026-07   974     -83,7 % -24,18 %  0,744  -3,31
    GBPUSD    2020-01 -> 2026-07  1032     -77,5 % -20,41 %  0,782  -2,96

**Funciona en 2 de 6.** Y los dos que funcionan -oro y GER40- son justo los
dos cuyos datos empiezan en 2023.

El +896 % del GER40 no es lo que parece: su `t` es **+0,75**. Es interés
compuesto sobre unos pocos aciertos grandes, no una ventaja demostrada.

### ¿es del instrumento o del régimen alcista?

2023-2026 fue alcista puro. Si la ventaja fuera "romper al alza en un mercado
alcista", debería aparecer también en el US100 de 2023-2026, que subió mucho.
Partiendo cada instrumento en los dos tramos:

    instr           tramo     n       ret     PF      t
    XAUUSD      2023-2026   597    +87,8 %  1,202  +1,80
    GER40       2023-2026   606   +896,3 %  1,247  +0,75
    US100       2020-2022   585     -2,2 %  0,992  -0,08
    US100       2023-2026   694     -3,2 %  0,992  -0,08
    US500       2020-2022   588    -45,8 %  0,784  -2,42
    US500       2023-2026   703    -36,6 %  0,758  -2,79
    EURUSD      2023-2026   506    -39,6 %  0,631  -4,04
    GBPUSD      2023-2026   560    -28,8 %  0,769  -2,29

**No es el régimen.** El US100 subió con fuerza en 2023-2026 y la estrategia
no gana nada ahí (PF 0,992). Es específica del oro (y del GER40).

## Veredicto

Lo que tiene a favor, y no es poco -nada en este proyecto lo había logrado:

    · bate a 8 de 8 controles de entrada al azar con su misma geometría
    · 19 de 19 vecinos de parámetros positivos: meseta, no filo
    · bate a 4 de 4 nulos con los bloques permutados
    · mejor retorno/drawdown que comprar y esperar oro (5,09 contra 4,22)
    · positiva los cuatro años

Lo que tiene en contra:

    · t = +1,80 sobre 597 operaciones: NO llega a 2
    · Sharpe +0,81 necesita 6,1 años para demostrarse; hay 3,55
    · no generaliza: 2 de 6 instrumentos, y los 2 son los del mismo tramo
    · el tramo más limpio (2026) es el más flojo: +3,2 % en siete meses
    · el filtro GannHiLo, que es la parte "inteligente", no aporta nada

**Puede ser real y 3,55 años de un solo instrumento no bastan para saberlo.**
Es la misma conclusión de siempre, pero por primera vez con un candidato que
supera sus propios controles internos.

## Qué hace, en números reales de las 581 operaciones

    distancia del stop (1 x ATR95)   mediana  6,82 $   (rango 2,45 a 88,24)
    tamaño de posición               mediana  1,77 lotes = 177 onzas
    riesgo por operación             mediana  1.227 $
    tiempo en el mercado             mediana  4,2 h    (máximo 79,2 h)
    noches aguantadas                0,20 de media (94 operaciones pagan swap)

    cuando GANA (247, 42,5 %)    mediana +1.480 $    mayor +8.102 $
    cuando PIERDE (334, 57,5 %)  mediana -1.199 $    mayor -1.929 $

    salidas por TIEMPO (302): ganan el 82 %
    salidas por STOP   (279): ganan el  0 %

Pierde más veces de las que gana. Vive de que las ganancias son un 24 % más
grandes que las pérdidas.

## Control 6 · el coste, que es lo que decide si él puede operarla

La especificación asume spread de 0,20 $. La estrategia opera de 01:30 a
23:30, o sea también en horas asiáticas, donde el oro se ensancha.

      spread   comisión   swap |   ret     CAGR     PF      DD       t
        0,20          6     35 | +87,8 % +19,42 %  1,202  -13,2 %  +1,80
        0,30          6     35 | +52,9 % +12,70 %  1,135  -14,1 %  +1,24
        0,35          6     35 | +43,1 % +10,62 %  1,114  -14,6 %  +1,05
        0,50          6     35 | +10,6 %  +2,88 %  1,032  -22,5 %  +0,30
        0,65          6     35 | -19,9 %  -6,06 %  0,931  -40,5 %  -0,70
        0,80          6     35 | -37,7 % -12,46 %  0,855  -51,1 %  -1,49
        1,00          6     35 | -55,3 % -20,27 %  0,763  -62,9 %  -2,49
        0,20          0      0 |+109,4 % +23,15 %  1,238  -12,7 %  +2,08

**El punto de equilibrio está en un spread de 0,52 $ aproximadamente.** Por
debajo gana, por encima pierde. Y entre 0,20 y 0,35 el resultado ya se parte
por la mitad.

Esto convierte la pregunta abierta de todo el proyecto en una pregunta con
respuesta concreta y comprobable: **¿cuál es el spread medio real del XAUUSD
en su cuenta, incluyendo las horas malas?** Si está por debajo de 0,35, la
estrategia tiene sentido. Si ronda 0,50, no.
