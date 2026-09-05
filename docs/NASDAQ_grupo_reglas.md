# Estrategia del grupo · reconstrucción en curso

Notas extraídas de las transcripciones. **No se guarda el texto literal**: es
contenido de un grupo privado y este repositorio es público. Aquí van solo
las reglas mecánicas, que es lo que hace falta para el backtest.

Estado: 3 de 35.

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
