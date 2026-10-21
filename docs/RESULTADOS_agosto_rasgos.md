# ¿Se puede ajustar un indicador a agosto?

`bt/agosto_rasgos.py`. Ejecutado el 28 de agosto de 2026.

## La pregunta

El usuario propone construir un indicador ajustado a cómo ejecutó en agosto,
partiendo de que «el patrón está ahí, tanto para bien como para mal».

## La prueba

Se miden 15 características en el momento exacto de cada entrada, sobre las 15
operaciones de agosto que tienen datos M1 (9 TP, 6 SL): hora, riesgo, distancia
al nivel, lado, alto o mínimo, dirección de H1, dirección de M15, toques previos
al nivel, cierres previos fuera, cuerpo, rango y mecha de la vela de entrada,
posición de la entrada dentro de la vela, día de la semana y ATR.

Luego se busca cuánto acierto alcanza cada una con un solo umbral, y se compara
contra lo que se consigue **barajando los resultados al azar**.

```
  característica   mejor acierto con un umbral
  hora                                    87 %
  riesgo                                  80 %
  dist                                    80 %
  lado                                    80 %
  alto / dirH1 / toques / mecha / pos / atr   73 %
  fuera / cuerpo / rango                  67 %
  dirM15 / dsem                           60 %

  (decir "TP" siempre ya acierta el 60 %)
```

**Permutación, 2.000 barajadas:** con resultados al azar, el mejor rasgo llega
de media al **82 %**, y alcanza o supera el 87 % observado en el **34 %** de las
barajadas.

O sea: **p = 0,34**. El 87 % no significa nada.

Con reglas de dos condiciones no existe ningún separador perfecto de sus 15
operaciones — pero con etiquetas aleatorias sí aparece uno el **20 %** de las
veces. La herramienta encuentra patrones perfectos en puro ruido una de cada
cinco veces.

## Conclusión

**No hay ningún rasgo medible en el momento de la entrada que explique cuáles de
sus operaciones fueron TP y cuáles SL.** Ni la hora, ni el riesgo, ni la
distancia al nivel, ni el contexto de H1, ni la forma de la vela.

Ajustar un indicador a esas 15 operaciones produciría una regla que describe el
ruido de agosto y no sobrevive a septiembre.

Esto no contradice nada de lo anterior. El filtro de contexto separa el 34,9 %
del 21,2 % **sobre 2.080 operaciones**; a nivel individual, en un 1:2, el
resultado de cada operación es esencialmente impredecible por construcción. Lo
que una estrategia controla es la tasa sobre muchas operaciones, no cuál gana.

## Lo que sí tiene sentido construir

Un indicador que **muestre**, sin ajustar nada:

1. El alto y el mínimo de Asia.
2. La dirección de H1 y M15, con estado «a favor / en contra». Único filtro
   validado (z +9,92).
3. El disparo del gatillo: envolvente o cierre con cuerpo fuera del nivel.
4. El stop propuesto y el objetivo a 2R.
5. **El coste como porcentaje del riesgo**, en rojo si el stop es demasiado
   apretado.
6. El contador de disparos del día — la segunda operación de un día rinde
   −0,363 y la tercera −0,472.

Cada elemento sale de un resultado preregistrado o de su propia descripción
escrita. Ninguno está ajustado a sus 24 operaciones.
