# Auditoría estática — CRT MSS+FVG (Pine Script v6): 0 operaciones

> Revisión estática exhaustiva. **No se ha compilado ni ejecutado**: no hay acceso a
> TradingView desde aquí. Todo lo que sigue se deduce del código y de la semántica
> documentada de Pine v6. El apartado *Cómo confirmarlo en 5 segundos* te da los
> contadores para verificar cuál de los eslabones muere realmente.

## 0. Resumen ejecutivo

El síntoma («los rombos de sweep sí, el MSS nunca») no lo produce **un** fallo, sino
**dos fallos independientes**, y ambos son del tipo que pediste buscar: manejo de
series temporales sobre variables `var`.

| # | Fallo | Efecto |
|---|-------|--------|
| **F1** | `sweepHiPx` / `sweepLoPx` se ponen a `na` en el reset de rango HTF, pero se leen mucho después, al calcular el SL | **cero operaciones garantizado** por propagación silenciosa de `na` |
| **F2** | El flanco del sweep se detecta con `sweptHi[1]`, valor de *cierre de la vela anterior*, es decir **anterior al reset** que ocurre en esa misma vela | se traga el sweep de la vela de apertura del rango, que es el caso más frecuente |
| **F3** | `mPend` es una única ranura global sin reset por rango: bloquea hasta 300 velas (**25 h en M5**) | ~1 setup/día como máximo |
| **F4** | La kill zone se aplica al **instante del barrido**, no a la confirmación | como `sweptHi` se enclava todo el rango, sólo hay **una vela candidata por rango** y tiene que caer justo dentro de la KZ |

**F2+F3+F4 explican que el MSS no aparezca nunca. F1 explica que, aunque lo
arreglases, siguieras con 0 operaciones.** Por eso el problema «persiste» después
de tu primera corrección: esa corrección era necesaria pero tocaba otra cosa.

Sobre tu corrección previa: **era correcta**. En Pine v5/v6 las funciones `ta.*`
con estado interno dejaron de evaluarse implícitamente en cada vela cuando están
dentro de un bloque condicional, así que sacar `ta.lowest()`/`ta.highest()` al
ámbito global era obligatorio. Simplemente no era *este* fallo.

---

## 1. Por qué el MSS no puede ser el eslabón que falla por sí solo

Conviene fijar esto primero, porque acota la búsqueda.

Si `mPend` llegara a armarse, el MSS se confirmaría casi con certeza:

```pine
mCounterLv := mssHigh[1]          // sweepDown -> mDir = 1
...
if mDir == 1 and close > mCounterLv
```

`mssHigh[1]` es el máximo de 20 velas del gráfico (100 min en M5), y el setup vive
300 velas (25 h en M5). En EURUSD, que un cierre supere en 25 horas un nivel que
estaba 20–30 pips por encima hace 100 minutos es prácticamente seguro.

**Conclusión:** si el MSS no aparece *nunca*, es que `mPend` **no se arma nunca**.
Y como el rombo sí se dibuja, la condición `sweepUp and not sweptHi[1]` sí se
cumple. Luego lo que falla está en `baseGate` y en el flanco. Eso es F2/F3/F4.

---

## 2. F1 — `var` leída después de haber sido borrada (cero garantizado)

```pine
if newHTF
    sweptHi   := false
    sweptLo   := false
    sweepHiPx := na        // <-- se borra cada 4 h
    sweepLoPx := na        // <--
    dirDone   := false
```

y **mucho más abajo**, en la entrada:

```pine
slPx = mDir == 1 ? math.min(sweepLoPx, mFvgFar) - slBufferATR * htfATR
                 : math.max(sweepHiPx, mFvgFar) + slBufferATR * htfATR
riskPx  = math.abs(entryPx - slPx)
if riskPx > 0 and riskPips >= minRiskPips
```

El setup nace en el barrido y muere hasta 300 velas después. El rango H4 se
renueva **cada 4 horas** (48 velas en M5, 16 en M15). Cualquier setup que cruce
un cierre de H4 —que es la inmensa mayoría, porque entre el sweep y el toque del
FVG median como mínimo varias velas M15— llega a la entrada con
`sweepLoPx = na`.

La cadena de `na` es silenciosa y ésta es la parte importante:

- `math.min(na, mFvgFar)` → `na`
- `slPx` → `na`
- `riskPx = math.abs(entryPx - na)` → `na`
- **`riskPx > 0` → `na`, y `if na` se comporta como `false`**

No hay error, no hay aviso, no hay orden. El `strategy.entry` es inalcanzable.
**Éste es el cero garantizado de operaciones**, independiente de todo lo demás.

**Corrección:** copiar el extremo del barrido (y el ATR HTF) *dentro* del estado
del setup en el momento de armar, para que el reset del rango no pueda tocarlos:

```pine
sSweepPx := high      // copia propia del setup
sATR     := htfATR    // idem
```

---

## 3. F2 — `sweptHi[1]` es el estado *anterior al reset de la misma vela*

Éste es exactamente el patrón de series temporales que buscabas.

Orden de ejecución dentro de una misma vela:

```pine
if newHTF
    sweptHi := false          // (1) reset, EN ESTA VELA
...
if sweepUp
    if not sweptHi
        sweptHi := true       // (2) latch, EN ESTA VELA
...
if sweepUp and not sweptHi[1] // (3) lee el CIERRE DE LA VELA ANTERIOR
```

`sweptHi[1]` **no** es «el estado antes del latch (2)»: es el estado al cierre de
la vela anterior, o sea **antes del reset (1)**. En la vela de apertura de un
rango H4 nuevo, `sweptHi[1]` todavía arrastra el `true` del rango anterior.

Consecuencia: **si el primer barrido de un rango ocurre en la propia vela de
apertura del rango —el caso más habitual, porque el precio suele venir con
inercia y supera el extremo de la vela H4 recién cerrada en los primeros
minutos—, ni se arma el setup ni se dibuja el rombo.** Y en la vela siguiente
`sweptHi[1]` ya vale `true`, así que tampoco.

Ojo: `plotshape()` arrastra el mismo defecto, así que los rombos que ves son
sólo el subconjunto de barridos que ocurren *después* de la vela de apertura.
Parecen «correctos» porque los que faltan no se ven.

**Corrección:** calcular el flanco leyendo el estado vivo, después del reset y
antes del latch:

```pine
firstSweepUp = sweepUp   and not sweptHi   // no sweptHi[1]
firstSweepDn = sweepDown and not sweptLo
```

---

## 4. F3 — `mPend` bloquea hasta 300 velas y no se resetea por rango

```pine
if not mPend and baseGate     // <-- mPend true bloquea TODO
...
if mPend
    mBarCount := mBarCount + 1
    if mBarCount > 300
        mPend := false
```

`mPend` es una ranura global única. Si el MSS no confirma y el FVG no aparece,
el setup ocupa la ranura **300 velas del gráfico = 25 h en M5, 75 h en M15**, y
el bloque `if newHTF` **no lo resetea** (resetea `sweptHi`, `sweepHiPx`,
`dirDone`… pero no `mPend`, `mMssDone` ni `mFvgNear`).

Es decir: el techo absoluto es **~1 setup al día en M5**, y el estado del setup
queda desincronizado del rango que lo originó.

---

## 5. F4 — la kill zone filtra el barrido, no la confirmación

El propio input dice *«Confirmar solo dentro de kill zone»*, pero `kzOK` entra en
`baseGate`, y `baseGate` sólo se evalúa en el **armado**:

```pine
baseGate = rangeOK and kzOK and (not dirDone or not oneDir) and (not inPosition or not oneTrade)
if not mPend and baseGate
    if sweepUp and not sweptHi[1]
```

Combinado con el enclavamiento de `sweptHi` durante todo el rango, el resultado
es demoledor: **hay exactamente una vela candidata por rango H4 y por dirección**
(la del primer barrido), y esa vela concreta tiene que caer dentro de
`0700-1000` o `1230-1500`. Si el primer barrido ocurre a las 05:40, ese rango
queda muerto entero aunque el precio vuelva a barrer dentro de la KZ a las 08:00
(`sweptHi` ya vale `true`).

Añade un detalle de zona horaria: `time(timeframe.period, "0700-1000")` **sin
tercer argumento usa la zona del exchange del símbolo**, que en muchos feeds de
FX es `America/New_York`, no UTC ni la hora que tú ves en el gráfico. El texto
del input («hora del gráfico») no describe lo que hace el código.

**Corrección:** `kzOK` al confirmar el MSS, no al barrer; y zona horaria
explícita como input.

---

## 6. Resto de hallazgos (no causan el cero, pero falsean el backtest)

### 6.1 El FVG mira una vela M15 demasiado atrás

```pine
m15High1 = request.security(..., "15", high[1], ..., barmerge.lookahead_off)
m15High3 = request.security(..., "15", high[3], ..., barmerge.lookahead_off)
```

Con `lookahead_off` y gráfico por debajo de M15, el offset 0 **ya es** la última
vela M15 cerrada (ése es justamente el mecanismo antirrepintado). Al pedir `[1]`
y `[3]` estás mirando las velas M15 **2ª y 4ª hacia atrás**, no las tres últimas
cerradas. Efecto: el hueco de desplazamiento que crea el propio MSS se detecta
**una vela M15 tarde**, cuando el precio puede haberlo rellenado ya; y como
`na(mFvgNear)` congela el primer hueco encontrado, el script puede quedarse
enganchado a un FVG viejo y lejano.

Lo correcto para las tres últimas velas cerradas es offset **0 y 2**:
`fLow0 > fHigh2` (alcista) / `fHigh0 < fLow2` (bajista).

### 6.2 `minRR` es código muerto

```pine
tpPx = entryPx + mDir * rMultiple * riskPx
rr   = math.abs(tpPx - entryPx) / riskPx
if rr >= minRR
```

`rr` es idénticamente igual a `rMultiple` (3.0) por construcción. El filtro no
filtra nada nunca. No es el fallo, pero te está dando una falsa sensación de
tener un control de R:R que no existe.

### 6.3 El SL/TP se coloca una vela tarde

```pine
strategy.entry("Long", strategy.long, qty = qty)
pendingSL := slPx
...
if strategy.position_size != 0 and not na(pendingSL)   // <-- vela siguiente
    strategy.exit(...)
```

En la vela de entrada `strategy.position_size` **todavía vale 0** (la posición se
actualiza tras la ejecución de la orden), así que la condición es falsa y el
`strategy.exit` no se emite hasta la vela siguiente. El comentario del código
dice lo contrario. Un stop que debía saltar intrabar en la vela de entrada no
existe todavía.

### 6.4 El precio de entrada usado en el cálculo no es el de ejecución

`entryPx = mFvgNear` alimenta el riesgo y el TP, pero la orden es de mercado, y
con `process_orders_on_close = true` se ejecuta al **cierre** de la vela del
toque. El R real no es el calculado. La entrada «al primer toque del borde» que
describe la especificación es literalmente una orden **límite** en `mFvgNear`.

### 6.5 `ta.atr(14)[1]` pasado como argumento de una función de usuario

```pine
f_htf(_exp) => request.security(syminfo.tickerid, htf, _exp, lookahead = barmerge.lookahead_on)
htfATR  = f_htf(ta.atr(14)[1])
```

Que los rombos salgan bien demuestra que el inlining re-contextualiza
correctamente `high[1]`/`low[1]` al marco H4, así que este patrón **no es el
fallo**. Aun así es el único punto del script donde una función `ta.*` **con
estado** se instancia fuera del literal `request.security()`, y es gratis quitar
la ambigüedad escribiéndola dentro de la expresión, en una sola llamada con
tupla:

```pine
[rangeHigh, rangeLow, htfATR, htfBarTime] = request.security(syminfo.tickerid, htf,
     [high[1], low[1], ta.atr(14)[1], time], lookahead = barmerge.lookahead_on)
```

Como beneficio secundario pasas de 4 llamadas a 1.

### 6.6 `barstate.isconfirmed` en la entrada es inocuo pero engañoso

En velas históricas siempre vale `true`, y con `calc_on_every_tick = false` el
script sólo se evalúa al cierre. No bloquea nada. No es el fallo; sobra.

### 6.7 Pip fijo a `0.0001` y tamaño de posición sin `pointvalue`

```pine
riskPips = riskPx / 0.0001
qty = (strategy.equity * riskPercent / 100.0) / riskPx
```

El pip fijo se rompe en cualquier par JPY (factor 100). El `qty` ignora
`syminfo.pointvalue`, así que el «1 % de riesgo» sólo es cierto si el símbolo
tiene valor de punto 1 y la divisa de la cuenta coincide con la de cotización.

### 6.8 `invalidated` es inalcanzable en la vela del toque

```pine
if touched
    ...
else if invalidated
```

Si en la misma vela el precio toca el borde cercano y cierra más allá del borde
lejano, se entra igualmente. Es un `else if` que debería evaluarse antes.

### 6.9 `box.new()` en cada vela para el rango

`box.delete()` + `box.new()` cada vela funciona, pero es gasto innecesario;
`box.set_lefttop()` / `box.set_rightbottom()` sobre un único box es lo correcto.

### 6.10 Lo que **sí** está bien (para que no lo «arregles»)

- `f_htf(high[1])` con `lookahead_on`: es el patrón antirrepintado documentado. Correcto.
- `htfTime = f_htf(time)` **sin** `[1]`: correcto y deliberado. Devuelve la hora de
  apertura del H4 en curso, que es un dato ya conocido; sirve para detectar el
  cambio de rango sin sesgo de futuro.
- `ta.change()`, `ta.atr()`, `ta.lowest()`, `ta.highest()`: **todas** en ámbito
  global. Tras tu corrección previa no queda ninguna `ta.*` dentro de un
  condicional. Ese frente está limpio.
- El orden de declaración de las `var`: `mssLow`/`mssHigh` se declaran antes de
  usarse. No hay lectura antes de declaración.

---

## 7. Cómo confirmarlo en 5 segundos

`pine/crt_mss_fvg_fixed.pine` incluye un panel con el embudo completo:

```
sweeps 1o   ->  cuántos primeros barridos se detectan
armados     ->  cuántos pasan baseGate
MSS         ->  cuántos confirman
FVG         ->  cuántos encuentran hueco
ordenes     ->  cuántas órdenes se emiten
```

El primer contador que se quede en 0 es el eslabón roto. En el script original,
la predicción de esta auditoría es que **«armados» se queda casi en 0** (F2+F3+F4)
y que, si fuerzas `onlyKZ = false` para desbloquearlo, entonces MSS y FVG suben
pero **«ordenes» sigue en 0** (F1).

Esa es la prueba discriminante: **desactiva `onlyKZ` en el script ORIGINAL**. Si
aparecen etiquetas MSS pero siguen 0 operaciones, F1 y F4 quedan confirmados
exactamente como los describe esta auditoría.

---

## 8. Ficheros

| Fichero | Qué es |
|---|---|
| `pine/crt_mss_fvg_original.pine` | el código auditado, tal cual (sin el encabezado de comentarios), para diffear |
| `pine/crt_mss_fvg_fixed.pine` | versión corregida: F1–F4 + 6.1–6.9, con panel de diagnóstico |

Los cambios de comportamiento respecto al original (kill zone en la confirmación,
caducidad por rango, entrada límite) están todos detrás de inputs, de modo que
puedes volver al comportamiento anterior si quieres aislar variables.

> Aviso: la versión corregida **no se ha compilado**. Se ha verificado
> estáticamente el balance de paréntesis y la regla de Pine de que las líneas de
> continuación no lleven una indentación múltiplo de 4, pero el veredicto real lo
> da el editor de TradingView.
