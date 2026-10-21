# Resultados · el barrido de sesión con sus correcciones

Código en `bt/barrido_sesion_v2.py`. Corrección del pre-registro, contestada por
él antes de medir. Tres cambios: stop al extremo de la excursión entera, se
intentan todos los barridos, la confirmación no caduca.

## La celda principal

    C2, Londres + NY   n 14.637   8,91 operaciones al día
                       acierto 32,8 %   (necesita 41,4 %)
                       riesgo 5,9 p     coste 24,2 % del riesgo
                       bruta -0,0170 (z -1,46)      NETA -0,3068
                       IC95 [-0,330, -0,284]        z -26,03

**El criterio no se cumple**, y el intervalo está aún más abajo que en la v1.

## Lo que cambió al aplicar sus correcciones

| | v1 (mis reglas) | v2 (las suyas) |
|---|---|---|
| operaciones | 3.055 | **14.637** |
| al día | 1,92 | **8,91** |
| acierto | 34,3 % | 32,8 % |
| bruta | +0,0291 | −0,0170 |
| neta | −0,2577 | −0,3068 |

Quitar "un nivel, una operación" multiplica la muestra por cinco y empeora todo.
Las repeticiones sobre un nivel ya barrido son peores que la primera.

## Y eso devuelve el hueco donde puede vivir su criterio

**La regla escrita da 8,91 señales al día. Él toma una o dos.**

En la v1 escribí que estaba "eligiendo 2 entre 2" y que le quedaba poco sitio.
Con su corrección eso deja de ser cierto: **está eligiendo 2 entre 9**. Descarta
el 80 % de lo que la regla dispara, y ese descarte no está en ninguna parte del
texto que escribió.

## Su confirmación sigue siendo lo mejor que hay

    C1 · al cierre del barrido     acierto 25,4 %   bruta -0,2377  (z -23,15)
    C2 · esperando confirmación    acierto 32,8 %   bruta -0,0170  (z  -1,46)

**+0,22 R de bruta**, otra vez. Sube el acierto 7,4 puntos y ensancha el stop de
4,3 a 5,9 pips. Es el único componente de todo el proyecto que aporta de forma
repetida y grande, y es suyo.

## El año que lo explica todo

| año | acierto | riesgo | coste %R | bruta | neta |
|---|---|---|---|---|---|
| 2022 | 32,2 % | **8,2 p** | 17,4 % | −0,034 | **−0,239** el menos malo |
| **2024** | **35,8 %** | 4,6 p | 31,1 % | **+0,074 (z +2,43)** | −0,305 |

2024 es el único año con bruta positiva y significativa, y aun así pierde más que
2022, que tiene la bruta negativa. La diferencia es el ancho del stop. Es la
misma lección que lleva saliendo dos meses, escrita esta vez por sus propios años.

## Veredicto

La regla escrita, con sus correcciones, **da cero en bruto y −0,31 en neto** sobre
14.637 operaciones. Ningún año positivo en neto, ninguna sesión, ningún lado.

Lo que queda sin medir, y ahora es lo único que queda:

**Cuál de las nueve señales diarias toma él, y en qué vela exactamente entra.**
Preguntado directamente, contestó *"no sé cuándo entras, necesitaría verlo"*.
Ése es el siguiente paso, y no se puede contestar con texto.
