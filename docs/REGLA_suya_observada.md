# Su regla, tal y como la describe él · en construcción

Documento vivo. Se va llenando con lo que él va contando sobre sus propias
capturas, **antes** de codificar nada. La lista de hipótesis que salga de aquí
es suya, no mía, y ésa es la diferencia con los dos meses anteriores.

Fecha de arranque: 10 de septiembre de 2026.

## La secuencia, en sus palabras

> «rotura del high de Asia, luego hace un retroceso y cuando la vela cierra con
> cuerpo por debajo del último mínimo ejecuto entrada»

```
1. el precio rompe el máximo de Asia            -> se lleva la liquidez
2. sigue y hace un máximo
3. retrocede
4. una vela CIERRA CON CUERPO por debajo del
   último mínimo relevante                      -> rotura de estructura
5. entrada en ese cierre, vendiendo
```

## Los tres ejemplos que ha enseñado

Todos EURUSD M1, ventana de Londres, y **los tres son ventas**.

| # | día | máximo previo | último mínimo = entrada | stop | objetivo | riesgo |
|---|---|---|---|---|---|---|
| 1 | 10 sep | 1,16443 (09:35) | **1,16387** (09:50) | 1,16415 | 1,16330 | 2,8 p |
| 2 | 10 sep | 1,16525 (09:45) | **1,16375** (10:05) | 1,16418 | 1,16310 | 4,3 p |
| 3 | 08 sep | 1,16360 (08:05) | **1,16303** (08:15) | 1,16340 | 1,16229 | 3,7 p |

## Lo que se deduce, pendiente de que él lo confirme

**El «último mínimo» es un mínimo de estructura, no el de la vela anterior.**
Es el suelo desde el que arrancó el último tramo al alza. En el ejemplo 2 son
las 09:30 (1,16375) y el tramo llega hasta 1,16525 quince minutos después.
Descartadas las otras dos lecturas que se le ofrecieron (mínimo de la última M5,
mínimo de la última M1).

**El stop parece ir encima del último máximo menor anterior a la entrada**, no
encima del máximo grande. Encaja en los tres: 1,16415 con máximo grande en
1,16443; 1,16418 con máximo grande en 1,16525; 1,16340 con máximo grande en
1,16360. Sin confirmar.

**La rotura del máximo de Asia puede ocurrir antes de las 08:00.** En el ejemplo
3 el precio ya está por encima de la caja de Asia cuando abre Londres, y la
entrada llega a las 08:15. Así que el barrido no tiene que caer dentro de la
ventana operativa; la entrada sí.

## Lo que hace falta antes de medir

1. **Definir «último mínimo» con un número.** Propuesta: mínimo más bajo que las
   N velas anteriores y las N posteriores. En sus capturas N parece estar entre
   5 y 10 minutos. Se probará un rango y se declarará una celda principal.
2. **Causalidad.** Un mínimo así no queda confirmado hasta N velas después de
   ocurrir. Sólo se usarán los confirmados **antes** de la vela de entrada. Este
   repositorio ya se ha tropezado dos veces con miradas al futuro
   (`CORRECCION_mirada_al_futuro.md`) y no habrá una tercera.
3. **Falta un ejemplo de compra.** Los tres son ventas tras barrer por arriba.
   Sin un caso simétrico no se puede saber si la regla es simétrica o si lo que
   describe es sólo el lado corto.

## Lo que ya se puede anticipar

Los riesgos de los tres ejemplos son **2,8 · 4,3 · 3,7 pips**. Con el coste
medido de 1,43 pips, el peaje es del 51 %, 33 % y 39 % del riesgo. Su regla
real produce stops pequeños, igual que la anterior, así que la aritmética del
coste va a volver a aparecer. Se reportarán por separado la ventaja bruta del
patrón y lo que se lleva el coste.

## Diferencia con lo medido hasta ahora

`bt/su_regla_instrumentos.py` mide otra cosa: el cuerpo de la última M5 cerrada
roto por el cierre de una M1, que dispara 49,5 veces al día. Lo que él describe
aquí es un barrido de liquidez más una rotura de estructura, y aparece muchísimo
menos.

**Los 31,3 % de acierto y las 85.453 señales de todos los documentos anteriores
miden esa otra regla, no ésta.**
