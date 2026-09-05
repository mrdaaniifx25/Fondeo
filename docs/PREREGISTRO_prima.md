# Preregistro · dimensionar la prima de riesgo contra las barreras del reto

Sellado ANTES de medir. Un solo pase. Código en `bt/prima.py`.

## Qué se prueba, y por qué es distinto de todo lo anterior

Todo lo medido en dos meses buscaba **una señal**: cuándo entrar. Ninguna
sobrevivió. La única ventaja que sí sobrevive (`docs/RESULTADOS_anomalias.md`)
no es una señal: es que la bolsa sube, **+0,070 % al día, z +2,93 y +2,04 en
dos tramos independientes**.

Nunca se ha probado lo obvio: **comprar y sostener, con el apalancamiento
ajustado a las barreras del reto**. Sin stop, sin entrada, sin criterio.

Por el teorema del muestreo opcional, si el precio fuera una martingala
P(pasar) estaría clavada en `10/(8+10) x 10/(5+10) = 37,0 %` haga uno lo que
haga. **La única forma de superar ese 37 % es que exista deriva real.** Este
experimento es, por tanto, también una prueba directa de si la deriva es real.

## El montaje

Instrumento US100. Reglas de FundingPips: fase 1 +8 %, fase 2 +5 %, pérdida
diaria máxima 5 %, pérdida total máxima 10 %, 60 días por fase, mínimo 3 días.
El límite diario se evalúa sobre la **equity flotante**, que es lo estricto.

Compra el primer día, mantiene, reequilibra a apalancamiento constante `L`
cada cierre. Se prueba `L` de 0,5 a 5,0.

Financiación: `(tipo + margen)/360` diario sobre el nocional. Se prueba al
3 %, 6 % y 9 % anual. El 6 % es el caso base.

Tres formas de generar caminos, y las tres se publican:

    A · ventanas históricas solapadas   todas las fechas de inicio reales
    B · bootstrap por bloques de 20 días   conserva los mercados bajistas
    C · bootstrap iid día a día            los destruye

Ajuste en **2020-2023**, comprobación en **2024-2026**.

## Las cinco predicciones firmadas

1. **Existe un `L` que da P(pasar la fase 1) > 55,6 %**, el techo de ventaja
   cero. Predigo que SÍ, porque la deriva es real.

2. **El `L` óptimo será ≤ 2,0**, porque el límite diario del 5 % es lo que
   ata. Con `L = 3` basta un día del índice de -1,7 % para quedar fuera, y
   eso pasa demasiado.

3. **P(pasar las dos fases) superará el 37,0 % de ventaja cero, y llegará al
   45 % o más** con el `L` óptimo y financiación al 6 %.

4. **Fuera de muestra (2024-2026) saldrá peor que en el ajuste (2020-2023)**,
   por el decaimiento ya medido de la deriva intradía.

5. **El bootstrap por bloques dará al menos 5 puntos porcentuales MENOS que
   el iid.** Si no, es que el iid está escondiendo los mercados bajistas y
   todos los bootstrap previos del proyecto son optimistas.

## Lo que invalidaría el resultado

Si `P(pasar)` no supera el 37,0 % con ningún `L`, entonces la deriva no
alcanza para nada operativo y **se acabó el proyecto**: no hay ventaja
explotable en estos datos, ni buscada ni regalada. Eso hay que decírselo tal
cual.
