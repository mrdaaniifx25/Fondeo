# Pre-registro · la estrategia del vídeo (@Elpsicologodeltrading)

Firmado **antes** de medir. Reglas transcritas literalmente de su ficha.

## Sus reglas

```
  temporalidad   M15
  activo         EUR/USD
  media          EMA 20
  filtro         RSI < 30 para largos · RSI > 70 para cortos
  confirmación   vela de rechazo

  SETUP LARGO    precio por debajo de la banda, muy alejado de la EMA 20
                 RSI < 30 · entrada larga tras vela de rechazo
  SETUP CORTO    precio por encima de la banda, muy alejado de la EMA 20
                 RSI > 70 · entrada corta tras vela de rechazo

  STOP           detrás del extremo reciente
  TARGET         vuelta a la EMA 20 o zona media
  extra          "tomar parciales en la media"
```

## Sus cifras

```
                        Mean Reversion   Buy & Hold intradía
  Rentabilidad total        +36 %              +9 %
  Profit Factor             1,48               0,97
  Win Rate                  61 %               44 %
  Drawdown máximo           -8 %              -15 %
  Ratio beneficio/riesgo    1,25               0,70
```

La propia ficha las etiqueta **«Ejemplo orientativo»**, así que no las tomo
como un backtest publicado sino como una ilustración. Aun así sirven de
contraste.

**Nota de consistencia interna, antes de medir nada**: con acierto 61 % y pago
1,25, el Profit Factor sería `0,61 × 1,25 / (0,39 × 1) = 1,96`, no 1,48. Para
que el PF sea 1,48 con 61 % de acierto, el pago real tiene que ser **0,95**, no
1,25. Las tres cifras no pueden ser verdad a la vez.

## Por qué este test importa y no es «otro más»

1. **La familia es la correcta.** En `RESULTADOS_scalping.md` acabo de medir
   que la reversión a la media en intradía tiene **bruto positivo de verdad**
   (+0,0596 R con RSI(2) en M5, n = 23.503). El vídeo apunta a algo real.
2. **El objetivo es variable, no un múltiplo fijo de R.** «Vuelta a la EMA 20»
   es un objetivo que se mueve. Eso es **gestión de la posición**, la única
   dimensión del proyecto que no he explorado nunca.
3. **Los parciales también.** «Tomar parciales en la media» es exactamente eso.

## Lo que voy a medir

```
  banda        1,5 · 2,0 · 2,5 desviaciones de la EMA 20
  RSI          14 periodos, umbrales 30/70 (los suyos)
  rechazo      vela que perfora la banda y cierra en la mitad contraria
  entrada      apertura de la vela M15 SIGUIENTE
  stop         detrás del extremo de las 3 últimas velas, +1 pip
  objetivo     A · EMA 20 congelada en la entrada
               B · EMA 20 dinámica (la de verdad: se mueve)
               C · parcial 50 % en la EMA 20, el resto a 2R
               D · control: objetivo fijo a 1R y a 2R
  salidas      resueltas minuto a minuto con el M1
  coste        0,7 pips ida y vuelta, y sensibilidad a 0,3 / 1,4 / 2,0
  reparto      70 % ajuste / 30 % validación
```

## Lo que declaro antes

1. **Espero un acierto alto, del 60-70 %.** Con el objetivo en la media y el
   stop pegado al extremo, así tiene que salir. Su 61 % me parece creíble.
2. **Y espero que no baste**, porque el stop «detrás del extremo reciente» es
   estrecho, y con stop estrecho el coste en R se dispara. Es el mismo muro de
   `RESULTADOS_scalping.md`: el bruto es real y vale 0,3 pips; el peaje cuesta
   0,7.
3. **Predicción concreta: acierto > 58 %, bruto positivo, neto negativo.**
4. Si el objetivo dinámico o los parciales baten al objetivo fijo, **eso sí
   sería nuevo** y lo diré con todas las letras.

## El criterio

Valida si el neto es ≥ 0 **en los dos tramos** con el coste a 0,7 pips. Si sólo
valida a 0,3, lo diré como lo que es: depende del bróker, no de la estrategia.
