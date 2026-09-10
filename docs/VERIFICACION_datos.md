# ¿Están bien los datos del backtest?

Comprobado el 29 de agosto de 2026, a raíz de la duda del usuario.

## Prueba 1 · las horas y el cambio de hora

Volatilidad media por minuto, por hora de Madrid, sobre 2,4 millones de velas:

```
   7h   1,16 pips
   8h   1,87            <- abre Londres, salto x1,7
   9h   2,27
  13h   1,88
  14h   2,64            <- abre Nueva York
  16h   2,87            <- pico
  22h   0,83
```

El salto cae exactamente donde tiene que caer. Y **el pico está a las 16:00
tanto en verano (jun-ago) como en invierno (dic-feb)**, con un salto de las 07h
a las 08h de x1,73 y x1,66 respectivamente. Si el cambio de hora estuviera mal
tratado, verano e invierno picarían con una hora de diferencia. No lo hacen.

## Prueba 2 · integridad del fichero

```
  2.397.463 velas de 2020-01-01 a 2026-07-31
  timestamps duplicados ................. 0
  velas imposibles ...................... 0
  precios nulos o cero .................. 0
  minutos presentes en 08:00-11:30 ...... 209 de 210 (99,6 %)
```

## Prueba 3 · contra una fuente distinta

Sus 25 operaciones de agosto las leyó él en **TradingView (feed de OANDA)**;
yo las resolví en **HistData**. Dos fuentes independientes:

```
  operaciones con datos en las dos ...... 14
  coinciden en el resultado ............. 14 de 14
  desviación mediana del precio de salida  0,7 pips
```

## La limitación real: esos 0,7 pips

Dos brókers no dan exactamente el mismo máximo y mínimo de cada minuto. La
desviación mediana medida es de **0,7 pips**. Sobre un stop de 4-5 pips eso es
el 15-20 % del riesgo, y puede voltear operaciones individuales.

**Es un argumento más contra las estrategias de stop pequeño**: a esa escala ni
siquiera se pueden testear con fiabilidad, independientemente de si son
rentables. No es sólo que el coste se las coma; es que el propio backtest tiene
un margen de error del tamaño de la señal.

## Y aun así, el resultado no se mueve

Prueba de esfuerzo: suponer que **todas** mis mechas son demasiado largas y
alejar el stop, o sea equivocarme siempre a favor de la estrategia.

```
  margen a favor     %TP   R/op bruta   neta a 1,43
       0,00 p       32,2%      +0,0172      -0,1149
       0,35 p       33,0%      +0,0231      -0,1026
       0,70 p       33,6%      +0,0189      -0,1012
       1,50 p       35,3%      +0,0313      -0,0782
       3,00 p       37,5%      +0,0254      -0,0695
```

Regalándole **3 pips de margen a cada operación** —cuatro veces la desviación
observada, sobre un stop mediano de 14— el bruto pasa de +0,017 a +0,025. Nada.
Y la neta sigue negativa.

## Lo que no puedo verificar, dicho claro

- HistData es **un** feed agregado. El de su bróker diferirá algo.
- El coste lo añado yo, constante a 1,43 pips. El real varía a lo largo del día.
- **El deslizamiento no está modelado en absoluto.** Se asume que el stop y el
  objetivo se ejecutan al precio exacto. En la realidad el stop suele llenarse
  peor.

Esa última es importante y va en la dirección incómoda: **mis backtests son
optimistas**, no pesimistas. Con deslizamiento real, todo lo medido en este
proyecto sería algo peor de lo que he informado.
