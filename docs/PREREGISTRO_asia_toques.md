# Preregistro · el nivel ya tocado

Escrito el 28 de agosto de 2026, **antes** de ejecutar nada.
Se ejecuta una sola vez. Nada de lo de aquí se toca después de ver el resultado.

## De dónde sale la hipótesis

El usuario clasificó 17 compras en niveles de Asia de agosto de 2026 (8 suyas,
9 disparos de la regla que se saltó) contestando cinco preguntas cerradas por
caso. Una de las cinco separó el resultado casi por completo:

| lo que él marcó | n | TP | SL | % |
|---|---|---|---|---|
| primera vez que el precio llega al nivel hoy | 9 | 2 | 7 | 22 % |
| ya lo rompió antes y ha vuelto | 2 | 2 | 0 | 100 % |
| lleva rato pegado al nivel | 4 | 3 | 1 | 75 % |
| no lo distingo | 2 | 2 | 0 | 100 % |

Agrupando: **primera vez 22 % · lo demás 88 %** (Fisher exacto p = 0,015,
descriptivo, sobre la misma muestra que generó la hipótesis).

Coincide con lo que había escrito en texto libre antes de ver las opciones:
*«una vez el precio rompe el alto pierde fuerza… espero a una reversión»* (T19),
*«lo que hice fue esperar un pequeño retroceso… y cuando **otra** vela alcista
envuelve la bajista, entonces ya tomar la entrada»* (T06), *«rechazo del mínimo
al tocarlo, **siguiente** vela alcista envuelve»* (T03).

Su única pérdida de las ocho (T04) y las dos que dijo que no tomaría (N04, N06)
encajan en el mismo sitio.

## La variable, definida sin él

`toques` = número de velas de 5 minutos, desde las 08:00 (hora de Madrid) hasta
la vela de entrada **excluida**, cuyo rango `[mínimo, máximo]` contiene el nivel
de Asia que se opera.

Ese contador reproduce su etiqueta en **15 de los 17** casos. Los dos que
fallan: N06 (él dice «pegado», mecánicamente 0 toques) y T04 (él dice «primera
vez», mecánicamente 4). Aun así el reparto agregado es idéntico al suyo:
0 toques → 2 TP / 7 SL; 1 o más → 7 TP / 1 SL.

**Aviso de colinealidad**: en esos 17, las 8 con `toques >= 1` son todas suyas y
las 9 con `toques == 0` son todas de la regla. La muestra que genera la
hipótesis no puede distinguir «los toques importan» de «lo que él hace
importa». Por eso hace falta esta prueba.

## Qué se prueba

Se parte la muestra **ya fijada** de `bt/asia_nivel.py` — mismos disparos,
misma ventana 08:00-11:30, mismo gatillo A/B, mismo stop en el extremo de la
vela anterior, mismo objetivo 2R, mismo horizonte hasta las 22:00. No se genera
ninguna operación nueva. Sólo se añade la columna `toques` y se corta por ella.

**Contraste principal, uno solo:** neta por día de `toques >= 1` menos neta por
día de `toques == 0`.

**Predicción firmada:** la diferencia será **positiva**. Es decir, los disparos
sobre un nivel ya tocado antes ese día irán mejor que los de la primera visita.

**Datos.** Principal: 2020-2025. Secundaria: enero-mayo de 2026, que él no ha
visto nunca en TradingView (su gráfico sólo llega a junio). Agosto de 2026 no
cuenta: es de donde sale la hipótesis.

**Unidad:** el día. Error estándar sobre la media diaria, como en todo el resto
del proyecto. Coste 1,2 pips de spread.

**Umbral:** el contraste es uno solo y está firmado en dirección, así que
|z| >= 1,96 con el signo predicho. Si sale al revés, la hipótesis cae, y se dice.

## Qué NO se prueba aquí

Estas quedan como exploratorias y se informan aparte, marcadas como tales:

- El reparto fino por número de toques (0 / 1-2 / 3+).
- El filtro de mecha de rechazo en la vela de ruptura (N04, N08).
- El contexto de M15 o H1 que él pide. No está implementado todavía.
