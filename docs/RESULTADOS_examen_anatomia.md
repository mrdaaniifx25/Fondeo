# Los 23 momentos, abiertos

**Exploratorio.** 23 casos, una docena de variables: algo tenía que salir. Nada
de aquí es un hallazgo. Son hipótesis para el segundo bloque.

## Lo que sí separa sus momentos de los de la regla

| | él | la regla | |
|---|---|---|---|
| **desvanece la ruptura** | **13 de 23 (57 %)** | 5 de 33 (15 %) | **Fisher p = 0,0016** |
| entra dentro del rango de Asia | 17 de 23 (74 %) | 14 de 33 (42 %) | |
| hora mediana | 08:32 | 09:05 | t −1,67 |
| posición en el rango de Asia | 52 % | 97 % | t −1,10 |
| distancia al nivel | 4,9 p | 1,3 p | t +3,45 |

**La diferencia de fondo es una sola y es limpia: juegan a cosas opuestas.**

La regla que llevo dos meses midiendo compra la ruptura del alto y vende la del
mínimo — sigue el movimiento en 28 de 33. Él lo **desvanece** en 13 de 23: vende
cerca del alto y compra cerca del mínimo, volviendo hacia dentro del rango.

Con p = 0,0016 sobre 56 observaciones, esa diferencia no es casualidad. **No es
que él filtre mejor las señales de la regla: es que no son sus señales.**

## Lo que NO he encontrado, y es lo que buscaba

**Dentro de sus 23, desvanecer no gana más que seguir:**

```
desvanece   n=13   acierto 61,5 %   R media +0,846
sigue       n=10   acierto 60,0 %   R media +0,635
                                    Fisher p = 1,000
```

Y **ninguna** de las nueve variables separa sus ganadoras de sus perdedoras:
todas con |t| < 1,5. Con 14 contra 9 no hay potencia para encontrarlo aunque
existiera.

Así que la anatomía explica **por qué los backtests medían otra cosa**, y no
explica **de dónde sale el 59 %**. Son dos preguntas distintas y solo he
contestado la primera.

## Una advertencia sobre la distancia al nivel

`dist_nivel` sale con t +3,45, la más fuerte de la tabla, y **es en parte
artefacto mío**: la regla exige que la vela de M5 *toque* el nivel, así que su
distancia es pequeña por construcción. Que él entre más lejos es real, pero el
tamaño de la diferencia no se puede leer como un descubrimiento sobre él.

La diferencia de desvanecer contra seguir **no tiene ese problema**: ninguna de
las dos definiciones fuerza el signo.

## Sus 23, una a una

```
  s   hora    lado  nivel   dist    pos    qué hace   stop      R
  1  08:07   venta   alto   1.7p    83%   desvanece   2.4p  +2.00
  1  08:40   venta   bajo   3.2p    31%       sigue   2.9p  +2.00
  1  09:22  compra   bajo   3.7p   -36%   desvanece   4.6p  +2.00
  2  08:10  compra   alto   4.6p   105%       sigue  11.8p  +2.00
  2  09:30   venta   alto  26.5p   127%   desvanece  12.2p  +2.00
  3  09:30   venta   alto   1.8p    91%   desvanece   9.1p  -1.00
  4  10:30   venta   alto   8.5p    73%   desvanece   9.8p  +2.00
  5  08:40  compra   alto   9.1p    63%       sigue   4.3p  -1.00
  6  08:32   venta   bajo   9.1p    40%       sigue   5.1p  +2.00
  6  09:35  compra   bajo   1.3p     6%   desvanece   7.2p  -1.00
  7  08:29  compra   bajo   0.7p    -3%   desvanece   5.5p  +2.00
  7  09:50  compra   bajo  12.1p    49%   desvanece   5.8p  -1.00
  8  08:09  compra   bajo   4.1p    18%   desvanece   7.4p  -1.00
  8  09:13  compra   alto  10.6p    54%       sigue   4.5p  -1.00
  9  08:25  compra   bajo  12.6p    41%   desvanece   8.7p  -1.00
 10  08:25   venta   alto   5.4p    83%   desvanece   8.0p  +2.00
 10  11:21   venta   bajo   8.2p    26%       sigue   3.7p  +0.35
 13  08:26   venta   alto   4.4p    79%   desvanece   4.9p  +2.00
 14  08:02  compra   alto   2.3p   123%       sigue   3.5p  +2.00
 16  08:16   venta   bajo   8.5p    44%       sigue   4.2p  -1.00
 17  08:42  compra   alto   4.9p   110%       sigue   7.1p  -1.00
 18  08:18  compra   alto  13.7p    52%       sigue   6.8p  +2.00
 19  08:16  compra   bajo   2.6p     6%   desvanece  10.9p  +2.00
```

`pos` es dónde está el precio dentro del rango de Asia: 0 % el mínimo, 100 % el
alto, y fuera de esa horquilla cuando el precio ya se ha salido.

## Reproducir

`python3 bt/examen_anatomia.py` · datos en `data/examen_anatomia.csv`
