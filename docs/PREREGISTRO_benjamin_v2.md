# Pre-registro · la regla de Benjamín, versión completa

Escrito y subido ANTES de medir. 21/09/2026. Tres transcripciones más
(estrategia en 10 min, operación en directo, «la estrategia que cambia vidas»).

## Lo que añaden sobre `PREREGISTRO_benjamin_regla.md`

La versión anterior sólo pedía el hueco. Ésta pide **dos confirmaciones en
orden** y matiza la entrada:

1. **Cambio de estructura primero**, y **con cuerpo**: *«los cambios de
   estructura con mecha… a mí no me valdría… la cuestión es que te cierre con
   cuerpo»*.
2. **Después el desequilibrio** (FVG).
3. **Entrada al mitigar el hueco**: *«cuando el precio toque ese vacío, pum,
   orden a mercado»*. No al cierre de la vela que lo crea.
4. **Jerarquía de niveles**: máximo/mínimo de la **semana** anterior (PWH/PWL),
   del **día** anterior (PDH/PDL), de **H4** y de **H1**.

## El dato que faltaba, y ya lo tenemos

En la operación en directo: **20 lotes** (15 + 5) con **~1.600 €** de riesgo
total en el stop.

```
1.600 € / (20 lotes × 8,62 €/pip) = 9,3 pips de stop
```

Coincide con lo medido en `RESULTADOS_benjamin_regla.md` (6,4 p en M2, 10,1 p
en M5). **Su stop está donde yo lo estaba poniendo.**

Y él lo dice explícitamente: *«un stop loss pequeñito y un profit alto»*.

## La regla, mecanizada

- **Niveles**: PWH/PWL, PDH/PDL, pivotes de H4 y de H1 (3 velas a cada lado,
  usables 3 velas después).
- **Barrido** de un nivel dentro de **Londres 09:00-11:00** o
  **NY 14:00-16:30** (Madrid).
- **Cambio de estructura** en la temporalidad de entrada: rompe el último
  extremo del último impulso **a favor del giro**, y el **cierre** queda al
  otro lado (con cuerpo).
- **Desequilibrio** después: tres velas donde la 1ª y la 3ª no se tocan, a
  favor del giro.
- **Entrada**: cuando el precio **vuelve al hueco** (orden límite en el borde).
  Variante de control: a mercado al cierre de la vela del hueco.
- **Stop**: el extremo del barrido.
- **Objetivo**: **1:2**.
- Máximo 40 velas entre barrido y cambio de estructura, y 20 entre cambio y
  hueco. Una por nivel y día.

## Celdas declaradas

| eje | opciones |
|---|---|
| temporalidad de entrada | **M1** · **M2** · **M5** |
| entrada | **al mitigar el hueco** · **a mercado al cierre** |

Seis celdas, todas publicadas. **Nulo**: lados barajados.

## Criterio

El umbral de empate con coste `c` sobre el riesgo es `(1+c)/3`. Con un stop de
9 pips, `c` = 15,9 % y el umbral es **38,6 %**.

1. acierto > umbral, con IC95 sin tocarlo, **y**
2. neta > 0 con IC95 sin tocar el cero, **y**
3. mejor que la versión sin cambio de estructura (33,4 %, neta −0,312).

Y para su propio plan hace falta además **neta ≥ +0,05 R**.

## Predicción

- El cambio de estructura **reducirá mucho el número de operaciones** (de
  ~30.000 a unos pocos miles) y **subirá algo el acierto**, pero no 7 puntos.
- **Acierto entre 33 y 38 %.** Por debajo del umbral.
- **La entrada al mitigar dará un stop más pequeño** que la entrada a mercado,
  y por tanto **peor neta**, no mejor.
- **Neta entre −0,10 y −0,30** en las seis celdas.

Seis predicciones mías llevan errores. Ésta también puede fallar.
