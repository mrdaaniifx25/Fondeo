# SMC-71 · qué instrumentos operar, y por qué todavía no con dinero

## Lo que sí está establecido

No filtrar. En el examen del bloque 8 lo que él eligió dio -0.086 R netas y
lo que descartó dio +0.282. Si se opera esto, se opera entero.

## Lo que NO está establecido

    M30, 6 instrumentos, 1290 operaciones:  R neta  +0.006
    M60, 6 instrumentos,  694 operaciones:  R neta  +0.065

    operaciones para llevar el +0.006 de M30 a z=2:  306.602  (1.565 años)
    operaciones para llevar el +0.065 de M60 a z=2:    2.459  (23 años)

La ventaja neta no es pequeña: es indistinguible de cero en cualquier
horizonte humano. El BRUTO sí está demostrado (z +3.42 en M30 sin oro); lo
que se lo come es el coste.

## La lista, ordenada por coste/R (criterio a priori, no por resultado)

    1 · US100  (NSXUSD)   coste/R  5.1 %   neta +0.083
    2 · GER40  (GRXEUR)   coste/R  5.8 %   neta +0.123   (solo 72 ops)
    3 · US500  (SPXUSD)   coste/R  7.3 %   neta -0.030
    4 · USDJPY            coste/R 14.8 %   neta -0.106
    5 · GBPUSD            coste/R 17.0 %   neta -0.036
    6 · EURUSD            coste/R 19.8 %   neta +0.093

    FUERA · XAUUSD: falla en BRUTO (-0.070 en M30 con coste 5.2 %)

Ordenar por R neta daria US100 / GER40 / EURUSD, que es seleccion a
posteriori. Ademas EURUSD sale positivo con el coste/R MAS ALTO de los
seis, lo que contradice el mecanismo -> esa columna es ruido.

## Reglas prácticas medidas

    US100 / US500 : 62 dias con senal en los dos, 94 % misma direccion
    EURUSD/ GBPUSD: 36 dias con senal en los dos, 92 % misma direccion

Abrir las dos de un par no diversifica, dobla la apuesta con doble
comision. Elegir una.

    71 % de los dias solo salta UN instrumento
    2 instrumentos a la vez: 23 % de los dias · 3 o mas: 6 %
    correlacion del resultado diario NSXUSD/SPXUSD: +0.47

    ritmo: 16.3 senales/mes en M30 · 8.8 en M60

## Recomendación

1. Conseguir el spread y la comision REALES de US100, US500 y GER40. Los
   tres instrumentos con neta positiva en M30 son justo los tres cuyo coste
   esta estimado (1.50 / 0.50 pts), no medido.

2. Demo de 3 meses, los 6, M30, todas las senales: unas 49 operaciones. Con
   49 el error tipico es 0.232 R, asi que solo detectaria una ventaja de
   0.46 R o mayor. NO va a demostrar que funciona. Lo que mide es si puede
   ejecutar 49 senales en tiempo real, que es lo que el examen no prueba
   (alli veia el desenlace en dos segundos).

3. Decidir con esos dos datos delante. No antes.
