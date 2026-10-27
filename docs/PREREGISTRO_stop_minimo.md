# Pre-registro · filtrar por stop mínimo

Escrito y subido ANTES de medir. 21/09/2026.

## De dónde sale

`docs/RESULTADOS_barrido_rr.md`: el CRT en H4 con R:R 2,0 da exceso **+3,5**
[+2,0, +4,9] sobre 4.280 operaciones y neta **−0,0103**. El desglose:

```
ventaja bruta   +0,105 R
coste MEDIO     −0,115 R
                ─────────
neta            −0,010 R
```

Y el dato que abre esta prueba: el coste **mediano** es 7,4 % del riesgo pero
el **medio** es 11,5 %. La diferencia son las operaciones con el stop diminuto,
cuyo `1/riesgo` arrastra la media.

**La hipótesis**: quitar esas operaciones baja el término que resta sin tocar la
señal. Si el exceso vive por igual en todos los tamaños de stop, la neta cruza.

**La hipótesis contraria, que es la que hay que poder descartar**: el exceso
vive precisamente en las operaciones de stop pequeño, y filtrarlas lo mata.

## Qué se mide

Base: **CRT en H4**, EURUSD + oro + DAX, igual que `bt/barrido_rr.py`.

**El filtro**: exigir `riesgo ≥ k × ATR` de la vela de entrada. Se usa ATR y no
pips absolutos porque los tres instrumentos tienen escalas distintas.

| eje | valores |
|---|---|
| **k** (stop mínimo en ATR) | **0** · **0,25** · **0,5** · **0,75** · **1,0** |
| R:R | **1,5** · **2,0** · **3,0** |

R:R 2,0 fue el pico del barrido, así que elegirlo solo sería seleccionar. Se
publican **los tres vecinos** y **las 15 celdas**.

Además, y declarado ahora, se publica el **exceso por tramo de tamaño de stop**
sin filtrar. Es el diagnóstico que decide entre las dos hipótesis de arriba, y
se mira aunque el resultado principal salga mal.

## El sesgo de selección, calculado antes

Con 15 celdas y bajo la hipótesis de que todas miden lo mismo, **el mejor de las
15 sale 1,74 errores estándar por encima de la verdad** sólo por azar
(percentil 95: 2,37). Con el error estándar de la neta en H4 (~0,022 con
n=4.280), eso son **+0,038** de regalo, y **+0,052** una de cada veinte veces.

**Cualquier "mejor celda" por debajo de +0,038 de neta no es un hallazgo, es el
procedimiento.**

## Criterio

1. neta > 0 con el IC95 sin tocar el cero, **y**
2. esa neta por encima de **+0,038** (el sesgo de selección de arriba), **y**
3. **el exceso no sube al filtrar.** Si el filtro mejora la neta *y* dispara el
   exceso, no está cortando coste: está eligiendo ganadoras, y eso es lo que
   hace el sobreajuste. El exceso debe quedarse donde estaba (+3,5 ± su
   intervalo) mientras baja el coste.
4. Y el resultado tiene que aguantar **partido en dos mitades** por fecha.

## Predicción

- El coste medio bajará mucho con k: de 11,5 % a un 5-7 % con k = 0,5.
- **El exceso se mantendrá** en torno a +3,0 a +3,5. Espero que la señal no
  dependa del tamaño del stop.
- **La neta cruzará el cero** en k = 0,5 o 0,75, quedando entre **+0,01 y
  +0,04**.
- Y por tanto **no superará el umbral de selección de +0,038**, así que el
  criterio completo **no se cumplirá** — quedará «positivo pero indistinguible
  del procedimiento», que exige entonces datos nuevos.
- Partido en dos mitades: **positivo en las dos**, pero con el cero dentro en
  cada una.

Van ocho predicciones con errores. Ésta también puede fallar.
