# Pre-registro · la base de Benjamín, con las tres vueltas

Escrito y subido ANTES de medir. 21/09/2026.

## La pista

| | ventaja BRUTA | de dónde |
|---|---|---|
| su regla, objetivo **1:2 fijo** | **+0,00** | `RESULTADOS_benjamin_regla.md` |
| CRT, objetivo en el **nivel opuesto** | **+0,087 a +0,125** | `RESULTADOS_crt_temporalidad.md` |

Es **el mismo setup**: barrer un nivel y girar. Cambia el objetivo. Y uno tiene
ventaja bruta medida y el otro no.

## Qué se conserva de él y qué se cambia

**Se conserva** — es su aportación y es lo que se está probando:

- **Sus niveles**: máximo/mínimo de la semana anterior, del día anterior, de H4
  y de H1. Es una jerarquía más rica que la del CRT desnudo (que usa sólo el
  rango de la vela anterior).
- **Sus horarios**: Londres 09:00-11:00 y NY 14:00-16:30.
- **Su disparo**: barrido del nivel y giro.

**Se cambia** — las tres vueltas, todas en la misma dirección:

1. **Temporalidad de entrada arriba**: M15 y H1, en vez de M1-M5.
2. **Stop por ATR** en vez de en el extremo del barrido: 1,0 y 1,5 ATR de la
   temporalidad de entrada. Deja de depender de lo apretada que sea la vela.
3. **Objetivo en el nivel opuesto** en vez de 1:2 fijo.

## Las 12 celdas

| eje | opciones |
|---|---|
| entrada | **M15** · **H1** |
| stop | extremo del barrido · **1,0 ATR** · **1,5 ATR** |
| objetivo | 1:2 fijo · **nivel opuesto** |

Todas publicadas.

## La pregunta que de verdad se contesta

Además del resultado, se compara contra el CRT desnudo de la misma
temporalidad. Si sus niveles y sus horarios **no mejoran** al CRT simple,
entonces su aportación es cero y lo que sirve es el CRT, no él.

## Medición

Resolución en M1, barreras por toque, empate = pérdida, horizonte 48 h,
objetivo por delante, coste 1,43 pips. Se publica el **exceso sobre el precio
justo** `riesgo/(riesgo+recorrido)`, que ahora ya no es 33,3 % porque el R:R
varía.

**Nulos**: lados barajados e instantes al azar sobre la mejor celda.

## Criterio

1. exceso > 0 con IC95 sin tocar el cero, **y**
2. **neta ≥ +0,05 R** (el umbral que necesita su propio plan), **y**
3. mejor que el CRT desnudo del mismo marco.

## Predicción

- **Bruta positiva** en las celdas con objetivo en el nivel opuesto, en torno a
  **+0,05 a +0,12**, porque ahí es donde vive la ventaja del CRT.
- **Bruta en cero** en las celdas de 1:2 fijo, replicando lo ya medido.
- **El stop por ATR mejorará la neta** frente al extremo del barrido, por ser
  más ancho y estable.
- **Neta entre −0,05 y +0,06** en las mejores celdas: **rozando el umbral, sin
  superarlo con claridad.**
- **Sus niveles y horarios no mejorarán al CRT desnudo.** Espero diferencia
  indistinguible de cero.

Van siete predicciones con errores. Ésta también puede fallar.
