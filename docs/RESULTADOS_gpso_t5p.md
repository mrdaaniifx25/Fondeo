# Resultados · la estrategia pública de GPSO Trader (Trading en 5 Pasos)

Especificación reconstruida por él a partir del material público, y probada tal
cual. **No he ajustado ni un parámetro**: la regla viene de fuera, así que un solo
pase sobre todos los datos es legítimo y no hace falta reservar muestra.

```
  1  NIVELES   en H1: máximo y mínimo del día anterior, y de los días previos
  2  CONTACTO  el precio tiene que llegar al nivel
  3  CIERRE    se espera al cierre de la vela de H1 que reacciona
  4  DIRECCIÓN cierre POR ENCIMA del nivel -> compra
               cierre POR DEBAJO del nivel -> venta
  5  ENTRADA   al cierre de esa H1
  6  STOP      detrás del pico de reacción (el extremo de esa vela)
  7  OBJETIVO  2R
```

## El resultado, sobre 66.408 operaciones y siete instrumentos

| instrumento | n | acierto | R bruta | z bruta | **R NETA** | stop | coste/R |
|---|---|---|---|---|---|---|---|
| EURUSD | 11.458 | 32,8 % | +0,009 | +0,69 | **−0,179** | 12,0 p | 11,9 % |
| GBPUSD | 11.815 | 32,0 % | −0,021 | −1,65 | **−0,180** | 15,4 p | 10,4 % |
| USDJPY | 11.023 | 32,8 % | +0,008 | +0,63 | **−0,132** | 16,9 p | 8,9 % |
| XAUUSD | 4.704 | 34,1 % | +0,044 | +2,18 | **−0,014** | 5,80 $ | 3,4 % |
| GRXEUR | 4.780 | 33,0 % | +0,019 | +0,95 | **−0,068** | 30,6 pt | 4,9 % |
| NSXUSD | 11.109 | 32,4 % | +0,001 | +0,09 | **−0,051** | 47,3 pt | 3,2 % |
| SPXUSD | 11.519 | 33,8 % | +0,040 | +3,10 | **−0,043** | 10,2 pt | 4,9 % |

**Los siete juntos:**

```
  acierto  32,85 %   contra el 33,33 % geométrico   ->  -0,48 puntos  (z -2,54)
  R bruta  +0,0107
  R NETA   -0,1067
  neta positiva en 0 de 7
```

**No hay ventaja.** El acierto queda medio punto *por debajo* de la geometría pura.

Y no depende de cómo se lea la parte ambigua del enunciado —«detrás del pico de
reacción»—. Con colchón, sin colchón, con más o menos vida, con dos días de
niveles en vez de cinco:

| variante | acierto medio | R bruta media |
|---|---|---|
| base (colchón 0, vida 48 h, 5 días) | 33,0 % | +0,014 |
| colchón 0,25 del rango de la vela | 31,9 % | −0,003 |
| colchón 0,50 | 31,5 % | +0,003 |
| vida 24 h | 32,0 % | +0,001 |
| vida 168 h | 33,2 % | +0,001 |
| solo 2 días de niveles | 32,7 % | +0,006 |

Seis lecturas, seis veces la geometría.

## Estable en el tiempo y sin sesgo de dirección

| | n | acierto | R bruta | R neta |
|---|---|---|---|---|
| 2020-2022 | 25.588 | 32,8 % | +0,010 | −0,114 |
| 2023-2026 | 40.820 | 32,9 % | +0,011 | −0,102 |

| | n | acierto | R bruta |
|---|---|---|---|
| compras | 33.736 | 33,4 % | +0,032 |
| ventas | 32.672 | 32,2 % | −0,011 |

Nada. Es la misma constante otra vez.

## Comparación con lo del fibo en H1

Vale la pena ponerlas juntas, porque son parientes:

| | acierto | R bruta | pasó un preregistro |
|---|---|---|---|
| GPSO T5P, entrada al cierre de H1 | 32,85 % | +0,011 | **no** |
| Fibo en H1 con stop pegado al extremo | 34,5 % | +0,043-0,058 | **sí** |

La diferencia entre las dos es **dónde va el stop y cuándo se entra**. La versión
que espera el retroceso y pone el stop pegado al extremo barrido tiene un efecto
pequeño y real; la que entra al cierre con el stop al otro lado de la vela entera
no tiene ninguno. Encaja con lo ya medido: el efecto es de *colocación del stop*,
no de dirección.

## Reproducir

`python3 bt/gpso_t5p.py` · variantes con `COL=`, `VIDA=`, `NDIAS=`
