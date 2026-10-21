# Pre-registro · lo más simple que se puede defender

Firmado **antes** de simular. Pregunta única:

> Para su cuenta FundingPips 10k de 2 fases, y suponiendo que la entrada **no
> tiene ventaja** (que es lo único que he podido demostrar en tres meses),
> ¿qué configuración de riesgo y de gestión del día maximiza la probabilidad
> de pasar las dos fases, y cuánto vale esa probabilidad?

## Lo que se mide

Montecarlo de la carrera completa: fase 1 +8 %, fase 2 +5 %, límite diario
−3 %, límite total −10 %. 40.000 cuentas, 300 días hábiles de tope.

Ejes:

```
  ventaja (esperanza en R, neta)   -0,05  -0,02  0,00  +0,02  +0,05  +0,10
  riesgo por operación             0,25 % 0,50 % 0,75 % 1,0 % 1,5 % 2,0 %
  operaciones/día (tope)           1  2  3  4
  regla de cierre de día           A sin regla
                                   B parar tras la primera pérdida
                                   C parar tras la primera ganancia
                                   D parar al tocar ±2R
  R:R                              1:2 fijo (su requisito)
  coste                            0,10 R por operación
```

## Lo que declaro antes

1. **A mayor riesgo, menos coste total pagado** (el coste en R es fijo y las
   operaciones necesarias caen con el cuadrado del riesgo). Así que sin límite
   diario, más riesgo sería siempre mejor.
2. **El límite diario del 3 % es lo que pone el techo.** Espero un óptimo
   interior: subir riesgo ayuda hasta que `n × riesgo` se acerca al 3 %, y
   entonces se desploma.
3. **Las reglas de cierre de día son neutras en esperanza** —no cambian la
   ventaja— **pero no en probabilidad de pasar**, porque recortan la varianza
   del día y por tanto las roturas del límite diario. Predicción: **B es la
   mejor de las cuatro**, y la diferencia es de varios puntos.
4. Con ventaja cero espero **P(pasar las dos) entre 25 % y 40 %** para la mejor
   celda, y **P(pasar fase 1) alrededor del 50 %**.

## Lo que sería un resultado útil

Una sola celda recomendada, con su número, y la frase honesta de qué significa
ese número. **No** una estrategia validada: eso ya se intentó y no existe.

## Lo que NO afirma este trabajo

Que la entrada funcione. La simulación supone explícitamente que **no**
funciona. Lo que se optimiza es la supervivencia dentro de las reglas del
examen, que es un problema de varianza, no de ventaja.
