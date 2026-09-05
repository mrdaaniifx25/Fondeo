# ¿Tiene el mercado algún patrón? · lo que se puede predecir y lo que no

Sobre los 2.397.462 minutos de EURUSD del proyecto (2020-01-01 a 2026-07-31).
La pregunta que la gente hace es «¿hay patrón?». La pregunta correcta son dos,
y tienen respuestas opuestas.

## A · Cuánto se va a mover: **sí, y mucho**

Autocorrelación de |rendimiento| por minuto:

| desfase | corr |
|---|---|
| 1 min | **+0,311** |
| 5 min | +0,264 |
| 15 min | +0,236 |
| 30 min | +0,220 |
| 60 min | +0,207 |
| 1 día | +0,163 |

Un minuto movido va seguido de otro movido. Se llama *agrupamiento de
volatilidad* y es de los efectos más robustos que existen en finanzas.

## B · Hacia dónde: **no**

Autocorrelación del rendimiento con signo:

| desfase | corr |
|---|---|
| 1 min | −0,0095 |
| 5 min | −0,0048 |
| 15 min | +0,0014 |
| 30 min | +0,0001 |
| 60 min | +0,0033 |
| 1 día | +0,0013 |

Cero, en 2,4 millones de observaciones.

## La misma cosa, en R²

Bloques de 30 minutos, el pasado explicando el futuro:

```
  recorrido -> recorrido siguiente ..... R2 = 0,6174
  recorrido -> DIRECCION siguiente ..... R2 = 0,0001
  direccion -> DIRECCION siguiente ..... R2 = 0,0004
```

**El 62 % del recorrido futuro se explica. El 0,04 % de la dirección.**

## Y lo poco que hay, no llega al coste

Seguir la dirección de los 30 minutos previos:

```
  tras subida   -0,100 pips        (o sea, revierte)
  tras bajada   +0,109 pips
  ventaja direccional bruta:  0,105 pips
  coste de ida y vuelta:      1,430 pips
```

**El efecto existe, es de reversión, y es catorce veces menor que el coste.**

## Por qué esto explica todo el proyecto

Las seis familias mecánicas probadas aterrizaron todas en el 1/(1+k) geométrico.
El caso más limpio: el turtle soup del CRT en cuatro referencias, **38.811
operaciones, acierto 33,3 % con una décima de margen**. Eso no es mala suerte ni
mal diseño: es la consecuencia aritmética de que la corr direccional sea 0,000.
Cuando la dirección no se puede predecir, cualquier entrada con objetivo fijo 1:k
acierta 1/(1+k) exactamente, da igual dónde entres y con qué stop.

Y el AUC de 0,445 fuera de muestra al intentar predecir el desenlace de las 250
roturas (`RESULTADOS_por_que_no_se_mecaniza.md`) es el mismo hecho medido por
tercera vía.

## Reproducir

`python3 bt/hay_patron.py`
