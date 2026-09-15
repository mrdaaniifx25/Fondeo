# Preregistro · Frankenstein v1

Firmado ANTES de medir. Combina los DOS únicos componentes del proyecto
que sobreviven a la prueba del stop:

    ESTRUCTURA + ENTRADA   SMC-71 (barrido de fractal -> BOS -> fibo 71 %)
    DIRECCIÓN              deriva alcista de los índices

## Por qué solo estos dos

La R bruta al mover la anchura del stop o la temporalidad:

    SMC-71           +0.166  +0.155  +0.156     plana  -> mecanismo
    rango asiático   +0.378  +0.214  +0.169  -0.050    se cae -> frágil
    compras índices  -0.016  +0.029  +0.059     sube   -> deriva

Se descartan: las confluencias del grupo (neta -0.227), el SMT (z -0.21),
los máximos históricos (signos opuestos entre índices), el rango asiático
(se evapora al ensanchar el stop) y las siete familias anteriores.

## Variantes, declaradas antes de correr

    0 · SMC-71 M60, solo índices (US100, US500, GER40)      referencia
    1 · igual, SOLO COMPRAS
    2 · igual, SOLO VENTAS
    3 · SMC-71 M60 en forex (EURUSD, GBPUSD, USDJPY)        control

## PREDICCIONES FIRMADAS

    1 · en índices, las COMPRAS del SMC-71 dan más R bruta que las
        VENTAS. Es la deriva sumándose a la señal.

    2 · la diferencia compras-ventas NO alcanza |z| > 2,0: la muestra de
        M60 en tres índices es demasiado pequeña para resolverla

    3 · la variante 1 (solo compras) da R NETA positiva, por encima
        de +0.065 que es lo que da el SMC-71 M60 completo

    4 · en el control de forex NO hay diferencia entre compras y ventas
        (|z| < 2,0), porque ahí no hay deriva estructural

## Umbral

    |z| > 2,0. Un solo pase. Menos de 80 operaciones en una celda: no se
    interpreta.

## Qué contaría como que ME EQUIVOCO

    Que las ventas rindan igual o más que las compras en índices. Eso
    significaría que la deriva y la señal no se solapan, y el
    Frankenstein se queda en SMC-71 a secas.
