# ESTRATEGIA EUR/USD — LIQUIDEZ DE SESIONES · VERSIÓN PARA BACKTEST

Especificación entregada por el usuario el **22/09/2026**, reproducida íntegra y
sin modificar. Es el pre-registro: cumple su propio artículo 17.

Resultados en `docs/RESULTADOS_liquidez_sesiones_v2.md`. Decisiones de
implementación en `docs/PREREGISTRO_liquidez_sesiones_v2.md`.

**OBJETIVO** · Validar una estrategia mecánica de EUR/USD basada exclusivamente
en la toma de liquidez de máximos y mínimos de sesiones anteriores, con TP fijo
de 1:2.

**1 · INSTRUMENTO Y HORARIOS.** EUR/USD. Ejecución M5. Contexto H4 y H1. No usar
M15. No mantener operaciones overnight. Ventanas (hora España): Londres
09:00-11:00, Nueva York 14:00-16:30. Fuera de ellas, no operar.

**2 · NIVELES DE LIQUIDEZ.** Sólo PDH, PDL (máximo y mínimo del día anterior) y
PSH, PSL (máximo y mínimo de la sesión anterior). Para Londres la sesión
anterior es Asia; para Nueva York, Londres. Si un nivel de sesión coincide o
queda muy próximo a PDH/PDL, es una confluencia del mismo nivel.

**3 · SWEEP.** El precio alcanza o supera un máximo/mínimo válido, toma
liquidez con mecha o cuerpo, y la vela **cierra de nuevo dentro** del nivel. Si
cierra con el cuerpo claramente fuera es un RUN y no se opera en contra. La
señal sólo existe tras el cierre de la vela; nunca anticipar.

**4 · CONTEXTO H4.** Debe existir un Sweep de H4 coherente: en corto, H4 barre
ese máximo y cierra por debajo; en largo, barre el mínimo y cierra por encima.
Si H4 muestra RUN, no hay operación.

**5 · CONFIRMACIÓN H1.** H1 debe barrer un máximo (corto) o mínimo (largo)
relevante y cerrar de vuelta dentro. El Sweep de H1 debe producirse dentro de la
ventana operativa. Si H1 y H4 están desalineados, no hay operación.

**6 · GATILLO M5.** Vela envolvente: bajista en cortos, alcista en largos, cuyo
cuerpo cubre completamente el cuerpo de la última vela contraria.

**7 · ENTRADA.** Tras el cierre de la envolvente. Secuencia obligatoria:
nivel → sweep H4 → sweep H1 → envolvente M5 → entrada. Si falta un paso, no hay
operación.

**8 · STOP LOSS.** Detrás del extremo exacto del Sweep que invalida la
operación, más el spread del momento y un margen de seguridad fijo
parametrizable.

**9 · TAKE PROFIT.** Fijo 1:2. No mover el SL, ni break even, ni parciales, ni
trailing, ni cierre manual, ni modificar el TP. La operación termina sólo en SL
(−1R) o TP (+2R).

**10 · DIRECCIÓN.** Sin bias previo: la dirección la fija el Sweep.

**11 · MÁXIMO DE OPERACIONES.** Una por setup. No repetir sobre el mismo Sweep
tras ser invalidado.

**12 · PÉRDIDA DIARIA.** Tras una pérdida completa de −1R, se termina el día.

**13 · CONDICIONES DE NO-TRADE.** No operar si no se ha tocado PDH/PDL/PSH/PSL;
si el precio sólo se aproxima; si hay RUN; si H4 o H1 no confirman o están
desalineados; si la vela correspondiente no ha cerrado; si no hay envolvente M5
o no es clara; fuera de Londres o Nueva York; si el setup ya fue invalidado; o
si se alcanzó la pérdida diaria máxima.

**14 · REGLA MECÁNICA COMPLETA.** LARGO: PDL/PSL alcanzado → Sweep del mínimo →
H4 confirma → H1 confirma → envolvente alcista M5 → BUY → SL bajo el extremo del
Sweep → TP 2R. CORTO: simétrico.

**15 · DATOS POR OPERACIÓN.** Fecha, hora, sesión, dirección, nivel atacado,
sesión barrida, entrada, SL, TP, distancias en pips, resultado, duración, MFE,
MAE, spread, resultado tras costes.

**16 · MÉTRICAS.** Total, win rate, loss rate, R total, profit factor,
esperanza, drawdown máximo en R, rachas máximas, y desglose por sesión,
dirección, nivel, sesión barrida, confluencia, mes y año.

**17 · VALIDACIÓN.** No modificar las reglas tras ver los resultados de una
operación concreta. Primero ejecutar, después analizar. Cualquier modificación
posterior debe probarse sobre un periodo distinto o fuera de muestra.
