# Resultado · el CRT clásico en M15 con stop ancho

Código: `bt/crt_clasico_m15.py`. EUR/USD, oro y DAX, coste ECN.
Patrón clásico puro: **la vela M15 anterior** define el rango, la actual barre un
extremo y cierra de vuelta dentro, entrada en la apertura de la siguiente.

---

## El stop ancho aquí EMPEORA, y mucho

```
  EURUSD · R:R 2 · todas las señales        n   ops/día  riesgo  acierto   geom    bruta     NETA
    stop 1,0 x ATR                      44219      26,1     6,0    29,7%  33,3%  -0,0318  -0,1650
    stop 1,5 x ATR                      44219      26,1     8,9    24,8%  33,3%  -0,0678  -0,1566
    stop 2,0 x ATR                      44219      26,1    11,9    19,8%  33,3%  -0,0950  -0,1616
```

**Monótono y al revés de lo esperado.** Cuanto más ancho el stop, peor el
acierto: del 29,7 % al 19,8 %, contra un nulo del 33,3 %. Con 1,5×ATR está
**8,5 puntos POR DEBAJO del azar**, con z −25,98.

## Por qué, y es mecánico

**El rango de referencia es UNA vela de 15 minutos.** Son 5-8 pips.
Un stop de 1,5×ATR son **8,9 pips**: más ancho que el propio nivel que se
supone que está protegiendo.

```
  rango de Asia  ->  30-60 pips  ->  un stop de 9 pips tiene sentido
  vela M15       ->   5-8 pips   ->  un stop de 9 pips no protege nada
```

**Ensanchar el stop sólo ayuda cuando está anclado a algo que mide más que el
stop.** Ésa es la lección, y no estaba escrita en ningún sitio del proyecto.

Con el stop ancho y un nivel diminuto, el objetivo a 2R queda a 17,8 pips — muy
lejos para una señal que nace de una vela de 15 minutos. El acierto se desploma.

## Las celdas menos malas

```
  EURUSD                                      n   ops/día  acierto    bruta     NETA      z
    1,5xATR · R:R 2 · solo Londres         5617       3,8    33,1%  +0,0239  -0,0664  -3,74
    1,5xATR · R:R 2 · Londres + 1 al día   1459       1,0    33,2%  +0,0069  -0,1025  -2,78
    1,5xATR · objetivo extremo opuesto    44192      26,1    69,2%  +0,0125  -0,0763 -22,39
  oro
    1,5xATR · R:R 2 · Londres + 1 al día    942       1,0    31,3%  +0,0011  -0,0319  -0,72
```

Incluso lo mejor se queda en el nulo geométrico clavado. **El filtro de Londres
sube el acierto del 24,8 % al 33,1 %** — ocho puntos y medio — pero sólo para
devolverlo al azar, no para superarlo.

## Y el volumen es inoperable

```
  26 señales al día en EURUSD.  29 en oro.  25 en DAX.
```

Con un límite de 3 operaciones diarias, hay que descartar **nueve de cada diez**
señales. Y elegir cuál tomar entre veintiséis es precisamente la discrecionalidad
que el método dice eliminar.

## Comparado con lo que ya tiene

```
  CRT clásico M15, stop 1,5xATR, todas          neta -0,1566
  CRT clásico M15, Londres + 1 al día           neta -0,1025
  SU VERSIÓN (rango de Asia, Londres, 1,5xATR)  neta -0,0208
```

**La versión del rango de Asia es cinco veces mejor que el clásico en M15.** Por
el motivo de arriba: el nivel mide lo suficiente para que el stop tenga sentido.

## Conclusión

El CRT clásico está diseñado para temporalidades donde la vela de referencia es
grande. Su propio indicador `pine/CRT_operativo.pine` lo dice: *«Recomendado:
gráfico de 12 horas. En M15 o H1 el coste se come cualquier ventaja.»*

Llevarlo a M15 y ensancharle el stop no lo arregla: **lo rompe por el otro
lado**, porque el stop deja de guardar relación con el nivel.
