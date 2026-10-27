# Resultados · la baraja ciega y el filtro que salió de ella

Pre-registros: `PREREGISTRO_etiquetado_asia.md` y `PREREGISTRO_asia_filtro.md`.
Fecha: 2026-08-28. Respondidos los 60 cortes: **26 operados, 34 pasados.**

## 1 · Lo primero que hay que decir: los stops no fueron el problema

El usuario avisó de que, respondiendo desde el móvil, quizá algún stop le quedó
más justo de lo que quería. Salió al revés:

| | suyo | la regla escrita |
|---|---|---|
| stop mediano | **9,2 p** | 7,9 p |
| más ancho que la regla | **20 de 26** | |
| más estrecho | 6 de 26 | |

Y en los 26 la **entrada fue el cierre exacto de la envolvente** y la
**dirección coincidió con la mecánica**. Ni una desviación. Así que toda su
discreción está en dos sitios y sólo dos: **cuáles elige** y **dónde pone stop
y objetivo**.

## 2 · Sus 26 entradas

| | n | riesgo | R:R | %TP | geometría | bruta | neta | z |
|---|---|---|---|---|---|---|---|---|
| sus entradas | 26 | 9,2 p | 2,25 | 15,4 % | 30,8 % | −0,115 | −0,282 | −1,09 |
| la regla, esos mismos 26 | 26 | 7,9 p | 2,00 | 26,9 % | 33,3 % | +0,083 | −0,125 | −0,39 |
| la regla, los 34 pasados | 34 | 5,3 p | 2,00 | 32,4 % | 33,3 % | +0,218 | −0,060 | −0,21 |

Acierto 4 de 26. Intervalo de Wilson **[6,1 %, 33,5 %]**: por debajo de la
geometría, pero el intervalo la roza. Con 26 operaciones no da para más.

**Colocación** (comparación emparejada, los mismos 26 cortes): −0,199 R,
IC95 [−0,530, +0,133], z −1,17. Y el conteo de signos, quitando los 15 empates
en que ambos van al stop: **5 mejores contra 6 peores.** O sea, cara o cruz. La
media negativa la mueven cuatro casos en que su objetivo más lejano no llegó.

**Selección**: los que eligió rinden −0,135 R *menos* que los que pasó,
IC95 [−0,970, +0,701], z −0,32. Nada, con un intervalo enorme.

Los tres resultados son compatibles con cero. Estaba escrito antes: con n=26 el
error típico es ±0,25 R y sólo se ven efectos muy grandes.

## 3 · Lo que sí apareció: elige sin saber que elige

Comparando los 26 operados con los 34 pasados salen tres rasgos, y los tres
dicen lo mismo:

| rasgo | operados | pasados | z |
|---|---|---|---|
| el barrido cierra pasado el nivel | 0,9 p | 2,5 p | **−3,85** |
| mecha pasada el nivel | 2,8 p | 5,5 p | **−3,16** |
| cuerpo de la envolvente | 4,8 p | 2,6 p | **+3,67** |

**Barrido corto, vuelta fuerte.** No lo dijo en ninguna descripción de la regla
—ni en la primera, ni al detallarla, ni al mandar las capturas—. Sale de las
decisiones. Es la primera vez en el proyecto que se mide algo que él hace y no
sabe que hace.

## 4 · El filtro puesto a prueba donde no había mirado

Umbrales fijados en el punto medio de las medianas, y probado en los **165
candidatos de 2020-2025 que no vio**. Umbral con Bonferroni: z ≥ 2,39.

| | n | riesgo | %TP | geometría | bruta | neta | IC95 neta | z |
|---|---|---|---|---|---|---|---|---|
| sin filtrar | 165 | 5,3 p | 34,5 % | 33,3 % | +0,252 | +0,005 | [−0,262, +0,272] | +0,03 |
| **A** barrido corto **y** vuelta fuerte | 32 | 7,8 p | 28,1 % | 33,3 % | −0,062 | −0,222 | [−0,729, +0,284] | −0,86 |
| B sólo barrido corto | 99 | 5,1 p | 40,4 % | 33,3 % | +0,416 | +0,146 | [−0,209, +0,500] | +0,80 |
| C sólo vuelta fuerte | 70 | 7,9 p | 28,6 % | 33,3 % | +0,012 | −0,142 | [−0,506, +0,223] | −0,76 |

Ninguno llega al umbral. **El filtro se archiva**, y se archiva por lo que se
dijo antes de mirar: por falta de efecto *grande*, no porque esté probado que no
haya nada. Con n=32 el filtro estricto sólo veía efectos de +0,55 R para arriba.

B queda con el mejor punto (+0,146) y un acierto de 40,4 % contra 33,3 % de
geometría. No es prueba de nada con z +0,80, pero es lo único de esta familia
que apunta hacia arriba, y es la mitad del hallazgo del usuario: **el barrido
corto, sin exigir además que la envolvente sea grande.**

## 5 · Una corrección que le debo

La baraja se construyó con la lectura **estricta** de su regla, la que coincide
con sus palabras: *sólo el primer barrido del día*, y si la envolvente no
aparece en una o dos velas, ese día no hay operación. La prueba de agosto usaba
la lectura **laxa**: seguía buscando barridos más tarde el mismo día.

No dan lo mismo, y la diferencia no es pequeña:

| lectura | n (6 años) | al año | %TP | geometría | bruta | neta | z |
|---|---|---|---|---|---|---|---|
| **estricta** (sus palabras) | 225 | 38 | 33,3 % | 33,3 % | +0,227 | **−0,020** | −0,18 |
| laxa (la prueba anterior) | 1.311 | 218 | 21,9 % | 33,3 % | −0,007 | **−0,252** | −5,41 |

Lo que le dije —que la estrategia pierde 0,25 R por operación y que ningún stop
la salva— **medía 218 operaciones al año, no las 38 que él tomaría.** Bajo su
propia regla el resultado no es perder: es **empatar**, neta −0,020 con el
intervalo cruzando cero de lado a lado.

Empatar no es tener ventaja. El acierto cae en 33,3 %, que es *exactamente*
`1/(1+2)`, la geometría pura: la señal no aporta información sobre a qué lado
va el precio. El bruto positivo (+0,227, z +1,98) sale de que las ganadoras
valen 2,38 R de media y no 2,00, porque en la rama de compra el objetivo —el
alto de Asia— a veces está más lejos de 2 R.

Y hay dos motivos para no entusiasmarse:

- La lectura estricta se eligió **después** de que la laxa saliera mal. Coincide
  con sus palabras, sí, pero es una segunda especificación probada sobre los
  mismos datos. Un z de 1,98 así no es un z de 1,98 limpio.
- El único periodo que nunca se ha tocado —2026 enero a julio, 22
  operaciones— da bruta **−0,257**. Son 22 operaciones y no prueban nada, pero
  no acompañan.

Por ramas, en 2020-2025: **venta** (barre el alto, objetivo 1:2) acierta 42,7 %
contra 33,3 % de geometría, bruta +0,304, z +2,14. **Compra** (barre el mínimo,
objetivo el alto de Asia) acierta 24,3 % contra 22,1 %, bruta +0,154, z +0,86.
Si algo hay, está en la rama de venta.

## 6 · Dónde queda

- El filtro deducido de sus decisiones: **archivado** según lo pre-registrado.
- Su criterio de selección y su colocación de stop y objetivo: **sin efecto
  medible** en 26 operaciones, ni a favor ni en contra.
- La regla en su lectura estricta: **empate**, no pérdida. Corrige lo dicho el
  27 de agosto.
- Lo único vivo: la rama de **venta** con barrido corto. No está probado, y
  probarlo requiere datos que no se hayan usado — el oro y el DAX de 2026 que
  siguen sin abrir en `reservado/`.

## Ficheros

```
bt/etiquetado_asia.py            construye la baraja
bt/resuelve_etiquetado.py        resuelve las respuestas
bt/asia_filtro.py                filtro deducido, candidatos y resolución
data/respuestas_asia.txt         sus 60 respuestas, tal cual las mandó
data/etiquetado_asia_rasgos.csv  los 60 con rasgos y su decisión
data/asia_filtro.csv             247 candidatos resueltos, 2020-2026
```
