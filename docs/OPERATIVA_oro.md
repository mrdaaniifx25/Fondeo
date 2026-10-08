# La operativa · XAUUSD H1, rotura de 51 velas

Sale de `docs/RESULTADOS_sqx_xauusd.md`. Es la versión limpia: **sin el filtro
GannHiLo**, que el control de vecindario demostró que no aporta (sin él el
backtest da +87,8 % en vez de +71,2 %).

## ANTES DE NADA: la medición que decide

**No operes esto sin haber medido tu spread del XAUUSD.** El punto de
equilibrio está en **0,52 $** y no es negociable:

     spread medido      qué hacer
     --------------------------------------------------------
     por debajo de 0,35 $   adelante
     entre 0,35 y 0,50 $    el resultado se parte por la mitad; piénsalo
     0,52 $ o más           NO la operes. Pierde dinero.

Cómo medirlo, y es media hora de trabajo repartida en dos días:

    1  abre MT5, pon XAUUSD, activa la columna de spread en Observación
       de Mercado (botón derecho -> Spread)
    2  anota el spread a las 03:00, 09:00, 15:30 y 22:00, hora de tu
       servidor, durante dos días de mercado
    3  haz la media de las ocho lecturas

Anota también el **swap de largos** (Especificaciones del símbolo -> Swap
largo) y la **comisión por lote**. El backtest asume 35 $/lote/noche y
6 $/lote ida y vuelta.

## Las reglas

    instrumento   XAUUSD  ·  gráfico de 1 hora  ·  SOLO COMPRAS, nunca ventas
    horario       señales solo entre 01:30 y 23:30 hora del servidor
    posiciones    1 como máximo. Con una abierta, no se hace nada más.

    ENTRADA
      · mira el máximo más alto de las últimas 51 velas H1 cerradas (~2 días)
      · deja una orden BUY STOP en ese nivel exacto
      · la orden vive 10 velas H1. Si no salta, se cancela y se recalcula.

    STOP
      · 1 x ATR(95) del gráfico H1, calculado en el momento de la entrada
      · mediana histórica: 6,82 $ por debajo de la entrada
      · NO se mueve nunca. Ni a break-even, ni trailing, ni parcial.

    SALIDA
      · no hay take profit
      · se cierra a mercado 5 velas H1 después de la apertura de la posición
      · lo que llegue antes: el stop o el reloj

    TAMAÑO
      lotes = (riesgo% x capital) / (ATR95 x 100)
      · en cuenta propia:  riesgo 1 %
      · en un reto de fondeo: riesgo 2 %   (ver más abajo el porqué)

## Qué esperar, para que no te pille

De las 581 operaciones del backtest:

    pierde el 57,5 % de las veces
    racha máxima de pérdidas seguidas:  13
    drawdown máximo:  -13,5 %   (al 1 % de riesgo; al 2 % sería ~-27 %)
    tiempo dentro:  4,2 horas de mediana
    frecuencia:  unas 14 operaciones al mes

    cuando gana:    +1.480 $ de mediana  (sobre 100.000 de cuenta)
    cuando pierde:  -1.199 $ de mediana

**Vas a perder más veces de las que ganas.** Eso es normal aquí y no significa
que esté rota. Lo que la rompería es que el tamaño medio de las ganancias deje
de superar al de las pérdidas.

De las que salen por reloj, ganan el 82 %. De las que salen por stop, el 0 %.

## Por qué 2 % en un reto y 1 % en cuenta propia

P(pasar las dos fases de FundingPips) según el riesgo:

     riesgo/op   vol anual   las dos fases   vs geometría sin ventaja (36,9 %)
        1 %        14,9 %       21,5 %              -15,4 pp
        2 %        29,8 %       42,7 %               +5,8 pp   <- óptimo
        3 %        44,7 %       31,8 %               -5,1 pp

Al 1 % la estrategia es demasiado lenta para 60 días y pasa MENOS que no tener
ventaja. Al 2 % es lo único de todo el proyecto que bate a la geometría pura.

En cuenta propia es al revés: al 1 % esperas +12,1 % anual con un peor año
típico de -17,7 %. Al 2 % el peor año típico es **-35,5 %**.

## Reglas de parada, escritas hoy y no el día malo

    · una sola posición abierta. Nunca dos.
    · el stop no se toca. Nunca.
    · no se opera fuera de 01:30-23:30.
    · si el spread medio de tu cuenta sube por encima de 0,50, se para.
    · si aparecen 20 pérdidas seguidas -nunca pasó en el backtest, cuyo
      máximo fue 13-, se para y se revisa.
    · no se añade ningún filtro "porque parece obvio". Cada filtro añadido
      es una comparación más, y este proyecto entero trata de eso.

## Lo que sigue sin estar demostrado

    t = +1,80 sobre 597 operaciones      (no llega a 2)
    Sharpe +0,81, necesita 6,1 años      (hay 3,55)
    funciona en 2 de 6 instrumentos      (oro y GER40, los dos del mismo tramo)
    el tramo más limpio, 2026, es el más flojo: +3,2 % en siete meses

Pasa todos sus controles internos -azar, vecindario de parámetros, nulos- y
eso no lo había conseguido nada más en este proyecto. Pero **3,55 años de un
solo instrumento en el mayor mercado alcista del oro de la década no son una
demostración**.

La evidencia que falta solo la da el tiempo hacia delante. Si la sigues, anota
cada operación desde el primer día: en seis meses tendrás un dato que vale más
que todo este backtest.
