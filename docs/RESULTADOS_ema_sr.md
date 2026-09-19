# Resultados · S/R en H1 + EMA 50 en M5 y M1

Pre-registro: `docs/PREREGISTRO_ema_sr.md` (subido antes de medir).
Código: `bt/ema_sr.py`. EURUSD 2021-2026, resolución en M1.

29 840 rupturas de la EMA 50 en M5 en el histórico.

## Veredicto

**No cumple ninguno de los tres criterios.** Y es el peor resultado neto de
todo el proyecto.

| celda | n | acierto | azar | exceso | R:R | riesgo | BRUTA | **NETA** |
|---|---|---|---|---|---|---|---|---|
| nivel H1 · N=10 · M1 | 9 506 | 75,0 % | 76,5 % | **−1,6** | 0,25 | 7,0 p | −0,020 | **−0,273** |
| nivel H1 · N=10 · sin M1 | 11 560 | 67,7 % | 69,0 % | −1,3 | 0,37 | 6,2 p | −0,015 | −0,327 |
| nivel H1 · N=20 · M1 | 9 809 | 68,2 % | 69,8 % | −1,6 | 0,41 | 8,4 p | −0,023 | −0,231 |
| nivel H1 · N=20 · sin M1 | 11 863 | 62,7 % | 64,0 % | −1,3 | 0,54 | 7,6 p | −0,017 | −0,265 |
| sin nivel · N=10 · M1 | 23 476 | 74,7 % | 76,2 % | −1,5 | 0,25 | 6,8 p | −0,021 | −0,283 |
| sin nivel · N=10 · sin M1 | 28 405 | 67,7 % | 69,0 % | −1,3 | 0,37 | 6,0 p | −0,017 | −0,336 |
| sin nivel · N=20 · M1 | 24 261 | 68,3 % | 69,6 % | −1,3 | 0,42 | 8,1 p | −0,018 | −0,233 |
| sin nivel · N=20 · sin M1 | 29 190 | 62,9 % | 64,0 % | −1,0 | 0,54 | 7,3 p | −0,013 | −0,266 |

Las ocho negativas en exceso, las ocho negativas en neta. Por años: −2,0 · −2,7
· −2,3 · +0,3 · −0,7.

Nulos limpios: lados barajados da −0,1 de exceso. La señal al revés da +1,4,
el espejo.

## De qué se muere

No del acierto. **Del coste.**

Acierta el 75 %, que suena muy bien. Pero su precio justo es el 76,5 %, así que
el acierto no es mérito: es geometría. Y el riesgo mediano son **7 pips**, o
sea que 1,43 pips de coste se llevan el **20 % del riesgo en cada operación**.

Comparación directa con la otra regla del proyecto:

| | riesgo | coste sobre el riesgo | neta |
|---|---|---|---|
| AMD + FVG | 19,9 p | 7,2 % | −0,057 |
| **ésta** | **7,0 p** | **20,4 %** | **−0,273** |

Misma bruta (las dos en cero), cinco veces peor la neta. **La diferencia entera
es dónde pones el stop.** Poner el stop en el máximo reciente de M5 lo deja a 7
pips, y a 7 pips el coste ya no es un detalle, es el resultado.

## La predicción del pre-registro

Se escribió antes. Las cuatro se cumplieron:

- «exceso entre −2 y +2» → −1,0 a −1,6 ✓
- «R:R mediano por debajo de 1» → 0,25 a 0,54 ✓
- «acierto por encima del 50 %» → 62,7 % a 75,0 % ✓
- «neta negativa en todas» → ✓

## Una cosa que aparece y hay que mirar aparte

El exceso no sale en cero: sale **por debajo del cero** en las ocho celdas y en
4 de los 5 años. La regla es un poco *peor* que el azar, de forma consistente.

La explicación que encaja: el stop está puesto en el **máximo o mínimo reciente**,
que es un nivel que el precio acaba de visitar. Una barrera ahí se toca más de
lo que dice su distancia. Ya apareció antes: en `docs/RESULTADOS_amd_fvg.md`,
las entradas con el stop pegado al extremo de la finta daban −11,6 de exceso.

Es decir: **poner el stop en el alto obvio hace que te lo toquen más de lo que
te tocaría por distancia.** Lo contrario de lo que se enseña.

Pero ojo: las operaciones se solapan (29 840 rupturas con ventanas de 20 horas),
así que los intervalos de arriba son **más estrechos de lo que deberían** y la
significación está inflada. El punto central se sostiene; la significación
necesita su propia prueba con bloques. Queda pendiente.
