# Pre-registro · doble barrido con el stop en el barrido de 4h

**Escrito el 2026-09-15, antes de medir.** Continuación de
`RESULTADOS_doble_barrido.md` (commit `dad3d02`).

## De dónde sale

La prueba anterior encontró la mayor ventaja bruta de todo el proyecto —**+0,1228
R** en 12h+4h con envolvente de M15— y murió porque el disparador deja un stop de
6,8 pips y el coste se lleva el 19,6 % del riesgo.

```
para empatar con +0,1228 de bruta  ->  stop de 11,6 pips
para sacar +0,05 neto              ->  stop de 19,6 pips
```

El stop lo pone el disparador, no el patrón. **Así que se cambia el stop y se
deja el patrón intacto.**

## El único cambio

Idéntico a la prueba anterior en todo —detección del doble barrido, envolvente de
M15 como disparador, entrada al cierre, objetivo 1:2— **salvo el stop**:

```
antes:  el extremo de la envolvente de M15
ahora:  el extremo del barrido de la vela de 4h
```

Es el extremo que el barrido de 4h dejó al llevarse la liquidez: el sitio donde
el patrón queda invalidado, no donde acaba la vela de entrada.

## Celda principal

```
par 12h+4h   ·   envolvente en M15   ·   stop en el barrido de 4h   ·   objetivo 1:2
```

La misma que la vez anterior, para que las dos sean comparables. Se reportan las
6 celdas (3 pares × M15 y M5).

## El desglose por instrumento, declarado AHORA

Pregunta suya: «¿y en el EURUSD?». Se declara antes de mirar para que no sea una
elección posterior: **se reportan los cinco instrumentos siempre, en las dos
pruebas —la anterior y ésta— y el EURUSD no recibe trato distinto.**

Cinco instrumentos son cinco comparaciones más. **Ningún instrumento suelto
cuenta como éxito**: el criterio sigue siendo la celda principal agregada. El
desglose es para ver si el efecto es consistente o vive en uno solo, que es
justo lo que hundió a la familia EMA+Fibo+estocástico en agosto.

## Qué cuenta como éxito

**R neta positiva en la celda principal, con IC95 al 95 % excluyendo el cero por
arriba**, error estándar agrupado por instrumento-día. Igual que antes.

## Qué cuenta como fracaso

Que el intervalo incluya el cero o quede por debajo. La idea se cierra y no se
renegocia.

## Predicciones

1. **El coste bajará del 19,6 % a menos del 10 % del riesgo.** Es aritmética: el
   stop se ensancha.
2. **La ventaja bruta en R BAJARÁ.** Y esto hay que decirlo por delante porque es
   lo que decide: al ensanchar el stop, la unidad R es mayor, así que el objetivo
   1:2 queda mucho más lejos en precio y el acierto cae. La línea del azar
   —33,3 % con 1:2— no cambia, pero que el patrón mantenga su ventaja a esa
   escala es justo lo que no se sabe.
3. **La neta quedará entre −0,05 y +0,05**, es decir cerca de cero. Si sale
   claramente positiva, es el primer hallazgo operable del proyecto. Si sale
   claramente negativa, se cierra la familia entera del doble barrido.

## Potencia

Con el stop más ancho habrá menos disparos válidos. Se reportará la n y el efecto
mínimo detectable **antes** de interpretar el resultado; si el detectable supera
al esperado, se dirá que la prueba sólo puede falsar.
