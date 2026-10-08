# Pre-registro · el PSH, solo, en oro y DAX

Escrito y subido ANTES de medir. 22/09/2026. Lo pide su propio §17: el
candidato se prueba fuera de muestra antes de darlo por bueno.

## De dónde sale el candidato, y lo poco que vale

`RESULTADOS_liquidez_sesiones_v2.md`. De los cuatro niveles de su spec, el
**PSH** (máximo de la sesión anterior, en cortos) fue el único con ventaja bruta
positiva:

```
  PSH   n 50   acierto 32,0 %   bruta +0,030   neta -0,156
```

**Hay que decir lo que esto es antes de medir nada más**: 50 operaciones, error
estándar de la bruta ≈ **0,18**, así que +0,030 significa ±0,36. Y era **el
mejor de cuatro casillas**, lo que por azar regala +0,19.

**El candidato no está por encima del ruido ni por asomo.** No se prueba porque
prometa: se prueba porque es lo único de su spec que no está en negativo, y
porque en oro y DAX el coste pesa mucho menos y ahí se vería mejor.

## Qué se mide

La misma regla de su spec, recortada a **PSH y sólo cortos**:

```
  máximo de la sesión anterior (Asia para Londres, Londres para NY)
  -> barrido en M5 con cierre de vuelta dentro
  -> envolvente bajista M5
  -> venta, SL sobre el extremo del barrido + spread + margen, TP 1:2
```

| | |
|---|---|
| instrumentos | **oro** y **DAX** (2023-2026). EURUSD va de referencia, no de prueba: es de donde salió el candidato |
| ventanas | Londres 09:00-11:00, Nueva York 14:00-16:30, hora de Madrid |
| sesiones | Asia 00:00-08:00, Londres 08:00-14:00 |
| coste | EURUSD 1,43 pips · oro 0,35 $ · DAX 1,6 puntos |
| spread en el SL | EURUSD 1,0 pip · oro 0,25 $ · DAX 1,0 punto |
| margen del SL | **0 · 0,33 · 0,66 · 1,0 × ATR(M5)**. El 0,33 reproduce exactamente el 1 pip usado en EURUSD |

### Las dos versiones, las dos declaradas ahora como principales

1. **CON la cadena H4+H1**, que es donde apareció el candidato.
2. **SIN la cadena**, porque en EURUSD se midió que la cadena **empeora** el
   resultado (22,2 % con ella, 27,1 % sin ella).

Se declaran las dos antes de mirar para que no pueda elegir la que salga mejor.

## Potencia, calculada antes

Oro y DAX tienen **3,6 años**, no 5,7, y PSH-cortos es la cuarta parte de la
regla. Con la cadena espero **menos de 30 operaciones por instrumento**.

**Si salen menos de 50, el resultado es «no se puede saber» y se dirá así**, no
se leerá el signo. Con n=50 el intervalo del acierto es ±13 puntos: no
distingue 25 % de 38 %.

La versión sin cadena debería dar 4-6 veces más, y es la que puede concluir algo.

## El sesgo de selección

2 instrumentos × 2 versiones × 4 márgenes = **16 celdas**. El mejor de 16 sale
1,77 errores estándar por encima de la verdad. No se declara una celda principal
porque la pregunta no es cuál es la mejor, sino **si el signo se repite fuera de
EURUSD**. Lo que se mira es la coherencia, no el máximo.

## Criterio

1. Bruta positiva en **oro y DAX a la vez**, en la misma versión, **y**
2. neta positiva en al menos uno con el IC95 sin tocar el cero, **y**
3. con n suficiente en el que cruce (≥ 50).

Si el signo sale positivo en uno y negativo en el otro, **no replica**, y eso
cierra el PSH.

## Predicción

- **Saldrán muy pocas operaciones con la cadena**: 15-30 por instrumento.
- **No replicará.** Espero bruta positiva en uno y negativa en el otro, o las
  dos cerca de cero con intervalos enormes.
- La versión sin cadena dará más muestra y saldrá **plana o ligeramente
  negativa** en los dos.
- El coste relativo será mucho más bajo que en EURUSD —alrededor del 5-8 % del
  riesgo frente al 16,7 %— y aun así **no bastará**, porque lo que falta no es
  coste, es ventaja.
- Conclusión probable: **el PSH queda cerrado** y con él la spec entera.

Van trece predicciones con errores. Ésta también puede fallar.
