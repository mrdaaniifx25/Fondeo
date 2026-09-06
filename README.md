# Fondeo · qué se midió y qué salió

Dos meses midiendo estrategias de trading sobre datos de precio reales, con
preregistro sellado antes de cada medición y controles al lado de cada
resultado. 174 documentos. Esto es el índice.

**Método, en una línea:** cada medición se firma antes de correrla (qué se
espera y qué umbral la declara buena), se hace **un solo pase**, y se publica
tal cual salga — incluidos los fallos propios, que están todos documentados.

---

## LO ÚNICO QUE SIGUE EN PIE

| qué | dónde | estado |
|---|---|---|
| **Estrategia del oro** (rotura de 51 velas H1, XAUUSD) | `RESULTADOS_sqx_xauusd.md` · `OPERATIVA_oro.md` | pasa sus 4 controles internos. **Depende de un dato que falta: el spread real del XAUUSD. Umbral 0,52 $** |
| **Geometría de barreras** para pasar un reto | `RESULTADOS_cfd_fondeo.md` | 36,9 % fuera de muestra = el techo de azar. No es una señal |
| **Prima de riesgo de los índices** | `RESULTADOS_anomalias.md` | +0,070 % diario, z +2,93. Real, y no alcanza para nada operable |

---

## LOS TRES HALLAZGOS QUE ORDENAN TODO LO DEMÁS

### 1 · El muro del coste
`COSTE_real.md` · `muro_del_coste.py`

Coste real medido: **1,43 pips** en EURUSD. Con stops de 5-10 pips eso es el
13-27 % de cada operación. Las ventajas brutas que existen son de ese tamaño.

    stop  2 pips  ->  el coste es el 71 % del riesgo
    stop 10 pips  ->  el 14 %
    stop 50 pips  ->  el 3 %

### 2 · El reto de fondeo premia la varianza, no la ventaja
`RESULTADOS_swing_eurusd.md` · `RESULTADOS_alto_winrate.md`

    estrategia SIN ventaja, geometria bien puesta   ->  36,9 % de aprobado
    estrategia CON ventaja real (Sharpe 0,5)        ->  28,4 %

Hace falta **Sharpe 1,2** solo para empatar con no tener ventaja. Una
estrategia buena y lenta no llega en 60 días. **Por eso pasar un reto no
demuestra nada.**

### 3 · Buscar produce resultados aunque no haya nada
`RESULTADOS_multiples_comparaciones.md` · `RESULTADOS_ema_fibo.md`

Con 225 celdas sobre **datos barajados sin ninguna estructura**, un nulo dio
z **+3,64** y 5 celdas por encima de z=2. Con 65 celdas, `P(alguna z ≥ 3,01)`
por azar = **15,6 %**.

Por eso cada resultado de este repositorio lleva su nulo al lado.

---

## LO QUE SE MIDIÓ Y NO FUNCIONA

| familia | dónde | resultado |
|---|---|---|
| SMC-71 / fibo 71 % | `RESULTADOS_smc71_instrumentos.md` | ventaja bruta real (+0,166 R, z +4,90 agrupado) del tamaño del coste |
| EMA + Fibonacci, 675 celdas | `RESULTADOS_ema_fibo.md` | 0 positivas. Peor que datos barajados |
| Búsqueda con árboles, 50 variables | `RESULTADOS_busqueda_ml.md` | IC +0,0126 contra una media de nulos de +0,0165 |
| Anomalías académicas (deriva nocturna, cambio de mes) | `RESULTADOS_anomalias.md` | las cuatro muertas. La del NY Fed murió al publicarse |
| Swing con stops anchos | `RESULTADOS_swing_eurusd.md` | Sharpe +0,52, t +0,94. Indetectable en 6,5 años |
| Rotura de canal simétrica | `HOJA_EURUSD.md` | bate a los nulos, no al azar. Estructura menor que el coste |
| Barrido asiático (2 versiones) | `RESULTADOS_barrido_asiatico.md` · `RESULTADOS_lsweep_v1.md` | **bruta negativa**. Aciertan por debajo del azar geométrico |
| Estrategia del grupo de NASDAQ | `RESULTADOS_grupo_nasdaq_2.md` | −0,044 bruto a su ritmo real de operativa |
| Rango asiático (Tradinverso) | `RESULTADOS_rango_asiatico.md` | ventaja bruta real, solo a 3-4 pips de stop, donde el coste la come |

---

## LA RESPUESTA A "CÓMO HAY GENTE QUE RETIRA"
`RESULTADOS_arbitraje_fondeo.md`

No operan mejor. Explotan que **su pérdida está topada en la cuota**:

    78 evaluaciones · 6.000 € en cuotas · 13 pasadas (16,7 %) · 17.729 € neto
    EV = +227 € por cada cuota de 77 €

Exige bankroll y repetición, no señal. Con una sola cuota, 83 % de perderla.

---

## HERRAMIENTAS QUE VALEN PARA CUALQUIER ESTRATEGIA NUEVA

| qué | dónde |
|---|---|
| Formulario para especificar una estrategia medible | `FORMULARIO_estrategia.md` |
| Control nulo (bloques permutados) | `bt/ema_fibo.py`, función `sintetico` |
| Control positivo (deriva inyectada) | `bt/control_positivo.py` |
| Curva de detección (qué tamaño de ventaja vería el montaje) | `bt/ema_fibo_deteccion.py` |
| Simulador de retos de fondeo | `bt/cfd_fondeo.py`, `bt/reto_montecarlo.py` |

---

## LOS FALLOS PROPIOS, TODOS DOCUMENTADOS

No están escondidos porque son la mitad del valor del repositorio. Los que más
enseñaron:

- **Mirada al futuro dentro de la vela de entrada** (`RESULTADOS_ema_fibo.md`):
  daba z **+12,53** falso. Detectado porque los nulos puntuaban igual de alto.
- **Nulo con fuga** (`RESULTADOS_busqueda_ml.md`): sorteaba bloques con
  reemplazo y se solapaban. El nulo batía a la señal, que es imposible.
- **Control positivo que no medía lo que decía**: agregaba compras y ventas,
  y una deriva direccional se cancelaba.
- **Cierre prematuro de la posición** (`RESULTADOS_lsweep_v1.md`): confundir
  la ventana de entrada con la de gestión cambiaba el reparto TP/SL de 38/313
  a 92/442.
