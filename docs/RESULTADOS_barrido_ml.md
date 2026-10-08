# Resultados · ¿se puede mecanizar la elección de la entrada?

Pre-registro `docs/PREREGISTRO_barrido_ml.md`, escrito antes de construir nada.
Código en `bt/barrido_ml_datos.py` y `bt/barrido_ml.py`.

**199.890 filas**: los 16.219 barridos de EURUSD 2020-2026 por las 13 velas en
las que se puede entrar, cada una etiquetada con su R neta real.

## El criterio, y qué pasa con él

| | condición | resultado |
|---|---|---|
| 1 | IC95 de la neta del decil superior entero sobre cero | ✘ **[−0,088, −0,041]** |
| 2 | la mejora supera el rango de los 20 nulos | ✔ +0,73 contra +0,06 a +0,13 |
| 3 | quedan ≥ 300 operaciones | ✔ 13.834 |

**Hacen falta las tres. No se cumple.**

## Pero la 2 importa mucho, y hay que decirlo entero

    mejora real          +0,7293
    20 nulos       de    +0,0628  a  +0,1322

El modelo encuentra **cinco veces y media** lo que el mismo método saca de datos
sin señal. Ahí hay estructura de verdad.

De decil a decil, fuera de muestra (2022-2026):

| decil | n | acierto | riesgo | coste %R | bruta | **neta** |
|---|---|---|---|---|---|---|
| 1 | 13.834 | 32,1 % | 0,7 p | 204 % | −0,037 | −3,587 |
| 5 | 13.834 | 29,7 % | 4,4 p | 33 % | −0,109 | −0,466 |
| 9 | 13.834 | 35,0 % | 12,0 p | 12 % | +0,050 | −0,088 |
| **10** | 13.834 | 34,9 % | 16,4 p | 9 % | **+0,048** | **−0,064** |

La columna de la neta se mueve 3,5 R de arriba abajo. La bruta se mueve 0,08.
**Casi toda la mejora es el canal del coste**: el modelo aprendió a elegir
entradas con el stop ancho, que es aritmética, no adivinación.

Y la importancia de las variables lo confirma sin lugar a dudas:

    rgoP (riesgo en pips)  0,7400  ################################
    costepc                0,0576  ##
    cerro_mas_alla         0,0214  #
    recorrido              0,0199  #

El riesgo en pips vale trece veces más que la siguiente variable. Todo lo demás
—profundidad del barrido, cuerpo, mechas, momento, hora, día, ATR— es ruido a su
lado.

## Y aun así hay selección de verdad, y es la primera vez

Comparando **a igualdad de ancho de stop**, que es la comparación justa:

    todas las operaciones con stop >= 10 p    bruta -0,0874   neta -0,1749
    el decil del modelo con stop >= 10 p      bruta +0,0501   neta -0,0267

**+0,137 de bruta con el mismo stop.** Eso ya no es el coste: es selección real,
y es la mayor que ha producido nada en el proyecto. La bruta del decil superior
es +0,0479 con z +3,94, significativa.

El mejor corte que se ha medido nunca:

    decil superior con stop >= 10 pips
    n 10.748   acierto 35,0 %   coste 7,4 %
    bruta +0,0501   NETA -0,0267   IC95 [-0,0538, +0,0003]

El intervalo **toca el cero por arriba** y no lo cruza. Es lo más cerca que ha
estado este proyecto en dos meses.

> Aviso: ese corte de 10 pips **no estaba pre-registrado**, se eligió después de
> ver la tabla. No cuenta como resultado, y necesitaría su propia prueba fuera de
> muestra antes de creérselo.

## Lo que hace falta para cruzar, en un número

Con bruta +0,050 y un riesgo mediano de 19 pips en esa banda, la neta sale cero
cuando el coste baja de **1,43 a 0,97 pips**.

No hace falta una estrategia mejor. Hace falta **un tercio menos de peaje**.

Y el techo está localizado: la ventaja bruta vive en la banda de 10 a 20 pips.
Por encima de 20 se desvanece (bruta −0,006 y plana), así que ensanchar más el
stop ya no ayuda.

## Veredicto

A su pregunta —*"no me digas que no se puede mecanizar"*— la respuesta honesta
es **a medias, y más cerca de lo que ha estado nunca**:

- **Sí se mecaniza**, y el modelo bate a los nulos por cinco veces y media.
- **Casi todo lo que aprende es el coste**, no el patrón. La variable que manda
  es el ancho del stop, con trece veces la importancia de la siguiente.
- **Pero queda selección real**: +0,137 de bruta a igualdad de stop.
- **Y sigue sin cruzar.** El mejor corte medido es −0,027, con el intervalo
  tocando el cero.

Ninguna regla escrita a mano, ninguna confluencia y ningún criterio suyo se
acercó nunca a esto. El modelo con 200.000 filas etiquetadas sí. Y se queda a
tres centésimas de R.
