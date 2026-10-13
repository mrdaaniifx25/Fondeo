# La afirmación fundacional: cómo actúa el precio según el cierre

Todo el material de bctrades descansa sobre una sola idea, y ellos la enuncian
literalmente en dos mitades opuestas:

> «Cuando el precio supera el máximo o el mínimo de una vela anterior y logra
> **cerrar con cuerpo más allá de ese nivel, aumenta la probabilidad de
> continuidad** hacia el siguiente objetivo.»

> «El precio toma la liquidez de la vela base y acaba **cerrando dentro** de la
> estructura. A partir de esa reacción, **se crea el rango**» — y la dirección
> es la contraria al barrido.

Mismo suceso —que el precio se lleve el extremo de la vela anterior—, dos
predicciones **opuestas**, y lo único que las separa es dónde cierra. Eso es una
hipótesis excelente: es falsable y no hace falta simular ninguna operación para
comprobarla. Sin coste, sin entrada, sin stop, sin objetivo. Estadística
condicionada pura.

Si las dos celdas no se separan, todo lo que se construye encima está en el aire.

## Prueba 1 · Lo que hace la vela siguiente

Retorno de la vela siguiente en unidades de ATR(20), con el signo que **ellos**
predicen. Positivo = acertaron. EURUSD, NAS100, GBPUSD y USDJPY, 2020-2026.

| | observaciones | media en su sentido | IC 95 % |
|---|---|---|---|
| **H1** | 115.220 | **−0,0062** | [−0,0109, −0,0016] |
| **H4** | 27.831 | +0,0008 | [−0,0080, +0,0096] |
| **D1** | 5.008 | +0,0097 | [−0,0095, +0,0288] |

**En H1 la regla está del revés, y con significación.** Y el que falla es
justamente el polo de la continuidad: −0,0089 [−0,0152, −0,0026] sobre 64.321
casos. Después de que el precio se lleve el máximo de la vela anterior y cierre
con cuerpo por encima, la vela siguiente baja más veces de las que sube.

En H4 y D1 —las temporalidades que ellos usan— es cero.

**Esto encaja con algo que ya había salido por otro camino.** El cribado de 54
variables mecánicas sobre EURUSD encontró que la única señal presente al
horizonte de una hora era de **reversión**, las 15 variables apuntando al mismo
sitio. Aquí, con un método completamente distinto y sobre cuatro instrumentos,
la afirmación de continuidad a una hora sale del revés. Es el mismo hecho visto
desde dos sitios que no se hablan.

Ojo con el tamaño: −0,0062 ATR por observación son unas **0,05 pips**. Es
significativo porque hay 115.000 casos, no porque sea grande. No es que haya
negocio en hacer lo contrario: es que la afirmación no se sostiene.

## Prueba 2 · La versión fiel: probabilidad de llegar al objetivo

Ellos no hablan del cierre siguiente, hablan de **probabilidad de continuidad
hacia el siguiente objetivo**. Así que se mide como carrera: desde el cierre de
la vela que actúa, ¿qué llega antes, +1 ATR o −1 ATR?

Simétrica a propósito. Comparar «llega al objetivo» contra «se da la vuelta un
poco» estaría sesgado a favor de la distancia más corta. Se resuelve vela a vela
en M1, así que el orden dentro de la barra es real. El 50 % es la moneda al aire.

| | | observaciones | acierto | IC 95 % |
|---|---|---|---|---|
| **H4** | cierra FUERA → continuidad | 10.884 | **50,62 %** | [49,68, 51,55] |
| **H4** | cierra DENTRO → reversión | 7.754 | **50,57 %** | [49,45, 51,68] |
| **D1** | cierra FUERA → continuidad | 2.047 | 50,90 % | [48,74, 53,07] |
| **D1** | cierra DENTRO → reversión | 1.452 | 48,76 % | [46,19, 51,33] |

**Las dos celdas no se separan.** En H4, 50,62 % y 50,57 %: idénticas. Y eso es
justo lo que su marco dice que no puede pasar, porque son las dos celdas que
predicen cosas contrarias. Dónde cierre la vela no informa de lo que viene
después.

De las 16 casillas individuales, dos rozan la significación —EURUSD H4 reversión
52,26 % y USDJPY H4 continuidad 52,36 %— y están en **celdas distintas de
instrumentos distintos**, sin patrón. Con 16 casillas probadas, una o dos así es
exactamente lo que da el azar.

## Qué queda en pie y qué no

**No se sostiene:** el eje del que cuelga el resto. La posición del cierre
respecto al nivel barrido no separa continuidad de reversión, ni en el cierre
siguiente ni en la carrera al objetivo, ni en H4 ni en D1.

**Sigue sin probar, y con razón:** la **liquidez doble y triple**. Su afirmación
es sobre un *subgrupo* dentro de la celda «cierra dentro»: que tomar la liquidez
dos o tres veces sube la probabilidad. Que la celda entera esté al 50 % no
impide lógicamente que un subgrupo suyo esté por encima. Es menos probable
—si el subgrupo estuviera muy por encima, tiraría de la media— pero no está
descartado, y es la única afirmación del material que trae un gradiente
ordenado que el ruido no fabrica. Merece medirse aparte.

## Reproducir

`bt/cierres.py` clasifica, `bt/run_cierres.py` mide el cierre siguiente,
`bt/carrera_cierres.py` mide la carrera simétrica.
