# Estrategia del grupo · reconstrucción en curso

Notas extraídas de las transcripciones. **No se guarda el texto literal**: es
contenido de un grupo privado y este repositorio es público. Aquí van solo
las reglas mecánicas, que es lo que hace falta para el backtest.

Estado: 1 de 35.

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
