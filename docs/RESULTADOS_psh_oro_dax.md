# Resultados · el PSH, solo, en oro y DAX

Pre-registro: `docs/PREREGISTRO_psh_oro_dax.md`, subido **antes** de medir.
Código: `bt/psh_oro_dax.py`. Oro y DAX 2023-2026; EURUSD 2021-2026 de referencia.

## Veredicto

**No replica. El PSH queda cerrado, y con él la spec entera.**

## Con la cadena H4+H1 — donde apareció el candidato

```
  oro · margen 0,33×ATR    n  28   TP 28,6 %   bruta -0,076 [-0,580,+0,428]
  DAX · margen 0,33×ATR    n  16   TP 25,0 %   bruta -0,157 [-0,812,+0,499]
```

**28 y 16 operaciones.** El pre-registro decía que por debajo de 50 el resultado
es «no se puede saber» y no se lee el signo. Se cumple: no se lee. Los
intervalos van de −0,8 a +0,5.

(Para el registro: la referencia de EURUSD reproduce el candidato original —
n 52, TP 30,8 %, bruta +0,033. Era lo que había que confirmar antes de nada.)

## Sin la cadena — la versión que sí tiene muestra

```
  instrumento    margen      n    coste    TP      umbral    bruta                    neta
  EURUSD         0,33×ATR   340   14,8 %   29,1 %   38,3 %   +0,068 [-0,076,+0,211]  -0,081
  oro            0,33×ATR   202    7,7 %   29,7 %   35,9 %   +0,043 [-0,145,+0,231]  -0,034
  DAX            0,33×ATR   182    6,8 %   29,7 %   35,6 %   -0,010 [-0,205,+0,186]  -0,077
```

Y con los cuatro márgenes, el DAX sale **negativo o cero en los cuatro**
(−0,027 · −0,010 · −0,001 · −0,006).

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. bruta positiva en oro **y** DAX a la vez | **NO.** Oro sí, DAX no |
| 2. neta positiva con el IC95 limpio en alguno | **NO.** Ninguna celda cruza |
| 3. n ≥ 50 en la que cruce | no aplica |

El pre-registro decía: *«si el signo sale positivo en uno y negativo en el otro,
no replica, y eso cierra el PSH»*. Es lo que ha pasado.

## Los tres juntos — posterior al pre-registro

No estaba declarado. Es la forma más justa de preguntar «¿hay algo o no?»,
juntando toda la muestra en vez de mirar instrumento por instrumento:

```
  n 724    coste medio 10,8 % del riesgo
  acierto 29,4 %    azar 33,3 %    umbral 36,9 %
  BRUTA +0,0412 [-0,0574, +0,1397]
  NETA  -0,0671 [-0,1658, +0,0316]
```

La bruta es positiva y pequeña, con el cero dentro. Con 724 operaciones y ese
intervalo, **lo que se puede afirmar es que si hay ventaja, es menor de +0,14 R**,
y el coste vale 0,108. No queda hueco.

## El patrón, por quinta vez

Fíjese en la columna del coste. Es lo mismo que en `RESULTADOS_stop_minimo.md`,
`RESULTADOS_barrido_rr.md`, `RESULTADOS_sesiones_oro_dax.md` y
`RESULTADOS_techo_filtro.md`:

```
  EURUSD  coste 14,8 %   bruta +0,068   ->  neta -0,081
  oro     coste  7,7 %   bruta +0,043   ->  neta -0,034
  DAX     coste  6,8 %   bruta -0,010   ->  neta -0,077
```

En el oro el coste es la mitad que en EURUSD y **sigue sin bastar**, porque la
bruta también es la mitad. No es que el peaje sea caro: es que **la ventaja bruta
de cualquier patrón de gráfico intradía vive entre 0,00 y +0,10 R**, y el coste
vive en el mismo sitio. Cinco pruebas independientes, cinco veces el mismo número.

## Récord de predicciones

**Cinco de cinco.**

| predicción | resultado |
|---|---|
| 15-30 operaciones por instrumento con la cadena | 28 y 16 ✔ |
| no replicará: positivo en uno, negativo en el otro | oro +0,043, DAX −0,010 ✔ |
| sin cadena, plana o ligeramente negativa en los dos | exacto ✔ |
| el coste relativo bajará al 5-8 % y aun así no bastará | 7,7 % y 6,8 %, no basta ✔ |
| el PSH queda cerrado | cerrado ✔ |

## Qué queda de su spec

Nada operable. Los cuatro niveles medidos, los dos con muestra (EURUSD, oro)
por debajo del umbral, el tercero (DAX) negativo, y la cadena de confirmaciones
midiendo peor que el azar en el instrumento donde hay datos para verlo.

Lo que sigue vivo en el proyecto está en `RESULTADOS_momento_largo.md` y
`RESULTADOS_carry.md`, y no es intradía.
