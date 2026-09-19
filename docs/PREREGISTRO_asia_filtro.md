# Pre-registro · el filtro que el usuario aplica sin saber que lo aplica

**Escrito con los candidatos ya contados y ninguno resuelto.** Fecha: 2026-08-28.

## De dónde sale

De la baraja ciega. El usuario respondió los 60 cortes: operó 26 y pasó 34. Ni
las entradas ni las direcciones se apartaron de la regla escrita —entrada exacta
al cierre en los 26, dirección igual a la mecánica en los 26—, así que **toda su
discreción está en dos sitios: cuáles elige y dónde pone stop y objetivo.**

Comparando los 26 operados con los 34 pasados aparecen tres diferencias grandes,
y las tres apuntan a lo mismo:

| rasgo | operados | pasados | z |
|---|---|---|---|
| el barrido cierra pasado el nivel | 0,9 p | 2,5 p | **−3,85** |
| mecha pasada el nivel | 2,8 p | 5,5 p | **−3,16** |
| cuerpo de la envolvente | 4,8 p | 2,6 p | **+3,67** |

Traducido: **barrido corto, vuelta fuerte.** Le vale que el precio asome apenas
por encima del nivel y vuelva de golpe; descarta el barrido que se va lejos o
cuya vuelta es floja. No lo dijo en ninguna de las descripciones de la regla —
sale de las decisiones, no de las palabras.

Nada de esto es un resultado todavía: es una hipótesis sacada de 60 casos que él
ya vio, así que sobre esos 60 no significa nada. Hay que probarla en otros.

## La regla, con los umbrales fijados ahora

Umbral = punto medio entre las dos medianas. Sin ajustar, sin buscar el mejor
corte, sin mirar ningún resultado.

```
exceso  = |cierre de la vela que barre  −  nivel de Asia|
cuerpo  = |cierre de la envolvente  −  su apertura|

A  (principal)   exceso <= 1,7 p   Y   cuerpo >= 3,7 p
B  (secundaria)  exceso <= 1,7 p
C  (secundaria)  cuerpo >= 3,7 p
```

Sobre los 60 que vio, A no se equivoca en una dirección: de los 7 que acepta,
operó los 7. De los 53 que rechaza, él operó 19 — o sea, A es más estricto que él.

Todo lo demás (entrada, stop, objetivo, horario, definición de envolvente) queda
exactamente como en `docs/PREREGISTRO_asia_londres.md`. Sólo se añade el filtro.

## Dónde se prueba

Candidatos contados antes de resolver nada, con el barrido **primero del día**:

| conjunto | candidatos | pasan A | pasan B | pasan C |
|---|---|---|---|---|
| 2020-2025, los 60 que vio | 60 | 7 | 28 | 24 |
| **2020-2025, los que NO vio** | **165** | **32** | **99** | **70** |
| 2026 ene-jul, reservado | 22 | 4 | 14 | 9 |

**La prueba principal son los 165 que no vio.** Los 60 se reportan sólo como
referencia y no cuentan para nada. 2026 tiene 22 candidatos: se mira, pero con
4 operaciones en A no decide nada y así queda dicho.

## Qué se mide

R neta media por operación (coste 1,2 pips sobre el riesgo), contra cero y
contra el mismo conjunto sin filtrar. Y el %TP contra la geometría pura
`1/(1+R:R)`, que es lo que saldría si el filtro no llevara información.

Corrección de Bonferroni por tres filtros: el umbral de significación es
**z ≥ 2,39** (equivale a 5 % repartido entre A, B y C).

## Potencia — lo que esta prueba puede y no puede

Con desviación por operación de ~1,3 R:

| filtro | n | error típico | detecta a partir de |
|---|---|---|---|
| A | 32 | ±0,23 R | **+0,55 R** |
| B | 99 | ±0,13 R | **+0,31 R** |
| C | 70 | ±0,16 R | **+0,37 R** |

Son efectos enormes. Un filtro que aporte +0,10 R —que sería excelente— pasa por
aquí sin dejar rastro. Así que un resultado plano **no cierra nada**; sólo un
resultado grande abriría algo.

## Lo que espero, dicho antes

Que el bruto suba algo respecto al sin filtrar, porque barrido corto y vuelta
fuerte es una descripción razonable de una trampa de liquidez. Y que el **neto
siga sin superar cero**, porque el stop mediano de estas entradas ronda los 8
pips y 1,2 de spread son el 15 % del riesgo: haría falta un bruto por encima de
+0,15 R sólo para empatar.

Llevo la cuenta de mis predicciones en este proyecto y he fallado varias
—el filtro de H1, la potencia del ciego de H12, las cinco del barrido de Asia—.
Esto es una predicción, no un pronóstico fiable.

## Decisión, fijada ahora

- **Sigue** si A o B dan neta > 0 con z ≥ 2,39 en los 165 no vistos.
- **Se archiva la familia del barrido de Asia** si ninguno llega, y se dice que
  se archiva por falta de efecto *grande*, no por prueba de que no haya nada.
- 2026 no cambia la decisión en ningún caso: sólo acompaña.

## Ficheros

```
bt/asia_filtro.py                    construye candidatos, filtra y resuelve
data/asia_filtro_candidatos.csv      los candidatos con sus rasgos, sin resolver
data/etiquetado_asia_rasgos.csv      los 60 de la baraja con rasgos y su decisión
```
