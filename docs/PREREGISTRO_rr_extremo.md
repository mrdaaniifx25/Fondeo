# Pre-registro · R:R extremo sobre stops diminutos

Escrito y subido ANTES de medir. 22/09/2026.

## De dónde sale

Vídeo que manda el usuario (Orion Funded, «programa Focus»). El operador dice,
literal: *«yo como mínimo mínimo siempre busco un 12»*, con stops de **3-4 pips**.

Eso ataca justo el término que mi propia fórmula dice que manda:

```
  neta = ventaja × (1 + R:R) − coste/riesgo
         ─────────────────────
         el R:R MULTIPLICA la ventaja
```

Con un stop de 4 pips y 1,43 de coste:

```
   R:R      azar    umbral    ventaja necesaria
   2:1     33,3 %   45,2 %        +11,9 puntos
   8:1     11,1 %   15,1 %         +4,0
  12:1      7,7 %   10,4 %         +2,7
  20:1      4,8 %    6,5 %         +1,7
  30:1      3,2 %    4,4 %         +1,2
```

**Y el proyecto lleva midiendo excesos de +2,7 a +4,9 puntos** en
`RESULTADOS_stop_minimo.md`, `RESULTADOS_barrido_rr.md` y
`RESULTADOS_techo_filtro.md`. A 1:2 ese exceso no llega al umbral. **A 1:12
llegaría.**

`bt/barrido_rr.py` barrió el R:R **sólo hasta 8,0**, y sobre el CRT en H4 con
stops anchos. **Nunca se ha probado esta geometría: stop diminuto, objetivo
lejísimos.**

## Qué se mide

Base: las entradas ya verificadas de `bt/benjamin_regla.py` — EURUSD, M2,
niveles de H1, sus horas — **~30.000 operaciones** con stop mediano de 6,4 pips,
contrastadas contra la pantalla real de un operador a medio pip
(`VERIFICACION_benjamin_real.md`). Se reutilizan tal cual: **sólo cambia el
objetivo**.

| eje | valores |
|---|---|
| R:R | **2 · 3 · 5 · 8 · 12 · 20 · 30** |
| horizonte | **1 día · 5 días · 20 días** |

**PRINCIPAL, declarado ahora: R:R 12, horizonte 5 días.** Es lo que él dice que
hace, y a esa distancia (≈ 77 pips desde un stop de 6,4) cinco días es el plazo
razonable. Las otras 20 celdas se publican y no cuentan como hallazgo.

## El sesgo que puede fabricar esto, y cómo se mata

Al subir el R:R, **muchas operaciones no se resuelven** dentro del horizonte. Ya
me equivoqué una vez por esto (`RESULTADOS_stop.md`, retractado). Por tanto:

1. Se publica el **% sin resolver** en cada celda.
2. Las no resueltas se cierran **a mercado** y se apunta el R que salga, nunca
   como pérdida ni como acierto.
3. Se corre el **placebo de lados barajados** en todas las celdas. Ése tiene que
   salir exactamente en el precio justo. Si el placebo también sube al subir el
   R:R, lo que se mide es el horizonte, no la señal.

## Las dos métricas, porque en puntos engañan

A R:R alto, un mismo tirón direccional vale **menos puntos** de acierto aunque
sea igual de real. Así que se publican las dos:

- **exceso en puntos** = acierto − azar
- **razón** = acierto ÷ azar. Si hay ventaja direccional de verdad, ésta se
  mantiene por encima de 1 al subir el R:R; si es un artefacto de puntos, no.

## El sesgo de selección

21 celdas. El mejor de 21 sale **1,90 errores estándar** por encima de la verdad.
Por eso el principal está fijado antes.

## Criterio

1. El principal (12:1, 5 días) con **neta > 0** y el IC95 sin tocar el cero, **y**
2. el placebo barajado en esa celda **en el precio justo** (razón ≈ 1,00), **y**
3. la razón acierto/azar **por encima de 1** de forma coherente en la fila del
   R:R, no sólo en una celda suelta.

## Predicción

- **El placebo saldrá en el precio justo a todos los R:R.** Si no, la prueba no
  vale y se dirá.
- **La razón acierto/azar bajará al subir el R:R.** Creo que el exceso de +3
  puntos que aparece a 1:2 es un tirón corto —el precio se aleja un poco del
  nivel barrido— y que ese tirón **no llega a 77 pips**. A 12:1 espero razón
  entre 0,90 y 1,05.
- Por tanto **la neta seguirá negativa** a todos los R:R, y el principal **no
  cumplirá el criterio**.
- El % sin resolver a 12:1 y 5 días será **alto, del 20 al 40 %**.
- Si me equivoco y la razón se mantiene por encima de 1,1 a 12:1, esto sería el
  primer patrón de gráfico intradía con ventaja real del proyecto, y habría que
  replicarlo en oro y DAX antes de creérselo.

Van catorce predicciones con errores. Ésta también puede fallar.
