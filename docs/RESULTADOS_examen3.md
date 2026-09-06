# Bloque 3 · pasa los tres umbrales

**33 operaciones · 81,2 % de acierto · R neta +1,160 por operación.**

## Corrección de lo que escribí primero

Al ver que las 24 sesiones se hicieron en 21 minutos, escribí que el dato no se
podía usar. **Estaba equivocado, por dos motivos.**

**Uno.** Dije que 69 segundos por sesión no daban tiempo material. Olvidé el botón
**«Terminar sesión»**, que yo mismo puse y que salta directo a las 11:30. Su
explicación —entrar pronto, dejar que la operación se resuelva, y cerrar la
sesión— hace que 69 segundos sean perfectamente posibles.

**Dos.** Di por hecho que un proceso más rápido era un proceso distinto. Se puede
comprobar, y lo comprobé.

## Las tres comprobaciones

**1 · La página está bien.** Resolví sus 33 operaciones contra los datos de un
minuto sin usar el simulador: **0 de 33 entradas** difieren del cierre real de su
minuto, **0 de 33 desenlaces** difieren de mi resolución.

**2 · Los días no eran más fáciles.** La regla mecánica en cada bloque:

| | disparos | acierto de la regla | neta de la regla |
|---|---|---|---|
| bloque 1 | 33 | 26,9 % | −0,823 |
| bloque 2 | 28 | 13,6 % | −0,658 |
| **bloque 3** | 30 | **20,8 %** | **−0,620** |

Si los días del bloque 3 fuesen regalados, la regla lo habría notado. Salen en
medio de los otros dos.

**3 · Su forma de entrar no cambió.**

| | hora mediana de entrada | antes de las 09:30 |
|---|---|---|
| bloques 1 y 2 | 08:40 | 79 % |
| bloque 3 | 08:46 | 85 % |

Entró pronto en los tres bloques. Lo que cambió no fue *cuándo* decide, sino la
velocidad a la que pasó el gráfico **después** de decidir. Que es exactamente lo
que él describió.

## Los tres umbrales firmados

| | | umbral | |
|---|---|---|---|
| acierto sobre el 33,3 % | 81,2 % · z **+5,75** | z > +1,64 | **pasa** |
| R neta por operación | +1,160 · z **+5,62** | z > +1,64 | **pasa** |
| diferencia contra la regla | +2,370 R/sesión · z **+5,75** | z > +1,64 | **pasa** |

**Los tres.** El bloque 2 se quedó en dos de tres; éste pasa los tres.

## Los tres bloques

| | ops | acierto | R neta / op | z | contra la regla |
|---|---|---|---|---|---|
| bloque 1 | 23 | 59,1 % | +0,490 | +1,60 | +1,921 |
| bloque 2 | 30 | 51,9 % | +0,377 | +1,44 | +1,487 |
| bloque 3 | 33 | 81,2 % | +1,160 | +5,62 | +2,370 |
| **los tres** | **86** | **65,4 %** | **+0,708** | **+4,73** | **+1,954** |

**86 operaciones, 64 sesiones, tres pre-registros.** La diferencia contra la
regla mecánica en el conjunto: **z +5,39**.

## Y el 81 % encaja con la hipótesis del cansancio

```
bloque 1, primera mitad (fresco) ......  72,7 %
bloque 2, primera mitad (fresco) ......  73,3 %
bloque 3, entero, 21 min sin cansarse .  81,2 %
bloque 1, segunda mitad ...............  45,5 %
bloque 2, segunda mitad ...............  25,0 %
```

El bloque 3 no refuta el cansancio: **es la versión más extrema de «fresco»**.
Veintiún minutos no dan tiempo a cansarse.

## Lo que sigue sin estar hecho

- **El contraste que el bloque 3 iba a ejecutar no se ejecutó.** Con una sola
  tanda, no se puede saber si *descansar* arregla la caída. Solo sabemos que sin
  cansancio el número es alto.
- **Sigue siendo un simulador**, sin deslizamiento, sin dinero y sin la presión
  de que lo haya.
- **Batir a la regla no es lo mismo que ganar dinero**: la regla pierde. El número
  que importa es la neta absoluta, +0,708 con z +4,73.
- Él conocía los resultados de los bloques anteriores.

## Reproducir

```
python3 bt/examen_regla.py 3     la regla en esos mismos 24 días
data/examen_respuestas_3.txt     sus 33 operaciones
```
