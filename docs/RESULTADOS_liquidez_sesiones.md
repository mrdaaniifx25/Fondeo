# Resultados · Liquidez de sesiones

Teoría del usuario, formulada a partir de su observación en el gráfico:

> *«Cuando se liquida un high o low de una sesión anterior, se va a la parte
> opuesta, o a las zonas de sesiones anteriores que han dejado liquidez
> pendiente.»*

Era una de las dos piezas de su lectura que nunca se habían medido.

**Resultado: la reversión tras el barrido de un nivel de sesión es exactamente
una moneda al aire. 49,7 % frente a 50,3 %.**

---

## Los datos

Sesiones en hora de Nueva York, las que él usa: Asia 18-01, Londres 02-08,
Nueva York 08-14. Sobre EURUSD 2020-2026:

- **5.125 sesiones cerradas**, 10.250 niveles (máximo y mínimo de cada una)
- **10.138 de ellos acabaron barridos (98,9 %)**

## La prueba limpia: misma distancia a los dos lados

La comparación tiene que ser simétrica o no vale nada. Si una sesión mide D de
alto y se barre su máximo, se mide qué llega antes: bajar D (hasta el mínimo de
esa sesión, que es la reversión que predice la teoría) o subir otro D (la
extensión). Con distancias iguales, una moneda daría 50/50.

| horizonte | reversión | extensión | sin resolver | z | p |
|---|---|---|---|---|---|
| 12 h | 2.880 · **49,0 %** | 2.994 · 51,0 % | 4.264 | −1,49 | 0,137 |
| 24 h | 3.873 · **49,7 %** | 3.914 · 50,3 % | 2.351 | −0,46 | 0,642 |
| 48 h | 4.534 · **49,8 %** | 4.579 · 50,2 % | 1.025 | −0,47 | 0,637 |

Una moneda. Y si algo se inclina, se inclina hacia el lado contrario al de la
teoría, aunque tan poco que no significa nada.

### Por qué en el gráfico parece que sí

La primera medición, sin corregir por distancia, daba «alcanza el opuesto antes
de seguir 15 pips: 30,7 %; sigue: 69,3 %». Parece demoledor, pero está sesgada:
llegar al extremo opuesto es un viaje mucho más largo que seguir 15 pips. Cuando
se igualan las distancias, la ventaja desaparece.

Es el mismo mecanismo por el que el CRT parece funcionar en los ejemplos: la
memoria selecciona los casos donde la reversión llegó lejos, y no cuenta los
otros.

## Medido como operación

Entrada al cierre de la vela M15 que vuelve dentro del rango de la sesión, en
sentido contrario al barrido, stop al otro lado de la mecha:

| objetivo | n | bruto/op | p | %TP | **PF neto** |
|---|---|---|---|---|---|
| extremo opuesto de esa sesión | 4.165 | +0,0044 | 0,881 | 26,1 % | **0,846** |
| liquidez viva más cercana | 3.956 | −0,0006 | 0,984 | 20,9 % | **0,848** |
| sin esperar el cierre de vuelta | 5.304 | +0,1209 | **0,0008** | 19,8 % | **0,912** |

### La tercera fila era un espejismo

Sale significativa, pero vive de stops diminutos:

- riesgo mediano **7,0 pips**, y el 30,8 % de las operaciones tienen el stop a
  **menos de 5 pips**
- esas concretamente rinden +0,224 R, y arrastran la media
- **el coste es el 20,3 % del riesgo**

Exigiendo un stop de al menos 8 pips: n 2.229, bruto +0,0806, p 0,047, **PF
0,977**. Sigue perdiendo dinero, y con diez variantes examinadas el umbral de
Bonferroni sería 0,005.

## El control

| | n | bruto/op | z | PF neto |
|---|---|---|---|---|
| La teoría | 4.165 | +0,0044 | +0,15 | 0,846 |
| **Dirección al azar** (5 rep) | 13.578 | **+0,0443** | **+2,73** | **0,893** |

Sortear una moneda rinde diez veces más que aplicar la teoría.

## El problema estructural: el coste

Este setup tiene stops muy ajustados —10,9 pips de mediana—, que suena bien hasta
que se mira lo que eso significa: **1,2 pips de coste son el 12,7 % del riesgo**.
Casi el doble que en el CRT (6,5 %). Cuanto más apretado el stop, más pesa el
coste.

## Conclusión

La observación es real: **el precio sí revierte tras barrer un nivel de sesión.**
Lo que no es cierto es que lo haga más veces de las que sigue. Lo hace el 49,7 %
de las veces, y el otro 50,3 % continúa.

Con las tres sesiones por separado el resultado no cambia: Asia −0,0354, Londres
+0,0208, Nueva York +0,0235, ninguna significativa.

Queda medida la primera de las dos piezas que faltaban. La otra —PDH y PDL como
objetivo del barrido, no como filtro de dirección— sigue pendiente.
