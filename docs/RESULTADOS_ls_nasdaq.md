# Las 4 confirmaciones (vídeo de liquidez) en el NASDAQ

El propio autor hace su demostración sobre el NASDAQ y dice que en índices usa
M3 para el disparo. Así se ha montado: **su activo, su temporalidad, sus
reglas**, sobre NSXUSD M1 de 2020 a 2026 (6,6 años, 2,2 millones de velas).

## Las reglas, tal como están en la transcripción

1. El precio elimina un nivel estructural: alto o bajo de la **sesión anterior**
   o del **día anterior**.
2. En **H4** ese barrido es un *liquidity sweep*: la mecha toma el nivel pero el
   cuerpo queda del otro lado. Si cierra con cuerpo más allá es un *liquidity
   run* y no hay operación.
3. Lo mismo en **H1**.
4. Vela **envolvente en M3** → entrada al cierre de esa vela.

Dirección: barrido de máximo, venta; barrido de mínimo, compra. Stop justo al
otro lado de la toma de liquidez. Objetivo **1:1 fijo**.

Sin mirar al futuro: en cada vela M3 solo se usan las velas H1/H4 acumuladas
hasta ese cierre, niveles de sesiones y días ya cerrados, y el desenlace se
resuelve vela a vela en M1 a partir del minuto siguiente.

## Resultado

| | operaciones | al año | acierto | R por operación | PF |
|---|---|---|---|---|---|
| día entero (como su backtest) | 2.971 | 452 | 49,04 % | **−0,0989** | 0,820 |
| solo aperturas Londres y NY | 1.173 | 178 | 48,08 % | **−0,0999** | 0,819 |
| disparo en M5 en vez de M3 | 2.097 | 319 | 49,31 % | **−0,0868** | 0,840 |

Negativo **los siete años**, sin una sola excepción:

```
2020  -0,1201    2021  -0,0922    2022  -0,0484    2023  -0,1618
2024  -0,0693    2025  -0,1078    2026  -0,1050
```

## Y esta vez el coste no es la explicación

Esto es lo importante y lo que separa este caso de todo lo anterior. **Con coste
cero la estrategia sigue perdiendo**: −0,0194 R por operación. Barridas las 23
variantes razonables —solo niveles del día, solo de sesión, sin exigir H4,
envolvente con cuerpo mínimo, cada ventana horaria, cada marco de disparo, cada
anclaje de la vela H4, objetivos de 0,5 a 3— **ninguna tiene ventaja bruta
distinguible de cero**, y 21 de las 23 tienen el punto en negativo:

```
tal cual                     -0,0194    apertura de Londres          +0,0305
solo día anterior            -0,0411    apertura de NY               -0,0632
solo sesión anterior         -0,0092    contado NY 09-11             -0,0389
sin exigir H4                -0,0275    disparo M1 / M5 / M15   -0,005 / -0,014 / -0,023
cuerpo >= 50 % / 70 %  -0,018 / -0,020  objetivo 1,5 / 2 / 3    -0,011 / -0,014 / +0,001
```

Ningún intervalo de confianza excluye el cero. Con 23 casillas probadas, una o
dos positivas por azar es exactamente lo que toca.

El coste solo remata: 1,5 puntos sobre un riesgo mediano de 25,1 puntos es un
**6,0 %**, y a 1:1 obliga a acertar el **52,99 %** de las veces. El acierto bruto
observado es 49,04 %.

## No es el activo

La misma estrategia, mismo motor, en EURUSD:

| | operaciones | acierto | R/op sin coste | R/op con coste |
|---|---|---|---|---|
| EURUSD | 1.237 | 50,04 % | +0,0010 | −0,1430 |
| NASDAQ | 2.971 | 49,04 % | −0,0194 | −0,0989 |

Los dos activos dan lo mismo: **cero bruto**. Cambiar de par no cambia nada
porque no había nada que cambiar de sitio.

## La semana del vídeo

En el vídeo enseña una semana con **7 aciertos de 8** y lo presenta como prueba.
Con el acierto real medido, 49,0 %, la probabilidad de que una semana de ocho
operaciones salga así o mejor es del **3,1 %**. En las 343 semanas del histórico
tocarían unas 11 semanas así por puro azar — y midiéndolas de verdad salen
**7 semanas** con 85 % de acierto o más. También salen **7 semanas igual de
malas**, con 15 % o menos. Esas no aparecen en ningún vídeo.

No hace falta suponer mala fe. Basta con grabar la semana que salió bien.

## Lo que se sentiría operándola

Peor racha: **11 pérdidas seguidas**. Hubo **27 rachas de 6 o más**. La caída
acumulada máxima es de 295 R, y el **98 % del tiempo** la cuenta está a más de
10 R por debajo de su máximo — que es donde salta el límite de una cuenta de
fondeo.

## Veredicto

Descartada, y esta vez sin matices ni condicionales: no es que la ventaja sea
demasiado pequeña para el coste, es que **no hay ventaja**.
