# Resultados · el modelo multivariante de sus entradas

Continuación de `RESULTADOS_ingenieria_inversa.md`, que se quedó corto: allí se
midió una variable cada vez y la regla se construyó solo con la más llamativa
—el rechazo del nivel— que cubre 35 de sus 150. Aquí se mira **todo**.

```
bt/taxonomia_150.py    en que se apoya cada una de las 150
bt/modelo_entradas.py  regresion logistica sobre pares (vela, direccion)
bt/regla_modelo.py     el modelo congelado, operando
```

## Primero: en qué se apoyan realmente sus 150

| en qué se apoya | n | % | acierto |
|---|---|---|---|
| **extremo de la sesión** (no de Asia) | 51 | 36,7 % | **73,5 %** |
| **rechazo del nivel de Asia** | 34 | 24,5 % | **75,0 %** |
| dentro del rango de Asia, sin nivel cerca | 32 | 23,0 % | 56,2 % |
| fuera del rango de Asia, sin nivel cerca | 12 | 8,6 % | 81,8 % |
| **rotura del nivel de Asia** | 10 | 7,2 % | **33,3 %** |

La primera fila es lo que la primera pasada se perdió: **más de un tercio de sus
entradas no están en el nivel de Asia, están pegadas al máximo o al mínimo que
lleva la propia sesión de Londres**. Y de ahí sale su mejor bloque.

Y va con el extremo, no contra él:

```
COMPRAS  89 · entra pegado al MÁXIMO de la sesión el 73 % de las veces (acierto 74,6 %)
VENTAS   50 · entra pegado al MÍNIMO de la sesión el 64 % de las veces (acierto 55,6 %)
```

La rotura del nivel de Asia es su peor categoría, 33,3 % — el azar geométrico.
Encaja con que la regla mecánica de rotura lleve todo el proyecto saliendo
negativa.

## El modelo: 147.690 pares (vela, dirección)

Cada vela de M5 entre las 08:00 y las 11:30 da dos posibilidades, comprar o
vender. Sus 150 entradas son los positivos; todo lo demás que tenía disponible y
no tomó son los negativos. Dieciséis variables, regresión logística con L2,
ajustada solo en los 114 días del examen y **validada sobre días que el modelo no
ha visto**.

| variable | peso |
|---|---|
| hora | **−1,006** |
| hacia el nivel de Asia | −0,411 |
| distancia al nivel de Asia | −0,333 |
| el cuerpo de la vela va en su dirección | +0,308 |
| rechazo del nivel | +0,221 |
| distancia al extremo de la sesión | −0,145 |
| M15 a favor | +0,091 |
| H4 a favor | +0,043 |
| rotura del nivel | −0,008 |

**AUC 0,800 sobre días no vistos.** Del 1 % de pares mejor puntuados, el 17,1 %
son suyos, contra un 2,11 % de base: ocho veces más.

**Sus entradas no son al azar. Ni de lejos.** Se pueden predecir.

Y H4 pesa 0,043 sobre 1,006 de la hora. Lo que manda es *cuándo*, no *qué dice
H4*.

## Pero predecir dónde entra no es predecir qué gana

El modelo congelado, operando con **su** stop medido (el extremo de las dos
últimas velas de M5) y 1:2:

| | operaciones | acierto | R neta | z |
|---|---|---|---|---|
| K=1 · 114 días del examen | 106 | 47,6 % | +0,072 | +0,49 |
| **K=1 · 1.032 días nuevos** | **1.449** | **37,4 %** | **−0,256** | −6,71 |
| K=2 · 1.032 días nuevos | 2.844 | 37,3 % | −0,265 | −9,75 |
| K=3 · 1.032 días nuevos | 4.219 | 36,5 % | −0,292 | −13,13 |

El acierto de 37,4 % está **por encima del 33,3 % geométrico con z = +3,26**. El
modelo encuentra algo real. Pero el equilibrio con coste está en el 41,3 %, así
que ese algo real vale unos cuatro puntos y hacen falta ocho.

Y lo más revelador: **cuanto más seguro está el modelo, peor sale.**

| umbral | n | acierto |
|---|---|---|
| p ≥ 0,05 | 14.027 | 33,2 % |
| p ≥ 0,10 | 3.857 | 32,4 % |
| p ≥ 0,20 | 767 | 32,3 % |
| p ≥ 0,30 | 137 | 27,7 % |

Las velas que **más se parecen a sus entradas** no ganan más. El modelo ha
aprendido dónde entra y no ha aprendido nada sobre qué gana, porque en las
variables no está.

## El resumen honesto

```
¿es al azar dónde entra?          NO. AUC 0,800, ocho veces la base.
¿está escrito el patrón?          SÍ, en 16 variables, y pesa la hora sobre todo.
¿ese patrón gana?                 +4 puntos sobre el azar. Hacen falta +8.
¿él gana?                         66,2 % en 142 resueltas. IC 95 % [58,4 %, 74,0 %].
¿de dónde salen los otros 29 pts? no está en nada de lo medido.
```

Su 66,2 % está a veinticinco puntos del equilibrio y el intervalo de confianza
entero está por encima. Con 150 operaciones eso ya no es suerte de racha. Quedan
dos explicaciones y solo dos:

1. **Lee algo que estas dieciséis variables no recogen.** La forma de la vela en
   M1, la velocidad, el orden en que llega el precio a un sitio. Es plausible: el
   modelo captura +4 puntos con lo grueso y él saca +33.
2. **El simulador le favorece.** Sin deslizamiento, sin requotes, sin la duda de
   apretar el botón con dinero, y con la vela formándose limpia.

**Ningún examen más distingue esas dos.** Es la misma medición repetida.

## Cuánto costaría distinguirlas en directo

Su equilibrio es el 41,3 %. Con 80 % de potencia, a una cola:

| si en directo acierta | operaciones | sesiones | mañanas |
|---|---|---|---|
| **66 %** (lo medido) | **24** | **~18** | **~1 mes** |
| 60 % | 43 | ~33 | ~1,6 meses |
| 55 % | 80 | ~62 | ~2,9 meses |
| 50 % | 200 | ~154 | ~7,3 meses |

**Si lo suyo es real, dieciocho mañanas lo demuestran.** Y si tras treinta y tres
sesiones no se separa del equilibrio, la respuesta también está: no era el 66 %.

Es el experimento más barato que queda, y el único que queda.

## Lo que ya se puede escribir de su método

De todo esto, lo mecanizable y medido:

```
ventana     08:00 a 11:30, y vive en la primera hora y media (mediana 08:40)
referencia  el extremo que lleva la propia sesion, y el alto/bajo de Asia
direccion   a favor del extremo de la sesion; contra el nivel de Asia cuando lo
            pincha y cierra dentro. NUNCA la rotura del nivel: es su peor caja, 33 %
stop        el extremo de las dos ultimas velas de M5   (error mediano 1,3 p)
objetivo    1:2 fijo
riesgo      1 % del inicial. Al 2 % revientan cuentas
parada      dos perdidas, o las 11:30
```

Lo que no se puede escribir es cuál de las velas candidatas tomar. Eso, de
momento, es suyo.
