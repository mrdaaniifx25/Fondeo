# Resultados · los 16 patrones de velas japonesas en sus 150 entradas

Pidió analizar en detalle sus operaciones ganadoras: el patrón de vela, el
contexto de M15 y M5, y el tipo de cierre. **Se hace con las 48 perdedoras al
lado**, porque un rasgo que aparece en las 94 ganadoras y también en las 48
perdedoras no es su sistema: es cómo se mueve el mercado.

Los 16 patrones son los del PDF de IG que él aportó, cuantificados. En forex
intradía no hay huecos, así que en los que el PDF describe con gap —penetrante,
cubierta de nube oscura, las estrellas— se usa la adaptación habitual.

```
bt/patrones_velas.py    los 16 patrones + tipo de cierre + contexto M15/M5
bt/patrones_informe.py  ganadoras contra perdedoras contra 3.400 controles
bt/cuerpo_vela.py       el hallazgo, afinado
```

## Ninguno de los 16 separa nada

| patrón | en 94 TP | en 48 SL | control | TP vs SL |
|---|---|---|---|---|
| envolvente alcista | 13 % | 15 % | 8,2 % | 0,80 |
| trompo | 12 % | 2 % | 9,6 % | 0,06 |
| envolvente bajista | 6 % | 15 % | 7,2 % | 0,13 |
| doji | 5 % | 0 % | 4,4 % | 0,17 |
| cubierta de nube oscura | 4 % | 2 % | 2,2 % | 0,66 |
| estrella fugaz | 3 % | 4 % | 2,8 % | 1,00 |
| los otros diez | ≤ 2 % | ≤ 2 % | ≤ 3,9 % | ≥ 0,34 |

Ninguno se acerca al umbral de Bonferroni (p < 0,003 con 16 contrastes). **El
61 % de sus entradas no tiene ningún patrón direccional de los 16.** Y de las que
lo tienen, el patrón va en su dirección en el 26,6 % de las ganadoras y el 29,2 %
de las perdedoras: idéntico.

## El contexto tampoco

| en el momento de entrar | ganadoras | perdedoras | p |
|---|---|---|---|
| la última M15 cerrada va con él | 45,7 % | 43,8 % | 0,86 |
| la tendencia de M15 va con él | 38,3 % | 25,0 % | 0,14 |
| la tendencia de M5 va con él | 46,8 % | 33,3 % | 0,15 |
| la vela de M5 va con él | 66,0 % | 62,5 % | 0,71 |
| está en el tercio alto de la M15 | 34,0 % | 35,4 % | 1,00 |

Cuarta medición del proyecto que dice lo mismo de las temporalidades altas.

## El hallazgo: el tamaño del cuerpo

| cuerpo / rango de la vela | n | acierto | R neta |
|---|---|---|---|
| 0-20 % | 26 | **80,8 %** | +1,133 |
| 20-40 % | 24 | 77,3 % | +1,029 |
| 40-60 % | 36 | 76,5 % | +1,045 |
| 60-80 % | 40 | 56,8 % | +0,493 |
| 80-100 % | 24 | **39,1 %** | −0,076 |

```
cuerpo lleno (>= 60 %)   64 ops   50,0 %   R neta +0,280
todo lo demás            86 ops   78,0 %   R neta +1,067
Fisher p = 0,0006   ·   Bonferroni sobre los 28 contrastes pide p < 0,0018
```

**Y se repite en los cuatro bloques**, que son cuatro muestras separadas y
preregistradas:

| | cuerpo lleno | resto |
|---|---|---|
| bloque 1 | 15 ops · 53,3 % | 8 ops · 71,4 % |
| bloque 2 | 12 ops · 44,4 % | 18 ops · 55,6 % |
| bloque 3 | 8 ops · 37,5 % | 25 ops · 95,8 % |
| bloque 4 | 29 ops · 53,6 % | 35 ops · 78,8 % |

**No es un corte a dedo.** La separación es significativa en todos los cortes
entre 0,40 y 0,80, y la más fuerte está en 0,70 (p < 0,0001).

**No es el stop.** Cuerpo lleno 6,3 p de stop mediano, resto 5,8 p, y el coste
sobre el riesgo es 25,9 % contra 25,6-27,2 %. La diferencia está entera en el
acierto.

**No es la caja de la rotura.** Son 64 operaciones contra las 10 de la rotura del
nivel de Asia.

## El matiz

El efecto está **solo** cuando entra lejos del nivel de Asia:

| | cuerpo lleno | resto | p |
|---|---|---|---|
| lejos del nivel (105 ops) | **42,5 %** | **81,7 %** | 0,00008 |
| pegado al nivel (45 ops) | 65,0 % | 68,2 % | 1,00 |

Pegado al nivel, una vela llena no le hace daño. Lejos del nivel, le cuesta
cuarenta puntos de acierto.

Y persiguiendo o comprando el retroceso da igual, las dos son malas:

```
cuerpo lleno en su direccion (persigue)        48 ops   53,3 %   +0,374
cuerpo lleno en contra (compra el retroceso)   16 ops   40,0 %   -0,004
cuerpo no lleno, en su direccion               50 ops   80,9 %   +1,130
cuerpo no lleno, en contra                     36 ops   74,3 %   +0,979
```

## La regla, y lo que de verdad hace

```
No entres si el cuerpo ocupa mas del 60 % de la vela.
```

| | ops | acierto | R neta/op | suma |
|---|---|---|---|---|
| tal cual las hizo | 150 | 66,2 % | +0,731 | +109,7 R |
| sin las de cuerpo lleno | 86 | **78,0 %** | **+1,067** | +91,8 R |
| con el matiz del nivel | 108 | 75,5 % | +0,984 | +106,3 R |

**La regla no le da más dinero.** Las 64 que descarta sumaban +17,9 R: no perdían,
casi empataban. Lo que da es el mismo resultado con 64 operaciones menos, nueve
puntos más de acierto y mucha menos varianza. En un reto con límite de pérdida
diaria, eso es exactamente lo que importa.

## Lo que esto no demuestra

Sale de las mismas 150 que lo sugirieron. Se repite en los cuatro bloques y
aguanta Bonferroni sobre los 28 contrastes del informe —es todo lo fuerte que
puede ser un hallazgo posterior— pero **no está confirmado hacia delante**. Hasta
que lo esté, es una hipótesis con muy buena pinta, no una ley.

Es, eso sí, **lo primero en 150 operaciones que separa sus ganadoras de sus
perdedoras**. Ni la hora, ni la distancia al nivel, ni el stop, ni H4, ni M15, ni
ninguno de los 16 patrones lo habían conseguido.

Página con las 94 una a una, con sus velas reales dibujadas:
`paginas/patrones.html`
