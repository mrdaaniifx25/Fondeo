# Preregistro · estrategia de swing en EURUSD, desde cero

Sellado ANTES de medir. Código en `bt/swing_eurusd.py`.

## Por qué esto, y no otra cosa

Su pregunta: *"¿qué riesgo estás asumiendo? porque lo mismo es eso"*. Tiene
razón y está medido:

    SMC-71 M15         stop  5,2 pips    coste = 27,3 % del riesgo
    SMC-71 M30         stop  7,2 pips    coste = 19,8 %
    EMA+Fibo           stop 10,9 pips    coste = 13,1 %
    SMC-71 M120        stop 21,7 pips    coste =  6,6 %
    busqueda ML        ~5 pips           coste = 385 % de la ventaja

**Dos meses de proyecto viven entre 5 y 22 pips de stop.** Con 100 pips el
coste cae al 1,4 % del riesgo y deja de ser el problema. Esa mitad del mapa
está sin tocar en EURUSD.

## El montaje

Velas diarias de EURUSD (cierre 17:00 Nueva York), 2020-2026. Tres familias,
porque no sé cuál de las dos direcciones -si alguna- es la buena:

    A · MOMENTO       posicion = signo del retorno de los ultimos N dias
    B · ROTURA        largo si el cierre supera el maximo de N dias (Donchian)
    C · REVERSION     largo si el precio esta N desviaciones por DEBAJO
                      de su media de N dias

    N     5 · 10 · 20 · 40 · 60 · 120 · 250 dias
    stop  1 · 2 · 3 · 5 veces el ATR(20) diario   (≈ 60 a 400 pips)
          = 84 celdas

Tamaño de posición a riesgo constante: cada operación arriesga lo mismo, o
sea que el tamaño va como 1/ATR. Coste 1,43 pips en cada cambio de posición,
convertido a fracción de R.

Medición sobre la **serie de P&L diaria**, no sobre operaciones sueltas: con
1.700 días eso da mucha más potencia que contar 85 operaciones. Intervalos por
bootstrap de bloques de 20 días, que conserva la autocorrelación.

Ajuste en 2020-2023, comprobación en 2024-2026. Nulo: EURUSD con los bloques
permutados, cinco repeticiones, misma rejilla.

## LA LIMITACION QUE HAY QUE DECIR ANTES, NO DESPUES

1.700 días son 6,5 años. Para un Sharpe verdadero `S`, el estadístico t
esperado es `S x raiz(6,5)`, o sea `2,55 x S`. Para llegar a t = 2 hace falta
**Sharpe 0,78**.

El seguimiento de tendencia en divisas tiene, en la literatura, Sharpe de
**0,3 a 0,5**. Con estos datos eso daría t de 0,8 a 1,3: **indetectable**.

Así que este experimento **no puede** confirmar un efecto del tamaño que cabe
esperar. Solo puede: (a) descartar efectos grandes, (b) medir la dirección, y
(c) decir si el resultado es compatible con la literatura. Si sale t = 1,2 no
será una prueba de nada, y lo diré así.

## Las cuatro predicciones firmadas

1. **Ninguna celda superará t = 2,5 fuera de muestra.** Por potencia, no por
   pesimismo.

2. **El momento (familia A) y la rotura (B) tendrán el MISMO signo entre sí**,
   y opuesto al de la reversión (C). Son la misma apuesta escrita de dos
   formas.

3. **El signo del momento a plazo largo (N = 120, 250) será POSITIVO**, que es
   lo que dice la literatura de seguimiento de tendencia en divisas.

4. **La mejor celda del ajuste 2020-2023 NO mantendrá su ventaja en
   2024-2026** — correlación ajuste/fuera de muestra por debajo de +0,3 sobre
   las 84 celdas. En este proyecto solo ha generalizado la geometría de
   barreras (+0,94); ninguna señal.

Si la 3 sale al revés, el seguimiento de tendencia no está en estos datos.
Si la 4 falla -si correlaciona bien-, sería la primera señal que generaliza y
habría que perseguirla.
