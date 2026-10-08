# HOJA DE TRABAJO · la mejor estrategia que encuentro para EURUSD

Rellenada por mí, no por él. Preregistro sellado en `docs/PREREGISTRO_eurusd_final.md`
antes de medir. Código en `bt/eurusd_final.py`. Un solo pase.

---

## 1 · QUÉ ES

- **Nombre**: Rotura de canal simétrica con stop ancho
- **De dónde sale**: de descartar todo lo demás. Es la única familia que salió
  con signo correcto y consistente en el pase de swing (positiva en 6 de 7
  plazos), combinada con la corrección que él mismo señaló: **stop ancho**,
  donde el coste pasa del 13-27 % al 1-3 % del riesgo.
- **¿Generador automático?** No. Elegida por eliminación sobre lo medido.

## 2 · MERCADO

- **Instrumento**: EURUSD
- **Temporalidad**: H1 y H4 (las dos medidas)
- **Dirección**: **las dos**. Y esto es una decisión, no un detalle: la
  estrategia del oro aplicada a EURUSD dio **-83,7 %, t -3,31**, porque era
  solo largos. Una divisa no tiene prima de riesgo: es un precio relativo.
- **Horario**: sin restricción (EURUSD es líquido 24 h en semana)
- **Días excluidos**: ninguno
- **Posiciones simultáneas**: 1
- **Con posición abierta, ¿se generan señales?** No

## 3 · ENTRADA

- **Filtro previo**: NINGUNO. Deliberado: cada filtro añadido es una
  comparación más, y este proyecto entero trata de eso. Además, el control de
  vecindario en el oro demostró que el filtro "inteligente" (GannHiLo) no
  aportaba nada.
- **Disparo**: rotura del canal de N velas cerradas
  - compra: orden stop en el **máximo** de las últimas N velas
  - venta: orden stop en el **mínimo** de las últimas N velas
- **Tipo de orden**: stop
- **Validez**: M velas, y se recalcula
- **¿En qué vela se evalúa?** En la vela N ya **cerrada**. La orden vive de la
  vela N+1 en adelante. Sin excepción.

## 4 · SALIDA

- **Stop loss**: k × ATR(N), fijado en el momento de la entrada
- **¿Se mueve?** No. Nunca.
- **Take profit**: no hay
- **Salida por tiempo**: a las M velas
- **Trailing / break-even / parciales / señal contraria**: no hay
- **Empate stop y salida en la misma vela**: resuelto **minuto a minuto**
  sobre el M1 real. Manda lo que ocurra antes en el tiempo.

## 5 · RIESGO Y TAMAÑO

- **Capital inicial**: 100.000 €
- **Riesgo por operación**: 1 %, compuesto sobre el capital del momento
- **Tamaño**: sale de la distancia al stop

## 6 · COSTES

- **Spread**: 0,7-1,0 pips (medido en su cuenta el 28-08-2026)
- **Comisión**: 5 €/lote ida y vuelta = 0,58 pips
- **Total aplicado**: **1,43 pips** por operación completa
- **Fuente**: `docs/COSTE_real.md`, dato suyo, no estimación mía

## 7 · PERIODO Y REJILLA

- **Datos**: 2.397.463 minutos, 2020-01-01 → 2026-07-31
- **Ajuste**: 2020-2023 · **Comprobación**: 2024-2026, sin tocar hasta el final
- **Rejilla**: N ∈ {20,40,60,100} · k ∈ {1,2,3} · M ∈ {5,10,20,40} × 2
  temporalidades = **96 celdas**

## 8 · EL RESULTADO

Las 8 mejores del ajuste, y lo que hicieron después:

     tf    N    k    M | n aj  PF aj   t aj | n fu  PF fu   t fu   ret fu
    240   60  3.0    5 |  333  1.108  +0.71 |  190  0.768  -1.44   -10.4 %
     60   20  3.0   40 |  488  1.076  +0.66 |  330  1.022  +0.15    +4.6 %
    240  100  3.0    5 |  266  1.114  +0.66 |  140  1.099  +0.44    +3.0 %
    240  100  2.0    5 |  266  1.110  +0.65 |  140  1.025  +0.12    +1.2 %
    240  100  1.0    5 |  266  1.070  +0.44 |  140  1.023  +0.11    +1.9 %
    240   60  2.0    5 |  333  1.055  +0.38 |  190  0.767  -1.50   -14.7 %
    240   60  2.0   10 |  239  1.034  +0.21 |  136  0.851  -0.77    -9.0 %
     60   20  2.0   40 |  488  1.016  +0.14 |  330  0.880  -0.89   -27.5 %

## 9 · LOS CONTROLES · y los cinco criterios firmados

    1  PF fuera de muestra > 1,10          0,768        FALLA
    2  bate a las entradas al azar         0,970 vs 1,023 (mejor azar)   FALLA
    3  >60 % de vecinos positivos fuera      8 %        FALLA
    4  bate a los 5 nulos                  0,970 vs 0,848 (peor nulo)    PASA
    5  correlación ajuste/fuera > +0,30    +0,583       PASA

Detalle de los controles 2 y 4:

    entradas al azar   PF medio 0,908   rango 0,831 a 1,023
    nulos permutados   PF medio 0,765   rango 0,694 a 0,848
    la estrategia      PF 0,970

## 10 · VEREDICTO

**DESCARTADA.** Falla 3 de los 5 criterios que firmé antes de mirar.

Y falló justo al revés de lo que predije. Escribí: *"espero que falle el
criterio 5"*. **El 5 lo pasa, y bien: +0,583.** La elección de parámetros SÍ
transfiere de 2020-2023 a 2024-2026 — es la primera señal de todo el proyecto
que generaliza su ordenación.

Lo que no transfiere es el **nivel**. Las mismas celdas que daban PF 1,108 en
el ajuste dan 0,768 después. El orden se mantiene; la rentabilidad, no.

## Lo que este resultado sí demuestra, y no es cero

La estrategia bate a los nulos (0,970 contra un máximo de 0,848). Es decir:
**romper un canal en EURUSD real funciona mejor que hacerlo sobre EURUSD
barajado.** Hay estructura de verdad ahí debajo.

Pero no bate a entrar al azar con la misma geometría (0,970 contra 1,023). O
sea: esa estructura es **más pequeña que los 1,43 pips que cuesta operarla.**

Es, otra vez, exactamente el mismo muro:

    hay senal     ->  la hay, y se mide: bate al ruido
    hay ventaja   ->  no, porque el coste es mayor que la senal

## Qué haría yo ahora, y qué no

**No** seguiría buscando en EURUSD con datos de precio. Cinco familias
distintas, 675 + 96 + 225 celdas, un modelo de árboles con 50 variables y
133.834 observaciones fuera de muestra: todas dan lo mismo por caminos
independientes. Eso ya no es mala suerte, es una medición.

**Sí** haría estas dos cosas, por este orden:

1. **Medir su spread real del XAUUSD.** La única estrategia que ha superado
   todos sus controles internos en dos meses es la del oro, y su punto de
   equilibrio es un número concreto: 0,52 $. Media hora de trabajo decide si
   existe o no.

2. **Si va a un reto, usar la geometría, no una señal.** 36,9 % fuera de
   muestra, que es el techo de azar. Y está demostrado -en
   `docs/RESULTADOS_swing_eurusd.md`- que una ventaja real de Sharpe 0,5 pasa
   MENOS (28,4 %), porque el reto premia la varianza, no la ventaja.
