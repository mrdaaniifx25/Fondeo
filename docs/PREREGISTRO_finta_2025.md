# Pre-registro · la finta a 1 hora, contra EURUSD 2025

Escrito y subido ANTES de mirar 2025. 20/09/2026.

## Por qué 2025 es especial

El efecto de `docs/RESULTADOS_deriva.md` se midió con los datos que había:
EURUSD 2021, 2022, 2023, 2024 y 2026. **2025 no estaba en el parquet.** El
usuario lo ha subido hoy.

Eso significa que 2025 es un año entero que la hipótesis **nunca ha visto**, ni
para encontrarla, ni para ajustarla, ni para elegir entre variantes. Es la
primera prueba fuera de muestra limpia del proyecto.

No la he mirado. El parquet se reconstruyó hace cinco minutos y lo único que he
ejecutado sobre él es el conteo de minutos por año.

## La hipótesis, tal cual quedó publicada

> Tras una caja apretada de 8 velas de H1 en la que una vela sale y cierra de
> vuelta dentro (la finta), el precio se mueve **en contra de la finta** una
> media de **+0,0601 σ** en la hora siguiente.

Medido sobre 1 701 sucesos: +0,63 pips [+0,17, +1,09].

## La prueba. UNA.

Se corre `bt/deriva.py` exactamente como está, sin tocar ni un parámetro, y se
mira **sólo 2025**.

Detalles fijados ahora para que no haya margen después:

- Señal `finta`, horizonte **h = 1 hora**, lado **contra la finta**.
- Se espera del orden de **300-380 sucesos** en un año (el histórico da entre
  259 y 397 por año).
- Estadístico: media del movimiento a favor, en pips y en σ de esa muestra.
- **Sin variantes, sin subgrupos, sin filtrar por horas ni por meses.** Un
  número.

## Criterio, declarado ahora

| resultado en 2025 | lectura |
|---|---|
| media **> +0,63 pips** | replica por encima de lo medido |
| media entre **0 y +0,63** | replica el signo, más flojo |
| media entre **−0,63 y 0** | **no replica** |
| media **< −0,63 pips** | contradice |

Con ~350 sucesos el intervalo será de unos ±1,0 pips, así que **ningún
resultado de un solo año va a ser concluyente por sí mismo**. Eso también va
escrito antes: lo que se puede saber de esto es si el signo aguanta, no si el
efecto existe.

Y el número que importa de verdad, con los años ya publicados:
**+0,71 · +0,02 · +1,42 · +0,62 · +0,52** eran 5 de 5 positivos. Con 2025 serán
**6 de 6** o se romperá la racha. Bajo la hipótesis nula de que no hay nada,
6 de 6 positivos tiene una probabilidad de 1 entre 64.

## Predicción

Positivo pero flojo, entre 0 y +1,0 pips, con el intervalo tocando el cero.
