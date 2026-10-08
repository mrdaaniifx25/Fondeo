# Pre-registro · las cuatro afirmaciones sobre el FVG

Escrito antes de medir. Material: 15 diapositivas de @snipertradingco, 19-09-2026.
Encargo suyo, literal: *"no lo quiero como estrategia, sino como complemento a mi
lectura del gráfico"*. Así que **no se mide si da dinero**: se mide si las
afirmaciones son ciertas.

## Con qué datos, y por qué no con EURUSD

El contenedor se reinició, el clon vino limpio y los parquet nunca estuvieron
versionados. HistData está bloqueado por la red. Lo que sobrevive en el
repositorio, en ZIP:

    oro (XAUUSD)   1.224.200 minutos   2023-01-02 a 2026-07-31
    DAX (GRXEUR)   1.026.084 minutos   2023-01-02 a 2026-07-31

Se mide en los dos. Si las afirmaciones son ciertas tienen que serlo fuera de su
par, así que esto es prueba más dura, no más blanda.

Nota de integridad: parte de este tramo (2026) fue el reservado que se gastó en
la prueba del filtro de Londres. Es una pregunta distinta y ortogonal, pero queda
dicho.

## La definición, mecánica

    FVG alcista en la vela i:  low[i] > high[i-2]   hueco [high[i-2], low[i]]
    FVG bajista en la vela i:  high[i] < low[i-2]   hueco [high[i], low[i-2]]

Tres velas, sin criterio.

## Las cuatro afirmaciones

1. **«El precio tiende a regresar al FVG.»**
2. **«El de Consolidación tiene altas probabilidades de ser testeado.»**
3. **«El Breakaway casi nunca se testea.»**
4. **«Cuanto mayor la temporalidad, más peso.»**

## Los tipos, separados mecánicamente

`r3 = recorrido de la vela 3 / recorrido de la vela 2`

    consolidación   r3 <= 0,50
    intermedio      0,50 < r3 < 1,00
    breakaway       r3 >= 1,00

## El listón, que es lo que hace que la prueba valga

El precio vuelve a cualquier sitio cercano casi siempre. Así que no basta con un
porcentaje: hay que compararlo con **lo que el precio hace normalmente**.

Para cada FVG se mide `d`, la distancia del cierre al borde del hueco en unidades
de ATR. El listón es la probabilidad empírica de que el precio recorra esa misma
distancia `d`, en esa misma dirección y en el mismo plazo, calculada sobre todas
las velas **que no son FVG**.

    exceso = % que vuelve al FVG  −  % que recorre esa distancia en general

**Si el exceso es cero, el FVG no añade nada:** el precio vuelve porque el hueco
estaba cerca, no porque sea un hueco.

## Horizonte

50 velas. Se informa también la mediana de velas que tarda en volver.

## El criterio

    1   cierta si el exceso tiene el IC95 entero por encima de cero
    2y3 ciertas si consolidación y breakaway se separan, y en el sentido dicho
    4   cierta si el exceso crece de M15 a D1

## Lo que se informa pase lo que pase

Los dos instrumentos por separado, los cuatro marcos, los tres tipos, alcistas y
bajistas, la mediana de velas hasta volver y el reparto de `d`.

## Lo que NO se mide, porque no es medible

Las huellas institucionales y los desequilibrios entre compradores y vendedores
son **el relato**. El hueco existe o no, y el precio vuelve o no. El porqué no
cambia el número.
