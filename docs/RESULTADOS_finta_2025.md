# Resultados · la finta a 1 hora contra EURUSD 2025

Pre-registro: `docs/PREREGISTRO_finta_2025.md`, subido en el commit `d52186e`
**antes** de ejecutar nada sobre 2025.

## El resultado

| | |
|---|---|
| sucesos en 2025 | 387 |
| media del movimiento a favor a 1 h | **−0,531 pips** [−1,702, +0,640] |
| en unidades de ruido | **−0,0452 σ** |

La tabla de lectura estaba escrita antes:

| resultado | lectura | |
|---|---|---|
| > +0,63 pips | replica por encima | |
| 0 a +0,63 | replica más flojo | |
| **−0,63 a 0** | **no replica** | ← **aquí** |
| < −0,63 | contradice | |

**No replica.**

## Lo que le hace al efecto

| año | media |
|---|---|
| 2021 | +0,705 |
| 2022 | +0,021 |
| 2023 | +1,422 |
| 2024 | +0,617 |
| **2025** | **−0,531** |
| 2026 | +0,586 |

La racha pasa de **5 de 5** a **5 de 6**. Bajo la hipótesis nula, 5 o más de 6
sale el 10,9 % de las veces. Deja de decir nada.

Y el estimador de toda la muestra:

| | antes (sin 2025) | ahora |
|---|---|---|
| n | 1 701 | 2 083 |
| media | +0,63 pips | **+0,424 pips** |
| IC95 | **[+0,17, +1,09]** | **[−0,038, +0,887]** |

**El cero entra dentro.** El único candidato que tenía el proyecto se ha caído.

## Mi predicción estaba mal

Escribí «positivo pero flojo, entre 0 y +1,0 pips». Salió −0,531. Fallé el
signo.

## Para qué sirvió el pre-registro

Para esto exactamente. Sin la tabla escrita antes, −0,531 con un intervalo que
contiene el cero se lee perfectamente como «consistente con un efecto positivo
débil, y la racha sigue en 5 de 6, que está muy bien». Las dos frases son
ciertas y las dos son una forma de no aceptar el resultado.

La tabla no deja. −0,531 cae en «no replica» y ya está.

Es la cuarta vez en el proyecto que un resultado bueno se cae al mirarlo bien.
Las tres anteriores fueron errores de medición
(`docs/CORRECCION_objetivo_rebasado.md`, `docs/CORRECCION_instante_entrada.md`,
las barreras asimétricas). **Ésta no: la medición estaba bien. El efecto no
estaba.**
