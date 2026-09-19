# Resultado · el rango CRT dinámico por sesión y la lógica de sesiones

Sale del cuarto vídeo (SmartRisk). Código en `bt/crt_sesion.py`. Cinco
instrumentos, 2020-2026, 59.852 filas. z con error estándar agrupado por
instrumento-día.

## Qué se midió, y por qué no estaba medido ya

    "instead of relying on fixed hours, I focus on the highest and lowest
     15-minute candles of the previous trading session or kill zone
     and use those as my range candles"

El rango no es una vela de reloj: es **la vela M15 más alta y la más baja de
la sesión anterior**. Se barre su extremo, se cierra de vuelta dentro, y el
objetivo es **el otro extremo de esa misma vela** — no el de la sesión.

Eso es lo que lo separa del barrido asiático de `RESULTADOS_barrido_asiatico.md`
y de `RESULTADOS_lsweep_v1.md`, donde el objetivo era el extremo opuesto de la
sesión entera. Aquí el objetivo es corto y el stop es corto.

**Celda primaria declarada:** operar Londres con el rango de Asia, objetivo la
vela. **Control de detección:** operar Asia con el rango de la sesión de Nueva
York **del día anterior** — misma mecánica, sin ninguna razón para funcionar.

## 1 · El trade

       opera  rango de  objetivo     n    R:R  acierto    geom   R BRUTA       z    R NETA
        ASIA        NY      2.5R  2924   2,50   27,6 %  28,6 %  +0,0545   +1,88   -0,1634
        ASIA        NY     medio  2915   4,48   29,8 %  29,1 %  +0,0421   +1,05   -0,1763
        ASIA        NY    sesion  2924   9,25   16,8 %  17,8 %  +0,0672   +1,17   -0,1507
        ASIA        NY      vela  2857   2,16   47,1 %  45,2 %  +0,0657   +2,25   -0,1547
     LONDRES      ASIA      2.5R  5948   2,50   28,0 %  28,6 %  +0,0237   +1,16   -0,1852
     LONDRES      ASIA     medio  5906   2,71   36,2 %  36,0 %  +0,0087   +0,41   -0,2012
     LONDRES      ASIA    sesion  5940   5,82   21,1 %  21,4 %  +0,0587   +1,87   -0,1505
     LONDRES      ASIA      vela  5463   1,27   54,2 %  54,3 %  +0,0003   +0,02   -0,2140  <- primaria
          NY   LONDRES      2.5R  6490   2,50   23,7 %  28,6 %  +0,0124   +0,67   -0,1623
          NY   LONDRES     medio  6263   2,54   37,9 %  39,1 %  +0,0192   +0,97   -0,1604
          NY   LONDRES    sesion  6435   5,35   20,2 %  25,0 %  +0,0170   +0,65   -0,1589
          NY   LONDRES      vela  5787   1,35   52,1 %  53,8 %  -0,0052   -0,34   -0,1922

**La celda primaria es +0,0003 R con z +0,02.** Acierto 54,2 % contra un 54,3 %
geométrico. No es "poco": es cero con cuatro decimales.

Y la frase que cierra el asunto: **el control de detección puntúa más alto que
el modelo.** Operar Asia con el rango de un Nueva York que ya terminó ayer da
+0,0657 (z +2,25); el modelo real da +0,0003 (z +0,02). Cuando el control gana,
lo que mides es el montaje, no la idea.

Las doce celdas están entre −0,005 y +0,067 bruto, ninguna pasa de z 2,25, y
las doce son negativas en neto (−0,15 a −0,21). El coste es el de siempre:
el stop es un barrido de sesión, así que se lleva el 15-20 % del riesgo.

### Un fallo por el camino, y para qué sirvió el control

La primera versión daba **z +21,23** en la celda de control. Eso no es un
hallazgo, es una mirada al futuro: estaba tomando el rango de la sesión de
Nueva York **del mismo día**, que ocurre *después* de la sesión asiática que
pretendía operar.

Arreglado tomando el día anterior, y añadida una aserción de causalidad
general — la ventana del rango tiene que terminar antes de que empiece la
ventana de operativa, o la celda no se calcula. Ese guardia habría cazado el
fallo solo, sin necesidad de que el número fuera absurdo.

Es la razón de poner controles: no para adornar el resultado, sino porque el
control es lo que se rompe primero cuando el código está mal.

## 2 · La lógica de sesiones

    "price accumulates during Asia, manipulates during London, distributes
     during New York ... but if price EXPANDS during Asia, then London is
     more likely to accumulate and the manipulation happens in New York"

Esto no necesita coste, ni entrada, ni objetivo. Es una frecuencia: ¿dónde
se forma el máximo y el mínimo del día? Clasificando Asia por su anchura
relativa a su propia mediana de 20 días:

              asia     n |  alto ASIA  alto LON  alto NY |  bajo ASIA  bajo LON  bajo NY
        ASIA ANCHA  2791 |    36,8 %    14,5 %   48,7 % |    40,2 %    16,0 %   43,7 %
     ASIA ESTRECHA  2573 |    22,4 %    18,3 %   59,3 % |    26,2 %    20,6 %   53,2 %
            normal  3089 |    28,3 %    19,9 %   51,8 % |    32,5 %    18,1 %   49,3 %

**La afirmación está al revés.** Dice que Asia ancha empuja la manipulación a
Nueva York. Los datos dicen lo contrario: Asia ancha → NY 48,7 %; Asia
estrecha → NY **59,3 %**.

Y lo que de verdad mueve la tabla es aritmética, no flujo de órdenes: cuando
Asia es ancha, el extremo del día se queda en Asia más a menudo (36,8 % contra
22,4 %). Un rango más ancho tiene más probabilidad de contener el extremo del
día. Eso es todo lo que hay.

### Un dato que conviene retener

Mirando las tres filas: **Londres se queda el máximo del día entre el 14 % y
el 20 % de los días. Nueva York, entre el 44 % y el 59 %.**

La afirmación de fondo de todo el material ICT/SMC —"Londres forma el máximo o
el mínimo del día"— **es falsa en estos datos.** Nueva York lo hace unas tres
veces más a menudo, y en el peor de los casos Asia también gana a Londres.

## Conclusión

- El rango CRT dinámico por sesión **no tiene ventaja**: la celda primaria es
  +0,0003 con z +0,02, y el control de detección la supera.
- La lógica de sesiones **está invertida** respecto a lo que afirma, y el
  efecto que sí existe es el trivial de que un rango ancho contiene el extremo.
- Londres no es la sesión de la manipulación. Es la que menos veces se queda
  con el extremo del día.
