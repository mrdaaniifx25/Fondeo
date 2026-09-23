# Resultado · las familias clásicas de indicadores, en el panel largo

Pre-registro: `docs/PREREGISTRO_indicadores.md`. Un solo pase.
Código: `bt/indicadores.py` y `bt/indicadores_diagnostico.py`.
25 series, 14.533 días, **1971 a 2026**, 265.533 observaciones útiles.
Estadístico sobre los **meses** (657), no sobre los días.

---

## Primero la respuesta: sí, aquí sí funciona

Y no un poco. Todas las familias de tendencia, a la vez:

```
familia              rot/año  corrROC  meses    BRUTO      t     NETO      t  Sharpe
  MM 50/200              6,4     0,59    659  +0,5748  +5,11  +0,5723  +5,09   +0,69
  MM 20/100              5,2     0,40    661  +0,7784  +6,99  +0,7731  +6,94   +0,94
  MM 10/50               6,7     0,29    661  +0,8945  +7,60  +0,8839  +7,51   +1,01
  MACD 12/26/9          19,3     0,00    661  +0,5904  +5,56  +0,5576  +5,24   +0,71
  MACD 12/26             7,9     0,29    661  +0,9280  +7,83  +0,9147  +7,71   +1,04
  RSI 14 reversión       7,3    -0,30    661  -0,6890  -8,11  -0,6953  -8,18   -1,10
  RSI 14 momento        25,4     0,25    661  +0,9231  +7,90  +0,8802  +7,50   +1,01
  Donchian 20            7,3     0,22    661  +0,9866  +8,54  +0,9741  +8,43   +1,14
  Donchian 55            2,7     0,35    661  +0,7869  +6,92  +0,7823  +6,88   +0,93
  canal ATR 20/2         7,7     0,24    661  +0,9665  +8,25  +0,9535  +8,13   +1,10
  ROC 250                9,3     1,00    657  +0,7058  +5,94  +0,6964  +5,86   +0,79
  ROC 20                24,8     0,21    661  +1,0021  +8,84  +0,9623  +8,46   +1,14

  comprar y mantener     0,0        -    661  +0,2302  +1,51  +0,2302  +1,51   +0,20
```

Diez de las doce con t por encima de +5. El mejor Sharpe, 1,14. Y el coste
apenas muerde: del bruto al neto se pierde un 4 %.

**Esto no es un hallazgo mío.** Es el seguimiento de tendencia, documentado
desde los años ochenta, con resultados auditados de gestoras reales. Lo único
que hace esta tabla es confirmarlo en este panel. Y explica de golpe por qué
tres meses de mediciones intradía dieron cero: **no era el indicador, era el
horizonte.** El mismo RSI que en H1 da +0,001 (`RESULTADOS_rsi_h1.md`), en
diario da t +7,90.

Y ahora las tres cosas que lo desmontan.

---

## 1 · No son once estrategias. Es una.

Correlación media entre los rendimientos mensuales de las once: **0,62**.
El 19 % de los meses van las once en el mismo sentido.

```
  mezcla de las once     t +8,66   Sharpe +1,17
  mejor individual       t +8,54   Sharpe +1,13
```

Juntar once indicadores distintos sube el Sharpe de 1,13 a 1,17. **Nada.** Si
de verdad fuesen once apuestas, once señales independientes darían √11 ≈ 3,3
veces más Sharpe. Dan 1,03 veces más.

MACD, Donchian, canal ATR, cruce de medias, RSI por encima de 50: todos son
**el mismo filtro paso-bajo del precio con otro nombre.** La tabla de arriba no
son doce números, es uno repetido doce veces.

## 2 · Un tercio sale de cinco divisas que no se pueden operar

Desglosando qué series aportan:

```
  top 8: Taiwán 1094 · China 753 · Malasia 741 · Dinamarca 608 · Corea 594 ·
         Suecia 589 · Tailandia 576 · Japón 558
  las cinco primeras = 37 % del total
```

Taiwán, China, Malasia, Corea, Tailandia. **Divisas ancladas que se devaluaron
de golpe.** Una moneda pegada tiene volatilidad casi nula durante años, así que
la normalización por volatilidad le da un peso enorme, y cuando rompe el ancla
el seguidor de tendencia se lleva el movimiento entero.

Es real, pasó. Pero el coste que he aplicado es **el de EUR/USD: 1,43 pips.**
En el baht tailandés de 1997 la horquilla real era diez o cincuenta veces eso, y
durante la crisis el mercado directamente cerró. El número está inflado y no sé
por cuánto.

*(El relleno de comillas no explica nada: repitiendo todo sin días rellenados y
sin rendimientos exactamente cero, los resultados no se mueven —MM 50/200 pasa
de +5,09 a +5,05.)*

## 3 · Y esto es lo que importa: se ha acabado

Partición temporal declarada de antemano. Panel completo:

```
familia                   1971-1999        2000-2012        2013-2026
  MM 50/200             +0,93 t +5,18    +0,45 t +2,32    -0,04 t -0,20
  MM 20/100             +1,17 t +6,77    +0,54 t +2,85    +0,19 t +0,97
  Donchian 20           +1,51 t +8,17    +0,60 t +3,05    +0,23 t +1,37
  Donchian 55           +1,18 t +6,55    +0,50 t +2,62    +0,23 t +1,25
  canal ATR 20/2        +1,46 t +7,76    +0,58 t +2,91    +0,26 t +1,56
  ROC 250               +1,07 t +5,71    +0,41 t +1,94    +0,21 t +1,12
  MACD 12/26/9          +0,86 t +4,98    +0,47 t +2,82    +0,01 t +0,07
```

Monótono y en las doce familias a la vez: **t +5..+8 → t +2..+3 → cero.**

Y restringiendo al universo que él puede operar de verdad —G10 y materias
primas, 14 series líquidas y flotantes, sin ancladas ni exóticas:

```
familia               2013-2026
  MM 50/200            t -0,68
  MM 20/100            t -0,49
  Donchian 20          t -0,40
  Donchian 55          t -0,36
  canal ATR 20/2       t -0,12
  ROC 250              t +0,34
  MACD 12/26/9         t -0,93
  RSI 14 momento       t -0,71

  mezcla de las once   efecto -0,0718   t -0,47   Sharpe -0,13
  familias positivas en el tramo: 1 de 11
```

**Trece años, catorce mercados líquidos, once familias de indicadores: una sola
positiva, y ninguna significativa.**

Y no es el coste. Poniendo el coste a cero, Donchian 55 en ese tramo sigue en
−0,0703. No es que la ventaja no cubra la horquilla: **es que no hay ventaja.**

## El único resultado nuevo y fuerte: el RSI de reversión pierde

```
  RSI 14 reversión   t -8,11   Sharpe -1,10   ·  1971-99 t -7,48  2000-12 t -3,23
```

Comprar sobrevendido y vender sobrecomprado —la familia a la que pertenece la
mitad del contenido de trading que circula, incluida la estrategia del vídeo de
`RESULTADOS_rsi_h1.md`— **no da cero. Da negativo, con t −8 sobre 55 años.**

Es el espejo exacto del seguimiento de tendencia, y tiene el mismo mecanismo: si
la tendencia paga, apostar contra ella cobra al revés. Esto sí es accionable, en
negativo: **una estrategia de «rebote en sobreventa» no es una moneda al aire.
Es una moneda sesgada en contra.**

*(En G10 2013-2026 también se ha ido: t +0,28. Lo mismo que la tendencia, por el
mismo motivo.)*

## Mi predicción firmada, y las dos que fallé

| firmé | salió | |
|---|---|---|
| lentas positivas, t +2 a +5 | t +5 a +7 | ✔ (corto) |
| **rápidas ≈ cero en bruto y negativas en neto por rotación** | **las mejores de la tabla** | ✘ |
| RSI reversión ≤ 0 | t −8,11 | ✔ |
| **ninguna supera a ROC 250 en neto** | **seis la superan** | ✘ |
| corr. señal MM 50/200 con ROC 250 > 0,6 | 0,59 | ✘ por un pelo |

Los dos fallos son el mismo fallo: **llevé la intuición de intradía a un
horizonte donde no vale.** Di por hecho que rotar 25 veces al año mataría a las
rápidas, porque en M15 rotar mata. En diario el coste se lleva el 4 % del bruto,
así que rotar no cuesta casi nada y las rápidas ganan.

Lo irónico es que eso está escrito en este mismo repositorio desde hace semanas
—`RESULTADOS_muro_horizonte.md`, el muro baja 20 veces de una hora a un mes— y
aun así firmé lo contrario. Anotado.

## Qué contesta esto

A la pregunta *«¿y montar una estrategia con indicadores, medias, RSI, MACD,
ATR?»*, la respuesta honesta tiene tres partes:

1. **Sí, y es lo único que ha medido positivo en tres meses.** Con t +8 y 55
   años. Los indicadores nunca fueron el problema; el horizonte lo era.
2. **Pero es una sola apuesta, no once**, y un tercio de ella sale de divisas
   ancladas que hoy no existen y cuyo coste real desconozco.
3. **Y en mercados líquidos lleva trece años sin aparecer.** Cero, no pequeño.

Lo cual no contradice `RESULTADOS_momento_largo.md`: allí el tramo 2013-2026 ya
daba t +0,91 y Sharpe 0,25, es decir **45 € al mes sobre 50.000 €**. Esta medida
lo confirma por otras once vías y añade la mala noticia de que en G10 el
remanente es aún menor.

**No hay una versión de esto que dé 300 € al mes sobre 10.000 €.** Ni con
indicadores, ni sin ellos.
