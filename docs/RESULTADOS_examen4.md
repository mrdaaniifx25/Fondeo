# Resultados · cuarto bloque del examen, con cuenta de 10.000

50 sesiones nuevas, cero solapamiento con las 64 anteriores. Es el primer bloque
que se juega con la cuenta de FundingPips encima: 10.000 $, 1 % por operación,
5 % de pérdida diaria, 10 % de pérdida total, 8 % de objetivo, mínimo tres días
operados. Cuando revienta o pasa, empieza otro intento.

`python3 bt/examen4.py` · salida completa en `data/examen4_salida.txt`

## Los tres umbrales firmados

Los mismos de siempre, a una cola, y los tres tenían que salir.

| | z | umbral | |
|---|---|---|---|
| acierto sobre el 33,3 % geométrico | **+5,61** | > +1,64 | pasa |
| R neta por operación | **+4,36** | > +1,64 | pasa |
| diferencia contra la regla, emparejada por día | **+6,51** | > +1,64 | pasa |

Es el segundo bloque consecutivo que pasa los tres, y con la muestra más grande
de las cuatro.

## El bloque

```
operaciones            64   en 39 sesiones (11 sin operar)  ·  1,28 por sesión
desenlaces             TP 41 · SL 20 · cierre a las 11:30 3
ACIERTO                67,2 %  sobre 61 resueltas
stop mediano           5,9 p    ·   coste sobre riesgo 26,9 %
R BRUTA por operación  +1,032   ·   suma +66,02 R
R NETA  por operación  +0,762   ·   suma +48,79 R
por sesión             +0,976
minutos hasta salir    mediana 36
```

La regla mecánica, en esos mismos 50 días: 69 disparos, **22,2 % de acierto**,
−0,685 R por sesión. La diferencia emparejada es de **+1,661 R por sesión** a su
favor. Los días no eran fáciles: es el peor de los cuatro bloques para la regla.

## Los cuatro bloques

| | opera | ops | acierto | stop | R bruta | R neta | z |
|---|---|---|---|---|---|---|---|
| bloque 1 | 16 | 23 | 59,1 % | 5,8p | +0,754 | +0,490 | +1,60 |
| bloque 2 | 19 | 30 | 51,9 % | 7,2p | +0,591 | +0,377 | +1,44 |
| bloque 3 | 19 | 33 | 81,2 % | 5,1p | +1,445 | +1,160 | +5,62 |
| bloque 4 | 39 | 64 | 67,2 % | 5,9p | +1,032 | +0,762 | +4,36 |
| **los cuatro** | **93** | **150** | **66,2 %** | **6,0p** | **+0,992** | **+0,731** | **+6,45** |

Acierto contra el 33,3 % geométrico: **z = +8,31**. Su punto de equilibrio con
un stop de 6 pips y 1,43 de coste es **41,3 %**. Suma neta de las 150: **+109,65 R**.

## Las cuentas

El libro mayor se reproduce desde las operaciones, con las reglas de la página,
y **cuadra al dólar con lo que él exportó** en los nueve intentos. Eso valida a
la vez el motor de la cuenta y el volcado.

```
intento 1: PASA  11.000 $  sesión  3 · 3 días operados
intento 2: PASA  10.800 $  sesión 10 · 5 días
intento 3: PASA  10.800 $  sesión 13 · 3 días
intento 4: PASA  10.800 $  sesión 20 · 6 días
intento 5: PASA  10.872 $  sesión 26 · 5 días
intento 6: PASA  10.878 $  sesión 34 · 7 días
intento 7: PASA  10.800 $  sesión 40 · 3 días
intento 8: PASA  10.852 $  sesión 47 · 4 días
intento 9: en curso, 9.800 $ al acabar el bloque
```

**8 superados · 0 reventados.** La simulación predecía 99,9 % de paso y 0,1 % de
reventón por intento al 1 %, con una mediana de 8 días operados; le salieron
**4,5 días de mediana**. Ni se acercó a los límites: el peor día dentro de un
intento fue **−200 $** sobre un tope de −500, y la peor caída acumulada **−400 $**
sobre un tope de −1.000.

**Con el coste real descontado**, que la página no cobra:

| riesgo | bruta (como jugó) | con coste de 1,43 p |
|---|---|---|
| 0,5 % | 4 pasa / 0 revienta | 3 / 0 |
| **1,0 %** | **8 / 0** | **6 / 0** |
| 2,0 % | 10 / 0 | **9 / 2** |

El 2 % es el primero que revienta cuentas, ahora con sus operaciones reales y no
en simulación. Confirma la recomendación del 1 %.

## Cansancio: no apareció

Las 50 sesiones salieron en **una sola sentada de 71 minutos**, sin descansos, así
que el contraste de tandas del bloque 3 no se puede repetir. Lo que sí se puede
mirar es si cayó dentro de la sentada.

| | n | acierto | R neta |
|---|---|---|---|
| 1ª mitad | 32 | 67,7 % | +0,819 |
| 2ª mitad | 32 | 66,7 % | +0,706 |

Fisher p = 1,000. En los bloques 1 y 2 la caída era de 34 puntos con p = 0,023.
Por tercios de la sentada hay una bajada suave —78,9 % → 61,9 % → 61,9 %— pero
nada parecido al desplome anterior. **La caída de los bloques 1 y 2 no ha
replicado en ninguno de los dos bloques posteriores.** Con eso, lo más probable
es que fuera ruido de muestra pequeña, no un rasgo suyo.

## Lo que no se pudo medir, y era lo importante

**Las etiquetas de «por qué entro» se usaron 0 veces de 64.** Era el cambio de
todo el bloque: sin ellas seguimos sin poder escribir la regla de entrada, que
es exactamente el componente que lleva parado desde el principio. El bloque
aporta muestra y aporta cuentas, pero no aporta lo que se diseñó para aportar.

**Y hay un fallo de la página**, encontrado al leer el volcado: cuatro etiquetas
de «qué falló» aparecen colgadas de operaciones que **ganaron**.

```
S22 09:22 cierre «nivel»      ← el stop de esa sesión fue el de las 08:11
S26 09:24 TP     «stopcorto»  ← el de las 09:12
S27 09:15 TP     «nivel»      ← el de las 08:15
S32 09:18 TP     «nivel»      ← el de las 08:02
```

La causa: `btnFallo` escribía en `reg().ops[reg().ops.length-1]`, la última
operación registrada. Si abría otra antes de pulsar «Seguir», la etiqueta se
colgaba de la nueva. Arreglado: al saltar un stop se guarda **a qué operación
pertenece el panel** (`S.fallo`), y la etiqueta va ahí aunque entre otra por
medio; y si abre una operación con el panel abierto, se cierra guardando lo
marcado. Reasignadas al stop que les toca, quedan 12 de 20 stops diagnosticados.

También se ha puesto un aviso: confirmar una entrada sin motivo marcado pide el
motivo la primera vez y entra igual a la segunda. No bloquea —eso cambiaría cómo
opera— pero saltárselo pasa a ser una decisión.

## ¿Se lee bien a sí mismo?

Para cada stop se mira qué hizo el precio **después** de saltarlo, hasta las
11:30: si llegó a tocar el objetivo que él había puesto, la dirección era buena y
lo que falló fue el sitio; si no llegó, la lectura estaba mal.

De los 20 stops, en **12 (60 %)** el precio sí llegó después a su objetivo.

| lo que dijo | n | a quién culpa | acierta |
|---|---|---|---|
| stopcorto | 3 | el sitio | 3/3 |
| precipitada | 1 | el sitio | 1/1 |
| nada | 1 | nada, no fue | 1/1 |
| nivel | 3 | la lectura | 1/3 |
| contexto | 1 | la lectura | 0/1 |
| contexto+precipitada | 1 | el sitio | 0/1 |
| nivel+precipitada | 1 | el sitio | 0/1 |
| tarde+precipitada | 1 | el sitio | 0/1 |

**6 de 12: cara o cruz.** Con doce casos no se puede concluir nada, pero el
reparto es sugerente: cuando dice «el stop era corto» acierta las tres veces —eso
es medible y él lo ve— y cuando dice «el nivel estaba mal» acierta una de tres.
Diagnostica bien la mecánica y mal la lectura. Merece más muestra.

## Lo que sigue sin saberse

El ritmo: 50 sesiones en 71 minutos son 85 segundos por sesión. Se comprobó lo
mismo que en el bloque 3 —que los días no fueran más fáciles (la regla sacó su
peor resultado de los cuatro bloques: 22,2 %) y que la hora de entrada no
cambiara (mediana 08:36, contra 08:32 / 08:44 / 08:46 en los anteriores)— y no
hay señal de que esté jugando a otra cosa. Pero sigue siendo un simulador sin
deslizamiento, sin requotes y sin dinero de verdad.

Con esto, **150 operaciones y z +6,45** en simulador, y **cero** hacia delante.
