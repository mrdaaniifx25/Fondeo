# Resultado · SMC-71 en forex, y cuál es la celda que queda en pie

Preregistro sellado en `3ac1582`, antes de medir.

## Agrupando los tres pares

       TF     n   R bruta       z       IC 95 % bruta    R NETA      IC 95 % neta
    ------------------------------------------------------------------------------
    M30    752    +0.183   +3.07  [+0.068, +0.300]    -0.018  [-0.136, +0.099]
    M60    379    +0.080   +0.98  [-0.076, +0.243]    -0.046  [-0.205, +0.114]
    M120   209    -0.059   -0.55  [-0.260, +0.147]    -0.145  [-0.345, +0.065]
    M240    99    +0.209   +1.31  [-0.098, +0.525]    +0.152  [-0.153, +0.473]

Las seis predicciones: 4 aciertan, 2 fallan (la de la R bruta plana y la
de la mejora monótona del neto). Pero ninguna diferencia ENTRE
temporalidades es significativa -M60 contra M120 da z +1,04; M120 contra
M240 da z -1,40- así que lo correcto no es "la bruta se cae" sino "con
n de 99 a 209 no se distingue nada". M240 no es utilizable.

## La celda que queda en pie: EURUSD en M30

        par     n  stop mediano   R bruta       z  coste max  coste real    R NETA
     ------------------------------------------------------------------------------
     EURUSD   254          7.2p    +0.317   +3.01      2.02p       1.43p    +0.093
     GBPUSD   227          9.4p    +0.154   +1.43      1.30p       1.60p    -0.036
     USDJPY   271         10.1p    +0.081   +0.84      0.65p       1.50p    -0.106

    EURUSD M30 en detalle
      acierto 38,2 % contra el azar de 29,0 %
      R bruta +0.317  ·  z +3.01
      R NETA  +0.093  ·  IC 95 % [-0.109, +0.299]  ·  p(neta<=0) = 19,1 %
      3,3 operaciones al mes
      coste/R 19,8 %: el peaje se lleva DOS TERCIOS del edge bruto

    POR AÑO
      2020 -0.257 · 2021 +0.105 · 2022 +0.025 · 2023 -0.231
      2024 +0.507 · 2025 +0.222 · 2026 +0.256        -> 5 de 7 positivos

    COMPRAS  n=134  neta +0.278
    VENTAS   n=120  neta -0.114

## Qué se puede y qué no se puede decir

SE PUEDE: la ventaja BRUTA en EURUSD M30 es real. z +3,01 sobre 254
operaciones, con el acierto 9 puntos por encima del listón geométrico.

NO SE PUEDE: decir que sea rentable. La neta es +0,093 pero con
p(neta<=0) = 19,1 %. Una de cada cinco veces, esto es cero o peor.

Y una advertencia que ya hice en `RESULTADOS_smc71_instrumentos.md` y que
sigue en pie: EURUSD sale positivo TENIENDO EL COSTE/R MÁS ALTO de los
siete instrumentos. Eso contradice el mecanismo del coste y es motivo de
sospecha, no de entusiasmo.

## El coste vuelve a ser la única palanca

     coste 1,5 pips (tu cuenta):  neta -0.018   no significativa
     coste 1,2 pips:              neta +0.022   no
     coste 1,0 pips:              neta +0.049   no
     coste 0,6 pips:              neta +0.103   no
     coste 0,4 pips:              neta +0.129   SÍ, IC [+0.014, +0.244]

Agrupando los tres pares en M30. El punto de equilibrio está en 1,4-1,5
pips y tu cuenta cobra 1,43-1,60: estás justo en el borde.

## Simulación del challenge con EURUSD M30

     riesgo 0,5 %:  fase 1 82 %  fase 2 85 %  ->  fondeado 70 %
     riesgo 1,0 %:  fase 1 70 %  fase 2 76 %  ->  fondeado 53 %
     riesgo 2,0 %:  fase 1 63 %  fase 2 68 %  ->  fondeado 43 %

Con ventaja cero el listón era 37 %. Con esto sube a 53 % al 1 %, y el
riesgo bajo es mejor: 70 % al 0,5 %.
