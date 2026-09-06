# ¿Está bien hecho el backtest? · la validación que faltaba

Pregunta suya, y es la correcta: *«no sé si es cuestión de la manera que se hacen
los backtest o qué… ya dudo de absolutamente todo»*.

Si el motor está roto, dos meses de trabajo no valen nada. Hay una forma de
saberlo: **meterle entradas al azar**. Un motor correcto tiene que devolver
**esperanza cero** en todas las celdas. Si devuelve ventaja donde no la hay, o
pérdida donde no la hay, miente.

## El montaje

128.000 operaciones simuladas. Entrada al cierre de un minuto **elegido al azar**,
dirección al azar, con el mismo código de resolución que todas las estrategias del
proyecto: empate dentro del minuto = STOP, no resueltas cerradas a mercado.

Dos instrumentos × 4 tamaños de stop (5, 10, 20, 50) × 4 ratios (1:1, 1:2, 1:2,45,
1:3) = 32 celdas.

## El resultado: R bruta cero en 32 de 32

| | R bruta | z |
|---|---|---|
| EURUSD 20p 1:1 | +0,0062 | +0,39 |
| EURUSD 20p 1:2 | +0,0042 | +0,19 |
| EURUSD 20p 1:2,45 | −0,0072 | −0,30 |
| EURUSD 50p 1:2 | −0,0116 | −0,67 |
| EURUSD 50p 1:3 | −0,0111 | −0,60 |
| NSXUSD 20p 1:2 | +0,0057 | +0,26 |
| NSXUSD 50p 1:2,45 | −0,0106 | −0,43 |
| NSXUSD 50p 1:3 | +0,0159 | +0,58 |

**Ninguna celda pasa de |z| = 1,6.** La esperanza del azar es exactamente cero, que
es lo que tiene que salir. **El motor no inventa ventaja ni la destruye.**

## Un sesgo real encontrado por el camino

La primera versión de esta validación **tiraba** las operaciones que no se
resuelven dentro del horizonte. Con stops de 50 pips y objetivo 1:3 en EURUSD, la
mitad no se resolvían en 48 horas, y tirarlas sesgaba el acierto **20 puntos hacia
abajo**:

```
  tirando las no resueltas:    9,60 % contra un 25,0 % esperado   (z -23,48)
  cerrándolas a mercado:      R bruta -0,011                       (z  -0,60)
```

Las estrategias del proyecto **nunca las tiraron** —siempre se cerraron a
mercado—, así que el sesgo estaba en el validador y no en ellas. Pero conviene
tenerlo escrito: **descartar operaciones sin resolver es una forma silenciosa de
mentir en un backtest**, y es de las más comunes.

Nota sobre el acierto: con cierre a mercado, el porcentaje de aciertos **no** tiene
que dar 1/(1+k), porque una operación que acaba a mitad de camino no es un
acierto. Lo que sí tiene que dar cero es **la R bruta**, y da cero.

## Lo que esto establece

Que cuando el proyecto dice «esta estrategia aterriza en el azar», **es verdad**.
No es que el backtest sea pesimista, ni que le falte algo: es que la estrategia no
tiene ventaja. Y cuando dice que algo da +0,124 con z +2,55, ese +0,124 tampoco es
un artefacto del motor.

## Reproducir

`python3 bt/valida_motor.py`
