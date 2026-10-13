# Resultados · filtrar por stop mínimo

Pre-registro: `docs/PREREGISTRO_stop_minimo.md`, subido en `074ee45` **antes** de
medir. Código: `bt/stop_minimo.py`. CRT en H4, EURUSD + oro + DAX,
**4.269 operaciones**, 5,6 años.

## Veredicto en una línea

**Positivo pero indistinguible del procedimiento.** Ninguna de las 15 celdas
tiene el intervalo de confianza fuera del cero. El criterio completo **no se
cumple**, que es exactamente lo que decía la predicción.

## Las 15 celdas

```
  R:R     k      n   acierto            exceso  coste medio                   NETA
--------------------------------------------------------------------------------------------
  1.5  0.00  4,269     43.2%   +3.2 [ +1.8, +4.7]        11.5%   -0.0340 [-0.0715,+0.0034]
  1.5  0.25  3,491     43.2%   +3.2 [ +1.6, +4.9]         7.6%   +0.0046 [-0.0365,+0.0458]
  1.5  0.50  1,983     43.8%   +3.8 [ +1.6, +6.0]         5.1%   +0.0435 [-0.0111,+0.0981]
  1.5  0.75    937     44.4%   +4.4 [ +1.2, +7.6]         3.8%   +0.0716 [-0.0080,+0.1512]
  1.5  1.00    408     41.9%   +1.9 [ -2.9, +6.7]         2.9%   +0.0187 [-0.1013,+0.1387]

  2.0  0.00  4,269     36.8%   +3.4 [ +2.0, +4.9]        11.5%   -0.0125 [-0.0560,+0.0311]
  2.0  0.25  3,491     36.6%   +3.2 [ +1.6, +4.8]         7.6%   +0.0214 [-0.0266,+0.0693]
  2.0  0.50  1,983     36.0%   +2.7 [ +0.6, +4.8]         5.1%   +0.0294 [-0.0340,+0.0928]
  2.0  0.75    937     35.8%   +2.4 [ -0.7, +5.5]         3.8%   +0.0343 [-0.0578,+0.1264]
  2.0  1.00    408     32.6%   -0.7 [ -5.3, +3.8]         2.9%   -0.0511 [-0.1879,+0.0856]

  3.0  0.00  4,269     27.3%   +2.3 [ +1.0, +3.6]        11.5%   -0.0235 [-0.0770,+0.0300]
  3.0  0.25  3,491     26.7%   +1.7 [ +0.3, +3.2]         7.6%   -0.0070 [-0.0657,+0.0517]
  3.0  0.50  1,983     25.6%   +0.6 [ -1.4, +2.5]         5.1%   -0.0281 [-0.1049,+0.0487]
  3.0  0.75    937     24.7%   -0.3 [ -3.1, +2.4]         3.8%   -0.0522 [-0.1626,+0.0583]
  3.0  1.00    408     20.6%   -4.4 [ -8.3, -0.5]         2.9%   -0.2055 [-0.3628,-0.0483]
```

Nueve celdas de quince dan neta positiva. **Cero tienen el intervalo limpio.**

## El diagnóstico, que es lo que de verdad enseña algo

Declarado en el pre-registro antes de medir: dónde vive el exceso, por tamaño de
stop, **sin filtrar**, a R:R 2,0.

```
    stop/ATR      n   acierto            exceso  coste medio       neta
------------------------------------------------------------------------
 0.00-0.25      778     37.5%   +4.2 [ +0.8, +7.6]        29.0%    -0.1644
 0.25-0.50    1,508     37.3%   +4.0 [ +1.6, +6.4]        10.9%    +0.0109
 0.50-0.75    1,046     36.2%   +2.9 [ -0.0, +5.8]         6.2%    +0.0250
 0.75-1.00      529     38.2%   +4.9 [ +0.7, +9.0]         4.5%    +0.1001
 1.00-1.50      334     33.2%   -0.1 [ -5.2, +5.0]         3.1%    -0.0338
```

Queda resuelta la pregunta que abría la prueba. **El exceso es el mismo en todos
los tamaños de stop hasta 1 ATR** (+4,2 / +4,0 / +2,9 / +4,9) mientras el coste
se desploma del **29,0 %** al **4,5 %** del riesgo. La hipótesis contraria —que
la señal viviese en los stops diminutos— queda descartada.

El tramo 0,00-0,25 ATR es el que hundía la media: acierta igual que los demás y
pierde −0,16 R por operación, porque paga **29 céntimos de coste por cada euro
arriesgado**. Por encima de 1 ATR el exceso desaparece (−0,1): el stop ya es tan
ancho que el patrón no lo distingue del ruido.

## Partido en dos mitades

Cada celda partida por su propia fecha mediana (en torno a agosto de 2024):

```
  R:R 1.5 k 0.5  | 1a n   991 exceso  +4.8 neta +0.0568 [-0.0208,+0.1343] | 2a n   992 exceso  +2.7 neta +0.0302 [-0.0467,+0.1072]
  R:R 1.5 k 0.75 | 1a n   468 exceso  +6.2 neta +0.1056 [-0.0076,+0.2187] | 2a n   469 exceso  +2.6 neta +0.0378 [-0.0742,+0.1497]
  R:R 2.0 k 0.5  | 1a n   991 exceso  +2.7 neta +0.0174 [-0.0724,+0.1072] | 2a n   992 exceso  +2.7 neta +0.0413 [-0.0482,+0.1309]
  R:R 2.0 k 0.75 | 1a n   468 exceso  +1.7 neta +0.0030 [-0.1269,+0.1329] | 2a n   469 exceso  +3.1 neta +0.0655 [-0.0653,+0.1962]
```

**Las ocho mitades positivas.** Ninguna con el cero fuera. No es una prueba, pero
sí es lo contrario de lo que hace un sobreajuste, que suele dejar una mitad
buena y la otra en negativo.

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. neta > 0 con el IC sin tocar el cero | **NO.** Cero celdas de quince |
| 2. y por encima de +0,038 (sesgo de selección) | **Sí**, la mejor da +0,0716 |
| 3. el exceso no sube al filtrar | **Con matiz.** A R:R 2,0 no sube (+3,4 → +2,4). A R:R 1,5 sube algo (+3,2 → +4,4) |
| 4. aguanta partido en dos mitades | **Sí**, las ocho positivas |

Falla el primero, que es el que manda. Un intervalo que toca el cero significa
que estos datos **no distinguen** este resultado de la casualidad.

## Y lo que importa de verdad: cuánto sería en dinero

Suponiendo que la neta fuese real —que es justo lo que no se ha demostrado— y
con riesgo **0,25 %** por operación, el único nivel que respeta su límite del
10 % de caída:

```
  R:R     k      n   anios  ops/anio   R/anio   %/anio  €/mes s/50k
------------------------------------------------------------------------
  1.5  0.25  3,491     5.6       620     +2.9    +0.7%         +30€
  1.5  0.50  1,983     5.6       353    +15.3    +3.8%        +160€
  1.5  0.75    937     5.6       168    +12.0    +3.0%        +125€
  1.5  1.00    408     5.6        73     +1.4    +0.3%         +14€
  2.0  0.25  3,491     5.6       620    +13.2    +3.3%        +138€
  2.0  0.50  1,983     5.6       353    +10.4    +2.6%        +108€
  2.0  0.75    937     5.6       168     +5.7    +1.4%         +60€
```

**El mejor caso son 160 € al mes sobre una cuenta de 50.000.** El objetivo son
750 €. Para llegar ahí con un 3,8 % anual harían falta **237.000 € fondeados**, o
subir el riesgo por operación a un nivel que rompe el límite del 10 %.

Y eso es el **mejor caso**: la celda elegida entre quince, con el intervalo
tocando el cero, sobre 1.983 operaciones que son tres instrumentos a la vez.

## Qué queda

El resultado no se puede afirmar ni descartar con estos datos. Las dos únicas
salidas honestas:

1. **Datos nuevos.** Los 26 ZIP de DAX y oro de 2010-2022 multiplicarían la
   muestra por tres y la respuesta sería limpia en un sentido o en otro.
2. **Registro en papel.** Anotar las operaciones reales en
   `docs/registro_operaciones.html` durante unos meses.

Lo que **no** es una salida: dar por bueno el +0,0716 y operarlo. Es la mejor de
quince casillas y su intervalo llega hasta −0,008.

## Récord de predicciones

Cuatro aciertos de cinco.

| predicción | resultado |
|---|---|
| coste medio a 5-7 % con k = 0,5 | **5,1 %** ✔ |
| el exceso se mantiene en +3,0/+3,5 | se mantiene ✔ |
| la neta cruza el cero en k = 0,5 o 0,75, entre +0,01 y +0,04 | cruza ✔, pero da +0,0435 y +0,0716, por encima del rango ✘ en magnitud |
| **no** superará el umbral de +0,038 | lo supera (+0,0716) ✘ |
| dos mitades positivas, con el cero dentro en cada una | exacto ✔ |
