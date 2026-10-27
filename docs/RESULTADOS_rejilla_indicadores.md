# Resultado · la rejilla completa de indicadores en sus instrumentos

Sin pre-registro: no hay hipótesis que firmar, es un **censo**. Se publican las
108 celdas salgan como salgan. Código: `bt/rejilla_indicadores.py` y
`bt/rejilla_vs_comprar.py`.

Nueve indicadores × cuatro temporalidades (M15, H1, H4, D1) × tres instrumentos
suyos: EURUSD 2021-2026, oro 2023-2026, DAX 2023-2026. Estadístico sobre meses.

---

## Primero: él tiene razón y yo me expresé mal

Mi mensaje anterior dejó la impresión de *«no funciona ningún indicador»*. **Eso
no es lo que dicen mis datos.** Lo que dicen mis propios números, publicados en
`RESULTADOS_indicadores.md`, es que sobre 55 años el RSI de momento da **t
+7,50**, el MACD **t +7,71** y Donchian 20 **t +8,43**. Eso es un indicador
funcionando, y con creces.

Lo que yo quería decir, y dije mal, es que **el efecto se ha ido de los mercados
líquidos en los últimos trece años**. Son afirmaciones distintas y las mezclé.

Y su incredulidad tiene un segundo fundamento: mis pruebas eran sobre divisas
del panel de la Fed, no sobre lo que él mira en pantalla. Así que aquí está la
rejilla entera, en sus instrumentos, para que no tenga que fiarse de mí.

## El censo: 108 celdas

```
  BRUTO   t mediano +0,86   con t>+2: 11   con t<-2:  2
  NETO    t mediano +0,57   con t>+2: 10   con t<-2: 13
  esperado por azar con 108 celdas al 5 %: 2,7 por cola
```

**Diez celdas con t neto por encima de +2, cuando el azar daría 2,7.** Eso es
más de lo esperable. Él tenía razón en no tragarse un «nada funciona».

Y el coste se comporta exactamente como manda la teoría del horizonte:

```
  t NETO mediano por temporalidad      coste medio por cambio
    M15    -1,15                        23,5 % del ruido de la barra
    H1     +0,55                        10,5 %
    H4     +0,88                         5,5 %
    D1     +0,84                         2,2 %
```

En M15 la mediana es **negativa**. Subiendo de temporalidad se vuelve positiva.
Ése es el muro de `RESULTADOS_muro_horizonte.md` visto desde otro lado.

## Dónde están esas diez celdas

Todas en **oro** y **DAX**. En EURUSD, 36 celdas y **ni una sola** por encima
de t +1,1 en neto. Lo mejor del par es MACD 12/26 en D1 con t +1,05.

¿Y qué hicieron el oro y el DAX en la muestra?

```
  EURUSD 2021-2026:   -5 %
  oro    2023-2026:  +143 %
  DAX    2023-2026:  +573 %
```

Ahí está la pregunta entera: ¿el indicador aporta algo, o simplemente estuvo
largo en un mercado que se multiplicó?

## El control que lo decide: contra comprar y aguantar

Exceso mes a mes de cada celda **sobre comprar y no tocar nada**. Oro, D1, que
es donde están las mejores:

```
  indicador           t propio   exceso sobre B&H   largo % del tiempo
  canal ATR 20/2       +3,09          +0,01                80 %
  Donchian 55          +2,70          -0,22                78 %
  MM 20/100            +2,61          -0,13                71 %
  MM 50/200            +2,50          -0,49                72 %
  Donchian 20          +1,94          -0,99                63 %
  MACD 12/26           +1,93          -1,16                68 %
  MACD 12/26/9         +1,18          -2,01                54 %
  RSI 14 momento       +0,76          -2,20                64 %
  RSI 14 reversión     -1,98          -2,98                18 %
```

**De las 108 celdas, ninguna bate a comprar y aguantar con t > +2.** La mejor de
todas es el canal ATR en oro diario, con un exceso de **+0,01**. Cero exacto.

Y la columna de la derecha lo explica sin más comentario: las celdas ganadoras
están **largas el 71-80 % del tiempo** en un metal que subió un 143 %. No son
señales. Son una posición larga con pasos intermedios.

En DAX, con un +573 % detrás, es aún más claro: **las 36 celdas pierden contra
comprar y aguantar**, varias con t por debajo de −2.

## Y EURUSD es el control que él ya tenía en casa

El euro se movió un −5 % en cinco años. No hay tendencia que capturar, y por eso
mismo es el instrumento honesto de los tres. Resultado:

```
  M15   las nueve celdas negativas en neto, hasta t -13,36
  H1    ocho de nueve negativas
  H4    mediana ~0
  D1    mediana ~0, mejor celda t +1,05
```

**Cuando el instrumento no sube solo, el indicador no encuentra nada.**

## Lo que queda en pie

1. **Los indicadores sí funcionan.** t +8 sobre 55 años y 25 mercados. Eso está
   medido y publicado, y no lo retiro.
2. **Pero lo que capturan es la tendencia del mercado, no una habilidad de la
   señal.** En cuanto se compara contra estar largo y no hacer nada, el exceso
   se va a cero en las 108 celdas.
3. **Y en intradía ni eso**: en M15 la mediana es negativa por el coste.

Eso no es «nada funciona». Es algo más incómodo y más preciso: **funciona
exactamente lo mismo que comprar y esperar, cobrando comisión por el trayecto.**

## Lo que esto no cierra

La muestra de oro y DAX es de **32 meses**. Con 32 meses no se distingue un
exceso pequeño de cero, y los excesos medidos son pequeños. Si alguien quiere
defender que el canal ATR en oro diario aporta algo sobre comprar y aguantar,
el dato de aquí no lo refuta: lo deja en +0,01 con un error grande.

Lo que sí refuta, con margen, es que alguno de estos indicadores en intradía
tenga algo que ofrecer.
