# Resultados · ¿es la ventaja del CRT invariante al anclaje?

Pre-registro `a2b7b3d`. Código `bt/anclajes.py`. Se publican **todos** los
anclajes, como estaba declarado.

## Criterio A · invarianza: PASA

| | Q | grados de libertad | lectura |
|---|---|---|---|
| H12 · DAX | 13,13 | 11 | compatible con invarianza |
| H12 · EURUSD | 6,16 | 11 | muy homogéneo |
| D1 · DAX | 8,20 | 23 | muy homogéneo |
| D1 · EURUSD | 20,59 | 23 | homogéneo |
| D1 · oro | 18,72 | 23 | homogéneo |

Los cinco con Q ≤ grados de libertad. **La ventaja del CRT no depende de dónde
se ancle la rejilla.** Mi predicción decía lo contrario y falló.

Media ponderada de la bruta: H12 DAX +0,100 · H12 EURUSD +0,113 ·
D1 DAX +0,068 · D1 EURUSD +0,070 · D1 oro +0,077.

## Criterio B · utilidad: NO PASA

| | neta peor | **neta mediana** | neta mejor | el azar da |
|---|---|---|---|---|
| H12 DAX | −0,075 | **+0,035** | +0,201 | +0,137 |
| H12 EURUSD | −0,037 | **+0,043** | +0,165 | +0,137 |
| D1 DAX | −0,092 | **+0,057** | +0,148 | +0,164 |
| D1 EURUSD | −0,122 | **+0,018** | +0,219 | +0,164 |
| D1 oro | −0,070 | **+0,037** | +0,238 | +0,164 |

**Ningún «mejor anclaje» supera de forma clara el sesgo de selección** que se
calculó antes de medir. Y la cifra honesta no es la mejor: es **la mediana**,
+0,018 a +0,057, con una incertidumbre de al menos ±0,15 (los anclajes comparten
datos, así que no se pueden promediar como si fueran independientes).

## Lo práctico, que sí es nuevo

Como la ventaja es invariante, **el anclaje se puede elegir por horario sin
pagar nada por ello.** En D1 sobre DAX hay anclajes con el **100 %** de las
entradas dentro de 08-12h / 13-16h de Madrid, y dan +0,073, +0,048, +0,090 y
−0,040 — lo mismo que la mediana general.

Es decir: la restricción horaria del usuario **no cuesta rendimiento**. Eso es
un resultado útil, aunque el rendimiento en sí siga con el cero dentro.

## Lo que corrige

El +0,072 que se venía citando era la mejor celda de una tabla. La estimación
honesta entre anclajes es **+0,02 a +0,06**, la mitad.
