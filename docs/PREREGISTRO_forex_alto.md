# Preregistro · SMC-71 en forex, temporalidades altas

Firmado ANTES de medir. El usuario quiere forex, no índices.

## Por qué esta prueba y no otra

El Frankenstein de índices (`37fd375`) funcionaba por el coste/R, no por
los índices: 3-4 % en US100/GER40 contra 11-12 % en forex a M60. Y su
componente "solo compras" venía de la deriva alcista de la renta
variable, que en forex NO EXISTE (diferencia compras-ventas en forex a
M60: -0,054, z -0,33).

Lo único que se traslada es la señal del SMC-71 y la palanca del coste.
En forex esa palanca solo se ha probado hasta M60.

    EURUSD  M15 coste/R 27,3 %  ->  neta -0.187
            M30          19,8 %  ->        +0.093
            M60          12,2 %  ->        +0.017
            M120          ~6 %   ->        ?
            M240          ~3 %   ->        ?

## Qué se mide

SMC-71 sin cambios, en EURUSD, GBPUSD y USDJPY, a M60, M120 y M240.
FVG=no, filtro H4=sí, entrada al 71 %, R:R 2,45.
Costes: 1,43 · 1,60 · 1,50 pips.

## PREDICCIONES FIRMADAS

    1 · la R BRUTA se mantiene plana de M60 a M240: ninguna de las tres
        celdas se aleja más de 0,10 de la media de las tres

    2 · la R NETA mejora de forma monótona: M240 > M120 > M60

    3 · la R NETA de M240 es POSITIVA

    4 · pero NO es significativa: el intervalo bootstrap del 95 % de la
        neta de M240 incluye el cero, por falta de muestra

    5 · el número de operaciones en M240 queda entre 40 y 250

    6 · NO hay diferencia compras-ventas en forex a ninguna de las tres
        temporalidades (|z| < 2,0 en las tres)

## Umbral

    |z| > 2,0. Bootstrap de 20.000 remuestreos para la neta.
    Menos de 40 operaciones en una celda: no se interpreta.

## Qué contaría como que ME EQUIVOCO

    Que la R bruta se caiga al subir de temporalidad. Eso significaría
    que el SMC-71 tampoco es un mecanismo, sino un artefacto de la
    temporalidad concreta, y cerraría también el resultado de índices.
