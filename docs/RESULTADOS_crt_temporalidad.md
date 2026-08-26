# El CRT desnudo por temporalidad · el mejor resultado de toda la investigación

## La pregunta

El CRT en su forma más simple tiene ventaja bruta medida —+0,085 R en H4— pero
el coste se lleva el 7 % del riesgo y la deja en negativo. **El coste en R es
exactamente `coste_fijo / riesgo`.** Así que si el mismo patrón aguanta en
temporalidades mayores, donde el stop es más ancho, la misma ventaja bruta
tendría menos coste enfrente.

Nunca lo había comprobado. Es una división, y no la había hecho.

## El resultado

Cinco instrumentos, 2020-2026, liquidez simple, objetivo en el extremo opuesto.

| TF | n | al año | acierto | riesgo mediano | **coste %R** | **R bruta** | IC 95 % | R neta |
|---|---|---|---|---|---|---|---|---|
| H1 | 47.408 | 7.183 | 49,4 % | 8,1 | 14,3 % | +0,087 | [+0,073, +0,100] | −0,141 |
| H2 | 23.180 | 3.512 | 48,5 % | 11,7 | 9,9 % | +0,132 | [+0,057, +0,208] | −0,024 |
| H4 | 11.392 | 1.726 | 47,7 % | 17,2 | 6,7 % | +0,075 | [+0,046, +0,103] | −0,030 |
| H6 | 6.973 | 1.057 | 47,5 % | 21,1 | 5,4 % | +0,065 | [+0,030, +0,100] | −0,017 |
| H8 | 4.930 | 747 | 46,6 % | 25,3 | 4,6 % | +0,064 | [+0,022, +0,106] | −0,006 |
| **H12** | 3.108 | 471 | 46,1 % | 32,5 | **3,4 %** | **+0,125** | [+0,064, +0,185] | **+0,072** |
| **D1** | 1.952 | 296 | 47,2 % | 47,7 | **2,3 %** | +0,042 | [−0,017, +0,101] | **+0,009** |

## Las dos cosas que dicen estos números

**1 · La ventaja bruta no depende de la temporalidad.**

Prueba de heterogeneidad: **Q = 7,75 con 6 grados de libertad**, cuando bajo
homogeneidad se espera ≈ 6. No hay señal de que la bruta cambie con el marco.
Los dos picos —H2 +0,132 y H12 +0,125— están rodeados de vecinos más bajos, que
es exactamente lo que produce una serie plana con ruido.

Media ponderada: **+0,082 R**, prácticamente igual en las siete.

Esto respalda su afirmación más de fondo: **el patrón es el mismo en todas las
temporalidades.** Con seis años y medio de datos, esa parte se sostiene.

**2 · El coste sí depende de la temporalidad, y de forma perfecta.**

```
H1 14,3 %   H2 9,9 %   H4 6,7 %   H6 5,4 %   H8 4,6 %   H12 3,4 %   D1 2,3 %
```

Monótona en las siete, con correlación **−1,000** contra el logaritmo del riesgo.
No es un hallazgo: es la división `coste / riesgo` dibujada.

## La consecuencia

Ventaja constante, coste decreciente → **la neta mejora al subir de marco, y
cruza el cero entre H8 y H12**:

```
neta implícita con bruta +0,082

H1  -0,061    H4  +0,015    H8   +0,036    D1  +0,059
H2  -0,017    H6  +0,028    H12  +0,048
```

**Toda la semana he estado midiendo este patrón donde peor funciona.** El CRT en
M15, M5, H1 — donde el coste se lleva del 7 al 15 % del riesgo. En D1 se lleva el
2,3 %.

## Lo que impide cantar victoria

**a · El intervalo agregado no vale.** Agrupar las siete temporalidades da
+0,082 con IC [+0,072, +0,093], pero **no son independientes**: un rango de H12
contiene rangos de H4, y los siete salen de los mismos precios. Ese intervalo
está artificialmente estrecho. Es el mismo error que ya cometí dos veces esta
semana y no lo voy a cometer una tercera.

Los intervalos **por temporalidad** sí valen, y ahí: H4 y H12 excluyen el cero,
D1 no.

**b · Ninguna neta supera el umbral corregido.** Se han probado siete
temporalidades. H12 da neta +0,072 con error típico ≈ 0,031, o sea **z ≈ 2,35**,
y con siete contrastes hace falta |z| > 2,69. **No llega.**

**c · Es un barrido, no una hipótesis previa.** He mirado siete marcos y he
señalado el mejor. El mecanismo —bruta plana, coste decreciente— es previo y
sólido, pero el número concreto de H12 no lo predije.

## Veredicto

**No confirmado, pero es lo único de toda la investigación que apunta hacia
arriba por un mecanismo que se entiende.**

La diferencia con todo lo anterior es que aquí no hay que creerse ninguna teoría
sobre liquidez ni manipulación: solo dos hechos medidos —la ventaja bruta es
plana, el coste cae con el riesgo— y una división.

## Lo que lo confirmaría o lo tumbaría

Datos **nunca vistos**. De HistData se bajan gratis y no los tenemos:

```
AUDUSD   USDCAD   USDCHF   EURGBP   NZDUSD   XAUUSD   US30
```

La predicción está escrita antes de mirarlos: **en H12 y D1, ventaja neta
positiva; en H1, negativa.** Con tres instrumentos nuevos hay muestra para
decidirlo.

## Reproducir

`bt/crt_por_temporalidad.py`
