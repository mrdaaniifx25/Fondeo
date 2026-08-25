# ¿Separa la vela diaria los setups buenos de los malos?

Pregunta del usuario: «hay ejemplos que sí y otros que no; ¿no lo dirá la vela
diaria, por objetivos?». Es una hipótesis buena y concreta, así que se mide.

Se parte de la única celda con ventaja bruta real medida hasta ahora: la
**liquidez simple en H4**, +0,085 R sobre 9.197 casos, coste 0,070 R, neta
−0,023 R. Solo le faltan **0,023 R** para pasar, así que bastaría un filtro que
aportase poco.

Cinco lecturas del contexto diario. Cinco contrastes, así que el umbral honesto
es |z| > 2,58, no 1,96.

## Un fallo que casi me cuela un resultado falso

La primera versión de la lectura 4 —«¿la diaria en curso ya barrió a la
anterior?»— daba **z = +10,73**, con las dos mitades de signo opuesto. Eso es
demasiado bueno, y demasiado bueno siempre significa un error.

Lo era: usaba el máximo y el mínimo de la vela diaria **entera**, que incluye
barras posteriores a la entrada. Para una compra, el mínimo del día baja
justamente cuando la operación sale mal. Estaba leyendo el futuro.

Corregido —acumulando los extremos del día solo hasta el cierre de la vela de
entrada— el z pasa de +10,73 a +0,82.

## El contraste correcto

También estaba mal planteado mi propio marcador: comparaba cada celda **contra
cero**, y eso no dice nada, porque la base ya es positiva. Lo que responde a la
pregunta es la **diferencia entre grupos**.

| lectura del contexto diario | grupo A | grupo B | diferencia | z |
|---|---|---|---|---|
| 1 · de acuerdo con el CRT de la diaria | +0,108 | +0,081 | +0,027 R | +0,53 |
| 2 · objetivo dentro del rango diario | +0,097 | +0,046 | +0,051 R | +1,26 |
| 3 · objetivo cerca vs lejos (en ATR diario) | +0,109 | +0,067 | +0,043 R | +1,26 |
| 4 · la diaria ya barrió a favor | +0,104 | +0,074 | +0,030 R | +0,82 |
| 5 · entrada en la mitad alta del rango diario | +0,091 | +0,079 | +0,011 R | +0,34 |

**Ninguna separa.** Todas por debajo de |z| = 1,3, cuando hacía falta 2,58.

## Pero hay algo que sí merece decirse

**Las cinco apuntan en la dirección de su intuición.** Las cinco diferencias son
positivas: +0,027, +0,051, +0,043, +0,030, +0,011. Ninguna contradice la idea.

Bajo la hipótesis nula, cinco señales independientes apuntando al mismo lado
tendría una probabilidad del 6 %. Pero **no son independientes** —la 2 y la 3
son prácticamente la misma cosa, «el objetivo está cerca»—, así que en la
práctica son unas tres señales y la probabilidad sube al 25 %. No es evidencia.
Es, como mucho, que la idea no está descartada.

## Por qué no puedo contestar, y esto es lo importante

El error típico de la diferencia con n ≈ 4.500 por grupo es **0,034 R**. El
filtro que haría falta para cruzar el coste aporta **+0,03 R**.

O sea: **el efecto que busco es más pequeño que el ruido de mi propia medición,
incluso con 9.197 operaciones.** Para detectar +0,03 R con esta varianza harían
falta del orden de 70.000 operaciones por grupo.

La razón por la que no puedo responder «¿lo dice la diaria?» no es que la
respuesta sea que no. Es que **a esta escala de efecto la pregunta no es
respondible con datos mecánicos**, por muchos que junte.

Eso cambia dónde hay que buscar: no en más variables mecánicas, sino en una
señal que aporte **mucho** en vez de poco. Si el criterio humano añade +0,03 R,
no se podrá demostrar nunca. Si añade +0,30 R, bastan unos 100 ejemplos
etiquetados.

## Reproducir

`bt/contexto_diario.py`.
