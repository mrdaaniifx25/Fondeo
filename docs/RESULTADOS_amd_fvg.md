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

---

## Qué hace esto en una cuenta de 10.000 €

`bt/cuenta_10k.py`, 20.000 simulaciones con la distribución real de las 587
operaciones. Un año son 120 operaciones (117 medidas, ~10 al mes).

| riesgo | €/op | lotes | final medio | peor 5 % | mejor 5 % | caída máx | acaba perdiendo |
|---|---|---|---|---|---|---|---|
| 0,5 % | 50 € | 0,22 | 10.235 | 9.533 | 10.954 | −3,5 % | 29,7 % |
| **1 %** | **100 €** | **0,45** | **10.467** | 9.087 | 11.909 | −6,7 % | 29,8 % |
| 2 % | 200 € | 0,90 | 10.951 | 8.128 | 13.807 | −12,8 % | 29,3 % |
| 5 % | 500 € | 2,24 | 12.342 | 5.288 | 19.505 | −28,2 % | 29,5 % |

**Acaba el año perdiendo 3 de cada 10 veces en los cuatro casos.** Subir el
riesgo no mejora esa probabilidad: solo agranda los dos extremos.

Con **5 lotes** (1.114 € por operación, el 11 % de la cuenta):

    revienta la cuenta        12,8 %
    acaba bajo los 10.000     31,0 %

Uno de cada ocho años se queda a cero.

## Y por qué no llega a los 750 €/mes

    al 1 % de riesgo, un año:   +467 EUR
    750 EUR/mes serian:       +9.000 EUR

Factor de **19**. Para ganarlos habría que arriesgar unos 1.900 € por operación,
el 19 % de la cuenta por trade, más agresivo que los 5 lotes que ya revientan el
13 % de las veces.

**No existe un tamaño que saque 750 €/mes de 10.000 € con esto.** El motor da un
4,7 % anual y el objetivo pide un 90 %.

## Lo que sí es cierto, y es nuevo

Con tamaño sensato esta estrategia **no pierde dinero**, y es la primera del
proyecto de la que se puede decir eso. Todas las anteriores tenían el signo
negativo. El salto de aquí a 750 €/mes no lo da una estrategia mejor: lo da el
capital.
