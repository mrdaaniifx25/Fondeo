# Resultado · ¿qué distingue un rango CRT que se completa?

Idea del usuario: *"creo que el CRT sí funciona pero hay algo dentro que se
nos escapa"*. Razonable, porque la ventaja bruta del CRT está medida y es real
(+0,082 R, homogénea entre temporalidades).

Lo probado hasta ahora eran cosas **añadidas por fuera** (confluencias, fibo,
contexto, M15+M1). Esto mide propiedades **del propio setup**.
Código en `bt/crt_anatomia.py`. H4, cinco instrumentos, 16.957 setups.

## El resultado

    R bruta global +0,0072 (z +0,64)   ·   neta -0,1004 (z -9,00)

    1 TAMANO del rango (x ATR)      z de +1,42 a -1,54
    2 PROFUNDIDAD del barrido       z de +1,26 a -0,87
    3 CIERRE dentro del rango       z de +1,58 a -0,44
    4 HORA del barrido              z de +2,58 a -2,05

**Ninguna propiedad discrimina.**

## Lo del horario

La franja 19-24 UTC da z +2,58 y bruta +0,1062. Pero son **19 comparaciones**
en total, y con 19 contrastes `P(algún |z| > 2,58)` por azar es del **17 %**.
Y su neta sigue siendo **-0,0567**.

## Lo que sí enseña, y es lo interesante

     cierre dentro del rango     n     R:R     BRUTA
     (0,0 - 0,3]  justo dentro  8966   3,20   +0,0048
     (0,3 - 0,5]                3836   1,02   +0,0259
     (0,5 - 0,7]                2375   0,51   -0,0064
     (0,7 - 1,0]  casi al fondo 1780   0,17   -0,0031

El mecanismo que él intuía **es real**: cuando la vela cierra justo por dentro
del rango queda todo el recorrido y el R:R es 3,20; cuando cierra al fondo, es
0,17. Diecinueve veces más recorrido.

**Y la R bruta es la misma (≈0) en las cuatro filas.**

El mercado ya lo tiene puesto en el precio: da más recorrido exactamente donde
la probabilidad de alcanzarlo es proporcionalmente menor. Es la demostración
más limpia de todo el proyecto de por qué la geometría no regala nada.

## Lo que queda sin probar en esta línea

    · propiedades de la vela ANTERIOR al rango (no del rango ni del barrido)
    · secuencias: si N rangos seguidos se completaron, ¿el siguiente cambia?
    · el rango en relacion a niveles de OTRAS temporalidades
