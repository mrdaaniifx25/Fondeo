# Barrido de niveles de día previo + fibonacci en M5

Su idea: *«marcar en H1 el alto y el bajo de los días anteriores, esperar un
liquidity sweep —que barra el alto y la vela cierre por debajo del rango—, tirar
el fibonacci en M5, esperar el retroceso a la zona de descuento y hacer la entrada
hasta el próximo alto»*.

Montada en las dos direcciones espejo: barrido de un alto → corto al premium con
objetivo el siguiente nivel por debajo; barrido de un bajo → largo al descuento
con objetivo el siguiente nivel por arriba. Siete instrumentos, 2020-2026.

## Dos miradas al futuro encontradas y corregidas

**La primera pasada daba bruto +0,07 a +0,11 y acierto del 64-67 %.** Sonaba
demasiado bien, y lo era. Dos fallos míos:

1. **El fibo y el disparo, en la misma vela.** Usaba el mínimo de una vela de M5
   para calcular el nivel del retroceso y el máximo de *esa misma vela* para
   disparar la entrada. Dentro de esos cinco minutos no se sabe qué pasó primero.
2. **La resolución empezaba antes del relleno.** El sello de tiempo de la entrada
   es la *apertura* de la vela de M5; contaba TP y SL desde el minuto siguiente,
   o sea desde minutos que podían ser anteriores al relleno real.

## Lo que queda al arreglarlos

| fibo | objetivo | acierto | R bruta | R neta | celdas netas positivas |
|---|---|---|---|---|---|
| 0,500 | 1:2 | 32,3 % | +0,010 | −0,067 | 0 de 7 |
| 0,618 | 1:2 | 32,8 % | +0,007 | −0,089 | 0 de 7 |
| 0,705 | 1:2 | 32,8 % | −0,002 | −0,121 | 0 de 7 |
| 0,790 | 1:2 | 32,9 % | −0,005 | −0,160 | 0 de 7 |
| 0,500 | al nivel | 61,7 % | −0,021 | −0,099 | 0 de 7 |
| 0,618 | al nivel | 60,1 % | −0,031 | −0,129 | 0 de 7 |
| 0,705 | al nivel | 58,3 % | −0,038 | −0,158 | 0 de 7 |
| 0,790 | al nivel | 55,6 % | −0,051 | −0,206 | 0 de 7 |

**Cero de 56 celdas con R neta positiva. Y el bruto también en cero.**

Antes y después del arreglo, en la celda que mejor pintaba:

```
  fibo 0,790 al nivel      acierto    R bruta    R neta
  con los dos fallos        63,5 %     +0,058    -0,097   (1 celda neta positiva)
  corregido                 55,6 %     -0,051    -0,206   (0 celdas)
```

**Todo el hallazgo era mi código.** El objetivo 1:2 no se movió con el arreglo
—32,3 % a 32,9 %, la geometría— porque ese sesgo pegaba sobre todo al objetivo
adaptativo.

## Octava familia, mismo sitio

Con objetivo 1:2 el acierto cae entre 31,8 % y 33,9 % en los siete instrumentos y
el bruto medio es +0,010, +0,007, −0,002 y −0,005 según el fibo. Cero.

Es lo que predice `RESULTADOS_hay_patron.md`: correlación direccional 0,000 sobre
2,4 millones de minutos. Ninguna regla de «entro aquí, objetivo 1:k» sale de
1/(1+k), y da igual que el nivel sea un alto de ayer, un order block, una
trendline o el cuerpo de una vela.

## El 60 % que pedía, y por qué no sirve

El objetivo «al nivel más cercano» da entre 53,4 % y 57,8 %, y en la versión con
los fallos daba 64 %. **Ese winrate no viene de acertar más: viene de que el
objetivo está más cerca del stop.** El ratio medio ronda 1:0,7, cuyo winrate
gratis es el 59 %. Sacar 55,6 % es estar *por debajo* de la geometría.

## Reproducir

`python3 bt/barrido_dia_fibo.py` · salida en `data/barrido_dia_fibo_salida.txt`
