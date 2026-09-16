# Pre-registro · el barrido de sesión, su regla escrita por él

Escrito **antes** de medir nada. La especificación es suya, entera, del 16 de
septiembre de 2026, y llegó con su propia lista de lo que no hay que añadir.

## La regla, tal y como la escribió

    INSTRUMENTO  EURUSD          EJECUCION  M5
    SESIONES     Londres + Nueva York
    NIVELES      maximo y minimo de la sesion de referencia

    COMPRA
      1 identificar el minimo de la sesion de referencia
      2 el precio lo barre: cotiza por debajo
      3 recupera: cierra por encima del nivel
      4 confirmacion alcista en M5
      5 entrada
      6 SL debajo del minimo alcanzado en el barrido
      7 TP = 2R

    VENTA: lo mismo del otro lado.

    GESTION  RR fijo 1:2 · no mover SL · no mover TP · no anadir
             posiciones · una operacion por senal · sin discrecionalidad

## Lo que he tenido que concretar para poder programarlo

Son decisiones mías, no suyas, y las dejo escritas para que se vean:

**1 · Cuál es "la sesión de referencia".** Londres barre los extremos de Asia;
Nueva York barre los extremos de Londres. Es la lectura estándar y coincide con
cómo lo describió en agosto ("rotura del high de Asia").

**2 · Los horarios**, tomados de su propio indicador Sesiones, en hora de
Madrid: Asia 00:00-08:00, Londres 08:00-14:00, Nueva York 14:00-23:00.

**3 · El barrido**, con su definición literal: una vela de M5 cuyo máximo supera
el nivel y cuyo cierre queda por debajo (venta), o cuyo mínimo lo perfora y
cierra por encima (compra). Romper y recuperar. Tocar no basta.

**4 · La confirmación.** Él mismo dice que no está seguro de cuál es la suya, y
tiene razón en no afirmarlo. Se miden **las dos**, declaradas aquí:

    C1 agresiva     entrada al cierre de la propia vela del barrido
    C2 la suya      tras el barrido, esperar un cierre de M5 a favor, y
                    entrar al romperse el extremo de la vela del barrido

**5 · Un nivel, una operación.** Cada extremo (máximo y mínimo de Asia, máximo y
mínimo de Londres) genera como mucho una entrada por sesión. Sin esto, un solo
nivel puede disparar veinte veces en una mañana, y él opera una o dos al día.
Se informa también el recuento sin esta regla.

**6 · Caducidad.** Si tras el barrido no hay entrada en 12 velas de M5 (una
hora), la señal se anula.

**7 · Resolución en M1**, no en M5, para no inventarme el orden dentro de la
vela. Si stop y objetivo caen en el mismo minuto, cuenta como pérdida.

**8 · Buffer del stop = 0.** Él pide expresamente no tocarlo todavía.

## Coste

1,43 pips ida y vuelta, medido en su cuenta el 28-08-2026.

## La celda principal y el criterio, fijados ahora

**Celda principal: C2 (su confirmación), Londres y Nueva York juntas, buffer 0,
un nivel una operación, 2020-2026.** Un solo contraste.

**Se considera que la regla funciona si el intervalo de confianza del 95 % de la
R NETA queda entero por encima de cero.**

Con 2R fijo, el acierto que hace falta en bruto es 33,3 %. Con coste `c` y stop
`s`, sube a `33,3 % + (100·c)/(3s)`. Se informará junto al acierto medido, que es
la comparación que de verdad decide.

## Lo que se informa pase lo que pase

Sin elegir después: C1 y C2; Londres y Nueva York por separado; por año; por
nivel barrido (máximo contra mínimo); la distribución del riesgo en pips; y el
recuento sin la regla de un nivel una operación.

## Lo que invalidaría la prueba

Si salen menos de 100 operaciones en seis años, la regla no es lo que él opera
—él entra una o dos veces al día— y habría que revisar la traducción antes de
concluir nada del resultado.

---

## Corrección · 16 de septiembre, contestada por él

Le pregunté por las siete decisiones que había tomado yo. Sus respuestas, antes
de volver a medir nada:

| | pregunta | respuesta | ¿cambia? |
|---|---|---|---|
| 1 | qué nivel se barre | **entre sesiones** (Londres barre Asia, NY barre Londres) | no |
| 2 | sesión entera o killzone | **sesión entera** | no |
| 3 | dónde entra exactamente | *"no sé cuándo entras, necesitaría verlo"* | **sin resolver** |
| 4 | dónde va el stop | **en el mínimo de todo el movimiento**, no de la vela | **sí** |
| 5 | un nivel una operación | **intenta todas** | **sí** |
| 6 | distancia máxima | **no hay**, busca el 1:2 | no |
| 7 | caducidad | **sigue valiendo** | **sí** |

### Lo que cambia en el código

**4 · El stop va al extremo de la excursión entera.** Se define excursión como el
tramo que va desde que el precio cruza el nivel hasta que una vela cierra de
vuelta dentro. El stop es el extremo alcanzado en todo ese tramo, no el de la
vela que cierra. Con barridos de una sola vela coincide; con barridos de varias,
el stop es más ancho.

**5 · Se quita "un nivel, una operación".** Cada excursión completa es una señal.
Cuando termina, el nivel vuelve a quedar armado.

**7 · Se quita la caducidad de una hora.** La confirmación vale hasta el final de
la sesión.

### Lo que sigue sin resolverse, y es lo importante

La 3. Él no sabe describir su entrada, y no pasa nada: es honesto y es
exactamente lo que ya vimos en agosto cuando cuatro codificaciones de su regla
salieron al azar. **La descripción no contiene la decisión.**

Se mantienen las dos confirmaciones declaradas (C1 y C2) y se informa de las dos.
Ninguna de las dos es "su entrada" mientras él no la señale sobre el gráfico.

### El criterio no se toca

Sigue siendo el mismo: celda principal C2, Londres y Nueva York juntas, y la
regla funciona si el IC95 de la R neta queda entero por encima de cero.
