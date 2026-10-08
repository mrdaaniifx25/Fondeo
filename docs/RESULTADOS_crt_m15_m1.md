# Resultados · CRT en M15 y en M5, con la entrada afinada en M1

Preregistrado en `docs/PREREGISTRO_crt_m15_m1.md`. Un solo pase, más la rejilla
de M5 añadida después porque su operativa real es M5 marcando y M1 ejecutando.

## El resultado en una línea

**90 celdas medidas** —3 instrumentos × 5 ejecuciones × 3 filtros horarios × 2
marcos—. **Las 90 dan R neta negativa.** Ninguna llega a z > +2,50. La mejor de
todas es **z = −10,7**.

No hace falta corrección de Bonferroni para nada: no hay ni un candidato.

## Su método exacto

Variante **D2**: la señal en M5, la entrada en M1 tras el cierre que confirma,
el stop pegado a las tres velas M1 cerradas, objetivo 1:2. Sesión de Londres,
2020-2026.

| | n | stop | coste | acierto | geometría | ventaja | pips/op | R neta | z |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 9.199 | 4,4 p | 33 % | 33,9 % | 33,3 % | +0,6 pp | +0,142 | −0,322 | −21,6 |
| GBPUSD | 9.219 | 5,7 p | 25 % | 35,0 % | 33,3 % | +1,7 pp | +0,281 | −0,214 | −14,4 |
| USDJPY | 9.283 | 5,1 p | 28 % | 32,9 % | 33,3 % | −0,4 pp | −0,068 | −0,322 | −21,9 |

Contra su propia geometría: EURUSD z **+1,22**, GBPUSD z **+3,46**, USDJPY z
**−0,82**. Uno de tres significativo, y en el instrumento que no opera. Eso es
la forma que tiene el ruido, no la que tiene una ventaja.

En EURUSD, sobre 9.199 operaciones, **el acierto está a 0,6 puntos de lo que da
una moneda cargada**. La ventaja bruta es de +0,142 pips por operación. El coste
es de 1,43. Muerta por un factor de diez.

## El hallazgo que sí es nuevo: esperar la confirmación en M1 cuesta dinero

Es la comparación limpia del preregistro. **A** entra a mercado en la apertura
de la Vela 3. **C** espera al primer M1 que cierra más allá del nivel. Mismo
stop, mismo objetivo, mismas señales: lo único que cambia es la entrada.

| | A · a mercado | C · espera al M1 | lo que cuesta esperar |
|---|---|---|---|
| M15 · EURUSD · Londres | +0,047 | −0,186 | **−0,233 pips** |
| M15 · GBPUSD · Londres | −0,040 | −0,209 | −0,169 |
| M15 · USDJPY · Londres | −0,122 | −0,277 | −0,155 |
| M5 · EURUSD · Londres | −0,008 | −0,065 | −0,057 |
| M5 · GBPUSD · Londres | +0,030 | −0,209 | −0,239 |
| M5 · USDJPY · Londres | −0,067 | −0,259 | −0,192 |

**Seis de seis en contra.** La vela que confirma se paga en precio de entrada, y
lo que devuelve en acierto no cubre lo que cobra. Entre 0,06 y 0,24 pips por
operación, cuando toda la ventaja del patrón vale menos que eso.

Esperar no es gratis. Es la conclusión más útil de este pase.

## Dónde me equivoqué

De las cinco predicciones firmadas, acerté la que decidía —ninguna llega a
+2,50— y fallé tres de las de mecanismo:

1. **«La bruta en R será mayor en D que en A, B y C.»** Falso. Casi siempre es
   **A** la más alta. El stop más estrecho de D multiplica la R, sí, pero la
   entrada llega tarde y se come más de lo que el multiplicador aporta.
2. **«La bruta en pips será parecida en las cuatro.»** Falso. C es
   sistemáticamente la peor, y por mucho.
3. **«El coste en A/B/C rondará el 10-15 %.»** Me quedé corto: sale entre el
   16 y el 42 %. Los stops de este patrón en M5 y M15 son más estrechos de lo
   que supuse.
4. El acierto sí superó su geometría de forma significativa en dos sitios:
   A en EURUSD M15 Londres (51,3 % contra 49,0 %, z +3,7) y D2 en GBPUSD M5
   (z +3,46). En ambos, la neta sigue siendo negativa: **hay algo de señal, y
   vale menos que el coste.**

## Dos fallos del motor, corregidos antes de leer nada

- `searchsorted` tardaba **170 ms por llamada** al comparar un `Timestamp` de
  pandas contra un array `datetime64`: numpy recorría los 2,4 M de elementos uno
  a uno. Vectorizado, el pase entero baja de 50 minutos a segundos.
- Con hueco de apertura al otro lado del extremo que fija el stop, el riesgo
  salía de una milésima de pip y la R se disparaba: USDJPY daba **z
  −47.774.440**. Un stop más estrecho que el propio buffer no es ejecutable, así
  que esas señales se descartan y se cuentan. Son entre 4 y 934 por celda sobre
  50.000-150.000, y los números apenas se mueven.

## El límite honesto de este pase

Las variantes C y D usan una confirmación **mecánica**: el primer M1 que cierra
más allá del nivel. La suya es discrecional —rechazo en el nivel, y después una
vela que cierra con cuerpo por encima de la última contraria—. **No son lo
mismo**, y este test no puede descartar que su lectura concreta sea mejor que el
sucedáneo mecánico.

Lo que mide esa diferencia es el simulador a ciegas, y los primeros 49 casos
dieron 29,2 % de acierto contra un 33,3 % geométrico.

## Reproducir

```
python3 bt/crt_m15_m1.py 15    # rejilla M15
python3 bt/crt_m15_m1.py 5     # rejilla M5
```

Salidas en `data/crt_m15_m1_salida.txt` y `data/crt_m5_m1_salida.txt`.
