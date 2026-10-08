# Resultados · segundo bloque del examen

Pre-registro: `docs/PREREGISTRO_examen2.md`, escrito antes de generar los datos.
**20 sesiones nuevas · 30 operaciones · 1 sesión sin operar.** Cero solapamiento
con el primer bloque.

## El veredicto: dos de tres. No confirmado.

El pre-registro exigía **los tres** umbrales, a una cola, en datos nuevos:

| | resultado | umbral | |
|---|---|---|---|
| 1 · acierto sobre el 33,3 % geométrico | **51,9 %** (14 de 27) · z **+2,04** | z > +1,64 | **pasa** |
| 2 · R neta por operación | +0,377 · z **+1,44** | z > +1,64 | **no pasa** |
| 3 · diferencia contra la regla | +1,487 R/sesión · z **+2,56** | z > +1,64 | **pasa** |

**No confirmado.** Lo escribí así a propósito —*«no vale que salga uno»*— y hay
que sostenerlo cuando el que falla es el que más importa. Falló por poco, pero
falló.

## Los dos bloques, lado a lado

| | bloque 1 | bloque 2 | juntos |
|---|---|---|---|
| operaciones | 23 | 30 | **53** |
| acierto | 59,1 % | 51,9 % | **55,1 %** |
| stop mediano | 5,8 p | 7,2 p | 7,0 p |
| R bruta por operación | +0,75 | +0,59 | +0,66 |
| **R neta por operación** | +0,49 | +0,38 | **+0,43** |
| z de la neta | +1,60 | +1,44 | **+2,16** |
| diferencia contra la regla | +1,92 | +1,49 | **+1,70 R/sesión** |
| z de la diferencia | | | **+3,25** sobre 40 sesiones |

La regresión a la media que predije **ocurrió**: 59,1 % → 51,9 %. Y el efecto no
desapareció al hacerlo.

**Las dos cosas son ciertas a la vez y ninguna anula a la otra:** la confirmación
declarada falló, y lo acumulado en 53 operaciones y 40 sesiones es lo más
sólido que ha producido este proyecto. El análisis conjunto **no era la regla de
decisión**, así que se reporta como lo que es, un post hoc.

## La secundaria declarada: falla

Se firmó *«volverá a desvanecer más de la mitad de las veces»*.

```
bloque 1: desvanece 13 de 23  (57 %)
bloque 2: desvanece 14 de 30  (47 %)
```

Y dentro del bloque 2, desvanecer tampoco separa: 53,8 % de acierto contra 50,0 %.
**El rasgo no es estable.** La diferencia contra la regla del primer bloque
(p = 0,0016) era en buena parte ruido, o describe cómo operó aquellos veinte días
y no cómo opera siempre.

## Lo que él vio antes que yo

Dijo, al entregar: *«las 5 últimas estaba super desconcentrado y he visto mis
propios fallos»*. Medido:

| | n | acierto | R neta media | suma |
|---|---|---|---|---|
| primeras 10 | 10 | 70,0 % | +0,835 | +8,35 |
| centrales 10 | 10 | 77,8 % | +1,176 | +11,76 |
| **últimas 10** | 10 | **0,0 %** | −0,879 | −8,79 |

Contando solo las resueltas: **14 TP y 5 SL en las primeras 19; 0 TP y 8 SL en
las últimas 8.** Fisher a dos colas **p = 0,00058**.

**No cuenta para la estimación.** Quitar las peores mejora cualquier registro, y
sin ellas la neta subiría a +0,645 con z +2,27 — que es exactamente el número que
no se puede usar. Lo señaló él antes de que yo mirara, lo cual ayuda, pero sigue
siendo post hoc.

Lo que sí es: **una hipótesis operativa con un tamaño de efecto enorme y una
consecuencia práctica inmediata.** Si el rendimiento se derrumba después de unas
veinte decisiones seguidas, la respuesta es hacer menos sesiones de una sentada.
Se pone a prueba en el tercer bloque, declarándolo antes.

## La predicción firmada: 3 de 6

| | | |
|---|---|---|
| 1 · entre 18 y 30 operaciones | 30 | acierto |
| 2 · acierto entre 40 y 55 % | 51,9 % | acierto |
| 3 · neta entre +0,10 y +0,35 | +0,377 | fallo, por poco |
| 4 · bate a la regla con z entre +1,0 y +2,0 | z +2,56 | fallo, por arriba |
| 5 · desvanece más de la mitad | 47 % | fallo |
| 6 · stop mediano 6-8 pips | 7,15 p | acierto |

Mejor que el 1 de 5 del primer bloque. Los dos fallos «por arriba» van en la
misma dirección: **subestimé el efecto las dos veces.**

## Lo que sigue sin estar resuelto

- **Sigue siendo un simulador.** Sin deslizamiento, sin requotes, sin la presión
  de que sea dinero.
- **Sabía lo que salió en el primer bloque.** Réplica informada, no ciega.
- **Ninguna variable medida separa sus ganadoras de sus perdedoras**, ni en el
  primer bloque ni en éste. Sigue sin saberse *qué* hace bien.
- **53 operaciones.** Es poco para una decisión que costaría dinero real.

## Reproducir

```
python3 bt/examen_regla.py 2      la regla en esos mismos 20 días
data/examen_respuestas_2.txt      sus 30 operaciones
```
