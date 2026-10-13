# ¿Es viable el plan del vídeo? ¿Y su estrategia?

Código `bt/benjamin.py` y `bt/plan_viable.py`. Pregunta del usuario: si el plan
que cuenta el vídeo (partir el capital en cuentas pequeñas y reinvertir) es
seguible, y si la estrategia que enseña lleva a esa escalabilidad.

## Son dos cosas distintas

El plan es un **multiplicador**. La estrategia es **lo que se multiplica**.
Así que la pregunta útil es: **qué ventaja hace falta para que el plan cruce**.

## La tabla que lo contesta

Dos años, empezando con 210 €. Drawdown **móvil** (el modelo estricto):

| ventaja por operación | riesgo | neto medio | % que gana | llega a 10.000 € |
|---|---|---|---|---|
| −0,05 | 0,5 % | −204 € | 0,0 % | 0,00 % |
| −0,05 | 1,0 % | −98 € | 3,7 % | 0,01 % |
| **0,00** | 0,5 % | **−46 €** | 7,7 % | **0,00 %** |
| 0,00 | 1,0 % | +1.294 € | 22,3 % | 3,7 % |
| **+0,05** | 0,5 % | **+3.423 €** | 50,5 % | 9,2 % |
| +0,05 | 1,0 % | +7.801 € | 47,5 % | 42,1 % |
| **+0,10** | 0,5 % | **+15.104 €** | **82,2 %** | **79,9 %** |
| +0,10 | 1,0 % | +23.846 € | 66,8 % | 66,8 % |
| +0,20 | 0,5 % | +54.931 € | 99,2 % | 99,2 % |

Con drawdown **fijo** (el modelo generoso) los números son mayores pero el
cruce está en el mismo sitio.

## Las tres conclusiones

**1 · El plan sí es viable, a partir de +0,05 R por operación.** Y por encima
de +0,10 es muy bueno: 8 de cada 10 llegan a los 10.000 €. La mecánica de
repartir el capital funciona, no es humo.

**2 · Pero es apalancamiento, no protección.** A −0,05 R lo pierdes todo con
casi total seguridad (0,0 % y 3,7 % de gente en positivo). El plan amplifica
en las dos direcciones. El vídeo sólo cuenta una.

**3 · Y el umbral real es más alto que +0,05**, porque mi modelo sigue siendo
generoso: a ventaja **cero** el 1 % de riesgo da +1.294 €, que es un trinquete
residual de mi simulación y no dinero real. Las prop de verdad añaden días
mínimos, reglas de consistencia y límites de retirada que no modelo.

## Y la estrategia del vídeo, concretamente

Lo que enseña es SMC: ineficiencias en H1/M30, cambio de estructura, **entrada
en M1**. Esa familia está medida en este repo varias veces
(`RESULTADOS_ob.md`, `RESULTADOS_sweep_choch.md`, `RESULTADOS_fvg.md`,
`RESULTADOS_barrido_sesion.md`) y sale **negativa**, siempre por el mismo
motivo: una entrada en M1 deja un stop de 3 a 8 pips, y ahí el coste se lleva
entre el **27 % y el 41 %** del riesgo.

Para cruzar el umbral del plan haría falta +0,05 **neto**. Esa familia está en
−0,2 o peor.

## Lo que tenemos nosotros, para comparar

Lo mejor medido en el proyecto es el CRT en marcos grandes:
**+0,02 a +0,06 R neto** (mediana entre anclajes), **con el cero dentro del
intervalo**.

O sea: **justo en el borde del umbral, y sin demostrar.**

## Resumen en una línea

El plan funciona si tienes una ventaja. Su estrategia no la da. La nuestra
podría estar en el límite y aún no está probada.
