# Resultado · la estrategia del vídeo (@Elpsicologodeltrading)

Pre-registro: `docs/PREREGISTRO_mean_reversion_video.md`, escrito **antes** de
medir. Código: `bt/mean_reversion_video.py`, `bt/mean_reversion_pips.py`.

EUR/USD M15, 2021-2026, 137.046 velas. Salidas resueltas minuto a minuto.

---

# Veredicto

**La filosofía del vídeo es correcta. La tabla de resultados no.**

Y el motivo es exactamente el mismo muro de siempre, pero esta vez se puede
decir con un número que no admite discusión:

```
  ventaja bruta de su señal   +0,51 a +0,87 pips por operación
  coste ida y vuelta           0,70 pips
```

---

## 1 · Lo que acierta, y no es poco

Su sección 1, «La filosofía», **es verdad y está medida**. La reversión a la
media en EUR/USD intradía existe: su señal (banda + RSI < 30 + vela de rechazo)
da un bruto positivo en **once de las doce** configuraciones que he probado.

Y coincide con lo que yo había medido por mi cuenta dos horas antes con otra
señal distinta (`RESULTADOS_scalping.md`, RSI(2) en M5, n = 23.503): el mismo
efecto, el mismo tamaño.

**Dos señales independientes apuntando al mismo sitio. El efecto es real.**

## 2 · En pips, que es como hay que mirarlo

Mirarlo en R confunde: al estrechar el stop, la cifra en R crece sin que haya
ni un euro más. **El coste son 0,7 pips siempre.** Así que lo que decide es la
ventaja en pips.

```
     k  stop     n  ops/año  acierto  BRUTO pips      t  NETO pips   dentro    fuera
   1,5     7  1131      200    29,2%       0,508   1,34     -0,192   -0,467    0,519
   1,5    10  1091      193    36,7%       0,542   1,20     -0,158   -0,335    0,293
   1,5    15  1030      182    46,1%       0,673   1,20     -0,027    0,075   -0,285
   1,5    20   983      174    51,6%       0,348   0,53     -0,352   -0,133   -0,902
   1,5    30   903      160    57,9%      -0,631  -0,78     -1,331   -0,737   -2,840
   1,5    45   830      147    62,3%      -0,826  -0,85     -1,526   -1,200   -2,353
```

**Ninguna celda es positiva en los dos tramos.** Y el mejor estadístico de todos
es **t = 1,34**, que no llega ni a la mitad del listón.

## 3 · El hallazgo que explica su tabla entera

Mire la columna del acierto según se ensancha el stop:

```
  stop  7p -> 29,2 %      stop 20p -> 51,6 %
  stop 10p -> 36,7 %      stop 30p -> 57,9 %
  stop 15p -> 46,1 %      stop 45p -> 62,3 %
```

**Su 61 % de acierto es alcanzable y es verdad.** Sale con un stop de unos
**45 pips**.

Y justo ahí, con ese stop, la ventaja bruta es **−0,826 pips**. Negativa.

> **El acierto alto no se gana: se compra ensanchando el stop, y se paga con
> el dinero.** Es la misma operación con otra contabilidad.

Su ficha dice «STOP: detrás del extremo reciente», que en M15 son **7,5 pips de
mediana** (lo he medido). Con ese stop el acierto es **29-33 %**, no 61 %. Las
dos cosas que dice su ficha no pueden pasar en la misma operación.

## 4 · Sus tres cifras no encajan entre ellas

Ya lo dejé escrito en el pre-registro, antes de medir nada:

```
  acierto 61 % y pago 1,25  ->  PF = 0,61 x 1,25 / (0,39 x 1) = 1,96
  su ficha dice PF 1,48
  para PF 1,48 con 61 % de acierto, el pago tiene que ser 0,95, no 1,25
```

Las tres no pueden ser verdad a la vez. **En su descargo: la propia ficha pone
«Ejemplo orientativo»**, así que no está publicando un backtest. Es una
ilustración, y como ilustración de la filosofía está bien.

## 5 · Lo nuevo que sí probé: gestión de la posición

Era la única dimensión del proyecto sin explorar. Objetivo en la media móvil
**que se mueve**, y parciales:

```
  k 1,5   A objetivo EMA20 congelada   n 1122  bruto +0,1265 R  neto +0,0215  z +0,41
  k 1,5   B objetivo EMA20 dinámica    n  730  bruto +0,1375 R  neto +0,0305  z +0,56
  k 1,5   C parcial 50 % en la media   n  730  bruto +0,0925 R  neto -0,0145  z -0,29
  k 1,5   D control objetivo 1R        n 1131  bruto +0,0739 R  neto -0,0311  z -1,05
  k 1,5   E control objetivo 2R        n 1122  bruto +0,1033 R  neto -0,0017  z -0,04
```

- **El objetivo dinámico bate al congelado** (+0,1375 contra +0,1265) y los dos
  baten a los objetivos fijos. Es el primer indicio del proyecto de que
  **adaptar la salida al mercado aporta algo**. Pero con z +0,56 no es un
  resultado, es una dirección.
- **Los parciales empeoran**: de +0,1375 a +0,0925. Cerrar media posición en la
  media te quita la parte buena y te deja la mala. Medido, no opinado.

## 6 · Qué haría falta para que ganase

La ventaja bruta es de **0,5 a 0,9 pips**. Luego:

```
  coste 0,3 pips  ->  neto +0,37 pips/op  ->  unos +19 EUR/mes sobre 10.000
  coste 0,7 pips  ->  neto -0,03 pips/op  ->  -1 EUR/mes. Cero.
  coste 1,4 pips  ->  neto -0,73 pips/op  ->  -37 EUR/mes
```

**Otra vez el mismo número.** Como en `RESULTADOS_scalping.md`: todo depende del
peaje de su bróker, y la frontera está por debajo de 0,7 pips.

## 7 · Lo que me salió como había predicho, y lo que no

Predije: acierto alto, bruto positivo, neto negativo.

- **Bruto positivo: acertado** (+0,51 a +0,87 pips, 11 de 12 celdas).
- **Neto negativo o cero: acertado** (ninguna celda positiva en los dos tramos).
- **Acierto alto: fallé con el stop de la ficha.** Predije 60-70 % y con el stop
  «detrás del extremo reciente» sale **29-33 %**. El 61 % existe, pero con un
  stop seis veces más ancho, y ahí el bruto ya es negativo.

## 8 · Conclusión para él

Esta estrategia **no es un fraude y no es una tontería**: apunta a un efecto
real que yo mismo he medido por separado. Lo que pasa es que ese efecto vale
**medio pip**, y el peaje normal cuesta **siete décimas**.

Si la quiere operar, está en el mismo sitio que todo lo demás: **un juego
justo**, unas 180 operaciones al año en M15. No le va a dar 300 €/mes. Tampoco
se los va a quitar.
