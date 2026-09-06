# Resultados · Daily Bias y CRT Nested

Las dos confluencias que la guía señala como las que más suben el win rate.
Referencia H4, killzones en hora española, entrada por Fibonacci 70,5 % en M5 o
por CRT anidado en M15.

**Ninguna de las dos funciona. Una apenas mueve el número mientras destruye la
muestra; la otra empeora el resultado.**

---

## Aclaración previa: el Fibonacci sí está en M5

El usuario señaló que parecía calculado en H1/H4. No lo está. La función
`ejecuta_fib` recibe el marco de 5 minutos y recorre `T5/H5/L5/O5`; el nivel de
entrada se comprueba contra velas M5. **El H1/H4/D1 de las tablas anteriores es la
vela de referencia del patrón CRT** (la Vela 1 y la Vela 2), no el marco del
Fibonacci. Mis cabeceras estaban mal puestas.

El punto A del retroceso es el mínimo del barrido, que es el mismo precio se mire
en H4 o en M5, así que ahí no hay ambigüedad posible.

## Los cuatro resultados

| entrada | filtro | n | bruto/op | p | R:R | %TP | **PF neto** |
|---|---|---|---|---|---|---|---|
| fib 70,5 % en M5 | — | 3.307 | +0,0258 | 0,478 | 4,46 | 22,6 % | 0,852 |
| fib 70,5 % en M5 | **Daily Bias** | 467 | **+0,0472** | 0,609 | 4,35 | 23,8 % | 0,868 |
| CRT anidado M15 | — | 4.243 | −0,0009 | 0,978 | 4,76 | 21,0 % | 0,801 |
| CRT anidado M15 | **Daily Bias** | 578 | **−0,0440** | 0,611 | 4,63 | 20,6 % | 0,751 |

## Daily Bias: cobra caro por casi nada

Sobre la entrada por Fibonacci, el filtro mejora la ventaja bruta de +0,0258 a
+0,0472. Suena bien hasta que se mira el precio:

- **Descarta el 86 % de los setups**: de 3.307 operaciones a 467.
- La mejora no es significativa (p 0,609).
- El profit factor neto pasa de 0,852 a 0,868. **Sigue perdiendo dinero.**

Y sobre el CRT anidado hace lo contrario: de −0,0009 baja a −0,0440. Lo empeora.

Solo 543 de unos 1.700 días tienen un CRT diario activo (un 32 %), y de esos solo
la mitad coincide en dirección con el setup intradía. De ahí el 14 % que
sobrevive.

## CRT Nested: la promesa se cumple y aun así da cero

La guía lo llama la técnica de mayor probabilidad, y su mecánica es correcta: el
stop va bajo el mínimo del CRT de M15 en vez del de H4, así que es mucho más
ajustado y el R:R sube — de 4,46 a **4,76**, tal como promete.

El problema está en el otro lado de la ecuación. Desglose de las 4.243
operaciones:

| salida | n | cuota | R media |
|---|---|---|---|
| SL | 3.350 | 79,0 % | −1,000 |
| TP | 890 | **21,0 %** | **+3,750** |
| tiempo | 3 | 0,1 % | +2,964 |

`0,210 × 3,750 − 0,790 × 1,000 = −0,0025`

**Cuadra exactamente con el −0,0009 medido.**

Y fíjate en el detalle que lo explica todo: el R:R **planificado** medio es 4,76,
pero el R:R medio de **las que ganan** es 3,750. Las operaciones con el objetivo
más ambicioso son precisamente las que menos veces llegan.

Ese es el mecanismo de fondo de toda la investigación, visto en una sola tabla:
**puedes elegir el R:R que quieras, y el mercado te devuelve exactamente el
porcentaje de aciertos que lo compensa.** Apretar el stop sube el R:R y baja los
aciertos en la misma proporción. El producto se queda en cero. Es lo que ocurre
cuando no hay información direccional en la señal.

## Los controles

| | n | bruto/op | frente al azar |
|---|---|---|---|
| fib · la estrategia | 3.307 | +0,0258 | diferencia +0,0297 · z +0,72 · **p 0,469** |
| fib · dirección al azar (6 rep) | 10.174 | −0,0039 | |
| anidado · la estrategia | 4.243 | −0,0009 | diferencia +0,0306 · z +0,89 · **p 0,374** |
| anidado · dirección al azar (6 rep) | 21.636 | −0,0315 | |

Esta vez la moneda sale ligeramente **peor** que la estrategia, al contrario que
en las pruebas anteriores. Pero la diferencia no es significativa en ninguno de
los dos casos (p 0,47 y p 0,37). Sigue sin poder distinguirse de una moneda.

## Por instrumento, CRT anidado

| | sin bias | con Daily Bias |
|---|---|---|
| EURUSD | +0,1084 (n 870) | +0,1722 (n 134) |
| GBPUSD | −0,0681 (n 934) | −0,1258 (n 135) |
| USDJPY | +0,0387 (n 1.075) | −0,0183 (n 138) |
| NAS100 | −0,0200 (n 754) | −0,1231 (n 96) |
| SP500 | −0,1003 (n 610) | −0,2291 (n 75) |

EURUSD es el único consistentemente positivo en bruto, y ni con eso llega a un
profit factor de 1 (0,883 sin bias, 0,959 con bias).

## Conclusión

Se han probado ya todas las piezas que la guía propone: el patrón de tres velas,
el anclaje correcto de la rejilla, la entrada en la Vela 3, la orden stop, el
cierre estricto, las killzones en hora local, el R:R mínimo, la mitigación, la
entrada por Fibonacci en M5, el Daily Bias y el CRT anidado.

Ninguna combinación de las probadas alcanza un profit factor neto de 1. La mejor
de todo el conjunto es **0,868**.

Lo único de la guía que queda sin medir es el contexto Wyckoff discrecional
—fases, zonas de demanda, absorción por volumen—, que no es mecanizable y por
tanto no es verificable con este método. Es un hueco real y lo dejo dicho.
