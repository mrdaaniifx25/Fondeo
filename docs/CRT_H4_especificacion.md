# CRT desde cero · la especificación que sale de tus respuestas

No de bctrades, no de los diez vídeos. De cómo operas tú, preguntado y
contestado, más lo que se ha podido medir de cada pieza.

## La regla, entera

```
1 · ESTRUCTURA en H4.  Una vela barre el extremo de la anterior y CIERRA
    dentro de su cuerpo. Eso crea el rango.
2 · CONFIRMACIÓN en H1.  Tiene que haber un rango vivo de H1 en la MISMA
    dirección en el momento en que cierra la vela de H4.
3 · ENTRADA al cierre de esa vela de H4. A mercado. Sin esperar nada más.
4 · STOP en la mecha del barrido, más un tick.
5 · OBJETIVO en el extremo opuesto de la vela base.
6 · SALIDA por objetivo, por stop, o a mercado a las 10 velas de H4.
```

| pieza | de dónde sale | qué dice la medición |
|---|---|---|
| Estructura en H4 | tu respuesta | — |
| H1 acompaña | **tu aportación** | +0,046 R frente a no exigirlo · **z +1,67, no significativo** |
| Entrada al cierre | **decisión mía** | sin medir alternativas |
| Stop en la mecha | **medido, no elegido** | acierta +2,9 puntos por encima de la geometría |
| Objetivo en el extremo opuesto | tu respuesta | canónico del CRT |
| 10 velas de horizonte | reconciliación | por debajo de 5 el resultado se distorsiona |

## Por qué el stop va pegado y no a 23 pips

Es lo más importante que se midió el día que montamos esto. Mismo setup, misma
entrada, mismo objetivo, cambiando **solo** dónde va el stop. Siete instrumentos.

| stop | tamaño | R:R | %TP | **%TP que predice la pura geometría** | diferencia | R bruta |
|---|---|---|---|---|---|---|
| **mecha del barrido** | 17 u | 1,31 | 46,2 % | 43,3 % | **+2,9 pts** | **+0,080** |
| extremo de 3 velas | 22 u | 1,04 | 49,7 % | 49,1 % | +0,6 pts | +0,051 |
| 0,5 × ATR | 18 u | 1,17 | 48,0 % | 46,1 % | +1,9 pts | +0,025 |
| **1,0 × ATR (23 pips)** | 36 u | 0,58 | 58,6 % | 63,1 % | **−4,5 pts** | **−0,014** |
| 2,0 × ATR | 71 u | 0,29 | 64,3 % | 77,4 % | **−13,1 pts** | −0,011 |

El objetivo del CRT es **estructural**: el extremo opuesto de la vela base, unos
20 pips de media en EURUSD H4. **No se ensancha cuando ensanchas el stop.** Con
23 pips estás arriesgando 23 para ganar 20.

Y hay algo peor que la geometría. Con el stop pegado, el CRT acierta **casi tres
puntos por encima** de lo que daría el azar con ese R:R: ahí está la información.
Con el stop a 1 ATR acierta **cuatro puntos y medio por debajo**. El stop ancho
no solo diluye la ventaja: te mantiene dentro de operaciones que ya estaban
invalidadas, y esas acaban peor que tirar una moneda.

Tiene sentido con lo que el CRT afirma. El setup dice «ese mínimo era el
mínimo». Si el precio vuelve a pasarlo, la lectura ya era falsa. El stop pegado
es lo que hace que el setup signifique algo.

## Lo que da, con los costes de verdad

Siete instrumentos, 2020-2026, con el filtro de H1:

```
n = 7.426     bruta +0,105 [+0,068, +0,141]     NETA +0,005
```

Por instrumento, la neta con el filtro puesto:

| | con filtro H1 | sin filtro |
|---|---|---|
| NAS100 | **+0,066** | +0,007 |
| XAUUSD | **+0,041** | +0,040 |
| GRXEUR | +0,018 | +0,006 |
| EURUSD | +0,016 | +0,017 |
| SPX500 | +0,004 | −0,057 |
| GBPUSD | −0,036 | −0,085 |
| USDJPY | −0,038 | −0,002 |

## Lo que esto NO es

**No es una estrategia demostrada.** La neta agregada es +0,005 R por operación:
cinco milésimas. Con 1.060 operaciones al año entre siete instrumentos eso son
unas 5 R anuales, y el intervalo de confianza incluye el cero con holgura.

**El filtro de H1 no está confirmado.** z +1,67, por debajo del umbral que
declaré antes de medirlo. En este proyecto tres hallazgos con z parecido se han
evaporado al confirmarlos. Y no queda ningún conjunto de datos limpio con
potencia suficiente para intentarlo.

**Y una predicción mía que falló.** Escribí antes de correr que el filtro de H1
no aportaría nada. Aportó +0,046 R. Me equivoqué en la dirección, y eso también
cuenta: es la primera vez que una idea tuya bate a mi expectativa.

## Para qué sirve entonces el indicador

Dijiste que lo que te deja fuera de operaciones no es el análisis: es no saber
**cuándo** entrar, y el miedo a llegar tarde. Eso no es un problema de criterio,
es una regla sin cerrar, y una regla sin cerrar se paga con ansiedad en cada
operación.

Por eso la entrada es **al cierre de la vela de H4, a mercado, sin excepciones**.
No hay punto óptimo que buscar. No se puede llegar tarde. El indicador decide y
tú ejecutas. Si la regla resulta ser mala, se verá en tu registro dentro de cien
operaciones — pero al menos habrás operado cien, en vez de mirar noventa.
