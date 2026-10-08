# Resultados · R:R extremo sobre stops diminutos

Pre-registro: `docs/PREREGISTRO_rr_extremo.md`, subido **antes** de medir.
Código: `bt/rr_extremo.py`. ~30.000 entradas verificadas, EURUSD 2021-2026.

## Veredicto

**El R:R no rescata nada, y el placebo lo demuestra sin discusión.**

## La celda principal declarada · 12:1, horizonte 5 días

```
                   azar  acierto  umbral  exceso   razón  sin res.   NETA
  12:1            7,69%    8,07%  10,11%   +0,38   1,050     1,2%   -0,2028
  12:1 barajado   7,69%    7,83%  10,11%   +0,14   1,018     1,4%   -0,2116
```

Y a 20 días, donde la razón sube más:

```
  12:1            7,69%    8,62%  10,11%   +0,93   1,120     0,1%   -0,1892
  12:1 barajado   7,69%    8,61%  10,11%   +0,92   1,120     0,1%   -0,1883
```

**Idénticos hasta el tercer decimal.** Barajar la dirección al azar da
exactamente el mismo resultado que la señal. No hay nada que multiplicar.

## La fila completa, 5 días

```
   R:R      azar   acierto   umbral   razón      NETA        razón del PLACEBO
   2:1    33,33%    33,65%   43,82%   1,010    -0,3045           0,996
   3:1    25,00%    25,81%   32,86%   1,032    -0,2810           1,018
   5:1    16,67%    16,93%   21,91%   1,016    -0,2905           1,024
   8:1    11,11%    11,10%   14,61%   0,999    -0,2942           1,027
  12:1     7,69%     8,07%   10,11%   1,050    -0,2028           1,018
  20:1     4,76%     3,62%    6,26%   0,760    -0,2052           0,770
  30:1     3,23%     1,42%    4,24%   0,440    -0,2437           0,485
```

La neta es **negativa en las 21 celdas**, entre −0,19 y −0,30, sin una sola
excepción. Y la columna del placebo sigue a la de la señal como una sombra.

## Por qué, y es la lección entera del proyecto en una línea

La fórmula que abrió esta prueba:

```
  neta = ventaja × (1 + R:R) − coste/riesgo
```

Subir el R:R **multiplica la ventaja**. Pero la ventaja medida es **cero**, y
multiplicar cero por trece sigue dando cero. Mientras tanto el término
`coste/riesgo` **no depende del R:R en absoluto**: depende sólo del tamaño del
stop. Con 6,4 pips de stop son 22 céntimos por euro arriesgado, se busque 1:2
o 1:30.

El R:R es un multiplicador, no un generador. Sin ventaja no hay nada que
multiplicar. **Era la última palanca de mi propia fórmula que quedaba sin
probar, y queda cerrada.**

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. principal con neta > 0 y el IC limpio | **NO.** −0,2028 [−0,2440, −0,1616] |
| 2. placebo en el precio justo | **NO, y es peor**: el placebo **iguala** a la señal |
| 3. razón por encima de 1 coherente en la fila | **NO**: 1,010 · 1,032 · 1,016 · 0,999 · 1,050 · 0,760 · 0,440 |

## Récord de predicciones

Cuatro de cinco.

| predicción | resultado |
|---|---|
| el placebo saldrá en el precio justo | sale, y además iguala a la señal ✔ |
| la razón bajará al subir el R:R; a 12:1 entre 0,90 y 1,05 | 1,050 a 5 días ✔ (1,120 a 20, pero el placebo también) |
| la neta seguirá negativa a todos los R:R | las 21 celdas ✔ |
| sin resolver a 12:1 y 5 días: 20-40 % | **1,2 %** ✘ — muy por debajo |
| el criterio no se cumplirá | no se cumple ✔ |
