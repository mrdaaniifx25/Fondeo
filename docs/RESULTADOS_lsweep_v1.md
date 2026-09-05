# Resultado · EUR/USD London Liquidity Sweep V1

Preregistro sellado antes de medir. Código en `bt/lsweep_v1.py`.
EURUSD M1, 2020-01 → 2026-07, hora de Londres, ejecución minuto a minuto.
Coste 1,43 pips fijos, declarado antes y no tocado después (regla 24).

## Primero, lo que hay que reconocerle al protocolo

Es la especificación mejor escrita de los dos meses de proyecto, y no por poco.
Prohíbe explícitamente el look-ahead con un ejemplo (regla 29), define los
swings mecánicamente (3 velas, regla 7), exige desplazamiento medible
(Body/Range ≥ 0,50), filtra por RR antes de entrar, lista 20 condiciones de
NO TRADE, y hasta incluye una regla de no-optimización prematura (34).

**Pude programarla sin inventarme casi nada.** Eso, por sí solo, la pone por
encima de todo el material anterior.

## El resultado

    555 operaciones · 7,1 al mes · 2020-01-08 → 2026-07-30

    riesgo mediano       6,8 pips     ->  el coste se lleva el 31,5 %
    RR mediano           2,85
    resultados           TP 92  ·  SL 442  ·  sin resolver 21
    win rate             19,5 %

    R BRUTA media       -0,2263    z  -2,93
    R NETA  media       -0,5411    z  -7,01
    profit factor neto   0,491
    R acumulada         -300,3     drawdown máximo -310,9 R

     año   ops  winrate    R neta     acum
    2020    84    19,0 %  -0,5171    -43,4
    2021   110    18,2 %  -0,7055    -77,6
    2022    75    22,7 %  -0,3361    -25,2
    2023   104    18,3 %  -0,5735    -59,6
    2024    74    14,9 %  -0,7421    -54,9
    2025    68    19,1 %  -0,6356    -43,2
    2026    40    30,0 %  +0,0934     +3,7

Seis de siete años negativos. El positivo tiene 40 operaciones.

## El número que lo explica todo

Con un RR mediano de 2,85, la probabilidad geométrica de acertar **sin ninguna
ventaja** es `1/(1+2,85) = 26,0 %`.

    la secuencia SWEEP -> MSS -> DESPLAZAMIENTO -> FVG acierta el 17,2 %
    (92 de 534 operaciones resueltas)

Está **9 puntos por debajo del azar**. No es que la ventaja sea pequeña: la
secuencia selecciona peor que no seleccionar.

## ¿Es la señal o es el stop de 1 pip?

Ésta era la pregunta importante, porque el stop del protocolo deja 6,8 pips y
ahí el peaje es el 31,5 %. Se repite todo cambiando **solo** el buffer:

     buffer     n    stop  coste/R     TP/SL     BRUTA       z      NETA       z
        1,0   555    6,8p    31,5 %   92/442   -0,2263   -2,93   -0,5411   -7,01
        3,0   523    8,6p    26,0 %   84/414   -0,2817   -4,24   -0,5419   -7,79
        6,0   464   11,3p    21,0 %   74/349   -0,2143   -3,01   -0,4240   -5,72
       10,0   378   14,9p    14,8 %   49/275   -0,1863   -2,10   -0,3339   -3,80
       20,0   213   24,8p    10,7 %   15/137   -0,2864   -3,53   -0,3933   -4,70

**No es la geometría. Es la señal.** El coste baja del 31,5 % al 10,7 % -tres
veces menos- y la ventaja bruta no mejora en ningún tramo.

Esto separa esta estrategia de casi todo lo demás del proyecto. En SMC-71 y en
el rango asiático de Tradinverso había ventaja bruta real que el coste se
comía. Aquí no hay nada que comerse.

## El análisis por subgrupos que pide el propio protocolo (sección 33)

    POR DIRECCION            n  winrate    BRUTA       z
      SHORT (Asia High)    283   20,5 %  -0,1694   -1,41
      LONG  (Asia Low)     272   18,4 %  -0,2854   -2,95

    POR DIA
      lunes                 79   29,1 %  +0,0301   +0,16
      martes               116   13,8 %  -0,2795   -1,23
      miercoles            112   19,6 %  -0,3207   -2,43
      jueves               127   22,0 %  -0,0904   -0,55
      viernes              121   15,7 %  -0,3978   -2,91

    POR RANGO ASIATICO
      10-15 pips           170   17,6 %  -0,1263   -0,69
      15-20                138   20,3 %  -0,2571   -2,02
      20-25                113   21,2 %  -0,2945   -2,19
      25-30                 90   22,2 %  -0,2161   -1,39
      30-35                 44   13,6 %  -0,3613   -1,38

    POR RR
      2 - 2,5              216   23,1 %  -0,2504   -2,69
      2,5 - 3               75   25,3 %  -0,1064   -0,59
      3 - 4                 80   22,5 %  -0,0587   -0,29
      > 4                  182   11,0 %  -0,3287   -1,90

**Ninguno de los 16 subgrupos tiene ventaja bruta positiva con z > 2.** El
único con signo positivo es el lunes (+0,0301, z +0,16), que es cero.

Y aunque hubiera aparecido uno: 16 subgrupos son 16 comparaciones. Con ventaja
cero, la probabilidad de que alguno diera z > 2 por azar rondaría el 40 %.

## Los cinco criterios firmados

    1  expectativa BRUTA positiva con z > 2     -0,2263 (z -2,93)   FALLA
    2  expectativa NETA positiva                -0,5411             FALLA
    3  bate a entradas al azar                  ver abajo           FALLA
    4  al menos 250 operaciones                 555                 PASA
    5  profit factor neto > 1,15                 0,491              FALLA

El criterio 3 no necesita simulación: con RR 2,85 y sin ventaja, la esperanza
en R es **cero** por construcción de las barreras. La estrategia da -0,2263
con z -2,93. Está significativamente **por debajo** de entrar al azar.

## Mi predicción, y en qué acerté y en qué no

Firmé dos cosas. **Acerté** que el filtro de RR ≥ 2 sería influyente: descarta
234 días y define la geometría entera. **Me equivoqué** en la otra: predije
menos de 300 operaciones y salieron 555, así que la muestra sí llega a lo que
el propio protocolo pide como mínimo. No hay excusa de tamaño muestral.

## Tres fallos míos, corregidos antes de dar resultados

1. **Cerraba la posición al final de la ventana.** La ventana 07:30-10:30
   limita cuándo se ABRE (regla 23); el SL y el TP son fijos (regla 18). Con
   stop de 7 pips y objetivo a 20, darle minutos en vez de horas la mataba por
   construcción. El reparto TP/SL pasó de 38/313 a 92/442.

2. **Los procesos hijos de la sensibilidad sobrescribían el CSV**, así que el
   primer análisis por subgrupos salió de la muestra del buffer de 20 pips
   (213 operaciones) en vez de la del protocolo (555). Detectado porque los
   subgrupos no sumaban. Corregido metiendo el buffer en el nombre del
   fichero.

3. Una línea muerta duplicada en el cálculo del stop.

## Lo que NO pude implementar, y sesga a favor de la estrategia

**El filtro de noticias (regla 22).** No tengo calendario macro de 2020-2026.
Declarado en el preregistro antes de medir. Mitigante: la ventana 07:30-10:30
deja fuera casi todo lo grande (NFP y CPI de EE.UU. a las 13:30, FOMC a las
19:00, tipos del BCE a las 13:15). Lo que sí cae dentro es el CPI de la zona
euro (10:00) y los datos alemanes.

Esas operaciones que la estrategia habría evitado aquí sí cuentan, así que el
resultado real sería algo **mejor** que -0,2263. No lo suficiente: haría falta
que el filtro de noticias explicara 0,23 R de media sobre 555 operaciones.
