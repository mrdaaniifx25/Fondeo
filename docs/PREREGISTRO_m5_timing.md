# Pre-registro · ¿afina M5/M15 la entrada de AMD+FVG?

Escrito y subido ANTES de medir nada. Fecha 2026-09-19.

## De dónde sale la pregunta

La regla base (`docs/RESULTADOS_amd_fvg.md`) detecta todo en H1 y entra al
cierre de la vela de H1 que deja el hueco. La pregunta del usuario:

> "si la entrada se da en H1, al ser multiframe quiere decir que en M5 o M15
> también tiene que existir algo que me haga hacer la entrada en el momento
> oportuno"

Es una pregunta distinta de la que ya está medida. Lo medido hasta ahora es
**el patrón entero calculado en M15** (negativo en los tres instrumentos).
Lo que NO está medido es **el patrón en H1 con la entrada afinada en M5/M15**.

## Las dos cosas que puede hacer una temporalidad menor

Son mecánicamente distintas y hay que separarlas, porque predicen lo contrario:

1. **Mejor precio** (entrar más cerca del stop). Acorta el riesgo en pips y
   alarga el R:R. Si el mercado pone precio justo a la geometría, la
   probabilidad baja en la misma proporción: la bruta no se mueve y **la neta
   empeora**, porque el coste fijo (1,43 pips en EURUSD) pesa más sobre un
   riesgo más pequeño.
2. **Filtro** (tomar sólo las de H1 que además cumplen algo en M5). No toca la
   geometría: mismo precio, mismo stop, mismo objetivo, menos operaciones. Es
   lo único que puede subir el acierto por encima de su precio justo.

## Variantes que se van a medir

Todas sobre EURUSD, detección idéntica a `bt/amd_fvg.py` (LIMITE 0,90,
n=8 velas de H1, ESPM 20, ESPD 20, ESPF 5).

| # | Variante | Entrada | Stop | Objetivo |
|---|---|---|---|---|
| A | Base H1 | cierre de la vela H1 con FVG | extremo de la finta | borde opuesto de la caja |
| B | Retiming M5 | cierre de la 1ª vela M5 con FVG tras cerrar la finta (máx. 60 M5) | último mínimo/máximo de M5 desde la finta | el mismo |
| C | Retiming M15 | igual con M15 (máx. 20 velas) | último mínimo/máximo de M15 | el mismo |
| D | Filtro M5 | **igual que A** (precio y stop de A), pero sólo si existía el FVG de M5 de B | el de A | el mismo |

D es la clave: comparte geometría con A, así que cualquier diferencia entre D y
A es información, no aritmética de barreras.

## Cómo se mide

- Resolución en **M1** para todas, para que ninguna variante se beneficie de
  mirar el precio con más o menos lupa que otra. Se vuelve a dar A también con
  resolución H1 para poder enlazar con el 76,5 % ya publicado.
- Barreras **las dos por toque**, la primera que se toca manda.
- Si stop y objetivo se tocan dentro del mismo minuto, cuenta **pérdida**.
- Horizonte 20 horas desde la entrada (= las 20 velas de H1 de la base).
- Entrada al **cierre** de su vela: la resolución empieza en el minuto
  siguiente. Nada de la vela de entrada entra en la decisión.
- Coste 1,43 pips (0,85 de horquilla + 5 €/lote de comisión).

## Criterio, declarado antes de ver nada

Para decir que M5/M15 aportan algo hace falta, sobre la misma muestra:

1. **B o C** con neta media > la de A y el intervalo de confianza del 95 % de
   la diferencia sin tocar el cero, **o**
2. **D** con exceso sobre el azar mayor que el de A y IC95 de la diferencia sin
   tocar el cero.

Si no se cumple ninguno, la respuesta es que la temporalidad menor **no añade**
y la entrada se queda en H1, al cierre, sin mirar nada más.

## Predicción

Dejada por escrito para poder equivocarme en público:

- **B y C peores en neta que A**, por el coste sobre un riesgo más corto.
- **B y C con bruta parecida a A**, porque la geometría se paga sola.
- **D indistinguible de A**, porque el FVG de M5 casi siempre existe dentro de
  una vela de H1 que ya tiene FVG, así que filtra poco.
