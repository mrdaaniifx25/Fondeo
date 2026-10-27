# BC · La regla del reinicio · **DESCARTADA**

Pre-registro en `BC_05`. Una pasada, como estaba comprometido.

# 1 · Qué se contrastó

El disparo de **transición** que ellos describen y que `BC_04` no implementaba:
las temporalidades mayores alineadas en una dirección, la de ejecución **en
contra**, y se entra cuando aparece la reiniciada que la realinea.

# 2 · La configuración principal

Fijada en `BC_05` §3 **por argumento y no por resultado**: huso UTC (rejilla
neutra) y lectura B (su definición escrita de qué crea un rango). Se eligió
deliberadamente distinta de la que había salido mejor en `BC_04` (UTC + A).

| | n | al año | acierto | bruta | **neta** | IC 95 % | z | recortada |
|---|---|---|---|---|---|---|---|---|
| **UTC · B · reinicio simple** | 1.845 | 461 | 12,8 % | −0,019 | **−0,165** | [−0,301, −0,029] | **−2,38** | −0,200 |
| UTC · B · reinicio estricto | 1.335 | 334 | 11,0 % | −0,032 | −0,207 | [−0,381, −0,032] | −2,33 | −0,256 |

Con 1.845 operaciones la prueba está **adecuadamente potenciada** (`BC_05` §4.1).

**El intervalo excluye el cero, pero por el lado negativo.** No es «no hay
evidencia»: es que la regla, tal como está especificada, pierde.

# 3 · Las variantes

**Cambiando cuántas temporalidades mayores se exigen:**

| | n | neta | z |
|---|---|---|---|
| 1 sola alineada | 3.985 | −0,223 | −4,99 |
| **2 alineadas** (principal) | 1.845 | −0,165 | −2,38 |
| las 3 alineadas | 401 | −0,076 | −0,52 |

Mejora al exigir más alineación, pero nunca cruza el cero: con las tres sigue en
−0,076 y sin significación.

**Las otras once celdas de la rejilla:**

```
UTC · A     -0,023      NY · A      -0,026      Madrid · A  -0,236
UTC · C     -0,170      NY · B      -0,164      Madrid · B  -0,143
                        NY · C      +0,021      Madrid · C  -0,091
Broker · A  -0,173      Broker · B  -0,189      Broker · C  -0,102
```

La única positiva es NY·C con **+0,021 y z +0,22**, o sea nada, y con la
recortada en −0,072. Ninguna de las doce supera ningún umbral.

# 4 · Lo que más dice del asunto

**El disparo de transición sale peor que el de estado.**

```
BC_04 · entrar cuando la de ejecución YA coincide        mejor celda  +0,133
BC_06 · entrar cuando pasa de estar en contra a coincidir  mejor celda  +0,021
```

Esa comparación es lo interesante, porque la regla del reinicio se presentaba
—con razón, viendo cómo la explican— como la pieza que faltaba y la que ordena
todo lo demás. Medida, **empeora el resultado en vez de mejorarlo**.

Y no es un detalle de implementación: la dirección es consistente en las doce
celdas y en las tres variantes de alineación.

# 5 · El filtro negativo · también al revés

La otra mitad de su respuesta no es una regla de entrada sino de abstención:

> «Si en esa temporalidad que tenemos cerrada al alza se nos crea una reiniciada
> bajista, **debemos protegernos**, porque las demás temporalidades todavía no
> han cerrado.»

Su predicción es clara: las operaciones tomadas **habiendo una reiniciada en
contra** deberían rendir **peor**. Medido sobre las operaciones de `BC_04`,
celda a celda:

| celda | con reiniciada en contra | sin ella | diferencia | z |
|---|---|---|---|---|
| UTC · A | +0,063 | +0,153 | −0,091 | −0,32 |
| UTC · B | +0,003 | −0,098 | +0,101 | +1,17 |
| NY · A | +0,031 | −0,095 | +0,126 | +0,52 |
| NY · B | −0,070 | −0,096 | +0,026 | +0,30 |
| Madrid · A | +0,034 | +0,002 | +0,032 | +0,13 |
| Madrid · B | +0,043 | −0,086 | +0,129 | +1,41 |
| Broker · A | +0,003 | +0,041 | −0,038 | −0,16 |
| Broker · B | +0,031 | −0,077 | +0,108 | +1,18 |

Media de las diferencias: **+0,049**, y **seis de ocho positivas**.

Ninguna alcanza significación —todas por debajo de |z| = 1,5— así que lo honesto
es decir que **no se detecta el efecto**. Pero conviene fijarse en el signo: el
punto estimado va **al revés** del que predicen. Las operaciones que su filtro
mandaría evitar salen, si acaso, ligeramente mejores.

# 6 · Salvedades, las mismas de siempre

Esto contrasta **mi lectura mecánica** de su regla:

- «Reiniciada» la he definido como llevarse el extremo contrario de la vela base
  del rango vivo. Es lo que se deduce de `BC_01` §3, pero ellos no lo escriben
  como fórmula.
- Sigo sin poder calibrar el huso. Por eso se reportan las doce celdas.
- La entrada al cierre de la vela de la reiniciada es decisión mía; ellos dicen
  «cuando aparece», que admite otras lecturas.

Si alguna de esas tres está mal, esto mide otra cosa. Lo que no cambia con
ninguna de ellas es el punto 4: **la misma comparación, con la misma lectura
mecánica en los dos lados, da peor con el reinicio que sin él.**
