# Pre-registro · ESTRATEGIA EUR/USD — LIQUIDEZ DE SESIONES

La especificación es **suya**, entregada el 22/09/2026 y reproducida íntegra en
`docs/SPEC_liquidez_sesiones_v2.md`. Cumple su propio §17: las reglas están
escritas antes de medir y no se tocan después.

Este documento sólo fija **las decisiones que su texto deja abiertas**, para que
no las elija yo después de ver el resultado.

## Lo que su spec no fija, y que decido ahora

| hueco | decisión | por qué |
|---|---|---|
| anclaje de las velas H4 | **00:00 hora de Madrid** (00-04-08-12-16-20) | es el que sale por defecto; `RESULTADOS_anclajes.md` ya midió que el anclaje no cambia el resultado |
| límites de sesión | Asia **00:00-08:00**, Londres **08:00-14:00** (Madrid) | son los del indicador de sus capturas |
| «muy próximo» para la confluencia (§2) | **≤ 2 pips** | |
| «margen de seguridad fijo» (§8) | parametrizado: **0 · 1 · 2 · 3 pips** | su §8 pide justo esto |
| cuántas velas esperar la envolvente M5 | parametrizado: **6 · 12** velas | su §6 no pone plazo |
| profundidad de búsqueda del sweep H4 | **las 6 últimas H4 cerradas** (24 h) | |
| «Sweep H1 dentro de la ventana» (§5) | **estricto** = la H1 cierra dentro de 09-11 o 14-16:30. Se publica también la versión laxa (cierra dentro de la sesión) | el estricto es el que dice su texto y es el PRINCIPAL |
| cierre por no-overnight (§1) | si a las **23:00 Madrid** no ha tocado SL ni TP, se cierra a mercado y se apunta el R que salga | |
| spread en el SL (§8) | **1,0 pip**, medido en su propia cuenta | |
| coste aplicado al resultado | **1,43 pips** ida y vuelta (spread 0,7-1,0 + comisión 5 €/lote) | `docs/COSTE_real.md` |

El spread aparece dos veces a propósito y no es doble contabilidad: **1,0 pip
como colchón del SL** porque lo pide su §8, y **1,43 pips como coste del
resultado** porque es lo que cobra el bróker.

## Datos

EURUSD M1, **2021-01-03 a 2026-09-01**, 2.055.684 minutos, de los ZIP que subió
él. 5,7 años.

## El umbral que hay que batir, calculado antes

Con TP fijo a 1:2 el azar puro acierta **33,3 %**. Cada operación paga 1,43 pips
de coste sobre su riesgo:

```
umbral de empate  =  (1 + 1,43/riesgo) / 3
```

Con un stop de 10 pips eso son **38,1 %**, es decir **+4,8 puntos** de ventaja
sobre el azar sólo para no perder. El umbral real se calculará con el riesgo
medido, no con este ejemplo.

## Potencia, calculada antes

La secuencia tiene cuatro filtros encadenados. Si deja menos de **200**
operaciones en 5,7 años, el intervalo de confianza del acierto será de ±6,5
puntos o peor y **no se podrá distinguir 33 % de 38 %**. En ese caso el
resultado será «no se puede saber», y se dirá así en vez de leer el signo.

## El sesgo de selección

4 márgenes × 2 esperas × 2 versiones de H1 = **16 celdas**. El mejor de 16 sale
**1,77 errores estándar** por encima de la verdad sólo por azar.

**El PRINCIPAL, declarado ahora**: margen **1 pip**, espera **12** velas, H1
**estricto**. Sobre esa celda no hay regalo. Las otras 15 se publican pero no
cuentan como hallazgo.

## Criterio

1. El principal con **acierto > umbral** y el IC95 de la neta sin tocar el cero,
   **y**
2. la neta por encima de **+0,038 R** (el sesgo de selección), **y**
3. mismo signo partido en dos mitades por fecha, **y**
4. los placebos (lados barajados, y la secuencia sin el filtro H4+H1) no rinden
   igual que la señal.

El cuarto es el que dice si los cuatro filtros encadenados aportan algo o si
estamos midiendo el barrido a secas, que ya salió plano en
`RESULTADOS_barrido_sesion_v2.md`.

## Predicción

- **Saldrán pocas operaciones**: entre 80 y 250 en 5,7 años. Los filtros H4+H1
  encadenados son muy restrictivos.
- El riesgo mediano quedará entre **8 y 14 pips**, más ancho que los 5,9 de
  Benjamin, porque el SL va al extremo del barrido más margen.
- **El acierto quedará entre 30 % y 38 %**, y el umbral entre 37 % y 39 %.
- **La neta será negativa o indistinguible de cero.** Si me equivoco aquí será
  la primera vez que un patrón de gráfico intradía cruce en este proyecto.
- El placebo sin H4+H1 rendirá **parecido** al completo, lo que indicaría que la
  cadena no aporta.
- Y la muestra será demasiado pequeña para cerrar la pregunta en un sentido u
  otro, así que lo más probable es «no se puede saber».

Van doce predicciones con errores. Ésta también puede fallar.
