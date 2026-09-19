# Resultados · las cuatro afirmaciones sobre el FVG

Pre-registro `docs/PREREGISTRO_fvg.md`. Código en `bt/fvg.py`.
Oro y DAX, M1 de 2023-01 a 2026-07. **34.000 FVG en M15**, 8.400 en H1.

## El resultado que lo explica todo

    el precio vuelve al FVG        90 %
    el precio recorre esa misma
    distancia en una vela normal   89 %

**El 90 % es verdad, y no significa casi nada.** El precio vuelve porque el hueco
estaba cerca, no porque sea un hueco. El FVG añade **un punto porcentual**.

## Las cuatro, una por una

### 1 · «El precio tiende a regresar al FVG» — CIERTA, y trivial

    oro M15   vuelve 89,5 %   listón 89,0 %   exceso +0,5 %  [+0,1, +0,9]
    DAX M15   vuelve 90,3 %   listón 89,3 %   exceso +1,0 %  [+0,5, +1,4]

Los dos intervalos quedan por encima de cero, así que por el criterio escrito es
cierta. Pero el tamaño es de **medio punto a uno**. Es de esas afirmaciones que
son verdad y aun así no te sirven de nada.

### 2 · «El de Consolidación tiene altas probabilidades de ser testeado» — CIERTA, y por el motivo equivocado

    oro M15   vuelve 94,2 %   listón 93,8 %   exceso +0,3 %  [-0,4, +1,1]
    DAX M15   vuelve 94,0 %   listón 93,9 %   exceso +0,2 %  [-0,6, +0,9]

Es el tipo con **más** vueltas de los tres, o sea que la afirmación acierta. Pero
su exceso es **cero**. Se testea más porque el hueco es más pequeño y está más
cerca, no porque sea de consolidación.

### 3 · «El Breakaway casi nunca se testea» — FALSA, y al revés de lo interesante

    oro M15   vuelve 84,2 %   listón 81,8 %   exceso +2,4 %  [+1,4, +3,4]
    DAX M15   vuelve 85,8 %   listón 83,3 %   exceso +2,5 %  [+1,5, +3,4]
    DAX H1    vuelve 87,8 %   listón 84,7 %   exceso +3,0 %  [+1,3, +4,8]

**«Casi nunca» es 85 % de las veces.** La afirmación confunde "menos que los
otros" con "casi nunca", y la diferencia es enorme si te quedas fuera esperando.

Y lo de verdad interesante: **el breakaway es el único tipo donde el FVG aporta
información real.** Su exceso es el mayor de los tres, replicado en los dos
instrumentos y en dos marcos. Es exactamente lo contrario de lo que dicen las
diapositivas.

### 4 · «Cuanto mayor la temporalidad, más peso» — A MEDIAS

    marco    exceso oro   exceso DAX
    M15        +0,5 %       +1,0 %
    H1         +0,3 %       +0,8 %
    H4         +0,6 %       -0,1 %
    D1         +4,5 %       +3,9 %

El diario destaca de verdad, con el intervalo por encima de cero en los dos. Pero
no hay gradiente: H1 y H4 no se ordenan. Y el diario tiene solo unos 200 casos,
así que el intervalo es ancho. **El diario sí, la escalera no.**

## Y el dato que de verdad sirve para leer el gráfico

    mediana de velas hasta volver al FVG:  1 a 3

Cuando vuelve, vuelve **enseguida**. No "en algún momento": en una, dos o tres
velas. Si han pasado cinco velas y el precio no ha vuelto, la probabilidad de que
vuelva ya no se parece en nada al 90 % de la diapositiva.

Eso sí es utilizable como lectura, y no está en ninguna de las quince
diapositivas.

## Veredicto

    1  cierta, y de un punto porcentual
    2  cierta, y por el motivo equivocado (exceso cero)
    3  FALSA: es el 85 %, y encima es el mejor de los tres
    4  solo en el diario, y sin escalera

El FVG no es humo: existe, es mecánico y tiene un exceso pequeño y medible. Lo
que es humo es **el tamaño que se le atribuye**. El 90 % que impresiona es el 89 %
que hace el precio de todas formas.
