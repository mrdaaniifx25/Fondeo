# Qué mandar de las 71, y qué no

Lista de criterios para que él escanee los títulos. Cinco casillas abiertas y
una lista de descartes. La razón de cada cosa está medida y enlazada.

---

## Por qué sólo cinco

Tres meses han cerrado familias enteras. Pedirle que mande «las cinco mejores»
no sirve: lo que decide si una prueba aporta algo no es lo buena que parezca,
es si **su respuesta es desconocida**. Estas cinco casillas lo son. El resto no.

---

## Casilla 1 · Swing con stop ancho · permanencia de 3 a 20 días

**Cómo se reconoce**: habla de gráfico diario o semanal, de «aguantar la
operación», de stops de 100+ pips, de operar «una o dos veces al mes».

**Por qué está abierta**: el muro de coste cae 20 veces al pasar de una hora a
un mes (`RESULTADOS_muro_horizonte.md`). Todo lo que he cerrado era intradía,
donde la horquilla decide sola. Ahí arriba no decide.

**Qué mediría**: la regla tal cual, en EURUSD/oro/DAX, con el control de
comprar y aguantar que faltó en todo lo demás.

**Datos**: los tengo. Se mide el mismo día.

---

## Casilla 2 · Un evento de calendario

**Cómo se reconoce**: NFP, datos de empleo, IPC, reuniones de la Fed o del BCE,
vencimiento de opciones, cierre de mes o de trimestre.

**Por qué está abierta**: es lo único con un **mecanismo que no es geometría del
gráfico**. Hay flujo real en fechas conocidas —rebalanceo de carteras, cobertura
de exportadores, vencimientos— y eso no es lo mismo que dibujar una línea. Todo
lo cerrado hasta ahora miraba formas en la pantalla.

**Qué mediría**: la deriva y la volatilidad alrededor de la fecha, contra el
control proporcional que se me ocurrió tarde (`RESULTADOS_reloj.md`).

**Datos**: fin de mes y día de la semana salen solos. Para las fechas exactas de
Fed y BCE tendría que pegármelas él.

---

## Casilla 3 · Relación entre dos instrumentos

**Cómo se reconoce**: correlación, divergencia entre pares, DXY contra EURUSD,
oro contra bonos, un índice contra otro, «cuando uno hace X el otro hace Y».

**Por qué está abierta**: es **otra fuente de información**, no la misma mirada
al mismo gráfico. `RESULTADOS_smt.md` midió una versión —divergencia SMT— y salió
plana, pero eso era una regla visual, no una relación estadística entre precios.

**Qué mediría**: la relación estimada sólo con pasado, y si el diferencial
vuelve a la media más de lo que cuesta esperarlo.

**Datos**: tengo EURUSD, oro y DAX. Con tres no da para mucho, pero da.

---

## Casilla 4 · Coste de financiación, swap o carry

**Cómo se reconoce**: habla de swap positivo, de «cobrar por mantener», de
diferenciales de tipos, de carry trade.

**Por qué está abierta**: **es el único bloque que sigue vivo.** En
`RESULTADOS_estrategia_final.md` el carry es lo único con correlación 0,10 con
todo lo demás y lo único aún positivo en 2013-2026 (Sharpe +0,19). Mi versión
usa inflación del Banco Mundial con dos años de retraso — una versión coja. Una
regla que use el swap real del bróker sería mejor que la mía.

**Qué mediría**: la regla contra mi versión coja, a ver cuál gana.

**Datos**: necesito **la tabla de swaps de su bróker**. Una captura vale.

---

## Casilla 5 · Estacionalidad con mecanismo

**Cómo se reconoce**: días concretos del mes, efecto fin de mes, un día de la
semana, «el oro sube en enero», rollover de futuros.

**Por qué está abierta**: es verificable y **barata de descartar**, y a
diferencia de las sesiones tiene un flujo detrás que se puede nombrar. Las
sesiones las cerré (`RESULTADOS_reloj.md`): cada una captura exactamente su
parte proporcional de la deriva. El calendario no está medido así.

**Qué mediría**: lo mismo que el reloj — la parte proporcional que le toca, no
contra cero.

**Datos**: los tengo. Sale el mismo día.

---

## Lo que NO hace falta que mande

Si el título va de esto, la respuesta ya está medida y sólo perderíamos tiempo:

| tema | dónde está cerrado |
|---|---|
| barridos de liquidez, order blocks, FVG, CRT, poder de tres | 9 familias, 175.000 operaciones |
| niveles de sesión (Asia, Londres, NY) | `RESULTADOS_reloj.md` |
| confluencia multimarco (diario→H4→H1→M5) | `RESULTADOS_techo_filtro.md`, `RESULTADOS_espacio.md` |
| RSI, MACD, medias, Donchian, ATR **en intradía** | `RESULTADOS_rejilla_indicadores.md`, 108 celdas |
| rebote en sobreventa / sobrecompra | t **−8,11** sobre 55 años. No es cero: es negativo |
| patrones de velas (envolvente, martillo, estrella) | `RESULTADOS_patrones_velas.md` |
| Fibonacci, retrocesos, extensiones | `RESULTADOS_crt_fib.md` |
| scalping, M1, M5, M15 de cualquier tipo | el coste se lleva del 17 % al 67 % del riesgo |

---

## Lo que espero, dicho antes

Para que no me acuse luego de moverme: **espero que las cinco salgan planas.**
Lo que las hace valer la pena no es que vayan a funcionar, es que **su respuesta
no la sé**, y hasta ahora todo lo que he podido predecir de antemano lo he
acertado.

La casilla 4 es la única donde apostaría algo a que hay algo. Y aun así no daría
300 €/mes sobre 10.000 €: ese número no lo arregla ninguna estrategia, lo arregla
el tamaño de la cuenta.
