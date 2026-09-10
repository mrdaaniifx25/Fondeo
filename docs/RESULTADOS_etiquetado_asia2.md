# Resultados · segunda baraja ciega, y cierre de la familia

Pre-registro: `PREREGISTRO_etiquetado_asia2.md`, commit `9780296`, escrito antes
de que el usuario viera un solo corte. Fecha: 2026-08-28.

90 cortes respondidos: **37 operados, 53 pasados.**

## 1 · La prueba principal: el perfil no se replica — pero por una razón útil

Umbral fijado antes: mismo signo y z ≥ 2,39 en al menos **2 de las 3**.

| variable | v1 operados | v1 pasados | z v1 | v2 operados | v2 pasados | **z v2** | ¿replica? |
|---|---|---|---|---|---|---|---|
| el barrido cierra pasado el nivel | 0,9 p | 2,5 p | −3,85 | 3,0 p | 4,2 p | −0,71 | no |
| mecha pasada el nivel | 2,8 p | 5,5 p | −3,16 | 4,8 p | 6,8 p | −0,56 | no |
| **cuerpo de la envolvente** | 4,8 p | 2,6 p | +3,67 | **4,3 p** | **1,6 p** | **+5,80** | **SÍ** |

Replica 1 de 3. **Perfil no replicado**, según lo escrito.

Pero el detalle importa más que el veredicto: no es que su criterio fuera ruido.
Es que **no eran tres cosas, era una.** Lo del barrido corto se cayó —de z −3,85
a z −0,71—; lo del cuerpo de la envolvente subió, de z +3,67 a **z +5,80**, que
es de las señales más fuertes de todo el proyecto.

Lo que este hombre selecciona, y lo hace sin decirlo, es: **una vela de vuelta
grande.** Nada más.

## 2 · Y esa costumbre hace algo concreto

Una envolvente grande deja el extremo de la vela anterior más lejos, así que el
stop sale más ancho. Y el stop más ancho es lo único que ha decidido algo en
todo este proyecto:

| | stop mediano | el spread es… |
|---|---|---|
| los cortes que **elige** | 6,8 p | **17,6 %** del riesgo |
| los cortes que **pasa** | 3,5 p | **34,3 %** del riesgo |

Sin haberlo formulado nunca, está esquivando las operaciones en las que el
diferencial se come un tercio del riesgo. Ese es el hallazgo de la fase, y no va
sobre el barrido de Asia: va sobre él.

## 3 · Las medidas de resultado, todas compatibles con cero

| | n | riesgo | %TP | geometría | bruta | neta | z |
|---|---|---|---|---|---|---|---|
| sus entradas | 37 | 8,2 p | 18,9 % | 30,8 % | −0,027 | −0,177 | −0,82 |
| la regla, esos mismos 37 | 37 | 6,8 p | 21,6 % | 33,3 % | +0,121 | −0,074 | −0,28 |
| la regla, los 53 pasados | 53 | 3,5 p | 18,9 % | 33,3 % | −0,235 | −0,583 | −2,62 |

**Colocación** (emparejada, mismos 37): −0,148, IC95 [−0,429, +0,133], z −1,03.
Quitando los 20 empates: mejor en 6, peor en 11.

**Selección**, las dos barajas:

| | operados vs pasados | diferencia | IC95 | z |
|---|---|---|---|---|
| v1 | 26 vs 34 | −0,135 | [−0,970, +0,701] | −0,32 |
| v2 | 37 vs 53 | **+0,356** | [−0,322, +1,034] | +1,03 |
| **juntas** | 63 vs 87 | **+0,161** | [−0,365, +0,687] | **+0,60** |

Signos opuestos entre barajas y un intervalo que cruza cero de lado a lado. No
hay efecto medible en su selección — aunque en la v2, que era la baraja difícil,
el punto va claramente a su favor.

## 4 · Sus dos reservas, y por qué no tocan lo principal

Dijo dos cosas al mandar las respuestas:

> *«hay muchas que no operaría porque esperaría a las siguientes velas»*

No afecta a nada de lo anterior. La prueba principal usa sólo su decisión de
operar o pasar, y si acaso significa que su selectividad real es aún mayor
que el 41 % que se ve aquí.

> *«los TP y los SL no están ajustados del todo porque lo hago desde la tablet»*

Sólo toca la medida de colocación, que ya salía nula. La selección y el perfil
se miden aplicando la **regla mecánica** sobre los cortes que él eligió, así que
dónde puso exactamente el stop no entra. Aun así, sus stops salieron **más
anchos** que la regla en 34 de 37 — igual que en la primera baraja. Desde la
tablet no le quedaron cortos: le quedaron largos.

Entrada al cierre exacto en 36 de 37, dirección igual a la mecánica en los 37.

## 5 · Lo que le debía: la regla mecánica sobre estos 90

Escrito y comprometido antes de que respondiera, en el commit `9780296`:

```
n 90 · riesgo mediano 4,7 p · R:R 2,00
%TP 20,0 %   frente a geometría pura 33,3 %
bruta −0,089 · neta −0,374 · IC95 [−0,711, −0,037] · z −2,17
```

Marzo-julio de 2026 fue un periodo **malo** para la regla, el único tramo con
z significativo en contra de todo el proyecto. Sobre eso, sus 37 elegidos dan
−0,074 y los 53 que pasó dan −0,583. Esquivó lo peor de un periodo malo.

## 6 · La familia se cierra

Según lo pre-registrado: perfil no replicado → **se cierra el barrido de Asia**.
Dos barajas, 150 cortes, 63 operaciones suyas etiquetadas a ciegas, y ni la
selección ni la colocación dan efecto medible. Se cierra por falta de efecto,
no por prueba de ausencia: con estas n sólo se veían efectos de +0,5 R.

Lo que **no** se cierra, porque replicó a z +5,80 y es suyo:

> **Elige velas de vuelta grandes, y con eso se pone stops anchos.**

Eso vale para cualquier estrategia que opere, y explica por qué el barrido de
Asia nunca iba a funcionarle: con stops de 3 a 8 pips, el diferencial se lleva
entre el 18 y el 34 % del riesgo antes de empezar. En el CRT de H4, con sus 23
pips de stop, el mismo diferencial es el **5 %**. No es que el CRT tenga más
señal — es que ahí su forma de elegir y el coste van en la misma dirección.

## Ficheros

```
data/respuestas_asia2.txt              sus 90 respuestas, tal cual
data/etiquetado_asia2_rasgos.csv       los 90 con rasgos y su decisión
data/etiquetado_asia2_respuestas.csv   los 37 resueltos, con la mecánica al lado
data/etiquetado_asia2_mecanica.csv     la regla sobre los 90, resuelta antes
```
