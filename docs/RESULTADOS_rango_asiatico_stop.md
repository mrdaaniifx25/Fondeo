# Resultado · rango asiático con distintas anchuras de stop

Preregistro sellado en `b503a21`. Un solo pase, cuatro variantes.

## El resultado

     modo  stop medio    R:R   R bruta            IC 95 % bootstrap
    --------------------------------------------------------------
        A        3.2p   15.1    +0.378      [+0.196 , +0.564]
        B        4.2p   10.1    +0.214      [+0.071 , +0.358]
     TOPE        4.4p    9.0    +0.169      [+0.035 , +0.309]
        C       12.1p    5.0    -0.050      [-0.187 , +0.093]

El bootstrap de 20.000 remuestreos confirma que el z era fiable pese a la
asimetría: la ventaja bruta es real en A, B y TOPE.

## Mis cuatro predicciones: dos fallan de lleno

    1 · la R bruta de A se reduce y pierde significación   FALLA
        (sale +0,378 con z +4,07: SUBE, no baja)
    2 · la R neta de A mejora al menos +0,10               FALLA
        (sale -0,295, peor que el -0,186 del tope)
    3 · la neta de A no es significativamente positiva     ACIERTA
    4 · GBPUSD el más fuerte, EURUSD plano                 PARCIAL
        (GBPUSD sí; EURUSD en modo A da +0,462, no está plano)

Me equivoqué en el mecanismo: di por hecho que quitar el suelo de 4 pips
ENSANCHARÍA el stop. Lo ESTRECHA, porque la entrada está en el 50 % de la
mecha y de ahí al extremo hay la mitad de la mecha, a menudo 2-3 pips.

## Lo que de verdad enseña este pase

La ventaja bruta escala AL REVÉS que la anchura del stop, y desaparece a
12 pips. Eso es lo contrario de lo que hace una ventaja robusta: la del
SMC-71 se mantenía plana al cambiar de temporalidad (+0,120 en M5 a
+0,191 en M60). Esta solo existe con stops de 3-4 pips.

Y 3-4 pips es exactamente donde el coste se lleva el 35-45 % de cada R.

**La ventaja y el coste están sobre la misma palanca, moviéndose en
direcciones opuestas.** Es la demostración más limpia del muro de costes
de todo el proyecto.

## El coste máximo que soporta cada celda

    resolviendo media(R - c/stop) = 0   ->   c = media(R) / media(1/stop)

     modo   instr     n    stop   R bruta    R NETA  coste max  coste real
    ----------------------------------------------------------------------
        A  EURUSD   793    2.5p    +0.462    -0.279      0.89p       1.43p
        A  GBPUSD   851    3.5p    +0.523    -0.095      1.35p       1.60p
        B  EURUSD   783    3.5p    +0.114    -0.349      0.35p       1.43p
        B  GBPUSD   848    4.5p    +0.447    +0.029      1.71p       1.60p
     TOPE  GBPUSD   850    4.5p    +0.336    -0.035      1.45p       1.60p

Once de las doce celdas dan neta negativa. La única positiva es
B/GBPUSD con **+0,029 e IC 95 % [-0,216 , +0,290]**, o sea, cero.

## La conclusión, y es útil

Esta estrategia NO es alfa: es una arbitraje del coste de ejecución.
Existe una ineficiencia real después del barrido del rango asiático,
pero es pequeña en términos absolutos -del orden de 1 a 1,7 pips por
operación- y solo la cobra quien pague menos que eso por operar.

    coste de equilibrio     0,24 a 1,71 pips según la celda
    coste en una prop firm  1,43 a 1,60 pips

Con una cuenta de spread crudo a 0,4 pips en GBPUSD, la celda A daría
neta en torno a +0,33. Con los 1,60 de una cuenta de fondeo, da -0,095.

Eso explica cómo el autor puede creerlo de buena fe -si opera futuros o
una cuenta institucional, sus números son otros- y por qué no se puede
replicar en una cuenta de fondeo, que es donde tú operarías.
