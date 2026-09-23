# Pre-registro · la regla de Benjamín, completa

Escrito y subido ANTES de medir. 21/09/2026.

## Por qué ésta sí

Es la primera descripción del proyecto que trae **las tres cifras que faltan
siempre**: dónde va el stop, cuál es el objetivo y en qué horario. Transcripción
del vídeo «de $120 a $1.000».

## La regla, tal cual la dice

1. **EURUSD**, sólo.
2. Marcar un **máximo o mínimo en H1 o H4**.
3. Esperar a que el precio **lo liquide** (lo supere). Máximo barrido → ventas.
4. Sólo dentro de **Londres 09:00-11:00** o **Nueva York 14:00-16:30**, hora de
   Madrid.
5. Bajar a **M1-M5** (él usa **M2**) y buscar **impulso + imbalance**: tres
   velas en las que la primera y la tercera **no se tocan**.
6. Entrar ahí. **Stop: «te cubres en los máximos»** → por encima del extremo
   del barrido.
7. **Objetivo: ratio 1:2.**

## Cómo se mecaniza, fijado ahora

- **Niveles**: pivotes de H1 y H4 con 3 velas a cada lado, **usables sólo 3
  velas después de formarse**.
- **Barrido**: una vela de la temporalidad de entrada supera el nivel.
- **Imbalance**: en las velas k−2, k−1, k, que `low[k] > high[k−2]` (alcista) o
  `high[k] < low[k−2]` (bajista), a favor del giro. Máximo **30 velas** de
  espera desde el barrido.
- **Entrada**: al **cierre** de la vela k. La resolución empieza en el minuto
  siguiente.
- **Stop**: el extremo alcanzado durante el barrido, más el propio impulso.
- **Objetivo**: 2 × riesgo.
- **Una por nivel y día.**

## Las 8 celdas, declaradas

| eje | opciones |
|---|---|
| temporalidad de entrada | **M2** · **M5** |
| nivel | **H1** · **H4** |
| horario | **sólo sus dos ventanas** · **todo el día** (control) |

Se publican las ocho.

## Medición

Resolución en M1, **las dos barreras por toque**, empate = pérdida, horizonte
24 h, agotarlo = pérdida. Objetivo **por delante** del precio de entrada.
Coste **1,43 pips**.

Lo que se mira es el **exceso sobre el precio justo**, que para un 1:2 es
**33,3 %**. Y el umbral de rentabilidad con coste `c` sobre el riesgo es
`(1+c)/3`.

**Nulos** sobre la celda principal (M2, H1, sus horarios): lados barajados e
instantes al azar.

## Criterio

1. exceso > 0 con IC95 sin tocar el cero, **y**
2. neta > 0 con IC95 sin tocar el cero, **y**
3. sus horarios no peores que el control de todo el día.

Y para que su propio plan funcione hace falta además **neta ≥ +0,05 R**
(`docs/RESULTADOS_plan_viable.md`).

## Predicción

- **Acierto entre 30 y 40 %**, cerca del 33,3 % que da la geometría.
- **Riesgo mediano de 5 a 15 pips**, así que el coste pesará entre el **10 % y
  el 28 %** del riesgo.
- **Neta entre −0,10 y −0,30.** No cumple el criterio.
- El umbral que necesitaría: con un coste del 14 %, acertar el **38 %** sólo
  para empatar.
- Sus dos ventanas horarias: **sin diferencia clara** contra el control.

Van cinco predicciones mías con errores. Ésta también puede fallar.
