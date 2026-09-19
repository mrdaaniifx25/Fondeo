# Preregistro · sacarle la regla de entrada a sus 150 operaciones

Escrito **antes** de mirar ninguna de las medidas. Se comprueba primero que la
reconstrucción es fiable (`bt/contexto_150.py`: los 150 precios de entrada caen
dentro del rango real de su vela de M1 — 150 de 150) y luego se declara esto.

## El problema que resuelve

El componente que lleva parado desde el principio es «la regla escrita»: 6 de 20.
El plan era que él etiquetara por qué entraba; en el bloque 4 lo usó 0 veces de
64, y en parte por culpa de dónde estaba el botón. Pedirle otra vez que se
acuerde es el peor camino disponible.

Pero sus 150 decisiones ya están registradas con hora, dirección y precio, y los
93 días están enteros en M1. **Se puede medir qué se veía en el gráfico cuando
entró, en vez de preguntárselo.**

## Diseño

- **Casos**: sus 150 entradas. Cada una se ancla a la última vela de M5 cerrada
  en el minuto de la entrada.
- **Controles**: todas las demás velas de M5 cerradas entre 08:00 y 11:30 de esos
  mismos 114 días de sesión (~4.800). Mismos días, misma ventana: lo único que
  cambia es que en unas entró y en otras no.
- Todo se calcula **solo con datos anteriores al cierre de esa vela**. Nada de
  mirar al futuro, con el mismo cuidado que en `CORRECCION_mirada_al_futuro.md`.

## Las ocho variables, declaradas antes de medirlas

Salen de lo que él ha dicho que hace, no de rebuscar:

1. **Distancia al nivel de Asia más cercano**, en pips (alto y bajo de 00:00 a
   08:00, que es lo que la página le pinta).
2. **Cuerpo fuera o mecha**: si la vela cerró el cuerpo pasado el nivel, o solo lo
   pinchó con la mecha y cerró dentro. Es la distinción que él marcó a mano en las
   capturas del lunes.
3. **Número de toque** de ese nivel en lo que va de sesión: primero, segundo,
   tercero.
4. **Dirección de H4**: signo del cuerpo de la última vela de H4 cerrada.
5. **Dirección de M15**: signo de cierre menos cierre de cuatro velas antes.
6. **Minutos desde las 08:00**.
7. **Rango de la vela** en pips, que es de donde sale su stop.
8. **Sentido del día hasta ese momento**: cierre menos apertura de las 08:00.

Ocho contrastes, **Bonferroni**: el umbral por variable es p < 0,00625.

Aparte, y solo sobre sus 150, se mira **hacia dónde** entró: a favor o en contra
del nivel, de H4, de M15 y del día.

## Predicción firmada

1. La distancia al nivel de Asia será **la que más separe**, y con mucho: su
   mediana quedará por debajo de 5 pips contra 15-20 de los controles.
2. Entrará **antes** de lo que da el azar: mediana en torno a los 35 minutos
   desde las 08:00 contra ~105 de los controles.
3. **Cuerpo fuera saldrá más frecuente que en los controles, pero mucho menos
   limpio de lo que él cree**: en el bloque 1 desvanecía la rotura el 57 % de las
   veces. Espero una diferencia real pero por debajo de los 25 puntos.
4. H4 y M15 **no separarán** por encima del umbral de Bonferroni. El filtro de H4
   ya se midió dos veces y no hacía nada (30,8 % a favor, 30,8 % en contra).
5. El primer toque dominará sobre el segundo y el tercero.
6. **Y la importante: una regla mecánica construida con lo que salga de aquí NO
   reproducirá su 66 %.** Predigo que quedará por debajo del 45 % en datos nuevos,
   que es lo que ha pasado con las noventa celdas anteriores del proyecto.

La 6 es la que de verdad se pone a prueba. Si me equivoco, es el hallazgo del
proyecto entero: querría decir que lo que hace es codificable y que llevamos
buscándolo en el sitio equivocado.

## Qué contaría como hallazgo

La parte descriptiva es **exploratoria** y se reporta como tal, con Bonferroni.

Lo confirmatorio es uno solo: la regla que salga se congela y se corre en los
**seis años de EURUSD fuera de muestra**, sin tocar nada. Hace falta **z > +1,96
en R neta** con el coste real de 1,43 pips. Nada por debajo cuenta, y si no llega
se escribe que no llegó.

## Ficheros

```
bt/contexto_150.py        comprueba la reconstruccion (hecho: 150 de 150)
bt/ingenieria_inversa.py  casos contra controles
data/operaciones_150.csv  sus 150 operaciones con dia real
```
