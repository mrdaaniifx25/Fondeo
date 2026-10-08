# Resultados · el AMD en todo el histórico de EURUSD

Pre-registro `docs/PREREGISTRO_amd.md`. Código en `bt/amd_estudio.py` y
`bt/amd_dinero.py`. Stop y objetivo medidos **igual** (los dos por toque) y el
camino resuelto en M1, que es lo único que no se inventa el orden dentro de la
vela.

## 1 · Sí, la fase de acumulación importa

Ordenando las secuencias por lo estrecho que era el rango, y comparando el
acierto contra el que da la pura geometría (`justo`):

**M15, n = 12, 15.044 secuencias**

| quintil | estrechez | acierto | justo | diferencia | bruta |
|---|---|---|---|---|---|
| 1 más apretado | 0,80 | **22,1 %** | 19,3 % | **+2,8** | −0,039 |
| 2 | 1,00 | 18,6 % | 17,2 % | +1,4 | −0,142 |
| 3 | 1,16 | 15,7 % | 15,8 % | −0,1 | −0,157 |
| 4 | 1,35 | 11,8 % | 14,0 % | −2,2 | −0,325 |
| 5 más ancho | 1,69 | 9,3 % | 12,3 % | −3,0 | −0,376 |

**Y se repite en las tres temporalidades**, con el mismo orden:

    M15   +2,8  +1,4  -0,1  -2,2  -3,0
    H1    +2,2  +1,0  -0,6  -3,6  -5,6
    H4    +3,8  -0,6  -3,4  -3,7  -4,2

Un gradiente monótono que aparece igual en tres escalas distintas no se produce
por azar. **La A no es un adorno: un barrido que sale de un rango apretado se
comporta distinto de uno que sale de un rango cualquiera.** Es el primer
resultado del proyecto en el que la fase de acumulación demuestra aportar.

## 2 · Pero lo mejor que consigue es empatar

El quintil apretado bate a la geometría, y su ventaja bruta es:

    M15   -0,039        H1   -0,099        H4   -0,053

**Cero.** Batir a la geometría por dos o tres puntos, con un R:R de 4, deja la
esperanza justo en la raya. No la cruza.

Y el quintil ancho da −0,38. Así que lo que hace la estrechez es **separar lo
neutro de lo malo**, no fabricar lo bueno.

## 3 · Y el peaje remata

| | riesgo | coste %R | bruta | **neta** |
|---|---|---|---|---|
| M15, apretado | 3,2 p | 45 % | −0,039 | −0,744 |
| H1, apretado | 7,0 p | 20 % | −0,099 | −0,426 |
| **H4, apretado** | **14,7 p** | **10 %** | −0,053 | **−0,218** [−0,51, +0,07] |

El stop va al extremo del barrido, que en M15 está a 3 pips. Otra vez lo mismo.

H4 es la única celda cuyo intervalo toca el cero, y sólo porque tiene 224 casos.

## La mejor configuración, que es lo que pidió

Para **describir** las fases, que es lo que hace el indicador:

    temporalidad   H4  (o H1)
    velas del rango   8
    estrechez máxima  0,90

En M15, `n = 12` y estrechez `0,90`. Por encima de 1,2 de estrechez lo que marque
el indicador es peor que el azar y conviene no mirarlo.

## Una nota metodológica que hay que dejar escrita

En la primera versión el stop saltaba por **toque** y el objetivo pedía **cierre**.
Eso es injusto contra la operación y hundía el acierto unos 4 puntos. Corregido a
toque contra toque y resuelto en M1, el quintil apretado pasa de 18,5 % a 22,1 %.
Medir las dos barreras igual no es un detalle: era la diferencia entre "por debajo
del azar" y "por encima del azar".

## Veredicto

    ¿aporta la A?              SI, con gradiente y replicado en tres escalas
    ¿supera la D al azar?      SI en el quintil apretado, +2,8 puntos
    ¿es rentable?              NO. Bruta cero, y el peaje la hunde.

El indicador vale como **descripción** —y ahora se sabe con qué ajustes describe
algo y con cuáles describe ruido— pero no como señal de entrada.
