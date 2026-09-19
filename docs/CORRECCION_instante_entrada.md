# Corrección · resolvía desde el inicio de la vela de entrada, no desde su cierre

Encontrado el 18 de septiembre de 2026 al desconfiar de un resultado demasiado
bueno (bruta +0,129 con z +7,5, la mayor del proyecto).

## El fallo

Las velas de M5 y M15 llevan la marca de tiempo de su **primer** minuto. La
entrada es al **cierre**. Al resolver desde la marca, los 5 o 15 minutos de la
propia vela de entrada entraban dentro de la operación: **recorrido que ya había
ocurrido cuando se decide entrar**.

    mal   i = searchsorted(t1, marca, "right")
    bien  i = searchsorted(t1, marca + duracion_vela, "left")

## Dónde estaba

`bt/barrido_sesion.py`, `bt/barrido_sesion_v2.py`, `bt/barrido_ml_datos.py`,
`bt/sweep_choch.py`, `bt/sweep_pivote.py`.

**No estaba** en `bt/doble_barrido*.py` (sumaba la duración correctamente) ni en
`bt/analiza_barridos.py` ni en `bt/donde_estaba_buena.py`, que usan `utc_de` con
`+1` vela. Esos resultados no cambian.

## Qué cambia, y en los dos sentidos

El sesgo **no era sistemático a favor**: depende de si el stop o el objetivo cae
más cerca dentro del recorrido de la vela de entrada.

| resultado | antes | corregido |
|---|---|---|
| barrido de sesión C2, bruta | −0,0170 (z −1,46) | **+0,0387 (z +3,28)** |
| su gatillo de estructura H4+M15, bruta | −0,1762 (z −4,19) | **−0,0837 (z −1,93)** |
| su gatillo H1+M5, bruta | −0,0711 (z −2,81) | **−0,0060 (z −0,23)** |
| modelo, decil superior, neta | −0,0644 | **−0,0567** |
| modelo, decil superior, bruta | +0,0479 (z +3,94) | **+0,0499 (z +4,11)** |

**Lo que hay que retirar de lo dicho:** que su cambio de estructura fuera
*"significativamente peor que el azar"*. No lo es. En H1+M5 su bruta es cero.

**Lo que aguanta:** la conclusión del modelo. El decil superior apenas se mueve,
porque ahí el stop es ancho y el recorrido de una vela pesa poco frente al riesgo.

## El reto de fondeo, recalculado

| escenario | R media | las dos fases | intentos |
|---|---|---|---|
| decil superior (pre-registrado) | −0,0567 | **19,0 %** | 5,3 |
| mejor corte medido (stop ≥10 p) | +0,0125 | **34,6 %** | 2,9 |
| si el coste bajara a 0,97 pips | +0,0371 | 41,3 % | 2,4 |
| moneda al aire | 0,0000 | 31,4 % | 3,2 |

    ya fondeado: llegar a +7,5 % antes de reventar   58,7 %
                 repetirlo seis meses seguidos        4,07 %

El corte de ≥10 pips pasa a **neta +0,0125**, positiva por primera vez, con
IC95 [−0,015, +0,040] — el cero dentro. **No estaba pre-registrado**, se eligió
después de ver la tabla, y por el criterio escrito la respuesta sigue siendo que
no se cumple: el decil superior completo da −0,0567 con el intervalo entero por
debajo de cero.

## La lección, que es la de siempre

El fallo se encontró porque un número salió **demasiado bueno**, no porque saliera
malo. Es la tercera vez en el proyecto. Un resultado que mejora de golpe merece
más desconfianza que uno que empeora.
