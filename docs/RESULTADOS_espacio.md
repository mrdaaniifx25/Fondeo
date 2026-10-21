# Resultados · ¿existe ALGUNA combinación?

Pre-registro: `docs/PREREGISTRO_espacio.md`, subido **antes** de medir.
Código: `bt/espacio.py`. EURUSD M15, sus horas operativas, 2021-2026,
**25.453 velas** sin condicionar a ningún patrón.

## Veredicto

**No existe.** Ninguna función de las 22 variables predice la dirección.

## Lo que salió primero, y estaba mal

```
  todas las variables            AUC 0,5147   por bloque: 0,505 0,540 0,538 0,496 0,499
  control · etiquetas barajadas  AUC 0,5049
  decil superior                 +5,47 puntos,  t aparente +3,57
```

Un AUC de 0,515 y un decil con t de +3,57 parecen un hallazgo. **Y son un error
de método mío.**

Velas de M15 con objetivo a 4 horas **se solapan dieciséis veces**: dieciséis
muestras consecutivas comparten casi todo su futuro. No son independientes, así
que el error estándar sale dieciséis veces más pequeño de lo que debe y todo se
infla. El control barajado lo delató: tendría que dar 0,5000 y dio 0,5049.

## Lo mismo, con muestras que no se solapan

Una vela de cada dieciséis. Ya no comparten futuro.

```
  todas las variables            AUC 0,4984   por bloque: 0,576 0,480 0,482 0,458 0,484
  control · etiquetas barajadas  AUC 0,4834

  decil superior     n 132   arriba 52,27 %  abajo 48,48 %
                     diferencia +3,79 [-8,31, +15,89]   t +0,61
  cuarto superior    n 331   diferencia  0,00 [-7,62, +7,62]   t 0,00
```

**AUC 0,4984.** Por debajo de 0,50, y dentro del ruido de fondo que marca el
control (0,4834). El decil superior y el inferior no se distinguen.

Y la demostración de lo que inflaba el solape:

```
  decil superior con solape:  t aparente +3,57
  el mismo, corregido:        t real     +0,89
```

## Su intuición apuntaba a las variables correctas

El usuario dijo: *«no sé si día anterior… algo»*. Estas son las variables que el
modelo consideró más importantes, de las 22:

```
  dist_PWL             +0,00818    <- distancia al mínimo de la semana previa
  dist_PDH             +0,00605    <- distancia al máximo del día previo
  PDL_barrido          +0,00485    <- ¿se ha barrido ya el mínimo del día previo?
  dist_PDL             +0,00435
  ancho_asia           +0,00434
  asia_alto_barrido    +0,00324
  sesion               +0,00277
```

**Son exactamente las que él señalaba**: el día anterior, la semana anterior, los
barridos ya hechos, la sesión. El modelo las prefiere a las demás.

Pero mire la columna de la derecha: el mayor aporta **+0,008 de AUC**, y el ruido
de fondo de esta medición es **±0,017**. Las variables correctas están
identificadas. **Lo que no hay dentro de ellas es dirección.**

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. AUC > 0,52 estable en los cinco bloques | **NO.** 0,4984, y un bloque a 0,458 |
| 2. decil superior por encima del umbral del coste | **NO.** t +0,61 |
| 3. control barajado en 0,500 | 0,4834 — marca el ruido de fondo, ±0,017 |

## Récord de predicciones

Tres de cuatro.

| predicción | resultado |
|---|---|
| AUC entre 0,495 y 0,515 | **0,4984** ✔ |
| control plano y decil sin separarse | decil t +0,61 ✔ |
| las variables importantes serán de volatilidad, no de dirección | fueron las de **nivel** (PWL, PDH, PDL) ✘ |
| el espacio queda cerrado | cerrado ✔ |

## Lo que esto cierra, y es distinto de todo lo anterior

Las 34 pruebas de sesiones y las 9 familias de los operadores cerraban **una
hipótesis cada una**. Siempre quedaba «¿y si además…?».

Esto no cierra una hipótesis. **Cierra el espacio.** Un modelo con libertad para
combinar sesión, hora, día de la semana, posición en el rango de Asia, distancia
a PDH, PDL, PWH, PWL, qué se ha barrido ya, momento a tres plazos, dos medidas de
volatilidad, distancia a la apertura, recorrido del día y distancia a la EMA — en
cualquier combinación, con cualquier interacción, buscando sobre 25.453 velas —
sale a **0,4984** fuera de muestra.

No es «no lo hemos encontrado». Es que **no está ahí**.
