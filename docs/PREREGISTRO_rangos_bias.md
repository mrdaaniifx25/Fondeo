# Pre-registro · rangos por temporalidad y bias diario

Firmado **antes** de medir. Lo pide él: identificar los rangos de las velas en
H4, H1 y M15, y el bias diario.

## Lo que voy a medir

**1 · El tamaño real de cada rango.** Mediana y cuartiles en pips de D1, H4, H1
y M15 en EUR/USD. Sirve para saber si un stop de 15 pips cabe dentro de un
rango de M15 o se lo come.

**2 · Qué hace la vela siguiente con el rango de la anterior**, por temporalidad:

```
  barre el máximo · barre el mínimo · barre los dos · no barre ninguno (vela interior)
```

Y, cuando barre: **con qué frecuencia cierra otra vez dentro del rango**. Ése es
el montaje del CRT, así que quiero su frecuencia exacta por temporalidad.

**3 · El bias diario.** Cinco definiciones, todas calculadas **sólo con velas
cerradas**, al abrir el día:

```
  A  dirección de la vela diaria de ayer (cierre contra apertura)
  B  apertura de hoy contra el rango de ayer (encima / dentro / debajo)
  C  cierre de ayer contra el punto medio del rango de ayer
  D  barrido CRT: ayer barrió el mínimo de anteayer y cerró dentro -> alcista
                  ayer barrió el máximo y cerró dentro -> bajista
  E  cierre de ayer contra la EMA 20 diaria
```

Contraste: el movimiento del día de hoy, de apertura a cierre, en unidades de
ATR(14) diaria, con el signo del bias. Mediré media, estadístico t y acierto
direccional. **n ≈ 1.400 días**, error estándar ≈ 0,027 ATR.

## Lo que declaro antes

1. **Los rangos son descriptivos, no una señal.** Medir su tamaño y su tasa de
   barrido no es buscar ventaja; es saber qué dibujo.
2. **Espero que las cinco definiciones de bias den cero.** `RESULTADOS_tendencia_filtro.md`
   ya mostró que el oráculo de tendencia vale +0,1515 (z +2,48) y que la mejor
   medida causal captura el 12 % de eso. El bias diario es otra medida causal
   de lo mismo.
3. **Predicción concreta: ninguna de las cinco pasa |t| = 2,33**, que es el
   listón con cinco celdas (E[max|z|] ≈ 1,16, pero exijo el doble).
4. Espero que la tasa de «barre y cierra dentro» sea **alta en todas las
   temporalidades**, en torno al 20-35 %, y que eso NO signifique nada: barrer
   y cerrar dentro es lo que hace el precio por geometría, no por intención.
   Por eso mediré también el movimiento posterior.

## Lo que entrego pase lo que pase

El indicador de Pine con los cuatro rangos y el bias. Si el bias no predice, va
igual **pero etiquetado como información, no como señal**, y con su número
delante en el propio código.
