# Preregistro · EMA + Fibonacci en EURUSD, y qué produce buscar

Sellado mientras la rejilla corre, ANTES de ver ningún resultado.
Código en `bt/ema_fibo.py`.

## Por qué esto se hace así y no simplemente buscando

Él pregunta, con razón: *"¿por qué no buscas para EURUSD con EMA de 20 y fibo,
por ejemplo?"*. Parte ya estaba hecho (`bt/ema_rsi.py` con EMA50+RSI14, y el
fibo en `crt_fib`, `sweep_fibo`, `verifica_fib` y el 71 % de SMC-71), pero la
rejilla completa EMA x Fibo en EURUSD no.

El problema de "probar combinaciones hasta que una salga" tiene nombre y tiene
número. Con 225 celdas, la mejor **por puro azar** ya sale grande. Este
proyecto ya lo midió una vez: con 65 celdas, `P(alguna con z >= 3,01) = 15,6 %`.

Así que la rejilla se corre **dos veces**:

    REAL   EURUSD tal cual, 225 celdas
    NULO   EURUSD remuestreado por bloques de 60 minutos, 225 celdas, x10

El nulo conserva la volatilidad y el agrupamiento de volatilidad, y destruye
cualquier patrón de más de una hora — que es exactamente lo que una EMA de 20
en H4 con un fibo pretende explotar. **Si en el nulo aparecen celdas igual de
buenas, es que buscar produce eso, no que el patrón exista.**

## La rejilla

    temporalidad   M15 · H1 · H4
    EMA            10 · 20 · 50 · 100 · 200
    fibo           38,2 % · 50 % · 61,8 % · 70,5 % · 78,6 %
    R:R            1 · 2 · 3
                   = 225 celdas

    tendencia   cierre por encima/debajo de la EMA -> solo compras/ventas
    impulso     última pierna confirmada por fractales de Williams, causal
    entrada     orden limitada en el retroceso de fibo de esa pierna
    stop        en el origen de la pierna (el 100 % del fibo)
    vida        96 velas
    coste       1,43 pips, el medido en `docs/COSTE_real.md`
    empate en la misma vela -> se asume el stop

## El criterio, firmado antes de mirar

**El umbral no es un z fijo. Es la distribución del mejor z de los diez
nulos.** Para declarar que EMA+Fibo tiene algo, la mejor celda real tiene que
superar al **mejor de los diez mejores nulos**, no a un 2 ni a un 3.

## Las tres predicciones firmadas

1. **La mejor celda real tendrá z entre +2 y +4.** Siempre lo tiene: es lo que
   produce una rejilla de este tamaño.

2. **El mejor z de un nulo estará en ese mismo rango**, con media entre +2,5
   y +3,5. Si es así, la rejilla real no demuestra nada.

3. **La mejor celda real NO superará al mejor de los diez nulos.**

Si la 3 falla — si lo real bate a los diez nulos — entonces EMA+Fibo tiene
algo de verdad y hay que seguirlo. Sería el primer caso del proyecto.
