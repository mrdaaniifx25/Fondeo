# Pre-registro · la estrategia ensamblada

Firmado **antes** de correr `bt/estrategia_final.py`. Un solo pase.

El usuario pide: *«hazme una estrategia con algo de todo esto y dime
resultados»*. Esto es el ensamblaje de lo único que ha medido positivo en tres
meses, con una regla que me prohíbe elegir.

## La regla de construcción: pesos iguales, nada elegido

Tres bloques de señal, **a peso igual**, sin ponderar por lo bien que salió
ninguno y sin buscar parámetros:

| bloque | señal | de dónde sale |
|---|---|---|
| **A · momento** | media de los signos de ROC a 21, 63, 126 y 252 días | `RESULTADOS_momento_largo.md` (t +5,04) |
| **B · tendencia** | media de los signos de MM 20/100, Donchian 55 y canal ATR 20/2 | `RESULTADOS_indicadores.md` (t +6,9 / +6,9 / +8,1) |
| **C · carry** | diferencial de inflación frente a EE.UU., tercios: largo el tercio alto, corto el bajo. Sólo divisas | `RESULTADOS_carry.md` (t +3,21) |

Posición del instrumento = media de los bloques disponibles, en [−1, +1].
Cartera = media entre instrumentos vivos, con rendimientos normalizados por
volatilidad ex-ante de 36 días (sólo pasado).

**Reequilibrio mensual**: la posición se fija el primer día hábil del mes y no
se toca. Es lo que él puede sostener, y hace el coste realista.

Coste: 0,02 unidades de ruido diario por cambio, el muro diario de EUR/USD.

## Los dos universos, los dos declarados de antemano

- **Completo** (25 series): lo que dice la investigación.
- **OPERABLE** (14 series): G10 + WTI + Brent + gas + S&P 500. Sin divisas
  ancladas ni exóticas. **Éste es el titular**, porque es el único que él puede
  ejecutar en una cuenta de fondeo.

## Contraste PRINCIPAL, declarado antes de mirar

**Efecto mensual neto y Sharpe del sistema completo en el universo OPERABLE,
tramo 2013-2026.** Ése es el número que decide, no el de 55 años.

Secundarios, todos declarados: muestra completa, los tres tramos, cada bloque
por separado, correlación entre bloques, y la traducción a €/mes.

## Predicción firmada

- Muestra completa, universo operable: **Sharpe entre +0,5 y +0,8**, t > +4.
- **2013-2026, universo operable: Sharpe entre −0,1 y +0,3, t < +1,5.**
  Es decir: no significativo.
- **Carry será el único bloque que aguante** en el tramo reciente, porque es el
  único que no mide el precio. Los bloques A y B saldrán ≈ 0 en 2013-2026.
- La mezcla de tres bloques **no** dará √3 veces el Sharpe del mejor: A y B
  están correlacionados por encima de 0,7 entre sí.
- **En dinero: menos de 100 €/mes sobre 10.000 € al ritmo reciente.**

## Qué me refutaría

Sharpe > +0,5 con t > +2 en el universo operable 2013-2026. Eso sería un sistema
operable de verdad y lo diría así, con las instrucciones para ejecutarlo.

## Controles obligatorios

1. **Placebo**: signos al azar con la misma rotación.
2. **Comprar y mantener** en el mismo universo.
3. Cada bloque **por separado** y la matriz de correlación entre los tres.
4. Peor racha, mayor caída y porcentaje de meses positivos.
5. Traducción a €/mes para 10.000 €, 50.000 € y 100.000 €, con la volatilidad
   que respeta un límite de caída del 10 %.

Una sola pasada. Lo que salga se publica, incluidas las instrucciones si sale.
