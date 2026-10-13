# Resultado · 14.166 estrategias mecánicas buscadas por fuerza bruta

Pre-registro: `docs/PREREGISTRO_busqueda_masiva.md`. Código: `bt/busqueda_masiva.py`.
63 primitivas · 9 paneles (EUR/USD, oro, DAX × M5, M15, H1) · 6 salidas × 2
direcciones · **20.000 estrategias generadas, 14.166 válidas** (≥200 operaciones
dentro de muestra y ≥50 fuera). Coste ECN.

Dentro de muestra: hasta 31-12-2024. **Fuera: 2025-2026**, no mirado hasta haber
elegido.

---

## Por qué esta prueba y no otra

Reto del usuario: *«tienes los datos, un sistema de backtest, no me creo que no
puedas encontrar nada ni scalping, ni day trading ni nada»*.

Es justo, y la respuesta no es repetir conclusiones: es **dejar de elegir yo**.
Se generan combinaciones aleatorias de 2-3 condiciones de entre 63 primitivas
—osciladores, medias, MACD, volatilidad, rupturas, barridos de liquidez, patrones
de velas, tramo horario, día de la semana— y se mide el espacio entero.

La arquitectura que lo hace posible: **el desenlace de cada barra se precalcula
una vez** para cada stop y objetivo, en largo y en corto. Después una
«estrategia» es sólo una máscara booleana, así que evaluar 20.000 es gratis.

## 1 · La distribución entera

```
  media del t dentro de muestra : -3,77      desviación : 3,92
  con t > +2:    90        con t < -2:  8.831
  con t > +3:     5        con t < -3:  6.730
  con t > +4:     0        con t < -4:  5.159
  R neta media de las 14.166: -0,0962 dentro / -0,0820 fuera
```

**El centro de la distribución es el coste.** Catorce mil estrategias mecánicas y
la media está en t −3,77. No es que las malas sean malas: es que **todas pagan la
horquilla**, y eso desplaza el histograma entero a la izquierda.

Y el dato que más dice: si estas 14.166 fueran monedas limpias, se esperarían
**322** con t > +2 y **19** con t > +3. Hay **90** y **5**.

**La búsqueda encuentra menos estrategias buenas que las que produciría el puro
azar.** Porque el azar no paga comisión.

## 2 · Las mejores dentro de muestra, ¿qué hacen fuera?

Primero en crudo, y ya se ve el encogimiento:

```
  selección                     t dentro   R dentro    R FUERA   t FUERA
  las 10  mejores por t dentro    +3,07    +0,1561    +0,0364     +0,67
  las 50  mejores                 +2,59    +0,1317    +0,0223     +0,56
  las 100 mejores                 +2,34    +0,1187    +0,0126     +0,39
  las 200 mejores                 +2,04    +0,1014    +0,0087     +0,30
  las 500 mejores                 +1,55    +0,0780    +0,0095     +0,30
```

De +0,156 dentro a **+0,036 fuera**, con t +0,67. Un 77 % del resultado
desaparece al cambiar de tramo, y lo que queda no es significativo.

## 3 · Y la correlación cruda miente — hay que quitar la línea base

```
  correlación CRUDA t dentro vs t fuera : +0,8416
  correlación CRUDA R dentro vs R fuera : +0,6116
```

**+0,84 parece demoledor a favor de buscar. Está confundido**, por dos cosas que
son idénticas en los dos tramos y no tienen nada que ver con ventaja:

1. **El coste depende de k y del panel.** Las estrategias con stop ancho en oro
   pagan el 2 % del riesgo; las de stop estrecho en EUR/USD el 20 %. Eso las
   ordena igual dentro y fuera.
2. **El oro subió 143 % y el DAX 573 %.** Cualquier cosa «larga» gana en los dos
   tramos sin saber nada.

La corrección: restar la **línea base** = el resultado de entrar en **todas** las
barras de ese panel con el mismo stop, objetivo y dirección. Lo que queda es el
**exceso**, que es lo único que mide si la *regla de entrada* aporta algo.

```
  correlación EXCESO dentro vs EXCESO fuera : +0,1287
  exceso medio de las 14.166: -0,0002 dentro / -0,0002 fuera
  n = 14.166   error estándar 0,0084
```

## 4 · PRINCIPAL · qué significa +0,1287

Es **estadísticamente distinto de cero** —quince errores estándar— y
**económicamente nada**:

```
  r = 0,1287   ->   r² = 0,0166
```

**El resultado dentro de muestra explica el 1,7 % del resultado fuera.** El
98,3 % de lo que mide en un backtest no le dice nada sobre el futuro.

Y en la práctica, el encogimiento es peor que eso: **cuanto más fuerte
selecciona, peor sale fuera.**

```
  selección por exceso dentro   exc dentro   exc FUERA   % positivas fuera
  las 10  mejores                 +0,2766     -0,0198          50 %
  las 50  mejores                 +0,2088     +0,0017          54 %
  las 100 mejores                 +0,1827     +0,0033          56 %
  las 200 mejores                 +0,1575     +0,0135          58 %
  las 500 mejores                 +0,1257     +0,0165          60 %
  (todas)                         -0,0002     -0,0002          50 %
```

Las **diez mejores** de catorce mil, con un exceso de +0,277 dentro de muestra,
dan **−0,0198 fuera**. Cara o cruz: 50 % positivas.

Las 500 mejores retienen +0,0165 de +0,1257: **un 13 %**. Ése es el factor de
encogimiento real de un backtest optimizado.

## 5 · Las seis mejores, con nombre y apellido

```
  DAX/M15   corto k1 RR2  hora 12-16 Y lunes Y RSI7<50
     dentro n  480  exc +0,3722      FUERA n  433  exc +0,1110  t +0,30
  DAX/H1    corto k1 RR2  hora 04-08 Y MACD<señal Y martes
     dentro n  224  exc +0,3100      FUERA n  159  exc +0,1327  t +0,29
  oro/H1    corto k1 RR2  hora 00-04 Y 3 rojas
     dentro n  254  exc +0,3005      FUERA n  196  exc +0,1381  t +0,54
  DAX/H1    largo k1 RR2  miércoles Y MM10>MM20 Y hora 12-16
     dentro n  206  exc +0,2755      FUERA n  178  exc -0,0942  t -0,35
  DAX/M15   largo k1 RR2  MM20<MM100 Y viernes Y MM10<MM20
     dentro n 1066  exc +0,2700      FUERA n 1260  exc -0,0801  t -2,07
  oro/H1    largo k1 RR2  miércoles Y barra estrecha
     dentro n  376  exc +0,2646      FUERA n  175  exc -0,3098  t -2,16
```

Tres positivas fuera, tres negativas. **Cara o cruz.** Y las tres «ganadoras»
tienen t de +0,30, +0,29 y +0,54: indistinguibles de cero.

Mire también **qué son**: «lunes por la tarde con RSI7 bajo 50», «martes de 4 a 8
con MACD bajo su señal», «miércoles con barra estrecha». Un día de la semana y un
tramo de cuatro horas. **Eso es la forma que tiene el sobreajuste**, y es
exactamente lo que uno encontraría buscando a mano y creería haber descubierto.

## 6 · Mi predicción firmada

| firmé | salió | |
|---|---|---|
| distribución desplazada a negativo y más ancha que N(0,1) | media −3,77, desv 3,92 | ✔ |
| habrá cientos con t > +3 dentro (y no significa nada) | hay 5 con t>+3, 90 con t>+2 | ✘ (menos aún) |
| las mejores darán fuera entre −0,05 y +0,02 | las 10 mejores por exceso: **−0,0198** | ✔ |
| **PRINCIPAL: correlación entre −0,10 y +0,10** | **+0,1287** | ✘ por poco |

El principal se salió de mi banda por 0,03, y lo digo: **la correlación no es
cero.** Lo que sí es, es irrelevante — un 1,7 % de varianza explicada.

Mi umbral de refutación declarado era +0,20 o las mejores dando fuera un positivo
con t > +2. **No se alcanza ninguno de los dos.**

## La respuesta a su reto

No es «no puedo encontrar nada». Es más preciso y más incómodo:

**Encuentro miles.** Noventa estrategias con t > +2 dentro de muestra, algunas
con profit factor por encima de 1,5. Si quisiera venderle una, tendría noventa
para elegir, cada una con su gráfico de equity subiendo.

**Y ninguna sobrevive al cambio de tramo.** Las diez mejores de catorce mil dan
−0,02 fuera de muestra. El 1,7 % de lo que mide dentro se conserva fuera.

Eso es lo que significa que un espacio sea eficiente: **no que no haya nada que
encontrar, sino que lo que se encuentra no se repite.** Y por eso existe un
mercado entero de cursos: encontrar es fácil, y comprobar que no se repite exige
guardarse dos años de datos sin mirarlos.
