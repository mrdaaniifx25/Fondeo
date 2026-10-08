# Preregistro · la familia "alta tasa de acierto / cola catastrófica"

Sellado ANTES de medir nada. Un solo pase. Código en `bt/alto_winrate.py`.

## Por qué este experimento y no otro

Los dos meses anteriores buscaron **una señal con ventaja**. La respuesta
está cerrada y documentada: la ventaja bruta que existe (SMC-71 M15 agrupado,
+0,166 R, z +4,90) es del tamaño del coste, y ninguna configuración concreta
sobrevive a la corrección por comparaciones múltiples.

Lo que sí está medido y es real (`docs/RESULTADOS_arbitraje_fondeo.md`) es que
quien retira de una prop firm **no opera mejor**: explota que su pérdida está
topada en la cuota. Y para eso usa deliberadamente estrategias de >90 % de
acierto con cola catastrófica, que en cuenta real son ruina.

**Esa familia nunca se ha medido en este proyecto.** Todo lo anterior usaba
R:R positivo. Este experimento la mide.

## La hipótesis que de verdad se juega

Para un paseo aleatorio sin deriva con barreras absorbentes en +a (objetivo)
y -b (drawdown), la probabilidad de tocar el objetivo primero es b/(a+b),
**independientemente de la geometría de cada operación**. Con objetivo 3.000 $
y drawdown 2.000 $ eso da 40 %, use uno TP:SL de 1:1 o de 1:30.

Si el teorema de la barrera manda, la estrategia de alto acierto NO sirve de
nada. Si sirve de algo, tiene que ser por las tres reglas que rompen el
paseo aleatorio limpio:

  1. **drawdown dinámico** (sigue al máximo de equity) — castiga curvas que
     oscilan, y la de alto acierto no oscila: sube en escalera
  2. **días mínimos de operativa** — exige ganancias repartidas
  3. **regla de consistencia** (ningún día puede ser más del X % del beneficio)
     — mata a la estrategia de un solo pelotazo

## Lo que se mide

Instrumentos: NASDAQ (`nsxusd_m1`) y SP500 (`spxusd_m1`), 2020-01 → 2026-07.
Sesión: cash de Nueva York, 09:30–15:55 NY. Sin overnight, plano al cierre.

Tres entradas, deliberadamente simples — este experimento NO busca señal,
mide geometría:

    A · CIEGA      compra a las 09:35 NY todos los días
    B · RETROCESO  compra en el primer retroceso de 0,15 x rango diario
                   desde la apertura de sesión, entre 09:30 y 12:00
    C · CONTROL    venta a las 09:35 NY todos los días

Doce geometrías por entrada: SL ∈ {0,25 · 0,50 · 1,00} x rango diario mediano,
y TP:SL ∈ {1:1 · 1:3 · 1:10 · 1:30}. Tasa de acierto geométrica esperada:
50 % · 75 % · 90,9 % · 96,8 %.

Coste asumido, ida y vuelta, en puntos del índice (futuro micro):

    MNQ (NASDAQ)   1,20 puntos   = comisión ~0,67 + horquilla ~0,50
    MES (SP500)    0,80 puntos   = comisión ~0,27 + horquilla ~0,50

Es una **asunción declarada**, no un dato suyo: no me ha pasado la tarifa de
su prop firm de futuros. Se publica sensibilidad a la mitad y al doble.

Evaluación simulada (asunción declarada, cuenta de 50K genérica):
objetivo +3.000 $, drawdown 2.000 $, mínimo 5 días, contratos dimensionados
para que el stop sea el 20 % del drawdown. Dos modos: estático y dinámico.
20.000 simulaciones por celda, remuestreo con reemplazo de las operaciones
reales de esa celda.

## Las cinco predicciones firmadas

1. **La tasa de acierto observada no batirá a la geométrica SL/(SL+TP) por más
   de 2 puntos porcentuales en ninguna celda de compra.** La deriva alcista
   medida (+0,09 R) es demasiado pequeña para mover estas geometrías.

2. **La esperanza neta por operación será negativa en al menos el 80 % de las
   celdas.** Coste sin ventaja.

3. **Con drawdown ESTÁTICO, P(pasar) será prácticamente igual en las celdas de
   alto acierto y en las de bajo acierto** — diferencia menor de 5 puntos
   porcentuales. El teorema de la barrera manda.

4. **Con drawdown DINÁMICO, las celdas de alto acierto batirán a las de bajo
   acierto por 5 puntos porcentuales o más.** Aquí es donde la familia gana
   su razón de existir.

5. **La regla de consistencia al 40 % matará más celdas de bajo acierto que de
   alto acierto**, con una diferencia de al menos 10 puntos porcentuales en
   la tasa de descalificación.

Si 3 y 4 salen las dos que no, la familia de alto acierto no tiene ninguna
justificación y hay que decírselo.

## Lo que este experimento NO puede contestar

No dice si la estrategia es rentable en cuenta real: por construcción no lo
es. Mide si es rentable **el boleto**, y a cambio de cuántos boletos.
