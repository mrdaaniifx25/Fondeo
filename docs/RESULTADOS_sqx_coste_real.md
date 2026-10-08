# Resultado · la estrategia del oro al coste REAL medido

El bloqueo de este proyecto durante semanas fue un dato que no existía: el
spread real del XAUUSD en la cuenta del usuario. El umbral de equilibrio
medido era **0,52 $**.

**Medido en FundingPips MT5 (septiembre 2026): 0,08 - 0,20 $.**

Está entre el 15 % y el 38 % del punto de equilibrio. El bloqueo se levanta.
Código en `bt/sqx_coste.py` y `bt/sqx_reto.py`.

## Lo primero: el backtest ya era conservador

`bt/sqx_xauusd.py` asumía spread 0,20 $ — el **techo** del rango real — más
6 $/lote de comisión y 35 $/lote/noche de swap. Así que el +71,2 % documentado
ya estaba calculado con su peor caso.

## La sensibilidad al coste, con su rango real

     spread  comision   swap |     n       ret     CAGR     PF      DD      t
       0,08         6     35 |   597    140,6 %  28,07 %  1,286  -12,2 %  +2,43
       0,14         6     35 |   597    109,4 %  23,15 %  1,238  -12,7 %  +2,08
       0,20         6     35 |   597     87,8 %  19,42 %  1,202  -13,2 %  +1,80
       0,08        10     35 |   597    132,3 %  26,79 %  1,274  -12,4 %  +2,34
       0,14        10     35 |   597    102,2 %  21,93 %  1,226  -13,0 %  +1,99
       0,20        10     35 |   597     81,2 %  18,24 %  1,191  -13,5 %  +1,71
       0,20        15     50 |   597     69,3 %  15,98 %  1,168  -13,9 %  +1,52
       0,20         6     70 |   597     77,6 %  17,56 %  1,184  -13,3 %  +1,65
       0,30         6     35 |   597     52,9 %  12,70 %  1,135  -14,1 %  +1,24
       0,50         6     35 |   597     10,6 %   2,88 %  1,032  -22,5 %  +0,30
       0,65         6     35 |   597    -19,9 %  -6,06 %  0,931  -40,5 %  -0,70
       1,00         6     35 |   597    -55,3 % -20,27 %  0,763  -62,9 %  -2,49

En el punto medio de su rango (0,14 $): **CAGR 23,15 %, drawdown máximo
−12,7 %, t +2,08.** Es la primera vez en todo el proyecto que un `t` pasa de 2
con un coste realista enfrente.

Y aguanta el margen: aun subiendo la comisión a 15 $/lote y el swap a 50 $, con
spread 0,20, sigue en +69,3 % y t +1,52.

## El reto de FundingPips: sigue siendo una lotería

Monte Carlo, 20.000 repeticiones, remuestreando **días de calendario enteros**
(los ~60 % de días sin operación entran en blanco) y comprobando el límite
diario contra el **equity flotante**, no contra la operación cerrada — para lo
cual se añadió la excursión adversa máxima de cada operación a
`bt/sqx_xauusd.py`.

    spread 0,20 (su peor caso)
     riesgo/op  vol anual   fase 1   fase 2   LAS DOS   vs azar 36,9 %
         0,6 %      8,9 %    13,0 %   32,5 %     4,2 %      -32,7 pp
         1,2 %     17,8 %    42,1 %   59,8 %    25,2 %      -11,7 pp
         1,8 %     26,8 %    52,6 %   64,6 %    33,9 %       -3,0 pp
         2,4 %     35,7 %    48,9 %   57,9 %    28,3 %       -8,6 pp

    spread 0,14 (punto medio)
         1,2 %     17,9 %    44,8 %   62,3 %    27,9 %       -9,0 pp
         1,8 %     26,8 %    55,3 %   67,3 %    37,2 %       +0,3 pp
         2,4 %     35,8 %    51,3 %   60,2 %    30,9 %       -6,0 pp

**Lo mejor que se consigue es empatar con el azar** (37,2 % contra 36,9 %), y
solo afinando el riesgo al 1,8 %. Es exactamente lo que dice
`RESULTADOS_swing_eurusd.md`: el reto premia la varianza, no la ventaja, y una
estrategia buena y lenta no llega en 60 días.

Así que hay que separar dos preguntas que no son la misma:

- **¿sirve para pasar el reto?** No más que no tener ninguna ventaja.
- **¿sirve para una cuenta propia?** 23 % anual con −12,7 % de drawdown. Sí,
  si el resto de objeciones se resuelve.

### Un fallo por el camino

La primera versión del simulador remuestreaba solo los 368 días **con
operación**, así que metía 60 días de trading en una fase de 60 días de
calendario cuando la estrategia opera 4 de cada 10 días. Daba 51,8 % de
aprobado. Corregido a días de calendario da 25,2 %, que ya concuerda con el
21,5 % que este mismo repositorio tenía medido por otra vía.

Se detectó porque el número **contradecía al repositorio en 30 puntos**. Un
resultado que se pelea con lo ya medido es un fallo hasta que se demuestre lo
contrario.

## Lo que sigue sin resolverse, y es lo importante

El spread era **la menor** de las cuatro objeciones. Las otras tres siguen
exactamente igual:

1. **3,55 años de datos, y empiezan en 2023** — es muy probable que solapen con
   el periodo en que StrategyQuant optimizó la estrategia. Un `t` de +2,08
   sobre la ventana en que se ajustaron los parámetros no es un `t` limpio.
2. **Funciona en 2 de 6 instrumentos**, y los dos que funcionan (oro y GER40)
   son justo los dos cuyos datos empiezan en 2023.
3. **El único tramo verdaderamente fuera de muestra es 2026**: +3,2 % en siete
   meses, el más flojo de los cuatro años.

Y los 3,55 años son 3,55 años de un mercado alcista histórico del oro. Un solo
régimen.

## La prueba que lo decide

**XAUUSD M1 de 2020, 2021 y 2022.** Tres años que ni yo he visto ni,
razonablemente, vio la optimización de StrategyQuant, y que además incluyen un
régimen distinto (el oro lateral de 2021-2022).

Si la estrategia gana ahí, deja de haber objeción seria. Si no gana, se cierra.

`histdata.com` está bloqueado por la política del proxy de este entorno (403 en
el CONNECT), así que la descarga tiene que hacerla el usuario. Es el mismo sitio
y el mismo formato de los ficheros que ya subió antes.
