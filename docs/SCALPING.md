# Scalping en M5. La mejor versión que existe.

Números: `docs/RESULTADOS_scalping.md`. 99 celdas medidas, ésta es la menos
dañada por el coste.

---

# PASO 0 · Antes de operar, mide tu coste

**Todo depende de este número y no lo tengo yo.**

En tu cuenta de FundingPips, con el tamaño mínimo:

```
  1  Abre una compra en EUR/USD.
  2  Ciérrala inmediatamente, sin esperar.
  3  Apunta cuánto has perdido, en pips.
  4  Repítelo 5 veces: a las 9:00, 11:00, 14:00, 15:30 y 17:00.
```

Esa pérdida es tu coste ida y vuelta. Y decide todo:

```
  menos de 0,49 pips  ->  la estrategia GANA. Opérala.
  0,5 a 0,8 pips      ->  queda en cero. Jugable, no rentable.
  1,0 pips            ->  -66 EUR/mes
  1,4 pips            ->  -118 EUR/mes
  2,0 pips            ->  -197 EUR/mes   NO la operes
```

**Si te sale por encima de 1 pip, el scalping está cerrado para ti en esa
cuenta** y no es cuestión de buscar otra estrategia: es el peaje.

---

## Las reglas

```
  INSTRUMENTO  EUR/USD
  GRÁFICO      5 minutos
  INDICADOR    RSI con periodo 2.  (TradingView lo trae: RSI, length 2.
               No hace falta ningún script.)
  HORARIO      08:00 a 18:00 Madrid. Fuera de ahí, no.

  COMPRA       cuando el RSI(2) cierra por debajo de 5
  VENTA        cuando el RSI(2) cierra por encima de 95

  ENTRADA      a mercado al cierre de esa vela de 5 minutos
  STOP         20 pips
  OBJETIVO     40 pips      (R:R 1:2)
  UNA POSICIÓN a la vez. Si tienes una abierta, ignoras las señales.
  RIESGO       0,50 % = 50 €   ->  0,25 lotes con stop de 20 pips
  TOPE         5 horas. Si no ha tocado nada, cierras a mercado.
```

Salen **2,5 operaciones al día**. Entras, pones stop y objetivo, y no la tocas.

## Por qué 20 pips y no 5

Porque lo medí en todas las anchuras:

```
  stop     5p      8p     12p     20p     25p     35p     50p
  bruto +0,0596 +0,0388 +0,0294 +0,0246 +0,0096 -0,0048 -0,0282
  coste  0,1400  0,0875  0,0583  0,0350  0,0280  0,0200  0,0140
  neto  -0,0804 -0,0487 -0,0289 -0,0104 -0,0184 -0,0248 -0,0422
```

Con 5 pips el peaje es el **14 % del riesgo** y pierdes **687 €/mes**. Con 50
pips el peaje es el 1,4 % pero la señal ya se ha deshecho y el bruto es
negativo. **20 pips es el fondo del valle**, medido, no elegido a ojo.

## Lo que vale, sin adornos

```
  n 23.503 señales en 5,7 años · 2,49 operaciones/día
  acierto 44,3 % · objetivo 2R
  bruto +0,0246 R   coste -0,0350 R   neto -0,0104 R   z -0,62
```

**z −0,62: estadísticamente es un juego justo.** El punto estimado es
ligeramente negativo y he elegido esta celda de una rejilla, así que lo honesto
es decir *justo*, no *positivo*.

Con eso, tu probabilidad de pasar las dos fases queda en torno al **30 %**, algo
por debajo del 35 % de un juego exactamente justo.

## Lo bueno que tiene esto de verdad

**La reversión a la media en M5 es real.** El RSI(2) en extremo da un bruto de
**+0,0596 R** con stop de 5 pips, con 23.503 operaciones detrás. Es el efecto
intradía más limpio de todo este proyecto, y es el primero que mido con un
bruto claramente distinto de cero.

No es que no haya nada ahí. **Lo que hay vale 0,3 pips, y el peaje normal
cuesta 0,7.** Toda tu rentabilidad está en el paso 0.

## Y lo que no te voy a esconder

El scalping de verdad —stops de 5 a 8 pips, 6-8 operaciones al día— cuesta
**entre 300 y 687 € al mes** sobre tu cuenta de 10.000. Eso es del **3 % al
6,9 % de la cuenta cada mes**, y con el límite total del 10 % el examen se
acaba en dos o tres semanas. Por aritmética, no por mala suerte.

Si después de medir tu coste te sale por debajo de 0,5 pips, dímelo y
reoptimizo la rejilla entera con tu número real en vez de con mi supuesto.
Cambiaría la anchura óptima del stop y probablemente también el montaje.

## El registro, como siempre

```
  fecha · hora · dirección · RSI al entrar · entrada · stop · objetivo · resultado
```

Y la segunda hoja: las veces que la señal apareció y **no** la tomaste, con el
motivo. A las 100 anotaciones puedo medir si filtrar señales a tu criterio
aporta algo. Con 2,5 señales al día tienes 100 en seis semanas, que es mucho
más rápido que con cualquier otra cosa que te haya dado.

**Eso es lo mejor que tiene esta estrategia: genera datos deprisa.**
