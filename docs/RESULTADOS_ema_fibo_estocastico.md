# Resultado · EMA + Fibonacci + estocástico

Sale de una captura de Instagram (`tradinglab.es`, "trade destacado"): retroceso
de Fibonacci, media móvil y un oscilador en el subpanel. Código en
`bt/ema_fibo_estocastico.py`, `bt/ema_fibo_esto_partido.py`,
`bt/ema_fibo_esto_auditoria.py` y `bt/ema_fibo_esto_instrumentos.py`.

EMA+Fibo solo ya estaba muerto (`RESULTADOS_ema_fibo.md`: 225 celdas, ninguna
con z > 2, por debajo de datos barajados). Aquí se le añade el estocástico
(14,3,3) leído en la **última vela cerrada antes de que se llene la orden
limitada**, que es causal y operable.

## 1 · Lo que hizo saltar la alarma

    filtro          celdas   R neta media   mejor z   z>2
    K<=20/>=80         225       -0,3564     +4,46     8
    K<=30/>=70         225       -0,3743     +3,21     2
    cruce K>D          225       -0,3115     +1,48     0
    sin filtro         225       -0,3248     -1,87     0

    mejor celda: H4 · EMA 20 · fibo 0,786 · R:R 2 · sobreventa
                 779 operaciones, R neta +0,2386, z +4,46

    5 rejillas sobre datos barajados: mejor z -0,49 a +1,96 (media +0,81)
    cero celdas de nulo por encima de z=2, contra ocho reales

**Por primera vez en el proyecto, lo real se separaba de los nulos.**

## 2 · La auditoría del filtro

El filtro solo QUITA operaciones, así que se compara su subconjunto contra
4.000 subconjuntos **al azar** del mismo tamaño sacados de las mismas
operaciones:

    todas las operaciones de la celda   3397   R neta -0,1320   z -5,46
    las que elige el estocástico         779   R neta +0,2386   z +4,46
    las que descarta                    2618   R neta -0,2423   z -9,10

    subconjuntos al azar de 779: media -0,1315, desviación 0,0433
    el estocástico está a +8,55 desviaciones   ·   p < 0,0001

No es un subconjunto cualquiera. Pero **el efecto se evapora al alejar la
lectura una sola vela**:

    velas antes del llenado    1        2        3        4
    R neta                 +0,2386  +0,0618  -0,0508  -0,0995
    z                       +4,46    +1,05    -0,78    -1,46

Eso identifica el mecanismo: el filtro distingue si el precio **llegó
despacio** al nivel o si **se lo llevó por delante de golpe**. Una vela
violenta que atraviesa el nivel suele seguir y salta el stop, que está justo
debajo. Es real y es causal, pero es un efecto de una vela, no una estrategia
de Fibonacci.

## 3 · El corte temporal, al revés de lo habitual

    tf  ema    fib   rr       filtro |  DENTRO 2020-2023  |  FUERA 2024-2026
   240   20  0,382  1,0   K<=30/>=70 |  +0,0475   +0,81   |  +0,0417   +0,53   <- la elegida
   240   20  0,786  2,0   K<=20/>=80 |  +0,0524   +0,75   |  +0,4730   +5,80
   240   10  0,786  2,0   K<=20/>=80 |  +0,0533   +0,76   |  +0,3877   +4,56

La celda elegida **sin mirar el futuro** da +0,0417 con z +0,53: nada. Y la
familia 0,705-0,786 es floja dentro y fortísima fuera, que es lo contrario del
sobreajuste — no se puede ajustar a un periodo que no miraste.

Eso dejaba el asunto abierto. Lo resuelve el paso siguiente.

## 4 · La prueba que lo cierra: los parámetros congelados en otros instrumentos

Las 12 celdas de esa familia, **sin tocar un solo parámetro**, aplicadas a
GBPUSD y USDJPY, que no intervinieron en ninguna elección:

               |     n  2020-2023      z |     n  2024-2026      z
        EURUSD |  4999    +0,0163  +0,80 |  3689    +0,2394  +9,67
        GBPUSD |  5455    +0,0272  +1,37 |  3881    -0,2196  -9,98
        USDJPY |  4970    -0,0378  -1,87 |  3531    +0,1935  +7,58

**En el mismo periodo, dos instrumentos dicen +9,67 y +7,58 y el tercero dice
−9,98.** Un efecto de mercado no cambia de signo con esa contundencia entre
pares de divisas a la vez.

Y por años, los tres juntos:

    2020 +0,1354 (z  +5,52)      2024 -0,1966 (z  -9,28)
    2021 +0,0059 (z  +0,26)      2025 +0,2420 (z +11,28)
    2022 -0,2871 (z -14,19)      2026 +0,1679 (z  +4,84)
    2023 +0,1956 (z  +7,66)

Años con z −14,19 y años con z +11,28. Eso no es una ventaja: es una cantidad
que depende del régimen y que promedia a nada.

## 5 · Y por eso el z era mentira

El `z` de todas las tablas anteriores trata **cada operación como
independiente**. No lo son: dentro de un régimen están correlacionadas, y aquí
el régimen manda.

    z ingenuo (n = 26.525)                          +3,18
    z agrupado por año-instrumento (21 bloques)     +0,41
    z sobre las 7 medias anuales                    +0,48

    media anual +0,0376   ·   desviación entre años 0,2060
    la variación de un año a otro es 5 veces la media

**+0,41.** Cero.

## Veredicto

El estocástico **sí** informa: separa las entradas en las que el precio llega
despacio de aquellas en las que llega de golpe, y eso es un efecto real,
causal y medible (p < 0,0001 contra subconjuntos al azar).

Pero dura una vela, cambia de signo entre instrumentos en el mismo periodo, y
alterna entre años con z de −14 y +11. Agrupando correctamente, la ventaja es
**+0,41 desviaciones**: nada.

Lo que la captura de Instagram enseña —EMA y Fibonacci— aporta cero: la celda
completa sin filtro rinde **−0,1320 con z −5,46**. Todo el movimiento venía del
oscilador, y el oscilador no sobrevive a que le cambien el instrumento.

### La lección de método

Esta fue la medición que más cerca estuvo de colar. Pasó los nulos (5 de 5),
pasó una auditoría de subconjuntos al azar (+8,55 desviaciones) y salió
reforzada del corte temporal. Lo que la tumbó fueron dos cosas que no son
estadística fina sino sentido común:

1. **aplicarla a instrumentos que no habían opinado**, y
2. **contar los grados de libertad de verdad** — 7 años, no 26.525 operaciones.


---

# Ampliación · ¿en algún par? ¿y si era un RSI?

Dos preguntas del usuario: si funcionaba en algún par, y si el oscilador de la
captura podía ser un RSI en vez de un estocástico. Código en
`bt/ema_fibo_osciladores.py`. Todo con **z agrupado por año desde el
principio**, que es la lección de arriba.

Criterio declarado antes de mirar: para contar, algo tiene que dar z agrupado
> 2 en un par **y** no ser negativo en los otros. Un efecto que cambia de signo
entre pares no es un efecto.

## Los tres pares de divisas

    filtro                    EURUSD    GBPUSD    USDJPY   LOS TRES
    sin filtro                 -3,75     -5,03     -4,08      -8,04
    estocastico <=20/>=80      -0,08     -0,96     +0,22      -0,37
    RSI <=30/>=70              +1,97     +0,84     +1,43      +2,21
    RSI <=40/>=60              +0,92     -0,72     +0,44      +0,39

**El estocástico está muerto en los tres.** El usuario tenía razón en dudar de
la identificación.

**El RSI 30/70 sale positivo en los tres a la vez**, dentro y fuera de muestra
(+1,28 / +1,99) y en 6 de 7 años. Es lo único del proyecto que no cambia de
signo entre pares. Pero son **127 entradas distintas en total** —unas 6,5 al
año por par— y es 1 de 4 filtros probados, así que +2,21 no pasa una corrección
por comparaciones múltiples.

## La prueba que lo cierra

Los mismos filtros, sin tocar nada, en **cuatro instrumentos que no han
intervenido en ninguna elección**:

    filtro                    NAS100    SPX500     GER40    XAUUSD   LOS CUATRO
    sin filtro                 -4,92     -4,41     -1,73     -6,96       -11,21
    estocastico <=20/>=80      +0,64     -0,50     +1,24     -3,75        -1,78
    RSI <=30/>=70              -0,47     +1,15     +1,86     -0,89        +0,55
    RSI <=40/>=60              -0,13     -0,15     +4,36     -4,26        -0,50

    RSI 30/70 donde se encontro (3 pares FX)   +0,3086   z +2,21
    RSI 30/70 en los 4 que NO participaron     +0,0861   z +0,55

**No replica.** Dos positivos y dos negativos, y el conjunto en +0,55.

## Los siete instrumentos juntos

    filtro                         n    R neta       z   instrumentos +
    RSI <=30/>=70              16324   +0,1840   +1,50          5/7
    RSI <=40/>=60             116968   -0,0021   -0,03          3/7
    estocastico <=20/>=80     162167   -0,0571   -1,14          3/7
    sin filtro                998367   -0,1577  -10,29          0/7

## Veredicto de la ampliación

- **EMA + Fibonacci sin oscilador: negativo en los siete instrumentos**, z
  −10,29. La entrada en el retroceso es una mala operación, punto.
- **Estocástico: muerto**, −1,14 sobre los siete.
- **RSI 30/70**: lo mejor que ha aparecido, +1,50 sobre los siete y positivo en
  5 de 7 — pero **el número honesto es el de los instrumentos que no lo
  eligieron, y ahí es +0,55.**

Ninguna mezcla de EMA, Fibonacci y oscilador supera a su propio control.
