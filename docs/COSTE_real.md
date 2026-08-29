# El coste real de operar

Medido el 28 de agosto de 2026 sobre la cuenta de FundingPips en MT5.
Sustituye al 1,20 pips que el proyecto venía asumiendo sin verificar.

## Los números

**Spread** en EURUSD: **0,7 a 1,0 pips** en la ventana de Londres.

**Comisión**: 5,00 €/lote ida y vuelta, confirmado en tres operaciones del
historial (8 lotes → 40 €, 7 lotes → 35 €, 5 lotes → 25 €).

Conversión: cuenta en EUR, 1 lote de EURUSD = 10 $/pip = **8,62 €/pip** a 1,16.
Así que 5 €/lote = **0,58 pips**.

**Coste total: entre 1,28 y 1,58 pips.** El proyecto asumía 1,20, o sea que
todos los backtests anteriores son ligeramente optimistas.

Comprobación cruzada: sus tamaños de posición cuadran exactamente con 150 € de
riesgo — stop 2,0p → 8,7 lotes, 2,5p → 7,0, 3,5p → 5,0, y ha operado 8, 7 y 5.

## Lo que decide

Con este coste, el tamaño del stop pesa más que el criterio de entrada.

```
   stop    coste/riesgo   acierto necesario sólo para no perder (1:2)
   1,5p         105 %                 68,4 %
   2,0p          79 %                 59,7 %
   3,5p          45 %                 48,4 %
   5,0p          32 %                 43,9 %
   8,0p          20 %                 39,9 %
  10,0p          16 %                 38,6 %
                                      33,3 % = geometría pura
```

Su stop mediano de agosto son 3,5 pips: necesita acertar el **48,4 %** sólo para
quedar en tablas. Operó al 75 %. El escenario honesto, con las once que dijo que
habría tomado, es el 57,1 %.

Casos extremos de agosto: T14 con stop de 1,4 pips pagó el **113 %** del riesgo
en costes; T16 el 79 %; T15 el 75 %.

## Agosto recalculado

```
                          1,28 p                  1,58 p
                    neta/d     z      €     neta/d     z      €
como lo operaste    +0,956 +3,21  3.504    +0,872 +2,90  3.181
honesto (+11)       +0,418 +1,42  2.245    +0,337 +1,14  1.802
desde las 09:00     +0,650 +2,20  2.984    +0,567 +1,92  2.610
```

Bruto sin coste: +32,55 R = 4.882 €. **El coste se lleva entre el 28 % y el
35 % del beneficio bruto.**

## Consecuencia inmediata

El grupo exploratorio que iba en la dirección que él describe — niveles ya rotos
diez veces o más, 38,5 % de acierto contra el 33,3 % geométrico — tenía un coste
de equilibrio de **0,26 pips**. Con 1,28 está muerto cinco veces. Esa familia
queda cerrada por caja, no por criterio.

## Pendiente

Medir el spread con `mt5/spread_sesion.mq5` sobre el historial real en vez de a
ojo, para tener la media y el p90 de la ventana 08:00-11:30 en lugar de un rango
estimado.
