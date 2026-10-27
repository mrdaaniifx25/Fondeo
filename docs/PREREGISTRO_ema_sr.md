# Pre-registro · soportes/resistencias H1 + EMA 50 en M5 y M1

Escrito y subido ANTES de medir. 19/09/2026. Regla propuesta por el usuario:

> «soportes y resistencias en H1 y una EMA de 50 en M5 y cuando haya un
> rompimiento de la media móvil exponencial tanto en M5 como en M1 poner el
> stop en el alto y el TP en el bajo»

## Cómo se mecaniza

Lo de arriba no es ejecutable tal cual, así que se fija todo aquí, por
escrito, antes de mirar ningún número.

**Niveles de H1.** Pivotes de H1 con 5 velas a cada lado (un máximo es pivote
si las 5 anteriores y las 5 siguientes son más bajas). **Sólo se usa 5 velas
después de formarse**, que es cuando se sabe que existe. Se mantienen vivos los
20 últimos.

**Cerca de un nivel.** `|precio − nivel| <= 0,25 × ATR(H1,14)`.

**Ruptura de la EMA 50 en M5.** El cierre cruza de un lado al otro:
`cierre[t] > ema[t]` y `cierre[t−1] <= ema[t−1]` (alcista), y al revés.

**Confirmación en M1.** En el instante en que cierra esa vela de M5, el cierre
de M1 está del mismo lado de su propia EMA 50.

**Lado.** El de la ruptura. Rompe abajo → venta. Rompe arriba → compra.

**Entrada.** Al **cierre** de la vela de M5 que confirma. La resolución empieza
en el minuto siguiente: ni un dato del futuro en la decisión.

**Stop y objetivo.** Sobre las últimas N velas de M5:
venta → stop en el máximo, objetivo en el mínimo. Compra → al revés.

**El objetivo tiene que estar POR DELANTE** del precio de entrada. Si ya está
rebasado, no hay operación. (El error de `docs/CORRECCION_objetivo_rebasado.md`
no se repite.)

## Las 8 celdas, declaradas ahora

| eje | opciones |
|---|---|
| nivel de H1 | exigido · no exigido |
| N velas de M5 para stop/objetivo | 10 · 20 |
| confirmación en M1 | exigida · no exigida |

Se publican **las ocho**. Con 8 celdas y un 5 %, se espera media celda
«significativa» sólo por azar; eso se tiene en cuenta al leerlas.

## Cómo se mide

- Resolución en **M1**, las dos barreras **por toque**, la primera manda.
- Empate en el mismo minuto → **pérdida**.
- Horizonte 20 horas. Agotarlo → **pérdida**.
- Coste 1,43 pips (0,85 horquilla + 5 €/lote).
- `azar = riesgo / (riesgo + recorrido)` = la probabilidad que le toca por
  geometría. Lo que importa es el **exceso** sobre eso, no el acierto.
- Además se mide la **deriva** (movimiento medio a favor a 1 h, sin barreras),
  que tiene más potencia para ver efectos pequeños.

**Nulos**, sobre la celda principal: lados barajados · instantes al azar ·
la señal al revés.

## Criterio, declarado antes de ver nada

Para decir que la regla aporta hace falta, en la misma celda:

1. exceso sobre el azar > 0 con el IC95 sin tocar el cero, **y**
2. neta media > 0 con el IC95 sin tocar el cero, **y**
3. los tres nulos en cero.

## Predicción

- Exceso entre −2 y +2 puntos en las ocho celdas. Ninguna cumple el criterio.
- R:R mediano **por debajo de 1** y acierto por encima del 50 %, por la forma
  de la regla (stop en el alto, objetivo en el bajo, entrando abajo).
- Neta negativa en todas, por el coste.
- La deriva a 1 h, entre −1 y +1 pips.
