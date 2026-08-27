# BC_09 · Pre-registro · la temporalidad de ejecución

**Escrito antes de correr nada.** Fecha: 2026-08-27.

## Por qué

`BC_02` §5 fijó la ejecución en **1H** y lo declaró «primera versión», anotando
15M como variante pendiente. La variante nunca se hizo. Mientras tanto el
material dice, literalmente:

> «Primera ejecución: entramos en el **primer rango de 15M**»
> «PO3 de 12H → **creación de rango en 15M**»
> «entrada al **cierre de una vela de 10 minutos**»

Sus dos operaciones mejor documentadas entran en 15M y en 10M. **Hemos medido la
ejecución más gruesa de las cinco que usan, y no es la que usan.**

## Qué se cambia

Una sola cosa: la temporalidad donde se busca el rango de ejecución. El contexto
sigue siendo 1D/12H/4H, la lectura sigue siendo B, el objetivo sigue siendo el
más cercano de los alineados, el stop sigue yendo al extremo de la vela de
ejecución más un tick, el R:R mínimo sigue siendo 3.

```
ejecución  ∈  { 1H, 15M, 10M, 5M }
```

Cuatro celdas por instrumento, cinco instrumentos, 2020-2023.

## Lo que predigo, y por qué

El coste es un número fijo de pips. El riesgo es el tamaño del stop. **Bajar de
temporalidad hace el stop más pequeño, y por tanto el coste más grande en
proporción.** En 1H el riesgo mediano es 9,1 pips y el coste se lleva el 13 %. En
15M el stop debería rondar los 4 pips y el coste se llevaría un 30 %.

1. **El R:R bruto sube** al bajar de temporalidad, monótonamente. Mismo objetivo,
   stop más pequeño.
2. **La tasa de aciertos baja**, aproximadamente como 1/(1+R:R).
3. **El coste en unidades de R sube** al bajar, monótonamente.
4. **Por tanto el neto empeora al bajar.** Predigo 15M peor que 1H, y 5M peor
   todavía o casi sin operaciones, porque la guarda de ejecutabilidad —stop ≥ 3×
   el coste, o sea 3,6 pips— se lleva la mayoría.
5. **La R bruta por operación se queda parecida**, entre +0,05 y +0,20, igual que
   se quedó parecida entre H1 y D1 en `RESULTADOS_crt_temporalidad.md`.

## Qué resultado me haría cambiar de opinión sobre el planteamiento entero

**Que el neto MEJORE al bajar de temporalidad.** Eso significaría que la
estructura de 15M o 5M lleva información de verdad —que entrar fino no es solo
apretar el stop, es acertar más— y que llevamos seis semanas midiendo la versión
equivocada del método.

Umbral: para declarar que una celda gana hace falta que su intervalo de confianza
del 95 % excluya el cero **por arriba**, con el error estándar del bootstrap por
bloques (`BC_08` §3), no el ingenuo. Con veinte celdas el umbral de Bonferroni es
|z| > 3,02, y sobre ese hay que aplicar el factor 1,1 de `BC_08`: **|z| > 3,3**.

## Qué NO resuelve esta prueba

La entrada por **order block** en 15M o 1H, que es otro esquema distinto y
aparece en el material del 31 de mayo. Eso queda para después y se pre-registra
aparte.
