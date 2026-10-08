# Liquidez simple, doble y triple

La última afirmación viva del material de bctrades, y la única con un gradiente:

> «El precio puede tomar la liquidez las veces que quiera mientras siga cerrando
> dentro de la vela base. La **doble** confirma la estructura y **aumenta la
> probabilidad**. La **triple** la refuerza y la aumenta **todavía más**.»

Un gradiente ordenado 1 → 2 → 3 es difícil de fabricar por azar. Por eso valía
la pena medirla aparte aunque la celda entera «cierra dentro» ya hubiera salido
al 50 %.

## El sesgo que había que matar primero

Con cada barrido extra el extremo se aleja, así que **el stop se aleja solo**.
Con el objetivo fijo en el extremo opuesto de la vela base, eso sube el
porcentaje de acierto **sin ninguna ventaja, solo por geometría**. Y se confirma
que el efecto es real: el coste en unidades de riesgo baja de 7,0 % a 6,1 % a
5,2 % conforme sube el contador, porque el stop es más ancho.

Por eso todo se mide dos veces: la operación natural, y una **carrera simétrica**
de ±1 ATR desde la misma entrada, con la misma distancia para k = 1, 2 y 3. Si
el gradiente fuera real, en la simétrica también tendría que aparecer.

## El resultado · H4, cuatro instrumentos, 2020-2026

**Cierre dentro del rango de la vela base**

| | n | riesgo mediano | coste en R | **R bruta** | IC 95 % | R neta | carrera simétrica |
|---|---|---|---|---|---|---|---|
| simple | 9.197 | 19,2 | 7,0 % | **+0,085** | [+0,052, +0,118] | −0,023 | 50,21 % |
| doble | 1.866 | 22,3 | 6,1 % | +0,067 | [+0,009, +0,125] | −0,015 | 50,40 % |
| triple+ | 508 | 25,4 | 5,2 % | **−0,029** | [−0,137, +0,080] | −0,093 | 47,32 % |

**Cierre dentro del cuerpo** (su versión más reciente, más estricta)

| | n | **R bruta** | IC 95 % | R neta | carrera simétrica |
|---|---|---|---|---|---|
| simple | 4.869 | +0,059 | [+0,023, +0,095] | −0,024 | 50,30 % |
| doble | 591 | +0,095 | [−0,006, +0,195] | +0,025 | 51,19 % |
| triple+ | 98 | **−0,201** | [−0,434, +0,032] | −0,260 | 46,81 % |

## No hay gradiente, y el tercer escalón va del revés

| diferencia | rango | cuerpo |
|---|---|---|
| doble − simple | −0,018 R (z −0,53) | +0,036 R (z +0,66) |
| **triple+ − simple** | **−0,113 R (z −1,96)** | **−0,260 R (z −2,16)** |
| triple+ − doble | −0,096 R (z −1,52) | −0,296 R (z −2,28) |

De simple a doble no pasa nada: ruido en las dos definiciones, y con el signo
cambiado entre una y otra. Y de ahí a triple **baja con significación en ambas**.

Esto no es «no hemos encontrado el efecto». Es que **justo donde ellos dicen que
la probabilidad es más alta, es donde peor sale**, y con las dos definiciones de
«cerrar dentro». La carrera simétrica dice lo mismo por su cuenta: 50,21 % /
50,40 % / 47,32 %.

## Lo que sí ha salido, y hay que decirlo

La celda **simple** tiene ventaja bruta positiva y sólida: **+0,085 R por
operación sobre 9.197 casos**, intervalo [+0,052, +0,118], que no toca el cero.
Y es el CRT en su forma más desnuda: vela base, la siguiente barra un extremo y
cierra dentro, entras al cierre, objetivo en el extremo opuesto, stop en el
barrido. Sin killzones, sin Fibonacci, sin mitigación, sin nada. Sale mejor que
el CRT canónico completo (+0,0248 R), que es un dato interesante en sí mismo.

Pero el riesgo mediano es de 19,2 unidades y el coste se lleva el **7,0 %**.
Neta: **−0,023 R**.

La misma pared de siempre, medida una vez más: ventaja bruta real de +0,085 R,
coste de 0,070 R, resultado −0,023 R.

## Salvedades

Las secuencias de velas base contiguas se solapan en el tiempo, así que los
intervalos de confianza son algo optimistas. No cambia el sentido de nada: las
dos conclusiones —no hay gradiente, y la ventaja bruta de la celda simple no
llega al coste— van en direcciones que el solapamiento no fabrica.

La celda triple+ tiene 508 casos con cierre en rango y 98 con cierre en cuerpo.
Con esos tamaños se descarta un efecto grande, no uno pequeño. Lo que queda
establecido es que **no hay rastro del gradiente que afirman**, y que el punto
del tercer escalón apunta al lado contrario en las dos definiciones.

## Reproducir

`bt/liquidez_multiple.py` y `bt/run_liquidez_multiple.py`.
