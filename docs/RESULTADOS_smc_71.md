# La estrategia del 71 % · lo mejor medido en todo el proyecto

Reglas de un vídeo en inglés, transcritas por él. **Es la especificación más
precisa que me han dado**: cuatro casillas, todas mecánicas, sin ninguna
subjetividad.

```
  1 SESGO H4    rango de las últimas 20 velas de H4. Por encima del 50 % =
                premium -> solo ventas. Por debajo -> solo compras.
  2 BARRIDO     una vela de M15 pincha con la MECHA el fractal previo más
                reciente y CIERRA de vuelta dentro.
  3 BOS + FVG   después, un cierre de cuerpo rompe el fractal contrario más
                reciente, y dentro de esa pierna hay un hueco de tres velas.
  4 FIBO 71 %   fibo del extremo barrido (100 %) al extremo del BOS (0 %).
                ENTRADA limitada al 71 % · STOP al 100 % · OBJETIVO al 0 %
```

Su aritmética es correcta: riesgo 29 %, beneficio 71 %, **R:R = 2,45**. El azar
geométrico ahí es **29,0 %**, no el 33,3 % de un 1:2.

## El resultado

| instrumento | n | acierto | R bruta | **R NETA** | stop | coste/R |
|---|---|---|---|---|---|---|
| EURUSD | 204 | 30,9 % | +0,065 | −0,229 | 5,7 p | 25,0 % |
| GBPUSD | 195 | 29,7 % | +0,026 | −0,234 | 7,0 p | 23,0 % |
| **USDJPY** | 195 | 36,4 % | +0,256 | **+0,014** | 8,0 p | 18,8 % |
| XAUUSD | 82 | 24,4 % | −0,159 | −0,236 | 3,07 $ | 6,5 % |
| **GRXEUR** | 63 | **42,9 %** | +0,478 | **+0,357** | 15,5 pt | 9,7 % |
| **NSXUSD** | 206 | 32,5 % | +0,122 | **+0,030** | 21,0 pt | 7,2 % |
| **SPXUSD** | 166 | 33,7 % | +0,163 | **+0,041** | 5,3 pt | 9,5 % |

```
  1.111 operaciones · acierto 32,6 % contra el 29,0 % del azar · z +2,63 · p = 0,0042
  R bruta +0,124 (z +2,55)   ·   positiva en 6 de 7
  R NETA  -0,066 (z -1,37)   ·   POSITIVA EN 4 DE 7
```

**Es la primera vez en todo el proyecto que una regla mecánica tiene R neta
positiva en algún instrumento.** Y lo tiene en cuatro.

## Aguanta el corte por épocas

| | n | acierto | R bruta | z |
|---|---|---|---|---|
| 2020-2022 | 431 | 32,7 % | +0,128 | +1,64 |
| 2023-2026 | 680 | 32,5 % | +0,121 | +1,95 |

Prácticamente idéntico. Y por instrumento, 10 de 12 celdas época×instrumento
salen positivas.

## Qué aporta cada casilla

Sobre los mismos cuatro instrumentos:

| | R bruta |
|---|---|
| completa | +0,117 |
| **sin el filtro premium/discount de H4** | **+0,071** |
| sin exigir el hueco de tres velas (FVG) | +0,151 |

**El filtro de H4 casi dobla la ventaja.** El del hueco de tres velas la baja
ligeramente: exigirlo quita operaciones buenas.

## Lo que sigue faltando

La neta media es **−0,066**. Donde funciona es donde el coste pesa poco:

```
  coste/R < 10 %   ->  GRXEUR +0,357 · SPXUSD +0,041 · NSXUSD +0,030
  coste/R > 18 %   ->  USDJPY +0,014 · EURUSD -0,229 · GBPUSD -0,234
```

En EURUSD, con stops de 5,7 pips, el coste vale el 25 % del riesgo y se lleva
una ventaja bruta de +0,065. **En índices, con el mismo criterio, sobra.**

## Advertencias, que son varias

1. **Es exploratorio.** No hay preregistro. La hipótesis viene de fuera —lo cual
   es mucho mejor que si la hubiera encontrado yo barriendo— pero el pase no está
   declarado de antemano.
2. **Las muestras son pequeñas**: 63 a 206 por instrumento. Ninguna z individual
   pasa de +2,20.
3. **Los costes de los seis no-EURUSD son estimaciones mías**, no medidas. Si el
   real del DAX o del S&P es el doble, tres de los cuatro positivos se caen.
4. **Mi implementación es una interpretación.** «Fractal más reciente», «rango de
   H4 de 20 velas», «vida de 96 horas»: él no da esos números y los he elegido yo.

## El siguiente paso, y es obvio

**Un preregistro y un pase limpio**, exactamente como con el fibo de H1. Reservar
instrumentos o épocas, firmar el umbral antes, y correr una vez.

## Reproducir

`python3 bt/smc_71.py` · ablaciones con `FVG=no`, `H4=no`
