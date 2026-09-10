# Ampliación del CRT · material de Instagram

Transcripción de 32 publicaciones de `@bctrades__` (el grueso) y
`@trader.derivados` (definiciones generales), pasadas a reglas mecánicas.
Recibido el 25 de agosto de 2026. **Nada medido todavía** salvo donde se dice.

Con el segundo bloque ya no son piezas sueltas: hay un **modelo completo y
ejecutable de arriba abajo**. Se escribe primero entero, y después qué parte
está probada y qué parte no.

---

# 1 · El modelo completo, de arriba abajo

## Paso 1 · Diaria (1D) — la dirección

> «Lo primero es tener una visión clara del mercado. Identificamos la dirección
> principal.»

Y una regla concreta para deducirla de las dos últimas velas diarias, en tres
casillas: **COMPRA**, **VENTA**, **INVÁLIDO**, con tres configuraciones cada una.

Con la captura en limpio los diagramas ya se leen, y confirman lo que había
inferido: es el CRT aplicado a la diaria.

| | vela 1 (base) | vela 2 | |
|---|---|---|---|
| **COMPRA** | define el rango | se lleva el **mínimo** y cierra dentro | comprar |
| **VENTA** | define el rango | se lleva el **máximo** y cierra dentro | vender |
| **INVÁLIDO** | define el rango | no se lleva nada (vela interna) o no vuelve dentro | no operar |

Su pie no enuncia la regla en palabras; solo dice «la vela diaria deja pistas…
pero hay que saber leerlas. **No todo es compra o venta.** Filtra, confirma y
ejecuta con cabeza». La tabla de arriba es lectura de los diagramas.

## Paso 2 · 4H — el rango y el objetivo principal

> «Una vez definida la dirección diaria, buscamos un rango en 4H que esté
> alineado con esa tendencia.»
> «Buscamos que en 4H el precio barra liquidez en la dirección que tenemos
> marcada.»

De aquí sale el **OBJETIVO 4H**: el extremo opuesto de la vela base.

## Paso 3 · 2H — confirmación y segundo objetivo

> «Afinamos aún más el análisis. En 2H confirmamos la estructura intradía y
> validamos nuestro sesgo. SEGUNDO OBJETIVO IDENTIFICADO.»

**2H es una temporalidad que no he usado nunca.** Todo mi trabajo ha ido con
H1 y H4.

## Paso 4 · 1H — el order block

> «Esperamos que, tras la liquidez tomada a favor nuestro y la creación de otro
> rango, se forme un Order Block en 1H.»
> **«Punto clave: al aparecer el Order Block en 1H y completar el rango, en 5
> min suele darse un cambio de estructura.»**

## Paso 5 · M15 (o M5) — el gatillo y los dos objetivos

> «Tenemos un rango en 15 min creado, buscamos como **primer objetivo el rango
> de 2H** y como **segundo objetivo el rango de 4H**.»
> «Tras liquidar el mínimo en 1H, bajamos a 15M para buscar confirmación y
> creación de rango. Con esa estructura, entramos buscando nuestro objetivo de 4H.»
> «La clave no es entrar rápido, sino entrar con confirmación.»

```
1D  dirección
 └─ 4H   rango alineado + barrido de liquidez        →  OBJETIVO 4H  (TP2)
     └─ 2H   confirma estructura intradía            →  OBJETIVO 2H  (TP1)
         └─ 1H   order block + rango completado
             └─ M15 / M5   rango creado / CHoCH      →  ENTRADA
```

**Dos objetivos escalonados, no uno.** Esa es la gestión, y es lo que más se
aleja de todo lo que he probado: siempre he salido en un solo punto.

---

# 2 · Las reglas de detalle

## 2.0 · Cómo actúa el precio según el cierre  ← **el eje de todo**

> «Cuando el precio supera el máximo o el mínimo de una vela anterior y logra
> **cerrar con cuerpo más allá de ese nivel, aumenta la probabilidad de
> continuidad** hacia el siguiente objetivo. Por el contrario, cuando el mercado
> deja de confirmar nuevos máximos o mínimos mediante sus cierres, suele entrar
> en fases de consolidación donde compradores y vendedores buscan equilibrio.»

Con el gráfico anotado de «saca alto / cierra dentro / cierra fuera / saca alto
reversión», la taxonomía queda cerrada en tres estados:

| lo que hace la vela | qué predicen |
|---|---|
| saca el extremo y **cierra fuera con cuerpo** | **continuidad** hacia el siguiente objetivo |
| saca el extremo y **cierra dentro** | se crea el rango → **reversión**, dirección contraria al barrido |
| no saca nada (vela interna) | consolidación, equilibrio |

Dos predicciones **opuestas sobre el mismo suceso**, separadas solo por dónde
cierra. Es de lo que cuelga el resto del material.

**MEDIDO Y NO SE SOSTIENE** · `RESULTADOS_cierres.md`. En H4 las dos celdas dan
50,62 % y 50,57 % de acierto en la carrera simétrica: idénticas, cuando su marco
dice que tienen que predecir cosas contrarias. En H1 la regla sale del revés con
significación (−0,0062 sobre 115.220 observaciones), y el polo que falla es el
de la continuidad.

## 2.1 · Las tres fases del rango

> «Primero la acumulación y la creación de la **vela base**. Después la
> **manipulación**, donde el precio liquida esa vela base y **cierra dentro del
> cuerpo** creando un rango. Y finalmente la **distribución**.»

Mi motor comprueba el cierre dentro del **rango** (`crt_canonico.py`, opción
`cierre_estricto`). Ellos dicen **cuerpo**. Es más restrictivo y es medible.

## 2.2 · Liquidez simple, doble y triple  ← la afirmación más contrastable

> «El precio puede tomar la liquidez las veces que quiera mientras siga cerrando
> dentro de la vela base. La doble y la triple ocurren cuando al precio le falta
> una activación de rango en otra temporalidad.»

| | qué afirman |
|---|---|
| **simple** | crea el rango y define el objetivo |
| **doble** | «confirmando la estructura y **aumentando la probabilidad**» |
| **triple** | «reforzando la estructura y aumentando **todavía más** la probabilidad» |

Es un contador sobre el motor que ya existe, y trae una predicción explícita:
un gradiente ordenado 1 → 2 → 3. Si el gradiente no aparece, se cae sola.

## 2.3 · Rango creado, continuación, descartado

> **Creación:** «el precio toma la liquidez de la vela base y acaba cerrando
> dentro de la estructura. A partir de esa reacción, se crea el rango que
> utilizaremos como referencia para leer la intención del movimiento.»
> **Continuación:** «con el rango ya creado, el precio comienza a respetar la
> estructura y continúa mostrando intención en la dirección del movimiento.»
> **Descartado:** «el precio deja de respetar el rango y termina cerrando fuera
> de la estructura, invalidándolo por completo. La idea del movimiento queda
> descartada y el contexto cambia por completo hasta que el precio vuelva a
> reestructurar.»
> Y una advertencia suya que conviene retener: «cuando esto pasa, es porque **no
> hemos alineado bien las temporalidades** y el precio no tiene por qué cumplir
> rangos sin sentido.»

## 2.4 · Rango reiniciado y descartado

> «Rango bajista **reiniciado**: el precio toma el mínimo de la vela que origina
> el rango, reiniciándolo y generando un rango alcista en contra.
> Rango bajista **descartado**: queda invalidado tras su reinicio y el precio
> confirma cerrando fuera.
> **Tras un reinicio, el rango solo se descarta si el precio confirma con un
> cierre fuera del rango principal.**»

Invalidación en tres estados. Mi motor solo tenía vivo o muerto. Aquí tomar el
extremo contrario **no mata el setup: lo da la vuelta**.

## 2.5 · PO3 en continuaciones

> «Barrida H4 → Rango M15 → Expansión → Objetivo H4»
> «Cada vela de 4H tiene una operación oculta de 15 min.»

1. Barrida en 4H: toma la liquidez del extremo de la vela base, activa el
   movimiento y define el objetivo en el extremo opuesto.
2. Rango en M15 dentro del PO3 de esa vela.
3. Expansión: **primera entrada** en M15.
4. Continuación en el PO3 de la **segunda** vela de 4H, en su mecha: **segunda
   entrada** hacia el mismo objetivo.

Dos entradas por estructura.

## 2.6 · CRT + order block

> «15M completa rango y 1H crea order block.»

## 2.7 · Correlaciones positivas

XAU–XAG · EURUSD–GBPUSD · AUDUSD–NZDUSD · EURJPY–GBPJPY · USDCHF–USDJPY ·
US500–NAS100 · NAS100–US30 · UKOIL–WTI · BTC–ETH.
«Cuando uno sube o baja, el otro suele acompañarlo.»

## 2.8 · Definiciones generales (trader.derivados)

**Order Block:** «la última vela antes de un movimiento muy fuerte en la
dirección opuesta». Marcar su rango y **esperar a que el precio vuelva**.

Ojo: **no es la definición del vídeo de liquidez**, donde el order block era la
propia vela envolvente y la entrada era inmediata. Dos modelos con el mismo
nombre. Aquí se usa el de bctrades: OB en 1H, y el gatillo llega después en M5.

**FVG:** hueco sin negociar al que el precio tiende a volver. *(Publicación
marcada como «Contenido generado con IA».)*

**Patrones de confirmación:** envolvente, martillo y estrella de la mañana en
compra; envolvente, estrella fugaz y estrella de la tarde en venta.

---

# 3 · Qué está medido y qué no

| pieza | estado |
|---|---|
| Patrón CRT de tres velas | medido · `RESULTADOS_crt_canonico.md` |
| **Objetivo en el extremo opuesto de la vela base** | **medido** — `crt_canonico.py:96` ya usa `tp = r.r_hi / r.r_lo`, no razón fija |
| Cierre de vuelta dentro del **rango** | medido (opción `cierre_estricto`) |
| Killzones | medido |
| Entrada por Fibonacci en M5 | medido · `RESULTADOS_crt_fib.md` |
| CRT anidado en M15 | medido · `RESULTADOS_crt_confluencias.md` |
| Envolvente como gatillo | medido · `RESULTADOS_ls_nasdaq.md` |
| FVG como zona | medido · `RESULTADOS_crt_fib.md` |
| Rangos internos en H4 | medidos (17,2 %, rango 2,11× más ancho) pero nunca metidos en el motor |
| «Daily Bias» | medido, **pero con otra definición**: el motor NSBE de swings de Multi Bias, no la regla de dos velas diarias de aquí |
| | |
| **La afirmación fundacional (cierra fuera → continúa / cierra dentro → se da la vuelta)** | **MEDIDA · no se sostiene** · `RESULTADOS_cierres.md` |
| **Cierre dentro del CUERPO, no del rango** | **sin medir** |
| **Liquidez doble y triple** | **sin medir** |
| **Rango reiniciado / descartado** | **sin medir** |
| **Regla de dos velas diarias (compra/venta/inválido)** | fijada; es el caso D1 de la prueba fundacional, y ahí sale al 48,76 % |
| **Temporalidad 2H** | **sin usar nunca** |
| **Dos objetivos escalonados (TP1 en 2H, TP2 en 4H)** | **sin medir** — siempre he salido en un punto |
| **Order block en 1H + cambio de estructura en M5** | **sin medir** |
| **PO3 con dos entradas** | **sin medir** |
| Correlaciones | trivial de comprobar, no es una estrategia |

Ocho piezas nuevas. Dos de ellas —los dos objetivos escalonados y las dos
entradas del PO3— **no son variantes del motor: cambian la gestión**, que es la
única dimensión que no he tocado en toda la semana.

# 4 · Orden de prueba propuesto

1. **Liquidez doble y triple.** Un contador sobre el motor que ya existe, y la
   única afirmación del material con una predicción explícita.
2. **Cierre en el cuerpo** y **rango reiniciado**. Dos cambios de regla, mismo motor.
3. **Los dos objetivos escalonados.** Es lo que más se aparta de todo lo probado.
   Mismas señales, salida distinta: parcial en el rango de 2H, resto en el de 4H.
4. **La cadena entera 1D → 4H → 2H → 1H → M15.** Motor nuevo. Se deja para el
   final porque encadenar seis filtros ya sabemos cómo acaba: la última vez que
   apilé seis condiciones quedaron 4 operaciones en seis años.

Pendiente: el pie de la publicación de las dos velas diarias.
