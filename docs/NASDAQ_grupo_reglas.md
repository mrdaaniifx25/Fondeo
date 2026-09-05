# Estrategia del grupo · reconstrucción en curso

Notas extraídas de las transcripciones. **No se guarda el texto literal**: es
contenido de un grupo privado y este repositorio es público. Aquí van solo
las reglas mecánicas, que es lo que hace falta para el backtest.

Estado: 16 de 35.

## Esqueleto provisional

    1 SESGO       direccional del día. En la nº1: "día muy alcista", máximos
                  históricos, se buscan CONTINUACIONES al alza.
                  -> PENDIENTE DE DEFINIR: cómo se decide el sesgo sin mirar
                     el futuro. Es el hueco más importante.

    2 ZONAS       altos/bajos de ASIA y de LONDRES, marcados en M15.

    3 BARRIDO     el precio barre esas zonas (para compras, barre los BAJOS).
                  REGLA CRUZADA: vale si barre en el SP *o* en el NASDAQ,
                  por correlación. La entrada va casi siempre en el SP.

    4 INDUCCIÓN   movimiento en contra de la dirección buscada, después del
                  barrido. En la nº1 hubo dos: una en premarket y otra
                  posterior, y se esperó a la segunda.
                  -> PENDIENTE: qué distingue una inducción de ruido.

    5 ENTRADA     en M1, sobre el IFVG (inverse fair value gap) que se forma
                  tras la inducción.

    6 R:R         1:1 FIJO. Textual: "hemos entrado en el 1 a 1 siguiendo
                  nuestro plan, nuestras normas" y "hay que seguir las
                  normas, chicos, en el 1 a 1".

    7 FRECUENCIA  "no opero todos los días" -> hay selección de día, y esa
                  selección es discrecional. Hueco a resolver.

## Modelo de sesiones que usa

Asia acumula · Londres manipula · Nueva York continúa (AMD / power of three).
En la nº1 Londres NO manipuló y Nueva York fue continuación alcista.

## Lo que ya se puede decir sin mirar datos

El R:R es 1:1, no 1:2 ni 1:3. Con 1:1 el listón del azar es el **50 %**, no
el 33 %. Y en M1 el stop es estrecho, así que el coste pesa mucho sobre la R:
ahí es donde se decidirá todo. El punto de equilibrio real estará bastante
por encima del 50 %, y cuánto depende del spread del índice, que sigue sin
medirse.

## Huecos que impiden mecanizar (a resolver con las 34 restantes)

    - cómo se fija el sesgo del día, sin usar información posterior
    - qué cuenta exactamente como inducción
    - definición operativa del IFVG que usan
    - a qué hora se puede entrar y hasta cuándo
    - qué se hace si no llega al TP: ¿cierre a la hora? ¿se deja correr?
    - qué días NO se opera

---

# Actualización tras las nº2 (día 19, pérdida) y nº3 (día 22, ganancia)

## Lo más importante: el sesgo puede que no sea un problema

Él habla de "continuaciones" y de "reversiones" como si fueran dos modos
distintos, y eso parecía imposible de mecanizar. Pero mirando las TRES
operaciones, las tres son el mismo patrón:

    nº1  barre los BAJOS de Asia y Londres   ->  COMPRA
    nº2  barre los BAJOS de Asia y Londres   ->  COMPRA
    nº3  barre los ALTOS (H4 y sesiones)     ->  VENTA

Siempre opera **en contra del barrido**. Lo que él llama "continuación" en
la nº1 es mecánicamente idéntico a lo que llama "reversión" en la nº2: en
las dos barrió bajos y compró. La etiqueta la pone el contexto de tendencia,
pero el disparo es el mismo.

Si esto aguanta en las 32 restantes, el sesgo deja de ser discrecional y la
estrategia es mecanizable entera.

## Reglas nuevas, ya concretas

    HORARIO   ventana de Nueva York: 9:30 a 10:30/11:00.
              "No suelo mirar más tarde de las 11:30." (nº3)
              -> regla dura y testeable.

    ENTRADA   definición textual de la nº2:
              "siempre busco que después de la inducción haya un impulso,
               un retroceso sano y que invalide un FVG. Al formarse el
               IFVG, yo entro."
              Y en la nº3 añade la confirmación de estructura: espera el
              primer bajo más bajo en M1 (quiebre estructural) antes de
              tomar el IFVG.

    SMT       divergencia entre SP500 y NASDAQ. En la nº2: "no hubo ningún
              SMT". Es la versión precisa de la regla cruzada de la nº1:
              un índice barre el nivel y el otro NO.
              -> comprobable directamente con los dos parquet.

    NIVELES   alto/bajo de Asia, alto/bajo de Londres, alto/bajo de la
              sesión de Nueva York del día anterior, y niveles de H4.

    NOTICIAS  no opera días de noticias (nº2, miércoles).

    R:R       1:1 confirmado por tercera vez.

## Secuencia de sesiones que describe (nº3, la más detallada)

    Asia acumula
    solapamiento Asia/Londres barre los ALTOS de Asia
    Londres baja y barre los BAJOS de Asia
    Londres sube haciendo altos  <- ESTO es la "inducción"
    Nueva York abre, extiende la inducción, y revierte  <- la entrada

## Huecos que siguen abiertos

    - "desequilibrio" / movimiento extendido: sin definición numérica
    - qué barrido cuenta (¿mecha? ¿cierre? ¿cuántos puntos por encima?)
    - si el SMT es obligatorio o solo una confluencia más
    - qué pasa si el 1:1 no se alcanza dentro de la ventana horaria

---

# Actualización tras la nº4 (break even)

## El DOL: el objetivo de liquidez de la sesión

Lo llama "doll" (DOL, draw on liquidity). Es el nivel al que espera que vaya
el precio en la sesión. Lo marca en **H4 y H1**, antes de operar, y son
altos/bajos relevantes (en la nº4: unos altos por encima, más los altos del
día anterior que descartó por lejanos).

El DOL **no es el take profit**. El TP sigue siendo 1:1. El DOL sirve para
otra cosa, y esa cosa es la regla más concreta que ha dado hasta ahora:

## Regla de break even, mecánica y falsable

    Si el OTRO índice barre el DOL mientras la operación está abierta,
    se mueve el stop a break even.

Textual: *"no tiene sentido seguir en este trade si nuestra Doll ya está
barrida en uno de los dos activos"*. En la nº4 entró en NASDAQ, el SP500
llegó antes a su DOL, y movió a BE. Perdió el TP por eso.

Y hace una afirmación **directamente comprobable**:

    "el break even que he puesto hoy podría haber sido TP, pero la mayoría
     de los días hubiese sido stop loss"

Eso se mide: cuando el otro índice barre el DOL, ¿la operación acaba peor
que cuando no lo barre? Es una de las pocas cosas de todo el proyecto que
se puede contrastar con un sí o un no limpio.

## Jerarquía de temporalidades

No entra en el primer FVG que aparece. Descartó FVGs de M1, M3 y M5 y esperó
al **tapeo del FVG de H1**. Textual: *"por jerarquía de temporalidades
tenemos que esperarnos al más grande"*. Después sí tomó un IFVG de M1, pero
como gatillo dentro del nivel de H1, no como señal por sí mismo.

Estructura real de la entrada, entonces:

    NIVEL     tapeo de un FVG de temporalidad alta (H1/H4)
    + SMT     divergencia con el otro índice en ese momento
    + GATILLO IFVG de M1 dentro de ese nivel

## Otras reglas nuevas

    SMT           aquí es REQUISITO, no adorno: "hemos entrado cuando
                  fileábamos un FVG de una hora y además hacíamos SMT".

    JUDAS SWING   nombra explícitamente el movimiento falso de la apertura
                  como lo que hay que esperar antes de entrar.

    UNA AL DÍA    "nosotros normalmente solo cogemos un trade". La segunda
                  oportunidad del día no se toma.

    INSTRUMENTO   la entrada NO va siempre en el SP500. En la nº4 entró en
                  NASDAQ. Entra donde el SMT le favorece.

## El patrón "en contra del barrido" sigue aguantando: 4 de 4

    nº1  barre BAJOS  -> compra
    nº2  barre BAJOS  -> compra
    nº3  barre ALTOS  -> venta
    nº4  barre BAJOS  -> compra

---

# Actualización tras las nº5 (TP) y nº6 (stop loss)

## CORRECCIÓN: la regla "en contra del barrido" era mía y es falsa

Con cuatro casos parecía que siempre entraba contra el barrido. Las nº5 y
nº6 lo rompen las dos:

    nº5  barre los BAJOS de Asia  ->  VENDE
    nº6  barre los ALTOS de Asia  ->  COMPRA

Coincidencia de las cuatro primeras. La regla real es otra, y en la nº5 la
dice él explícitamente.

## LA REGLA DE SESGO, por fin

El punto de decisión es el **FVG de H4**. Textual de la nº5:

    "cuando hemos invalidado este FVG de 4 horas hemos acabado de decidir
     el bias... si el precio hubiese empezado a revertir después de barrer
     esos bajos de Asia fileando este FVG SIN INVALIDARLO, podríamos haber
     llegado a buscar las compras"

O sea:

    el precio llega a un FVG de H4 (normalmente tras barrer liquidez
    de sesión)

      -> lo TAPEA y AGUANTA      = REVERSIÓN, se opera en la dirección
                                   del FVG
      -> lo INVALIDA (lo rompe)  = CONTINUACIÓN, se opera en la dirección
                                   de la rotura

Esto es completamente mecanizable: es una prueba sobre velas de H4 y no
depende de ninguna lectura subjetiva. Y explica las seis, incluidas las dos
que rompían el patrón anterior.

## El DOL es dinámico

En la nº6, el DOL era un FVG de H4 por encima. Cuando el precio lo invalidó,
el DOL pasó a ser los altos siguientes. Textual: *"una vez el FVG de 4 horas
se invalidó, pasó de ser mi doll el FVG a estos altos de aquí"*.

Así que el DOL se recalcula: es el siguiente charco de liquidez en la
dirección que marca el FVG de H4.

## El gatillo de M1 tiene alternativa: el CISD

    si hay un FVG de M1 limpio  ->  se entra en su invalidación
    si NO lo hay                ->  se espera al CISD de la manipulation leg
    si el FVG se invalida con POCA FUERZA -> también se espera al CISD

Textual nº5: *"como no había ningún FVG pequeño aquí, me esperaba al CISD"*.
Textual nº6: *"si hubiese visto que este FVG se invalidaba superpoquito, con
poca fuerza, me hubiese esperado al CISD"*.

"Con fuerza" no está definido numéricamente. Hueco.

## Confirmación intermedia: tapeo de FVG de M5

En las dos entra tras **tapear un FVG de M5 haciendo SMT con el otro
índice**. Esa parece ser la capa intermedia estable entre el nivel de H4/H1
y el gatillo de M1.

## Colocación del stop

Prefiere el **cuerpo** de la vela, no la mecha, cuando la mecha deja un R
malo. Textual: *"si el precio baja hasta el body, ya baja hasta aquí porque
hace un reswip"*.

## Confirmación del TP

nº5: el 1:1 cayó justo en el DOL (bajos de H4). Y da la razón de por qué no
alarga: *"no tiene sentido dejar un trade tantos R, sobre todo en empresas
de fondeo"*. El 1:1 no es una lectura del mercado, es una regla de gestión
de challenge.

## Huecos nuevos, y son los peores hasta ahora

    - DESCARTA setups válidos "porque los RS no me gustan" (nº6). Es
      discrecional y afecta a qué operaciones existen. Si no se puede
      formalizar, el backtest medirá una estrategia distinta a la suya.
    - "invalidar con mucha fuerza" no tiene definición.
    - jerarquía de temporalidades: prefiere M5 sobre M3 "si dan los mismos
      RS". Otra decisión sin umbral.

---

# Actualización tras las nº7, nº8 y nº9 (tres TP)

## CAMBIO DE ALCANCE: también opera LONDRES

La nº7 y la nº9 son operaciones de la **sesión de Londres**, no de Nueva
York. La nº8 es de Nueva York el mismo día que la nº7. Textual: *"opero las
dos, normalmente me miro las dos sesiones"*.

Esto invalida la ventana 9:30-11:30 NY como regla única. Son dos ventanas:
la apertura de Londres y la apertura de Nueva York. Y **una operación por
sesión**, no por día: en la nº8 dice *"yo meto un trade al día solo"* pero
ese mismo día ya había operado Londres, así que se refiere a una por sesión.

## Regla del DOL, ahora precisa y mecánica

El objetivo de liquidez debe estar **sin barrer en LOS DOS índices**.
Textual nº8:

    "esos bajos ya estaban barridos en el NASDAQ, entonces para mí ya no
     tiene relevancia; los que sí tenían relevancia eran estos, que no
     estaban barridos en ninguno de los dos"

Un nivel ya tomado en uno de los dos deja de ser objetivo. Esto es
programable tal cual.

## El stop, por fin explícito

    "con el stop loss en la inducción, en los bajos de la inducción,
     como suelo hacer siempre"   (nº9)

El stop va al extremo de la pierna de inducción, no a la mecha de la vela de
entrada. Con lo de la nº6 (preferir el cuerpo cuando la mecha da mal R),
queda: extremo de la inducción, y cuerpo si la mecha estropea el ratio.

## La confluencia de M15 vale en cualquiera de los dos índices

Textual nº9:

    "este pequeño FVG en el Nasdaq no llegó a ser tapeado... en el SP500 sí.
     Una vez hemos tapeado en el SP500, para mí ya cuenta como si hubiésemos
     tapeado los dos porque van correlacionados"

Entró en NASDAQ por un tapeo que ocurrió en el SP500. La regla cruzada no es
solo para el barrido: vale también para la confluencia de entrada.

## El sesgo tiene dos ramas, no una

La nº8 aclara algo que la nº5 dejaba a medias. Mira H4 **y H1** siempre.

    si el precio está interactuando con un FVG de H4/H1
        -> aguanta   = reversión en dirección del FVG
        -> invalida  = continuación en dirección de la rotura

    si NO hay ningún FVG relevante en juego
        -> manda la tendencia: continuación
        textual nº8: "no hay FVGs de los que estemos reaccionando en 4
        horas, todo superbajista, aquí veo ventas de manual"

## Confirmación de reglas ya anotadas

    - TP 1:1 en las tres. En la nº9 dice que el trade ideal daba más pero
      "por el tema de la entry no nos daba bien los RS, entonces lo he
      dejado hasta el uno a uno, como suelo hacer siempre".
    - BE en 1:1 o en un nivel relevante. nº7: "no siempre hay zona para
      poner break even".
    - No se entra al primer IFVG: hay que esperar la confluencia de M15/M5
      primero. nº9: "si buscas continuaciones no puedes entrar al primer
      invers que se haga".
    - Fuerza de la invalidación: nº8 repite que un IFVG flojo no lo toma.

## Huecos discrecionales acumulados (van cuatro)

    1. descarta setups "porque los RS no me gustan"          (nº6, nº9)
    2. "invalidar con mucha fuerza" sin definición           (nº6, nº8)
    3. elige M5 o M15 "depende del contexto"                 (nº9)
    4. NUEVO: se salta sesiones enteras. nº9: "Nueva York no me gustaba
       cómo se está moviendo el precio"

El 4 es el más caro: no es un filtro sobre la entrada, es un filtro sobre
qué días existen. Si no se puede formalizar, el backtest medirá la
estrategia sin su ojo, y hay que decirlo así de claro.

---

# Actualización tras las nº10 (BE) y nº11 (TP)

## CORRECCIÓN: el TP no siempre es 1:1

Lo tenía como regla fija y no lo es. El TP es el **DOL**; el 1:1 es lo que
sale casi siempre porque el DOL suele caer por ahí. Cuando no coinciden,
manda el DOL. Textual nº10:

    "podría haberlo dejado hasta el 1 a 1, que era casi igual, pero para qué
     voy a dejarlo en el 1 a 1 si mi objetivo es venir a barrer esto; si no
     lo barre es que no he leído bien el movimiento"

Esto importa para el backtest: el R:R deja de ser constante y el listón
geométrico deja de ser el 50 % fijo. Hay que medir el ratio operación a
operación.

## CISD, ahora con definición

    cierre de CUERPO a través del CUERPO de la última manipulation leg

Textual nº10: *"ha cruzado la manipulation leg, la última que ha habido, la
ha cruzado con cuerpo desde el body de la manipulation leg"*.

Y su jerarquía entre los dos gatillos: *"me gusta más utilizar el IFVG, pero
tengo en cuenta también el CISD"*.

## Selección del gatillo: hay tope, y es M5

Cuando hay varios IFVG a la vez sube de temporalidad y coge el mayor
disponible, **con techo en M5**:

    nº10: había uno de M2 y uno de M5 -> cogió el de M5
          "yo como máximo cojo un invers de 5 minutos"
    nº11: había de M1, M2 y M3, ninguno de M5 -> cogió el de M3
          "cuando hay muchos FVGs me fijo en el que tiene más valor, que es
           el de temporalidad más alta. Como máximo 5 minutos."

Esto cierra el hueco nº3 de la lista de discrecionales: **ya no es "depende
del contexto", es el mayor disponible entre M1 y M5.**

## Break even: cuándo NO ponerlo

    "cuando no hay motivo de poner break even, no hay que ponerlo... si te
     pillas un break even que no tiene sentido te echan cuando en verdad no
     había motivos"                                              (nº11)

Y la regla completa, dicha mejor que en la nº4:

    "si ya has tocado tu objetivo de liquidez con uno de los dos activos,
     protégete del trade o ciérralo, porque ya no tienes excusa para seguir
     dentro"                                                     (nº11)

El BE se coloca en un **nivel de liquidez interna** (nº10: "el break even lo
hemos puesto en un internal low"), no en el 1:1 automáticamente.

## El SMT y la regla cruzada son el mismo hecho visto dos veces

    un evento (barrido, tapeo de FVG, barrido de LRL) que ocurre en UN
    índice y no en el otro:

      -> cuenta como ocurrido para los dos   ("solo con que lo haga un
         activo ya sirve para los dos, van correlacionados")
      -> y el que solo lo haga uno ES el SMT, que es confluencia a favor

O sea: el caso bueno es exactamente la divergencia. Programable sin
ambigüedad.

## Liquidez interna / externa y HRL

    externa  = el DOL, los extremos hacia los que va el precio
    interna  = todo lo que hay entre medias, donde rebota por el camino
               -> es donde se coloca el break even

    HRL      = "high resistance liquidity": relative equal highs/lows en
               temporalidad alta. El equivalente de la LRL pero en H1/H4.
               Cuenta como DOL de calidad.

## Huecos discrecionales: quedan tres

    1. descarta setups "porque los RS no me gustan"       SIGUE ABIERTO
    2. "invalidar con mucha fuerza" sin definición        SIGUE ABIERTO
    3. elige M5 o M15 "depende del contexto"              RESUELTO (nº10/11)
    4. se salta sesiones enteras                          SIGUE ABIERTO

---

# Actualización tras las nº12 (TP 1:1) y nº13 (TP 1,44R)

## CORRECCIÓN: el SMT no es requisito

Lo tenía como obligatorio por la nº4. No lo es. En la nº12 entra sin SMT y
lo dice expresamente:

    "no hay SMT, eso es importante también... a mí me gusta que haya SMT.
     Sería un setup A+ si hubiese SMT."                          (nº12)

Y en la nº13 tampoco hay SMT en H1. Así que el SMT **sube la calidad del
setup pero no lo condiciona**. Eso lo convierte en una variable a medir por
separado en el backtest: ¿ganan más las operaciones con SMT que sin él?
Pregunta limpia y contestable.

## CORRECCIÓN: el TP puede pasar del 1:1, y el techo no es el mercado

La nº13 cierra en **1,44R**, en el extremo lejano del FVG de M15. Y da la
razón de por qué no alarga más, que es la admisión más reveladora de las
trece:

    "podríamos haber alargado el TP hasta aquí perfectamente. Lo que pasa
     que como cuentas de fondeo no puedo ganar tanto, porque si no la
     consistencia jugaría en mi contra"                          (nº13)

El TP no está limitado por lo que hace el precio: está limitado por la
**regla de consistencia de la empresa de fondeo**. Es una restricción de
gestión, no una lectura del mercado. Para el backtest significa que la R
que él realiza es un SUELO de lo que la estrategia daría sin esa atadura.

## El gatillo: la temporalidad cede ante el R:R

Refina lo de la nº10/11. En la nº12 había IFVG de M2, M3 y M5 y cogió el de
**M1**, porque los mayores quedaban lejos:

    "podríamos mirarlo en FVG de 2 minutos, pero ya quedaba bastante lejos
     y los RS no tendrían tanto sentido"                         (nº12)

Regla real: el IFVG de mayor temporalidad **cuyo R siga funcionando**, con
techo en M5.

## Noticias, con matiz

No es que no opere días de noticias. Le gustan:

    "me mola que haya noticias, es gasolina para el precio, es liquidez que
     entra. Obviamente cuando hay una noticia de alto impacto no entro
     mientras la noticia está saliendo."                         (nº12)

O sea: se excluye la ventana del dato, no el día.

## LA BALANZA: el núcleo discrecional, y él lo nombra

Este es el concepto central de la nº12 y no se puede programar:

    "nunca vas a encontrar el setup perfecto que no tenga nada en contra...
     me gusta hacer balanza con las confluencias a favor y en contra"

En la nº12 la única en contra era un FVG de M5 opuesto, y decidió que la
balanza ganaba. Eso no es una regla: es un juicio sobre un conjunto abierto
de factores, distinto en cada operación.

Consecuencia para el proyecto: puedo mecanizar TODO lo demás. Lo que salga
del backtest será **la estrategia sin la balanza**. Si sale positiva, la
balanza es un extra. Si sale plana, entonces todo el valor está en la
balanza, y eso solo se puede contrastar con el registro real de operaciones
del grupo, con sus precios.

## Estado de los huecos discrecionales

    1. "los RS no me gustan"                  parcialmente resuelto: es el
                                              criterio de desempate del
                                              gatillo, no un filtro aparte
    2. "invalidar con mucha fuerza"           SIGUE ABIERTO
    3. elección de temporalidad del gatillo   RESUELTO
    4. se salta sesiones enteras              SIGUE ABIERTO
    5. NUEVO: la balanza                      IRREDUCTIBLE

---

# Actualización tras las nº14, nº15 y nº16

## Su lista de confluencias, enumerada por él (nº16)

Es la formulación más limpia de las dieciséis:

    "Yo siempre busco confluencias que pueden ser tapeos en un FVG de 15
     minutos o de 5, o barridos de liquidez muy claros, Judas Swing, LRL a
     mi favor y barrer LRL en contra."

Cinco cosas, todas programables:

    1. tapeo de FVG de M15 o M5
    2. barrido de liquidez claro (niveles de sesión)
    3. Judas Swing (acumulación premarket -> manipulación -> distribución)
    4. LRL a favor: liquidez acumulada en la dirección del trade
    5. LRL en contra YA BARRIDA antes de entrar

Curioso, porque en la nº14 dice *"no es memorizar y una checklist mecánica
la fórmula mágica"* y dos vídeos después da la checklist.

## El TP tiene tope numérico

    "yo no suelo hacer trades de más del 1 a 1 y medio. Normalmente lo cojo
     al 1 a 1"                                                    (nº15)

    "como operamos fondeadas, tampoco puedo dejar un trade en el 1 a 3.
     Yo siempre lo pongo en un a uno"                              (nº14)

Regla final del TP: **el DOL si cae entre 1:1 y 1:1,5; si no, 1:1.**
En la nº15 el DOL daba 1:2,5 y no lo tomó por eso.

## El sesgo puede darse la vuelta a mitad de sesión

Esto complica la mecanización y hay que tenerlo en cuenta. En la nº14 abre
la sesión buscando compras hasta unos altos, y acaba vendiendo:

    "no quedarte casado con el bias que tengas al principio de la sesión...
     si al principio se me alinea todo para compras y luego en el premarket
     se me alinea todo para ventas, voy a saber adaptarme"

Consecuencia: el sesgo no se fija en la apertura, se **reevalúa vela a
vela**. En código eso es más fácil, no más difícil: se evalúa la condición
de H4/H1 en cada barra y se opera la primera confluencia que aparezca.

## LRL a favor / LRL en contra

Concepto que aparece por fin claro (nº14):

    a favor  = liquidez acumulada en la dirección del trade -> combustible
    en contra = liquidez acumulada en dirección opuesta

    "yo siempre intento que haya la máxima LRL a mi favor posible"
    "hemos borrado toda la LRL que teníamos en contra y teníamos todo esto
     a nuestro favor"

Regla: la LRL en contra debe estar **ya barrida** antes de entrar.

## Ventana del premarket

    acumulación de 9:00 a 9:29 hora de Nueva York               (nº15)
    manipulación justo en el open
    distribución = la operación

## Reconfirmaciones

    - DOL: nº16 descarta unos altos "porque ya estaban barridos en el
      SP500". Tercera vez que aplica la regla.
    - CISD: nº14 vuelve a definirlo igual y vuelve a exigir fuerza.
    - Sin SMT en la nº16 y aun así entra. Cuarta confirmación de que no es
      requisito.
    - BE: nº15 lo omite tras hacer balanza. "muchas veces te va a echar en
      break even si lo pones muy justito".

## Estado: ya se puede escribir el código

Con dieciséis transcripciones el esqueleto está completo salvo un umbral:
qué es "invalidar con fuerza". Todo lo demás tiene definición.
