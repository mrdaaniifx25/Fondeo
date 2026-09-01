# Bloque 3 · el dato no se puede usar

**33 operaciones, 81,2 % de acierto, z +5,75, p = 4,5 × 10⁻⁹.** Y no sirve.

## Primero: la página está bien

Antes de mirar nada, resolví sus 33 operaciones yo mismo contra los datos de un
minuto, sin usar la página.

```
entradas que no coinciden con el cierre real de ese minuto:  0 de 33
desenlaces que no coinciden con mi resolución independiente: 0 de 33
```

Las 33 entradas coinciden **al quinto decimal**. Los 33 desenlaces coinciden.
Una sola salida difiere en un minuto (S05, redondeo del cierre). **No hay ningún
fallo en el simulador**, y el resultado no viene de un error mío.

## Los números

| | operaciones | acierto | R neta / op | z | duración | tandas |
|---|---|---|---|---|---|---|
| bloque 1 | 23 | 59,1 % | +0,490 | +1,60 | — | — |
| bloque 2 | 30 | 51,9 % | +0,377 | +1,44 | — | — |
| **bloque 3** | 33 | **81,2 %** | **+1,160** | **+5,62** | **21 min** | **1** |

## Por qué no se puede usar

El registro de horas, que se añadió justo para esto, dice:

```
minutos entre la primera y la última decisión:  21
tandas detectadas:                               1   (el diseño pedía 3)
sesiones completadas:                           24   ->  69 segundos por sesión
```

**Sesenta y nueve segundos por sesión.** Cada sesión son 210 minutos de precio
sobre cuatro gráficos; recorrerla entera exige catorce pulsaciones del botón de
quince minutos, más abrir el formulario, arrastrar el stop y confirmar. En 69
segundos eso es mecánicamente posible y **no deja tiempo para mirar nada**.

Sea lo que sea lo que produjo el 81,2 %, **no fue el mismo proceso que produjo el
59,1 % y el 51,9 %**, que llevaron mucho más tiempo. No son comparables, y
juntarlos con los otros dos bloques contaminaría los 53 datos buenos que hay.

## Y el contraste principal no se ha ejecutado

El bloque 3 existía para contestar una sola pregunta: **¿desaparece la caída de
rendimiento si descansa?** Con una sola tanda de 21 minutos, el cansancio no
tiene ni tiempo ni ocasión de aparecer. La pregunta sigue **sin contestar**.

## Estado

- Los bloques 1 y 2 siguen en pie: 53 operaciones, 40 sesiones, dos
  pre-registros cumplidos como se escribieron.
- El bloque 3 queda **anulado como medición**, con sus datos guardados en
  `data/examen_respuestas_3.txt` para que conste.
- Los 24 días del bloque 3 quedan **quemados**: él ya los ha visto, así que un
  bloque nuevo tiene que usar días distintos.

## Reproducir la comprobación

Los datos y la verificación están en `data/examen_respuestas_3.txt` y
`data/examen_dias3.json`.
