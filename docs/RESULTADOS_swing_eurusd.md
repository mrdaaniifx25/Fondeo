# Resultado · swing en EURUSD con stops anchos

Preregistro sellado antes de medir. Código en `bt/swing_eurusd.py`.
84 celdas: momento / rotura / reversión x 7 plazos x 4 anchuras de stop.
Velas diarias, 2020-2026, stops de 60 a 400 pips.

## Su pregunta era buena, y la respuesta es sí

    familia probada          stop típico     coste/riesgo
    SMC-71 M15                  5,2 pips        27,3 %
    SMC-71 M30                  7,2 pips        19,8 %
    EMA+Fibo                   10,9 pips        13,1 %
    SMC-71 M120                21,7 pips         6,6 %
    búsqueda con árboles       ~5 pips         385 % de la ventaja

Dos meses de proyecto vivían entre 5 y 22 pips de stop. Con 100 pips el coste
cae al 1,4 % del riesgo. Esa mitad del mapa estaba sin tocar.

## Las cuatro predicciones firmadas: las cuatro se cumplen

    1  ninguna celda con t > 2,5 fuera de muestra     SI   máximo +1,43
    2  momento y rotura mismo signo, reversión al revés SI
    3  momento a plazo largo POSITIVO                 SI   +0,85 (N=120)
    4  correlación ajuste/fuera por debajo de +0,3    SI   -0,429

La 4 merece leerse dos veces: **-0,429**. Elegir la celda por lo que hizo en
2020-2023 te lleva sistemáticamente a la peor de 2024-2026. Compárese con la
geometría de barreras, que correlacionaba **+0,94**.

## Lo que sí aparece, y por qué no basta

    t medio por familia y plazo (2020-2023)
     N      A momento   B rotura   C reversión
     10      +0,82       +0,37       -1,26
     20      +0,45       +0,22       +0,10
     60      +0,71       +0,62       -1,15
    120      +0,85       +0,16       -0,38
    250      +0,30       +0,39       -0,28

Momento y rotura a favor, reversión en contra. Y replica en los cuatro
instrumentos:

    EURUSD +0,878   ·   GBPUSD +1,397   ·   USDJPY +2,486   ·   XAUUSD +0,205

**Pero los nulos hacen lo mismo 4 de 5 veces** (+0,058, +0,824, +0,906, +0,076
y -0,719). Es un sesgo mecánico: entrar contra tendencia con un stop fijo hace
saltar el stop más a menudo, exista o no estructura. No puedo separar una
cosa de la otra con estos datos.

El mejor Sharpe del ajuste es **+0,52** — justo en el 0,3-0,5 que la
literatura da para seguimiento de tendencia en divisas. Y con 6,5 años eso da
t = 0,94. Lo dije en el preregistro antes de mirar: **este experimento no
puede confirmar un efecto del tamaño que cabe esperar.**

    años de operativa necesarios para demostrar el Sharpe (t = 2)
      Sharpe 0,3  ->  44,4 años
      Sharpe 0,5  ->  16,0 años
      Sharpe 0,8  ->   6,2 años

## Y el hallazgo que da la vuelta al proyecto entero

*(Primer cálculo equivocado: puse la deriva diaria como `Sharpe x vol / raíz(252)`
en vez de `/252`, inflándola 16 veces y dando 94 % de aprobado con Sharpe 0,3.
Corregido abajo.)*

P(pasar el reto de FundingPips) según el Sharpe **verdadero** de la
estrategia, con la cuenta al 20 % de volatilidad anual:

    Sharpe   retorno anual   fase 1   fase 2   las dos   vs azar 37,0 %
      0,0           0 %      36,7 %   55,1 %    20,2 %      -16,8 pp
      0,3           6 %      41,7 %   59,8 %    24,9 %      -12,1 pp
      0,5          10 %      45,0 %   63,0 %    28,4 %       -8,6 pp
      0,8          16 %      50,5 %   67,5 %    34,1 %       -2,9 pp
      1,2          24 %      57,7 %   73,0 %    42,1 %       +5,1 pp
      2,0          40 %      70,5 %   83,1 %    58,6 %      +21,6 pp

**Una estrategia con ventaja REAL de Sharpe 0,5 pasa el reto el 28,4 % de las
veces. La estrategia sin ninguna ventaja, con la geometría ajustada a las
barreras, pasa el 36,9 %.**

Hace falta **Sharpe 1,2** -el doble de lo que consiguen los fondos de
tendencia profesionales- solo para empatar con no tener ventaja ninguna.

La razón es el calendario: con 20 % de volatilidad anual, ganar un 8 % tarda
del orden de un año. El reto da 60 días. Una estrategia buena y lenta no
llega; una apuesta concentrada sí.

## La conclusión

**El reto de fondeo no premia la ventaja. Premia la varianza.**

Por eso pasar no demuestra nada, por eso los que retiran no operan mejor, y
por eso la respuesta correcta a "dame una estrategia para pasar el reto" no es
una señal: es una geometría. Está en `docs/RESULTADOS_cfd_fondeo.md`.

Y por eso mismo: si algún día tiene una ventaja real de verdad, **el peor
sitio para usarla es un reto de dos fases con límite de 60 días**.
