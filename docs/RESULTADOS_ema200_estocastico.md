# Resultado · EMA 200/20 y reversión con estocástico, sin Fibonacci

Ideas del usuario después de ver que el Fibonacci era la pieza dañina
(`RESULTADOS_ema_fibo_estocastico.md`: EMA+Fibo sin oscilador da z −10,29 en
siete instrumentos). Código en `bt/ema200_estocastico.py`.

Siete instrumentos, `z` agrupado por año desde el principio, y criterio
declarado antes de mirar: **z > 2 y positiva en 5 de los 7 instrumentos.**

## Las tres formas medidas

    A  retroceso a la EMA20    el precio toca la EMA20 y cierra de vuelta a favor
    B  cruce EMA20 / EMA200    el cruce clásico
    C  reversión estocástica   %K vuelve a cruzar el 20 (o el 80) desde fuera

Cada una con y sin el filtro de tendencia de la EMA200. Stop más allá del
extremo de las últimas 5/10/20 velas, objetivo 1/2/3 R, en H1, H4 y D1.
162 celdas.

## El resultado

              estrategia  EMA200 |       n    R neta       z  instrumentos +
    retroceso a la EMA20      no |  435372   -0,0409   -4,20            2/7
    retroceso a la EMA20      sí |  259695   -0,0398   -2,85            2/7
         cruce EMA20/200      no |   25809   +0,0062   +0,58            3/7
         cruce EMA20/200      sí |   25809   +0,0062   +0,58            3/7
   reversión estocástica      no |  204702   -0,0485   -6,44            1/7
   reversión estocástica      sí |   71172   -0,0532   -5,68            2/7

**Las dos ideas son negativas o cero.** El filtro de la EMA200 no cambia nada
—en el cruce ni siquiera puede, porque el propio cruce ya define la relación—.

Y un dato robusto dentro de esto: **la reversión del estocástico en H1 pierde
en los 7 instrumentos con z −10,03.** Eso no es ruido: es que desvanecer el
oscilador, en esa temporalidad, pierde de forma consistente.

Celdas que cumplen el criterio declarado: **1 de 162** (aparece dos veces en la
tabla porque el filtro es redundante en el cruce). H4, cruce EMA20/200, stop 10
velas, R:R 2 → +0,0495 R con z +2,05, positiva en 5 de 7. Con 162 celdas,
esperar una por encima de z=2 por azar es exactamente lo normal. Y aunque
fuera real: 550 operaciones en 6,5 años entre 7 instrumentos son 12 al año por
instrumento a +0,05 R, o sea **0,6 R al año**. No es operable.

## Lo que unifica dos meses de mediciones

Puestas juntas todas las familias medidas sobre siete instrumentos:

    entrada en retroceso de Fibonacci        z -10,29    0/7 positivos
    reversión con el estocástico             z  -6,44    1/7
    retroceso a la EMA20                     z  -4,20    2/7
    CRT (barrido y cierre de vuelta dentro)  bruta positiva, neta negativa

**Todo lo que consiste en entrar en contra del movimiento inmediato —comprar la
caída, desvanecer el extremo, esperar el retroceso— pierde después de costes, y
pierde en todos los instrumentos a la vez.**

Ésa es la generalización más útil del proyecto entero, y explica por qué han
fallado tantas cosas distintas: no eran ideas distintas. Eran la misma idea con
distinto disfraz.
