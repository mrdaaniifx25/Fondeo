# Resultado · el contexto de M15 y H1

Ejecutado el 28 de agosto de 2026 según `docs/PREREGISTRO_asia_contexto.md`.
Una sola pasada. `bt/asia_contexto.py`.

## Los tres contrastes pasan, y con margen

```
2020-2025                        n     días    %TP     R/op   neta/d       z
  M15 a favor                1.739   1.295   31,8%   -0,026   -0,190   -5,08
  M15 en contra                341     320   25,8%   -0,216   -1,166   -9,98
  DIFERENCIA                                                  +0,976   +7,96

  H1 a favor                 1.564   1.267   34,8%   +0,068   -0,123   -3,14
  H1 en contra                 516     463   18,6%   -0,437   -1,092  -14,22
  DIFERENCIA                                                  +0,969  +11,24

  M15 y H1 a favor           1.454   1.219   34,9%   +0,071   -0,104   -2,58
  el resto                     626     538   21,2%   -0,355   -1,014  -14,35
  DIFERENCIA                                                  +0,910  +11,19
```

Bonferroni con tres contrastes pedía |z| >= 2,39. Salen +7,96, +11,24 y +11,19,
con el signo predicho. En enero-mayo de 2026, que no se había tocado: +4,28,
+2,54 y +4,47.

**Operar contra H1 acierta el 18,6 %.** La geometría de un 1:2 da 33,3 %. Es la
única cosa en todo el proyecto que se aleja tanto del azar, y va exactamente en
la dirección que el usuario venía diciendo desde hacía días.

## Aparece la primera ventaja bruta real

```
BRUTO, sin costes                    n    días    %TP     R/op    R/día      z      c*
  2020-2025 sin filtro           2.080   1.441   30,8%   -0,057   +0,024  +0,72  -0,23p
  2020-2025 M15 y H1 a favor     1.454   1.219   34,9%   +0,071   +0,140  +3,52  +0,41p
  2026 ene-may filtrado             89      79   39,3%   +0,268   +0,291  +1,82  +1,59p
  los dos juntos, filtrado       1.543   1.298   35,2%   +0,082   +0,149  +3,87  +0,48p
```

Es la primera vez en todo el proyecto que un corte preregistrado da ventaja
bruta con z por encima de 3. 35,2 % de acierto contra el 33,3 % geométrico.

## Y aun así no llega

El coste de equilibrio del conjunto filtrado es de **0,48 pips**. El coste real
medido es **1,43**. Falta un factor de tres.

Añadir el arranque a las 09:00 no lo salva:

```
  M15 y H1 a favor, desde las 09:00 · n=729 · %TP 34,3 % · c* 0,53p
    con 0,50p de coste -> +0,039/día (z +0,72)
    con 1,00p         -> -0,029/día (z -0,54)
    con 1,43p         -> -0,088/día (z -1,60)
```

## Lo que queda establecido

1. **El contexto de temporalidad mayor es real y es grande.** Lo dijo él, se
   preregistró y pasó en las dos muestras. Operar contra H1 es un desastre.
2. **La ventaja bruta existe pero es pequeña**: unos 0,08 R por operación.
3. **El coste se la come tres veces.** Con entradas de 3-7 pips de riesgo y
   1,43 pips de coste, 0,08 R no sobrevive.

El problema deja de ser el criterio y pasa a ser el tamaño. Para que 0,08 R por
operación valga algo hace falta que el coste baje del 8 % del riesgo, o sea
stops de **18 pips o más** — otra operación distinta a la que él hace.

## Retractación

En el mensaje anterior dije que entrar más barato dentro de la vela movía la
geometría del 33 % al 50 %. **Es falso.** Con el objetivo definido como 2 veces
la distancia al stop, la probabilidad es 1/3 sea cual sea la entrada: es la
ruina del jugador, `riesgo / (riesgo + 2·riesgo)`. Los 2.080 disparos lo
confirman — el acierto es plano entre stops de 4 y de 11 pips.

Lo que sí queda de aquella medición: él entra en el 0,51 del rango de la vela y
la regla en el 0,82. Eso es una descripción correcta de dónde entra cada uno.
Lo que era falso es el beneficio que le atribuí. Y la diferencia de recorrido
posterior (38 % contra 52 %) sale de 16 operaciones: p = 0,18, ruido.
