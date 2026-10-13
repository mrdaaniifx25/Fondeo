# Resultado · búsqueda amplia y mecánica de patrón en forex

Código en `bt/busqueda_ml.py`. Es la búsqueda más potente de todo el proyecto,
y también la que más fallos míos ha destapado.

## El montaje

No es una regla escrita a mano. Es un modelo de árboles impulsados
(`HistGradientBoostingRegressor`, 300 iteraciones, profundidad 4) buscando a
la vez en **~50 variables causales** por instrumento:

    retornos normalizados a 1, 2, 3, 6, 12, 24, 72 y 168 barras
    volatilidad corta / volatilidad larga
    posición dentro del rango de 24 y de 120 barras
    distancia a las EMA de 20, 50 y 200, en unidades de volatilidad
    RSI, cuerpo/rango, mecha superior, mecha inferior, aceleración
    hora del día, día de la semana
    ...y LO MISMO de los otros instrumentos (variables cruzadas)

**Validación hacia delante**: se entrena solo con el pasado de cada año y se
predice el año siguiente, que el modelo no ha visto nunca. 133.834
observaciones fuera de muestra por instrumento, en M15, 2020-2026.

## Lo que pareció que encontraba

    EURUSD   IC +0,0126   top 5 % bruto +0,371 pips   z +2,49   acierto 52,5 %
    GBPUSD   IC +0,0100   top 5 % bruto +0,431 pips   z +2,45   acierto 51,6 %

Y una curva de horizonte con forma sensata: la señal existe a 15 y 60 minutos
y **se muere a las 4 horas**.

    horizonte      IC       top 5 % bruto      coste/ventaja
    15 min      +0,0162        +0,175              8,2x
    60 min      +0,0126        +0,371              3,9x   <- el mejor punto
     4 horas    +0,0033        +0,331              4,3x
    12 horas    -0,0043        -1,560               --

Con selección extrema (top 0,2 %, n=267) la ventaja llegaba a **+1,225 pips**
con 59,2 % de acierto — casi el coste. Pero en GBPUSD el mismo corte daba
**-0,400**. No replicaba.

## Y el nulo lo tumbó

El mismo proceso entero -mismas variables, mismo modelo, misma validación
hacia delante- sobre datos barajados por bloques, donde **no hay nada que
encontrar**:

    EURUSD     IC        top 5 % bruto      z
    ---------------------------------------------
    REAL     +0,0126        +0,371        +2,49
    nulo 1   +0,0063        -0,078        -0,42
    nulo 2   +0,0260        +0,761        +4,28
    nulo 3   +0,0201        +0,525        +2,66
    nulo 4   +0,0137        +0,307        +1,83
    media    +0,0165

    GBPUSD
    REAL     +0,0100        +0,431        +2,45
    nulo 1   -0,0027        -0,140        -0,46
    nulo 2   +0,0020        -0,026        -0,09
    nulo 3   +0,0084        +0,373        +1,62

**Tres de cuatro nulos igualan o superan a los datos reales, y el IC real está
por debajo de la media de los nulos.** El +0,371 bruto del top 5 % es
exactamente lo que produce buscar en 50 variables con árboles impulsados
cuando no hay nada.

No es que la ventaja sea pequeña y el coste se la coma. **No hay ventaja.**

## Dos fallos míos en este mismo experimento

### 1 · el oro recortaba la muestra a la cuarta parte

`xauusd_m1` solo cubre 2023-2025. Al cruzarlo con los demás para las variables
cruzadas, el `dropna` dejaba **5.905 barras de 20.000**. Se sacó del conjunto
por defecto y la muestra pasó a 133.834.

### 2 · el primer nulo tenía fuga, y puntuaba MEJOR que la señal

Sorteaba inicios de bloque al azar **con reemplazo**. Con 1.665 bloques de
1.440 minutos sobre 2,4 millones de posiciones, miles de pares se solapaban,
así que trozos casi idénticos caían en entrenamiento y en prueba y el modelo
los memorizaba:

    nulo con fuga    IC +0,0373   ·   +0,0322   ·   +0,0144
    REAL             IC +0,0126

Los tres batían a los datos reales. **Un nulo que gana a la señal está roto**,
y ése fue el aviso. Corregido a una permutación de bloques consecutivos
disjuntos: cada minuto aparece exactamente una vez, volatilidad idéntica
(1,34e-04 en los dos casos).

## Lo que esto cierra

Es el último recurso metodológico que quedaba. Si un modelo con 50 variables,
133.834 observaciones fuera de muestra y validación hacia delante estricta no
encuentra nada por encima de su propio ruido, la conclusión no es "hay que
buscar mejor". Es que **en M15 y H1 de EURUSD y GBPUSD, con datos de precio,
no hay estructura predecible explotable**.

Coincide con lo medido por otras cinco vías en este proyecto, y con la
literatura: la ventaja que existe en estos mercados es del tamaño del coste
o menor.
