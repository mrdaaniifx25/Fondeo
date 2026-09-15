# Resultado · las anomalías académicas, medidas en 2020-2026

Preregistro sellado en `748ab3a`. Un solo pase. Código en `bt/anomalias.py`.
Un tick corrupto del GER40 (2023-12-04, +271 % de noche) se anuló con un
filtro de |salto| > 15 %; está en el código.

## Las cuatro, y las cuatro muertas

    H1  la noche frente al día      dif +0,0075 %   z +0,37    NO
    H2  ventana 02:00-03:00 NY      ver abajo                  MUERTA (predicho)
    H3  cambio de mes               dif -0,0066 %   z -0,13    NO
    H4  noche tras día bajista      dif -0,0238 %   z -0,88    NO, y al revés

Exigía z ≥ 3,0 agregado, mismo signo en los tres índices y ausencia en los
placebos. No llega ninguna, ni de lejos.

## H2 · la única predicción que acerté, y era en contra

El paper del NY Fed (Boyarchenko, Larsen & Whelan, 2023) dice que casi el
100 % de la prima de riesgo americana se ganaba entre las 02:00 y las 03:00
de Nueva York. Los mismos autores publicaron en julio de 2026 que eso murió.

Medido aquí:

    NASDAQ   2020-2021    +4,71 % anualizado   z +1,52
    NASDAQ   2022-2026    +0,43 % anualizado   z +0,34
     SP500   2020-2021    +2,99 % anualizado   z +1,11
     SP500   2022-2026    -0,32 % anualizado   z -0,32

Reproducido exactamente. Firmé que estaría muerta y lo está.

Esto importa por una razón que no es la ventana: **un efecto publicado en
una de las mejores revistas de finanzas del mundo, con 21 años de datos y
revisión por pares, dejó de funcionar en cuanto se publicó.** Si eso le pasa
a ese, no hay ninguna razón para pensar que un método de Instagram sin datos
vaya a durar más.

## Lo que sí aparece, y no es una anomalía

    instr        n     NOCHE       z       DIA       z
    NASDAQ    1690   +0,0401   +1,71   +0,0405   +1,42
    SP500     1691   +0,0324   +1,64   +0,0244   +1,12
    GER40      770   +0,0500   +2,05   +0,0260   +1,03
    AGREGADO  4155   +0,0388   +2,93   +0,0313   +2,04

La noche sube. El día sube. Y suben **casi lo mismo**: la famosa asimetría
noche/día no existe en esta muestra (dif z +0,37).

Sumando los dos tramos: **+0,070 % al día, unos +19 % al año.** Con z +2,93 y
+2,04 en tramos independientes.

Eso no es una anomalía ni un patrón: es la prima de riesgo de la renta
variable. Y es, con diferencia, **lo único de todo este proyecto con un
z robusto que no se cae al corregir por comparaciones múltiples** — porque no
salió de buscar, salió de que la bolsa sube.

## Por año, para no venderlo mejor de lo que es

    anio     NOCHE       z       DIA       z
    2020   +0,0812   +1,29   +0,0399   +0,72
    2021   +0,0529   +2,12   +0,0443   +1,31
    2022   -0,0737   -1,68   -0,0312   -0,49     <- el año que te arruina
    2023   +0,0307   +1,53   +0,0808   +2,94
    2024   +0,0706   +3,34   +0,0113   +0,45
    2025   +0,0541   +1,69   +0,0264   +0,70
    2026   +0,0342   +0,73   +0,0399   +0,87

Seis años de siete positivos. Uno, 2022, que se lleva por delante todo.

## Placebos

EURUSD limpio (z +0,86 y +1,30, nada). El oro da la noche a +3,71, pero es su
propia subida de 2023-2025, y la diferencia noche-día se queda en +2,55, por
debajo del umbral que firmé. No invalida, pero tampoco confirma nada.

## Adónde lleva esto

La prima de riesgo es real, grande y medible. La pregunta que queda, y que
no se ha hecho nunca en este proyecto, es:

    ¿con cuánto apalancamiento hay que sostener esa prima para maximizar
    P(pasar un reto de fondeo), dadas SUS barreras y SU límite de 60 días?

Eso no es buscar señal. Es dimensionar la única ventaja que existe.
Se mide en `docs/PREREGISTRO_prima.md`.

## Fuentes

- Boyarchenko, Larsen & Whelan, *The Overnight Drift*, NY Fed Staff Report
  917 · Review of Financial Studies 36(9), 2023 —
  https://www.newyorkfed.org/research/staff_reports/sr917
- *The Disappearing Overnight Drift*, Liberty Street Economics, julio 2026 —
  https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/
- Quantpedia, *Turn of the Month in Equity Indexes* —
  https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes
