# BC · Pre-registro

Escrito **antes** de la primera corrida. Especificación en `BC_02`.

# 1 · Qué se contrasta

La especificación de `BC_02`, no «el método de bctrades». La diferencia está
escrita en `BC_02` §12 y se mantendrá al informar.

# 2 · Datos

| | periodo | uso |
|---|---|---|
| EURUSD, GBPUSD, USDJPY, NAS100, SPX500 | **2020-2023** | desarrollo |
| los mismos | **2024-2026** | **cerrado** hasta la confirmación |

Los datos ya los he mirado mucho esta semana. La protección no es que sean
nuevos —no lo son— sino que **no se ajusta nada**: la especificación está
congelada en `BC_02` y los parámetros libres se resuelven por el procedimiento
del punto 3, que no mira resultados.

# 3 · Calibración · fase que NO mira resultados

Cinco parámetros libres (`BC_02` §11). Se fijan comparando con **el relato** de
sus operaciones documentadas, nunca con si ganaron.

Operaciones utilizables (los datos acaban el 31-07-2026):

| operación | fecha | qué narran |
|---|---|---|
| S&P 500 | 2026-07-22 | activación de rango en 12H con objetivo, ejecución en 1H, compra |
| NASDAQ | 2026-07-30 | objetivo diario activado y completado, ejecución PO3 1H |
| GBPUSD | ≤ 2026-05-21 | rango 1D activado, doble liquidez en 4H, cierre en 1H, compra |

**Criterio de calibración, fijado ahora.** El anclaje y la lectura de activación
elegidos son aquellos en los que, en la fecha de cada operación, existe un rango
**activo en la temporalidad que ellos nombran y en la dirección que ellos
nombran**. Se puntúa cuántas de las tres operaciones reproduce cada combinación.

- Gana la combinación que reproduzca **más** operaciones.
- Empate → se llevan **todas** las empatadas a la fase 2 y se reportan todas.
- Ninguna reproduce ninguna → **se declara que la especificación no reproduce
  su método** y se dice así, sin seguir adelante buscando una que sí.

Estas tres fechas caen en 2026, fuera del periodo de desarrollo. Se usan solo
para fijar la rejilla, no para medir rendimiento.

# 4 · Criterio principal · 2020-2023

Ventaja **neta** por operación, en R, con el coste de `BC_02` §10.

**Se considera que hay algo si el intervalo de confianza al 95 % de la R neta
por operación excluye el cero, por el lado positivo.**

Un solo contraste sobre la combinación calibrada. Si la calibración deja varias
empatadas, el umbral pasa a **99 %** y se dice cuántas se probaron.

## 4.1 · Potencia · declarado por adelantado

Con objetivo estructural la R varía mucho, así que la desviación típica será
grande. Se declara ahora:

- **n < 100 operaciones** en desarrollo → la prueba está **infrapotenciada**.
  Se informa el número pero **no se concluye nada**, ni a favor ni en contra.
- **n ≥ 100** → se aplica el criterio del punto 4.

Esto se escribe ahora para no poder decir después «salió positivo» con 30
operaciones, ni «no funciona» con 40.

# 5 · Confirmación · 2024-2026

Se abre **una sola vez**, y solo si el criterio principal se cumple.

1. El signo se mantiene.
2. La ventaja neta es al menos **la mitad** de la de desarrollo.

Si falla cualquiera de los dos, **descartada**, y se dice así.

# 6 · Lo que se mide sin que decida nada

Se calcula y se informa, pero no entra en el criterio. Sirve para entender, no
para rescatar:

- rejilla completa de RR: **≥3**, **2–3**, **1–2**, **<1** → ¿existe el gradiente
  que afirman?
- liquidez simple, doble y triple
- número de objetivos acumulados (1, 2, 3, 4)
- con y sin la confluencia CRT 15M + order block en 1H
- reparto por instrumento
- porcentaje de salidas por tiempo
- ventaja bruta además de la neta, siempre las dos

# 7 · Controles obligatorios

Los mismos que en todo el repositorio:

- **dirección invertida** con el mismo momento y el mismo stop
- **entrada aleatoria** en los mismos instantes con la misma distribución de
  riesgo
- **sensibilidad al coste** de 0 a 4× el supuesto
- **año a año**, sin agregar

# 8 · Qué invalidaría la prueba

- Menos de 100 operaciones en desarrollo → infrapotenciada (punto 4.1).
- La calibración no reproduce ninguna de sus tres operaciones → la
  especificación no es su método y se dice.
- Cualquier resultado con |z| > 5 se trata como **error propio hasta demostrar
  lo contrario**, y se audita antes de informarlo. Ya ha pasado dos veces esta
  semana.

# 9 · Compromiso

Una pasada. Sin reajustes. Si sale que no, se escribe que no y se dice qué parte
de la lectura era mía y cuál del usuario.
