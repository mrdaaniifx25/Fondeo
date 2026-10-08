# Pre-registro · el hallazgo de sesiones, donde el coste no es excusa

Escrito y subido ANTES de medir. 21/09/2026.

## De dónde sale

El usuario insiste, con razón, en las sesiones. Están medidas —**34 scripts**—
y de todo aquello sobrevivió **una** cosa, que es suya:

> `RESULTADOS_asia_contexto.md`: barrido del rango de Asia en Londres, filtrado
> por que **M15 y H1 vayan a favor**. Diferencia **+0,916 de suma diaria con
> z +9,92**, confirmada en la muestra de 2026 que no se había tocado.

Es el hallazgo más firme de dos meses. Y no paga, por el motivo de siempre:

```
ventaja bruta   +0,085 R
coste 1,43 p sobre un riesgo mediano de 7,7 p   =  18,6 % del riesgo
                                                   ──────────────────
neta                                               ~0    (22-32 €/mes)
```

`RESULTADOS_asia_ancho.md` ensanchó el stop y lo llevó de claramente negativo a
aproximadamente cero. Ahí se quedó.

## El agujero que queda, y es real

Ese filtro —el hallazgo firme— **sólo se ha medido en EURUSD**. La réplica en
oro y DAX (`asia_limpia.py`) probó **otro** filtro distinto, el de «vuelta
limpia», y salió del revés. **El filtro de contexto de M15 y H1 nunca se ha
corrido fuera de EURUSD.**

Y eso importa ahora más que en agosto, porque las tres últimas pruebas
(`stop_minimo`, `barrido_rr`, `techo_filtro`) dicen lo mismo: **lo único que
mueve la neta es el cociente coste/riesgo.** En EURUSD ese cociente es 18,6 %.
En oro y DAX, con un stop de 1,5 ATR, sale alrededor del 5-8 %.

O sea: es el mismo patrón, en instrumentos donde **el coste ya no es la excusa**.

## Qué se mide

La regla de `asia_nivel.py`, portada tal cual:

- rango de **Asia** (00:00-08:00 Madrid), máximo y mínimo
- ventana de **Londres** (08:00-11:30 Madrid)
- el precio toca el nivel; gatillo **A** (cuerpo entero al otro lado) o **B**
  (cierra pasado el cuerpo de la última vela contraria)
- entrada al cierre de esa vela de M5, stop en el extremo de la anterior,
  objetivo **1:2**
- horizonte: hasta las **22:00** del mismo día
- **filtro de contexto**: las 4 últimas velas cerradas de **M15 y de H1** a favor

| eje | valores |
|---|---|
| instrumento | **EURUSD** (control) · **oro** · **DAX** |
| stop mínimo | **0** · **0,5** · **1,0** · **1,5** · **2,0** × ATR de M15 |

EURUSD va como control: si no reproduce el +0,085 bruto conocido, el porte está
mal y no se lee nada de lo demás.

Métrica: **suma diaria**, no media (la corrección de `asia_ancho.md`), y R por
operación con su intervalo.

## Potencia, calculada antes

Oro y DAX tienen **3 años**, no seis. Con ~1.000 disparos y el filtro dejando
~70 %, quedan unos **700 por instrumento**. El error estándar de R por operación
es ≈ 1,3/√700 = **0,049**, o sea ±0,096 al 95 %.

**Una ventaja de +0,085 no se distingue del cero con esa muestra.** Se dice
ahora: esta prueba puede confirmar una ventaja grande, y no puede descartar una
pequeña. Lo que sí hace es medir la **neta**, que es lo que se cobra.

## El sesgo de selección

15 celdas (3 instrumentos × 5 anchos). El mejor de 15 sale 1,74 errores
estándar por encima de la verdad: con ee 0,049, eso son **+0,085** de regalo.

**Cualquier celda por debajo de +0,085 de neta no es un hallazgo.**

## Criterio

1. El control de EURUSD reproduce la bruta conocida (+0,06 a +0,11), **y**
2. oro **y** DAX dan neta > 0 con el IC95 sin tocar el cero, **y**
3. por encima de +0,085, **y**
4. el mismo signo en los dos instrumentos nuevos, no uno sí y otro no.

## Predicción

- El control de EURUSD reproducirá: bruta entre +0,06 y +0,11.
- **Oro y DAX darán bruta positiva pero más pequeña**, entre +0,02 y +0,06,
  porque el +0,085 de EURUSD lleva dentro la selección de haberlo encontrado ahí.
- La neta subirá con el stop mínimo en los dos, y **cruzará el cero** en oro
  hacia 1,0-1,5 ATR, porque su coste relativo es la mitad.
- **Ningún intervalo quedará limpio del cero**, por la potencia calculada arriba.
- Y por tanto el criterio **no se cumplirá**: quedará otra vez «positivo y sin
  resolver». Si sale así, la conclusión no es «hay que seguir probando»: es que
  esta familia entera vive pegada al coste y sólo se decide con más años.

Van nueve predicciones con errores. Ésta también puede fallar.
