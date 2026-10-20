# Resultado · scalping en M1 y M5

Pre-registro: `docs/PREREGISTRO_scalping.md`, escrito **antes** de medir.
Código: `bt/scalping.py`, `bt/scalping_frontera.py`, `bt/scalping_coste_mes.py`.
Operativa: `docs/SCALPING.md`.

**99 celdas medidas. Ninguna positiva.** Pero el resultado útil no es ése: es
que todo el scalping se reduce a **un solo número que él puede medir en su
cuenta en cinco minutos.**

---

## 1 · Las 63 celdas del pre-registro

Siete montajes clásicos en velas de 5 minutos, salidas resueltas minuto a
minuto con el M1, sesión 08:00-18:00 Madrid, coste 0,7 pips ida y vuelta,
empates como pérdida, reparto 70/30.

**Las 63 negativas.** La mejor z es **−2,42**. Muestra: de 2.859 a 113.830
operaciones según el montaje.

```
  mejores z dentro de muestra
    5 fade de Bollinger      stop 20  R:R 2,0   z -2,42   FUERA -0,0198
    3 rotura rango Londres   stop 20  R:R 2,0   z -2,43   FUERA -0,0336
    1 cruce EMA 9/21         stop 20  R:R 2,0   z -2,50   FUERA +0,0239
```

El listón por selección con 63 celdas era **2,88**. No hay nada que ni se
acerque, y encima por el lado malo.

## 2 · Lo que sí aparece al sumar el coste de vuelta

Separando bruto y coste, los montajes de **reversión a la media** tienen un
bruto **positivo de verdad**:

```
  RSI(2) en M5, R:R 1:2, una posición a la vez
    stop    coste/riesgo   ops/día   BRUTO     neto      z    EUR/mes   % cuenta
       5        14,0 %       8,14   +0,0596  -0,0804  -7,00     -687     -6,87 %
       8         8,8 %       5,86   +0,0388  -0,0487  -3,76     -300     -3,00 %
      12         5,8 %       4,06   +0,0294  -0,0289  -1,98     -123     -1,23 %
      20         3,5 %       2,49   +0,0246  -0,0104  -0,62      -27     -0,27 %
      35         2,0 %       1,46   -0,0048  -0,0248  -1,38      -38     -0,38 %
      50         1,4 %       1,03   -0,0282  -0,0422  -2,26      -45     -0,45 %
```

**La reversión a la media en M5 existe.** El RSI(2) en extremo da **+0,0596 R
de bruto** con stop de 5 pips, y es el efecto más limpio que he medido a
horizonte intradía en todo el proyecto.

**Y el diferencial se lo come entero**, porque con stop de 5 pips el coste es
el 14 % del riesgo.

## 3 · Por qué ensanchar el stop no lo arregla

Es lo primero que uno piensa: si el coste es `diferencial/stop`, ensancho el
stop. **No funciona, y aquí está medido por qué:**

```
  stop     5p      8p     12p     20p     25p     30p     35p     50p
  bruto +0,0596 +0,0388 +0,0294 +0,0246 +0,0096 +0,0079 -0,0048 -0,0282
  coste  0,1400  0,0875  0,0583  0,0350  0,0280  0,0233  0,0200  0,0140
```

**El bruto se desinfla a la misma velocidad que el coste.** La reversión del
RSI(2) es un efecto de minutos: si le das 20 pips de margen todavía queda algo,
si le das 50 ya se ha deshecho y el bruto es negativo.

El mínimo de la curva está en **20 pips** (lo afiné en 12-15-18-20-22-25-30) y
ahí el neto es **−0,0104 R con z −0,62**. Estadísticamente indistinguible de
cero. Pero el punto estimado es negativo, y **he elegido esa celda de una
rejilla**, así que lo honesto es leerlo como *justo*, no como positivo.

## 4 · Todo se reduce a un número

El coste de equilibrio es `bruto × stop`:

```
  stop  5 pips  ->  necesita coste < 0,30 pips
  stop  8 pips  ->  necesita coste < 0,31 pips
  stop 12 pips  ->  necesita coste < 0,35 pips
  stop 20 pips  ->  necesita coste < 0,49 pips
```

Y en la celda buena, el resultado mensual en función de **su** coste real:

```
  coste 0,3 pips  ->  neto +0,0096 R (z +0,58)   +25 EUR/mes   (+0,25 %)
  coste 0,5 pips  ->  neto -0,0004 R (z -0,02)    -1 EUR/mes   (-0,01 %)
  coste 0,7 pips  ->  neto -0,0104 R (z -0,62)   -27 EUR/mes   (-0,27 %)
  coste 1,0 pips  ->  neto -0,0254 R (z -1,52)   -66 EUR/mes   (-0,66 %)
  coste 1,4 pips  ->  neto -0,0454 R (z -2,72)  -118 EUR/mes   (-1,18 %)
  coste 2,0 pips  ->  neto -0,0754 R (z -4,52)  -197 EUR/mes   (-1,97 %)
```

**El scalping no es una cuestión de estrategia. Es una cuestión de peaje.** La
frontera está en **0,49 pips** de coste ida y vuelta, y él puede medir el suyo
en cinco minutos abriendo y cerrando una posición mínima.

Mi supuesto de 0,7 pips es de ECN. **En una cuenta de fondeo suele ser peor**,
1,0-1,5 pips con la comisión incluida, y entonces esto cuesta entre 66 y 118 €
al mes. Ése es el dato que falta y lo tiene él.

## 5 · El scalping de verdad, con su número

Lo que la gente llama scalping —stops de 5 a 8 pips, 6-8 operaciones al día—
cuesta, medido, **entre 300 y 687 € al mes** sobre una cuenta de 10.000 al
0,50 % de riesgo. Eso es **del 3 % al 6,9 % de la cuenta cada mes**.

Con un límite total del 10 %, **el examen se termina en dos o tres semanas.**
No por mala suerte: por aritmética.

Y fíjese en la coincidencia del stop de 8 pips: **−300 €/mes** es exactamente
la cifra que quiere ganar, con el signo cambiado.

## 6 · Mi predicción, y en qué me equivoqué

Predije que ninguna celda sobreviviría al coste. Acertado: 99 de 99.

En lo que me equivoqué: **predije que el bruto estaría en cero**, como todo lo
demás que he medido a horizonte intradía. No lo está. El bruto de la reversión
a la media es **+0,0596 R** y es sólido (n = 23.503). Es la primera señal
intradía de este proyecto con un bruto claramente distinto de cero.

No cambia la conclusión práctica, pero sí cambia el diagnóstico: **no es que no
haya nada ahí. Es que lo que hay vale 0,3 pips y el peaje cuesta 0,7.**
