# Pre-registro · barrido en H4/H1 con cambio de estructura en M15/M5

Escrito **antes** de medir. Idea suya del 18 de septiembre de 2026, literal:

> buscar un nivel importante de liquidez en M15 que sería el rango de la vela de
> H4, o lo mismo en M5 pero rango de H1 [...] y buscamos un cambio de estructura
> mediante un OB, y en ese momento que en una temporalidad mayor se esté
> produciendo un liquidity sweep, y ya hacer la entrada en el cierre de la vela
> que ha roto la estructura, SL por debajo del último mínimo y el TP en el 1:2.

## En qué se diferencia de todo lo anterior

| pieza | lo ya medido | **esto** |
|---|---|---|
| nivel | extremo de la sesión previa | **rango de la vela de H4/H1 anterior** |
| gatillo | envolvente, o rotura de cuerpo | **cambio de estructura con cierre** |
| stop | extremo del barrido | **último mínimo/máximo de estructura** |
| condición | — | **simultaneidad con el barrido de arriba** |

Las tres primeras no se han medido nunca juntas, y la del stop importa: el último
mínimo suele quedar más lejos que el extremo del barrido, y el modelo ya dejó
dicho que la ventaja bruta vive en la banda de 10 a 20 pips de riesgo.

## Definiciones, que son mías y por eso van escritas

**1 · Barrido en curso.** La vela de H4 (o H1) **en curso** ha superado el extremo
de la anterior ya cerrada, y el precio ha vuelto dentro de ese rango. Es
"produciéndose", no cerrado: se sabe en tiempo real y no mira al futuro.

**2 · Cambio de estructura.** En M15 (o M5), tras el barrido: para una venta, el
precio hace un máximo y un mínimo de estructura, y después **cierra por debajo de
ese mínimo**. Para una compra, al revés.

Los pivotes se detectan con fractales de 2 velas a cada lado y **solo se usan una
vez confirmados**, que es donde este proyecto ya se pilló una fuga en agosto.

**3 · El order block.** Él lo nombra, pero la entrada que describe es al cierre de
la vela que rompe la estructura, no en el retroceso al OB. Así que el OB **no
entra en el código**: sería un grado de libertad sin efecto sobre la entrada. Se
dice para que conste, no para esconderlo.

**4 · Stop.** Venta: el máximo de estructura anterior a la rotura. Compra: el
mínimo. Buffer cero.

**5 · Objetivo.** 2R exactos.

**6 · Caducidad.** El cambio de estructura tiene que llegar dentro de la misma
vela de H4 (o H1) en la que se está produciendo el barrido. Si esa vela cierra,
la señal muere.

**7 · Una operación por barrido.**

**8 · Resolución en M1.** Empate dentro del mismo minuto cuenta como pérdida.

## Coste

1,43 pips ida y vuelta.

## Celda principal y criterio

**Celda principal: H4 + M15, EURUSD, 2020-2026.** Un solo contraste.

**Funciona si el IC95 de la R neta queda entero por encima de cero.**

## Lo que se informa pase lo que pase

H4+M15 y H1+M5; por año; por lado; el reparto del riesgo en pips; las operaciones
al día; y el desglose bruta/neta, porque es lo que distingue una ventaja real de
un simple stop más ancho.

## Lo que invalidaría la prueba

Menos de 200 operaciones en seis años: sería una regla tan rara que no se puede
concluir nada, ni a favor ni en contra.

## El listón, dicho antes de medir

Lo mejor que ha dado el proyecto es bruta **+0,048** (el modelo, con 200.000
filas). Cualquier cosa por debajo de eso no es un hallazgo nuevo. Para que la neta
cruce cero con un riesgo de 15 pips hace falta bruta por encima de **+0,095**.
