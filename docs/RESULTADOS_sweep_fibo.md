# Resultados · sweep de H1 + retroceso de fibonacci

Su idea, con sus palabras: *«si en H1 hay liquidity sweep de la vela que crea el
rango, medir con el fibo el retroceso y hacer la entrada hasta el otro extremo»*.

## Cómo se ha montado

```
  RANGO     una vela de H1, i. Su alto y su bajo son el rango.
  SWEEP     la vela i+1 se sale del rango y CIERRA dentro otra vez.
              barre el alto -> setup bajista   ·   barre el bajo -> alcista
  PIERNA    del extremo barrido al otro lado de la vela de sweep.
  ENTRADA   limitada en el fibo 0,500 / 0,618 / 0,705 / 0,790 de esa pierna,
            dentro de las 4 horas siguientes.
  STOP      un 10 % de la pierna pasado el extremo barrido.
  OBJETIVO  «extremo» = el otro extremo del RANGO   ·   o un 1:2 fijo.
  VIDA      24 horas. Se resuelve con M1 real; empate en el minuto = STOP.
```

Siete instrumentos, 2020-2026, **658.240 operaciones** en 56 celdas.

## Todas las celdas pierden

| fibo | objetivo | acierto medio | R neta media | positivas |
|---|---|---|---|---|
| 0,500 | 1:2 | 29,5 % | −0,240 | **0 de 7** |
| 0,500 | extremo | **41,9 %** | −0,252 | **0 de 7** |
| 0,618 | 1:2 | 30,7 % | −0,242 | **0 de 7** |
| 0,618 | extremo | 36,0 % | −0,247 | **0 de 7** |
| 0,705 | 1:2 | 31,3 % | −0,263 | **0 de 7** |
| 0,705 | extremo | 30,4 % | −0,262 | **0 de 7** |
| 0,790 | 1:2 | 31,3 % | −0,323 | **0 de 7** |
| 0,790 | extremo | 24,1 % | −0,311 | **0 de 7** |

*(el acierto de la fila «0,500 extremo» es el más alto de todo el proyecto para una
regla mecánica —41,9 %— y sigue perdiendo: el objetivo está más cerca del stop,
así que el listón sube con él)*

## Y la ventaja bruta, antes del coste, es cero

| fibo | objetivo | R bruta media | peor | mejor |
|---|---|---|---|---|
| 0,500 | 1:2 | −0,110 | −0,154 | −0,079 |
| 0,618 | 1:2 | −0,077 | −0,125 | −0,045 |
| 0,705 | extremo | −0,058 | −0,079 | −0,020 |
| 0,790 | extremo | **−0,049** | −0,076 | **+0,010** |

Una sola celda de 56 tiene bruto positivo, y es +0,010 R.

**No es que la idea sea mala: es que es neutra.** Igual que las seis familias
anteriores, aterriza en la geometría y el coste hace el resto. Es la séptima
comprobación del mismo hecho: `RESULTADOS_hay_patron.md` mide la correlación
direccional del EURUSD en 0,000 sobre 2,4 millones de minutos, y con eso ninguna
regla de «entro aquí, objetivo 1:k» puede salir del 1/(1+k).

## Reproducir

`python3 bt/sweep_fibo.py` · salida en `data/sweep_fibo_salida.txt`
