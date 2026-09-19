# Resultados · AMD + FVG

Pre-registro `docs/PREREGISTRO_amd_fvg.md`. Código en `bt/amd_fvg.py`.
EURUSD, oro y DAX. Barreras medidas igual (las dos por toque).

## El criterio, primero

| | condición | resultado |
|---|---|---|
| 1 | CON FVG supera a SIN FVG en los tres | ✔ y por mucho |
| 2 | bruta positiva con IC95 entero sobre cero | **✔ solo EURUSD** |
| 3 | ≥ 200 operaciones por instrumento | ✔ 361 a 587 |

**No se cumple del todo.** Oro y DAX son positivos pero su intervalo incluye el
cero. El pre-registro exigía los tres.

## Lo que sí ha pasado, y no es poco

### El FVG cambia la operación entera

    H1, EURUSD
    SIN FVG   n 1.126   completa 13,0 %   R:R 3,9   riesgo  5,8 p   bruta -0,5231
    CON FVG   n   587   completa 76,5 %   R:R 0,4   riesgo 25,9 p   bruta +0,1048

No es un filtro que quita ruido: es **otra operación**. Al esperar al FVG entras
más tarde, el objetivo queda cerca y el stop lejos. Pasas de arriesgar 1 para
ganar 3,9, a arriesgar 1 para ganar 0,4 — y el acierto sube del 13 % al 76 %.

Y el riesgo pasa de 5,8 a **25,9 pips**, con lo que el peaje baja al **5,5 %**.
Es el mejor cociente coste/riesgo de todo el proyecto.

### Bate a la geometría, y en los tres

    exceso sobre el azar    EURUSD +6,2    oro +3,7    DAX +3,7

La rama SIN FVG da −11,6, −11,2 y −12,6. La diferencia entre las dos ramas es de
unos **15 puntos**, igual en los tres mercados.

### Y los trece años son positivos

    EURUSD  2021 +0,054  2022 +0,116  2023 +0,039  2024 +0,213  2026 +0,072
    oro     2023 +0,011  2024 +0,157  2025 +0,010  2026 +0,028
    DAX     2023 +0,002  2024 +0,022  2025 +0,068  2026 +0,012

**Trece de trece.** Ni un año negativo en bruta, en tres mercados distintos. Eso
no estaba pre-registrado y por eso no cuenta como criterio, pero es la señal más
consistente que ha dado este proyecto.

### Y la neta cruza cero

    EURUSD, coste 1,43 pips:  NETA +0,0390

Primera vez que una celda bien medida da neta positiva.

## Ahora lo que hay que decir para no engañarse

**1 · Solo EURUSD es significativo por separado.** Oro +0,055 [−0,021, +0,132] y
DAX +0,030 [−0,042, +0,102]. El signo coincide, la potencia no llega.

**2 · La forma de la operación es incómoda.** R:R 0,4 con 76 % de acierto son
muchas ganancias pequeñas y de vez en cuando una pérdida que se lleva dos o tres.
Psicológicamente es lo contrario de lo que él viene haciendo.

**3 · El tamaño, en dinero.**

    neta +0,039 x 150 EUR = +5,85 EUR por operación
    unas 100 operaciones al año en EURUSD  ->  +585 EUR al año
    vaiven de un mes: +-250 EUR

Esperanza de unos 48 EUR al mes contra un vaivén de 250. Es real y es pequeño.

**4 · Y lo más importante: esto es dentro de muestra.**

Los parámetros del rango (n = 8, estrechez 0,90) salieron del estudio del AMD
sobre estos mismos datos. No hay ajuste fino, pero tampoco hay una prueba
limpia. Y ya he mirado todo el histórico, así que **cualquier corte que haga
ahora estará contaminado por haberlo visto**.

## La única prueba que queda es hacia delante

No hay más datos que reservar. La prueba honesta es correrlo desde hoy, sin
tocar nada, y ver qué sale. Es lo que este proyecto lleva sin hacer desde agosto.
