# Lo que se aprende viéndole operar en directo (live 160)

La transcripción del directo contiene tres cosas que **no estaban** en la
especificación de siete pasos, y una corrección importante.

## La corrección: los 7 pasos se dejaron fuera el requisito clave

Sus palabras en el directo:

> *«solamente única y exclusivamente voy a buscar esos movimientos cuando el
> precio me haya roto la zona del máximo del día anterior o el mínimo del día
> anterior»*
>
> *«si el precio se queda con la mecha por debajo y el cuerpo por arriba, eso es
> la manipulación en una hora»*

Eso **no** es «cierra por encima → compra». Es un **barrido con vuelta dentro**, o
sea exactamente la configuración que pasó el preregistro en
`RESULTADOS_pase_fibo_h1.md` (+0,050 R bruta) y **no** la de
`RESULTADOS_gpso_t5p.md` (+0,011, nada).

La versión que se reconstruyó del material escrito perdía el filtro que hace todo
el trabajo.

## Filtro A · la hora a la que se formó el nivel · **FUNCIONA**

> *«si está a las 6 de la mañana, ese máximo a mí no me sirve. Si está a las 7 de
> la mañana sí me sirve»* — y por eso insiste en leer los niveles en H1 y nunca
> en diario.

Medido sobre 20.416 barridos:

| | n | acierto | R bruta | z |
|---|---|---|---|---|
| **sin filtrar** | 20.416 | 33,3 % | +0,005 | +0,56 |
| **nivel formado entre 7 y 17 h** | 6.675 | **34,5 %** | **+0,042** | **+2,40** |

Y el perfil por hora es coherente, no un pico aislado:

| hora en que se formó el nivel | n | acierto | R bruta |
|---|---|---|---|
| 00-03 | 2.155 | 33,9 % | +0,022 |
| 03-06 | 767 | 33,6 % | +0,014 |
| 06-09 | 952 | 34,5 % | +0,041 |
| 09-12 | 1.487 | 33,2 % | +0,002 |
| 12-15 | 1.659 | 34,1 % | +0,031 |
| **15-18** | 3.727 | **35,0 %** | **+0,056** |
| **18-21** | 2.616 | **31,8 %** | **−0,040** |
| **21-24** | 7.053 | **32,4 %** | **−0,020** |

**Los niveles formados de noche son basura y los de sesión valen.** Es una regla
que él dice de pasada, que nadie adivinaría, y que se sostiene en 3 de 4
instrumentos (EURUSD +0,075 · USDJPY +0,041 · NSXUSD +0,028 · GBPUSD +0,020).

## Filtro C · «que el precio se quede cercano» · **no aporta**

| | R bruta |
|---|---|
| pierna < 1,5× la vela de H1 | −0,002 |
| pierna < 2,0× | +0,011 |
| pierna < 3,0× | +0,011 |

## Filtro D · su hora de operar · **es la peor**

| ventana (hora de Madrid) | n | acierto | R bruta |
|---|---|---|---|
| **08-12** (la ventana de él, el usuario) | 5.083 | **34,0 %** | **+0,028** |
| 09-18 | 8.096 | 32,7 % | −0,007 |
| **14-17** (la de los directos de Jorge) | 2.250 | **32,0 %** | **−0,025** |
| 15-17 | 1.400 | 32,2 % | −0,018 |

La hora a la que Jorge hace sus directos es la peor de las medidas. Su racha de
19 aciertos en 26 directos no sale de la hora.

## Todo junto

```
  A (nivel 7-17 h) + C (pierna < 2×) + D (operar 8-18 h)
  n = 2.759 · acierto 34,7 % · R bruta +0,048 · z +1,77 · R NETA -0,109
```

Sigue sin llegar. Pero es la mejor R neta medida de una regla mecánica en todo el
proyecto.

## Sobre su racha declarada

19 TP, 3 SL y 3 BE en 26 directos. Con 26 operaciones y una sola por semana no se
puede distinguir una ventaja de una racha, y hay dos cosas que la inflan: solo
opera cuando ve su patrón (si no lo ve, no hay operación que contar) y la
operativa del directo de hoy fue **1:1**, no 1:2 —entrada 1,15830, stop 1,15757,
objetivo 1,15903—, con break-even a 0,7R y cierre manual. Con 1:1 el listón del
azar no es el 33 % sino el 50 %.

Nada de esto dice que mienta. Dice que 26 operaciones no son una prueba.

## Reproducir

`python3 bt/gpso_filtros.py`

---

# Ampliación · el live 159 y su regla horaria exacta

En el live 159 da la regla con números, cosa que no hace en los otros dos:

> *«Todos los horarios válidos de Asia son **las 2, las 3 y las 4** de la mañana…
> si hay un mínimo en una de estas [otras] horas, no puedo buscar manipulación
> porque es un horario inválido»*

Y se le ve rechazar un setup que él mismo llama perfecto: *«este mínimo no me
sirve porque es el de las 6 de la mañana. Horario de Asia no válido.»*

## Su regla exacta NO se sostiene

| bloque | n | acierto | R bruta |
|---|---|---|---|
| **horas 2-4** · las que él llama válidas | 1.223 | 33,9 % | **+0,025** |
| horas 0-1 · las que llama inválidas | 1.538 | 33,4 % | +0,007 |
| **horas 5-7** · rechazó una de las 6 | 568 | **36,6 %** | **+0,102** |

**El bloque que descarta es mejor que el que acepta.** La hora de las 07:00 sola
da 39,8 % y +0,202 sobre 253 casos.

## Pero el efecto horario es real, y el corte está en otro sitio

| bloque | EURUSD | GBPUSD | NSXUSD | USDJPY | todos | n | z |
|---|---|---|---|---|---|---|---|
| 00-04 | −0,062 | +0,133 | −0,068 | +0,040 | +0,015 | 2.761 | +0,55 |
| 05-07 | +0,001 | +0,092 | — | +0,186 | +0,102 | 568 | +1,69 |
| 08-12 | +0,096 | +0,021 | −0,098 | −0,120 | −0,003 | 2.396 | −0,11 |
| **13-17** | +0,087 | +0,026 | +0,033 | +0,072 | **+0,054** | 5.022 | **+2,69** |
| **18-23** | −0,019 | −0,001 | −0,079 | −0,017 | **−0,026** | 9.669 | **−1,82** |

```
  BUENAS (05-07 y 13-17)  n=5.590  acierto 35,1 %  bruta +0,059  z +3,09  4/4 positivos
  MALAS  (18-22)          n=5.512  acierto 31,6 %  bruta -0,043  z -2,32  0/4 positivos
```

**Acierta en el principio y falla en los números.** El corte real no separa Asia
temprana de Asia tardía: separa **los niveles formados en sesión** (Londres tarde
y Nueva York, 13-17 h de Madrid) de **los formados de noche** (18-23 h).

Es exactamente el tipo de error que cabe esperar de una regla aprendida por
experiencia y no medida: el efecto existe, la explicación no.

## Lo que queda sin probar del live 159

La regla del CRT que da: la entrada vale más cuando **a la vela de H4 y a la de
H1 les queda el mismo tiempo para cerrar**, o sea cuando el barrido cae en la
última hora de la vela de H4. Es específica y falsable, y no se ha medido.
