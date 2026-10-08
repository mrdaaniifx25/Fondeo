# Preregistro · la hoja de trabajo de EURUSD

Sellado ANTES de medir. Código en `bt/eurusd_final.py`.

## Por qué esta familia y no otra

Lo que YA está medido en EURUSD y por tanto no se vuelve a probar:

    EMA + Fibonacci          675 celdas, 0 positivas, peor que datos barajados
    busqueda con arboles     IC +0,0126 contra una media de nulos de +0,0165
    SMC-71 / fibo 71 %       retirado por comparaciones multiples
    rango asiatico           ventaja bruta real, se la come el coste
    reversion a la media     signo NEGATIVO en el pase de swing

Lo único que salió con signo correcto y consistente fue **rotura y momento**
(familias A y B del pase de swing: positivas en 6 de 7 plazos). Y el propio
usuario señaló la pieza que faltaba: **el stop ancho**, donde el coste pasa
del 13-27 % al 1-3 % del riesgo.

Además, la estrategia del oro aplicada a EURUSD dio **-83,7 %, t -3,31**. Pero
era SOLO LARGOS, y EURUSD no es un activo con prima de riesgo: es un precio
relativo. Una estrategia direccional fija ahí no tiene sentido. **Por eso esta
va en los dos sentidos.**

## La familia

Rotura de canal (Donchian) simétrica, sobre velas de H1 y H4.

    entrada    orden stop en el maximo de N velas cerradas (compra)
               o en el minimo de N velas cerradas (venta)
    stop       k x ATR(N_atr) fijado en la entrada, no se mueve
    salida     a las M velas, o el stop, lo que llegue antes
    validez    la orden vive V velas y se recalcula
    una sola posicion, sin piramidar, sin filtro de tendencia

    N     20 · 40 · 60 · 100          k   1,0 · 2,0 · 3,0
    M      5 · 10 ·  20 ·  40         V   igual a M
    = 48 celdas por temporalidad, 96 en total

Coste: 1,43 pips (spread 0,7-1,0 + comision 5 EUR/lote), el medido en
`docs/COSTE_real.md`. Riesgo 1 % compuesto. Empate stop/salida en la misma
vela: resuelto minuto a minuto.

Ajuste en **2020-2023**. Comprobacion en **2024-2026**, sin tocar.

## MI CRITERIO DE ÉXITO, escrito antes de ver un solo número

La declaro **operable** solo si cumple **las cinco**:

    1  profit factor fuera de muestra > 1,10 con el coste real
    2  bate a las entradas al azar con su misma geometria
    3  al menos el 60 % de los vecinos de parametros positivos fuera de muestra
    4  bate a los 5 nulos con bloques permutados
    5  correlacion ajuste / fuera de muestra > +0,30 sobre las 96 celdas

La declaro **descartada** si falla cualquiera de ellas, y lo escribo en la
hoja como fallo, no como "resultado prometedor".

## Lo que espero, dicho antes

Espero que **falle el criterio 5**. En este proyecto solo ha generalizado la
geometria de barreras (+0,94); ninguna senal. La rotura simetrica en EURUSD
con stop ancho es la ultima carta razonable que queda, y la juego entera.
