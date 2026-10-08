# Resultados · la regla de Benjamín, completa

Pre-registro `82a915b`, subido antes de medir. Código `bt/benjamin_regla.py`.
EURUSD 2021-2026, 5,7 años, resolución en M1.

## Veredicto

**No cumple ninguno de los tres criterios.** Y falla por el motivo que él
mismo elige: **dónde pone el stop.**

| celda | n | al año | acierto | azar | exceso | riesgo | coste | **umbral** | **NETA** |
|---|---|---|---|---|---|---|---|---|---|
| **M2 · H1 · sus horas** | 29 959 | 5 296 | **33,4 %** | 33,3 % | **+0,1** | **6,4 p** | **22,3 %** | **40,8 %** | **−0,312** |
| M2 · H1 · todo el día | 39 624 | 7 005 | 34,5 % | 33,3 % | +1,2 | 3,5 p | 40,9 % | 47,0 % | −0,684 |
| M2 · H4 · sus horas | 26 045 | 4 605 | 32,9 % | 33,3 % | −0,4 | 6,2 p | 23,1 % | 41,0 % | −0,342 |
| M2 · H4 · todo el día | 33 018 | 5 837 | 33,0 % | 33,3 % | −0,4 | 3,1 p | 46,1 % | 48,7 % | −0,834 |
| M5 · H1 · sus horas | 28 451 | 5 030 | 32,4 % | 33,3 % | −1,0 | 10,1 p | 14,2 % | 38,1 % | −0,242 |
| M5 · H1 · todo el día | 39 351 | 6 957 | 32,9 % | 33,3 % | −0,4 | 6,0 p | 23,8 % | 41,3 % | −0,426 |
| M5 · H4 · sus horas | 25 232 | 4 461 | 31,2 % | 33,3 % | −2,1 | 9,7 p | 14,7 % | 38,2 % | −0,285 |
| M5 · H4 · todo el día | 32 805 | 5 800 | 32,3 % | 33,3 % | −1,0 | 5,4 p | 26,5 % | 42,2 % | −0,495 |

Nulo (lados barajados) sobre la celda principal: exceso −0,4, neta −0,327.
**Indistinguible de la regla real.**

## La línea que lo explica todo

```
acierta 33,4 %    ·    necesita 40,8 % para EMPATAR
```

Su acierto es exactamente el que da la geometría de un 1:2 — **33,3 %**. Ni uno
más. La regla no predice nada.

Y el umbral de 40,8 % no sale de ninguna teoría: sale de su propio stop.
«Te cubres en los máximos» deja el stop a **6,4 pips** del precio de entrada
después de un impulso de M2. Con 1,43 pips de coste:

```
coste = 1,43 / 6,4 = 22,3 % del riesgo
umbral = (1 + 0,223) / 3 = 40,8 %
```

**Necesita 7,4 puntos de acierto por encima de lo que da el azar. Saca 0,1.**

## Su filtro horario sí hace algo, pero no lo que él cree

Comparando sus ventanas contra todo el día:

| | riesgo | coste | neta |
|---|---|---|---|
| sus horas | 6,4 p | 22,3 % | −0,312 |
| todo el día | 3,5 p | 40,9 % | −0,684 |

Sus horas salen **menos malas** — pero no porque el algoritmo interbancario
haga nada. Es que **en sus ventanas el mercado se mueve más, los impulsos son
mayores y el stop sale más ancho** (6,4 pips contra 3,5). Menos coste
proporcional. Nada más.

El mismo efecto explica que M5 salga mejor que M2 (10,1 pips contra 6,4).
**Cuanto mayor la temporalidad de entrada, mayor el stop, menor el coste.**
Siempre la misma tabla.

## Contra el umbral de su propio plan

`docs/RESULTADOS_plan_viable.md` fijó que su esquema de cuentas necesita
**+0,05 R** por operación para cruzar.

```
lo que necesita su plan:  +0,05
lo que da su estrategia:  -0,31
                          -------
                          le faltan 0,36 R por operación
```

**Su plan es correcto. Su estrategia no lo alimenta.** Y no le falta un poco:
está al otro lado por un margen de siete veces el umbral.

## Mi predicción

| predije | salió |
|---|---|
| acierto entre 30 y 40 %, cerca del 33,3 % | ✅ 33,4 % |
| riesgo mediano de 5 a 15 pips | ✅ 6,4 p |
| coste entre el 10 y el 28 % | ✅ 22,3 % |
| neta entre −0,10 y −0,30 | ✅ casi: −0,312 |
| sus horarios sin diferencia contra el control | ❌ **sí hay**, y a su favor |

Primera predicción del proyecto que acierta casi entera.

## Lo que no se le puede reprochar

La regla está **bien especificada** y es **mecanizable**. Es la única
descripción que me han dado en dos meses que traía el stop, el objetivo y el
horario. Se pudo medir sin inventar nada, y eso es más de lo que ofrece casi
nadie.
