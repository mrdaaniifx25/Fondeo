# Resultados · el examen de Londres

Pre-registro: `docs/PREREGISTRO_examen.md`, escrito antes de que hiciera una sola
sesión. Un solo pase. **20 sesiones · 23 operaciones · 4 sesiones sin operar.**

## El veredicto contra lo firmado

El pre-registro decía: *«R neta positiva con z > +1,96, **o** una diferencia
contra la regla mecánica con z > +1,96 a su favor. Nada más cuenta.»*

| criterio | resultado | ¿pasa? |
|---|---|---|
| R neta por operación | **+0,490** · z **+1,60** · p 0,110 | no |
| R neta por sesión | +0,563 · z +1,39 · p 0,164 | no |
| **diferencia contra la regla, emparejada por día** | **+1,921 R/sesión** · z **+2,17** · p **0,030** | **sí** |

**Uno de los dos criterios se cumple.** Es el primer resultado del proyecto que
pasa un umbral escrito de antemano.

## Los números

| | él | la regla, esos mismos 20 días |
|---|---|---|
| operaciones | 23 | 33 |
| por sesión | 1,15 | 1,65 |
| acierto | **59,1 %** (13 TP / 9 SL) | 26,9 % (7 / 19) |
| contra el 33,3 % geométrico | **z +2,56** · p 0,010 | z −0,69 |
| stop mediano | 5,8 p | 6,8 p |
| R bruta por operación | +0,754 | −0,103 |
| **R neta por operación** | **+0,490** | −0,823 |
| **suma en 20 días** | **+11,27 R** | −27,16 R |

Le gana en **14 de las 20 sesiones**.

## Tres comprobaciones que podrían haberlo tumbado

**1 · ¿Fueron 20 días malos para la regla?** No. La regla saca −0,823 R aquí
contra −0,385 en 2020-2026 — una diferencia de z −0,87 sobre 33 disparos. La
muestra no se separa de lo normal. **Su ventaja no es que la regla tuviera un mal
día.**

**2 · ¿Aguanta sin la mejor sesión?** Aquí es donde se resiente:

| | n | él | la regla | diferencia | z | p |
|---|---|---|---|---|---|---|
| las 20 | 20 | +0,563 | −1,358 | +1,921 | **+2,17** | 0,030 |
| sin S01 | 19 | +0,351 | −1,265 | +1,616 | +1,84 | 0,066 |
| sin las dos mejores | 18 | +0,161 | −1,480 | +1,641 | +1,77 | 0,077 |

**El resultado se apoya en una o dos sesiones.** Quitando S01 —tres objetivos
seguidos el mismo día— ya no pasa el umbral. Su acierto baja del 59,1 % al
52,6 % y su neta por operación de +0,490 a +0,333.

**3 · ¿Opera las señales de la regla?** **No.** Y esto es lo más importante del
examen:

```
sus entradas a menos de  5 min de un disparo de la regla:   3 de 23   (13 %)
                         15 min                          :   3 de 23   (13 %)
                         30 min                          :   6 de 23   (26 %)
mismo día y misma dirección, sin mirar la hora           :  15 de 23
```

En 20 sesiones no hubo **ni una** en la que él operase y la regla no disparara —
usa los mismos días— pero **entra en momentos distintos**. No está filtrando las
señales de la regla: está haciendo otra cosa.

## Lo que eso significa

Dos meses de backtests han estado midiendo una regla que **dispara en minutos
distintos de los suyos**. El gatillo A/B de `REGLA_asia_nivel.md`, verificado
contra sus dieciséis explicaciones de agosto, describe *cuándo se puede* entrar,
no *cuándo entra él*. Ya lo sospechábamos —«74,5 disparos por mañana contra sus
1,6»— pero ahora está medido operación a operación.

**La pregunta ya no es si su criterio filtra bien. Es qué hace en esos 23
minutos concretos**, que ahora están registrados con precisión de minuto y con
los datos delante.

## La predicción firmada: 1 de 5

| | |
|---|---|
| 1 · entre 20 y 40 operaciones | **acierto** — 23 |
| 2 · acierto entre 30 y 45 %, sin separarse del 33,3 % | **fallo** — 59,1 %, z +2,56 |
| 3 · R neta negativa, entre −0,2 y −0,5 | **fallo** — +0,490 |
| 4 · no batirá a la regla de forma significativa | **fallo** — z +2,17 |
| 5 · stops de 7 pips o más de mediana | **fallo** — 5,8 p, aunque sí los ensanchó desde los 3,8 de agosto |

Fallé las cuatro que importaban, y en la dirección que importa.

## Lo que este examen no prueba

- **23 operaciones y 20 sesiones.** Es poco, y el resultado se apoya en una o
  dos de ellas.
- **Vio el resultado de cada operación** según avanzaba. Era necesario para su
  regla de parar tras dos pérdidas, pero significa que sus decisiones dentro de
  una sesión no son independientes entre sí.
- **La página guardaba en memoria toda la sesión hasta las 11:30** desde el
  principio, aunque solo dibujara hasta el cursor. No hay motivo para dudar de
  él, pero es una propiedad del diseño y queda escrita.
- **Un examen no es dinero real.** No hay deslizamiento, ni requotes, ni la
  presión de la cuenta.

## Qué haría falta para confirmarlo

Otro bloque de 20 sesiones nuevas, con la predicción escrita antes: **acierto por
encima del 45 % y diferencia positiva contra la regla**. Si vuelve a salir con
una muestra que no ha visto, deja de ser una racha.

## Ficheros

```
data/examen_respuestas_1.txt   sus 23 operaciones
data/examen_regla.csv          los 33 disparos de la regla en esos días
bt/examen_regla.py             la regla corrida solo en esos 20 días
```
