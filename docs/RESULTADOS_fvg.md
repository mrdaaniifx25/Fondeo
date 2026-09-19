# Resultados · las cuatro afirmaciones sobre el FVG

Pre-registro `docs/PREREGISTRO_fvg.md`. Código en `bt/fvg.py`.
EURUSD (2021-2024 y 2026), oro y DAX (2023 a 2026-07).
**58.000 FVG en M15**, 14.000 en H1. Tres instrumentos.

## El resultado que lo explica todo

    el precio vuelve al FVG        90 %
    el precio recorre esa misma
    distancia en una vela normal   89 %

**El 90 % es verdad, y no significa casi nada.** El precio vuelve porque el hueco
estaba cerca, no porque sea un hueco. El FVG añade **un punto porcentual**.

## Las cuatro, una por una

### 1 · «El precio tiende a regresar al FVG» — CIERTA, y trivial

    EURUSD M15  vuelve 90,4 %   listón 89,6 %   exceso +0,9 %  [+0,5, +1,2]
    oro    M15  vuelve 89,5 %   listón 89,0 %   exceso +0,5 %  [+0,1, +0,9]
    DAX    M15  vuelve 90,3 %   listón 89,3 %   exceso +1,0 %  [+0,5, +1,4]

Los dos intervalos quedan por encima de cero, así que por el criterio escrito es
cierta. Pero el tamaño es de **medio punto a uno**. Es de esas afirmaciones que
son verdad y aun así no te sirven de nada.

### 2 · «El de Consolidación tiene altas probabilidades de ser testeado» — CIERTA, y por el motivo equivocado

    EURUSD M15  vuelve 93,7 %   listón 94,2 %   exceso -0,5 %  [-1,1, +0,1]
    oro    M15  vuelve 94,2 %   listón 93,8 %   exceso +0,3 %  [-0,4, +1,1]
    DAX    M15  vuelve 94,0 %   listón 93,9 %   exceso +0,2 %  [-0,6, +0,9]

Es el tipo con **más** vueltas de los tres, o sea que la afirmación acierta. Pero
su exceso es **cero**. Se testea más porque el hueco es más pequeño y está más
cerca, no porque sea de consolidación.

### 3 · «El Breakaway casi nunca se testea» — FALSA, y al revés de lo interesante

    EURUSD M15  vuelve 85,2 %   listón 82,8 %   exceso +2,4 %  [+1,6, +3,3]
    oro    M15  vuelve 84,2 %   listón 81,8 %   exceso +2,4 %  [+1,4, +3,4]
    DAX    M15  vuelve 85,8 %   listón 83,3 %   exceso +2,5 %  [+1,5, +3,4]

**+2,4 · +2,4 · +2,5 en tres instrumentos distintos.** Esa repetición es lo que
convierte esto en un hallazgo y no en una casualidad.

**«Casi nunca» es 85 % de las veces.** La afirmación confunde "menos que los
otros" con "casi nunca", y la diferencia es enorme si te quedas fuera esperando.

Y lo de verdad interesante: **el breakaway es el único tipo donde el FVG aporta
información real.** Su exceso es el mayor de los tres, replicado en los dos
instrumentos y en dos marcos. Es exactamente lo contrario de lo que dicen las
diapositivas.

### 4 · «Cuanto mayor la temporalidad, más peso» — A MEDIAS

    marco    EURUSD     oro      DAX
    M15       +0,9 %   +0,5 %   +1,0 %
    H1        +0,3 %   +0,3 %   +0,8 %
    H4        +0,6 %   +0,6 %   -0,1 %
    D1        -0,4 %   +4,5 %   +3,9 %

Con solo oro y DAX parecía que el diario destacaba (+4,5 y +3,9). **EURUSD lo
desmiente: -0,4 %.** Con 200-250 casos en diario, los intervalos son tan anchos
que aquello era ruido. No hay escalera y el diario tampoco aguanta.

Es un buen recordatorio de lo fácil que es creerse un hallazgo con dos
instrumentos y perderlo con el tercero.

## Y el dato que de verdad sirve para leer el gráfico

    mediana de velas hasta volver al FVG:  1 a 3

Cuando vuelve, vuelve **enseguida**. No "en algún momento": en una, dos o tres
velas. Si han pasado cinco velas y el precio no ha vuelto, la probabilidad de que
vuelva ya no se parece en nada al 90 % de la diapositiva.

Eso sí es utilizable como lectura, y no está en ninguna de las quince
diapositivas.

## Veredicto

    1  cierta, y de un punto porcentual
    2  cierta, y por el motivo equivocado: su exceso es cero en los tres
    3  FALSA: es el 85 %, y encima es el UNICO tipo con exceso real,
       replicado en los tres instrumentos con +2,4 / +2,4 / +2,5
    4  NO se sostiene: lo que parecia en oro y DAX lo desmiente EURUSD

El FVG no es humo: existe, es mecánico y tiene un exceso pequeño y medible. Lo
que es humo es **el tamaño que se le atribuye**. El 90 % que impresiona es el 89 %
que hace el precio de todas formas.
