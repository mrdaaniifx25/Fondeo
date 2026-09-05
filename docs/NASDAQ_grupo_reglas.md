# Estrategia del grupo · reconstrucción en curso

Notas extraídas de las transcripciones. **No se guarda el texto literal**: es
contenido de un grupo privado y este repositorio es público. Aquí van solo
las reglas mecánicas, que es lo que hace falta para el backtest.

Estado: 6 de 35.

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
