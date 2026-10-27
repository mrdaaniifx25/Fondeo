# Pre-registro · el AMD, medido en todo el histórico

Escrito antes de medir. Petición suya: comprobar el indicador con todos los datos
y sacar la mejor configuración de las tres fases.

## La pregunta bien planteada

"¿Cuál es la mejor configuración?" invita a buscar hasta que algo salga bien.
Así que se parte en dos preguntas que sí se pueden contestar:

**1 · ¿Importa la A?** Se arma un rango en **todas** las velas, estrecho o no, y
se anota su estrechez. Luego se mira si los rangos apretados completan el AMD más
que los anchos. Si no, la fase de acumulación es un adorno y hay que decirlo.

**2 · ¿La D supera al azar?** Tras la manipulación, el precio está dentro del
rango a una distancia `a` del extremo barrido y `b` del contrario. Para un paseo
sin deriva, la probabilidad de tocar antes el contrario es `a/(a+b)`. Ésa es la
tasa que hay que batir. **Completar el AMD el 40 % de las veces no significa nada
si el azar da el 40 %.**

## Definiciones

    A   ventana de n velas. Estrechez = recorrido / (ATR x raiz(n)).
        1,00 es un rango corriente.
    M   una vela sale del rango y CIERRA de vuelta dentro, dentro de espM velas.
    D   un cierre mas alla del extremo CONTRARIO, dentro de espD velas.

Todo con velas cerradas. Nada mira al futuro.

## La rejilla, declarada ahora

    temporalidad   M15, H1, H4
    n              8, 12, 16, 24, 32
    espM           20        espD   20

La estrechez **no se rejillea**: se mide continua y se informa por deciles. Así no
hay ningún umbral que elegir a posteriori.

## Lo que se informa

Por cada celda: número de secuencias, tasa A→M, tasa M→D, **tasa M→D esperada por
azar**, y la diferencia. Más la tabla de completar por decil de estrechez.

## El criterio

**El AMD aporta información si la tasa M→D supera a la del azar con el IC95 de la
diferencia entero por encima de cero**, y si esa ventaja crece cuando el rango es
más estrecho.

Si la tasa observada iguala a la del azar, el AMD describe lo que el precio hace,
pero no predice nada, y se dirá exactamente así.

## Y una nota sobre lo que ya sabemos

La pata M sola está medida: 16.219 casos, ventaja bruta cero. Lo nuevo aquí es
exigir la A delante. Si tampoco aporta, el indicador vale como descripción y no
como señal, y así irá escrito en su cabecera.
