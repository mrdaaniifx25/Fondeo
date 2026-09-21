# Pre-registro · el techo de un filtro invisible

Escrito y subido ANTES de medir. 21/09/2026.

## La objeción del usuario, que es correcta

*«Enseña payouts, y en sus vídeos dice algo que no se ve en la imagen y no
tenemos en cuenta.»*

Tiene razón en la segunda parte. Todo lo medido hasta ahora mecaniza lo que él
**dice**. Si además aplica un filtro que no verbaliza —una condición que ve en
la pantalla y no nombra— mis 33,4 % de acierto miden la regla sin ese filtro.

Esta prueba no intenta adivinar cuál es ese filtro. Intenta **acotar cuánto
puede valer, como máximo, cualquier filtro de ese tipo**.

## El hueco que habría que tapar

De su pantalla, verificado en tres operaciones (`VERIFICACION_benjamin_real.md`):

```
riesgo 5,9 p · coste 1,43 p · coste/riesgo 24,2 % · R:R 2,0
umbral de empate  41,4 %
acierto de azar   33,3 %
                  ───────
el filtro oculto tiene que valer  +8,1 puntos de acierto
```

No basta con que el filtro ayude. Tiene que valer **más de ocho puntos**, y eso
sólo para no perder dinero.

## Qué se mide

Base: la celda **verificada** de `bt/benjamin_regla.py` — M2, niveles de H1,
sus horas — **29.959 operaciones**, 5,6 años, acierto 33,4 %.

Para cada operación se calculan **14 variables observables en el momento de
entrar**, sin mirar ni un minuto al futuro:

| | |
|---|---|
| 1 | hora de Madrid |
| 2 | día de la semana |
| 3 | ATR de M2 al entrar |
| 4 | cuánto sobrepasó el nivel el barrido, en ATR |
| 5 | tamaño del stop en pips |
| 6 | stop / ATR |
| 7 | antigüedad del nivel, en horas |
| 8 | veces que se había tocado ese nivel antes |
| 9 | velas entre el barrido y el disparo |
| 10 | compra o venta |
| 11 | distancia al máximo/mínimo del día previo, en ATR |
| 12 | recorrido del día hasta ese momento / ATR diario |
| 13 | precio menos EMA 50 de M15, en ATR |
| 14 | cuerpo / rango de la vela de disparo |

**Prueba A · el techo de una regla simple.** Para cada variable se parte la
muestra en deciles y se publica el **mejor decil**, elegido con el resultado ya
visto. Es deliberadamente tramposo: si ni siquiera haciendo trampa se llega al
umbral, ninguna regla honesta de esa familia llega.

**Prueba B · el techo de una combinación.** Un modelo de árboles (gradient
boosting) sobre las 14 variables a la vez, con predicción **fuera de muestra**
por validación cruzada de 5 pliegues, ordenando por probabilidad predicha. Esto
busca combinaciones que un humano podría estar viendo sin saber nombrarlas.

## El sesgo de selección, calculado antes

14 variables × 10 deciles = **140 casillas**. Bajo la hipótesis de que todas
miden lo mismo, la mejor de 140 sale **2,63 errores estándar** por encima de la
verdad (p95: 3,38). Con n≈3.000 por decil el error estándar es 0,86 puntos:

**el procedimiento regala +2,3 puntos, y +2,9 una de cada veinte veces.**

Hace falta **+8,1**. El margen es cómodo: el ruido no puede fabricar ocho puntos.

## Criterio

- Si **ningún** decil y **ningún** decil del modelo llega al umbral de su
  celda, queda acotado: **ningún filtro basado en el gráfico salva su
  geometría**, se vea o no se vea en el vídeo.
- Si alguno pasa el umbral por más de +2,9 puntos, hay algo que perseguir y se
  vuelve a medir partido en dos mitades.

## Lo que esta prueba NO puede descartar

Información que **no está en el precio**: noticias, calendario macro, flujo de
órdenes, o que él simplemente no opere lo que enseña. Eso queda fuera y se dice
aquí para no venderlo luego como más de lo que es.

## Predicción

- **Ningún decil llegará al umbral.** Espero el mejor entre 36 % y 38 %.
- La variable con más recorrido será **el tamaño del stop** (5), pero por el
  motivo conocido: subir el stop baja el coste y baja el umbral, no sube el
  acierto.
- El modelo fuera de muestra dará un decil superior **por debajo de 37 %** y un
  AUC entre 0,50 y 0,53.
- Y por tanto la conclusión será que el hueco de +8,1 puntos **no lo tapa nada
  que esté en el gráfico**.

Van nueve predicciones con errores. Ésta también puede fallar.
