# Resultado · el mismo sistema en oro y DAX

El sistema de `docs/RESULTADOS_sistema_eurusd_intradia.md`, **sin tocar un solo
parámetro**, aplicado a oro (2023-2026) y DAX (2023-2026).
Código: `bt/sistema_tres_instrumentos.py` y `bt/sistema_oro_ny.py`.

---

## La tabla

```
  instrumento  ventana             n   riesgo  coste  acierto  PFbru PFneto   R neta      z     B&H  exceso
  EURUSD       Londres 08-12    4133     10,6   7,0%    40,9%   0,98   0,87  -0,0797  -2,59 -0,0670 -0,0128
  EURUSD       NuevaYork 08-12  3941     13,3   5,6%    42,8%   0,96   0,86  -0,0759  -2,80 +0,0031 -0,0790
  oro          Londres 08-12    2584    475,5   2,7%    41,6%   0,99   0,94  -0,0322  -0,79 +0,0021 -0,0343
  oro          NuevaYork 08-12  2399    732,8   1,9%    47,6%   1,09   1,05  +0,0213  +0,66 +0,0079 +0,0134
  DAX          Londres 08-12    2538     39,7   3,5%    41,7%   0,96   0,90  -0,0546  -1,49 -0,0284 -0,0262
  DAX          NuevaYork 08-12  2399     42,8   3,1%    41,4%   0,89   0,84  -0,0884  -2,51 +0,0113 -0,0997
```

*(Nota: probé también «Fráncfort 09-13» y da resultados idénticos a Londres
08-12. No es casualidad ni error: Fráncfort va siempre exactamente una hora por
delante de Londres, así que 09-13 Berlín **es** 08-12 Londres, siempre. No
existe una «sesión de Fráncfort» separable. Las filas duplicadas se han
eliminado de la tabla.)*

## El coste deja de ser la excusa — y sigue sin haber nada

Esto es lo primero que aporta la prueba. En EUR/USD el coste era el 7,0 % del
riesgo. En oro es el **1,9 %**, porque el riesgo mediano son **7,33 $** con una
horquilla de 0,12 $:

```
  EURUSD   coste 6,5 % del riesgo
  DAX      coste 3,4 %
  oro      coste 2,5 %
```

Si el problema fuera la horquilla, el oro tendría que funcionar. **El profit
factor bruto del oro en Londres es 0,99.** Justo. Sin coste de por medio, no hay
nada que cobrar.

## Los placebos, otra vez

```
  instrumento      n      REAL  invertida  siempre largo  comprar y aguantar  % largos
  EURUSD       12207   -0,0131    +0,0166        -0,0344             -0,0444       48%
  oro           7567   +0,0095    -0,0136        +0,0292             +0,0040       59%
  DAX           7475   -0,0317    +0,0360        -0,0295             -0,0157       59%
```

**En EUR/USD y DAX, la dirección invertida gana a la real.** Y fíjese en la
simetría casi exacta: −0,0131/+0,0166 y −0,0317/+0,0360. Eso es la firma de una
señal con cero información: el resultado y su espejo son el mismo número con
otro signo.

**Y en oro, «siempre largo» (+0,0292) gana al sistema (+0,0095).** El filtro de
dirección por EMA diaria **resta** valor frente a estar simplemente comprado en
un metal que subió un 143 %.

## La única celda positiva, mirada de cerca

Oro · Nueva York 08-12 es la única con profit factor neto por encima de 1.
Merece el escrutinio entero:

```
  tramo         n  acierto  PFbru  PFnet   R neta      z      B&H   exceso  €/mes
  completa   2399    47,6%   1,09   1,05  +0,0213  +0,66  +0,0079  +0,0134   +179
  2023-2024  1307    47,5%   1,07   1,01  +0,0070  +0,16  +0,0050  +0,0020    +58
  2025-2026  1092    47,6%   1,11   1,08  +0,0385  +0,81  +0,0114  +0,0271   +327
  2023        545    48,4%   1,11   1,04  +0,0189  +0,30  +0,0471  -0,0282   +144
  2024        762    46,9%   1,04   1,00  -0,0015  -0,02  -0,0251  +0,0236    -13
  2025        632    47,2%   1,07   1,04  +0,0185  +0,28  +0,1740  -0,1555   +151
  2026        460    48,3%   1,16   1,14  +0,0660  +0,97  -0,2119  +0,2779   +590

  placebos:  invertida -0,0532  ·  siempre largo -0,0251  ·  comprar y aguantar +0,0079
```

**Lo que tiene a favor**, y es más de lo que ha tenido ninguna celda en tres
meses: los cuatro años son positivos o cero, ninguno la carga sola, y bate a los
tres controles —invertida, siempre largo y comprar y aguantar—.

**Lo que la mata:**

```
  SUELO: con n=2.399 y desviación 1,05, para z=+2 haría falta R neta >= +0,0429
  Observado: +0,0213.  La mitad justa.
```

Y sobre todo esto, que es lo decisivo:

```
  z de la mejor de mis 6 celdas:                      +0,66
  E[máximo de 6 celdas de puro ruido]:                +1,27
```

**La mejor celda de las seis salió por debajo de lo que produce el azar
eligiendo la mejor de seis.** No es que no alcance la significación: es que
rinde *menos* que la selección sola. Con esa referencia, la rejilla entera es
compatible con cero en todas partes.

## Respuesta a la pregunta

**No, no cambia nada.**

- De seis celdas, cinco tienen profit factor neto por debajo de 1.
- La sexta está en 1,05 con z +0,66, por debajo del +1,27 que da seleccionar la
  mejor de seis al azar.
- El placebo invertido gana en dos de los tres instrumentos.
- En oro, estar simplemente largo gana al sistema.
- Y el coste, que era el sospechoso natural, baja del 7,0 % al 1,9 % sin que
  aparezca nada: el bruto es 0,99.

## Lo único que dejaría abierto

Para resolver la celda del oro en Nueva York harían falta **unas cuatro veces
más operaciones**, es decir el histórico de oro de 2010-2022 que no tengo. Con
600 días no se puede, y decir lo contrario sería inventar.

Si algún día aparecen esos datos, ésa es la celda que mediría primero. No porque
crea que va a salir —el argumento del máximo de seis me dice que no— sino porque
es la única donde la respuesta no la sé.
