# ¿Cuánto se puede sacar de verdad de 10.000 €?

Código `bt/cuanto_10k.py`. 20.000 simulaciones del año por celda.

Se usa **lo mejor medido en todo el proyecto**: el CRT en H12
(`docs/RESULTADOS_crt_temporalidad.md` y `docs/RESULTADOS_crt_tf_partido.md`).

```
bruta +0,125 R · neta +0,072 R · acierto 46,1 % · R:R mediano 1,38
471 operaciones al año repartidas entre 5 instrumentos
IC 95 % de la neta: [-0,027, +0,136]   <- el cero esta DENTRO
```

Por eso se simulan **los tres escenarios del intervalo**, no sólo el centro.

## Corrección de una cifra anterior

En el mensaje anterior se dijo «63 € al mes» usando **sólo EURUSD** (94
operaciones al año). Repartiendo las mismas operaciones entre los cinco
instrumentos son 471, y el resultado se multiplica por cinco. Aquel 63 € era un
suelo, no la cifra.

## Resultados

### Riesgo 0,5 % por operación

| ventaja | fin de año | al mes | caída máx. | años que pierden | toca −10 % |
|---|---|---|---|---|---|
| −0,027 | 9 247 € | −63 € | 16,1 % | 72,0 % | 87,3 % |
| **+0,072** | **11 730 €** | **+144 €** | **9,2 %** | **9,9 %** | **40,1 %** |
| +0,136 | 13 690 € | +308 € | 7,1 % | 0,8 % | 15,1 % |

### Riesgo 1 %

| ventaja | fin de año | al mes | caída máx. | años que pierden | toca −10 % |
|---|---|---|---|---|---|
| −0,027 | 8 617 € | −115 € | 30,3 % | 74,7 % | 99,9 % |
| **+0,072** | **13 533 €** | **+294 €** | 17,8 % | 12,1 % | **97,2 %** |
| +0,136 | 18 430 € | +702 € | 14,0 % | 0,9 % | 89,0 % |

### Riesgo 2 %

| ventaja | fin de año | al mes | caída máx. | años que pierden | toca −10 % |
|---|---|---|---|---|---|
| −0,027 | 6 642 € | −280 € | 53,0 % | 77,2 % | 100 % |
| +0,072 | 17 150 € | +596 € | 33,3 % | 13,9 % | 100 % |
| +0,136 | 31 771 € | +1 814 € | 26,5 % | 1,3 % | 100 % |

## Lo que dicen estas tablas

**1 · El rango realista es 150-300 € al mes.** De 10.000 €, si la ventaja
medida es real.

**2 · Los 750 € no salen de 10.000 € sin apostar.** Al 2 % el centro da 596 €
al mes con una caída máxima del **33 %**, y el escenario malo del intervalo
pierde 280 € al mes.

**3 · Esto y el fondeo son incompatibles.** Al 1 % de riesgo, el **97,2 %** de
los años tocan una caída del 10 % en algún momento. Con las reglas de una
cuenta fondeada te echan aunque acabes el año en verde. No porque la estrategia
sea mala: porque una caída del 10 % es **normal** aquí, y allí es la muerte.

**4 · El 0,5 % es lo único que sobrevive entero**: 144 €/mes, caída del 9,2 %,
y un año malo de cada diez.

## La letra pequeña que no se puede saltar

La fila de arriba de cada tabla —la que pierde dinero— **es tan compatible con
lo medido como la del centro**. El intervalo incluye el cero. Estas tablas
dicen lo que pasaría *si* la ventaja fuese real, y eso no está demostrado.

## Lo que sí queda claro

| objetivo | lo que hace falta |
|---|---|
| 150 €/mes | 10.000 € al 0,5 % |
| 300 €/mes | 10.000 € al 1 %, con caídas del 18 % |
| **750 €/mes** | **~50.000 € al 1 %**, o 10.000 € apostando |

El número que bloquea el objetivo de 750 €/mes no es la estrategia. Es el
capital.
