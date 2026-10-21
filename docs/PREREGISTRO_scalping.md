# Pre-registro · scalping en M1 y M5

Firmado **antes** de medir. Lo pide él explícitamente y con razón: una
estrategia que no va a ejecutar vale cero, y la de 5 días no la va a ejecutar.

## El problema declarado de antemano, con su número

El coste en R es `diferencial / stop`. Eso **no depende del horizonte**: depende
del ancho del stop. Y el scalping usa stops estrechos por definición.

```
  diferencial 0,7 pips (ECN)
    stop  5 pips  ->  coste = 14,0 % del riesgo
    stop  8 pips  ->  coste =  8,8 %
    stop 12 pips  ->  coste =  5,8 %
    stop 20 pips  ->  coste =  3,5 %
    stop 71 pips  ->  coste =  1,0 %   (la estrategia que no le gusta)
```

Umbral de acierto para no perder: `umbral = (1 + coste/riesgo) / (1 + R:R)`

```
            R:R 1:1   R:R 1:1,5   R:R 1:2
  stop  8p   54,4 %     43,5 %      36,3 %
  stop 12p   52,9 %     42,3 %      35,3 %
  stop 20p   51,8 %     41,4 %      34,5 %
```

**Con R:R 1:1 hace falta acertar el 52-54 %.** Con 1:2, el 34-36 %. Por eso el
test va a barrer el R:R: es la variable que decide si el coste es asumible.

## Las reglas congeladas

Siete montajes clásicos de scalping, en velas de **5 minutos**, con las salidas
resueltas **minuto a minuto** con el M1:

```
  1  cruce EMA 9/21 con EMA 50 a favor
  2  RSI(2) extremo (<5 compra, >95 venta)
  3  rotura del rango de las 3 primeras velas de Londres
  4  reversión a VWAP +-1 sigma
  5  fade de Bollinger (20, 2)
  6  momentum: 3 velas seguidas en la misma dirección
  7  barrido del máximo/mínimo de 12 velas y cierre dentro (CRT en M5)
```

Cada uno con:

```
  stop        8 · 12 · 20 pips
  R:R         1:1 · 1:1,5 · 1:2
  horizonte   120 minutos
  sesión      08:00-18:00 Madrid (Londres + Nueva York, el diferencial más fino)
  coste       0,7 pips ida y vuelta, y 1,4 como sensibilidad
  empates     resueltos como pérdida
```

**63 celdas.** Reparto 70 % ajuste / 30 % validación, por tiempo.

## El listón, declarado antes

Con 63 celdas, el máximo |z| esperado por puro azar es **≈ 2,65**. Una celda no
vale por ser positiva: tiene que **batir 2,65 dentro de muestra y seguir
positiva fuera**.

## Mi predicción

Que ninguna celda con R:R 1:1 sobreviva al coste, y que las de 1:2 queden en
cero, igual que todo lo demás medido a horizonte intradía. Si me equivoco,
mejor.

## Lo que entregaré pase lo que pase

Si algo valida: las reglas y el Pine. Si no valida: **la celda menos dañada por
el coste**, con su número honesto, porque la pidió y porque una estrategia que
ejecuta a esperanza cero es mejor que una que abandona. Pero con la cifra
delante, no escondida.
