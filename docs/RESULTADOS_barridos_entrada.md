# Resultados · dónde entra él, señalado sobre el gráfico

60 barridos reales de EURUSD, sorteados de los 16.219 del histórico con semilla
20260916. Él marcó los 60 el 16 de septiembre de 2026 tocando la vela donde
abriría, o descartando. Página `docs/barridos_entrada.html`, análisis en
`bt/analiza_barridos.py`.

**Esto no era una prueba de acierto** y así estaba escrito en la página: se
enseñaban 12 velas posteriores al barrido porque sin ellas no se puede señalar
una entrada. Servía para aprender su regla. Lo que sigue hay que leerlo con esa
ventaja a su favor, no en su contra.

## 1 · No selecciona: toma el 87 %

    entra      52
    descarta    8      ->  87 % tomadas

Esto tumba lo que yo había escrito el mismo día. La regla dispara 8,91 señales
diarias y él opera una o dos, y yo supuse que descartaba el 80 % con criterio.
**No lo descarta.** Puesto delante de las señales, las toma casi todas.

La diferencia entre 8,91 y 1-2 no es criterio: es que sólo está delante de la
pantalla por la mañana. Es un horario, no un filtro.

De los 8 descartes, **7 son de Nueva York** y casi todos de 14:00 a 21:00. Lo
único que se parece a una regla de descarte es que le gusta menos Nueva York, y
eso también es horario.

## 2 · Ninguna regla mecánica reproduce su entrada

Se probaron siete descripciones candidatas contra sus 52 marcas:

| regla | exacta | ±1 vela |
|---|---|---|
| R1 la propia vela del barrido | **19 %** | 42 % |
| R2 1er cierre a favor | 8 % | 31 % |
| R4 1a que rompe el extremo de la anterior | 8 % | 31 % |
| R5 1er cierre más allá del cierre del barrido | 8 % | 35 % |
| R3 1a que rompe el extremo de la del barrido | 5 % | 35 % |
| R6 1er cierre más allá del extremo del barrido | 6 % | 32 % |
| **R7 su propuesta escrita** | **5 %** | 35 % |

Hay 13 posiciones posibles, así que acertar al azar da un 8 %. **Seis de las
siete reglas están en el azar.** La mejor, entrar en la propia vela del barrido,
llega al 19 %.

Y la que él mismo escribió como su regla acierta el **5 %**: por debajo del azar.

Sus desfases van de 0 a +11 velas sin moda clara. Mediana +2 velas, 10 minutos.

**Es la quinta vez que pasa lo mismo**, y esta vez es la más concluyente: las
cuatro anteriores codificaban su *descripción*. Ésta le puso el gráfico delante y
le pidió que **señalara**. Sigue sin haber regla.

## 3 · Y sus entradas no salen mejor que las mecánicas

Mismos 52 casos, su vela contra la que elegiría cada regla:

| | acierto | riesgo | coste %R | bruta | neta |
|---|---|---|---|---|---|
| **sus entradas** | 29,4 % | **2,9 p** | **49,3 %** | −0,118 | **−0,898** |
| R1 al cierre del barrido | 32,7 % | 2,5 p | 57,2 % | −0,019 | −0,691 |
| R2 1er cierre a favor | 25,0 % | 5,2 p | 27,8 % | −0,250 | −0,914 |
| **R7 su propuesta escrita** | 30,0 % | 5,4 p | 26,7 % | −0,100 | **−0,412** |

Emparejado, que es la comparación potente porque son los mismos casos:

    suyo - R1   diferencia -0,234 ± 0,367   z -1,25
    suyo - R7   diferencia -0,215 ± 0,452   z -0,93

**No se distingue de cero**, con n 51. No está demostrado que elija peor. Lo que
no hay es ni rastro de que elija mejor, y eso con 12 velas de futuro delante.

El detalle que más duele: **su propuesta escrita gana a sus marcas reales**
(−0,412 contra −0,898). No porque acierte más, sino porque espera, y esperar le
da 5,4 pips de stop en vez de 2,9.

## 4 · Control de que marcó en serio

    riesgo de sus 52 marcas    mediana 2,9 p   cuartiles 1,7 - 5,6
    sus operaciones reales     2 a 4 pips

Coinciden. Si hubiera ido tocando a bulto, la distribución del riesgo no
reproduciría la de sus capturas de esta semana. **Marcó como opera.**

## Veredicto

Las tres preguntas que quedaban vivas se han contestado a la vez, y las tres en
contra:

1. **¿Selecciona?** No. Toma el 87 %.
2. **¿Hay una regla de entrada?** No. Ninguna descripción la reproduce por encima
   del azar, ni siquiera la suya.
3. **¿Elige mejor que una regla?** No hay señal. Con el futuro a la vista,
   empata o pierde por un cuarto de R.

Lo único que sobrevive de todo esto, y sigue siendo suyo, es que **esperar a la
confirmación vale +0,22 R en bruta** — medido dos veces sobre 14.637
operaciones. Su instinto de no entrar al primer rechazo es correcto. Lo que hace
en la práctica es lo contrario: entra a 2,9 pips del extremo y el peaje se lleva
la mitad del riesgo.
