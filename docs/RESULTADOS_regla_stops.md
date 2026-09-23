# Resultados · la misma señal, ocho stops distintos

Pre-registro: `docs/PREREGISTRO_regla_stops.md`. Un solo pase.
**2.262 señales en 1.584 días**, 2020-2026.

## El resultado

| variante | stop | coste/riesgo | acierto | vs 33,3 % | z | R bruta | **R neta** | z neta |
|---|---|---|---|---|---|---|---|---|
| `M1 ×1` | 1,3 p | 110 % | 30,6 % | −2,8 pp | −2,59 | −0,083 | **−1,731** | −36,95 |
| **`M1 ×3`** | **2,8 p** | **51 %** | **31,2 %** | −2,1 pp | −2,06 | −0,062 | **−0,874** | −23,90 |
| `fijo 3p` | 3,0 p | 48 % | 31,2 % | −2,1 pp | −2,14 | −0,064 | −0,540 | −18,48 |
| `M5 señal` | 4,8 p | 30 % | 31,4 % | −1,9 pp | −1,94 | −0,057 | −0,459 | −15,14 |
| `fijo 5p` | 5,0 p | 29 % | 31,7 % | −1,6 pp | −1,65 | −0,049 | −0,335 | −11,41 |
| `M5 anterior` | 6,9 p | 21 % | 31,5 % | −1,8 pp | −1,80 | −0,053 | −0,385 | −12,51 |
| `fijo 8p` | 8,0 p | 18 % | 32,0 % | −1,4 pp | −1,37 | −0,041 | −0,219 | −7,47 |
| `fijo 20p` | 20,0 p | 7 % | 30,1 % | −3,3 pp | −2,97 | −0,080 | −0,152 | −5,78 |

Umbral Bonferroni para ocho variantes: |z| > 2,73. Ninguna neta se acerca.

## Lo que dicen estos números

**1 · El acierto no depende de lo ancho que sea el stop.**

De 1,3 pips a 20, el acierto va del **30,1 % al 32,0 %**. Una franja de dos
puntos, sin tendencia, y ninguna anchura se separa del 33,3 % geométrico por
encima del umbral. Es exactamente lo que predice la geometría de un 1:2 sobre un
paseo aleatorio: **el momento de entrada no lleva información**. Si la llevara,
los stops estrechos —los que dependen de acertar el momento— tendrían que
destacar, y no destacan.

**2 · Por eso la neta es, literalmente, la geometría menos el coste.**

Y como el coste en R es `coste / riesgo`, la neta mejora al ensanchar el stop, de
forma monótona en las anchuras fijas:

```
3 p  -0,540      5 p  -0,335      8 p  -0,219      20 p  -0,152
```

**3 · Su ajuste le cuesta 0,72 R por operación.**

Su stop real —la estructura de M1, 2,8 pips de mediana— da **−0,874 R**. El mismo
patrón, la misma mano, el mismo 1:2, con 20 pips de stop: **−0,152 R**. Con 1,43
disparos al día y 100 € de riesgo:

| stop | R/operación | al mes | con 100 € de riesgo |
|---|---|---|---|
| **el suyo, 2,8 p** | −0,874 | −26,2 R | **−2.621 €** |
| fijo 5 p | −0,335 | −10,0 R | −1.005 € |
| fijo 8 p | −0,219 | −6,6 R | −657 € |
| fijo 20 p | −0,152 | −4,6 R | −456 € |

**Tenía razón en el diagnóstico y se queda corto en la conclusión.** El ajuste del
stop le está costando cinco de cada seis euros que pierde. Y arreglarlo del todo
lo deja en −456 €/mes, no en positivo.

## La predicción firmada, punto por punto

| | |
|---|---|
| 1 · la neta sube al ensanchar y ninguna se pone positiva | **acierto** |
| 2 · `M1 ×3` será la peor de las ocho | **fallo** — es la segunda; la peor es `M1 ×1`, aún más estrecha. La dirección era buena, el nombre concreto no |
| 3 · el acierto quedará en o por debajo del 33,3 % sin superarlo | **acierto** |
| 4 · el coste pasará del 40 % en las dos de M1 | **acierto** — 110 % y 51 % |

## Un fallo del motor, corregido antes de leer nada

El primer pase resolvía desde el **mismo minuto** de la entrada. Como se entra al
cierre de la vela de M5 y ese minuto ya está formado, un stop pegado saltaba
siempre dentro de la propia vela de entrada: `M1 ×1` daba **0,0 % de acierto sobre
1.951 operaciones**. Se resuelve desde el minuto siguiente. Además, las que no
resuelven antes de las 22:00 se cuentan aparte y ya no deflactan el acierto: en
`fijo 20p` son el 18 %.

## Lo que esto NO mide

Mide **la regla**, que dispara 1,43 veces al día. No mide **su selección**, que se
queda con una parte de esos disparos. La diferencia entre las dos cosas es lo
único que puede salvar el asunto, y el instrumento que la mide es el simulador a
ciegas: 49 casos, 29,2 % de acierto.

## Reproducir

`python3 bt/regla_stops.py`
