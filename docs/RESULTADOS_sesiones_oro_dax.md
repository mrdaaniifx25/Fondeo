# Resultados · sesiones en oro y DAX — y una retractación

Pre-registro: `docs/PREREGISTRO_sesiones_oro_dax.md`, subido en `ddf3ee9`
**antes** de medir. Código: `bt/sesiones_oro_dax.py`.

## El criterio 1 falla, y eso manda sobre todo lo demás

El pre-registro exigía, antes que nada, que **EURUSD reprodujese la bruta
conocida de +0,06 a +0,11**. Si el control no sale, nada de lo demás se lee.

```
EURUSD (control)   k·ATR      n   días    stop   coste     %TP   R bruta
                     0.0    875    808     6.5   29.0%   33.1%    +0.007
                     1.0    875    808     7.0   22.8%   33.4%    +0.014
                     2.0    875    808    10.4   14.7%   31.3%    -0.036
```

**+0,007 en vez de +0,085.** El control no reproduce.

## Qué pasó: no es el porte, son los datos

Para descartar que fuese un error mío, volví a correr **el código de agosto sin
tocar una línea** (`bt/asia_nivel.py` y `bt/asia_contexto.py`) sobre los datos
de hoy:

```
                                     n      %TP    R bruta   neta/día      z
agosto, datos de agosto (2020-2025)  1.454   34,9%   +0,071    -0,208    -4,50
hoy,    datos de hoy    (2021-2025)    781   32,3%   -0,022    -0,283    -5,41
```

El mismo código, la misma regla, el mismo filtro. **La ventaja bruta de +0,071
es hoy −0,022.**

La diferencia son los datos. El parquet de EURUSD se reconstruyó con los ZIP que
él subió: ahora va de **2021 a 2026**; el de agosto incluía **2020** y un fichero
suelto de agosto de 2026 que ya no está. Y no es sólo el rango: para la misma
etiqueta de 2020-2025 el fichero de agosto daba 2.080 disparos y el de hoy da
1.720, así que el propio minuto a minuto viene de una fuente distinta.

Por año, con los datos de hoy:

```
   año      n     %TP   R bruta                IC95
  2021    152   38.2%    +0.153  [-0.079,+0.385]
  2022    152   32.2%    -0.024  [-0.248,+0.199]
  2023    154   28.6%    -0.130  [-0.345,+0.085]
  2024    159   31.4%    -0.057  [-0.274,+0.161]
  2025    164   31.1%    -0.047  [-0.260,+0.165]
  2026     94   40.4%    +0.246  [-0.051,+0.544]
```

Cuatro años seguidos en negativo. Los dos positivos tienen el cero dentro.

**Retractación.** `RESULTADOS_asia_contexto.md` y `RESULTADOS_asia_ancho.md`
llamaban a esto «el hallazgo firme del proyecto». No lo es. La ventaja bruta que
sostenía aquello no aparece en los datos actuales. Lo que **sí** sobrevive es
mucho más débil: el filtro sigue **separando** (diferencia +0,240, z +3,03; en
agosto era +0,916 con z +9,92), pero **los dos lados son negativos**. Separa
malo de peor, no bueno de malo.

No puedo decidir entre las dos explicaciones posibles —que la ventaja viviese en
2020, que fue un año de rangos enormes, o que las dos fuentes de datos no sean
comparables— porque **el fichero de 2020 ya no está en el repositorio**.

## Oro y DAX, para el registro

Se publican aunque el control haya fallado, porque estaban declarados.

```
instrumento    k·ATR      n   días     stop   coste    %TP   R bruta          NETA/op
oro              0.0    865    563    242.9   24.5%  32.1%    -0.034   -0.2785
oro              1.0    865    563    308.3   12.4%  34.3%    +0.032   -0.0921
oro              1.5    865    563    411.2    9.1%  35.0%    +0.056   -0.0352 [-0.1304,+0.0600]
oro              2.0    865    563    538.4    7.0%  33.8%    +0.046   -0.0247 [-0.1189,+0.0694]

DAX              0.0    568    439     25.4    9.2%  34.9%    +0.068   -0.0238
DAX              0.5    568    439     25.5    7.8%  35.4%    +0.084   +0.0058 [-0.1121,+0.1237]
DAX              1.5    568    439     35.1    5.1%  33.6%    +0.033   -0.0174
DAX              2.0    568    439     43.7    4.1%  34.0%    +0.090   +0.0492 [-0.0670,+0.1653]
```

Ninguna celda cruza con el intervalo limpio. El sesgo de selección declarado era
**+0,085** y la mejor celda da +0,0492.

Lo único que se repite, y ya van cuatro pruebas seguidas, es la forma de la
curva: **al ensanchar el stop el coste se desploma y la neta sube**. En oro,
de −0,279 a −0,025 al pasar de stop natural a 2 ATR. Sube hasta cero y se para.

## Criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. el control de EURUSD reproduce +0,06 a +0,11 | **NO.** +0,007 |
| 2. oro y DAX con neta > 0 y el IC limpio | NO |
| 3. por encima de +0,085 | NO |
| 4. mismo signo en los dos | parcial |

## Récord de predicciones

Dos de cinco. El fallo grande es el primero, y es el que importa.

| predicción | resultado |
|---|---|
| el control reproducirá +0,06 a +0,11 | **+0,007** ✘ — y esto retracta el hallazgo |
| oro y DAX darán bruta entre +0,02 y +0,06 | oro +0,056, DAX +0,033 a 1,5 ATR ✔ |
| la neta cruzará el cero en oro hacia 1,0-1,5 ATR | llega a −0,025, no cruza ✘ |
| ningún intervalo quedará limpio del cero | ninguno ✔ |
| el criterio no se cumplirá | no se cumple ✔ |

## Lo que esto cambia

El proyecto tenía tres resultados vivos. Ahora tiene dos:

1. ~~El filtro de contexto de M15 y H1 sobre el barrido de Asia~~ — **retirado**.
2. El CRT en H4 con R:R 2,0: exceso +3,5, neta −0,010 (`RESULTADOS_barrido_rr.md`).
3. El stop mínimo: la neta sube al ensanchar, sin intervalo limpio
   (`RESULTADOS_stop_minimo.md`).

Y los tres, más éste, dicen el mismo número: **la ventaja bruta que produce
cualquier cosa que hemos encontrado es de +0,03 a +0,10 R, y el coste vale lo
mismo.** Eso no es mala suerte repetida cuatro veces. Es la medición.
