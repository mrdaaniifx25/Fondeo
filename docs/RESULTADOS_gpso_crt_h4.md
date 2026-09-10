# La regla CRT del H4 · y una mirada al futuro que casi cuela

Del live 159:

> *«la clave es que cuando al precio de 4 horas le falta el mismo tiempo para
> cerrar que a la vela de una hora, esa entrada tiene mucha mayor probabilidad»*
>
> *«no una manipulación que me deje la entrada en una hora, sino que además tengo
> una manipulación que me lo deja en la temporalidad de 4 horas»*

Se probaron las dos partes por separado.

## El resultado que había que tirar

```
  la H4 también barre y cierra dentro   14.849   37,2 %   +0,121   z +10,24
  la H4 no lo hace                       5.567   23,0 %   -0,303   z -17,93
```

Catorce puntos de diferencia y z +10,24. **Es cuatro veces mayor que cualquier
cosa medida en este proyecto, y por eso se comprobó antes de reportarlo.**

Está mal. Es futuro:

| | n | cumplen la condición de H4 |
|---|---|---|
| la H1 **es** la última hora de la H4 | 4.368 | **99,9 %** |
| la H1 **no** es la última hora | 16.048 | 65,3 % |

Cuando la H1 del barrido es la última hora de su vela de H4, las dos cierran a la
vez y la condición se cumple sola: no informa de nada. Cuando **no** lo es, exigir
que la H4 «cierre dentro» es exigir que el precio siga del lado correcto **hasta
tres horas después** de la entrada. Y ahí está todo el efecto:

```
  no alineadas, cumplen la condición    10.487   39,1 %   +0,176
  no alineadas, no la cumplen            5.561   23,0 %   -0,302
```

Es el mismo fallo que `CORRECCION_mirada_al_futuro.md` de agosto, con otra cara.
**Descartado.**

## Su regla de verdad, sin futuro, no replica

La versión que él describe —H4 y H1 cerrando a la vez— no tiene futuro dentro,
porque en ese instante las dos velas cierran. Medida:

| rejilla de H4 | | n | acierto | R bruta | z |
|---|---|---|---|---|---|
| **UTC** | alineadas | 4.368 | 32,5 % | **−0,013** | −0,60 |
| | no alineadas | 16.048 | 33,5 % | +0,010 | +0,94 |
| **Madrid** | alineadas | 5.070 | 34,4 % | **+0,036** | +1,82 |
| | no alineadas | 15.346 | 32,9 % | −0,005 | −0,41 |

**En la rejilla UTC su regla sale ligeramente peor que no aplicarla.** En la de
Madrid sale débilmente mejor, sin llegar al umbral de +1,96.

Y que el signo dependa de dónde se empiecen a contar las velas de 4 horas es, por
sí solo, motivo para no fiarse: un efecto real no cambia de signo según si dibujas
las H4 desde medianoche UTC o desde medianoche de Madrid.

## Balance de sus reglas medidas

| regla suya | veredicto |
|---|---|
| exige manipulación (barrido con vuelta dentro) | **sostiene** · es lo único con ventaja bruta |
| la hora a la que se formó el nivel importa | **sostiene** · z +3,09, 4/4 instrumentos |
| las horas válidas son 2, 3 y 4 de la mañana | **falla** · el bloque que descarta es mejor |
| «que se quede cercano a la zona» | no aporta |
| entrada al cierre de H1 sin manipulación | no aporta |
| gestión a break-even en 1R | no aporta (+0,013 contra +0,009) |
| parciales del 80 % a 2R | **empeora** (−0,034) |
| CRT: H4 y H1 cerrando a la vez | **no replica** · negativa en UTC, débil en Madrid |

## Reproducir

`python3 bt/gpso_crt_h4.py`
