# Formulario · describir una estrategia para que yo la programe y la mida

Rellena lo que esté entre `<< >>` y bórralo todo lo demás si quieres. Pégamelo
tal cual en el chat.

**No hace falta que me mandes datos.** Ya tengo EURUSD M1 de 2020-01 a 2026-07
(2.397.463 minutos), y también GBPUSD, USDJPY, XAUUSD, US100, US500 y GER40.

**Si un campo no lo sabes, escribe `NO SÉ`.** No lo rellenes a ojo: prefiero
preguntarte a inventármelo, porque lo que me invente se convierte en el
resultado.

---

## 0 · CÓMO QUIERO QUE TRATES ESTO

- Cada regla es literal. Si algo no está escrito, NO existe: no añadas
  filtros, confirmaciones ni gestión que no aparezcan aquí.
- Si detectas ambigüedad o contradicción, **pregúntame antes de programar**.
- No estimes ni aproximes ningún número. Todo sale del script ejecutado.
- Antes de darme resultados, pásale los controles de la sección 9.

---

## 1 · QUÉ ES

- Nombre: `<< como quieras llamarla >>`
- De dónde sale: `<< vídeo / grupo / StrategyQuant / idea mía / ... >>`
- Si viene de un generador automático (StrategyQuant, EA Studio...), **dilo**:
  cambia radicalmente cómo hay que validarla.

## 2 · MERCADO

- Instrumento: `<< EURUSD >>`
- Temporalidad de la lógica: `<< M15 / H1 / H4 / D1 >>`
- Dirección: `<< solo compras / solo ventas / las dos >>`
- Horario en que se aceptan señales: `<< de 08:00 a 17:00 / todo el día >>`
  y **en qué huso**: `<< hora del servidor MT5 / Madrid / Nueva York >>`
- Días de la semana excluidos: `<< ninguno / viernes tarde / ... >>`
- Posiciones simultáneas máximas: `<< 1 >>`
- Con una posición abierta, ¿se siguen generando señales? `<< no >>`

## 3 · ENTRADA

**Filtro previo** (la condición que permite operar; si no hay, escribe NINGUNO)
- Indicador y parámetros: `<< EMA 200 / GannHiLo 5 / ninguno >>`
- Condición exacta: `<< el cierre está por encima de la EMA >>`
- **¿En qué vela se evalúa?** `<< la ANTERIOR ya cerrada / la actual en curso >>`
  *(este campo es donde nacen la mitad de los backtests falsos: contestarlo
  mal hace que el backtest vea el futuro)*

**Disparo**
- Qué lo activa: `<< rotura del máximo de las últimas N velas / cruce / patrón >>`
- Tipo de orden: `<< a mercado / limitada / stop >>`
- Nivel exacto de la orden: `<< el máximo de las últimas 51 velas cerradas >>`
- Validez de la orden pendiente: `<< 10 velas / hasta fin de día / no caduca >>`
- Si no se ejecuta, ¿se recalcula el nivel o se abandona? `<< se recalcula >>`

## 4 · SALIDA

- Stop loss: `<< 1 x ATR(95) / N pips fijos / bajo el mínimo de la vela X >>`
  - se calcula en: `<< el momento de la entrada >>` y ¿se mueve después? `<< no >>`
- Take profit: `<< no hay / 2 x el riesgo / nivel fijo >>`
- Salida por tiempo: `<< a las 5 velas / al cierre del día / no hay >>`
- Trailing stop: `<< no hay >>`
- Break-even: `<< no hay >>`
- Cierres parciales: `<< no hay >>`
- Salida por señal contraria: `<< no hay >>`
- **Si en la misma vela se tocan stop y objetivo, ¿qué mando?**
  `<< resuélvelo bajando a M1 / asume lo peor (el stop) >>`

## 5 · RIESGO Y TAMAÑO

- Capital inicial del backtest: `<< 100.000 € >>`
- Riesgo por operación: `<< 1 % del capital del momento >>`
- ¿El tamaño sale de la distancia al stop? `<< sí >>`
- ¿Se compone (el 1 % es del capital actual) o es fijo sobre el inicial?
  `<< se compone >>`

## 6 · COSTES REALES DE TU CUENTA

*Estos tres números deciden si la estrategia vive o muere. Míralos en tu MT5,
no los estimes.*

- Spread medio: `<< 1,0 pips >>` — medido a `<< qué horas >>`
- Comisión: `<< 5 €/lote ida y vuelta >>`
- Swap: `<< largos X, cortos Y, por lote y noche >>`
- ¿Aplico el spread en la entrada y en la salida? `<< sí >>`

*(De EURUSD en tu cuenta de FundingPips ya tengo medido: spread 0,7-1,0 pips
y comisión 5 €/lote = 1,28-1,58 pips totales. Si sigue igual, escribe
`LOS QUE YA TIENES`.)*

## 7 · PERIODO

- Periodo a medir: `<< todo lo que tengas / 2022-2026 >>`
- ¿Sabes en qué periodo se creó u optimizó la estrategia? `<< no lo sé >>`
  *(si lo sabes, dímelo: solo lo posterior es prueba de verdad)*

## 8 · QUÉ QUIERO QUE ME DEVUELVAS

- Número de operaciones, retorno total, CAGR, acierto, profit factor, payoff,
  drawdown máximo, racha máxima de pérdidas, desglose por año.
- El listado de operaciones en CSV.
- Gráficos: curva de capital, drawdown, distribución de resultados.
- El script completo, para que pueda cambiar los parámetros yo.

## 9 · LOS CONTROLES · no me des el resultado sin esto

*Esta sección es lo que el prompt del vídeo no tiene, y es lo que separa un
backtest de un espejismo. Marca los que quieres (recomendado: todos).*

- [ ] **Entradas al azar** con la misma geometría y los mismos costes.
      Si el azar gana lo mismo, la señal no aporta nada.
- [ ] **Vecindario de parámetros**: mover cada número arriba y abajo.
      Si solo funciona la combinación exacta, es sobreajuste.
- [ ] **Nulo**: la misma estrategia sobre datos barajados por bloques.
      Si también gana ahí, el fallo está en el código.
- [ ] **Comprar y mantener** como vara de medir.
- [ ] **Otros instrumentos** con las mismas reglas.
- [ ] **Fuera de muestra**: ajustar en la primera mitad, comprobar en la segunda.
- [ ] **Sensibilidad al coste**: hasta qué spread sigue siendo rentable.
- [ ] **Curva de detección**: qué tamaño de ventaja habría podido ver este
      montaje, para saber qué significa un cero.

## 10 · TU CRITERIO DE ÉXITO, escrito ANTES de ver el resultado

`<< qué número tiene que dar para que la operes, y qué número para que la
descartes. Escríbelo ahora, no después. >>`

Ejemplo: *"la opero si el profit factor supera 1,15 con mi spread real y bate
a las entradas al azar; la descarto si el drawdown pasa del 20 % o si menos
de la mitad de los vecinos de parámetros son positivos."*
