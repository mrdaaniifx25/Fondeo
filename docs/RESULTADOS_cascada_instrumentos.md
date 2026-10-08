# Resultado · la cascada en siete instrumentos

Ejecutado el 29 de agosto de 2026 según `docs/PREREGISTRO_cascada_instrumentos.md`.
`bt/cascada_multi.py`. Mismo código, sólo cambia el fichero de precios.

## No replica

```
TODO EN BRUTO, sin suponer ningún coste
              n   desde     %TP     R/op  bruta/d      z   stop mediano       c*
  EURUSD  1.557    2020   35,2%   +0,085   +0,085  +2,35    5,2 pips      0,37 pips
  GBPUSD  1.531    2020   33,6%   +0,026   +0,026  +0,71    6,1 pips      0,13 pips
  USDJPY  1.539    2020   30,0%   -0,051   -0,051  -1,47    6,8 pips     -0,29 pips
  XAUUSD    722    2023   30,6%   -0,043   -0,043  -0,83  190,2 centavos -4,59 centavos
  DAX       691    2023   32,6%   -0,000   -0,000  -0,00   11,0 puntos    0,00 puntos
  NAS100  1.563    2020   32,6%   -0,003   -0,003  -0,08   15,2 puntos   -0,03 puntos
```

(SP500 no llegó a terminar en el tiempo de ejecución; no cambia la lectura.)

La geometría de un 1:2 da 33,3 %. **Cinco de los seis instrumentos nuevos están
en el 30-33,6 %**, es decir, en el azar o por debajo. Sólo EURUSD se despega, y
con z +2,35 cuando Bonferroni para seis contrastes pide **2,64**.

## Qué significa

Un efecto que aparece en un instrumento de siete, sin cruzar el umbral de
multiplicidad, y que en ese único instrumento no llega a cubrir su propio coste,
**es indistinguible del ruido**.

Esto cierra la familia entera de los niveles de sesión. No es que el coste se la
coma: es que probablemente no había nada que comerse.

## La aritmética que explica todo el proyecto

```
  coste fijo: 1,43 pips por operación

      stop    coste/riesgo   acierto extra necesario sólo para empatar
        5p          28,6 %                     9,5 puntos
       10p          14,3 %                     4,8 puntos
       20p           7,2 %                     2,4 puntos
       50p           2,9 %                     1,0 puntos
      100p           1,4 %                     0,5 puntos
```

Todo lo que hemos probado deja stops de **4 a 7 pips**, porque todo nace de un
barrido y la mecha de un barrido mide lo que mide. En ese régimen hay que batir
al azar en **casi diez puntos porcentuales** sólo para empatar. Ninguna
estrategia pública lo hace.

Con stops de 50 pips bastaría con un punto. La misma ventaja hipotética, veinte
veces más fácil de cobrar.

Referencia: el recorrido diario mediano del EURUSD son **61 pips**; el semanal,
157.

## La conclusión del proyecto

Dos fracasos distintos y ninguno se arregla ajustando parámetros:

- **Los niveles de sesión**: stops de 5 pips, coste del 29 %. Aunque hubiera
  ventaja no cabría, y sobre siete instrumentos parece que no la hay.
- **El CRT**: stops de 19 pips, coste del 7,8 %, cabe de sobra. Pero acierta el
  41,6 % cuando su geometría pide 43,1 %.

**Lo único que queda sin explorar es el otro extremo de la aritmética**:
operativa sobre estructuras de varios días, con stops de 40-100 pips, donde 1,43
pips es el 1-3 % del riesgo en vez del 29 %. Nada de lo hecho en este proyecto
toca ese régimen.
