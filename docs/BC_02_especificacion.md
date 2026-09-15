# BC · Especificación mecánica

Escrita solo desde el material de `BC_01_material.md`, según las reglas de
`BC_00_reglas.md`. **Antes de correr una sola línea.**

## Leyenda del origen

Cada regla lleva marcado de dónde sale. Es lo que permite defender el resultado
después, o saber a quién echarle la culpa si falla.

| marca | significado |
|---|---|
| **[T]** | texto literal de bctrades |
| **[D]** | leído de sus diagramas |
| **[U]** | lectura del usuario, no publicada por ellos |
| **[?]** | sin resolver — se enumeran las opciones y se prueban todas |

---

# 1 · De qué va

Una vela deja un rango. La siguiente sale de ese rango, toma la liquidez y
vuelve a meterse dentro. Eso «activa» el rango y crea un objetivo en el extremo
opuesto. Cuando varias temporalidades tienen objetivos vivos en la misma
dirección, se baja a una temporalidad menor, se espera un cierre que confirme, y
se entra buscando esos objetivos con un margen de 1:3. **[T]**

# 2 · Temporalidades

**[T]** Aparecen 1D, 12H, 8H, 4H, 2H, 1H, 15M, 10M, 5M y 2M. No hay una rejilla
fija: se usa la que tenga objetivo pendiente.

> «En 8 horas vemos que el precio tiene un objetivo pendiente de completar. Esto
> nos da el contexto principal y el recorrido potencial que vamos a buscar.»

**Reducción para la primera versión.** Se implementan **1D, 12H, 4H y 1H**, que
son las que aparecen en las dos operaciones mejor documentadas (la libra y el
análisis del 25 de mayo). 8H y 2H quedan fuera de la primera pasada y se anota
como limitación, no como decisión de diseño.

## 2.1 · Anclaje de cada bloque  **[?]**

| TF | inicio | origen |
|---|---|---|
| 1D | **[?]** | ninguna publicación lo dice |
| 12H | 00:00 y 12:00 **[U]**, huso **[?]** | lectura del usuario |
| 4H | **[?]** | no publicado |
| 1H | en punto, sin ambigüedad | — |

Husos a probar: **UTC**, **Nueva York**, **Madrid**, **bróker típico (UTC+2/+3)**.

Cuatro rejillas distintas producen estrategias distintas. **No se elige la que
mejor rinda.** Se resuelve como dice el punto 11.

# 3 · Vela base, activación y rango

## 3.1 · Vela base  **[T]**

La vela anterior. Sus extremos definen el rango; su cuerpo define la zona de
cierre válida.

> «El precio crea una vela base donde comienza la acumulación de liquidez y,
> posteriormente, manipula esa zona para construir el rango.»

## 3.2 · Activación  **[?]** — dos lecturas, se prueban las dos

Describen el mismo suceso de dos formas en publicaciones distintas:

> **[T]** «El precio **abre por debajo de la vela anterior**, activando liquidez.»
> **[T]** «La manipulación, donde el precio **liquida esa vela base y cierra
> dentro del cuerpo** creando un rango.»

**Lectura A · apertura estricta**
```
alcista:  open[i] < low[i-1]
bajista:  open[i] > high[i-1]
```
Fiel a «abre por debajo». En divisas la apertura casi coincide con el cierre
anterior, así que dará muy pocos casos. Es una predicción, no una pega.

**Lectura B · barrido con cierre en el cuerpo**
```
alcista:  low[i] < low[i-1]
          Y  cuerpo_bajo[i-1] <= close[i] <= cuerpo_alto[i-1]
bajista:  high[i] > high[i-1]
          Y  cuerpo_bajo[i-1] <= close[i] <= cuerpo_alto[i-1]
```
donde `cuerpo_bajo = min(open,close)` y `cuerpo_alto = max(open,close)`.

**Lectura C · las dos a la vez.** Abre fuera *y* cierra dentro del cuerpo.

Se reportan las tres. La C es la más restrictiva y la que más se parece a lo que
enseñan los diagramas.

## 3.3 · Objetivo  **[T][D]**

El **extremo opuesto** de la vela base.
```
rango alcista activado  ->  objetivo = high[i-1]
rango bajista activado  ->  objetivo = low[i-1]
```

## 3.4 · Estados del rango  **[T]**

| estado | condición |
|---|---|
| **creado** | se cumple la activación |
| **continuación** | el precio respeta la estructura y sigue hacia el objetivo |
| **completado** | el precio alcanza el objetivo |
| **reiniciado** | el precio toma el extremo **contrario** de la vela base |
| **descartado** | tras el reinicio, **cierra fuera** del rango principal |

> «Tras un reinicio, el rango **solo se descarta si el precio confirma con un
> cierre fuera** del rango principal.»

Esto es lo importante y es distinto de tener solo «vivo/muerto»: **tomar el
extremo contrario no mata el setup, lo da la vuelta.**

## 3.5 · Los cuatro reinicios  **[T]**

Los cuatro casos están descritos en `BC_01` §3. Para la primera versión se
implementa la **máquina de estados** de 3.4, que los cubre a los cuatro como
trayectorias posibles. La regla de *cómo operarlos* no está publicada —está
detrás de «Comenta REINICIO»— así que **no se inventa**.

## 3.6 · Doble y triple liquidez  **[T]**

Número de veces que el precio toma el mismo extremo de la vela base sin que el
rango quede descartado. Se cuenta y se guarda como atributo del setup.

> «El precio ya tiene un rango previamente creado y vuelve a buscar la liquidez
> de ese mismo rango, respetando en todo momento la estructura.» *(la libra)*

# 4 · Acumulación de objetivos  **[T]**

En cada instante se cuenta cuántas temporalidades tienen **objetivo vivo en la
misma dirección**.

> «Vamos acumulando objetivos y reforzando la dirección, dejando ya las
> temporalidades alineadas hacia esa dirección.»

`n_objetivos ∈ {1, 2, 3, 4}` sobre 1D, 12H, 4H, 1H. Se guarda como atributo. En
las dos operaciones documentadas hay al menos 1D + 12H, y en una también 4H.

# 5 · Ejecución  **[T]**

```
1 · hay objetivo vivo en temporalidad mayor
2 · en la temporalidad de ejecución (1H) se CREA un rango en la misma dirección
3 · se espera el CIERRE de esa vela
4 · entrada al cierre
```

> «En 1H vemos el primer rango creado que nos da la confirmación para ejecutar.
> Entramos en el cierre de 1H buscando un margen de 1:3 hasta los objetivos de
> 12H y diario.»

**Temporalidad de ejecución [?]:** en el material aparece 1H, 15M, 10M, 5M y 2M.
Primera versión: **1H**, que es la de las dos operaciones mejor documentadas. Se
anotará 15M como variante.

# 6 · Stop  **[U]**

No lo publican nunca. Lectura del usuario, coherente con los diagramas:

```
compra:  stop = low  de la vela de ejecución  −  colchón
venta:   stop = high de la vela de ejecución  +  colchón
```

Colchón **[?]**: 0, 1 o 2 ticks. Se reportan los tres.

# 7 · Objetivo de la operación y R:R  **[T]**

El objetivo de la operación es **el objetivo de la temporalidad mayor**, no un
múltiplo fijo del riesgo.

```
riesgo  = |entrada − stop|
premio  = |objetivo_mayor − entrada|
RR      = premio / riesgo
```

## 7.1 · Las tres zonas — el filtro de calidad  **[T]**

| zona | RR | qué dicen |
|---|---|---|
| **óptima** | **≥ 3** | «la zona más favorable para buscar una ejecución» |
| continuación | ≈ 2 | «el movimiento todavía tiene margen» |
| últimas oportunidades | ≈ 1 | «el margen disponible se reduce» |

> «No solo importa identificar el PO3, sino saber dónde está el precio dentro de
> él y qué RR nos ofrece esa fase. Esto nos permite **decidir si la entrada
> tiene sentido**.»

**Este es el filtro de «se ve bien», y es un cociente, no una sensación.**
Regla implementada: se opera solo con **RR ≥ 3**. Se medirán también las bandas
2–3 y 1–2 para ver si el gradiente que afirman existe.

Nota: su única operación perdedora documentada entró con RR 1:1, o sea en la
peor de las tres zonas según su propio criterio.

# 8 · Confluencias que se guardan pero no filtran

Se calculan y se anotan por operación, sin usarse para entrar. Así se puede ver
después si aportan, sin haber elegido nada por adelantado.

- **[T]** CRT completado en 15M + order block en 1H
- **[T]** doble / triple liquidez
- **[T]** número de objetivos acumulados
- **[T]** PO3 de 2 velas o de 3 velas
- **[T]** rango dentro de rango

# 9 · Salida

- objetivo alcanzado → cierre a objetivo
- stop alcanzado → cierre a stop
- **[?]** tiempo máximo: no lo publican. Se pone un tope de **5 velas de la
  temporalidad del objetivo** y se declara aquí. Se reporta qué porcentaje sale
  por tiempo.
- empate stop/objetivo dentro de la misma vela M1 → se cuenta **stop**

# 10 · Coste

No lo mencionan nunca. Se usan los mismos que en todo el repositorio, y se
reporta la ventaja **bruta y neta** por separado siempre:

```
EURUSD 1,2 pips · GBPUSD 1,5 · USDJPY 1,3 · NAS100 1,5 pts · SPX500 0,6 pts
```

# 11 · Cómo se resuelven las ambigüedades  ← la parte que decide si esto vale

Hay **cinco** parámetros libres: huso de la rejilla, lectura de la activación,
temporalidad de ejecución, colchón del stop y tope temporal. Probarlos todos y
quedarse con el mejor sería ajustar a resultados.

**Se resuelven en dos fases, y la primera no mira ningún resultado.**

### Fase 1 · calibración contra su propio relato

Publican operaciones con fecha, gráfico y una narración de qué pasó en cada
temporalidad. Se busca qué combinación de parámetros hace que **la estructura
que ellos describen aparezca donde ellos dicen**. Eso es ajustar a su
descripción, que es independiente de si la operación ganó o perdió.

Calibrables con los datos disponibles (terminan el 31-07-2026):

| operación | fecha | dato |
|---|---|---|
| S&P 500 | 2026-07-22 | SPXUSD ✓ |
| NASDAQ | 2026-07-30 | NSXUSD ✓ |
| GBPUSD | ≤ 2026-05-21 | GBPUSD ✓, falta el día exacto |

Criterio de calibración, escrito ahora: el anclaje elegido es aquel en el que,
en la fecha de la operación, **existe un rango activo en la temporalidad que
ellos nombran y en la dirección que ellos nombran**. Si dos anclajes empatan, se
reportan los dos.

### Fase 2 · lo que la calibración no resuelva

Se reporta **la rejilla entera**, todas las celdas, sin elegir. Y se dice
explícitamente cuántas celdas se han probado, para que el lector aplique el
descuento por contrastes múltiples que corresponda.

# 12 · Lo que esta especificación NO cubre

Se dice para que nadie —yo el primero— presente esto como «el método de
bctrades» sin matices:

- **Cómo operan los reinicios.** No está publicado.
- **Cuándo no operan.** Nunca lo dicen.
- **Tamaño de posición y gestión de la cuenta.** No publicado.
- **8H y 2H**, que usan y aquí no están.
- **La parte discrecional.** Si al mirar el gráfico descartan setups por algo
  que no han escrito, eso no está aquí y no puede estarlo.

Lo que se va a medir es **esta especificación**, no «lo que hace bctrades». Si
sale mal, lo honesto será decir que falló esta lectura del método, y qué parte
de la lectura era mía.

# 13 · Siguiente paso

Pre-registro con los criterios de éxito en número, antes de la primera corrida.
