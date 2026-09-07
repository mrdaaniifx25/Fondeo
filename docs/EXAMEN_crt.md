# Examen CRT · para mirarlo tú mismo

Dos piezas. La primera es un indicador que puedes poner en tu gráfico y que
calcula su propia estadística delante de ti. La segunda es una lista de todas
las señales del periodo fuera de muestra, sin filtrar ninguna.

---

## 1 · El indicador · `pine/CRT_operativo.pine`

Cópialo entero en TradingView → Pine Editor → *Añadir al gráfico*.

**Ponlo en gráfico de 12 HORAS.** Es la única temporalidad donde el coste baja
del 4 % del riesgo. En M15 o H1 el coste se come cualquier ventaja, y eso está
medido en `RESULTADOS_crt_temporalidad.md`.

Marca **COMPRA** y **VENTA** con entrada, stop, objetivo, R:R, riesgo en pips y
qué porcentaje del riesgo se lleva el coste. Y arriba a la derecha pone una
tabla con dos líneas que son las que importan:

    ACIERTO real      <- lo que hizo el patrón
    acierto por AZAR  <- lo que daría una moneda con esa misma geometría

**Si la primera no supera a la segunda, no hay ventaja.** Es toda la prueba, y
la hace el indicador solo, sobre el instrumento y el periodo que tú cargues.

Ajusta el coste según el par: EURUSD 1,43 · GBPUSD 1,60 · USDJPY 1,50. Son
medidos. **USDCAD no lo he medido nunca** — prueba con 2,0 y compruébalo tú en
tu bróker.

### Por qué USDCAD es la prueba buena

No tengo, ni he tenido nunca, datos de USDCAD. No he corrido un solo test sobre
ese par. Así que nada de lo que hay en este indicador puede estar ajustado a
él. Póntelo ahí y lo que salga es limpio del todo.

### Para comprobar que el indicador es fiel

Cárgalo en EURUSD 12H desde enero de 2026 y la tabla debería dar algo
parecido a esto (no idéntico: TradingView usa otro feed y otra hora de corte
para las velas de 12 h):

    ~130 señales  ·  acierto ~20 %  ·  azar ~32 %  ·  R neta ~ +0,13

Si te sale algo radicalmente distinto, es que la zona horaria del gráfico está
cambiando dónde empiezan las velas de 12 horas. Avísame.

---

## 2 · El examen · `data/examen_crt_preguntas.csv`

**392 señales. Todas las del periodo. Sin filtrar ninguna.**

Van de enero a julio de 2026 en EURUSD, GBPUSD y USDJPY — el tramo fuera de
muestra, porque la configuración se eligió mirando solo 2020-2023.

- `examen_crt_preguntas.csv` — fecha, par, COMPRA/VENTA, entrada, stop,
  objetivo, R:R y coste. **Sin el resultado.**
- `examen_crt_respuestas.csv` — lo mismo con lo que pasó en cada una.

Abre las preguntas, busca las fechas en tu gráfico, decide tú, y luego mira las
respuestas. No hay forma de que yo haya elegido cuáles enseñarte: son todas.

## Lo que salió, y te lo digo antes de que lo abras

     instr    n   R:R  objetivo  stop  vencida  acierto   azar   R BRUTA    R NETA
    EURUSD  133  3,44        27    73       33   20,3 %  31,6 %  +0,2117   +0,1335
    GBPUSD  130  3,10        24    78       28   18,5 %  32,6 %  -0,0767   -0,1434
    USDJPY  129  3,14        27    68       34   20,9 %  33,5 %  -0,0312   -0,0889
     TODOS  392  3,23        78   219       95   19,9 %  32,5 %  +0,0361   -0,0315

    suma total: -12,35 R  ·  al 1 % en una cuenta de 10.000 €: -1.235 €

**EURUSD sale positivo**: +0,1335 R neta sobre 133 señales, que en tu cuenta de
10.000 € al 1 % serían +1.335 € en siete meses. No te lo escondo y no te lo
vendo: **uno de cada tres pares tenía que salir positivo por puro reparto.**
El conjunto es negativo, y el acierto real (19,9 %) está por debajo del azar
geométrico (32,5 %) en los tres pares a la vez.

Eso último es lo que hay que mirar. No es que gane poco: es que **acierta menos
veces de las que acertaría una moneda con la misma geometría**, en los tres.

---

## Qué haría yo con esto

Póntelo en USDCAD, que es el par limpio, y en los años que quieras. Si la
columna del acierto real se pone por encima de la del azar de forma sostenida,
tráemelo y lo medimos en serio. Si no, ya lo has visto tú con tus ojos y no
hace falta que te lo diga yo.
