# Verificación de agosto · con las horas de entrada exactas

Fecha: 2026-08-28. Datos: `data/eurusd_m1_2026_08.parquet` (2 al 21 de agosto,
lo que HistData ha publicado). Fichas: `data/agosto_operaciones.csv`, con
precios leídos de su herramienta de posición y **hora de entrada facilitada por
él**.

## Lo primero: mi método estaba mal y ahora coincide en todo

Sin sus horas yo resolvía cada operación desde el **primer momento en que el
precio tocaba su entrada a partir de las 08:00**. Con stops de tres pips ese
precio se toca muchas veces en una mañana, y el resultado se movía de −0,14 a
+1,11 R según la hora que supusiera.

Con la hora real:

> **Mi resolución coincide con su herramienta en las 14 de 14 que se resuelven.**
> Cero discrepancias.

El desvío de precio entre mi feed (HistData) y el suyo (OANDA) en el minuto de
entrada es de **0,7 pips de mediana, 3,4 como máximo**. No era eso: era mi
suposición de la hora.

**Su registro es exacto.** Las cinco discrepancias que reporté antes eran mías.

## Detalle de las 16 con datos

| id | fecha | hora | dir | riesgo | R:R | resultado |
|---|---|---|---|---|---|---|
| T17 | 3 ago | 08:40 | venta | 2,5 p | 2,00 | SL |
| T18 | 4 ago | 09:30 | venta | 3,4 p | 2,00 | **TP** |
| T20 | 5 ago | 09:15 | venta | 3,8 p | 2,00 | SL |
| T19 | 5 ago | 11:10 | compra | 3,4 p | 2,03 | **TP** |
| T21 | 6 ago | 09:15 | venta | 5,2 p | 2,00 | **TP a las 16:50** |
| T22 | 7 ago | 11:20 | compra | 3,8 p | 2,32 | **TP a las 14:12** |
| T24 | 10 ago | 09:55 | venta | 4,7 p | 2,00 | SL |
| T23 | 10 ago | 10:50 | venta | 3,4 p | 2,00 | **TP** |
| T25 | 11 ago | 08:25 | venta | 2,4 p | 2,00 | SL |
| T01 | 14 ago | 09:40 | compra | 3,8 p | 2,00 | **TP** |
| T02 | 17 ago | 08:30 | compra | 9,7 p | 2,01 | **TP** |
| T04 | 18 ago | 08:20 | compra | 2,8 p | 2,04 | SL |
| T03 | 18 ago | 10:30 | compra | 3,6 p | 2,00 | **TP** |
| T05 | 19 ago | 09:25 | compra | 6,5 p | 2,00 | **TP** |
| T07 | 20 ago | 09:05 | venta | 6,8 p | 1,87 | SL |
| T06 | 20 ago | 09:55 | compra | 7,5 p | 2,00 | **TP** |

**Dos detalles de especificación que salen de aquí:**

- **T21 y T22 llegaron al objetivo DESPUÉS de las 14:00** (16:50 y 14:12). Él no
  cierra al final de Londres. Todos mis backtests sí lo hacían. Es otra
  diferencia con lo que yo medía.
- **T14 tiene R:R 4,29**, no 2 — riesgo 1,4 p y objetivo 6,0 p con los números
  que él corrige. Las otras 24 van de 1,87 a 2,32, mediana 2,00. Queda anotada
  como anomalía, no se corrige por mi cuenta.

## Los números

| | n | TP | SL | acierto |
|---|---|---|---|---|
| **3 al 20 de agosto** — verificado al minuto por mí | 15 | 9 | 6 | **60,0 %** |
| 24 al 28 de agosto — sin datos publicados | 9 | 9 | 0 | **100 %** |
| **total del mes** | 24 | 18 | 6 | **75,0 %** |

Con un 1:2, 18 aciertos de 24 sale por azar **una vez de cada 27.794**.

Agrupando por día, que es la unidad independiente —él toma de una a tres al día
y la segunda suele ser reacción a la primera—:

```
16 días · R neta media +0,979 ± 0,298 · z +3,29 · 14 de 16 días en positivo
en euros, con 150 € de riesgo: +3.590 € en el mes
```

Sobre lo que **sí** he podido verificar (3 al 20), a nivel de día: bruta +0,803
(z +2,14), neta +0,488 (z +1,21), 8 de 10 días en positivo.

## Lo que queda por resolver

1. **La semana del 24 al 28 es 9 de 9 y no la puedo comprobar.** Y hace la mitad
   del trabajo: sin ella el mes es 60 % y la neta no llega a significativa
   (z +1,21); con ella es 75 % y z +3,29. Habiendo coincidido 14 de 14 en todo
   lo demás, no hay motivo para dudar de su registro — pero verificado no está,
   y HistData publica el mes completo en unos días.
2. **Un mes es un régimen.** EURUSD subió +129 pips casi en línea recta del 3 al
   21. Sus compras hicieron 10 de 12; sus ventas, 8 de 12. Con agosto solo no se
   separa «compra bien» de «el mes subía».
3. **La regla de dirección sigue sin estar escrita.** En el mismo borde de Asia
   unas veces sigue la ruptura y otras la desvanece, y ahora sabemos que parte
   de esas segundas son **reentradas** tras una vuelta del precio, no señales
   independientes. Hasta que eso esté en una frase no se puede probar en
   histórico ni repetir en un mal día.

## Ficheros

```
data/agosto_operaciones.csv    las 25 con precios y hora de entrada
data/agosto_verificacion.csv   resolución al minuto de cada una
```
