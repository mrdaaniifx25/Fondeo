# Preregistro · Barrido de Liquidez Asiático en la apertura de Londres

Sellado ANTES de medir. Código en `bt/barrido_asiatico.py`. EURUSD,
2020-01 → 2026-07. Coste 1,43 pips (`docs/COSTE_real.md`).

## La especificación, tal como me la dio

    rango asiatico    02:00 a 09:00 CEST, en M15 -> Asian High y Asian Low
    ventana           09:00 a 12:00 CEST, ejecucion en M5
    barrido           entre 09:00 y 11:00 el precio cotiza por encima del
                      Asian High (sesgo bajista) o por debajo del Low (alcista)
    MSS               vela impulsiva de M5 que rompe y CIERRA CON CUERPO mas
                      alla del ultimo maximo/minimo estructural previo
    FVG               el impulso del MSS debe dejar un hueco de 3 velas en M5
    entrada           orden limitada en el inicio (o 50 %) del FVG
    stop              a 2 pips del extremo que hizo el barrido
    objetivo          1:3 fijo, o el extremo opuesto del rango asiatico
    riesgo            0,5 a 1 %

## Las cuatro ambigüedades, resueltas y declaradas

La hoja dice "pregunta antes de programar". Como quiere el resultado, las
resuelvo yo y las dejo escritas, y **pruebo las variantes en vez de elegir**:

1. **"último máximo/mínimo estructural previo"**. Lo defino como el fractal de
   Williams de M5 (dos velas a cada lado) más reciente **confirmado** en el
   lado contrario al barrido. Confirmado = formado en j con j+2 ≤ la vela
   actual, para que sea causal.

2. **"el inicio (o 50 %) del FVG"**. Ambiguo: en una venta, el borde cercano
   llena más veces y el lejano da mejor precio. Se prueban los **tres**:
   borde cercano, 50 % y borde lejano.

3. **Objetivo**. La hoja da dos opciones. Se prueban las **dos**: 1:3 fijo y
   extremo opuesto del rango asiático.

4. **Vida de la orden y cierre**. No lo dice. Declaro: la orden limitada vive
   hasta las 12:00 CEST y se cancela; la posición abierta corre hasta stop u
   objetivo, con cierre forzoso a las 23:00 CEST. Una operación al día como
   máximo.

Horario en **Europe/Madrid**, que resuelve solo el cambio CEST/CET.

## Lo que ya sé que va a decidir esto, y lo digo antes

El stop es **2 pips más allá del extremo barrido**, y la entrada está en el
FVG, que queda por dentro. Eso hace stops **cortos**. Con 1,43 pips de coste:

    stop  4 pips  ->  el coste es el 36 % del riesgo
    stop  8 pips  ->  el 18 %
    stop 15 pips  ->  el 10 %

Si el stop mediano sale por debajo de 8 pips, la ventaja bruta tendrá que ser
enorme para sobrevivir. **Publicaré el stop mediano junto al resultado**,
porque es el número que manda.

## Los cinco criterios de éxito, firmados

    1  ventaja BRUTA positiva con z > 2 en la mejor variante
    2  ventaja NETA positiva tras 1,43 pips
    3  bate a entradas al azar en la misma ventana y con la misma geometria
    4  bate a 5 nulos con bloques permutados
    5  al menos 4 de las 6 variantes (3 entradas x 2 objetivos) netas positivas

Operable solo si cumple las cinco. Si falla la 2 pero pasa la 1, es el muro
del coste otra vez y lo diré así, no como "prometedor".

## Mi predicción

Espero que **pase la 1 y falle la 2**. Es el patrón exacto de las otras dos
estrategias de barrido asiático ya medidas en este proyecto: ventaja bruta
real (+0,169 R, z +2,45 en el rango de Tradinverso) que el coste se come
entera porque el stop es corto.
