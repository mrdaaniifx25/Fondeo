# Resultado · el nivel ya tocado

Ejecutado el 28 de agosto de 2026 según `docs/PREREGISTRO_asia_toques.md`.
Una sola pasada. `bt/asia_toques.py`.

## El contraste principal no sale

```
PRINCIPAL · 2020-2025
                              n   días     %TP   riesgo   NETA/día       z
  nivel YA tocado           349    302   29.5%     8.7p     -0.330   -3.98
  primera visita          1.731  1.414   31.1%     6.8p     -0.294   -7.53
  DIFERENCIA                                                -0.036   -0.39   AL REVÉS
```

La predicción firmada era que la diferencia sería positiva. Sale **negativa y
sin fuerza**: z −0,39. Y no hay ni rastro de gradiente en el acierto:

```
  toques   0    1-2    3-5    6+
  %TP    31,1   31,2   30,8   25,0        (geometría de un 1:2 = 33,3 %)
```

En enero-mayo de 2026 la diferencia sale con el signo predicho (+0,437) pero
son 15 disparos y z +1,11. Eso no es evidencia de nada.

**La hipótesis, tal como la firmé, queda descartada.** El control pasa: los
nueve casos de la baraja salen a 0 toques en el backtest, igual que en el
diagnóstico, así que el resultado no es un fallo de implementación.

## Segundo vistazo, exploratorio

Su descripción hablaba de una **ruptura** previa que pierde fuerza, no de un
simple toque. Contando cierres previos al otro lado del nivel, el neto es aún
peor (diferencia −0,399, z −3,79). Pero el bruto dice otra cosa:

```
2020-2025 · BRUTO, sin spread
  cierres      n     %TP   riesgo   R BRUTA  z bruta  c* (pips)  spread/riesgo
  0        1.646   30,3%     7,4p    -0,073    -0,11      -0,41         16 %
  1-3        124   31,5%     5,3p    -0,039    -0,26      -0,11         22 %
  4-9        115   25,2%     6,2p    -0,226    -1,90      -0,52         19 %
  10+        195   38,5%     3,6p    +0,165    +1,43       0,26         33 %
```

El grupo de niveles ya rotos diez veces o más **acierta el 38,5 %**, por encima
del 33,3 % que da la pura geometría de un 1:2, y es el único con bruta positiva.
Es la dirección que él describía.

Muere por el coste. Esas entradas quedan a 3,6 pips del nivel, así que un
spread de 1,2 pips es el 33 % del riesgo. El coste de equilibrio es de
**0,26 pips**.

```
  spread   % del riesgo   neta/día      z   euros/mes a 150 €
    0,2p            6 %     +0,020   +0,18              +7 €
    0,4p           11 %     -0,112   -0,95             -43 €
    0,6p           17 %     -0,244   -1,91             -93 €
    1,2p           33 %     -0,639   -3,82            -244 €
```

Advertencia: z +1,43 en bruto tampoco es significativo, y este grupo aparece
**después** de que el contraste preregistrado fallara. Es orientación, no
resultado.

## Lo que cambia esto

La pregunta deja de ser «¿tiene razón en lo que ve?» y pasa a ser **«cabe esta
operación dentro de su coste?»**. Con entradas de 3-4 pips de riesgo, el spread
decide el signo, no el criterio.

Todo el proyecto lleva asumiendo **1,2 pips** de coste. Nunca se ha verificado
contra su bróker. Su agosto, recalculado:

```
  spread 0,2p  ->  +31,11 R   (+4.667 €)
  spread 0,4p  ->  +29,68 R   (+4.451 €)
  spread 1,2p  ->  +23,93 R   (+3.590 €)
```

Sobre su mes cambia poco porque acertó mucho. Sobre seis años de operaciones a
33,3 % lo cambia todo.

**Siguiente paso: medir el coste real** — spread medio en EURUSD entre las 08:00
y las 11:30 más comisión por lote, en la cuenta que vaya a usar. Sin ese número
ningún backtest de entradas de 3 pips significa nada.
