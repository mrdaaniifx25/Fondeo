# Pre-registro · ¿es la ventaja del CRT invariante al anclaje?

Escrito y subido ANTES de medir. 21/09/2026.

## La pregunta, y la que NO es

`docs/RESULTADOS_dax_horario.md`: en H12 y D1 no cae **ninguna** operación
dentro del horario del usuario, porque la rejilla se ancla a la 01:00 de Nueva
York y eso deja los cierres a las 07:00 y 19:00 de Madrid. Se queda fuera por
una hora.

**La pregunta que NO se hace aquí**: «¿qué anclaje da mejor resultado?». Elegir
el mejor de doce es fabricar un falso positivo.

**La que sí**: ¿da lo mismo el CRT en los doce anclajes? Si el patrón existe,
sí. Si sólo aparece en uno, no existe.

## El número que me ata las manos, calculado antes

Simulado con 200.000 repeticiones, suponiendo que **los doce anclajes miden lo
mismo** (o sea, ventaja verdadera única) y con el error estándar real del DAX
en H12 (SE ≈ 0,084):

| | el mejor de los k sale, sólo por azar |
|---|---|
| **12 anclajes** (H12) | **+0,137 R** por encima de la verdad · percentil 95: **+0,221** |
| **24 anclajes** (D1) | **+0,164 R** por encima de la verdad · percentil 95: **+0,240** |

O sea: **con ventaja verdadera CERO, el mejor de doce anclajes enseñará del
orden de +0,14 R, y uno de cada veinte llegará a +0,22.** Cualquier «mejor
anclaje» por debajo de esas cifras no es un hallazgo, es el procedimiento.

Esto queda escrito para que no me lo pueda saltar dentro de una hora.

## Qué se mide

Mismo código (`velas_ref`, `secuencias`, `resuelve`), cambiando sólo
`ancla_ny`.

- **H12**: los **12** anclajes (0 a 11).
- **D1**: los **24** anclajes (0 a 23).
- Instrumentos: **DAX, EURUSD y oro** — los tres que hay, para que la
  invarianza se mida con toda la muestra disponible y no sólo con el DAX.
- Por cada anclaje: n, R bruta, IC95, R neta, y **qué porcentaje de las
  entradas cae en el horario del usuario** (08-12h y 13-16h de Madrid).
- **Se publican todos.** Los 12 y los 24, de los tres instrumentos.

## Criterio

**A · Invarianza.** Se calcula la dispersión observada entre anclajes y se
compara con la que produciría el ruido de muestreo. Los anclajes comparten
datos, así que están correlacionados y la prueba es conservadora: si aun así la
dispersión supera lo esperado, la ventaja **depende de la rejilla**.

**B · Utilidad.** Sólo si A sale invariante tiene sentido mirar si algún
anclaje cae en su horario. Y aun entonces, su neta tiene que superar el sesgo
de selección de arriba (+0,137 en H12, +0,164 en D1) para contar.

Si A sale **no invariante**, la conclusión es que el resultado de H12/D1 que
quedaba en pie **era un artefacto de la rejilla**, y se cierra.

## Predicción

- **No invariante.** Espero ver una dispersión entre anclajes mayor que el
  ruido, porque la muestra es pequeña y el CRT en H12 ya venía con el cero
  dentro del intervalo.
- El mejor anclaje de cada tabla rondará **+0,15 a +0,25 R**, que es justo lo
  que predice el sesgo de selección con ventaja cero.
- Y por tanto: **se cierra el H12/D1** como candidato.

Van cuatro predicciones mías con errores. Ésta también puede fallar.
