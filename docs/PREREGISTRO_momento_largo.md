# Pre-registro · momento a horizonte largo, con muestra de verdad

Escrito y subido ANTES de medir. 22/09/2026.

## Por qué esta prueba y no otra

Dos documentos del proyecto marcan dónde está el sitio:

**`RESULTADOS_muro_horizonte.md`** — el coste es fijo por operación y el ruido
crece con la raíz del tiempo, así que la ventaja mínima para empatar se derrumba
al alargar el plazo:

| horizonte | EURUSD | oro | DAX |
|---|---|---|---|
| 1 hora | 0,1076 | 0,0353 | 0,0156 |
| 1 día | 0,0226 | 0,0070 | 0,0032 |
| **1 mes** | **0,0053** | 0,0019 | **0,0007** |

Todo lo medido en dos meses es intradía, donde el muro es 0,10 y la ventaja
encontrada es 0,03-0,10. Por eso todo sale cero: **estamos jugando justo en el
sitio donde el peaje vale lo mismo que el premio.**

**`RESULTADOS_largo.md`** — a horizonte de semanas y meses las ocho mediciones
salieron **positivas** y entre **6 y 170 veces el coste**, pero las ocho con el
cero dentro. Su veredicto fue literal: *«no se puede saber con estos datos»*.
Tres instrumentos y pocos años no dan potencia.

**Esta prueba arregla justo eso: la muestra.**

## Los datos nuevos

La política de red sólo deja pasar GitHub. Ahí está la serie del Fed de tipos de
cambio diarios:

- **22 divisas contra el dólar**, diarias, **desde 1971** para diez de ellas
  (273.261 observaciones)
- más **oro** (mensual desde 1833), **WTI**, **Brent**, **gas natural** y
  **S&P 500** (mensual desde 1871)

**27 series.** Frente a las tres de todo lo anterior.

## Qué se mide

**Momento de series temporales** (Moskowitz-Ooi-Pedersen): el signo del
rendimiento de los últimos K meses predice el del mes siguiente. Es un premio
documentado durante décadas y **no es un patrón de gráfico** — es la única
familia que este proyecto no ha tocado.

- frecuencia **mensual**, último dato de cada mes
- señal: signo del rendimiento logarítmico de los últimos **K** meses
- posición: `signo / σ`, con **σ = desviación de los 36 meses anteriores**
  (sólo pasado, nunca la del propio mes)
- K ∈ **1 · 3 · 6 · 12**

**El contraste PRINCIPAL, declarado ahora para que no haya elección después:
K = 12, las 27 series, muestra completa.** Los otros tres K son secundarios.

### La corrección estadística que decide si esto vale algo

Las 22 divisas son todas contra el dólar: **están correlacionadas entre sí**. Si
se calcula el error estándar sobre las 6.600 observaciones individuales sale
falsamente pequeño, y ése es el error que convierte ruido en hallazgo.

Por eso: **cada mes se promedian las series en UN solo número de cartera, y el
estadístico se calcula sobre los meses**, no sobre las observaciones. Con ~660
meses, no 6.600 filas.

Además se publica la versión con el **factor dólar quitado** (restando cada mes
la media de las divisas), que es donde se vería si el efecto es sólo «el dólar
tendencia».

### Exclusiones, fijadas antes de mirar

- **Venezuela** fuera: hiperinflación y redenominaciones.
- Un mes de una serie se excluye si su volatilidad de 36 meses es **< 0,5 %**
  (divisa anclada: China hasta 2005, Malasia 1998-2005, Hong Kong) o si el
  rendimiento del mes supera el **50 %** en valor absoluto.

### Coste

Sólo se paga cuando el signo cambia. Se carga **0,01 en unidades de ruido
mensual por cambio de signo**, que es el doble del muro de EURUSD a un mes
(0,0053) y varias veces el del DAX. Conservador a propósito.

### Placebos

1. signos aleatorios
2. señal invertida (contraria)
3. signos barajados entre series dentro del mismo mes

Si el placebo 3 rinde como la señal, lo que se mide es el factor dólar y no el
momento.

### Partición temporal, declarada antes

**1971-1999 · 2000-2012 · 2013-2026.** Los cortes son de calendario y no se
eligen después.

## El sesgo de selección

Cuatro valores de K. El mejor de cuatro sale **1,03 errores estándar** por
encima de la verdad por azar. Por eso el principal es K = 12 y está fijado
ahora: sobre él no hay regalo.

## Criterio

1. El principal (K = 12, completa) da **t > 2** sobre los meses, **y**
2. positivo en **los tres** subperiodos, **y**
3. sobrevive al coste declarado, **y**
4. los tres placebos salen planos.

## Predicción

- **El principal saldrá positivo, con t entre 2 y 4.** Es un efecto documentado
  y 55 años de 27 series deberían verlo.
- **Habrá deterioro claro**: fuerte en 1971-1999, más flojo en 2000-2012, y
  **cerca de cero o negativo en 2013-2026**. El momento en divisas se degradó
  mucho después de 2008 y eso lo he visto documentado.
- Por tanto **el criterio 2 fallará** y quedará «existió, y hoy no se puede
  afirmar que siga».
- El coste se llevará menos del 10 % del efecto: a este plazo es irrelevante.
- Los placebos planos, salvo quizá el del factor dólar, que puede llevarse una
  parte del efecto de las divisas.
- Y en dinero, con 0,25 % de riesgo por posición, **no llegará a 750 € al mes
  sobre una cuenta de 50.000**. Lo escribo antes: si el efecto es real pero da
  150 €, eso es el resultado y no lo voy a maquillar.

Van diez predicciones con errores. Ésta también puede fallar.
